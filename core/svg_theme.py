"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SVGTheme:
    canvas_width: int = 560
    canvas_min_height: int = 180
    background_fill: str = "#ffffff"
    title_fill: str = "#111827"
    title_font_family: str = "Arial, sans-serif"
    title_font_size: int = 18
    node_font_family: str = "Arial, sans-serif"
    package_font_family: str = "Arial, sans-serif"
    relationship_font_family: str = "Arial, sans-serif"
    node_font_size: int = 14
    package_font_size: int = 16
    relationship_font_size: int = 13
    node_fill: str = "#ffffff"
    package_fill: str = "#dbeafe"
    definition_fill: str = "#dcfce7"
    relationship_fill: str = "#f8fafc"
    node_stroke: str = "#1f2937"
    relationship_stroke: str = "#64748b"
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
