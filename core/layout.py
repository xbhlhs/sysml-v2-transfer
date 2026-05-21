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
    for index, statement in enumerate(statements):
        kind = classify_statement(statement)
        width = min(420, max(260, 16 + len(statement) * 8))
        nodes.append(
            {
                "id": f"node-{index}",
                "label": statement,
                "kind": kind,
                "x": 40,
                "y": 40 + index * 100,
                "width": width,
                "height": 56,
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

