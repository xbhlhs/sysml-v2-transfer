from __future__ import annotations

import xml.etree.ElementTree as ET
from textwrap import wrap
from typing import Any


DEFAULT_CANVAS_WIDTH = 560
DEFAULT_CANVAS_MIN_HEIGHT = 180
DEFAULT_BACKGROUND_FILL = "#f8fafc"
DEFAULT_TITLE_FILL = "#0f172a"
DEFAULT_TITLE_FONT_FAMILY = "Arial, sans-serif"
DEFAULT_TITLE_FONT_SIZE = 18
DEFAULT_NODE_FONT_FAMILY = "Arial, sans-serif"
DEFAULT_NODE_FONT_SIZE = 14
DEFAULT_NODE_FILL = "#ffffff"
DEFAULT_NODE_STROKE = "#0f172a"
DEFAULT_NODE_STROKE_WIDTH = 1.5


def _node_fill(kind: str) -> str:
    return {
        "package": "#bfdbfe",
        "definition": "#dcfce7",
        "relationship": "#f8fafc",
        "statement": "#ffffff",
    }.get(kind, DEFAULT_NODE_FILL)


def _node_stroke(kind: str) -> str:
    if kind == "relationship":
        return "#94a3b8"
    return DEFAULT_NODE_STROKE


def _node_stroke_width(kind: str) -> str:
    if kind == "package":
        return "2"
    if kind == "relationship":
        return "1.25"
    return f"{DEFAULT_NODE_STROKE_WIDTH}"


def _node_dasharray(kind: str) -> str | None:
    if kind == "relationship":
        return "6 4"
    return None


def draw_background(
    parent: ET.Element,
    *,
    width: int = DEFAULT_CANVAS_WIDTH,
    height: int = DEFAULT_CANVAS_MIN_HEIGHT,
    fill: str = DEFAULT_BACKGROUND_FILL,
) -> ET.Element:
    return ET.SubElement(
        parent,
        "rect",
        {
            "x": "0",
            "y": "0",
            "width": str(width),
            "height": str(height),
            "fill": fill,
        },
    )


def draw_rect(
    parent: ET.Element,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = DEFAULT_NODE_FILL,
    stroke: str = DEFAULT_NODE_STROKE,
    stroke_width: str | float = DEFAULT_NODE_STROKE_WIDTH,
    rx: str | int = "12",
    ry: str | int = "12",
    dasharray: str | None = None,
) -> ET.Element:
    attrs = {
        "x": str(x),
        "y": str(y),
        "width": str(width),
        "height": str(height),
        "fill": fill,
        "stroke": stroke,
        "stroke-width": str(stroke_width),
        "rx": str(rx),
        "ry": str(ry),
    }
    if dasharray:
        attrs["stroke-dasharray"] = dasharray
    return ET.SubElement(parent, "rect", attrs)


def draw_line(
    parent: ET.Element,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = "#64748b",
    stroke_width: str | float = "2",
    dasharray: str | None = None,
    linecap: str = "round",
) -> ET.Element:
    attrs = {
        "x1": str(x1),
        "y1": str(y1),
        "x2": str(x2),
        "y2": str(y2),
        "stroke": stroke,
        "stroke-width": str(stroke_width),
        "stroke-linecap": linecap,
    }
    if dasharray:
        attrs["stroke-dasharray"] = dasharray
    return ET.SubElement(parent, "line", attrs)


def draw_text(
    parent: ET.Element,
    x: float,
    y: float,
    text: str,
    *,
    font_family: str = DEFAULT_NODE_FONT_FAMILY,
    font_size: str | int = DEFAULT_NODE_FONT_SIZE,
    font_weight: str = "normal",
    fill: str = DEFAULT_TITLE_FILL,
    text_anchor: str = "start",
) -> ET.Element:
    text_node = ET.SubElement(
        parent,
        "text",
        {
            "x": str(x),
            "y": str(y),
            "font-family": font_family,
            "font-size": str(font_size),
            "font-weight": font_weight,
            "fill": fill,
            "text-anchor": text_anchor,
        },
    )
    text_node.text = text
    return text_node


def _draw_title(
    parent: ET.Element,
    title: str,
    *,
    x: float = 24,
    y: float = 28,
    font_family: str = DEFAULT_TITLE_FONT_FAMILY,
    font_size: str | int = DEFAULT_TITLE_FONT_SIZE,
    font_weight: str = "bold",
    fill: str = DEFAULT_TITLE_FILL,
) -> ET.Element:
    return draw_text(
        parent,
        x,
        y,
        title,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        fill=fill,
    )


def _draw_node_label(
    parent: ET.Element,
    label: str,
    *,
    x: float,
    y: float,
    font_size: str | int,
    font_weight: str,
    fill: str = DEFAULT_TITLE_FILL,
    font_family: str = DEFAULT_NODE_FONT_FAMILY,
) -> None:
    text_lines = wrap(label, width=42) or [label]
    for line_index, text_line in enumerate(text_lines[:2]):
        draw_text(
            parent,
            x,
            y + line_index * 18,
            text_line,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            fill=fill,
        )


def render_package(parent: ET.Element, node: dict[str, Any]) -> None:
    x = node["x"]
    y = node["y"]
    node_width = node["width"]
    node_height = node["height"]
    label = str(node.get("label", ""))
    group = ET.SubElement(parent, "g")
    draw_rect(
        group,
        x,
        y,
        node_width,
        node_height,
        fill=_node_fill("package"),
        stroke=_node_stroke("package"),
        stroke_width=_node_stroke_width("package"),
        rx="16",
        ry="16",
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + 44,
        font_size="16",
        font_weight="bold",
    )


def render_definition(parent: ET.Element, node: dict[str, Any]) -> None:
    x = node["x"]
    y = node["y"]
    node_width = node["width"]
    node_height = node["height"]
    label = str(node.get("label", ""))
    group = ET.SubElement(parent, "g")
    draw_rect(
        group,
        x,
        y,
        node_width,
        node_height,
        fill=_node_fill("definition"),
        stroke=_node_stroke("definition"),
        stroke_width=_node_stroke_width("definition"),
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + 30,
        font_size="14",
        font_weight="normal",
    )


def render_relationship(parent: ET.Element, node: dict[str, Any]) -> None:
    x = node["x"]
    y = node["y"]
    node_width = node["width"]
    node_height = node["height"]
    label = str(node.get("label", ""))
    group = ET.SubElement(parent, "g")
    draw_rect(
        group,
        x,
        y,
        node_width,
        node_height,
        fill=_node_fill("relationship"),
        stroke=_node_stroke("relationship"),
        stroke_width=_node_stroke_width("relationship"),
        dasharray=_node_dasharray("relationship"),
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + 30,
        font_size="13",
        font_weight="normal",
    )


def render_statement(parent: ET.Element, node: dict[str, Any]) -> None:
    x = node["x"]
    y = node["y"]
    node_width = node["width"]
    node_height = node["height"]
    label = str(node.get("label", ""))
    group = ET.SubElement(parent, "g")
    draw_rect(
        group,
        x,
        y,
        node_width,
        node_height,
        fill=_node_fill("statement"),
        stroke=_node_stroke("statement"),
        stroke_width=_node_stroke_width("statement"),
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + 30,
        font_size="14",
        font_weight="normal",
    )


def render_svg(graphics_model: dict[str, Any]) -> str:
    nodes = graphics_model.get("nodes", [])
    edges = graphics_model.get("edges", [])
    width = DEFAULT_CANVAS_WIDTH
    height = max(DEFAULT_CANVAS_MIN_HEIGHT, 100 + max(len(nodes), 1) * 100)
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

    draw_background(svg, width=width, height=height)
    _draw_title(svg, title)

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
        draw_line(
            svg,
            x1,
            y1,
            x2,
            y2,
            stroke="#94a3b8" if dashed else "#64748b",
            stroke_width="1.5" if dashed else "2",
            dasharray="6 4" if dashed else None,
        )

    for node in nodes:
        kind = str(node.get("kind", "statement"))
        if kind == "package":
            render_package(svg, node)
        elif kind == "definition":
            render_definition(svg, node)
        elif kind == "relationship":
            render_relationship(svg, node)
        else:
            render_statement(svg, node)

    return ET.tostring(svg, encoding="utf-8", xml_declaration=True).decode("utf-8")
