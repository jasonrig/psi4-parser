"""Exercise source-preserving access to the grammar's concrete syntax tree."""

import pytest
from antlr4 import CommonTokenStream, InputStream, ParserRuleContext, Token
from antlr4.Token import CommonToken

from psi4_parser import parse, validate

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonLexer import PsithonLexer

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonParser import PsithonParser


def test_lexer_retains_original_source() -> None:
    """Keep comments and physical newlines before validation preprocessing."""
    source = "# header\r\nx = 12# trailing comment\r\n\t# final comment"
    lexer = PsithonLexer(InputStream(source))
    tokens = CommonTokenStream(lexer)
    tokens.fill()

    assert lexer.original_source == source


def _rule(root: ParserRuleContext, name: str) -> ParserRuleContext:
    pending = [root]
    index = PsithonParser.ruleNames.index(name)
    while pending:
        node = pending.pop()
        if node.getRuleIndex() == index:
            return node
        pending.extend(
            child
            for child in node.getChildren()
            if isinstance(child, ParserRuleContext)
        )
    raise AssertionError("Missing grammar rule: " + name)


def test_native_context_preserves_comments_and_crlf() -> None:
    """Recover a native block's exact spelling despite masked comment tokens."""
    block = "molecule atom {\r\n  He # geometry comment\r\n}"
    source = "# leading\r\n\r\n" + block + "\r\n# trailing\t"

    result = parse(source)
    node = _rule(result.tree, "molecule_block")

    assert not result.diagnostics
    assert result.source == source
    assert result.input_span == (0, len(source))
    assert result.source_text(node) == block
    assert result.source_span(node) == (source.index("molecule"), source.index("}") + 1)
    assert result.tokens.fetchedEOF
    assert any(token.channel == Token.HIDDEN_CHANNEL for token in result.tokens.tokens)


@pytest.mark.parametrize(
    "source",
    [
        "",
        "\n",
        "\r",
        "\r\n",
        "# comment",
        "x = 1",
        "x = 1\r",
        "x = 1\r\n",
        "x = 1\nx = 2\ry = 3\r\n",
    ],
)
def test_original_end_of_input(source: str) -> None:
    """Map physical and synthetic EOF boundaries without inventing source text.

    Args:
        source: Input with empty, mixed or missing physical line endings.
    """
    result = parse(source)
    eof = result.tokens.tokens[-1]

    assert not result.diagnostics
    assert result.source == source
    assert eof.type == Token.EOF
    assert result.source_span(eof) == (len(source), len(source))
    assert result.source_text(eof) == ""


def test_synthetic_dedent_has_empty_source_span() -> None:
    """Keep ANTLR layout tokens anchored after a missing terminal newline."""
    source = "if True:\r\n    value = 1"
    result = parse(source)
    dedent = next(
        token
        for token in result.tokens.tokens
        if PsithonLexer.symbolicNames[token.type] == "DEDENT"
    )

    assert not result.diagnostics
    assert result.source_span(dedent) == (len(source), len(source))
    assert result.source_text(dedent) == ""


def test_unicode_token_offsets_count_characters() -> None:
    """Use Python string offsets after Unicode text and mixed newline spellings."""
    source = "\N{GREEK SMALL LETTER ALPHA} = 'β'\r\nvalue = 3\r"
    result = parse(source)
    token = next(token for token in result.tokens.tokens if token.text == "value")

    assert not result.diagnostics
    assert result.source_span(token) == (
        source.index("value"),
        source.index("value") + 5,
    )
    assert result.source_text(token) == "value"


def test_literal_cfour_source_is_unchanged() -> None:
    """Preserve literal hashes, quotes and CRLF inside foreign-program data."""
    body = "\r\n  # literal hash\r\n  'unmatched quote\r\n"
    result = parse("cfour {" + body + "}\r\n")
    token = next(
        token
        for token in result.tokens.tokens
        if PsithonLexer.symbolicNames[token.type] == "CFOUR_TEXT"
    )

    assert not result.diagnostics
    assert result.source_text(token) == body


def test_extracted_input_maps_to_original_log() -> None:
    """Keep the full output log and locate extracted input in its original text."""
    delimiter = "-" * 74
    block = "molecule atom {\r\n  He # comment\r\n}"
    source = (
        "Psi4: An Open-Source Ab Initio Electronic Structure Package\r\n"
        "  ==> Input File <==\r\n\r\n"
        + delimiter
        + "\r\n"
        + block
        + "\r\n"
        + delimiter
        + "\r\nCalculation output\r\n"
    )

    result = parse(source)
    node = _rule(result.tree, "molecule_block")
    eof = result.tokens.tokens[-1]

    assert not result.diagnostics
    assert result.source == source
    assert result.source_text(node) == block
    assert result.source_span(node) == (source.index("molecule"), source.index("}") + 1)
    boundary = source.rindex(delimiter)
    assert result.input_span == (source.index(block), boundary)
    assert result.source_span(eof) == (boundary, boundary)


@pytest.mark.parametrize(
    ("source", "line"),
    [("answer =\r\n", 1), ("molecule {\r\nHe\r\n", 3), ("return 1", 1)],
)
def test_invalid_parse_retains_source_and_diagnostics(source: str, line: int) -> None:
    """Expose recovered input without hiding syntax, native or scope errors.

    Args:
        source: Input rejected at a distinct validation layer.
        line: Original line containing the first reported error.
    """
    result = parse(source)

    assert result.diagnostics
    assert bool(result.diagnostics) == bool(validate(source))
    assert result.diagnostics[0].line == line
    assert result.source == source
    assert result.tokens.tokens[-1].type == Token.EOF


def test_malformed_output_log_retains_source() -> None:
    """Keep malformed log text even when input extraction adds an error marker."""
    source = (
        "Psi4: An Open-Source Ab Initio Electronic Structure Package\r\nmissing input"
    )

    result = parse(source)

    assert result.diagnostics
    assert result.source == source
    assert result.source_span(result.tokens.tokens[-1]) == (len(source), len(source))


def test_unanchored_recovery_token_has_no_source_span() -> None:
    """Refuse to assign an invented source location to ANTLR's missing tokens."""
    result = parse("value = 1\n")
    missing = CommonToken()

    with pytest.raises(ValueError, match="no anchored source interval"):
        result.source_span(missing)


@pytest.mark.parametrize("prefix", ["f", "t"])
@pytest.mark.parametrize(
    ("literal", "positions"),
    [
        ('"abc{{xyz}}"', [(1, 14), (1, 19)]),
        ('"""abc\r\n{{xyz}}"""', [(2, 1), (2, 6)]),
    ],
)
def test_interpolation_braces_keep_exact_source_positions(
    prefix: str, literal: str, positions: list[tuple[int, int]]
) -> None:
    """Locate split escaped braces after literal text and physical newlines.

    Args:
        prefix: Formatted-string or template-string prefix.
        literal: Single-line or multiline string containing escaped braces.
        positions: Expected logical line and column for the second brace of each pair.
    """
    source = "value = " + prefix + literal + "\r\n"
    result = parse(source)
    braces = [
        token
        for token in result.tokens.tokens
        if token.channel == Token.HIDDEN_CHANNEL
        and PsithonLexer.symbolicNames[token.type] in {"LBRACE", "RBRACE"}
    ]

    assert not result.diagnostics
    assert [result.source_text(token) for token in braces] == ["{", "}"]
    assert [(token.line, token.column) for token in braces] == positions
    assert [result.source_span(token) for token in braces] == [
        (source.index("{{") + 1, source.index("{{") + 2),
        (source.index("}}") + 1, source.index("}}") + 2),
    ]
