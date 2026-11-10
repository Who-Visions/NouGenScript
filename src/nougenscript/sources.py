"""Safe local and GitHub source acquisition for read-only repository analysis."""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from nougenscript.dynamic_guard import DynamicFinding, audit_dynamic_literals

_OWNER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+$")
_REF = re.compile(r"^[A-Za-z0-9._/-]+$")


def _github_repository_url(source: str) -> str:
    parsed = urlparse(source)
    try:
        has_port = parsed.port is not None
    except ValueError as exc:
        raise ValueError("remote source URL has an invalid port") from exc
    if (parsed.scheme != "https" or parsed.hostname != "github.com" or has_port
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("remote source must be a plain https://github.com/OWNER/REPOSITORY URL")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2 or not _OWNER.fullmatch(parts[0]):
        raise ValueError("GitHub source must identify exactly one owner and repository")
    repository = parts[1].removesuffix(".git")
    if not repository or not _REPOSITORY.fullmatch(repository):
        raise ValueError("invalid GitHub repository name")
    return f"https://github.com/{parts[0]}/{repository}.git"


def _clone_public_or_authenticated(url: str, destination: Path, ref: str | None) -> None:
    hooks_directory = destination.parent / "hooks-disabled"
    hooks_directory.mkdir(mode=0o700)
    command = [
        "git", "-c", f"core.hooksPath={hooks_directory.as_posix()}", "clone", "--depth=1", "--single-branch",
        "--filter=blob:limit=1m", "--no-tags", url, str(destination),
    ]
    if ref:
        if not _REF.fullmatch(ref) or ref.startswith("-") or ".." in ref or "//" in ref:
            raise ValueError("ref must be a simple branch or tag name")
        command[7:7] = ["--branch", ref]

    env = os.environ.copy()
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
    })
    token = env.get("GITHUB_TOKEN")
    if token:
        import base64

        authorization = base64.b64encode(f"x-access-token:{token}".encode()).decode("ascii")
        env.update({
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
            "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {authorization}",
        })
    try:
        subprocess.run(command, check=True, capture_output=True, env=env, timeout=120)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("GitHub source download exceeded the 120-second limit") from exc
    except (OSError, subprocess.CalledProcessError) as exc:
        # Do not include subprocess output: it may contain remote metadata or credentials.
        code = getattr(exc, "returncode", "unavailable")
        raise ValueError(f"GitHub source download failed (exit {code})") from exc


@contextmanager
def source_checkout(source: str | Path, ref: str | None = None) -> Iterator[Path]:
    """Yield a local directory or an ephemeral GitHub checkout, read-only to callers."""
    source_text = str(source)
    if not source_text.startswith(("https://", "http://", "git@")):
        if ref:
            raise ValueError("--ref is supported only for GitHub URLs")
        directory = Path(source_text).resolve(strict=True)
        if not directory.is_dir():
            raise ValueError("local source must be a directory")
        yield directory
        return

    repository_url = _github_repository_url(source_text)
    if ref and (not _REF.fullmatch(ref) or ref.startswith("-") or ".." in ref or "//" in ref):
        raise ValueError("ref must be a simple branch or tag name")
    with tempfile.TemporaryDirectory(prefix="nougenscript-github-") as temporary:
        checkout = Path(temporary) / "source"
        _clone_public_or_authenticated(repository_url, checkout, ref)
        yield checkout


def audit_dynamic_source(
    source: str | Path,
    policy: str | Path = ".udct-policy.json",
    ref: str | None = None,
) -> list[DynamicFinding]:
    """Audit a local Git checkout or a GitHub repository without modifying either.

    Remote repositories are shallow-cloned into a temporary directory. A local
    policy may be supplied for them; remote code is never executed or written.
    Private GitHub repositories may use the process environment's GITHUB_TOKEN.
    """
    source_text = str(source)
    if source_text.startswith(("https://", "http://", "git@")):
        policy_path = Path(policy)
        if not policy_path.is_absolute():
            policy_path = Path.cwd() / policy_path
        with source_checkout(source_text, ref) as checkout:
            return audit_dynamic_literals(checkout, policy_path)
    with source_checkout(source_text, ref) as checkout:
        return audit_dynamic_literals(checkout, policy)
