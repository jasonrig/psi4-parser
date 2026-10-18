"""Space comments and align standalone comments with their enclosing scope."""

import re

from antlr4 import ParserRuleContext, Token

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import Layout, line_start, tokens

# noinspection PyProtectedMember
from psi4_parser._formatting.verification import xyz_title_span

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._tree import contexts, rule_name, terminals

_NATIVE = frozenset({"molecule_block", "set_block", "basis_block"})
_FOREIGN = frozenset({"external_block", "pcm_block", "cfour_block"})
_OPENING = frozenset({"LPAR", "LSQB", "LBRACE", "D_LBRACKET", "D_LPAREN"})
_CLOSING = frozenset({"RPAR", "RSQB", "RBRACE", "D_RBRACKET", "D_RPAREN"})
_LAYOUT = frozenset({"NEWLINE", "D_NEWLINE", "INDENT", "DEDENT", "ENCODING"})


def format_comments(layout: Layout) -> Layout:
    """Normalize comment whitespace outside literals and foreign payloads.

    Args:
        layout: Edit plan with completed statement and table spacing.

    Returns:
        An independent plan with two-space inline gaps and scoped comments.
        Source-sensitive gaps before comment markers remain intact.
    """
    layout = layout.copy()
    source = layout.result.source
    if "#" not in source:
        return layout
    nodes = list(contexts(layout.result.tree))
    protected = _literal_ranges(layout, nodes)
    scopes = [node for node in nodes if rule_name(node) in _NATIVE | {"block"}]
    continuations = _continuations(layout)
    first, last = layout.result.input_span or (0, len(source))
    consumed = first
    for marker in re.finditer(r"(?<!\\)(?:\\#|#)", source[first:last]):
        start, stop = first + marker.start(), first + marker.end()
        if start < consumed or any(left <= start < right for left, right in protected):
            continue
        consumed = _line_end(source, stop)
        beginning = line_start(source, start)
        prefix = source[beginning:start]
        if prefix.strip():
            gap = beginning + len(prefix.rstrip())
            escaped = source[start] == "\\"
            # An adjacent unescaped hash consumes the preceding code character.
            if gap < start or escaped:
                layout.gap(gap, start, "  ")
        else:
            layout.indent(start, _indentation(layout, start, scopes, continuations))
        if (
            start == first
            and source[start:stop] == "#"
            and source[stop : stop + 1] == "!"
        ):
            continue
        end = stop
        while end < consumed and source[end].isspace():
            end += 1
        layout.gap(stop, end, " " if end < consumed else "")
    return layout


def _line_end(source: str, position: int) -> int:
    return min(
        (index for newline in "\r\n" if (index := source.find(newline, position)) >= 0),
        default=len(source),
    )


def _literal_ranges(
    layout: Layout, nodes: list[ParserRuleContext]
) -> list[tuple[int, int]]:
    result = layout.result
    ranges = [
        result.source_span(token)
        for token in result.tokens.tokens
        if token.type != Token.EOF
        and PsithonLexer.symbolicNames[token.type] in {"STRING", "D_STRING"}
    ]
    for node in nodes:
        name = rule_name(node)
        if name in {"fstring", "tstring"}:
            ranges.append(result.source_span(node))
        elif name in _FOREIGN:
            start, stop = result.source_span(node)
            ranges.append((result.source.index("{", start, stop) + 1, stop - 1))
        elif name in {"basis_record", "literal_line"}:
            start, stop = result.source_span(node)
            ranges.append((start, _line_end(result.source, stop)))
        elif name == "molecule_block":
            title = xyz_title_span(result, node)
            if title is not None:
                ranges.append(title)
    return ranges


def _indentation(
    layout: Layout,
    position: int,
    scopes: list[ParserRuleContext],
    continuations: list[tuple[int, int, int]],
) -> int:
    candidates = [(0, 0)]
    for scope in scopes:
        if rule_name(scope) == "block":
            candidate = _python_scope(layout, scope, position)
            if candidate is not None:
                candidates.append(candidate)
        else:
            braces = [
                child for child in terminals(scope) if child.getText() in {"{", "}"}
            ]
            start = layout.result.source_span(braces[0].getSymbol())[1]
            stop = layout.result.source_span(braces[-1].getSymbol())[0]
            if start <= position < stop:
                base = layout.indentation(layout.result.source_span(scope)[0])
                candidates.append((start, base + 4))
    candidates.extend(
        (start, width)
        for start, stop, width in continuations
        if start <= position < stop
    )
    return max(candidates)[1]


def _python_scope(
    layout: Layout, scope: ParserRuleContext, position: int
) -> tuple[int, int] | None:
    result = layout.result
    body: ParserRuleContext | None = None
    for child in scope.getChildren():
        if isinstance(child, ParserRuleContext) and rule_name(child) == "statements":
            body = child
            break
    parent = scope.parentCtx
    if body is None or not isinstance(parent, ParserRuleContext):
        return None
    boundary = result.source_span(scope)[0]
    colons = [
        child
        for child in terminals(parent)
        if child.getText() == ":"
        and result.source_span(child.getSymbol())[1] <= boundary
    ]
    start = (
        result.source_span(colons[-1].getSymbol())[1]
        if colons
        else result.source_span(scope)[0]
    )
    stop = result.source_span(scope)[1]
    if not start <= position < stop:
        return None
    first = result.source_span(body)[0]
    significant = [
        token
        for token in tokens(result, body)
        if token.channel == Token.DEFAULT_CHANNEL
        and token.type != Token.EOF
        and PsithonLexer.symbolicNames[token.type] not in _LAYOUT
    ]
    original = result.source[line_start(result.source, first) : first]
    prefix = result.source[line_start(result.source, position) : position]
    if position > result.source_span(significant[-1])[1] and len(
        prefix.expandtabs()
    ) < len(original.expandtabs()):
        return None
    return start, layout.indentation(first)


def _continuations(layout: Layout) -> list[tuple[int, int, int]]:
    result = layout.result
    significant = [
        token
        for token in result.tokens.tokens
        if token.channel == Token.DEFAULT_CHANNEL
        and token.type != Token.EOF
        and PsithonLexer.symbolicNames[token.type] not in _LAYOUT
    ]
    frames: list[tuple[int, int]] = []
    ranges: list[tuple[int, int, int]] = []
    for index, token in enumerate(significant):
        symbol = PsithonLexer.symbolicNames[token.type]
        start, stop = result.source_span(token)
        if symbol in _CLOSING and frames:
            opening, width = frames.pop()
            ranges.append((opening, start, width))
        elif symbol in _OPENING:
            following = significant[index + 1]
            position = result.source_span(following)[0]
            closing = PsithonLexer.symbolicNames[following.type] in _CLOSING
            inline = line_start(result.source, start) == line_start(
                result.source, position
            )
            width = (
                layout.column(position)
                if inline and not closing
                else max(
                    layout.indentation(start) + 4,
                    layout.indentation(position) if not closing else 0,
                )
            )
            frames.append((stop, width))
    return ranges
