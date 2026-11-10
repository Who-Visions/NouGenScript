import json
import subprocess

import pytest

from nougenscript.dynamic_apply import apply_dynamic_resolutions

LITERAL = "https://api.example.invalid/v1"


def _repo(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run([
        "git", "-C", str(path), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "--allow-empty", "-qm", "init",
    ], check=True)
    return path


def _commit(root, path):
    subprocess.run(["git", "-C", str(root), "add", path.name], check=True)
    subprocess.run([
        "git", "-C", str(root), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-qm", "fixture",
    ], check=True)


def _policy(root, suffix):
    policy = root / ".udct-policy.json"
    policy.write_text(json.dumps({"version": 1, "rules": [{
        "id": "api-origin", "literal": LITERAL, "slot": "API_BASE_URL",
        "paths": [f"*.{suffix}"], "rationale": "Set per deployment.",
    }]}), encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", policy.name], check=True)


@pytest.mark.parametrize("suffix", ["js", "mjs", "cjs", "jsx", "ts", "tsx"])
def test_apply_js_ts_exact_initializer_is_preview_bound_and_syntax_checked(tmp_path, suffix):
    root = _repo(tmp_path / "repo")
    source = root / f"client.{suffix}"
    annotation = ": string" if suffix in {"ts", "tsx"} else ""
    prefix = "const café = 1;\r\n" if suffix == "ts" else ""
    if suffix in {"jsx", "tsx"}:
        prefix = "const View = () => <div />;\n"
    source.write_bytes((prefix + f'const API_BASE_URL{annotation} = "{LITERAL}";\r\n').encode("utf-8"))
    _commit(root, source)
    _policy(root, suffix)

    preview = apply_dynamic_resolutions(root)
    assert apply_dynamic_resolutions(root).plan_id == preview.plan_id
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    content = source.read_text(encoding="utf-8")
    assert preview.changed_files == (source.name,)
    assert report.written is True
    assert report.replacements == 1
    assert report.unresolved == ()
    assert 'process.env["API_BASE_URL"] ?? (() => { throw new Error("API_BASE_URL must be set"); })()' in content
    assert apply_dynamic_resolutions(root).replacements == 0


def test_apply_js_object_and_assignment_values_but_preserve_comments_and_calls(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "settings.js"
    source.write_text(
        f'const settings = {{ apiOrigin: "{LITERAL}" }};\n'
        f'client.endpoint = "{LITERAL}";\n'
        f'// {LITERAL}\n'
        f'connect("{LITERAL}");\n', encoding="utf-8",
    )
    _commit(root, source)
    _policy(root, "js")

    preview = apply_dynamic_resolutions(root)
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    content = source.read_text(encoding="utf-8")
    assert report.replacements == 2
    assert report.unresolved == ("settings.js",)
    assert content.count('process.env["API_BASE_URL"]') == 2
    assert f'// {LITERAL}' in content
    assert f'connect("{LITERAL}")' in content


def test_apply_js_refuses_to_parse_invalid_syntax_without_changing_file(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "broken.js"
    source.write_text(f'const = "{LITERAL}";\n', encoding="utf-8")
    _commit(root, source)
    _policy(root, "js")
    before = source.read_bytes()

    with pytest.raises(ValueError, match="invalid or unsupported JavaScript/TypeScript syntax"):
        apply_dynamic_resolutions(root, write=True)

    assert source.read_bytes() == before


def test_apply_js_leaves_escaped_and_noninitializer_occurrences_unresolved(tmp_path):
    root = _repo(tmp_path / "repo")
    source = root / "client.js"
    source.write_text(
        f'const escaped = "https:\\u002f\\u002fapi.example.invalid/v1";\n'
        f'connect("{LITERAL}");\n', encoding="utf-8",
    )
    _commit(root, source)
    _policy(root, "js")

    report = apply_dynamic_resolutions(root, write=True)

    assert report.changed_files == ()
    assert report.replacements == 0
    assert report.unresolved == ("client.js",)
    assert source.read_text(encoding="utf-8").count(LITERAL) == 1
