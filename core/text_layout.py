from __future__ import annotations

import re


_CAMEL_PART_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+|\d+")
_CLOSING_PUNCTUATION = set("，。！？；：、）】》』」”’,.!?;:)]")
_OPENING_PUNCTUATION = set("（【《『「“‘([{")


def _split_word_parts(word: str) -> list[str]:
    parts: list[str] = []
    index = 0
    while index < len(word):
        char = word[index]
        if char.isascii() and char.isalnum():
            match = _CAMEL_PART_RE.match(word, index)
            if match:
                parts.append(match.group(0))
                index = match.end()
                continue
        parts.append(char)
        index += 1
    return parts


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for paragraph in text.splitlines() or [text]:
        stripped = paragraph.strip()
        if not stripped:
            continue
        words = re.findall(r"\S+", stripped)
        for word_index, word in enumerate(words):
            if word_index:
                tokens.append(" ")
            tokens.extend(_split_word_parts(word))
    return tokens or [text]


def _normalize_punctuation(lines: list[str]) -> list[str]:
    if not lines:
        return lines

    normalized = list(lines)
    for index in range(1, len(normalized)):
        while normalized[index] and normalized[index][0] in _CLOSING_PUNCTUATION:
            normalized[index - 1] += normalized[index][0]
            normalized[index] = normalized[index][1:]
        while normalized[index - 1] and normalized[index - 1][-1] in _OPENING_PUNCTUATION:
            normalized[index] = normalized[index - 1][-1] + normalized[index]
            normalized[index - 1] = normalized[index - 1][:-1]

    return [line for line in normalized if line]


def wrap_text(text: str, max_width_chars: int) -> list[str]:
    tokens = _tokenize(text)
    lines: list[str] = []
    current = ""

    for token in tokens:
        if token == " ":
            if current and not current.endswith(" "):
                current += " "
            continue

        candidate = token if not current else f"{current}{token}"
        if current and len(candidate) > max_width_chars:
            lines.append(current.rstrip())
            current = token.lstrip()
            continue

        current = candidate

    if current:
        lines.append(current.rstrip())

    return _normalize_punctuation(lines)
