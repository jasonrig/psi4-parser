"""Share diagnostic retention and message spelling across input errors."""

from psi4_parser.api import Diagnostic


class DiagnosticError(ValueError):
    """Retain parser diagnostics and describe the first reported error.

    Attributes:
        diagnostics: Complete, nonempty tuple of parser diagnostics.
    """

    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        """Retain diagnostics without copying or discarding later errors."""
        self.diagnostics: tuple[Diagnostic, ...] = diagnostics
        first = diagnostics[0]
        super().__init__(f"{first.line}:{first.column}: {first.message}")
