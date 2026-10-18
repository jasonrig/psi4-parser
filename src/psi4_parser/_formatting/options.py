"""Align native option sections and related occupation vectors."""

from collections.abc import Iterator
from itertools import pairwise

from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl
from pydantic import BaseModel, ConfigDict, Field

# noinspection PyProtectedMember
from psi4_parser._formatting.arrays import NumericRow, align_segments, numeric_segments

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import Layout, cell, inside_interpolation, sections
from psi4_parser._tree import contexts, rule_name


class OccupationVector(BaseModel):
    """Retain wrapped numeric rows with their starting continuation column."""

    model_config = ConfigDict(frozen=True, strict=True)
    rows: list[NumericRow] = Field(
        description="Physical segments of one occupation vector."
    )
    baseline: int = Field(
        description="Column used to align corresponding vector entries."
    )


def format_options(layout: Layout) -> Layout:
    """Align keys and values within explicit, contiguous native option sections.

    Args:
        layout: Shared edit plan after base spacing.

    Returns:
        An independent edit plan with this style applied.
    """
    layout = layout.copy()
    for group in _option_sections(layout):
        _section(layout, group)
    return layout


def _option_sections(layout: Layout) -> Iterator[list[ParserRuleContext]]:
    result = layout.result
    for block in contexts(result.tree):
        if rule_name(block) == "set_block" and not inside_interpolation(block):
            nodes = [
                node
                for node in block.getTypedRuleContexts(ParserRuleContext)
                if rule_name(node) == "option_assignment"
            ]
            yield from sections(result, nodes)


def _section(layout: Layout, nodes: list[ParserRuleContext]) -> None:
    records = []
    for node in nodes:
        fields = [
            child
            for child in node.getChildren()
            if isinstance(child, ParserRuleContext)
        ]
        key, value = cell(layout.result, fields[0]), cell(layout.result, fields[-1])
        equals = [
            child.getSymbol()
            for child in node.getChildren()
            if isinstance(child, TerminalNodeImpl)
        ]
        records.append((key, value, equals))
    width = max(len(key.text) + len(equals) + 2 for key, _, equals in records)
    for key, value, equals in records:
        if equals:
            for first, last in pairwise(equals):
                layout.gap(
                    layout.result.source_span(first)[1],
                    layout.result.source_span(last)[0],
                    "",
                )
            left, right = (
                layout.result.source_span(equals[0])[0],
                layout.result.source_span(equals[-1])[1],
            )
            layout.gap(key.stop, left, " " * (width - len(key.text) - len(equals) - 1))
            layout.gap(right, value.start, " ")
        else:
            layout.gap(key.stop, value.start, " " * (width - len(key.text)))


def format_occupations(layout: Layout) -> Layout:
    """Align adjacent equal-length option vectors after ordinary array spacing.

    Args:
        layout: Edit plan with aligned option values and formatted arrays.

    Returns:
        An independent plan with corresponding vector columns aligned.
    """
    layout = layout.copy()
    for section in _option_sections(layout):
        group: list[OccupationVector] = []
        for node in section:
            vector = _vector(layout, node)
            if vector is None or (
                group
                and tuple(map(_cell_count, group[-1].rows))
                != tuple(map(_cell_count, vector.rows))
            ):
                _align_occupations(layout, group)
                group = []
            if vector is not None:
                group.append(vector)
        _align_occupations(layout, group)
    return layout


def _cell_count(row: NumericRow) -> int:
    """Return a segment's column count for matching wrapped occupation vectors."""
    return len(row.cells)


def _align_occupations(layout: Layout, group: list[OccupationVector]) -> None:
    if len(group) > 1:
        align_segments(
            layout, [vector.rows for vector in group], baseline=group[0].baseline
        )


def _vector(layout: Layout, node: ParserRuleContext) -> OccupationVector | None:
    children = [
        child for child in node.getChildren() if isinstance(child, ParserRuleContext)
    ]
    key, value = children[0], children[-1]
    arrays = [item for item in contexts(value) if rule_name(item) == "set_option_array"]
    if (
        not arrays
        or "BASIS" in key.getText().upper()
        or layout.result.source_span(arrays[0]) != layout.result.source_span(value)
    ):
        return None
    rows = numeric_segments(layout, arrays[0])
    return (
        OccupationVector(
            rows=rows,
            baseline=layout.column(layout.result.source_span(arrays[0])[0] + 1),
        )
        if rows
        else None
    )
