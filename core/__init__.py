"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from .convert import SysMLModel, code_to_graphics, graphics_to_code, graphics_to_svg
from .layout import build_graphics_model, classify_statement, extract_title, strip_inline_comment
from .parser import ParseEvent, parse_sysml, parse_sysml_events
from .svg import render_svg

__all__ = [
    "SysMLModel",
    "build_graphics_model",
    "classify_statement",
    "code_to_graphics",
    "extract_title",
    "graphics_to_code",
    "graphics_to_svg",
    "ParseEvent",
    "parse_sysml",
    "parse_sysml_events",
    "render_svg",
    "strip_inline_comment",
]
