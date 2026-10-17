"""Provide a thin entry point for the generated ANTLR parser."""

from typing import override

from antlr4 import CommonTokenStream, InputStream
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


def validate(source: str) -> tuple[Diagnostic, ...]:
    """Return ANTLR errors for a native input without executing its Python.

    Args:
        source: Native Psithon input text.

    Returns:
        Lexer and parser errors, or an empty tuple for accepted input.
    """
    terminated = source if source.endswith("\n") else source + "\n"
    lexer = PsithonLexer(InputStream(terminated))
    errors = _Errors()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errors)
    parser = PsithonParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(errors)
    parser.file_input()
    if lexer.native.kind:
        errors.items.append(
            Diagnostic(
                line=lexer.line,
                column=lexer.column,
                message="Unterminated native directive",
            )
        )
    return tuple(errors.items)


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
