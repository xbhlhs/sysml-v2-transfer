"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from .ast import AstNode, DefinitionNode, FlowNode, PackageNode, SysMLDocument, UnknownNode, UsageNode


_DOC_BLOCK_RE = re.compile(r"doc\s*/\*(.*?)\*/", re.IGNORECASE | re.DOTALL)
_PACKAGE_RE = re.compile(r"^package\s+([A-Za-z_][\w.]*)\s*(\{)?$", re.IGNORECASE)
_DEF_RE = re.compile(
    r"^(item|part|port|action|state|connection)\s+def\s+([A-Za-z_][\w.]*)\s*(\{)?$",
    re.IGNORECASE,
)
_USAGE_RE = re.compile(r"^(part|port)\s+([A-Za-z_][\w.]*)\s*:\s*([A-Za-z_][\w.]*)$", re.IGNORECASE)
_FLOW_RE = re.compile(
    r"^flow\s+of\s+([A-Za-z_][\w.]*)\s+from\s+([\w.]+)\s+to\s+([\w.]+)$",
    re.IGNORECASE,
)
_ARROW_RE = re.compile(r"^([\w.]+)\s*->\s*([\w.]+)$")

ParseEventKind = Literal["enter_package", "enter_definition", "usage", "flow", "doc", "unknown", "exit"]


@dataclass(frozen=True)
class ParseEvent:
    kind: ParseEventKind
    keyword: str = ""
    name: str = ""
    type_name: str = ""
    documentation: str = ""
    item_type: str = ""
    source: str = ""
    target: str = ""
    text: str = ""


def parse_sysml(sysml_code: str) -> SysMLDocument:
    parser = _Parser(parse_sysml_events(sysml_code))
    return parser.parse()


def parse_sysml_events(sysml_code: str) -> list[ParseEvent]:
    events: list[ParseEvent] = []
    for line in _normalize_lines(sysml_code):
        if line == "}":
            events.append(ParseEvent(kind="exit"))
            continue

        doc = _extract_doc(line)
        if doc:
            events.append(ParseEvent(kind="doc", documentation=doc))
            continue

        package_match = _PACKAGE_RE.match(line)
        if package_match:
            events.append(
                ParseEvent(
                    kind="enter_package",
                    name=package_match.group(1),
                    text="inline_empty" if line.endswith("{}") else "",
                )
            )
            continue

        definition_match = _DEF_RE.match(line)
        if definition_match:
            events.append(
                ParseEvent(
                    kind="enter_definition",
                    keyword=definition_match.group(1).lower(),
                    name=definition_match.group(2),
                    text="inline_empty" if line.endswith("{}") else "",
                )
            )
            continue

        flow_match = _FLOW_RE.match(line)
        if flow_match:
            events.append(
                ParseEvent(
                    kind="flow",
                    item_type=flow_match.group(1),
                    source=flow_match.group(2),
                    target=flow_match.group(3),
                )
            )
            continue

        arrow_match = _ARROW_RE.match(line)
        if arrow_match:
            events.append(
                ParseEvent(
                    kind="flow",
                    item_type="relation",
                    source=arrow_match.group(1),
                    target=arrow_match.group(2),
                )
            )
            continue

        usage_match = _USAGE_RE.match(line)
        if usage_match:
            events.append(
                ParseEvent(
                    kind="usage",
                    keyword=usage_match.group(1).lower(),
                    name=usage_match.group(2),
                    type_name=usage_match.group(3),
                )
            )
            continue

        events.append(ParseEvent(kind="unknown", text=line))
    return events


class _Parser:
    def __init__(self, events: list[ParseEvent]) -> None:
        self.events = events
        self.index = 0

    def parse(self) -> SysMLDocument:
        document = SysMLDocument()
        while self.index < len(self.events):
            event = self._peek()
            if event.kind == "enter_package":
                document.package = self._parse_package(event)
                continue
            document.unknown.append(event.text)
            self.index += 1
        return document

    def _parse_package(self, event: ParseEvent) -> PackageNode:
        self.index += 1
        package = PackageNode(name=event.name)
        if event.text == "inline_empty":
            return package
        package.members = self._parse_members(owner=package)
        return package

    def _parse_definition(self, event: ParseEvent) -> DefinitionNode:
        self.index += 1
        definition = DefinitionNode(keyword=event.keyword, name=event.name)
        if event.text == "inline_empty":
            return definition
        definition.members = self._parse_members(owner=definition)
        return definition

    def _parse_members(self, *, owner: PackageNode | DefinitionNode | None = None) -> list[AstNode]:
        members: list[AstNode] = []
        while self.index < len(self.events):
            event = self._peek()
            if event.kind == "exit":
                self.index += 1
                break

            if event.kind == "doc":
                _attach_documentation(members, event.documentation, owner=owner)
                self.index += 1
                continue

            if event.kind == "enter_package":
                node = self._parse_package(event)
                members.append(node)
                continue

            if event.kind == "enter_definition":
                node = self._parse_definition(event)
                members.append(node)
                continue

            if event.kind == "flow":
                members.append(
                    FlowNode(
                        item_type=event.item_type,
                        source=event.source,
                        target=event.target,
                    )
                )
                self.index += 1
                continue

            if event.kind == "usage":
                members.append(
                    UsageNode(
                        keyword=event.keyword,
                        name=event.name,
                        type_name=event.type_name,
                    )
                )
                self.index += 1
                continue

            members.append(UnknownNode(text=event.text))
            self.index += 1
        return members

    def _peek(self) -> ParseEvent:
        return self.events[self.index]


def _normalize_lines(sysml_code: str) -> list[str]:
    lines: list[str] = []
    in_doc = False
    doc_buffer: list[str] = []
    flow_buffer: list[str] = []

    for raw_line in sysml_code.splitlines():
        line = _strip_inline_comment(raw_line).strip()
        if not line:
            continue

        if in_doc:
            doc_buffer.append(line)
            if "*/" in line:
                lines.append(" ".join(doc_buffer))
                doc_buffer = []
                in_doc = False
            continue

        if line.lower().startswith("doc /*") and "*/" not in line:
            doc_buffer = [line]
            in_doc = True
            continue

        if line.lower().startswith("flow of") or (flow_buffer and line.lower().startswith(("from ", "to "))):
            flow_buffer.append(line.rstrip(";"))
            if line.rstrip(";").lower().startswith("to "):
                lines.append(" ".join(flow_buffer))
                flow_buffer = []
            continue

        if flow_buffer:
            lines.append(" ".join(flow_buffer))
            flow_buffer = []

        for part in _split_structural_line(line):
            if part:
                lines.append(part)

    if flow_buffer:
        lines.append(" ".join(flow_buffer))
    return lines


def _split_structural_line(line: str) -> list[str]:
    cleaned = line.strip().rstrip(";").strip()
    if not cleaned:
        return []
    if cleaned.endswith("{}"):
        return [cleaned[:-2].strip() + " {}"]
    if cleaned == "}":
        return ["}"]
    if cleaned.endswith("}"):
        body = cleaned[:-1].strip()
        if body.endswith("{"):
            body = body[:-1].strip()
        return [body, "}"] if body else ["}"]
    if cleaned.endswith("{"):
        return [cleaned[:-1].strip() + " {"]
    return [cleaned]


def _strip_inline_comment(line: str) -> str:
    comment_start = line.find("//")
    if comment_start >= 0:
        return line[:comment_start].rstrip()
    return line


def _extract_doc(line: str) -> str:
    match = _DOC_BLOCK_RE.match(line)
    if not match:
        return ""
    return " ".join(match.group(1).split())


def _attach_documentation(
    members: list[AstNode],
    documentation: str,
    *,
    owner: PackageNode | DefinitionNode | None,
) -> None:
    if not members:
        if owner is not None:
            owner.documentation = " ".join(part for part in [owner.documentation, documentation] if part)
        return
    last = members[-1]
    if isinstance(last, (PackageNode, DefinitionNode, UsageNode)):
        last.documentation = " ".join(part for part in [last.documentation, documentation] if part)
