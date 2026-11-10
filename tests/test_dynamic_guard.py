import json
import subprocess
from pathlib import Path

import pytest

from nougenscript.cli import main
from nougenscript.dynamic_guard import audit_dynamic_literals
from nougenscript.sources import _github_repository_url, audit_dynamic_source


def _git_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=Test", "-c",
                    "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "init"], check=True)
    return path


def _write_policy(root: Path, rules: list[dict]) -> Path:
    policy = root / ".udct-policy.json"
    policy.write_text(json.dumps({"version": 1, "rules": rules}), encoding="utf-8")
    return policy


def test_audit_is_deterministic_tracked_only_and_read_only(tmp_path):
    root = _git_repo(tmp_path / "repo")
    source = root / "src" / "client.py"
    source.parent.mkdir()
    source.write_text('URL = "https://api.example.invalid/v1"\nOTHER = "https://api.example.invalid/v1"\n',
                      encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "src/client.py"], check=True)
    untracked = root / "untracked.py"
    untracked.write_text('URL = "https://api.example.invalid/v1"\n', encoding="utf-8")
    _write_policy(root, [{
        "id": "api-origin",
        "literal": "https://api.example.invalid/v1",
        "paths": ["src/**/*.py"],
        "slot": "API_BASE_URL",
        "rationale": "Deployment environments supply the API origin.",
    }])

    before = source.read_bytes()
    first = audit_dynamic_literals(root)
    second = audit_dynamic_literals(root)
    assert first == second
    assert [(item.path, item.line, item.column, item.slot) for item in first] == [
        ("src/client.py", 1, 8, "API_BASE_URL"),
        ("src/client.py", 2, 10, "API_BASE_URL"),
    ]
    assert source.read_bytes() == before
    assert untracked.exists()


def test_cli_returns_findings_as_json_and_failure_status(tmp_path, capsys):
    root = _git_repo(tmp_path / "repo")
    file = root / "service.py"
    file.write_text('HOST = "localhost"\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "service.py"], check=True)
    _write_policy(root, [{"id": "local-host", "literal": "localhost", "paths": ["*.py"],
                         "slot": "SERVICE_HOST", "rationale": "Host varies by deployment."}])

    assert main(["audit-dynamic", str(root), "--json"]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output == [{"column": 9, "line": 1, "path": "service.py", "rationale": "Host varies by deployment.",
                       "rule_id": "local-host", "slot": "SERVICE_HOST"}]


def test_invalid_policy_is_reported_without_scanning(tmp_path, capsys):
    root = _git_repo(tmp_path / "repo")
    _write_policy(root, [{"id": "bad", "literal": "x", "paths": ["*.py"],
                         "slot": "not valid", "rationale": "reason"}])
    assert main(["audit-dynamic", str(root)]) == 2
    assert "slot must be a valid template slot name" in capsys.readouterr().err


def test_policy_rejects_unknown_fields(tmp_path):
    root = _git_repo(tmp_path / "repo")
    (root / ".udct-policy.json").write_text(
        '{"version": 1, "rules": [], "typo": true}', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="only version and rules"):
        audit_dynamic_literals(root)


def test_policy_can_live_outside_repository(tmp_path):
    root = _git_repo(tmp_path / "repo")
    outside = tmp_path / "outside.json"
    outside.write_text('{"version":1,"rules":[]}', encoding="utf-8")
    assert audit_dynamic_literals(root, outside) == []


def test_policy_file_is_excluded_even_for_broad_globs(tmp_path):
    root = _git_repo(tmp_path / "repo")
    policy = _write_policy(root, [{"id": "self", "literal": "policy-marker", "paths": ["**/*"],
                                 "slot": "POLICY_MARKER", "rationale": "The marker is dynamic."}])
    subprocess.run(["git", "-C", str(root), "add", policy.name], check=True)
    assert audit_dynamic_literals(root) == []


def test_source_api_accepts_a_local_checkout(tmp_path):
    root = _git_repo(tmp_path / "repo")
    source = root / "config.py"
    source.write_text('API_URL = "https://api.example.invalid"\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "config.py"], check=True)
    _write_policy(root, [{"id": "api", "literal": "https://api.example.invalid", "paths": ["*.py"],
                         "slot": "API_URL", "rationale": "Set by deployment."}])
    assert audit_dynamic_source(root)[0].slot == "API_URL"


def test_github_source_parser_rejects_non_github_or_ambiguous_urls():
    assert _github_repository_url("https://github.com/owner/repo") == "https://github.com/owner/repo.git"
    assert _github_repository_url("https://github.com/owner/repo.git") == "https://github.com/owner/repo.git"
    for source in (
        "http://github.com/owner/repo",
        "https://evil.example/owner/repo",
        "https://user:secret@github.com/owner/repo",
        "https://github.com/owner/repo/tree/main",
        "https://github.com/owner/repo?download=1",
    ):
        with pytest.raises(ValueError):
            _github_repository_url(source)


def test_audit_requires_repository_root(tmp_path):
    root = _git_repo(tmp_path / "repo")
    nested = root / "src"
    nested.mkdir()
    _write_policy(nested, [])
    with pytest.raises(ValueError, match="must be the Git root"):
        audit_dynamic_literals(nested)


def test_targeted_symlink_cannot_escape_repository(tmp_path):
    root = _git_repo(tmp_path / "repo")
    outside = tmp_path / "outside.py"
    outside.write_text('HOST = "outside"\n', encoding="utf-8")
    link = root / "linked.py"
    link.symlink_to(outside)
    subprocess.run(["git", "-C", str(root), "add", "linked.py"], check=True)
    _write_policy(root, [{"id": "outside", "literal": "outside", "paths": ["*.py"],
                         "slot": "VALUE", "rationale": "Value is dynamic."}])
    with pytest.raises(ValueError, match="escapes repository"):
        audit_dynamic_literals(root)


def test_cli_help_renders_without_percent_format_error(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--help"])
    assert error.value.code == 0
    assert "audit-dynamic" in capsys.readouterr().out
