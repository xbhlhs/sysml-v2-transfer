from __future__ import annotations

import xml.etree.ElementTree as ET
from textwrap import wrap
from typing import Any


def _node_fill(kind: str) -> str:
    return {
        "package": "#bfdbfe",
        "definition": "#dcfce7",
        "relationship": "#f8fafc",
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
        source_kind = str(source.get("kind", "statement"))
        target_kind = str(target.get("kind", "statement"))
        dashed = source_kind == "relationship" or target_kind == "relationship"
        edge_attrs = {
            "x1": str(x1),
            "y1": str(y1),
            "x2": str(x2),
            "y2": str(y2),
            "stroke": "#94a3b8" if dashed else "#64748b",
            "stroke-width": "1.5" if dashed else "2",
        }
        if dashed:
            edge_attrs["stroke-dasharray"] = "6 4"
        ET.SubElement(svg, "line", edge_attrs)

    for node in nodes:
        x = node["x"]
        y = node["y"]
        node_width = node["width"]
        node_height = node["height"]
        label = str(node.get("label", ""))
        kind = str(node.get("kind", "statement"))
        text_lines = wrap(label, width=42) or [label]
        group = ET.SubElement(svg, "g")
        is_package = kind == "package"
        is_relationship = kind == "relationship"
        rect_attrs = {
            "x": str(x),
            "y": str(y),
            "rx": "16" if is_package else "12",
            "ry": "16" if is_package else "12",
            "width": str(node_width),
            "height": str(node_height),
            "fill": _node_fill(kind),
            "stroke": "#0f172a" if not is_relationship else "#94a3b8",
            "stroke-width": "2" if is_package else ("1.25" if is_relationship else "1.5"),
        }
        if is_relationship:
            rect_attrs["stroke-dasharray"] = "6 4"
        ET.SubElement(group, "rect", rect_attrs)
        text_y = y + (44 if is_package else 30)
        font_size = "16" if is_package else ("13" if is_relationship else "14")
        for line_index, text_line in enumerate(text_lines[:2]):
            text_node = ET.SubElement(
                group,
                "text",
                {
                    "x": str(x + 16),
                    "y": str(text_y + line_index * 18),
                    "font-family": "Arial, sans-serif",
                    "font-size": font_size,
                    "fill": "#0f172a",
                    "font-weight": "bold" if is_package else "normal",
                },
            )
            text_node.text = text_line

    return ET.tostring(svg, encoding="utf-8", xml_declaration=True).decode("utf-8")
