"""Share source edits and column padding without interpreting scientific values."""

import re
from collections.abc import Iterable, Sequence
from itertools import pairwise
from typing import Literal

from antlr4 import ParserRuleContext, Token
from pydantic import BaseModel, ConfigDict

from psi4_parser._tree import rule_name
from psi4_parser.api import ParseResult, SourceSpan

_NUMBER = re.compile(r"[+-]?(?:\d[\d_]*(?:\.[\d_]*)?|\.[\d_]+)(?:[eEdD][+-]?[\d_]+)?\Z")
_INTEGER = re.compile(r"[+-]?0[xXbBoO][\da-fA-F_]+\Z")
type Alignment = Literal["left", "right", "number"]


class Edit(BaseModel):
    """Replace a half-open original-source interval with text.

    Attributes:
        start: First original character replaced.
        stop: First original character after the replacement.
        text: Replacement source.
    """

    model_config = ConfigDict(frozen=True, strict=True)
    start: int
    stop: int
    text: str


class Cell(BaseModel):
    """Locate one intact table field in the original source.

    Attributes:
        start: First source character of the field.
        stop: Exclusive source end of the field.
        text: Significant field spelling; literal atom labels retain interior spaces.
    """

    model_config = ConfigDict(frozen=True, strict=True)
    start: int
    stop: int
    text: str


# Table cells, before/after padding pairs, and consecutive syntax sections.
type CellRow = list[Cell]
type CellTable = list[CellRow]
type CellPadding = tuple[int, int]
type PaddingRow = list[CellPadding]
type TablePadding = list[PaddingRow]
type SyntaxSection = list[ParserRuleContext]


def cell(
    result: ParseResult, node: ParserRuleContext | Token, *, literal: bool = False
) -> Cell:
    """Locate a CST field while retaining its significant token spelling.

    Args:
        result: Owning parse result.
        node: Field context or token.
        literal: Retain interior whitespace, for complete native atom labels.

    Returns:
        Original-source boundaries and the field's token text.
    """
    start, stop = result.source_span(node)
    return Cell(
        start=start,
        stop=stop,
        text=result.source_text(node)
        if literal
        else (node.getText() if isinstance(node, ParserRuleContext) else node.text),
    )


def numeric_anchor(text: str) -> int | None:
    """Locate a literal's decimal column without parsing or rounding its value.

    Args:
        text: Intact signed numeric spelling, including any exponent.

    Returns:
        Decimal-point offset, implicit decimal position, or None for other text.
    """
    if _INTEGER.fullmatch(text):
        return len(text)
    if not _NUMBER.fullmatch(text):
        return None
    exponent = re.search("[eEdD]", text)
    mantissa = text[: exponent.start()] if exponent is not None else text
    return mantissa.index(".") if "." in mantissa else len(mantissa)


def padding(rows: Sequence[Sequence[Cell]], modes: Sequence[Alignment]) -> TablePadding:
    """Compute before/after padding for ragged rows with shared columns.

    Number columns align decimal points when every populated field is numeric;
    mixed symbolic columns align complete fields on their right edge.

    Args:
        rows: Fields in logical row order, with missing trailing cells permitted.
        modes: Alignment for each possible column.

    Returns:
        Left and right padding for each populated field.
    """
    widths: list[CellPadding] = []
    numeric: list[bool] = []
    for column, mode in enumerate(modes):
        texts = [row[column].text for row in rows if column < len(row)]
        anchors = [numeric_anchor(text) for text in texts]
        use_decimal = mode == "number" and all(anchor is not None for anchor in anchors)
        numeric.append(use_decimal)
        if use_decimal:
            widths.append(
                (
                    max(
                        (anchor for anchor in anchors if anchor is not None), default=0
                    ),
                    max(
                        (
                            len(text) - anchor
                            for text, anchor in zip(texts, anchors, strict=True)
                            if anchor is not None
                        ),
                        default=0,
                    ),
                )
            )
        else:
            widths.append((max(map(len, texts), default=0), 0))
    result: TablePadding = []
    for row in rows:
        pads = []
        for index, field in enumerate(row):
            left, right = widths[index]
            anchor = numeric_anchor(field.text) if numeric[index] else None
            if anchor is not None:
                pads.append((left - anchor, right - len(field.text) + anchor))
            elif modes[index] == "left":
                pads.append((0, left - len(field.text)))
            else:
                pads.append((left - len(field.text), 0))
        result.append(pads)
    return result


class Layout:
    """Collect whitespace replacements; later style passes own matching gaps.

    Attributes:
        result: Shared original source and CST, treated as read-only.
        edits: Replacements keyed by their original-source interval.
    """

    def __init__(self, result: ParseResult, initial: Iterable[Edit]) -> None:
        """Seed a plan with ordinary token spacing and indentation.

        Args:
            result: Original input and CST.
            initial: Base style edits, before table alignment overrides.
        """
        self.result: ParseResult = result
        self.edits: dict[SourceSpan, Edit] = {
            (edit.start, edit.stop): edit for edit in initial
        }

    def copy(self) -> Layout:
        """Return an independent edit plan for a pure style transformation."""
        return Layout(self.result, self.edits.values())

    def gap(self, start: int, stop: int, text: str) -> None:
        """Replace horizontal whitespace only, preserving comments and row breaks.

        Args:
            start: Start of the gap.
            stop: Exclusive end of the gap.
            text: Desired whitespace.
        """
        original = self.result.source[start:stop]
        if any(not char.isspace() or char in "\r\n" for char in original):
            return
        key = start, stop
        if original == text:
            self.edits.pop(key, None)
        else:
            self.edits[key] = Edit(start=start, stop=stop, text=text)

    def line_breaks(self, start: int, stop: int, text: str) -> None:
        """Replace a verified blank separator, removing enclosed whitespace edits.

        Args:
            start: First newline after the preceding statement's final line.
            stop: Start of the next statement's line or its leading comments.
            text: Two newline spellings representing one empty line.

        Raises:
            ValueError: The interval or replacement contains non-whitespace data.
        """
        original = self.result.source[start:stop]
        if (original and not original.isspace()) or not text.isspace():
            raise ValueError("Block separation may replace whitespace only")
        self.edits = {
            key: edit
            for key, edit in self.edits.items()
            if not (start <= edit.start < stop and edit.stop <= stop)
        }
        if original != text:
            self.edits[start, stop] = Edit(start=start, stop=stop, text=text)

    def indent(self, position: int, width: int) -> None:
        """Set indentation when the field starts its physical line."""
        self.gap(line_start(self.result.source, position), position, " " * width)

    def indentation(self, position: int) -> int:
        """Return the planned indentation of a source line."""
        first = line_start(self.result.source, position)
        source = self.result.source
        stop = first
        while stop < position and source[stop].isspace() and source[stop] not in "\r\n":
            stop += 1
        edit = self.edits.get((first, stop))
        return (
            len(edit.text) if edit is not None else len(source[first:stop].expandtabs())
        )

    def column(self, position: int) -> int:
        """Return the zero-based boundary column before insertions at that boundary.

        Args:
            position: Original-source boundary after earlier fields on its line.

        Returns:
            Column after applying edits strictly before the boundary.
        """
        first = line_start(self.result.source, position)
        return (
            position
            - first
            + sum(
                len(edit.text) - (edit.stop - edit.start)
                for edit in self.edits.values()
                if first <= edit.start < position and edit.stop <= position
            )
        )

    def between(self, left: Cell, right: Cell, spaces: int, trailing: int = 0) -> None:
        """Space adjacent fields while retaining an optional comma delimiter.

        Args:
            left: Previous intact field.
            right: Next intact field.
            spaces: Padding and separation before the next field.
            trailing: Padding after the previous field, before a comma if present.
        """
        source = self.result.source
        commas = [
            left.stop + match.start()
            for match in re.finditer(",", source[left.stop : right.start])
        ]
        if commas:
            self.gap(left.stop, commas[0], " " * trailing)
            for first, last in pairwise(commas):
                self.gap(first + 1, last, "")
            self.gap(commas[-1] + 1, right.start, " " * spaces)
        else:
            self.gap(left.stop, right.start, " " * (trailing + spaces))


def line_start(source: str, position: int) -> int:
    """Return the physical line's first offset for LF, CRLF or CR source."""
    return max(source.rfind("\n", 0, position), source.rfind("\r", 0, position)) + 1


def tokens(result: ParseResult, node: ParserRuleContext) -> list[Token]:
    """Return a context's full token interval, including hidden whitespace.

    Args:
        result: Owning parse result.
        node: Successfully parsed context.

    Returns:
        Tokens in the context's original stream order.

    Raises:
        ValueError: The context has no anchored token interval.
    """
    first, last = node.start, node.stop
    if first is None or last is None:
        raise ValueError("Context has no token interval")
    start, stop = first.tokenIndex, last.tokenIndex
    if start is None or stop is None:
        raise ValueError("Context has no token indices")
    return result.tokens.tokens[start : stop + 1]


def sections(
    result: ParseResult, nodes: Iterable[ParserRuleContext]
) -> list[SyntaxSection]:
    """Group consecutive records, retaining blank lines and comment-only boundaries.

    Args:
        result: Owning original source.
        nodes: Records in source order.

    Returns:
        Independent sections of adjacent records.
    """
    groups: list[SyntaxSection] = []
    for node in nodes:
        gap = ""
        if groups:
            first = result.source_span(groups[-1][-1])[1]
            last = result.source_span(node)[0]
            gap = result.source[first:last].replace("\r\n", "\n").replace("\r", "\n")
        if not groups or gap.count("\n") != 1:
            groups.append([])
        groups[-1].append(node)
    return groups


def inside_interpolation(node: ParserRuleContext) -> bool:
    """Return whether a field belongs to literal-sensitive f/t-string source."""
    parent = node.parentCtx
    while isinstance(parent, ParserRuleContext):
        if rule_name(parent) in {"fstring", "tstring"}:
            return True
        parent = parent.parentCtx
    return False
