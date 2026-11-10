import json
import os
import shutil
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


@pytest.mark.parametrize("source,expected", [
    (f'package main\n\nvar endpoint = "{LITERAL}"\n', 'os.LookupEnv("API_BASE_URL")'),
    (f'package main\nimport "os"\nvar endpoint = "{LITERAL}"\n', 'os.LookupEnv("API_BASE_URL")'),
    (f'package main\nimport sys "os"\nvar endpoint = "{LITERAL}"\n', 'sys.LookupEnv("API_BASE_URL")'),
    (f'package main\nfunc get() string {{ endpoint := "{LITERAL}"; return endpoint }}\n', 'os.LookupEnv("API_BASE_URL")'),
])
def test_go_dynamic_apply_handles_runtime_bindings_and_imports(tmp_path, source, expected):
    root = _repo(tmp_path / "repo")
    path = root / "client.go"
    path.write_text(source, encoding="utf-8")
    _commit(root, path)
    _policy(root, "go")

    preview = apply_dynamic_resolutions(root)
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    content = path.read_text(encoding="utf-8")
    assert report.written and report.replacements == 1
    assert expected in content
    assert content.count('"os"') == 1
    assert apply_dynamic_resolutions(root).replacements == 0


def test_go_keeps_constants_and_comments_unmodified(tmp_path):
    root = _repo(tmp_path / "repo")
    path = root / "client.go"
    path.write_text(
        f'package main\nconst endpoint = "{LITERAL}"\n// {LITERAL}\n', encoding="utf-8"
    )
    _commit(root, path)
    _policy(root, "go")

    report = apply_dynamic_resolutions(root)

    assert report.replacements == 0
    assert report.unresolved == ("client.go",)
    assert path.read_text(encoding="utf-8").count(LITERAL) == 2


def test_go_leaves_dot_imports_unresolved(tmp_path):
    root = _repo(tmp_path / "repo")
    path = root / "client.go"
    path.write_text(f'package main\nimport . "os"\nvar endpoint = "{LITERAL}"\n', encoding="utf-8")
    _commit(root, path)
    _policy(root, "go")

    report = apply_dynamic_resolutions(root)

    assert report.replacements == 0
    assert report.unresolved == ("client.go",)
    assert LITERAL in path.read_text(encoding="utf-8")


def test_java_rewrites_runtime_values_and_preserves_compile_time_constants(tmp_path):
    root = _repo(tmp_path / "repo")
    path = root / "Client.java"
    path.write_text(
        f'class Client {{ static final String CONSTANT = "{LITERAL}"; '
        f'static String endpoint = "{LITERAL}"; '
        f'void configure() {{ final String LOCAL = "{LITERAL}"; '
        f'String api = "{LITERAL}"; api = "{LITERAL}"; }} '
        f'// {LITERAL}\n}}\n', encoding="utf-8"
    )
    _commit(root, path)
    _policy(root, "java")

    preview = apply_dynamic_resolutions(root)
    report = apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    content = path.read_text(encoding="utf-8")
    assert report.written and report.replacements == 3
    assert content.count('java.util.Objects.requireNonNull(System.getenv("API_BASE_URL"), "API_BASE_URL must be set")') == 3
    assert f'static final String CONSTANT = "{LITERAL}";' in content
    assert f'final String LOCAL = "{LITERAL}";' in content
    assert f'// {LITERAL}' in content
    assert report.unresolved == ("Client.java",)
    javac = shutil.which("javac")
    if javac and subprocess.run(
        [javac, "-version"], check=False, capture_output=True, text=True
    ).returncode == 0:
        subprocess.run(["javac", path.name], cwd=root, check=True, capture_output=True, text=True)


def test_java_leaves_compile_time_constant_only_file_unresolved(tmp_path):
    root = _repo(tmp_path / "repo")
    path = root / "Client.java"
    path.write_text(f'class Client {{ static final String API = "{LITERAL}"; }}\n', encoding="utf-8")
    _commit(root, path)
    _policy(root, "java")

    report = apply_dynamic_resolutions(root)

    assert report.replacements == 0
    assert report.unresolved == ("Client.java",)


def test_java_leaves_implicit_interface_constants_unresolved(tmp_path):
    root = _repo(tmp_path / "repo")
    path = root / "Client.java"
    path.write_text(f'interface Client {{ String API = "{LITERAL}"; }}\n', encoding="utf-8")
    _commit(root, path)
    _policy(root, "java")

    report = apply_dynamic_resolutions(root)

    assert report.replacements == 0
    assert report.unresolved == ("Client.java",)


@pytest.mark.skipif(shutil.which("go") is None, reason="Go compiler is not installed")
def test_generated_go_import_and_expression_compile(tmp_path):
    root = _repo(tmp_path / "repo")
    path = root / "client.go"
    path.write_text(f'package client\nvar Endpoint = "{LITERAL}"\n', encoding="utf-8")
    _commit(root, path)
    _policy(root, "go")
    preview = apply_dynamic_resolutions(root)
    apply_dynamic_resolutions(root, write=True, confirm=preview.plan_id)

    subprocess.run(
        ["go", "test", "./..."], cwd=root, env={**os.environ, "GO111MODULE": "off"},
        check=True, capture_output=True, text=True,
    )
