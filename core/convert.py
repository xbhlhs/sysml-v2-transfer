from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET
from textwrap import wrap
from typing import Any

@dataclass
class SysMLModel:
    elements: dict[str, Any]

    def __init__(self, elements: dict[str, Any] | None = None) -> None:
        self.elements = elements or {}

    def to_dict(self) -> dict[str, Any]:
        return {"elements": self.elements}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SysMLModel":
        return cls(elements=payload.get("elements", {}))


def _strip_inline_comment(line: str) -> str:
    comment_start = line.find("//")
    if comment_start >= 0:
        return line[:comment_start].rstrip()
    return line


def _classify_statement(statement: str) -> str:
    lowered = statement.lower()
    if lowered.startswith("package "):
        return "package"
    if " def " in f" {lowered} " or lowered.startswith("def "):
        return "definition"
    if "->" in statement or "connect" in lowered:
        return "relationship"
    return "statement"


def code_to_graphics(sysml_code: str) -> dict[str, Any]:
    """Convert SysML v2 textual code to a simple graphics model."""
    statements = [
        _strip_inline_comment(line).strip()
        for line in sysml_code.splitlines()
    ]
    statements = [line for line in statements if line]
    if not statements:
        statements = ["empty model"]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for index, statement in enumerate(statements):
        kind = _classify_statement(statement)
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
        "title": next(
            (
                statement.split(maxsplit=1)[1].replace("{", "").replace("}", "").strip()
                for statement in statements
                if statement.lower().startswith("package ")
            ),
            "SysML v2 model",
        ),
        "nodes": nodes,
        "edges": edges,
    }


def graphics_to_svg(graphics_model: dict[str, Any]) -> str:
    """Render the graphics model as a minimal SVG diagram."""
    nodes = graphics_model.get("nodes", [])
    edges = graphics_model.get("edges", [])
    width = 560
    height = max(180, 100 + max(len(nodes), 1) * 100)
    title = str(graphics_model.get("title", "SysML v2 Transfer"))

    node_index = {node["id"]: node for node in nodes}
    svg = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(width),
            "height": str(height),
            "viewBox": f"0 0 {width} {height}",
        },
    )

    ET.SubElement(
        svg,
        "rect",
        {
            "x": "0",
            "y": "0",
            "width": "100%",
            "height": "100%",
            "fill": "#f8fafc",
        },
    )
    title_node = ET.SubElement(
        svg,
        "text",
        {
            "x": "24",
            "y": "28",
            "font-family": "Arial, sans-serif",
            "font-size": "18",
            "font-weight": "bold",
            "fill": "#0f172a",
        },
    )
    title_node.text = title

    for edge in edges:
        source = node_index.get(edge.get("source"))
        target = node_index.get(edge.get("target"))
        if not source or not target:
            continue
        x1 = source["x"] + source["width"] / 2
        y1 = source["y"] + source["height"]
        x2 = target["x"] + target["width"] / 2
        y2 = target["y"]
        ET.SubElement(
            svg,
            "line",
            {
                "x1": str(x1),
                "y1": str(y1),
                "x2": str(x2),
                "y2": str(y2),
                "stroke": "#64748b",
                "stroke-width": "2",
            },
        )

    for node in nodes:
        x = node["x"]
        y = node["y"]
        width = node["width"]
        height = node["height"]
        label = str(node.get("label", ""))
        kind = str(node.get("kind", "statement"))
        fill = {
            "package": "#dbeafe",
            "definition": "#dcfce7",
            "relationship": "#fef3c7",
            "statement": "#ffffff",
        }.get(kind, "#ffffff")
        text_lines = wrap(label, width=42) or [label]
        group = ET.SubElement(svg, "g")
        ET.SubElement(
            group,
            "rect",
            {
                "x": str(x),
                "y": str(y),
                "rx": "12",
                "ry": "12",
                "width": str(width),
                "height": str(height),
                "fill": fill,
                "stroke": "#0f172a",
                "stroke-width": "1.5",
            },
        )
        text_y = y + 28
        for line_index, text_line in enumerate(text_lines[:2]):
            text_node = ET.SubElement(
                group,
                "text",
                {
                    "x": str(x + 16),
                    "y": str(text_y + line_index * 18),
                    "font-family": "Arial, sans-serif",
                    "font-size": "14",
                    "fill": "#0f172a",
                },
            )
            text_node.text = text_line

    return ET.tostring(svg, encoding="utf-8", xml_declaration=True).decode("utf-8")


def graphics_to_code(graphics_model: dict[str, Any]) -> str:
    """Convert graphics representation back to SysML v2 textual code."""
    return graphics_model.get("content", "")
