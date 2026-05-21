from __future__ import annotations

from typing import Any


def strip_inline_comment(line: str) -> str:
    comment_start = line.find("//")
    if comment_start >= 0:
        return line[:comment_start].rstrip()
    return line


def classify_statement(statement: str) -> str:
    lowered = statement.lower()
    if lowered.startswith("package "):
        return "package"
    if " def " in f" {lowered} " or lowered.startswith("def "):
        return "definition"
    if "->" in statement or "connect" in lowered:
        return "relationship"
    return "statement"


def extract_title(statements: list[str]) -> str:
    for statement in statements:
        if statement.lower().startswith("package "):
            title = statement.split(maxsplit=1)[1]
            return title.replace("{", "").replace("}", "").strip()
    return "SysML v2 model"


def build_graphics_model(sysml_code: str) -> dict[str, Any]:
    statements = [strip_inline_comment(line).strip() for line in sysml_code.splitlines()]
    statements = [line for line in statements if line]
    if not statements:
        statements = ["empty model"]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    content_y = 48
    package_seen = False

    for index, statement in enumerate(statements):
        kind = classify_statement(statement)
        if kind == "package" and not package_seen:
            width = 520
            height = 76
            x = 20
            y = 48
            content_y = 156
            package_seen = True
            display_label = extract_title([statement])
        elif kind == "definition":
            width = min(480, max(320, 18 + len(statement) * 8))
            height = 64
            x = 40
            y = content_y
            content_y += 96
            display_label = statement
        elif kind == "relationship":
            width = min(440, max(300, 18 + len(statement) * 7))
            height = 44
            x = 72
            y = content_y
            content_y += 72
            display_label = statement
        else:
            width = min(480, max(300, 18 + len(statement) * 8))
            height = 56
            x = 40
            y = content_y
            content_y += 88
            display_label = statement

        nodes.append(
            {
                "id": f"node-{index}",
                "label": display_label,
                "kind": kind,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        )
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
