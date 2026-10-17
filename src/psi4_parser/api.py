"""Provide a thin entry point for the generated ANTLR parser."""

from typing import override

from antlr4 import CommonTokenStream, InputStream, ParserRuleContext, Token
from antlr4.error.ErrorListener import ErrorListener
from pydantic import BaseModel, ConfigDict

from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._generated.PsithonParser import PsithonParser


class Diagnostic(BaseModel):
    """Describe an ANTLR syntax error.

    Attributes:
        line: One-based source line.
        column: Zero-based source column.
        message: Description from the lexer or parser.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    line: int
    column: int
    message: str


class ParseResult(BaseModel):
    """Expose ANTLR parsing results alongside the exact original source.

    Attributes:
        source: Original input, including comments and physical newline spelling.
        tree: ANTLR concrete syntax tree; recovered input can contain error nodes.
        tokens: Complete validation token stream, including hidden-channel tokens.
        diagnostics: Lexer, parser and grammar-constraint errors.
        source_offsets: Original character offsets for validation-text boundaries.
            Tokens refer to prepared text; use source_span or source_text to access
            their original spelling. Offsets count Python string characters.
    """

    model_config = ConfigDict(frozen=True, strict=True, arbitrary_types_allowed=True)

    source: str
    tree: ParserRuleContext
    tokens: CommonTokenStream
    diagnostics: tuple[Diagnostic, ...]
    source_offsets: tuple[int, ...]

    def source_span(self, node: ParserRuleContext | Token) -> tuple[int, int]:
        """Return an original-source interval with an exclusive end offset.

        Args:
            node: Context or token belonging to this parse result. Context spans
                include interior trivia, but exclude trivia outside their tokens.

        Returns:
            Start and end offsets suitable for slicing source. Synthetic layout
            tokens have empty spans.

        Raises:
            ValueError: A recovered node has no anchored source interval.
        """
        if isinstance(node, ParserRuleContext):
            first, last = node.start, node.stop
        else:
            first = last = node
        if first is None or last is None or first.start < 0:
            raise ValueError("Node has no anchored source interval")
        limit = len(self.source_offsets) - 1
        start = min(first.start, limit)
        stop = max(start, min(last.stop + 1, limit))
        return self.source_offsets[start], self.source_offsets[stop]

    def source_text(self, node: ParserRuleContext | Token) -> str:
        """Return a node's original spelling, including interior comments and spaces.

        Args:
            node: Context or token belonging to this parse result.

        Returns:
            Original source within the node's token interval. The source attribute
            retains the whole file, including leading and trailing trivia.

        Unanchored recovery nodes raise ValueError through source_span.
        """
        start, stop = self.source_span(node)
        return self.source[start:stop]


def parse(source: str) -> ParseResult:
    """Parse and validate Psithon while retaining its original source and CST.

    Args:
        source: Native input text; its Python statements are never executed.

    Returns:
        Original source, ANTLR tree and tokens, source intervals and diagnostics.
        Invalid input retains the recovered tree and complete token stream.
    """
    lexer = PsithonLexer(InputStream(source))
    errors = _Errors()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errors)
    tokens = CommonTokenStream(lexer)
    parser = PsithonParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(errors)
    tree = parser.file_input()
    tokens.fill()
    if lexer.native.kind:
        errors.items.append(
            Diagnostic(
                line=lexer.line,
                column=lexer.column,
                message="Unterminated native directive",
            )
        )
    return ParseResult(
        source=lexer.original_source,
        tree=tree,
        tokens=tokens,
        diagnostics=tuple(errors.items),
        source_offsets=lexer.source_offsets,
    )


def validate(source: str) -> tuple[Diagnostic, ...]:
    """Return ANTLR errors for a native input without executing its Python.

    Args:
        source: Native Psithon input text.

    Returns:
        Lexer and parser errors, or an empty tuple for accepted input.
    """
    return parse(source).diagnostics


class _Errors(ErrorListener):
    def __init__(self) -> None:
        self.items: list[Diagnostic] = []

    @override
    def syntaxError(
        self,
        recognizer: object,
        offendingSymbol: object,
        line: int,
        column: int,
        msg: str,
        e: object,
    ) -> None:
        # ANTLR leaves these three callback values untyped. The adapter needs
        # only the precisely typed source location and message, not their values.
        del recognizer, offendingSymbol, e
        self.items.append(Diagnostic(line=line, column=column, message=msg))
