"""Deterministic, read-only checks for repository-specific hardcoded values.

Intent is supplied by a checked-in policy: a generic scanner cannot safely
decide whether an arbitrary literal is a protocol constant or configuration.
"""
from __future__ import annotations

import fnmatch
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SLOT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MAX_TRACKED_FILES = 10_000
_MAX_FILE_BYTES = 1_000_000
_MAX_TOTAL_BYTES = 100_000_000


@dataclass(frozen=True)
class DynamicFinding:
    path: str
    line: int
    column: int
    rule_id: str
    slot: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "rule_id": self.rule_id,
            "slot": self.slot,
            "rationale": self.rationale,
        }


def _load_policy(policy_path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read policy {policy_path}: {exc}") from exc
    version = raw.get("version") if isinstance(raw, dict) else None
    if (not isinstance(raw, dict) or type(version) is not int or version != 1
            or not isinstance(raw.get("rules"), list)):
        raise ValueError("policy must be a JSON object with version=1 and a rules array")
    if set(raw) != {"version", "rules"}:
        raise ValueError("policy may contain only version and rules")

    seen: set[str] = set()
    rules: list[dict[str, Any]] = []
    for index, rule in enumerate(raw["rules"]):
        if not isinstance(rule, dict):
            raise ValueError(f"rules[{index}] must be an object")
        if set(rule) != {"id", "literal", "slot", "paths", "rationale"}:
            raise ValueError(f"rules[{index}] must contain only id, literal, slot, paths, and rationale")
        rule_id, literal, slot = rule.get("id"), rule.get("literal"), rule.get("slot")
        paths, rationale = rule.get("paths"), rule.get("rationale")
        if not isinstance(rule_id, str) or not rule_id.strip() or rule_id != rule_id.strip() or rule_id in seen:
            raise ValueError(f"rules[{index}].id must be a unique non-empty string")
        if not isinstance(literal, str) or not literal or "\n" in literal or "\r" in literal:
            raise ValueError(f"rules[{index}].literal must be a non-empty single-line string")
        if not isinstance(slot, str) or not _SLOT.fullmatch(slot):
            raise ValueError(f"rules[{index}].slot must be a valid template slot name")
        if not isinstance(paths, list) or not paths or any(not isinstance(p, str) or not p for p in paths):
            raise ValueError(f"rules[{index}].paths must be a non-empty array of glob strings")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"rules[{index}].rationale must explain why the value is dynamic")
        seen.add(rule_id)
        rules.append({"id": rule_id, "literal": literal.encode("utf-8"), "slot": slot,
                      "paths": tuple(paths), "rationale": rationale.strip()})
    return rules


def _tracked_files(root: Path) -> list[str]:
    try:
        top_level = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"cannot enumerate tracked Git files under {root}: {exc}") from exc
    git_root = Path(top_level.stdout.decode("utf-8").strip()).resolve()
    if git_root != root:
        raise ValueError(f"repository argument must be the Git root ({git_root})")
    return sorted({entry.decode("utf-8", errors="surrogateescape")
                   for entry in result.stdout.split(b"\0") if entry})


def _matches_path(path: str, pattern: str) -> bool:
    # pathlib/fnmatch disagree on whether **/ includes zero directories. Treat
    # it as zero-or-more so conventional src/**/*.py policies include src/a.py.
    return fnmatch.fnmatchcase(path, pattern) or fnmatch.fnmatchcase(path, pattern.replace("**/", ""))


def audit_dynamic_literals(root: str | Path, policy: str | Path = ".udct-policy.json") -> list[DynamicFinding]:
    """Find policy-listed values in tracked files, without changing the worktree."""
    repo = Path(root).resolve(strict=True)
    if not repo.is_dir():
        raise ValueError(f"repository root is not a directory: {repo}")
    policy_path = Path(policy)
    if not policy_path.is_absolute():
        policy_path = repo / policy_path
    policy_path = policy_path.resolve(strict=True)
    policy_relative = policy_path.relative_to(repo).as_posix() if policy_path.is_relative_to(repo) else None
    rules = _load_policy(policy_path)
    findings: list[DynamicFinding] = []

    tracked_files = _tracked_files(repo)
    if len(tracked_files) > _MAX_TRACKED_FILES:
        raise ValueError("repository contains more than 10,000 tracked files; narrow the audit scope")
    total_bytes = 0
    for relative in tracked_files:
        if policy_relative is not None and relative == policy_relative:
            continue
        applicable_rules = [rule for rule in rules
                            if any(_matches_path(relative, pattern) for pattern in rule["paths"])]
        if not applicable_rules:
            continue
        candidate = (repo / relative).resolve()
        if not candidate.is_relative_to(repo):
            raise ValueError(f"tracked path escapes repository through a symlink: {relative}")
        if not candidate.is_file():
            continue
        try:
            size = candidate.stat().st_size
            if size > _MAX_FILE_BYTES:
                continue
            total_bytes += size
            if total_bytes > _MAX_TOTAL_BYTES:
                raise ValueError("repository exceeds the 100 MB policy scan limit; narrow the audit scope")
            content = candidate.read_bytes()
        except ValueError:
            raise
        except OSError as exc:
            raise ValueError(f"cannot read tracked file {relative}: {exc}") from exc
        if b"\0" in content:
            continue
        for rule in applicable_rules:
            start = 0
            while True:
                offset = content.find(rule["literal"], start)
                if offset < 0:
                    break
                findings.append(DynamicFinding(
                    path=relative,
                    line=content.count(b"\n", 0, offset) + 1,
                    column=len(content[content.rfind(b"\n", 0, offset) + 1:offset].decode(
                        "utf-8", errors="replace"
                    )) + 1,
                    rule_id=rule["id"],
                    slot=rule["slot"],
                    rationale=rule["rationale"],
                ))
                start = offset + len(rule["literal"])

    return sorted(findings, key=lambda item: (item.path, item.line, item.column, item.rule_id, item.slot))
