"""Apply PEP 8 spacing and continuation indentation without moving source rows."""

from itertools import pairwise

from antlr4 import ParserRuleContext, Token
from antlr4.tree.Tree import TerminalNodeImpl

# noinspection PyProtectedMember
from psi4_parser._formatting.arrays import numeric_segments

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import (
    Layout,
    cell,
    inside_interpolation,
    line_start,
)

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import tokens as context_tokens

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._tree import contexts, rule_name, terminals

_OPENING = frozenset({"LPAR", "LSQB", "LBRACE"})
_CLOSING = frozenset({"RPAR", "RSQB", "RBRACE"})
_SIMPLE = frozenset(
    {
        "NAME",
        "NAME_OR_LAZY",
        "NAME_OR_TYPE",
        "NAME_OR_MATCH",
        "NAME_OR_CASE",
        "NUMBER",
        "STRING",
        "NONE",
        "TRUE",
        "FALSE",
        "ELLIPSIS",
    }
)


def format_python(layout: Layout) -> Layout:
    """Apply Python-specific whitespace before scientific table alignment.

    Args:
        layout: Original-source edit plan with ordinary token spacing.

    Returns:
        An independent plan following PEP 8 within the retained physical rows.
    """
    layout = layout.copy()
    nodes = list(contexts(layout.result.tree))
    for node in nodes:
        if inside_interpolation(node):
            continue
        name = rule_name(node)
        if name in {"param_with_default", "param_maybe_default"}:
            _default(layout, node)
        elif name == "slice":
            _slice(layout, node)
        elif name == "except_star_block":
            _except_star(layout, node)
    _continuations(layout, nodes)
    return layout


def _default(layout: Layout, node: ParserRuleContext) -> None:
    children = {
        rule_name(child): child
        for child in node.getChildren()
        if isinstance(child, ParserRuleContext)
    }
    parameter, assignment = children["param"], children.get("default_assignment")
    if assignment is None or not any(
        rule_name(child) == "annotation" for child in contexts(parameter)
    ):
        return
    equals = context_tokens(layout.result, assignment)[0]
    start, stop = layout.result.source_span(equals)
    layout.gap(layout.result.source_span(parameter)[1], start, " ")
    expression = next(
        child
        for child in assignment.getChildren()
        if isinstance(child, ParserRuleContext)
    )
    layout.gap(stop, layout.result.source_span(expression)[0], " ")


def _slice(layout: Layout, node: ParserRuleContext) -> None:
    children = list(node.getChildren())
    fields = [child for child in children if isinstance(child, ParserRuleContext)]
    space = " " if any(not _simple(layout, field) for field in fields) else ""
    for left, right in pairwise(children):
        if isinstance(left, TerminalNodeImpl) and left.getText() == ":":
            if isinstance(right, ParserRuleContext):
                layout.gap(
                    layout.result.source_span(left.getSymbol())[1],
                    layout.result.source_span(right)[0],
                    space,
                )
        elif (
            isinstance(right, TerminalNodeImpl)
            and right.getText() == ":"
            and isinstance(left, ParserRuleContext)
        ):
            layout.gap(
                layout.result.source_span(left)[1],
                layout.result.source_span(right.getSymbol())[0],
                space,
            )


def _simple(layout: Layout, node: ParserRuleContext) -> bool:
    tokens = [
        token
        for token in context_tokens(layout.result, node)
        if token.channel == Token.DEFAULT_CHANNEL
    ]
    if tokens and tokens[0].text in {"+", "-", "~"}:
        tokens = tokens[1:]
    return len(tokens) == 1 and PsithonLexer.symbolicNames[tokens[0].type] in _SIMPLE


def _except_star(layout: Layout, node: ParserRuleContext) -> None:
    tokens = [
        token
        for token in context_tokens(layout.result, node)
        if token.channel == Token.DEFAULT_CHANNEL
    ]
    first, star, value = (cell(layout.result, token) for token in tokens[:3])
    layout.gap(first.stop, star.start, "")
    layout.gap(star.stop, value.start, " ")


def _python_tokens(layout: Layout, nodes: list[ParserRuleContext]) -> list[Token]:
    protected = {
        token.tokenIndex
        for node in nodes
        if rule_name(node) in {"fstring", "tstring"} and not inside_interpolation(node)
        for token in context_tokens(layout.result, node)[1:]
    }
    return [
        token
        for token in layout.result.tokens.tokens
        if token.channel == Token.DEFAULT_CHANNEL
        and token.type != Token.EOF
        and token.tokenIndex not in protected
        and PsithonLexer.symbolicNames[token.type]
        not in {"ENCODING", "INDENT", "DEDENT", "NEWLINE"}
        and not PsithonLexer.symbolicNames[token.type].startswith(("D_", "CFOUR_"))
    ]


def _continuations(layout: Layout, nodes: list[ParserRuleContext]) -> None:
    parameter_openings = {
        layout.result.source_span(child.getSymbol())[0]
        for node in nodes
        if rule_name(node) == "function_def_raw" and not inside_interpolation(node)
        for child in terminals(node)
        if child.getText() == "("
    }
    # Numeric literals retain the table pass's own continuation convention.
    tables = {
        token.tokenIndex
        for node in nodes
        if rule_name(node) in {"list", "tuple"} and numeric_segments(layout, node)
        for token in context_tokens(layout.result, node)
    }
    # Each frame retains the closing-line indent and the continuation column.
    frames: list[tuple[int, int]] = []
    tokens = _python_tokens(layout, nodes)
    for index, token in enumerate(tokens):
        start = layout.result.source_span(token)[0]
        symbol = PsithonLexer.symbolicNames[token.type]
        if symbol in _CLOSING and frames:
            closing, _ = frames.pop()
            if token.tokenIndex not in tables:
                layout.indent(start, closing)
        elif frames and token.tokenIndex not in tables:
            layout.indent(start, frames[-1][1])
        if symbol in _OPENING:
            base = layout.indentation(start)
            following = tokens[index + 1] if index + 1 < len(tokens) else token
            position = layout.result.source_span(following)[0]
            inline = line_start(layout.result.source, start) == line_start(
                layout.result.source, position
            )
            column = (
                layout.column(position)
                if inline and PsithonLexer.symbolicNames[following.type] not in _CLOSING
                else base + (8 if start in parameter_openings else 4)
            )
            frames.append((base, column))
