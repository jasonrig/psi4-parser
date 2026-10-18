"""Connect the upstream Python lexer support to native Psithon modes."""

import sys
from typing import TextIO, override

from antlr4 import InputStream

# noinspection PyProtectedMember
from psi4_parser._vendor.PythonLexerBase import PythonLexerBase
from psi4_parser.native import NativeLexerSupport


class PsithonLexerBase(PythonLexerBase):
    """Preserve Python's lexer behavior while adding native block state."""

    native_input = True

    def __init__(self, stream: InputStream, output: TextIO = sys.stdout) -> None:
        """Initialize Python and native lexical state.

        Args:
            stream: ANTLR source character stream.
            output: Destination for ANTLR runtime messages.
        """
        super().__init__(self.prepare_input(stream), output)
        self.native = NativeLexerSupport(self, enabled=self.native_input)

    def prepare_input(self, stream: InputStream) -> InputStream:
        """Return input normalized by the generated grammar's lexer hook.

        Args:
            stream: Original source character stream.

        Returns:
            Source stream used by Python and native tokenization.
        """
        return stream

    @override
    def reset(self) -> None:
        """Reset both language states when the lexer is reused."""
        super().reset()
        self.native = NativeLexerSupport(self, enabled=self.native_input)
