from __future__ import annotations

from dataclasses import dataclass
from html import escape
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


def code_to_graphics(sysml_code: str) -> dict[str, Any]:
    """Convert SysML v2 textual code to a simple graphics model."""
    lines = [line.strip() for line in sysml_code.splitlines() if line.strip()]
    if not lines:
        lines = ["empty model"]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for index, label in enumerate(lines):
        nodes.append(
            {
                "id": f"node-{index}",
                "label": label,
                "x": 40,
                "y": 40 + index * 100,
                "width": 360,
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
        "nodes": nodes,
        "edges": edges,
    }


def graphics_to_svg(graphics_model: dict[str, Any]) -> str:
    """Render the graphics model as a minimal SVG diagram."""
    nodes = graphics_model.get("nodes", [])
    edges = graphics_model.get("edges", [])
    width = 440
    height = max(180, 80 + max(len(nodes), 1) * 100)

    node_index = {node["id"]: node for node in nodes}
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="24" y="28" font-family="Arial, sans-serif" font-size="18" fill="#0f172a">SysML v2 Transfer</text>',
    ]

    for edge in edges:
        source = node_index.get(edge.get("source"))
        target = node_index.get(edge.get("target"))
        if not source or not target:
            continue
        x1 = source["x"] + source["width"] / 2
        y1 = source["y"] + source["height"]
        x2 = target["x"] + target["width"] / 2
        y2 = target["y"]
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#64748b" stroke-width="2"/>'
        )

    for node in nodes:
        x = node["x"]
        y = node["y"]
        width = node["width"]
        height = node["height"]
        label = escape(str(node.get("label", "")))
        parts.append(
            f'<g><rect x="{x}" y="{y}" rx="12" ry="12" width="{width}" height="{height}" fill="#ffffff" stroke="#0f172a" stroke-width="1.5"/>'
            f'<text x="{x + 16}" y="{y + 34}" font-family="Arial, sans-serif" font-size="14" fill="#0f172a">{label}</text></g>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def graphics_to_code(graphics_model: dict[str, Any]) -> str:
    """Convert graphics representation back to SysML v2 textual code."""
    return graphics_model.get("content", "")
