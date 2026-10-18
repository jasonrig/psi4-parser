"""Indent native molecule records and align Cartesian and Z-matrix fields."""

from itertools import pairwise

from antlr4 import ParserRuleContext, Token
from antlr4.tree.Tree import TerminalNodeImpl

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import (
    Alignment,
    Cell,
    Layout,
    cell,
    inside_interpolation,
    padding,
    sections,
    tokens,
)

# noinspection PyProtectedMember
from psi4_parser._formatting.verification import xyz_title_span
from psi4_parser._tree import contexts, rule_name


def format_molecules(layout: Layout) -> Layout:
    """Apply molecule styles using grammar fields, without touching literal records.

    Args:
        layout: Shared original-source edit plan.

    Returns:
        An independent edit plan with this style applied.
    """
    layout = layout.copy()
    result = layout.result
    for block in contexts(result.tree):
        if rule_name(block) != "molecule_block" or inside_interpolation(block):
            continue
        base = layout.indentation(result.source_span(block)[0])
        rows, variables = _records(layout, block, base)
        _align_atoms(layout, rows)
        _variables(layout, variables)
        for child in block.getChildren():
            if isinstance(child, TerminalNodeImpl) and child.getText() == "}":
                layout.indent(result.source_span(child.getSymbol())[0], base)

    return layout


def _records(
    layout: Layout, block: ParserRuleContext, base: int
) -> tuple[dict[str, list[list[Cell]]], list[ParserRuleContext]]:
    result = layout.result
    rows: dict[str, list[list[Cell]]] = {"cartesian": [], "zmatrix": [], "numeric": []}
    variables = []
    title = xyz_title_span(result, block)
    for node in contexts(block):
        name = rule_name(node)
        start, stop = result.source_span(node)
        if title is not None and title[0] <= start <= title[1]:
            continue
        if name in {"molecule_line", "xyz_header", "numeric_xyz"}:
            layout.indent(result.source_span(node)[0], base + 4)
            _metadata(layout, node)
        if name == "atom_line" and not (title is not None and stop < title[0]):
            fields, kind = _atom_fields(layout, node)
            rows[kind].append(fields)
            layout.indent(fields[0].start, base + 4)
        elif name == "numeric_xyz":
            rows["numeric"].append(
                [
                    cell(result, token)
                    for token in tokens(result, node)
                    if token.channel == Token.DEFAULT_CHANNEL and token.text != ","
                ]
            )
        elif name == "geometry_variable":
            variables.append(node)
    return rows, variables


def _align_atoms(layout: Layout, rows: dict[str, list[list[Cell]]]) -> None:
    for kind, records in rows.items():
        width = max(map(len, records), default=0)
        modes: list[Alignment] = ["left"]
        modes.extend(
            "right" if kind == "zmatrix" and index % 2 else "number"
            for index in range(1, width)
        )
        if kind == "numeric":
            modes[0] = "number"
        pads = padding(records, modes)
        for row, row_pads in zip(records, pads, strict=True):
            if kind == "numeric":
                layout.indent(
                    row[0].start, layout.indentation(row[0].start) + row_pads[0][0]
                )
            for index in range(1, len(row)):
                gap = 1 if kind == "zmatrix" and index % 2 == 0 else 2
                layout.between(
                    row[index - 1],
                    row[index],
                    gap + row_pads[index][0],
                    row_pads[index - 1][1],
                )


def _atom_fields(layout: Layout, atom: ParserRuleContext) -> tuple[list[Cell], str]:
    children = [
        child for child in atom.getChildren() if isinstance(child, ParserRuleContext)
    ]
    fields = [cell(layout.result, children[0], literal=True)]
    kind = (
        "cartesian"
        if any(rule_name(child) == "coordinate" for child in children)
        else "zmatrix"
    )
    for child in children[1:]:
        if rule_name(child) == "anchor_pair":
            for part in child.getChildren():
                if isinstance(part, ParserRuleContext):
                    fields.append(cell(layout.result, part))
                elif isinstance(part, TerminalNodeImpl) and part.getText() != ",":
                    fields.append(cell(layout.result, part.getSymbol()))
        else:
            fields.append(cell(layout.result, child))
    return fields, kind


def _variables(layout: Layout, variables: list[ParserRuleContext]) -> None:
    for group in sections(layout.result, variables):
        records = []
        result = layout.result
        for node in group:
            source_tokens = [
                token
                for token in tokens(result, node)
                if token.channel == Token.DEFAULT_CHANNEL
            ]
            equals = next(token for token in source_tokens if token.text == "=")
            first, last = result.source_span(equals)
            start = result.source_span(node)[0]
            lhs_end = first
            while lhs_end > start and result.source[lhs_end - 1].isspace():
                lhs_end -= 1
            records.append(
                (
                    lhs_end,
                    first,
                    last,
                    result.source_span(source_tokens[-1])[0],
                    len(result.source[start:lhs_end]),
                )
            )
        width = max((size for _, _, _, _, size in records), default=0)
        for lhs_end, first, last, value_start, size in records:
            layout.gap(lhs_end, first, " " * (width - size + 1))
            layout.gap(last, value_start, " ")


def _metadata(layout: Layout, node: ParserRuleContext) -> None:
    fields = []
    for child in node.getChildren():
        if isinstance(child, TerminalNodeImpl):
            if child.getText() not in {"\n", "\r\n", "\r"}:
                fields.append(cell(layout.result, child.getSymbol()))
        elif isinstance(child, ParserRuleContext):
            if rule_name(child) in {"charge_multiplicity", "efp_fragment"}:
                _metadata(layout, child)
            fields.append(cell(layout.result, child))
    for left, right in pairwise(fields):
        space = (
            "" if right.text in {",", ":"} or left.text == right.text == "=" else " "
        )
        layout.gap(left.stop, right.start, space)
