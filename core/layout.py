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


def estimate_row_height(text: str, width: int) -> int:
    chars_per_line = max(18, (width - 28) // 7)
    lines = wrap_text(text, chars_per_line)
    height = 10
    height += len(lines) * 18
    height += 8
    return max(26, height)


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
    children_by_parent_key: dict[str, list[dict[str, str]]] = {}
    for row in flat_nodes[1:]:
        children_by_parent_key.setdefault(str(row.get("parent_key", "")), []).append(row)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_lookup: dict[str, str] = {}

    package_row = flat_nodes[0]
    view_title = package_row["label"]
    content_y = 64
    content_y = _layout_rows(
        children_by_parent_key,
        parent_key=str(package_row["node_key"]),
        parent_id="",
        x=40,
        y=content_y,
        width_limit=500,
        nodes=nodes,
        node_lookup=node_lookup,
        edges=edges,
    )

    _reflow_top_level_groups(nodes, view_title, node_lookup)
    edges = []

    return {
        "type": "sysml-diagram",
        "content": sysml_code,
        "title": f"Definition View of {view_title}",
        "nodes": nodes,
        "edges": edges,
    }


def _layout_rows(
    children_by_parent_key: dict[str, list[dict[str, str]]],
    *,
    parent_key: str,
    parent_id: str,
    x: int,
    y: int,
    width_limit: int,
    nodes: list[dict[str, Any]],
    node_lookup: dict[str, str],
    edges: list[dict[str, Any]],
) -> int:
    cursor_y = y
    for row in children_by_parent_key.get(parent_key, []):
        kind = row["kind"]
        kind_tag = row["kind_tag"]
        title = row["label"]
        secondary_label = row.get("secondary_label", "")
        documentation = row.get("documentation", "")
        node_key = row.get("node_key", "")
        row_parent_key = row.get("parent_key", "")
        node_id = f"node-{len(nodes)}"

        if kind == "definition":
            width = min(width_limit, max(360, estimate_card_width(title, kind_tag, documentation, secondary_label)))
            height = estimate_card_height(title, kind_tag, documentation, secondary_label, width)
            node_x = x
            node_y = cursor_y
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": node_x,
                "y": node_y,
                "width": width,
                "height": height,
            }
            if documentation:
                node["documentation"] = documentation
            nodes.append(node)
            _register_node_lookup(node_lookup, node, row)
            if parent_id and parent_id != node_id:
                edges.append(
                    {
                        "id": f"edge-{parent_id}-{node_id}",
                        "source": parent_id,
                        "target": node_id,
                        "kind": "containment",
                    }
                )

            child_start_y = node_y + height + 14
            child_end_y = _layout_rows(
                children_by_parent_key,
                parent_key=node_key,
                parent_id=node_id,
                x=node_x + 24,
                y=child_start_y,
                width_limit=max(240, width - 36),
                nodes=nodes,
                node_lookup=node_lookup,
                edges=edges,
            )
            node["height"] = max(height, child_end_y - node_y + 12)
            cursor_y = node_y + node["height"] + 20
            continue

        if kind == "section":
            width = min(width_limit, 520)
            height = 26
            node_x = x
            node_y = cursor_y
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": node_x,
                "y": node_y,
                "width": width,
                "height": height,
            }
            nodes.append(node)
            _register_node_lookup(node_lookup, node, row)
            if parent_id and parent_id != node_id:
                edges.append(
                    {
                        "id": f"edge-{parent_id}-{node_id}",
                        "source": parent_id,
                        "target": node_id,
                        "kind": "containment",
                    }
                )

            child_rows = children_by_parent_key.get(node_key, [])
            if child_rows and all(child_row.get("kind") in {"usage", "relationship", "statement"} for child_row in child_rows):
                child_end_y = _layout_section_children_grid(
                    child_rows,
                    parent_key=node_key,
                    parent_id=node_id,
                    x=node_x + 12,
                    y=node_y + height + 8,
                    width_limit=max(220, width - 24),
                    nodes=nodes,
                    node_lookup=node_lookup,
                    edges=edges,
                )
            else:
                child_end_y = _layout_rows(
                    children_by_parent_key,
                    parent_key=node_key,
                    parent_id=node_id,
                    x=node_x + 18,
                    y=node_y + height + 8,
                    width_limit=max(220, width - 24),
                    nodes=nodes,
                    node_lookup=node_lookup,
                    edges=edges,
                )
            node["height"] = height
            cursor_y = child_end_y + 8
            continue

        if kind == "usage":
            row_text = f"{title}{secondary_label}"
            width = min(width_limit, max(260, 18 + len(row_text) * 7))
            height = estimate_row_height(row_text, width)
            node_x = x
            node_y = cursor_y
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "subtype": row.get("subtype", ""),
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": node_x,
                "y": node_y,
                "width": width,
                "height": height,
            }
            if documentation:
                node["documentation"] = documentation
            nodes.append(node)
            _register_node_lookup(node_lookup, node, row)
            cursor_y = node_y + height + 8
            continue

        if kind == "relationship":
            row_text = f"{title} {secondary_label}".strip()
            width = min(width_limit, max(260, 18 + len(row_text) * 7))
            height = estimate_row_height(row_text, width)
            node_x = x
            node_y = cursor_y
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": node_x,
                "y": node_y,
                "width": width,
                "height": height,
                "flow_source": row.get("flow_source", ""),
                "flow_target": row.get("flow_target", ""),
            }
            if documentation:
                node["documentation"] = documentation
            nodes.append(node)
            _register_node_lookup(node_lookup, node, row)
            cursor_y = node_y + height + 8
            continue

        width = min(width_limit, max(260, 18 + len(title) * 7))
        height = estimate_card_height(title, kind_tag, documentation, secondary_label, width)
        node_x = x
        node_y = cursor_y
        node = {
            "id": node_id,
            "label": title,
            "kind": kind,
            "kind_tag": kind_tag,
            "secondary_label": secondary_label,
            "node_key": node_key,
            "parent_key": row_parent_key,
            "x": node_x,
            "y": node_y,
            "width": width,
            "height": height,
        }
        if documentation:
            node["documentation"] = documentation
        nodes.append(node)
        _register_node_lookup(node_lookup, node, row)
        if parent_id and parent_id != node_id:
            edges.append(
                {
                    "id": f"edge-{parent_id}-{node_id}",
                    "source": parent_id,
                    "target": node_id,
                    "kind": "containment",
                }
            )
        cursor_y = node_y + height + 16

    return cursor_y


def _layout_section_children_grid(
    child_rows: list[dict[str, str]],
    *,
    parent_key: str,
    parent_id: str,
    x: int,
    y: int,
    width_limit: int,
    nodes: list[dict[str, Any]],
    node_lookup: dict[str, str],
    edges: list[dict[str, Any]],
) -> int:
    if not child_rows:
        return y

    built_nodes: list[dict[str, Any]] = []
    for row in child_rows:
        kind = row["kind"]
        kind_tag = row["kind_tag"]
        title = row["label"]
        secondary_label = row.get("secondary_label", "")
        documentation = row.get("documentation", "")
        node_key = row.get("node_key", "")
        row_parent_key = row.get("parent_key", parent_key)
        node_id = f"node-{len(nodes)}"
        row_text = f"{title}{secondary_label}" if kind == "usage" else f"{title} {secondary_label}".strip()

        if kind == "usage":
            width = max(260, width_limit - 24)
            height = estimate_row_height(row_text, width)
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "subtype": row.get("subtype", ""),
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
            if documentation:
                node["documentation"] = documentation
        elif kind == "relationship":
            width = max(260, width_limit - 24)
            height = estimate_row_height(row_text, width)
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "flow_source": row.get("flow_source", ""),
                "flow_target": row.get("flow_target", ""),
            }
            if documentation:
                node["documentation"] = documentation
        else:
            width = max(260, width_limit - 24)
            height = estimate_row_height(row_text, width)
            node = {
                "id": node_id,
                "label": title,
                "kind": kind,
                "kind_tag": kind_tag,
                "secondary_label": secondary_label,
                "node_key": node_key,
                "parent_key": row_parent_key,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
            if documentation:
                node["documentation"] = documentation

        nodes.append(node)
        _register_node_lookup(node_lookup, node, row)
        built_nodes.append(node)
    cursor_y = float(y)
    row_gap = 6.0
    for node in built_nodes:
        node["x"] = float(x)
        node["y"] = cursor_y
        cursor_y += float(node["height"]) + row_gap

    return int(cursor_y)


def _flatten_ast(package: PackageNode) -> list[dict[str, str]]:
    result: list[dict[str, str]] = [
        {
            "kind": "package",
            "kind_tag": "package",
            "label": package.name,
            "documentation": package.documentation,
            "node_key": _package_key(package.name),
            "parent_key": "",
        }
    ]
    for member in package.members:
        result.extend(_flatten_member(member, owner_key=_package_key(package.name)))
    return result


def _flatten_member(member: AstNode, *, owner_key: str) -> list[dict[str, str]]:
    if isinstance(member, DefinitionNode):
        rows = [
            {
                "kind": "definition",
                "kind_tag": f"{member.keyword} def",
                "label": member.name,
                "documentation": member.documentation,
                "node_key": _definition_key(member.keyword, member.name, owner_key),
                "parent_key": owner_key,
            }
        ]
        rows.extend(_flatten_definition_members(member, owner_key=rows[0]["node_key"]))
        return rows
    if isinstance(member, UsageNode):
        return [_usage_row(member, owner_key=owner_key)]
    if isinstance(member, FlowNode):
        return [_flow_row(member, owner_key=owner_key)]
    if isinstance(member, PackageNode):
        return _flatten_ast(member)
    if isinstance(member, UnknownNode):
        return [
            {
                "kind": "statement",
                "kind_tag": "statement",
                "label": member.text,
                "documentation": "",
                "node_key": _statement_key(member.text, owner_key),
                "parent_key": owner_key,
            }
        ]
    return []


def _flatten_child(child: AstNode, *, owner: str) -> list[dict[str, str]]:
    if isinstance(child, UsageNode):
        row = _usage_row(child, owner_key=owner)
        row["secondary_label"] = f"{owner} / : {child.type_name}"
        return [row]
    if isinstance(child, FlowNode):
        return [_flow_row(child, owner_key=owner)]
    if isinstance(child, DefinitionNode):
        return _flatten_member(child, owner_key=owner)
    if isinstance(child, UnknownNode):
        return [
            {
                "kind": "statement",
                "kind_tag": "statement",
                "label": child.text,
                "documentation": "",
                "node_key": _statement_key(child.text, owner),
                "parent_key": owner,
            }
        ]
    return []


def _flatten_definition_members(member: DefinitionNode, *, owner_key: str) -> list[dict[str, str]]:
    groups: list[tuple[str, list[dict[str, str]]]] = [
        ("Ports", []),
        ("Parts", []),
        ("Flows", []),
        ("Members", []),
    ]

    for child in member.members:
        if isinstance(child, UsageNode) and child.keyword == "port":
            groups[0][1].append(_usage_row(child, owner_key=_section_key(owner_key, "Ports")))
            continue
        if isinstance(child, UsageNode) and child.keyword == "part":
            groups[1][1].append(_usage_row(child, owner_key=_section_key(owner_key, "Parts")))
            continue
        if isinstance(child, FlowNode):
            groups[2][1].append(_flow_row(child, owner_key=_section_key(owner_key, "Flows")))
            continue
        groups[3][1].extend(_flatten_child(child, owner=owner_key))

    rows: list[dict[str, str]] = []
    for label, group_rows in groups:
        if not group_rows:
            continue
        if label != "Members":
            section_key = _section_key(owner_key, label)
            rows.append(
                {
                    "kind": "section",
                    "kind_tag": "section",
                    "label": label,
                    "documentation": "",
                    "node_key": section_key,
                    "parent_key": owner_key,
                }
            )
            for row in group_rows:
                row["parent_key"] = section_key
        rows.extend(group_rows)
    return rows


def _usage_row(node: UsageNode, *, owner_key: str) -> dict[str, str]:
    return {
        "kind": "usage",
        "kind_tag": node.keyword,
        "label": node.name,
        "secondary_label": f": {node.type_name}",
        "documentation": node.documentation,
        "subtype": node.keyword,
        "node_key": _usage_key(node.keyword, node.name, owner_key),
        "parent_key": owner_key,
    }


def _flow_row(node: FlowNode, *, owner_key: str) -> dict[str, str]:
    return {
        "kind": "relationship",
        "kind_tag": "flow",
        "label": node.item_type,
        "secondary_label": f"{node.source} -> {node.target}",
        "documentation": "",
        "flow_source": node.source,
        "flow_target": node.target,
        "node_key": _flow_key(node.item_type, node.source, node.target, owner_key),
        "parent_key": owner_key,
    }


def _register_node_lookup(node_lookup: dict[str, str], node: dict[str, Any], item: dict[str, str]) -> None:
    label = str(node.get("label", ""))
    kind = str(node.get("kind", ""))
    node_id = str(node["id"])
    node_key = str(node.get("node_key", ""))
    if label:
        node_lookup[label] = node_id
    if kind in {"definition", "package"}:
        node_lookup.setdefault(label, node_id)
    if node_key:
        node_lookup.setdefault(node_key, node_id)
    secondary_label = str(node.get("secondary_label", ""))
    if secondary_label.startswith(": "):
        node_lookup.setdefault(secondary_label[2:], node_id)
    flow_source = item.get("flow_source")
    flow_target = item.get("flow_target")
    if flow_source:
        node_lookup.setdefault(flow_source, node_id)
    if flow_target:
        node_lookup.setdefault(flow_target, node_id)


def _resolve_flow_endpoint(node_lookup: dict[str, str], endpoint: str) -> str | None:
    if endpoint in node_lookup:
        return node_lookup[endpoint]
    if "." in endpoint:
        tail = endpoint.rsplit(".", maxsplit=1)[-1]
        return node_lookup.get(tail)
    return None


def _package_key(name: str) -> str:
    return f"package:{name}"


def _definition_key(keyword: str, name: str, owner_key: str) -> str:
    return f"{owner_key}/definition:{keyword}:{name}"


def _section_key(owner_key: str, label: str) -> str:
    return f"{owner_key}/section:{label}"


def _usage_key(keyword: str, name: str, owner_key: str) -> str:
    return f"{owner_key}/usage:{keyword}:{name}"


def _flow_key(item_type: str, source: str, target: str, owner_key: str) -> str:
    return f"{owner_key}/flow:{item_type}:{source}->{target}"


def _statement_key(text: str, owner_key: str) -> str:
    return f"{owner_key}/statement:{text}"


def _top_level_family_label(kind_tag: str, kind: str) -> str:
    if kind == "usage":
        return "Usages"
    lowered = kind_tag.lower()
    if lowered.startswith(("item def", "part def", "port def", "action def", "state def", "connection def")):
        base = lowered.split()[0]
        return {
            "item": "Item Definitions",
            "part": "Part Definitions",
            "port": "Port Definitions",
            "action": "Action Definitions",
            "state": "State Definitions",
            "connection": "Connection Definitions",
        }.get(base, "Definitions")
    return "Other Elements"


def _reflow_top_level_groups(
    nodes: list[dict[str, Any]],
    package_title: str,
    node_lookup: dict[str, str],
) -> None:
    _ = package_title
    if not nodes:
        return

    child_map: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        parent_key = str(node.get("parent_key", ""))
        if parent_key:
            child_map.setdefault(parent_key, []).append(node)

    package_key = f"package:{package_title}"
    top_level_rows = [
        node
        for node in nodes
        if str(node.get("parent_key", "")) == package_key and node.get("kind") in {"definition", "usage"}
    ]
    if not top_level_rows:
        return

    def descendants(root_key: str) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        stack = list(child_map.get(root_key, []))
        while stack:
            node = stack.pop()
            collected.append(node)
            stack.extend(child_map.get(str(node.get("node_key", "")), []))
        return collected

    column_gap = 24.0
    cursor_x = 40.0
    target_y = 64.0

    for root in top_level_rows:
        group_nodes = [root] + descendants(str(root.get("node_key", "")))
        left = min(float(item["x"]) for item in group_nodes)
        top = min(float(item["y"]) for item in group_nodes)
        right = max(float(item["x"]) + float(item["width"]) for item in group_nodes)
        bottom = max(float(item["y"]) + float(item["height"]) for item in group_nodes)
        group_width = right - left

        dx = cursor_x - left
        dy = target_y - top
        for item in group_nodes:
            item["x"] = float(item["x"]) + dx
            item["y"] = float(item["y"]) + dy

        cursor_x += max(group_width, 360.0) + column_gap


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
            previous_kind = str(nodes[-2]["kind"]) if len(nodes) > 1 else "package"
            edges.append(
                {
                    "id": f"edge-{index - 1}-{index}",
                    "source": f"node-{index - 1}",
                    "target": f"node-{index}",
                    "kind": "containment" if previous_kind == "package" else "sequence",
                }
            )

    return {
        "type": "sysml-diagram",
        "content": sysml_code,
        "title": extract_title(statements),
        "nodes": nodes,
        "edges": edges,
    }
