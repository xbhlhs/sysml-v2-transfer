"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from .text_layout import wrap_text
from .svg_theme import DEFAULT_THEME, SVGTheme


SVG_KIND_TAG_Y_OFFSET = 18
SVG_KIND_TITLE_GAP = 4
SVG_KIND_TITLE_FONT_SIZE = 15
SVG_PACKAGE_TITLE_FONT_SIZE = 16
SVG_KIND_TAG_FONT_SIZE = 12
SVG_KIND_TAG_FONT_SIZE_REDUCED = 11
SVG_SECONDARY_LABEL_FONT_SIZE = 12
SVG_DOC_HEADER_GAP = 6
SVG_DOC_BODY_GAP = 2
SVG_DOC_LABEL = "Doc"
SVG_DOC_LABEL_FONT_SIZE = 12
SVG_DOC_BODY_FONT_SIZE = 13
SVG_DOC_BODY_FONT_SIZE_REDUCED = 12
SVG_DOC_LABEL_COLOR = "#64748b"
SVG_DOC_BODY_COLOR = "#334155"
SVG_DOC_BODY_COLOR_DIM = "#475569"
SVG_KIND_TAG_COLOR_PACKAGE = "#0f766e"
SVG_KIND_TAG_COLOR_DEFAULT = "#166534"
SVG_SECONDARY_LABEL_COLOR = "#1d4ed8"
SVG_SECONDARY_LABEL_Y_OFFSET = 2
SVG_CARD_LEFT_PADDING = 16
SVG_CARD_RIGHT_PADDING = 16
SVG_CARD_TEXT_WIDTH_PADDING = 16
SVG_CARD_TEXT_WRAP_DIVISOR = 7
SVG_CARD_MIN_WRAP_CHARS = 10
SVG_DEFAULT_FONT_SIZE = 14
SVG_DEFAULT_EDGE_STROKE_WIDTH = "2"
SVG_DEFAULT_EDGE_STROKE = "#475569"
SVG_LAYOUT_HEIGHT_BASE = 100
SVG_LAYOUT_HEIGHT_PER_NODE = 100
SVG_LAYOUT_BOTTOM_PADDING = 40
SVG_CENTER_DIVISOR = 2
SVG_COORDINATE_ORIGIN = "0"
SVG_XML_NAMESPACE = "http://www.w3.org/2000/svg"
SVG_XML_ENCODING = "utf-8"


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
            "x": SVG_COORDINATE_ORIGIN,
            "y": SVG_COORDINATE_ORIGIN,
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
    stroke: str = SVG_DEFAULT_EDGE_STROKE,
    stroke_width: str | float = SVG_DEFAULT_EDGE_STROKE_WIDTH,
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
    font_size: str | int = SVG_DEFAULT_FONT_SIZE,
    font_weight: str = "normal",
    font_style: str = "normal",
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
            "font-style": font_style,
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


def _fit_text_lines(
    text: str,
    *,
    width: float,
) -> list[str]:
    chars_per_line = max(SVG_CARD_MIN_WRAP_CHARS, int((width - SVG_CARD_TEXT_WIDTH_PADDING) / SVG_CARD_TEXT_WRAP_DIVISOR))
    return wrap_text(text, chars_per_line)


def _draw_lines(
    parent: ET.Element,
    lines: list[str],
    *,
    x: float,
    y: float,
    theme: SVGTheme = DEFAULT_THEME,
    kind: str = "statement",
    font_size: str | int = SVG_DEFAULT_FONT_SIZE,
    font_weight: str = "normal",
    font_style: str = "normal",
    fill: str | None = None,
    text_anchor: str = "start",
) -> None:
    font_family = theme.font_family_for_kind(kind)
    fill = theme.title_fill if fill is None else fill
    for line_index, text_line in enumerate(lines):
        draw_text(
            parent,
            x,
            y + line_index * theme.text_line_height,
            text_line,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            font_style=font_style,
            fill=fill,
            text_anchor=text_anchor,
        )


def _draw_centered_text_block(
    parent: ET.Element,
    text: str,
    *,
    x: float,
    y: float,
    width: float,
    theme: SVGTheme = DEFAULT_THEME,
    kind: str = "statement",
    font_size: str | int = 14,
    font_weight: str = "normal",
    font_style: str = "normal",
    fill: str | None = None,
) -> int:
    lines = _fit_text_lines(
        text,
        width=width,
    )
    _draw_lines(
        parent,
        lines,
        x=x,
        y=y,
        theme=theme,
        kind=kind,
        font_size=font_size,
        font_weight=font_weight,
        font_style=font_style,
        fill=fill,
        text_anchor="middle",
    )
    return len(lines)


def _draw_left_text_block(
    parent: ET.Element,
    text: str,
    *,
    x: float,
    y: float,
    width: float,
    theme: SVGTheme = DEFAULT_THEME,
    kind: str = "statement",
    font_size: str | int = 14,
    font_weight: str = "normal",
    font_style: str = "normal",
    fill: str | None = None,
) -> int:
    lines = _fit_text_lines(
        text,
        width=width,
    )
    _draw_lines(
        parent,
        lines,
        x=x,
        y=y,
        theme=theme,
        kind=kind,
        font_size=font_size,
        font_weight=font_weight,
        font_style=font_style,
        fill=fill,
        text_anchor="start",
    )
    return len(lines)


def _add_documentation(parent: ET.Element, node: dict[str, Any]) -> None:
    documentation = str(node.get("documentation", "")).strip()
    if documentation:
        desc = ET.SubElement(parent, "desc")
        desc.text = documentation


def _render_card(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
    kind: str,
    package_style: bool = False,
) -> None:
    x = node["x"]
    y = node["y"]
    node_width = node["width"]
    node_height = node["height"]
    label = str(node.get("label", ""))
    kind_tag = str(node.get("kind_tag", kind))
    secondary_label = str(node.get("secondary_label", ""))
    documentation = str(node.get("documentation", "")).strip()
    group = ET.SubElement(parent, "g")
    _add_documentation(group, node)
    draw_rect(
        group,
        x,
        y,
        node_width,
        node_height,
        theme=theme,
        fill=theme.fill_for_kind(kind),
        stroke=theme.stroke_for_kind(kind),
        stroke_width=theme.stroke_width_for_kind(kind),
        rx=theme.package_rx if package_style else None,
        ry=theme.package_ry if package_style else None,
        dasharray=theme.dasharray_for_kind(kind),
    )

    current_y = y + SVG_KIND_TAG_Y_OFFSET
    kind_fill = SVG_KIND_TAG_COLOR_PACKAGE if kind == "package" else SVG_KIND_TAG_COLOR_DEFAULT
    kind_lines = _draw_centered_text_block(
        group,
        f"<<{kind_tag}>>",
        x=x + node_width / SVG_CENTER_DIVISOR,
        y=current_y,
        width=node_width,
        theme=theme,
        kind=kind,
        font_size=SVG_KIND_TAG_FONT_SIZE_REDUCED if kind == "relationship" else SVG_KIND_TAG_FONT_SIZE,
        font_weight="bold",
        fill=kind_fill,
    )
    current_y += kind_lines * theme.text_line_height
    current_y += SVG_KIND_TITLE_GAP
    title_lines = _draw_centered_text_block(
        group,
        label,
        x=x + node_width / SVG_CENTER_DIVISOR,
        y=current_y,
        width=node_width - SVG_CARD_TEXT_WIDTH_PADDING,
        theme=theme,
        kind=kind,
        font_size=SVG_PACKAGE_TITLE_FONT_SIZE if kind == "package" else SVG_KIND_TITLE_FONT_SIZE,
        font_weight="bold",
    )
    current_y += title_lines * theme.text_line_height

    if secondary_label:
        secondary_lines = _draw_centered_text_block(
            group,
            secondary_label,
            x=x + node_width / SVG_CENTER_DIVISOR,
            y=current_y + SVG_SECONDARY_LABEL_Y_OFFSET,
            width=node_width - SVG_CARD_TEXT_WIDTH_PADDING,
            theme=theme,
            kind=kind,
            font_size=SVG_SECONDARY_LABEL_FONT_SIZE,
            font_style="italic",
            fill=SVG_SECONDARY_LABEL_COLOR,
        )
        current_y += secondary_lines * theme.text_line_height

    if documentation and kind != "package":
        current_y += SVG_DOC_HEADER_GAP
        _draw_left_text_block(
            group,
            SVG_DOC_LABEL,
            x=x + SVG_CARD_LEFT_PADDING,
            y=current_y,
            width=node_width - (SVG_CARD_LEFT_PADDING + SVG_CARD_RIGHT_PADDING),
            theme=theme,
            kind=kind,
            font_size=SVG_DOC_LABEL_FONT_SIZE,
            font_weight="bold",
            fill=SVG_DOC_LABEL_COLOR,
        )
        current_y += theme.text_line_height + SVG_DOC_BODY_GAP
        _draw_left_text_block(
            group,
            documentation,
            x=x + SVG_CARD_LEFT_PADDING,
            y=current_y,
            width=node_width - (SVG_CARD_LEFT_PADDING + SVG_CARD_RIGHT_PADDING),
            theme=theme,
            kind=kind,
            font_size=SVG_DOC_BODY_FONT_SIZE_REDUCED if kind == "relationship" else SVG_DOC_BODY_FONT_SIZE,
            fill=SVG_DOC_BODY_COLOR_DIM if kind == "package" else SVG_DOC_BODY_COLOR,
        )


def render_package(parent: ET.Element, node: dict[str, Any], *, theme: SVGTheme = DEFAULT_THEME) -> None:
    _render_card(parent, node, theme=theme, kind="package", package_style=True)


def render_definition(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
) -> None:
    _render_card(parent, node, theme=theme, kind="definition")


def render_relationship(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
) -> None:
    _render_card(parent, node, theme=theme, kind="relationship")


def render_statement(
    parent: ET.Element,
    node: dict[str, Any],
    *,
    theme: SVGTheme = DEFAULT_THEME,
) -> None:
    _render_card(parent, node, theme=theme, kind="statement")


def render_svg(graphics_model: dict[str, Any], *, theme: SVGTheme = DEFAULT_THEME) -> str:
    nodes = graphics_model.get("nodes", [])
    edges = graphics_model.get("edges", [])
    width = theme.canvas_width
    title = str(graphics_model.get("title", "SysML v2 Transfer"))
    max_bottom = max((float(node["y"]) + float(node["height"]) for node in nodes), default=0.0)
    height = max(
        theme.canvas_min_height,
        int(max_bottom + SVG_LAYOUT_BOTTOM_PADDING),
        SVG_LAYOUT_HEIGHT_BASE + max(len(nodes), 1) * SVG_LAYOUT_HEIGHT_PER_NODE,
    )

    node_index = {node["id"]: node for node in nodes}
    svg = ET.Element(
        "svg",
        {
            "xmlns": SVG_XML_NAMESPACE,
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
            stroke=theme.relationship_stroke if dashed else SVG_DEFAULT_EDGE_STROKE,
            stroke_width=theme.relationship_stroke_width if dashed else SVG_DEFAULT_EDGE_STROKE_WIDTH,
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

    return ET.tostring(svg, encoding=SVG_XML_ENCODING, xml_declaration=True).decode("utf-8")
