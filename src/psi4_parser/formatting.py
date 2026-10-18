"""Format through ANTLR source spans, then verify the represented program."""

import re
from bisect import bisect_right
from collections.abc import Iterator

from antlr4 import ParserRuleContext, Token
from antlr4.tree.Tree import TerminalNodeImpl

# noinspection PyProtectedMember
from psi4_parser._formatting.arrays import format_arrays

# noinspection PyProtectedMember
from psi4_parser._formatting.blocks import format_blocks

# noinspection PyProtectedMember
from psi4_parser._formatting.comments import format_comments

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import Edit as _Edit

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import Layout

# noinspection PyProtectedMember
from psi4_parser._formatting.molecules import format_molecules

# noinspection PyProtectedMember
from psi4_parser._formatting.options import format_occupations, format_options

# noinspection PyProtectedMember
from psi4_parser._formatting.python import format_python

# noinspection PyProtectedMember
from psi4_parser._formatting.verification import restore_molecule_layout

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._tree import contexts, rule_name
from psi4_parser.api import ParseResult, parse
from psi4_parser.ast import InvalidInputError, build_ast

_LAYOUT = frozenset({"INDENT", "DEDENT", "NEWLINE", "D_NEWLINE"})
_BINARY = frozenset(
    {"+", "-", "*", "**", "/", "//", "%", "@", "<<", ">>", "&", "|", "^"}
)
_ASSIGNMENT = frozenset(
    {
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "//=",
        "%=",
        "**=",
        "@=",
        "&=",
        "|=",
        "^=",
        "<<=",
        ">>=",
        ":=",
    }
)
_COMPARISON = frozenset({"==", "!=", "<>", "<", ">", "<=", ">=", "->"})
_CALL_KEYWORDS = frozenset(
    {
        "if",
        "elif",
        "while",
        "for",
        "with",
        "except",
        "match",
        "case",
        "return",
        "yield",
        "assert",
        "raise",
        "not",
        "and",
        "or",
        "in",
        "is",
        "lambda",
        "import",
        "from",
        "del",
        "await",
    }
)
_COMPACT_EQUALS = frozenset(
    {
        "default_assignment",
        "type_param_default",
        "type_param_starred_default",
        "kwarg_or_starred",
        "kwarg_or_double_starred",
        "keyword_pattern",
    }
)
_LITERAL_RULES = frozenset(
    {
        "fstring",
        "tstring",
        "inline_option_value",
        "set_option_value",
        "basis_record",
        "basis_name",
        "basis_label",
        "module_list",
    }
)
_OPAQUE_BLOCKS = frozenset(
    {"molecule_block", "external_block", "pcm_block", "cfour_block"}
)


class FormattingError(ValueError):
    """Reject a formatting candidate whose preservation checks fail."""


class _ProtectedRanges:
    """Locate literal and foreign-data spans using the grammar's contexts."""

    def __init__(self, result: ParseResult) -> None:
        ranges: list[tuple[int, int]] = []
        for node in contexts(result.tree):
            name = rule_name(node)
            if name in _LITERAL_RULES:
                ranges.append(result.source_span(node))
            elif name in _OPAQUE_BLOCKS:
                start, stop = result.source_span(node)
                opening = result.source.index("{", start, stop)
                ranges.append((opening, stop))
        ranges.extend(
            result.source_span(token)
            for token in result.tokens.tokens
            if _symbol(token) in {"STRING", "D_STRING", "CFOUR_TEXT"}
        )
        merged: list[tuple[int, int]] = []
        for start, stop in sorted(ranges):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(stop, merged[-1][1]))
            else:
                merged.append((start, stop))
        self._ranges = tuple(merged)
        self._starts = tuple(start for start, _ in merged)

    def overlaps(self, start: int, stop: int) -> bool:
        """Return whether an edit touches the interior of protected source."""
        index = bisect_right(self._starts, start) - 1
        if index >= 0:
            first, last = self._ranges[index]
            if start < last and (start < stop or first < start):
                return True
        following = index + 1
        return following < len(self._ranges) and self._starts[following] < stop


def format_source(source: str) -> str:
    """Apply the documented whitespace style and verify every returned result.

    Args:
        source: Native input, including its original comments and line endings.

    Returns:
        Source with canonical spacing and four-space Python suite indentation.
        Numeric and literal spelling is retained; molecule and table layout aligns.
        Foreign solver and basis payloads retain their exact original text.

    Raises:
        InvalidInputError: The original input is invalid.
        FormattingError: Validation, AST equality, CST equality or idempotence fails.
    """
    original = parse(source)
    if original.diagnostics:
        raise InvalidInputError(original.diagnostics)
    candidate = _render(original)
    formatted = parse(candidate)
    verify_format(original, formatted)
    if _render(formatted) != candidate:
        raise FormattingError("Formatting is not idempotent")
    return candidate


def verify_format(original: str | ParseResult, formatted: str | ParseResult) -> None:
    """Require valid, equivalent ASTs and unchanged significant CST structure.

    Source locations and whitespace spelling are excluded from comparison.
    Native molecule layout is checked through its CST fields and literal records
    before restoring its original body for lowered-Python AST comparison. Ordinary
    Python literals, template expressions and retained native payloads stay strict.

    Args:
        original: Original source or its existing parse result.
        formatted: Candidate output or its existing parse result.

    Raises:
        InvalidInputError: The original input is invalid.
        FormattingError: The candidate is invalid or changes either syntax tree.
    """
    before = parse(original) if isinstance(original, str) else original
    after = parse(formatted) if isinstance(formatted, str) else formatted
    if before.diagnostics:
        raise InvalidInputError(before.diagnostics)
    if after.diagnostics:
        raise FormattingError(
            "Formatted input is invalid: " + after.diagnostics[0].message
        )
    if tuple(_events(before.tree)) != tuple(_events(after.tree)):
        reason = (
            "significant CST"
            if build_ast(before).equivalent(build_ast(after))
            else "program AST"
        )
        raise FormattingError("Formatting changed the " + reason)
    if before.native_data != after.native_data:
        raise FormattingError("Formatting changed native payloads in the program AST")
    try:
        comparison_source = restore_molecule_layout(before, after)
    except ValueError as error:
        raise FormattingError(str(error)) from error
    comparison = (
        after if comparison_source == after.source else parse(comparison_source)
    )
    if comparison.diagnostics or not build_ast(before).equivalent(
        build_ast(comparison)
    ):
        raise FormattingError("Formatting changed the program AST")


def _events(node: ParserRuleContext) -> Iterator[tuple[int, int, str]]:
    yield 0, node.getRuleIndex(), ""
    for child in node.getChildren():
        if isinstance(child, ParserRuleContext):
            yield from _events(child)
        elif isinstance(child, TerminalNodeImpl):
            token = child.getSymbol()
            text = "" if _symbol(token) in _LAYOUT else token.text
            yield 1, token.type, text
    yield 2, 0, ""


def _symbol(token: Token) -> str:
    return "EOF" if token.type == Token.EOF else PsithonLexer.symbolicNames[token.type]


def _roles(result: ParseResult) -> dict[int, str]:
    roles: dict[int, str] = {}
    for node in contexts(result.tree):
        for child in node.getChildren():
            if isinstance(child, TerminalNodeImpl):
                index = child.getSymbol().tokenIndex
                if index is not None:
                    roles[index] = rule_name(node)
        if rule_name(node) == "import_from":
            roles.update(_relative_dot_roles(node))
    for dot in _sensitive_dots(result):
        if dot.tokenIndex is not None:
            roles[dot.tokenIndex] = "sensitive_dot"
    return roles


def _relative_dot_roles(node: ParserRuleContext) -> dict[int, str]:
    roles: dict[int, str] = {}
    run = 0
    for child in node.getChildren():
        if isinstance(child, TerminalNodeImpl):
            token = child.getSymbol()
            run = run + 1 if token.text == "." else 0
            if token.tokenIndex is not None and token.text in {".", "..."}:
                roles[token.tokenIndex] = (
                    "relative_dot_even" if run and run % 2 == 0 else "relative_dot"
                )
    return roles


def _sensitive_dots(result: ParseResult) -> Iterator[Token]:
    tokens = [
        token
        for token in result.tokens.tokens
        if token.channel == Token.DEFAULT_CHANNEL and _symbol(token) not in _LAYOUT
    ]
    for left, dot, right in zip(tokens[:-2], tokens[1:-1], tokens[2:], strict=True):
        sensitive = left.text == "psi4" or right.text == "extract_subsets"
        if dot.text == "." and sensitive:
            left_gap = result.source_span(dot)[0] - result.source_span(left)[1]
            right_gap = result.source_span(right)[0] - result.source_span(dot)[1]
            if left_gap or right_gap:
                yield dot


def _line_start(source: str, position: int) -> int:
    return max(source.rfind("\n", 0, position), source.rfind("\r", 0, position)) + 1


def _render(result: ParseResult) -> str:
    protected = _ProtectedRanges(result)
    roles = _roles(result)
    edits = list(_token_edits(result, protected, roles))
    edits.extend(_trailing_edits(result, protected))
    layout = Layout(result, edits)
    # Each pass owns a visible style decision. More specific passes override
    # ordinary spacing at the same source gap; none may replace data tokens.
    layout = format_python(layout)
    layout = format_molecules(layout)
    layout = format_options(layout)
    layout = format_arrays(layout)
    layout = format_occupations(layout)
    layout = format_comments(layout)
    layout = format_blocks(layout)
    source = result.source
    for edit in sorted(layout.edits.values(), key=_edit_order, reverse=True):
        source = source[: edit.start] + edit.text + source[edit.stop :]
    eof, _ = result.source_span(result.tokens.tokens[-1])
    if source and not source.endswith(("\r", "\n")) and eof == len(result.source):
        newline = re.search(r"\r\n|\r|\n", result.source)
        if newline is None:
            source += "\n"
        else:
            source += newline.group()
    return source


class _Indentation:
    """Track Python suites and delimiter continuations independently of native data."""

    def __init__(self) -> None:
        self._suite = 0
        self._native = 0
        self._delimiters = 0
        self._continued = False

    def before(self, token: Token) -> int:
        """Update layout state before the current token.

        Args:
            token: Current default-channel token.

        Returns:
            Suite and continuation depth at this token.
        """
        symbol = _symbol(token)
        if symbol == "EXPLICIT_LINE_JOINING":
            self._continued = True
        elif symbol == "NEWLINE":
            self._continued = False
        self._suite += int(symbol == "INDENT") - int(symbol == "DEDENT")
        self._native -= int(symbol == "D_RBRACE")
        closing = symbol in {"RPAR", "RSQB", "RBRACE"}
        continuation = int(self._continued and self._delimiters == 0)
        return (
            self._suite
            + self._native
            + continuation
            + max(0, self._delimiters - int(closing))
        )

    def after(self, token: Token) -> None:
        """Account for delimiters opened or closed by the current token."""
        symbol = _symbol(token)
        self._native += int(symbol == "D_LBRACE")
        self._delimiters += int(symbol in {"LPAR", "LSQB", "LBRACE"})
        self._delimiters -= int(symbol in {"RPAR", "RSQB", "RBRACE"})


def _edit_order(edit: _Edit) -> tuple[int, int]:
    return edit.start, edit.stop


def _token_edits(
    result: ParseResult, protected: _ProtectedRanges, roles: dict[int, str]
) -> Iterator[_Edit]:
    indentation = _Indentation()
    previous: Token | None = None
    for token in result.tokens.tokens:
        symbol = _symbol(token)
        depth = indentation.before(token)
        if token.channel != Token.DEFAULT_CHANNEL:
            continue
        if symbol in _LAYOUT or symbol == "EOF":
            continue
        start, stop = result.source_span(token)
        if start == stop:
            continue
        first = _line_start(result.source, start)
        prefix = result.source[first:start]
        if _horizontal_space(prefix, native=symbol.startswith(("D_", "PSI_"))):
            yield from _edit(result, protected, first, start, " " * (4 * depth))
        elif previous is not None:
            previous_stop = result.source_span(previous)[1]
            gap = result.source[previous_stop:start]
            native = symbol.startswith("D_") or _symbol(previous).startswith("D_")
            if _horizontal_space(gap, native=native):
                space = _space(previous, token, roles)
                yield from _edit(result, protected, previous_stop, start, space)
        indentation.after(token)
        previous = token


def _horizontal_space(text: str, *, native: bool) -> bool:
    if native:
        # D_INLINE_SPACE uses the pinned Python Unicode whitespace inventory.
        return all(char.isspace() and char not in "\r\n" for char in text)
    return not text.strip(" \t\f")


def _edit(
    result: ParseResult,
    protected: _ProtectedRanges,
    start: int,
    stop: int,
    text: str,
) -> Iterator[_Edit]:
    if result.source[start:stop] != text and not protected.overlaps(start, stop):
        yield _Edit(start=start, stop=stop, text=text)


def _trailing_edits(
    result: ParseResult, protected: _ProtectedRanges
) -> Iterator[_Edit]:
    start, eof = result.input_span or (0, len(result.source))
    for match in re.finditer(r"[^\S\r\n]+(?=\r?\n|\r|$)", result.source[start:eof]):
        first, last = start + match.start(), start + match.end()
        prefix = result.source[_line_start(result.source, first) : first]
        if "#" not in prefix:
            yield from _edit(result, protected, first, last, "")


def _role(token: Token, roles: dict[int, str]) -> str:
    return roles.get(token.tokenIndex, "") if token.tokenIndex is not None else ""


def _unary(token: Token, roles: dict[int, str]) -> bool:
    role = _role(token, roles)
    return (
        token.text in {"+", "-", "~"}
        and role in {"factor", "signed_number", "signed_real_number"}
    ) or (token.text in {"*", "**"} and role not in {"term", "power"})


def _operator_space(token: Token, roles: dict[int, str]) -> str | None:
    if token.text == "=" and _role(token, roles) in _COMPACT_EQUALS:
        return ""
    if token.text in _ASSIGNMENT | _COMPARISON:
        return " "
    if token.text in _BINARY and not _unary(token, roles):
        return " "
    return None


def _punctuation_space(left: Token, right: Token, roles: dict[int, str]) -> str | None:
    before, after = left.text, right.text
    if after in {",", ";", ")", "]", "}"}:
        return ""
    if after == ":" or (before == ":" and _role(left, roles) == "slice"):
        return ""
    if before in {",", ";", ":"}:
        return " "
    if before in {"(", "[", "{"}:
        return ""
    return None


def _relative_space(left: Token, right: Token, roles: dict[int, str]) -> str | None:
    left_role, right_role = _role(left, roles), _role(right, roles)
    if right_role.startswith("relative_") and left.text == "from":
        return " "
    if left_role.startswith("relative_"):
        if right.text == "import":
            return " "
        if right_role.startswith("relative_"):
            separated = left.text == "." and (
                right.text == "..." or left_role == "relative_dot_even"
            )
            return " " if separated else ""
        return ""
    return None


def _adjacent_space(left: Token, right: Token, roles: dict[int, str]) -> str:
    if "sensitive_dot" in {_role(left, roles), _role(right, roles)}:
        return " "
    relative = _relative_space(left, right, roles)
    if relative is not None:
        return relative
    if left.text == "." or right.text == ".":
        return " " if right.text == "." and _symbol(left) == "NUMBER" else ""
    if right.text in {"(", "["}:
        keyword = left.text in _CALL_KEYWORDS and _role(left, roles) != "name"
        return " " if keyword else ""
    return " "


def _space(left: Token, right: Token, roles: dict[int, str]) -> str:
    if _symbol(left).startswith("D_") or _symbol(right).startswith("D_"):
        return "" if _symbol(right) == "SEMI" else " "
    punctuation = _punctuation_space(left, right, roles)
    if punctuation is not None:
        return punctuation
    if _unary(left, roles) or (left.text == "@" and _role(left, roles) == "decorators"):
        return ""
    left_space = _operator_space(left, roles)
    right_space = _operator_space(right, roles)
    if left_space is not None or right_space is not None:
        return left_space if left_space is not None else right_space or ""
    return _adjacent_space(left, right, roles)
