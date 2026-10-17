"""Public interface used from the generated lexer."""

from typing import ClassVar

from psi4_parser.lexer_base import PsithonLexerBase

class PsithonLexer(PsithonLexerBase):
    symbolicNames: ClassVar[list[str]]
    original_source: str
    source_offsets: tuple[int, ...]
