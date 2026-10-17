"""Surround native block statements without moving comments or data rows."""

import re
from itertools import pairwise

from antlr4 import ParserRuleContext, Token

from psi4_parser._formatting.layout import (
    Layout,
    inside_interpolation,
    line_start,
    tokens,
)
from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._tree import contexts, rule_name

_BLOCKS = frozenset(
    {
        "molecule_block",
        "set_block",
        "basis_block",
        "external_block",
        "pcm_block",
        "cfour_block",
    }
)


def format_blocks(layout: Layout) -> Layout:
    """Put one empty line on each side of standalone native block statements.

    Only neighboring statements in the same Python suite share a separator.
    Inline native directives and native expressions retain their existing rows.

    Args:
        layout: Completed horizontal-spacing plan.

    Returns:
        An independent plan with canonical native block boundaries.
    """
    layout = layout.copy()
    for suite in contexts(layout.result.tree):
        if rule_name(suite) != "statements" or inside_interpolation(suite):
            continue
        statements = [
            node for node in suite.getChildren() if isinstance(node, ParserRuleContext)
        ]
        for left, right in pairwise(statements):
            if not (_is_block(left) or _is_block(right)):
                continue
            start = _statement_end(layout, left)
            stop = layout.result.source_span(right)[0]
            separator = _separator(layout.result.source, start, stop)
            if separator is not None:
                first, last, text = separator
                layout.line_breaks(first, last, text)
    return layout


def _is_block(statement: ParserRuleContext) -> bool:
    node = statement
    for wrapper in ("statement", "psithon_statement", "native_expression"):
        if rule_name(node) != wrapper:
            return False
        node = next(
            child
            for child in node.getChildren()
            if isinstance(child, ParserRuleContext)
        )
    return rule_name(node) in _BLOCKS


def _statement_end(layout: Layout, statement: ParserRuleContext) -> int:
    last = next(
        token
        for token in reversed(tokens(layout.result, statement))
        if token.channel == Token.DEFAULT_CHANNEL
        and PsithonLexer.symbolicNames[token.type]
        not in {"NEWLINE", "D_NEWLINE", "INDENT", "DEDENT"}
    )
    return layout.result.source_span(last)[1]


def _separator(source: str, start: int, stop: int) -> tuple[int, int, str] | None:
    if start >= stop:
        return None
    gap = source[start:stop]
    lines = gap.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if any(
        line.strip() and not line.lstrip().startswith(("#", "\\#")) for line in lines
    ):
        return None
    first = re.search(r"\r\n|\r|\n", gap)
    if first is None:
        return None
    anchor = line_start(source, stop)
    for match in re.finditer(r"(?:\r\n|\r|\n)([^\r\n]*)", gap):
        if gap[match.start(1) : match.end(1)].lstrip().startswith(("#", "\\#")):
            anchor = start + match.start(1)
            break
    begin = start + first.start()
    breaks = [
        match.group() for match in re.finditer(r"\r\n|\r|\n", source[begin:anchor])
    ]
    if not breaks:
        return None
    return begin, anchor, breaks[0] + breaks[-1]
