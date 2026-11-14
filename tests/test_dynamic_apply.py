import json
import subprocess

import pytest

from nougenscript.cli import main
from nougenscript.dynamic_apply import apply_dynamic_resolutions


def _repo(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run([
        "git", "-C", str(path), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "--allow-empty", "-qm", "init",
    ], check=True)
    return path


def _policy(root, literal, *, paths=("*.py",)):
    policy = root / ".udct-policy.json"
    policy.write_text(json.dumps({"version": 1, "rules": [{
        "id": "api-origin", "literal": literal, "slot": "API_BASE_URL", "paths": list(paths),
        "rationale": "Set for each deployment.",
    }]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", policy.name], check=True)
    return policy


def _commit_file(root, path):
    subprocess.run(["git", "-C", str(root), "add", path.name], check=True)
    subprocess.run([
        "git", "-C", str(root), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-qm", "fixture",
    ], check=True)


def test_apply_preview_is_value_free_and_does_not_write(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text('API_BASE_URL = "https://private.example.invalid/v1"\n', encoding="utf-8")
    _commit_file(root, source)
    _policy(root, "https://private.example.invalid/v1")
    before = source.read_bytes()

    report = apply_dynamic_resolutions(root)

    assert report.changed_files == ("client.py",)
    assert report.replacements == 1
    assert report.written is False
    assert "private.example.invalid" not in json.dumps(report.to_dict())
    assert source.read_bytes() == before


def test_apply_write_replaces_exact_python_literal_and_is_idempotent(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text(
        '"""Module docs."""\nfrom __future__ import annotations\n\n'
        'API_BASE_URL = "https://api.example.invalid/v1"\n'
        '# https://api.example.invalid/v1 is mentioned in a comment\n',
        encoding="utf-8",
    )
    _commit_file(root, source)
    _policy(root, "https://api.example.invalid/v1")

    preview = apply_dynamic_resolutions(root)
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    result = source.read_text(encoding="utf-8")
    assert report.written is True
    assert report.replacements == 1
    assert report.unresolved == ("client.py",)
    assert result.startswith('"""Module docs."""\nfrom __future__ import annotations\nimport os\n')
    assert 'API_BASE_URL = os.environ[\'API_BASE_URL\']' in result
    assert '# https://api.example.invalid/v1 is mentioned in a comment' in result
    assert apply_dynamic_resolutions(root).replacements == 0


def test_apply_refuses_dirty_target_before_writing(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text('API_BASE_URL = "https://api.example.invalid/v1"\n', encoding="utf-8")
    _commit_file(root, source)
    _policy(root, "https://api.example.invalid/v1")
    source.write_text(source.read_text(encoding="utf-8") + "# user edit\n", encoding="utf-8")
    preview = apply_dynamic_resolutions(root)
    before = source.read_bytes()

    with pytest.raises(ValueError, match="existing Git changes"):
        apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    assert source.read_bytes() == before


def test_apply_reports_non_python_match_for_manual_resolution(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "settings.json"
    source.write_text('{"API_BASE_URL": "https://api.example.invalid/v1"}\n', encoding="utf-8")
    _commit_file(root, source)
    _policy(root, "https://api.example.invalid/v1", paths=("*.json",))

    preview = apply_dynamic_resolutions(root)
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    assert report.changed_files == ()
    assert report.unresolved == ("settings.json",)
    assert report.written is False
    assert source.read_text(encoding="utf-8").startswith("{")


def test_apply_refuses_conflicting_slots_for_one_literal_location(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text('API_BASE_URL = "https://api.example.invalid/v1"\n', encoding="utf-8")
    _commit_file(root, source)
    (root / ".udct-policy.json").write_text(json.dumps({"version": 1, "rules": [
        {"id": "first", "literal": "https://api.example.invalid/v1", "slot": "API_BASE_URL",
         "paths": ["*.py"], "rationale": "First setting."},
        {"id": "second", "literal": "https://api.example.invalid/v1", "slot": "SERVICE_URL",
         "paths": ["*.py"], "rationale": "Conflicting setting."},
    ]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", ".udct-policy.json"], check=True)

    with pytest.raises(ValueError, match="conflicting UDCT slots"):
        apply_dynamic_resolutions(root, write=True)

    assert "https://api.example.invalid/v1" in source.read_text(encoding="utf-8")


def test_apply_skips_annotation_but_rewrites_assignable_value(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text(
        'from typing import Literal\n'
        'API_BASE_URL: Literal["https://api.example.invalid/v1"] = "https://api.example.invalid/v1"\n',
        encoding="utf-8",
    )
    _commit_file(root, source)
    _policy(root, "https://api.example.invalid/v1")

    preview = apply_dynamic_resolutions(root)
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    content = source.read_text(encoding="utf-8")
    assert report.replacements == 1
    assert report.unresolved == ("client.py",)
    assert 'Literal["https://api.example.invalid/v1"]' in content
    assert "= os.environ['API_BASE_URL']" in content


def test_apply_rejects_remote_source_without_network_access():
    with pytest.raises(ValueError, match="local Git repository"):
        apply_dynamic_resolutions("https://github.com/example/project")


def test_apply_dynamic_cli_previews_then_writes_only_when_requested(tmp_path, capsys):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text('API_BASE_URL = "https://api.example.invalid/v1"\n', encoding="utf-8")
    _commit_file(root, source)
    _policy(root, "https://api.example.invalid/v1")

    assert main(["apply-dynamic", str(root), "--json"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["written"] is False
    assert source.read_text(encoding="utf-8").startswith("API_BASE_URL")

    assert main(["apply-dynamic", str(root), "--write", "--confirm", preview["plan_id"], "--json"]) == 0
    written = json.loads(capsys.readouterr().out)
    assert written["written"] is True
    assert "os.environ" in source.read_text(encoding="utf-8")


def test_apply_requires_current_preview_plan_id(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text('API_BASE_URL = "https://api.example.invalid/v1"\n', encoding="utf-8")
    _commit_file(root, source)
    _policy(root, "https://api.example.invalid/v1")
    preview = apply_dynamic_resolutions(root)
    source.write_text(source.read_text(encoding="utf-8") + "# changed after preview\n", encoding="utf-8")

    with pytest.raises(ValueError, match="fresh preview"):
        apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)
