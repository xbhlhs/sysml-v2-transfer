from __future__ import annotations

import xml.etree.ElementTree as ET
from textwrap import wrap
from typing import Any


def _node_fill(kind: str) -> str:
    return {
        "package": "#dbeafe",
        "definition": "#dcfce7",
        "relationship": "#fef3c7",
        "statement": "#ffffff",
    }.get(kind, "#ffffff")


def render_svg(graphics_model: dict[str, Any]) -> str:
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
        node_width = node["width"]
        node_height = node["height"]
        label = str(node.get("label", ""))
        kind = str(node.get("kind", "statement"))
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
                "width": str(node_width),
                "height": str(node_height),
                "fill": _node_fill(kind),
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

