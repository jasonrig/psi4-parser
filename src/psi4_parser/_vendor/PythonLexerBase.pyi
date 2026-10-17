"""Typed boundary for the vendored upstream ANTLR lexer support."""

from typing import TextIO
from antlr4 import InputStream, Lexer

class PythonLexerBase(Lexer):
    def __init__(self, input: InputStream, output: TextIO = ...) -> None: ...
