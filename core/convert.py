"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .layout import build_graphics_model
from .svg import render_svg

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
    return build_graphics_model(sysml_code)


def graphics_to_svg(graphics_model: dict[str, Any]) -> str:
    """Render the graphics model as a minimal SVG diagram."""
    return render_svg(graphics_model)


def graphics_to_code(graphics_model: dict[str, Any]) -> str:
    """Convert graphics representation back to SysML v2 textual code."""
    return graphics_model.get("content", "")
