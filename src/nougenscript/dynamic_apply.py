"""Conservative, opt-in application of policy-backed Python resolutions."""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nougenscript.dynamic_guard import _load_policy, audit_dynamic_literals


@dataclass(frozen=True)
class ApplyReport:
    """Value-free summary of a dynamic-resolution application."""

    changed_files: tuple[str, ...]
    replacements: int
    unresolved: tuple[str, ...]
    written: bool
    plan_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "replacements": self.replacements,
            "unresolved": list(self.unresolved),
            "written": self.written,
            "plan_id": self.plan_id,
            "review_required": True,
        }


def _is_docstring(node: ast.Constant, tree: ast.Module) -> bool:
    for scope in ast.walk(tree):
        body = getattr(scope, "body", None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str) and first.value is node):
            return True
    return False


def _annotation_constants(tree: ast.Module) -> set[int]:
    excluded: set[int] = set()
    for parent in ast.walk(tree):
        fields = []
        if isinstance(parent, ast.AnnAssign):
            fields.append(parent.annotation)
        elif isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if parent.returns is not None:
                fields.append(parent.returns)
            fields.extend(arg.annotation for arg in (*parent.args.posonlyargs, *parent.args.args, *parent.args.kwonlyargs)
                          if arg.annotation is not None)
            if parent.args.vararg and parent.args.vararg.annotation is not None:
                fields.append(parent.args.vararg.annotation)
            if parent.args.kwarg and parent.args.kwarg.annotation is not None:
                fields.append(parent.args.kwarg.annotation)
        elif isinstance(parent, ast.arg) and parent.annotation is not None:
            fields.append(parent.annotation)
        for field in fields:
            excluded.update(id(node) for node in ast.walk(field) if isinstance(node, ast.Constant))
    return excluded


def _module_imports_os(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.Import)
        and any(alias.name == "os" and alias.asname in (None, "os") for alias in node.names)
        for node in tree.body
    )


def _import_insertion(text: str, tree: ast.Module) -> int:
    """Return a character offset after the module docstring and future imports."""
    lines = text.splitlines(keepends=True)
    prefix_lines = 0
    for index, line in enumerate(lines[:2]):
        if (index == 0 and line.startswith("#!")) or re.match(r"\s*#.*coding[:=]\s*[-\w.]+", line):
            prefix_lines = index + 1
    statement_lines = prefix_lines
    body = tree.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        statement_lines = max(statement_lines, body[0].end_lineno or body[0].lineno)
        body = body[1:]
    for node in body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            statement_lines = max(statement_lines, node.end_lineno or node.lineno)
    return sum(len(line) for line in lines[:statement_lines])


def _parse_source(text: str, relative: str) -> ast.Module:
    try:
        return ast.parse(text, filename=relative)
    except (SyntaxError, ValueError, tokenize.TokenError) as exc:
        # Parser exceptions may include the source line, which can contain a
        # private literal. Surface only a path and a stable reason to callers.
        raise ValueError(f"cannot safely transform {relative}: invalid or unsupported Python syntax") from exc


def _prepare_file(
    path: Path, relative: str, rules: list[dict[str, Any]], findings: list[Any]
) -> tuple[str | None, int, bool, bytes]:
    original_bytes = path.read_bytes()
    original = original_bytes.decode("utf-8")
    tree = _parse_source(original, relative)
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(original).readline))
    except (tokenize.TokenError, IndentationError) as exc:
        raise ValueError(f"cannot safely transform {relative}: invalid or unsupported Python syntax") from exc
    lines = original.splitlines(keepends=True)
    line_offsets: list[int] = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    # Match only a complete Python string token whose decoded value is exactly
    # the policy literal. Substrings, comments, f-strings, and docstrings stay put.
    rule_by_id = {rule["id"]: rule for rule in rules}
    by_location: dict[tuple[int, int], Any] = {}
    for finding in findings:
        key = (finding.line, finding.column)
        previous = by_location.get(key)
        if previous is not None and previous.slot != finding.slot:
            raise ValueError(f"conflicting UDCT slots target {relative}:{finding.line}")
        by_location[key] = finding
    nodes_by_start: dict[tuple[int, int], list[ast.Constant]] = {}
    annotation_nodes = _annotation_constants(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            nodes_by_start.setdefault((node.lineno, node.col_offset), []).append(node)

    edits: list[tuple[int, int, str]] = []
    used_tokens: set[tuple[int, int]] = set()
    for finding in by_location.values():
        rule = rule_by_id[finding.rule_id]
        literal = rule["literal"].decode("utf-8")
        match = None
        for token in tokens:
            if token.type != tokenize.STRING or token.start[0] != finding.line or token.end[0] != finding.line:
                continue
            raw = token.string
            inner = raw.find(literal)
            if inner < 0 or token.start[1] + inner + 1 != finding.column:
                continue
            try:
                if ast.literal_eval(raw) != literal:
                    continue
            except (SyntaxError, ValueError):
                continue
            start_byte = len(lines[token.start[0] - 1][:token.start[1]].encode("utf-8"))
            nodes = nodes_by_start.get((token.start[0], start_byte), [])
            if not any(node.value == literal and id(node) not in annotation_nodes and not _is_docstring(node, tree)
                       for node in nodes):
                continue
            token_key = token.start
            if token_key in used_tokens:
                continue
            used_tokens.add(token_key)
            start = line_offsets[token.start[0] - 1] + token.start[1]
            end = line_offsets[token.end[0] - 1] + token.end[1]
            match = (start, end, f'os.environ[{rule["slot"]!r}]')
            break
        if match is not None:
            edits.append(match)

    if not edits:
        return None, 0, bool(findings), original_bytes
    rewritten = original
    for start, end, replacement in sorted(edits, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    if not _module_imports_os(tree):
        insertion = _import_insertion(rewritten, _parse_source(rewritten, relative))
        newline = "\r\n" if "\r\n" in rewritten else "\n"
        prefix = rewritten[:insertion]
        if prefix and not prefix.endswith(("\n", "\r")):
            prefix += newline
        rewritten = prefix + "import os" + newline + rewritten[insertion:]
    # Refuse transformations that do not leave syntactically valid Python.
    _parse_source(rewritten, relative)
    return rewritten, len(edits), len(edits) != len(by_location), original_bytes


def apply_dynamic_resolutions(
    root: str | Path,
    policy: str | Path = ".udct-policy.json",
    *,
    write: bool = False,
    confirm: str | None = None,
) -> ApplyReport:
    """Prepare or explicitly write exact policy-backed Python rewrites.

    The default is a value-free preview. Writes are limited to a local Git root,
    Python files with exact standalone string-token matches, and clean target files.
    """
    root_text = str(root)
    if root_text.startswith(("https://", "http://", "git@")):
        raise ValueError("apply-dynamic requires a local Git repository; remote sources are read-only")
    repo = Path(root).resolve(strict=True)
    if not repo.is_dir():
        raise ValueError("apply-dynamic requires a local Git repository")
    findings = audit_dynamic_literals(repo, policy)
    policy_path = Path(policy)
    if not policy_path.is_absolute():
        policy_path = repo / policy_path
    rules = _load_policy(policy_path.resolve(strict=True))

    grouped: dict[str, list[Any]] = {}
    for finding in findings:
        grouped.setdefault(finding.path, []).append(finding)

    prepared: dict[Path, tuple[str, bytes]] = {}
    unresolved: set[str] = set()
    replacement_count = 0
    for relative, file_findings in grouped.items():
        path = (repo / relative).resolve(strict=True)
        if not path.is_relative_to(repo):
            raise ValueError(f"tracked path escapes repository through a symlink: {relative}")
        if path.suffix.lower() != ".py":
            unresolved.add(relative)
            continue
        content, count, has_unresolved, original_bytes = _prepare_file(path, relative, rules, file_findings)
        if content is None:
            unresolved.add(relative)
            continue
        prepared[path] = (content, original_bytes)
        replacement_count += count
        if has_unresolved:
            unresolved.add(relative)

    plan_material = {
        "version": 1,
        "files": [
            {
                "path": path.relative_to(repo).as_posix(),
                "source_sha256": hashlib.sha256(original).hexdigest(),
                "result_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
            for path, (content, original) in sorted(prepared.items(), key=lambda item: item[0].as_posix())
        ],
        "unresolved": sorted(unresolved),
    }
    plan_id = hashlib.sha256(json.dumps(plan_material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    if write and prepared:
        if confirm != plan_id:
            raise ValueError(f"write requires --confirm {plan_id} from a fresh preview")
        relative_paths = [path.relative_to(repo).as_posix() for path in prepared]
        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all", "--", *relative_paths],
            check=True, capture_output=True, text=True,
        )
        if status.stdout.strip():
            raise ValueError("refusing to write: one or more target files have existing Git changes")
        # Stage complete replacement files before changing any target. Each file
        # is atomically replaced and retains its original permission bits.
        staged: list[tuple[Path, Path, bytes]] = []
        try:
            for path, (content, original_bytes) in prepared.items():
                if path.read_bytes() != original_bytes:
                    raise ValueError("refusing to write: a target changed during preparation")
                descriptor, temporary_name = tempfile.mkstemp(prefix=".udct-", dir=path.parent)
                temporary = Path(temporary_name)
                staged.append((path, temporary, original_bytes))
                try:
                    os.chmod(temporary, path.stat().st_mode)
                    with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
                        handle.write(content)
                        handle.flush()
                        os.fsync(handle.fileno())
                except Exception:
                    try:
                        os.close(descriptor)
                    except OSError:
                        pass
                    raise
            for path, _, original_bytes in staged:
                if path.read_bytes() != original_bytes:
                    raise ValueError("refusing to write: a target changed during preparation")
            replaced: list[tuple[Path, bytes]] = []
            for path, temporary, original_bytes in staged:
                os.replace(temporary, path)
                replaced.append((path, original_bytes))
        except Exception:
            for path, original_bytes in reversed(locals().get("replaced", [])):
                descriptor, rollback_name = tempfile.mkstemp(prefix=".udct-rollback-", dir=path.parent)
                rollback = Path(rollback_name)
                try:
                    os.chmod(rollback, path.stat().st_mode)
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(original_bytes)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(rollback, path)
                finally:
                    rollback.unlink(missing_ok=True)
            raise
        finally:
            for _, temporary, _ in staged:
                temporary.unlink(missing_ok=True)

    return ApplyReport(
        changed_files=tuple(sorted(path.relative_to(repo).as_posix() for path in prepared)),
        replacements=replacement_count,
        unresolved=tuple(sorted(unresolved)),
        written=write and bool(prepared),
        plan_id=plan_id,
    )
