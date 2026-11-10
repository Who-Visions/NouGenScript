import json
import subprocess
from pathlib import Path

from nougenscript.cli import main
from nougenscript.resolution_plan import plan_dynamic_resolutions


def _repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "commit", "--allow-empty", "-qm", "init"], check=True)
    return path


def test_policy_resolution_plan_is_deterministic_value_free_and_read_only(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.py"
    source.write_text('API_BASE_URL = "https://private.example.invalid/v1"\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", source.name], check=True)
    policy = root / ".udct-policy.json"
    policy.write_text(json.dumps({"version": 1, "rules": [{
        "id": "api-origin",
        "literal": "https://private.example.invalid/v1",
        "slot": "API_BASE_URL",
        "paths": ["*.py"],
        "rationale": "Set for each deployment.",
    }]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", policy.name], check=True)
    before = source.read_bytes()

    first = plan_dynamic_resolutions(root)
    second = plan_dynamic_resolutions(root)

    assert first == second
    assert first[0].resolution == 'os.environ["API_BASE_URL"]'
    assert first[0].required_import == "import os"
    assert first[0].review_required is True
    assert "private.example.invalid" not in json.dumps(first[0].to_dict())
    assert source.read_bytes() == before


def test_plan_marks_unknown_file_types_for_manual_review(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "settings.json"
    source.write_text('{"API_URL": "https://api.example.invalid"}\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", source.name], check=True)
    policy = root / ".udct-policy.json"
    policy.write_text(json.dumps({"version": 1, "rules": [{
        "id": "api", "literal": "https://api.example.invalid", "slot": "API_URL",
        "paths": ["*.json"], "rationale": "Set per deployment.",
    }]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", policy.name], check=True)

    plan = plan_dynamic_resolutions(root)[0]

    assert plan.resolution is None
    assert plan.review_required is True


def test_plan_dynamic_cli_returns_machine_readable_plan(tmp_path, capsys):
    root = _repo(tmp_path / "repo")
    source = root / "client.ts"
    source.write_text('const API_URL = "https://api.example.invalid";\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", source.name], check=True)
    (root / ".udct-policy.json").write_text(json.dumps({"version": 1, "rules": [{
        "id": "api", "literal": "https://api.example.invalid", "slot": "API_URL",
        "paths": ["*.ts"], "rationale": "Set per deployment.",
    }]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", ".udct-policy.json"], check=True)

    assert main(["plan-dynamic", str(root), "--json"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output[0]["resolution"] == "process.env.API_URL"
    assert output[0]["review_required"] is True
