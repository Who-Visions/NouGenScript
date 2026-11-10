"""Read-only candidate discovery for literals that commonly vary by deployment."""
from __future__ import annotations

import ast
import hashlib
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from nougenscript.sources import source_checkout

_CODE_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte",
    ".go", ".rs", ".java", ".kt", ".kts", ".swift", ".cs", ".php", ".rb", ".sh",
    ".bash", ".zsh", ".yaml", ".yml", ".toml", ".json", ".properties", ".tf",
    ".hcl", ".c", ".cc", ".cpp", ".h", ".hpp", ".sql",
}
_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "vendor", "build", "dist", "target", "__pycache__"}
_DYNAMIC_NAME = re.compile(r"(?:URL|URI|HOST|ENDPOINT|BASE_URL|PATH|DIRECTORY|DIR|PORT|TIMEOUT|REGION|BUCKET|MODEL|RETRIES|INTERVAL|POOL_SIZE)", re.IGNORECASE)
_SENSITIVE_NAME = re.compile(r"(?:TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE_KEY|API_KEY|ACCESS_KEY|AUTH)", re.IGNORECASE)
_ASSIGNMENT = re.compile(
    r"^\s*(?:(?:export|const|let|var|static|final|readonly|public|private|protected|val|var)\s+)*"
    r"(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)\s*(?::[^=]+)?\s*(?:=|:)\s*"
    r"(?:(?P<quote>['\"])(?P<string>(?:\\.|[^\\\n])*?)(?P=quote)|(?P<number>-?\d+(?:\.\d+)?))"
)
_JSON_ASSIGNMENT = re.compile(
    r"^\s*\{?\s*(?P<quote>['\"])(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)(?P=quote)\s*:\s*"
    r"(?:(?P<value_quote>['\"])(?P<string>(?:\\.|[^\\\n])*?)(?P=value_quote)|(?P<number>-?\d+(?:\.\d+)?))"
)
_URL = re.compile(r"^https?://", re.IGNORECASE)
_ABS_PATH = re.compile(r"^(?:/|\\\\|[A-Za-z]:[\\/])")


@dataclass(frozen=True)
class DynamicSuggestion:
    id: str
    path: str
    line: int
    column: int
    symbol: str
    kind: str
    slot: str
    value_preview: str
    resolution: str | None
    required_import: str | None
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "symbol": self.symbol,
            "kind": self.kind,
            "slot": self.slot,
            "value_preview": self.value_preview,
            "resolution": self.resolution,
            "required_import": self.required_import,
            "rationale": self.rationale,
        }


def _tracked_or_source_files(root: Path) -> list[str]:
    try:
        subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        if any((parent / ".git").exists() for parent in (root, *root.parents)):
            raise ValueError("cannot enumerate files in the Git source")
        files = []
        for current, directories, names in os.walk(root):
            directories[:] = sorted(name for name in directories if name not in _SKIP_DIRS and not name.startswith("."))
            for name in sorted(names):
                candidate = Path(current, name)
                if candidate.suffix.lower() in _CODE_SUFFIXES:
                    files.append(candidate.relative_to(root).as_posix())
        return sorted(files)
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached"],
            check=True,
            capture_output=True,
        )
        untracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("cannot enumerate files in the Git source") from exc
    entries = {entry.decode("utf-8", errors="surrogateescape")
               for output in (tracked.stdout, untracked.stdout)
               for entry in output.split(b"\0") if entry}
    return sorted(entries)


def _resolution(path: str, slot: str) -> tuple[str, str | None]:
    suffix = Path(path).suffix.lower()
    if suffix in {".py", ".pyi"}:
        return f'os.environ["{slot}"]', "import os"
    if suffix in {".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte"}:
        return f"process.env.{slot}", None
    if suffix in {".ts", ".tsx"}:
        return f"process.env.{slot}", None
    if suffix == ".go":
        return f'os.Getenv("{slot}")', 'import "os"'
    if suffix == ".rs":
        return f'std::env::var("{slot}")?', "use std::env;"
    if suffix in {".kt", ".kts"}:
        return f'System.getenv("{slot}")', None
    if suffix == ".java":
        return f'System.getenv("{slot}")', None
    if suffix == ".cs":
        return f'Environment.GetEnvironmentVariable("{slot}")', "using System;"
    if suffix == ".rb":
        return f'ENV.fetch("{slot}")', None
    if suffix == ".php":
        return f"getenv('{slot}')", None
    if suffix in {".sh", ".bash", ".zsh"}:
        return '"${' + slot + ':?' + slot + ' must be set}"', None
    return None, None


def _candidate_value(kind: str, value: str) -> str:
    if kind == "url":
        parsed = urlsplit(value)
        host = parsed.hostname or "host"
        return f"{parsed.scheme}://{host}/…"
    if kind == "path":
        return "<absolute path redacted>"
    return value


def suggest_dynamic_literals(source: str | Path, ref: str | None = None) -> list[DynamicSuggestion]:
    """Find likely deployment-specific assignments; never prints source values verbatim."""
    with source_checkout(source, ref) as root:
        file_names = _tracked_or_source_files(root)
        if len(file_names) > 10_000:
            raise ValueError("source contains more than 10,000 files; narrow the checkout before scanning")
        suggestions: list[DynamicSuggestion] = []
        total_bytes = 0
        for relative in file_names:
            if Path(relative).suffix.lower() not in _CODE_SUFFIXES:
                continue
            candidate = (root / relative).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                continue
            try:
                size = candidate.stat().st_size
                if size > 1_000_000:
                    continue
                total_bytes += size
                if total_bytes > 100_000_000:
                    raise ValueError("source exceeds the 100 MB text scan limit")
                content = candidate.read_bytes()
            except OSError as exc:
                raise ValueError(f"cannot read source file {relative}") from exc
            if b"\0" in content:
                continue
            text = content.decode("utf-8", errors="replace")
            for line_number, line in enumerate(text.splitlines(), start=1):
                match = _ASSIGNMENT.match(line) or _JSON_ASSIGNMENT.match(line)
                if not match:
                    continue
                symbol = match.group("name")
                if _SENSITIVE_NAME.search(symbol) or not _DYNAMIC_NAME.search(symbol):
                    continue
                string_value = match.group("string")
                number_value = match.group("number")
                if string_value is None:
                    if number_value is None or not re.search(r"PORT|TIMEOUT|RETRIES|INTERVAL|POOL_SIZE", symbol, re.IGNORECASE):
                        continue
                    kind, value = "numeric-setting", number_value
                else:
                    groups = match.groupdict()
                    quote = groups.get("value_quote") or groups.get("quote")
                    try:
                        value = ast.literal_eval(f"{quote}{string_value}{quote}")
                    except (SyntaxError, ValueError):
                        continue
                    if _URL.match(value):
                        kind = "url"
                    elif _ABS_PATH.match(value):
                        kind = "path"
                    else:
                        continue
                slot = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", symbol).upper()
                slot = re.sub(r"[^A-Z0-9_]+", "_", slot).strip("_")
                if not slot or not slot[0].isalpha():
                    continue
                resolution, required_import = _resolution(relative, slot)
                column = match.start("string") + 1 if string_value is not None else match.start("number") + 1
                fingerprint = hashlib.sha256(f"{relative}\0{line_number}\0{symbol}".encode()).hexdigest()[:12]
                rationale = {
                    "url": "Service origins commonly differ between local, test, and production environments.",
                    "path": "Absolute machine paths commonly vary across developers and deployment hosts.",
                    "numeric-setting": "Operational limits commonly need environment-specific configuration.",
                }[kind]
                suggestions.append(DynamicSuggestion(
                    id=fingerprint,
                    path=relative,
                    line=line_number,
                    column=column,
                    symbol=symbol,
                    kind=kind,
                    slot=slot,
                    value_preview=_candidate_value(kind, value),
                    resolution=resolution,
                    required_import=required_import,
                    rationale=rationale,
                ))
        return sorted(suggestions, key=lambda item: (item.path, item.line, item.column, item.id))


def render_environment_template(suggestions: list[DynamicSuggestion]) -> str:
    """Render a deterministic, value-free template for deployment settings."""
    slots = sorted({item.slot for item in suggestions})
    lines = ["# Generated by UDCT. Set each value for this deployment."]
    lines.extend(f"{slot}=" for slot in slots)
    return "\n".join(lines) + "\n"
