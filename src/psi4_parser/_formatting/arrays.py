"""Align numeric list/tuple rows, including native arrays and flat row layouts."""

from collections.abc import Sequence
from itertools import pairwise

from antlr4 import ParserRuleContext, Token
from pydantic import BaseModel, ConfigDict

from psi4_parser._formatting.layout import (
    Cell,
    Layout,
    cell,
    inside_interpolation,
    line_start,
    numeric_anchor,
    padding,
    tokens,
)
from psi4_parser._tree import contexts, rule_name


class NumericRow(BaseModel):
    """Locate a physical segment of numeric cells and its surrounding delimiters.

    Attributes:
        cells: Intact numeric fields, in source order.
        opening: End of an opening delimiter on this line, or None for indentation.
        closing: Start of the following comma or closing delimiter, when present.
    """

    model_config = ConfigDict(frozen=True, strict=True)
    cells: tuple[Cell, ...]
    opening: int | None
    closing: int | None


def format_arrays(layout: Layout) -> Layout:
    """Align numeric rows recognized from list, tuple and native-array CST nodes.

    Args:
        layout: Shared edit plan after base spacing and native option styles.

    Returns:
        An independent edit plan with this style applied.
    """
    layout = layout.copy()
    nodes = [
        node
        for node in contexts(layout.result.tree)
        if rule_name(node) in {"list", "tuple", "set_option_array"}
        and not _protected(node)
    ]
    for node in nodes:
        if rule_name(node) == "set_option_array":
            _native_spacing(layout, node)
            _native_indentation(layout, node)
    by_span = {layout.result.source_span(node): node for node in nodes}
    handled: set[tuple[int, int]] = set()
    for node in nodes:
        span = layout.result.source_span(node)
        if span in handled:
            continue
        items = _items(layout, node)
        nested = [by_span.get((item.start, item.stop)) for item in items]
        if items and all(child is not None for child in nested):
            children = [child for child in nested if child is not None]
            rows = [numeric_segments(layout, child) for child in children]
            if any(rows):
                align_segments(layout, rows)
                handled.update(layout.result.source_span(child) for child in children)
        else:
            flat_rows = numeric_segments(layout, node)
            if len(flat_rows) > 1 and len({len(row.cells) for row in flat_rows}) == 1:
                align_rows(layout, flat_rows)
    return layout


def align_rows(
    layout: Layout, rows: Sequence[NumericRow], *, baseline: int | None = None
) -> None:
    """Apply shared decimal padding to equally sized physical table rows.

    Args:
        layout: Shared whitespace edit plan.
        rows: Numeric rows or matching wrapped segments.
        baseline: Explicit first-cell column for corresponding option vectors.
    """
    if not rows:
        return
    columns = len(rows[0].cells)
    if not columns or any(len(row.cells) != columns for row in rows):
        return
    pads = padding([row.cells for row in rows], ["number"] * columns)
    # Keep columns aligned even when the first row follows code on its line.
    first_row = rows[0]
    baseline = (
        baseline
        if baseline is not None
        else (
            layout.column(first_row.opening)
            if first_row.opening is not None
            else layout.indentation(first_row.cells[0].start)
        )
    )
    for row, row_pads in zip(rows, pads, strict=True):
        first = row.cells[0]
        if row.opening is not None:
            if first_row.opening is not None:
                layout.indent(row.opening - 1, baseline - 1)
            layout.gap(row.opening, first.start, " " * row_pads[0][0])
        else:
            layout.indent(first.start, baseline + row_pads[0][0])
        for index in range(1, columns):
            layout.between(
                row.cells[index - 1],
                row.cells[index],
                1 + row_pads[index][0],
                row_pads[index - 1][1],
            )
        if row.closing is not None:
            layout.gap(row.cells[-1].stop, row.closing, " " * row_pads[-1][1])


def align_segments(
    layout: Layout,
    groups: Sequence[Sequence[NumericRow]],
    *,
    baseline: int | None = None,
) -> None:
    """Align corresponding segments of logical rows with matching wrapping.

    Args:
        layout: Shared edit plan local to the active style pass.
        groups: Physical segments for each logical row or occupation vector.
        baseline: Explicit cell column, or each segment's ordinary indentation.
    """
    if not groups or not all(groups):
        return
    shapes = {tuple(len(segment.cells) for segment in row) for row in groups}
    if len(shapes) == 1:
        for index in range(len(groups[0])):
            align_rows(layout, [row[index] for row in groups], baseline=baseline)


def _items(layout: Layout, node: ParserRuleContext) -> list[Cell]:
    source_tokens = tokens(layout.result, node)[1:-1]
    items: list[Cell] = []
    current: list[Token] = []
    depth = 0
    for token in source_tokens:
        if token.channel != Token.DEFAULT_CHANNEL or token.text in {"\n", "\r\n"}:
            continue
        if token.text == "," and depth == 0:
            if current:
                items.append(_token_cell(layout, current))
                current = []
        else:
            current.append(token)
            depth += int(token.text in {"[", "(", "{"}) - int(
                token.text in {"]", ")", "}"}
            )
    if current:
        items.append(_token_cell(layout, current))
    return items


def _token_cell(layout: Layout, tokens: list[Token]) -> Cell:
    return Cell(
        start=cell(layout.result, tokens[0]).start,
        stop=cell(layout.result, tokens[-1]).stop,
        text="".join(token.text for token in tokens),
    )


def numeric_segments(layout: Layout, node: ParserRuleContext) -> list[NumericRow]:
    """Locate the physical segments of an entirely numeric literal sequence.

    Args:
        layout: Original source and active edit plan.
        node: List, tuple or native array context.

    Returns:
        Numeric segments, or an empty list for mixed or nonliteral values.
    """
    items = _items(layout, node)
    if not items or any(numeric_anchor(item.text) is None for item in items):
        return []
    source = layout.result.source
    rows: list[list[Cell]] = []
    for item in items:
        if line_start(source, item.start) != line_start(source, item.stop):
            return []
        if not rows or line_start(source, item.start) != line_start(
            source, rows[-1][0].start
        ):
            rows.append([])
        rows[-1].append(item)
    opening, closing = layout.result.source_span(node)
    result = []
    for row in rows:
        first = row[0].start
        lead = (
            opening + 1
            if line_start(source, opening) == line_start(source, first)
            else None
        )
        # The final cell is followed by a comma or closing bracket. Do not reach
        # across comments or line breaks when inserting end-of-cell padding.
        stop = row[-1].stop
        end = stop
        while end < closing and source[end].isspace() and source[end] not in "\r\n":
            end += 1
        tail = end if end < closing and source[end] in ",])" else None
        result.append(NumericRow(cells=tuple(row), opening=lead, closing=tail))
    return result


def _protected(node: ParserRuleContext) -> bool:
    if inside_interpolation(node):
        return True
    parent = node.parentCtx
    while isinstance(parent, ParserRuleContext):
        if rule_name(parent) in {"set_command", "option_assignment"}:
            keys = [
                child
                for child in parent.getChildren()
                if isinstance(child, ParserRuleContext)
                and rule_name(child) == "option_key"
            ]
            if keys and "BASIS" in keys[0].getText().upper():
                return True
        parent = parent.parentCtx
    return False


def _native_indentation(layout: Layout, node: ParserRuleContext) -> None:
    parent = node.parentCtx
    depth = 1
    while isinstance(parent, ParserRuleContext) and rule_name(parent) not in {
        "set_command",
        "option_assignment",
    }:
        depth += int(rule_name(parent) == "set_option_array")
        parent = parent.parentCtx
    if not isinstance(parent, ParserRuleContext):
        return
    base = layout.indentation(layout.result.source_span(parent)[0])
    source_tokens = tokens(layout.result, node)
    for token in source_tokens[1:]:
        if token.channel != Token.DEFAULT_CHANNEL or token.text in {"\n", "\r\n"}:
            continue
        position = layout.result.source_span(token)[0]
        closing = token is source_tokens[-1]
        layout.indent(position, base + 4 * (depth - int(closing)))


def _native_spacing(layout: Layout, node: ParserRuleContext) -> None:
    source_tokens = [
        token
        for token in tokens(layout.result, node)
        if token.channel == Token.DEFAULT_CHANNEL and token.text not in {"\n", "\r\n"}
    ]
    for left, right in pairwise(source_tokens):
        if left.text in {"[", ","} or right.text in {",", "]"}:
            space = " " if left.text == "," and right.text != "]" else ""
            layout.gap(
                cell(layout.result, left).stop, cell(layout.result, right).start, space
            )
