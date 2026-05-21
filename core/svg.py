from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET
from textwrap import wrap
from typing import Any


@dataclass(frozen=True)
class SVGTheme:
    canvas_width: int = 560
    canvas_min_height: int = 180
    background_fill: str = "#f8fafc"
    title_fill: str = "#0f172a"
    title_font_family: str = "Arial, sans-serif"
    title_font_size: int = 18
    node_font_family: str = "Arial, sans-serif"
    package_font_family: str = "Arial, sans-serif"
    relationship_font_family: str = "Arial, sans-serif"
    node_font_size: int = 14
    package_font_size: int = 16
    relationship_font_size: int = 13
    node_fill: str = "#ffffff"
    package_fill: str = "#bfdbfe"
    definition_fill: str = "#dcfce7"
    relationship_fill: str = "#f8fafc"
    node_stroke: str = "#0f172a"
    relationship_stroke: str = "#94a3b8"
    node_stroke_width: float = 1.5
    package_stroke_width: float = 2
    relationship_stroke_width: float = 1.25
    package_rx: int = 16
    package_ry: int = 16
    node_rx: int = 12
    node_ry: int = 12
    relationship_dasharray: str = "6 4"
    title_x: int = 24
    title_y: int = 28
    package_text_y_offset: int = 44
    node_text_y_offset: int = 30
    text_line_height: int = 18

    def fill_for_kind(self, kind: str) -> str:
        return {
            "package": self.package_fill,
            "definition": self.definition_fill,
            "relationship": self.relationship_fill,
            "statement": self.node_fill,
        }.get(kind, self.node_fill)

    def stroke_for_kind(self, kind: str) -> str:
        if kind == "relationship":
            return self.relationship_stroke
        return self.node_stroke

    def stroke_width_for_kind(self, kind: str) -> str:
        if kind == "package":
            return str(self.package_stroke_width)
        if kind == "relationship":
            return str(self.relationship_stroke_width)
        return str(self.node_stroke_width)

    def dasharray_for_kind(self, kind: str) -> str | None:
        if kind == "relationship":
            return self.relationship_dasharray
        return None

    def font_family_for_kind(self, kind: str) -> str:
        if kind == "package":
            return self.package_font_family
        if kind == "relationship":
            return self.relationship_font_family
        return self.node_font_family

    def font_size_for_kind(self, kind: str) -> str:
        if kind == "package":
            return str(self.package_font_size)
        if kind == "relationship":
            return str(self.relationship_font_size)
        return str(self.node_font_size)

    def font_weight_for_kind(self, kind: str) -> str:
        if kind == "package":
            return "bold"
        return "normal"

    def text_y_offset_for_kind(self, kind: str) -> int:
        if kind == "package":
            return self.package_text_y_offset
        return self.node_text_y_offset


DEFAULT_THEME = SVGTheme()


def draw_background(
    parent: ET.Element,
    *,
    theme: SVGTheme = DEFAULT_THEME,
    width: int | None = None,
    height: int | None = None,
    fill: str | None = None,
) -> ET.Element:
    return ET.SubElement(
        parent,
        "rect",
        {
            "x": "0",
            "y": "0",
            "width": str(width if width is not None else theme.canvas_width),
            "height": str(height if height is not None else theme.canvas_min_height),
            "fill": fill if fill is not None else theme.background_fill,
        },
    )


def draw_rect(
    parent: ET.Element,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    theme: SVGTheme = DEFAULT_THEME,
    fill: str | None = None,
    stroke: str | None = None,
    stroke_width: str | float | None = None,
    rx: str | int | None = None,
    ry: str | int | None = None,
    dasharray: str | None = None,
) -> ET.Element:
    attrs = {
        "x": str(x),
        "y": str(y),
        "width": str(width),
        "height": str(height),
        "fill": fill if fill is not None else theme.node_fill,
        "stroke": stroke if stroke is not None else theme.node_stroke,
        "stroke-width": str(stroke_width if stroke_width is not None else theme.node_stroke_width),
        "rx": str(rx if rx is not None else theme.node_rx),
        "ry": str(ry if ry is not None else theme.node_ry),
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
    font_family: str = "Arial, sans-serif",
    font_size: str | int = 14,
    font_weight: str = "normal",
    fill: str = "#0f172a",
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
    theme: SVGTheme = DEFAULT_THEME,
    x: float | None = None,
    y: float | None = None,
) -> ET.Element:
    return draw_text(
        parent,
        x if x is not None else theme.title_x,
        y if y is not None else theme.title_y,
        title,
        font_family=theme.title_font_family,
        font_size=theme.title_font_size,
        font_weight="bold",
        fill=theme.title_fill,
    )


def _draw_node_label(
    parent: ET.Element,
    label: str,
    *,
    x: float,
    y: float,
    theme: SVGTheme = DEFAULT_THEME,
    kind: str = "statement",
) -> None:
    text_lines = wrap(label, width=42) or [label]
    font_family = theme.font_family_for_kind(kind)
    font_size = theme.font_size_for_kind(kind)
    font_weight = theme.font_weight_for_kind(kind)
    fill = theme.title_fill
    for line_index, text_line in enumerate(text_lines[:2]):
        draw_text(
            parent,
            x,
            y + line_index * theme.text_line_height,
            text_line,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            fill=fill,
        )


def render_package(parent: ET.Element, node: dict[str, Any], *, theme: SVGTheme = DEFAULT_THEME) -> None:
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
        theme=theme,
        fill=theme.fill_for_kind("package"),
        stroke=theme.stroke_for_kind("package"),
        stroke_width=theme.stroke_width_for_kind("package"),
        rx=theme.package_rx,
        ry=theme.package_ry,
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + theme.package_text_y_offset,
        theme=theme,
        kind="package",
    )


def render_definition(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
) -> None:
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
        theme=theme,
        fill=theme.fill_for_kind("definition"),
        stroke=theme.stroke_for_kind("definition"),
        stroke_width=theme.stroke_width_for_kind("definition"),
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + theme.node_text_y_offset,
        theme=theme,
        kind="definition",
    )


def render_relationship(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
) -> None:
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
        theme=theme,
        fill=theme.fill_for_kind("relationship"),
        stroke=theme.stroke_for_kind("relationship"),
        stroke_width=theme.stroke_width_for_kind("relationship"),
        dasharray=theme.dasharray_for_kind("relationship"),
    )
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + theme.node_text_y_offset,
        theme=theme,
        kind="relationship",
    )


def render_statement(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
) -> None:
    x = node["x"]
    y = node["y"]
    node_width = node["width"]
    node_height = node["height"]
    label = str(node.get("label", ""))
    group = ET.SubElement(parent, "g")
    draw_rect(group, x, y, node_width, node_height, theme=theme)
    _draw_node_label(
        group,
        label,
        x=x + 16,
        y=y + theme.node_text_y_offset,
        theme=theme,
        kind="statement",
    )


def render_svg(graphics_model: dict[str, Any], *, theme: SVGTheme = DEFAULT_THEME) -> str:
    nodes = graphics_model.get("nodes", [])
    edges = graphics_model.get("edges", [])
    width = theme.canvas_width
    height = max(theme.canvas_min_height, 100 + max(len(nodes), 1) * 100)
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

    draw_background(svg, theme=theme, width=width, height=height)
    _draw_title(svg, title, theme=theme)

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
            stroke=theme.relationship_stroke if dashed else "#64748b",
            stroke_width=theme.relationship_stroke_width if dashed else "2",
            dasharray=theme.relationship_dasharray if dashed else None,
        )

    for node in nodes:
        kind = str(node.get("kind", "statement"))
        if kind == "package":
            render_package(svg, node, theme=theme)
        elif kind == "definition":
            render_definition(svg, node, theme=theme)
        elif kind == "relationship":
            render_relationship(svg, node, theme=theme)
        else:
            render_statement(svg, node, theme=theme)

    return ET.tostring(svg, encoding="utf-8", xml_declaration=True).decode("utf-8")
