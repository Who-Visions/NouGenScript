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


def _tree_sitter_parser(path: Path):
    """Create a pinned, in-process parser without fetching grammars at runtime."""
    from tree_sitter import Language, Parser

    suffix = path.suffix.lower()
    if suffix in {".js", ".jsx", ".mjs", ".cjs"}:
        import tree_sitter_javascript

        grammar = tree_sitter_javascript.language()
    elif suffix in {".ts", ".tsx"}:
        import tree_sitter_typescript

        grammar = (tree_sitter_typescript.language_tsx() if suffix == ".tsx"
                   else tree_sitter_typescript.language_typescript())
    elif suffix == ".go":
        import tree_sitter_go

        grammar = tree_sitter_go.language()
    elif suffix == ".java":
        import tree_sitter_java

        grammar = tree_sitter_java.language()
    else:
        raise ValueError(f"cannot safely transform {path.name}: unsupported language")
    return Parser(Language(grammar))


def _parse_js_ts(parser: Any, source: bytes) -> Any:
    return parser.parse(source)


def _js_binding_contains(node: Any, name: str) -> bool:
    """Return whether a JavaScript binding pattern declares ``name``."""
    if node.type in {"identifier", "shorthand_property_identifier_pattern"}:
        return node.text.decode("utf-8") == name
    if node.type == "pair_pattern":
        value = node.child_by_field_name("value")
        return value is not None and _js_binding_contains(value, name)
    if node.type == "assignment_pattern":
        left = node.child_by_field_name("left")
        return left is not None and _js_binding_contains(left, name)
    if node.type == "type_annotation":
        return False
    return any(_js_binding_contains(child, name) for child in node.named_children)


def _js_declares_binding(root: Any, name: str) -> bool:
    """Conservatively detect file-local bindings that can capture globals.

    A file-wide check intentionally prefers leaving a candidate unresolved over
    emitting ``process.env`` that binds to a local parameter or declaration.
    """
    declaration_fields = {
        "variable_declarator": ("name",),
        "function_declaration": ("name", "parameters"),
        "function_expression": ("name", "parameters"),
        "generator_function_declaration": ("name", "parameters"),
        "generator_function": ("name", "parameters"),
        "class_declaration": ("name",),
        "class": ("name",),
        "method_definition": ("parameters",),
        "arrow_function": ("parameters",),
        "catch_clause": ("parameter",),
        "import_specifier": ("alias",),
        "import_clause": ("*",),
        "namespace_import": ("name",),
    }
    stack = [root]
    while stack:
        node = stack.pop()
        for field in declaration_fields.get(node.type, ()):
            bindings = node.named_children if field == "*" else (node.child_by_field_name(field),)
            if any(binding is not None and _js_binding_contains(binding, name) for binding in bindings):
                return True
        stack.extend(node.children)
    return False


def _is_js_initializer(node: Any) -> bool:
    """Limit JS/TS writes to direct variable, object-property, and assignment values."""
    parent = node.parent
    if parent is None:
        return False
    return (
        (parent.type == "variable_declarator" and parent.child_by_field_name("value") == node)
        or (parent.type == "pair" and parent.child_by_field_name("value") == node)
        or (parent.type == "assignment_expression" and parent.child_by_field_name("right") == node)
    )


def _prepare_js_ts_file(
    path: Path, relative: str, rules: list[dict[str, Any]], findings: list[Any]
) -> tuple[str | None, int, bool, bytes]:
    """Prepare exact, syntax-checked JavaScript/TypeScript initializer rewrites.

    Escaped strings and other expression contexts remain unresolved. The parser
    establishes syntax and token boundaries; only complete, unescaped string
    values at direct initializer sites can be replaced.
    """
    with path.open("rb") as source_file:
        original_bytes = source_file.read(1_000_001)
    if len(original_bytes) > 1_000_000:
        raise ValueError(f"cannot safely transform {relative}: source exceeds the 1 MB parser limit")
    try:
        original_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"cannot safely transform {relative}: source is not UTF-8") from exc
    parser = _tree_sitter_parser(path)
    tree = _parse_js_ts(parser, original_bytes)
    if tree is None:
        raise ValueError(f"cannot safely transform {relative}: parser could not produce a syntax tree")
    if tree.root_node.has_error:
        raise ValueError(f"cannot safely transform {relative}: invalid or unsupported JavaScript/TypeScript syntax")

    if _js_declares_binding(tree.root_node, "process"):
        return None, 0, bool(findings), original_bytes

    rule_by_id = {rule["id"]: rule for rule in rules}
    by_location: dict[tuple[int, int], Any] = {}
    for finding in findings:
        key = (finding.line, finding.column)
        previous = by_location.get(key)
        if previous is not None and previous.slot != finding.slot:
            raise ValueError(f"conflicting UDCT slots target {relative}:{finding.line}")
        by_location[key] = finding

    line_starts = [0]
    line_starts.extend(index + 1 for index, byte in enumerate(original_bytes) if byte == 0x0A)
    nodes_by_location: dict[tuple[int, int], Any] = {}
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "string" and _is_js_initializer(node):
            line_index = node.start_point.row
            content_start = node.start_byte + 1
            line_start = line_starts[line_index]
            column = len(original_bytes[line_start:content_start].decode("utf-8")) + 1
            nodes_by_location[(line_index + 1, column)] = node
        stack.extend(reversed(node.children))

    edits: list[tuple[int, int, bytes]] = []
    for finding in by_location.values():
        rule = rule_by_id[finding.rule_id]
        literal = rule["literal"]
        node = nodes_by_location.get((finding.line, finding.column))
        if node is not None:
            token = original_bytes[node.start_byte:node.end_byte]
            if len(token) < 2 or token[:1] not in (b"'", b'"') or token[-1:] != token[:1]:
                continue
            value = token[1:-1]
            if b"\\" in value or value != literal:
                continue
            slot = rule["slot"]
            escaped_slot = json.dumps(slot, ensure_ascii=True)
            replacement = (
                f"process.env[{escaped_slot}] ?? (() => {{ throw new Error({json.dumps(slot + ' must be set')}); }})()"
            ).encode("ascii")
            edits.append((node.start_byte, node.end_byte, replacement))

    if not edits:
        return None, 0, bool(findings), original_bytes
    rewritten = original_bytes
    for start, end, replacement in sorted(edits, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    rewritten_tree = _parse_js_ts(parser, rewritten)
    if rewritten_tree is None:
        raise ValueError(f"cannot safely transform {relative}: parser could not validate generated syntax")
    if rewritten_tree.root_node.has_error:
        raise ValueError(f"cannot safely transform {relative}: generated JavaScript/TypeScript syntax is invalid")
    return rewritten.decode("utf-8"), len(edits), len(edits) != len(by_location), original_bytes


def _tree_text(source: bytes, node: Any) -> bytes:
    return source[node.start_byte:node.end_byte]


def _is_go_runtime_initializer(node: Any) -> bool:
    parent = node.parent
    if parent is None or parent.type != "expression_list":
        return False
    declaration = parent.parent
    if declaration is None:
        return False
    if declaration.type in {"short_var_declaration", "assignment_statement"}:
        return declaration.child_by_field_name("right") == parent
    if declaration.type == "var_spec":
        # Go constants are compile-time expressions and must never be rewritten.
        return declaration.child_by_field_name("value") == parent
    return False


def _go_os_import(root: Any, source: bytes) -> tuple[bool, str | None]:
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type == "import_spec":
            path = node.child_by_field_name("path")
            if path is not None and _tree_text(source, path) == b'"os"':
                alias = node.child_by_field_name("name")
                name = _tree_text(source, alias).decode("ascii") if alias is not None else "os"
                return True, None if name in {".", "_"} else name
        stack.extend(node.children)
    return False, None


def _go_declares_identifier(root: Any, source: bytes, name: str) -> bool:
    """Conservatively detect declarations that could shadow a package import.

    The check is intentionally file-wide: false positives leave a finding
    unresolved, while missing a shadow could emit code that does not compile.
    """
    declaration_types = {
        "const_spec", "function_declaration", "parameter_declaration",
        "variadic_parameter_declaration", "type_spec", "var_spec",
    }
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type in declaration_types:
            names = list(node.children_by_field_name("name"))
            while names:
                candidate = names.pop()
                if candidate.type == "identifier" and _tree_text(source, candidate).decode("utf-8") == name:
                    return True
                names.extend(candidate.children)
        elif node.type == "short_var_declaration":
            left = node.child_by_field_name("left")
            if left is not None:
                names = [left]
                while names:
                    candidate = names.pop()
                    if candidate.type == "identifier" and _tree_text(source, candidate).decode("utf-8") == name:
                        return True
                    names.extend(candidate.children)
        elif node.type == "range_clause":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            if (left is not None and right is not None
                    and b":=" in source[left.end_byte:right.start_byte]):
                names = [left]
                while names:
                    candidate = names.pop()
                    if candidate.type == "identifier" and _tree_text(source, candidate).decode("utf-8") == name:
                        return True
                    names.extend(candidate.children)
        elif node.type == "type_switch_statement":
            alias = node.child_by_field_name("alias")
            if alias is not None:
                names = [alias]
                while names:
                    candidate = names.pop()
                    if candidate.type == "identifier" and _tree_text(source, candidate).decode("utf-8") == name:
                        return True
                    names.extend(candidate.children)
        stack.extend(node.children)
    return False


def _prepare_go_file(
    path: Path, relative: str, rules: list[dict[str, Any]], findings: list[Any]
) -> tuple[str | None, int, bool, bytes]:
    original = path.read_bytes()
    if len(original) > 1_000_000:
        raise ValueError(f"cannot safely transform {relative}: source exceeds the 1 MB parser limit")
    try:
        original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"cannot safely transform {relative}: source is not UTF-8") from exc
    parser = _tree_sitter_parser(path)
    tree = parser.parse(original)
    if tree is None or tree.root_node.has_error:
        raise ValueError(f"cannot safely transform {relative}: invalid or unsupported Go syntax")
    has_os_import, os_name = _go_os_import(tree.root_node, original)
    if has_os_import and os_name is None:
        # Dot and blank imports cannot be referenced by generated expressions.
        return None, 0, bool(findings), original
    if has_os_import:
        assert os_name is not None
        if _go_declares_identifier(tree.root_node, original, os_name):
            # Do not generate a reference that a local/package declaration can
            # capture instead of the imported package.
            return None, 0, bool(findings), original
        import_alias = None
    else:
        # Pick a deterministic import alias absent from every identifier in the
        # file so generated package references cannot be captured by user code.
        identifiers: set[str] = set()
        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            if node.type == "identifier":
                identifiers.add(_tree_text(original, node).decode("utf-8"))
            stack.extend(node.children)
        import_alias = "__nougen_udct_os"
        suffix = 2
        while import_alias in identifiers:
            import_alias = f"__nougen_udct_os_{suffix}"
            suffix += 1
        os_name = import_alias

    rule_by_id = {rule["id"]: rule for rule in rules}
    by_location = {(finding.line, finding.column): finding for finding in findings}
    starts = [0]
    starts.extend(index + 1 for index, byte in enumerate(original) if byte == 0x0A)
    candidates: dict[tuple[int, int], Any] = {}
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "interpreted_string_literal" and _is_go_runtime_initializer(node):
            row = node.start_point.row
            column = len(original[starts[row]:node.start_byte + 1].decode("utf-8")) + 1
            candidates[(row + 1, column)] = node
        stack.extend(node.children)

    edits: list[tuple[int, int, bytes]] = []
    for location, finding in by_location.items():
        node = candidates.get(location)
        if node is None:
            continue
        rule = rule_by_id[finding.rule_id]
        token = _tree_text(original, node)
        literal = rule["literal"]
        if len(token) < 2 or token[:1] != b'"' or token[-1:] != b'"' or token[1:-1] != literal:
            continue
        slot_literal = json.dumps(rule["slot"], ensure_ascii=True)
        message_literal = json.dumps(rule["slot"] + " must be set", ensure_ascii=True)
        replacement = (
            f"func() string {{ value, ok := {os_name}.LookupEnv({slot_literal}); "
            f"if !ok {{ panic({message_literal}) }}; return value }}()"
        ).encode("ascii")
        edits.append((node.start_byte, node.end_byte, replacement))

    if not edits:
        return None, 0, bool(findings), original
    rewritten = original
    for start, end, replacement in sorted(edits, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    if not has_os_import:
        package = next((node for node in tree.root_node.children if node.type == "package_clause"), None)
        if package is None:
            raise ValueError(f"cannot safely transform {relative}: package clause is unavailable")
        insertion = package.end_byte
        newline = b"\r\n" if b"\r\n" in original else b"\n"
        assert import_alias is not None
        import_line = f'import {import_alias} "os"'.encode("ascii")
        rewritten = rewritten[:insertion] + newline + import_line + rewritten[insertion:]
    checked = parser.parse(rewritten)
    if checked is None or checked.root_node.has_error:
        raise ValueError(f"cannot safely transform {relative}: generated Go syntax is invalid")
    return rewritten.decode("utf-8"), len(edits), len(edits) != len(by_location), original


def _is_java_runtime_initializer(node: Any) -> bool:
    parent = node.parent
    if parent is None:
        return False
    if parent.type == "variable_declarator" and parent.child_by_field_name("value") == node:
        declaration = parent.parent
        if declaration is None:
            return False
        if declaration.type not in {"local_variable_declaration", "field_declaration"}:
            return False
        modifiers = declaration.child_by_field_name("modifiers")
        if modifiers is None:
            modifiers = next((child for child in declaration.children if child.type == "modifiers"), None)
        if modifiers is not None and b"final" in modifiers.text:
            # A final primitive/String variable can be a compile-time constant.
            return False
        ancestor = declaration.parent
        while ancestor is not None:
            if ancestor.type == "interface_declaration":
                # Interface fields are implicitly public static final.
                return False
            ancestor = ancestor.parent
        return True
    return parent.type == "assignment_expression" and parent.child_by_field_name("right") == node


def _java_declares_identifier(root: Any, source: bytes, name: str) -> bool:
    """Conservatively avoid generated fully-qualified names captured by locals."""
    declaration_types = {
        "formal_parameter", "spread_parameter", "variable_declarator",
        "catch_formal_parameter", "resource", "enhanced_for_statement",
        "class_declaration", "interface_declaration", "enum_declaration",
        "record_declaration", "record_component", "enum_constant",
        "annotation_type_declaration",
    }
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type in declaration_types:
            declared = node.child_by_field_name("name")
            if declared is not None and _tree_text(source, declared).decode("utf-8") == name:
                return True
        stack.extend(node.children)
    return False


def _prepare_java_file(
    path: Path, relative: str, rules: list[dict[str, Any]], findings: list[Any]
) -> tuple[str | None, int, bool, bytes]:
    original = path.read_bytes()
    if len(original) > 1_000_000:
        raise ValueError(f"cannot safely transform {relative}: source exceeds the 1 MB parser limit")
    try:
        original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"cannot safely transform {relative}: source is not UTF-8") from exc
    parser = _tree_sitter_parser(path)
    tree = parser.parse(original)
    if tree is None or tree.root_node.has_error:
        raise ValueError(f"cannot safely transform {relative}: invalid or unsupported Java syntax")

    if _java_declares_identifier(tree.root_node, original, "java"):
        return None, 0, bool(findings), original

    rule_by_id = {rule["id"]: rule for rule in rules}
    by_location = {(finding.line, finding.column): finding for finding in findings}
    starts = [0]
    starts.extend(index + 1 for index, byte in enumerate(original) if byte == 0x0A)
    candidates: dict[tuple[int, int], Any] = {}
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "string_literal" and _is_java_runtime_initializer(node):
            row = node.start_point.row
            column = len(original[starts[row]:node.start_byte + 1].decode("utf-8")) + 1
            candidates[(row + 1, column)] = node
        stack.extend(node.children)

    edits: list[tuple[int, int, bytes]] = []
    for location, finding in by_location.items():
        node = candidates.get(location)
        if node is None:
            continue
        rule = rule_by_id[finding.rule_id]
        token = _tree_text(original, node)
        literal = rule["literal"]
        if len(token) < 2 or token[:1] != b'"' or token[-1:] != b'"':
            continue
        if token[1:-1] != literal or b"\\" in token:
            continue
        slot_literal = json.dumps(rule["slot"], ensure_ascii=True)
        message_literal = json.dumps(rule["slot"] + " must be set", ensure_ascii=True)
        replacement = (
            f"java.util.Objects.requireNonNull(java.lang.System.getenv({slot_literal}), {message_literal})"
        ).encode("ascii")
        edits.append((node.start_byte, node.end_byte, replacement))

    if not edits:
        return None, 0, bool(findings), original
    rewritten = original
    for start, end, replacement in sorted(edits, reverse=True):
        rewritten = rewritten[:start] + replacement + rewritten[end:]
    checked = parser.parse(rewritten)
    if checked is None or checked.root_node.has_error:
        raise ValueError(f"cannot safely transform {relative}: generated Java syntax is invalid")
    return rewritten.decode("utf-8"), len(edits), len(edits) != len(by_location), original


def apply_dynamic_resolutions(
    root: str | Path,
    policy: str | Path = ".udct-policy.json",
    *,
    write: bool = False,
    confirm: str | None = None,
) -> ApplyReport:
    """Prepare or explicitly write exact policy-backed Python, JS/TS, Go and Java rewrites.

    The default is a value-free preview. Writes are limited to a local Git root,
    supported source files with exact syntax-backed matches, and clean targets.
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
        suffix = path.suffix.lower()
        if suffix in {".py", ".pyi"}:
            content, count, has_unresolved, original_bytes = _prepare_file(path, relative, rules, file_findings)
        elif suffix in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}:
            content, count, has_unresolved, original_bytes = _prepare_js_ts_file(
                path, relative, rules, file_findings
            )
        elif suffix == ".go":
            content, count, has_unresolved, original_bytes = _prepare_go_file(
                path, relative, rules, file_findings
            )
        elif suffix == ".java":
            content, count, has_unresolved, original_bytes = _prepare_java_file(
                path, relative, rules, file_findings
            )
        else:
            unresolved.add(relative)
            continue
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
