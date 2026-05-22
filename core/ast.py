"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SysMLDocument:
    package: "PackageNode | None" = None
    unknown: list[str] = field(default_factory=list)


@dataclass
class PackageNode:
    name: str
    members: list["AstNode"] = field(default_factory=list)
    documentation: str = ""


@dataclass
class DefinitionNode:
    keyword: str
    name: str
    members: list["AstNode"] = field(default_factory=list)
    documentation: str = ""


@dataclass
class UsageNode:
    keyword: str
    name: str
    type_name: str
    documentation: str = ""


@dataclass
class FlowNode:
    item_type: str
    source: str
    target: str


@dataclass
class UnknownNode:
    text: str


AstNode = PackageNode | DefinitionNode | UsageNode | FlowNode | UnknownNode
