"""Keep native block lexing separate from Python indentation and string modes."""

import re

from antlr4 import Lexer

_BLOCK_HEADER = re.compile(r"\s*[-,\w]*?[\s=]*\{", re.IGNORECASE)
_BASIS_HEADER = re.compile(
    r"(?:basis_relativistic|df_basis_(?:scf|mp2|cc|sapt|sad|dct)|basis)"
    r"[=\s]*\w*?\s*\{",
    re.IGNORECASE,
)


class NativeLexerSupport:
    """Track Psithon lexical boundaries for an ANTLR lexer.

    Attributes:
        kind: Active native directive, or an empty string outside a directive.
    """

    def __init__(self, lexer: Lexer, *, enabled: bool = True) -> None:
        """Attach lexical state to one lexer instance.

        Args:
            lexer: Generated lexer receiving mode and token-type changes.
            enabled: Whether the source still contains native directives.
        """
        self._lexer = lexer
        self._enabled = enabled
        self._source = lexer.inputStream.getText(0, lexer.inputStream.size - 1)
        self.kind = ""
        self._arrays = 0
        self._inline = False
        self._start = 0

    def is_directive(self) -> bool:
        """Return whether a native header starts at the current position."""
        return any(
            self.is_start(kind)
            for kind in ("molecule", "set", "basis", "external", "pcm", "cfour")
        )

    def is_start(self, kind: str) -> bool:
        """Identify a directive without reserving ordinary Python identifiers.

        Args:
            kind: Directive family to recognize.

        Returns:
            Whether the current position starts this native directive.
        """
        if not self._enabled:
            return False
        offset = self._lexer.getCharIndex()
        prefix = self._source[offset - self._lexer.column : offset]
        if prefix.strip(" \t\f"):
            return False
        tail = self._source[offset:]
        if kind == "basis":
            return _BASIS_HEADER.match(tail) is not None
        if tail[: len(kind)].casefold() != kind:
            return False
        suffix = tail[len(kind) :]
        if kind == "set":
            return bool(
                _BLOCK_HEADER.match(suffix)
                or re.match(r"\s+[-,\w]+[\s=]+[^=\s]", suffix)
            )
        return bool(re.match(r"[=\s]*[^\s{}]*\s*\{", suffix))

    def begin(self, kind: str) -> None:
        """Enter a directive and determine whether its newline ends the mode.

        Args:
            kind: Recognized directive family.
        """
        self.kind = kind
        self._arrays = 0
        suffix = self._source[self._lexer.getCharIndex() :]
        self._start = self._lexer.getCharIndex()
        self._inline = kind == "set" and _BLOCK_HEADER.match(suffix) is None

    def open_brace(self, cfour_mode: int) -> None:
        """Preserve literal CFOUR text after its opening brace.

        Args:
            cfour_mode: Generated lexer's literal CFOUR mode number.
        """
        if self.kind == "cfour":
            self._lexer.mode(cfour_mode)

    def close_brace(self) -> None:
        """Leave a block at the closing boundary used by Psi4."""
        if self._inline and self._arrays > 0:
            return
        if self.kind == "pcm" and self._lexer.column != 1:
            return
        self._finish()

    def open_array(self) -> None:
        """Keep multiline option arrays inside the native mode."""
        self._arrays += 1

    def close_array(self) -> None:
        """Finish one nested option array."""
        self._arrays -= 1

    def newline(self, python_newline_type: int) -> None:
        """Resume Python indentation after an inline directive.

        Args:
            python_newline_type: Generated lexer's Python NEWLINE token number.
        """
        if self._inline and self._arrays == 0:
            # The regex permits blank lines between 'set' and its first field.
            if not self._source[self._start : self._lexer.getCharIndex()].strip():
                return
            self._lexer.type = python_newline_type
            self._finish()

    def _finish(self) -> None:
        self.kind = ""
        self._lexer.popMode()
