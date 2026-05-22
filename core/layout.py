"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

import re
from typing import Any

from .ast import AstNode, DefinitionNode, FlowNode, PackageNode, SysMLDocument, UnknownNode, UsageNode
from .parser import parse_sysml
from .text_layout import wrap_text


_DOC_BLOCK_RE = re.compile(r"doc\s*/\*(.*?)\*/", re.IGNORECASE | re.DOTALL)


def strip_inline_comment(line: str) -> str:
    comment_start = line.find("//")
    if comment_start >= 0:
        return line[:comment_start].rstrip()
    return line


def extract_doc_blocks(sysml_code: str) -> tuple[str, list[str]]:
    docs: list[str] = []

    def replace(match: re.Match[str]) -> str:
        docs.append(" ".join(match.group(1).split()))
        return f"doc __DOC_{len(docs) - 1}__"

    return _DOC_BLOCK_RE.sub(replace, sysml_code), docs


def normalize_statement(statement: str) -> str:
    cleaned = strip_inline_comment(statement).strip()
    if not cleaned:
        return ""
    if cleaned in {"{", "}", ";", "{}"}:
        return ""
    cleaned = cleaned.rstrip(";").strip()
    cleaned = cleaned.rstrip("{").strip()
    cleaned = cleaned.rstrip("}").strip()
    return cleaned


def classify_statement(statement: str) -> str:
    lowered = statement.lower()
    if lowered.startswith("package "):
        return "package"
    if lowered.startswith(("item ", "part ", "port ", "action ", "state ", "connection ")):
        return "definition"
    if " def " in f" {lowered} " or lowered.startswith("def "):
        return "definition"
    if lowered.startswith("flow ") or "->" in statement or "connect" in lowered:
        return "relationship"
    return "statement"


def extract_label(statement: str) -> str:
    lowered = statement.lower()
    if lowered.startswith("package "):
        title = statement.split(maxsplit=1)[1]
        return title.replace("{", "").replace("}", "").strip()

    patterns = [
        r"^(?:item|part|port|action|state|connection)\s+def\s+([A-Za-z_][\w.]*)",
        r"^(?:item|part|port|action|state|connection)\s+([A-Za-z_][\w.]*)",
        r"^def\s+([A-Za-z_][\w.]*)",
        r"^flow\s+of\s+([A-Za-z_][\w.]*)",
    ]
    for pattern in patterns:
        match = re.match(pattern, statement, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    if "->" in statement:
        return statement.split("->", maxsplit=1)[0].strip()
    if ":" in statement:
        return statement.split(":", maxsplit=1)[0].strip()
    return statement


def extract_kind_tag(statement: str) -> str:
    lowered = statement.lower()
    if lowered.startswith("package "):
        return "package"
    if lowered.startswith("item def "):
        return "item def"
    if lowered.startswith("part def "):
        return "part def"
    if lowered.startswith("port def "):
        return "port def"
    if lowered.startswith("action def "):
        return "action def"
    if lowered.startswith("state def "):
        return "state def"
    if lowered.startswith("connection def "):
        return "connection def"
    if lowered.startswith("item "):
        return "item"
    if lowered.startswith("part "):
        return "part"
    if lowered.startswith("port "):
        return "port"
    if lowered.startswith("action "):
        return "action"
    if lowered.startswith("state "):
        return "state"
    if lowered.startswith("connection "):
        return "connection"
    if lowered.startswith("flow "):
        return "flow"
    if lowered.startswith("def "):
        return "def"
    if "->" in statement or "connect" in lowered:
        return "relation"
    return "statement"


def extract_secondary_label(statement: str) -> str:
    lowered = statement.lower()
    if lowered.startswith("package "):
        return ""
    if ":" in statement and not lowered.startswith("flow "):
        remainder = statement.split(":", maxsplit=1)[1].strip()
        if remainder:
            return f": {remainder}"
    return ""


def estimate_card_width(title: str, kind_tag: str, documentation: str, secondary_label: str) -> int:
    title_part = len(title) * 11
    kind_part = len(kind_tag) * 8
    secondary_part = len(secondary_label) * 7
    doc_part = max((len(line) for line in documentation.splitlines()), default=0) * 6
    width = max(260, 24 + max(title_part, kind_part, secondary_part, doc_part))
    return min(360, width)


def estimate_package_height(title: str, width: int) -> int:
    chars_per_line = max(18, (width - 32) // 7)
    title_lines = wrap_text(title, chars_per_line)
    height = 16
    height += 16
    height += len(title_lines) * 22
    height += 16
    return max(76, height)


def estimate_card_height(
    title: str,
    kind_tag: str,
    documentation: str,
    secondary_label: str,
    width: int,
) -> int:
    chars_per_line = max(18, (width - 32) // 7)
    title_lines = wrap_text(title, chars_per_line)
    secondary_lines = wrap_text(secondary_label, chars_per_line) if secondary_label else []
    doc_lines = wrap_text(documentation, chars_per_line) if documentation else []

    height = 16
    height += 16
    height += len(title_lines) * 22
    if secondary_lines:
        height += 18 * len(secondary_lines)
    if doc_lines:
        height += 14
        height += len(doc_lines) * 18
    height += 16
    return max(72, height)


def extract_title(statements: list[str]) -> str:
    for statement in statements:
        if statement.lower().startswith("package "):
            title = statement.split(maxsplit=1)[1]
            return title.replace("{", "").replace("}", "").strip()
    return "SysML v2 model"


def build_graphics_model_from_ast(document: SysMLDocument, sysml_code: str) -> dict[str, Any]:
    if document.package is None:
        return _build_graphics_model_from_statements(sysml_code)

    flat_nodes = _flatten_ast(document.package)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    content_y = 48

    for index, item in enumerate(flat_nodes):
        kind = item["kind"]
        kind_tag = item["kind_tag"]
        title = item["label"]
        secondary_label = item.get("secondary_label", "")
        documentation = item.get("documentation", "")

        if kind == "package":
            width = 520
            height = estimate_package_height(title, width)
            x = 20
            y = 48
            content_y = y + height + 32
        elif kind == "definition":
            width = estimate_card_width(title, kind_tag, documentation, secondary_label)
            height = estimate_card_height(title, kind_tag, documentation, secondary_label, width)
            x = 40
            y = content_y
            content_y += height + 24
        elif kind == "relationship":
            width = min(360, max(260, 18 + len(title) * 7))
            height = 56
            x = 72
            y = content_y
            content_y += height + 20
        else:
            width = estimate_card_width(title, kind_tag, documentation, secondary_label)
            height = estimate_card_height(title, kind_tag, documentation, secondary_label, width)
            x = 40
            y = content_y
            content_y += height + 20

        node = {
            "id": f"node-{index}",
            "label": title,
            "kind": kind,
            "kind_tag": kind_tag,
            "secondary_label": secondary_label,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        if documentation:
            node["documentation"] = documentation
        nodes.append(node)

        if index > 0:
            edges.append(
                {
                    "id": f"edge-{index - 1}-{index}",
                    "source": f"node-{index - 1}",
                    "target": f"node-{index}",
                }
            )

    return {
        "type": "sysml-diagram",
        "content": sysml_code,
        "title": document.package.name,
        "nodes": nodes,
        "edges": edges,
    }


def _flatten_ast(package: PackageNode) -> list[dict[str, str]]:
    result: list[dict[str, str]] = [
        {
            "kind": "package",
            "kind_tag": "package",
            "label": package.name,
            "documentation": package.documentation,
        }
    ]
    for member in package.members:
        result.extend(_flatten_member(member))
    return result


def _flatten_member(member: AstNode) -> list[dict[str, str]]:
    if isinstance(member, DefinitionNode):
        rows = [
            {
                "kind": "definition",
                "kind_tag": f"{member.keyword} def",
                "label": member.name,
                "documentation": member.documentation,
            }
        ]
        for child in member.members:
            rows.extend(_flatten_child(child, owner=member.name))
        return rows
    if isinstance(member, UsageNode):
        return [_usage_row(member)]
    if isinstance(member, FlowNode):
        return [_flow_row(member)]
    if isinstance(member, PackageNode):
        return _flatten_ast(member)
    if isinstance(member, UnknownNode):
        return [{"kind": "statement", "kind_tag": "statement", "label": member.text, "documentation": ""}]
    return []


def _flatten_child(child: AstNode, *, owner: str) -> list[dict[str, str]]:
    if isinstance(child, UsageNode):
        row = _usage_row(child)
        row["secondary_label"] = f"{owner} / : {child.type_name}"
        return [row]
    if isinstance(child, FlowNode):
        return [_flow_row(child)]
    if isinstance(child, DefinitionNode):
        return _flatten_member(child)
    if isinstance(child, UnknownNode):
        return [{"kind": "statement", "kind_tag": "statement", "label": child.text, "documentation": ""}]
    return []


def _usage_row(node: UsageNode) -> dict[str, str]:
    return {
        "kind": "definition",
        "kind_tag": node.keyword,
        "label": node.name,
        "secondary_label": f": {node.type_name}",
        "documentation": node.documentation,
    }


def _flow_row(node: FlowNode) -> dict[str, str]:
    return {
        "kind": "relationship",
        "kind_tag": "flow",
        "label": node.item_type,
        "secondary_label": f"{node.source} -> {node.target}",
        "documentation": "",
    }


def build_graphics_model(sysml_code: str) -> dict[str, Any]:
    document = parse_sysml(sysml_code)
    if document.package is not None:
        return build_graphics_model_from_ast(document, sysml_code)
    return _build_graphics_model_from_statements(sysml_code)


def _build_graphics_model_from_statements(sysml_code: str) -> dict[str, Any]:
    stripped_code, doc_blocks = extract_doc_blocks(sysml_code)
    statements: list[str] = []
    statement_docs: list[str] = []
    flow_buffer: list[str] = []

    for raw_line in stripped_code.splitlines():
        line = normalize_statement(raw_line)
        if not line:
            if flow_buffer:
                statements.append(" ".join(flow_buffer))
                statement_docs.append("")
                flow_buffer = []
            continue

        lowered = line.lower()
        if lowered.startswith("doc __doc_"):
            match = re.search(r"__doc_(\d+)__", lowered)
            if match:
                doc_index = int(match.group(1))
                if 0 <= doc_index < len(doc_blocks):
                    if statement_docs:
                        statement_docs[-1] = " ".join(
                            doc for doc in [statement_docs[-1], doc_blocks[doc_index]] if doc
                        )
            continue
        if lowered.startswith("flow of") or (flow_buffer and lowered.startswith(("from ", "to "))):
            flow_buffer.append(line)
            continue

        if flow_buffer:
            statements.append(" ".join(flow_buffer))
            statement_docs.append("")
            flow_buffer = []

        statements.append(line)
        statement_docs.append("")

    if flow_buffer:
        statements.append(" ".join(flow_buffer))
        statement_docs.append("")

    if not statements:
        statements = ["empty model"]
        statement_docs = [""]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    content_y = 48
    package_seen = False

    for index, statement in enumerate(statements):
        kind = classify_statement(statement)
        kind_tag = extract_kind_tag(statement)
        title = extract_label(statement)
        secondary_label = extract_secondary_label(statement)
        documentation = statement_docs[index].strip()
        if kind == "package" and not package_seen:
            width = 520
            height = estimate_package_height(title, width)
            x = 20
            y = 48
            content_y = y + height + 32
            package_seen = True
            display_label = title
        elif kind == "definition":
            width = estimate_card_width(title, kind_tag, documentation, secondary_label)
            height = estimate_card_height(title, kind_tag, documentation, secondary_label, width)
            x = 40
            y = content_y
            content_y += height + 24
            display_label = title
        elif kind == "relationship":
            width = min(360, max(260, 18 + len(title) * 7))
            height = 56
            x = 72
            y = content_y
            content_y += height + 20
            display_label = title
        else:
            width = estimate_card_width(title, kind_tag, documentation, secondary_label)
            height = estimate_card_height(title, kind_tag, documentation, secondary_label, width)
            x = 40
            y = content_y
            content_y += height + 20
            display_label = title

        nodes.append(
            {
                "id": f"node-{index}",
                "label": display_label,
                "kind": kind,
                "kind_tag": kind_tag,
                "secondary_label": secondary_label,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        )
        if statement_docs[index]:
            nodes[-1]["documentation"] = statement_docs[index]
        if index > 0:
            edges.append(
                {
                    "id": f"edge-{index - 1}-{index}",
                    "source": f"node-{index - 1}",
                    "target": f"node-{index}",
                }
            )

    return {
        "type": "sysml-diagram",
        "content": sysml_code,
        "title": extract_title(statements),
        "nodes": nodes,
        "edges": edges,
    }
