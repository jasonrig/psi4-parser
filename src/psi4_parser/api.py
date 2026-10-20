"""Provide a thin entry point for the generated ANTLR parser."""

from typing import Literal, override

from antlr4 import CommonTokenStream, InputStream, ParserRuleContext, Token
from antlr4.error.ErrorListener import ErrorListener
from pydantic import BaseModel, ConfigDict, Field

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonLexer import PsithonLexer

# noinspection PyProtectedMember
from psi4_parser._generated.PsithonParser import PsithonParser

# Half-open character offsets into the original input source.
type SourceSpan = tuple[int, int]


class Diagnostic(BaseModel):
    """A syntax error and its location in the input."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    line: int = Field(description="Line containing the error, counting from 1.")
    column: int = Field(description="Column containing the error, counting from 0.")
    message: str = Field(description="What is wrong with the input syntax.")


class NativePayload(BaseModel):
    """Psi4-specific data retained alongside the Python input text."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    kind: Literal["pcm", "from_file", "anonymous_basis", "external"] = Field(
        description=(
            "Type of retained Psi4 data: solvent, file geometry, basis "
            "marker, or external potential."
        )
    )
    text: str = Field(description="Psi4 data text associated with this item.")


class ParseResult(BaseModel):
    """Original input, parsed structure, and any syntax errors."""

    model_config = ConfigDict(frozen=True, strict=True, arbitrary_types_allowed=True)

    source: str = Field(
        description="Original input text, including comments and line endings."
    )
    tree: ParserRuleContext = Field(
        description="Syntax tree produced by the input parser."
    )
    tokens: CommonTokenStream = Field(
        description="Input tokens, including spaces and comments."
    )
    diagnostics: tuple[Diagnostic, ...] = Field(
        description="Syntax errors found in the input."
    )
    source_offsets: tuple[int, ...] = Field(
        description=(
            "Original character positions corresponding to the parser's prepared text."
        )
    )
    python_source: str | None = Field(
        default=None,
        description=(
            "Equivalent Python input text produced by the parser, when available."
        ),
    )
    native_data: tuple[NativePayload, ...] = Field(
        default=(),
        description="Psi4-specific data retained alongside the Python input text.",
    )
    input_span: SourceSpan | None = Field(
        default=None,
        description=(
            "Start and end character positions of the job within the original text."
        ),
    )

    def source_span(self, node: ParserRuleContext | Token) -> SourceSpan:
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
        python_source=parser.python_source,
        input_span=lexer.input_span,
        native_data=tuple(
            NativePayload(kind=kind, text=text) for kind, text in parser.native_payloads
        ),
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

    # noinspection PyPep8Naming
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
