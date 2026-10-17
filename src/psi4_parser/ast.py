"""Expose the complete lowered Python AST and native data omitted by lowering."""

import ast
import warnings

from pydantic import BaseModel, ConfigDict

from psi4_parser.api import Diagnostic, NativePayload, ParseResult, parse


class InvalidInputError(ValueError):
    """Reject AST construction or formatting of an invalid input.

    Attributes:
        diagnostics: The original parser's syntax and static-constraint errors.
    """

    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        """Retain diagnostics and describe the first error.

        Args:
            diagnostics: Nonempty diagnostics returned by the parser.
        """
        self.diagnostics = diagnostics
        first = diagnostics[0]
        super().__init__(f"{first.line}:{first.column}: {first.message}")


class ProgramAST(BaseModel):
    """Represent a complete, validated input without executing user code.

    Attributes:
        python: CPython's complete AST of the grammar-owned Psithon lowering.
            Includes literal values, template expression text and evaluation order.
            Treat the standard AST nodes as read-only.
        native_data: Payloads retained by the native preprocessing callbacks,
            including original external bodies. These remain literal data,
            without opening files or invoking solvers.
    """

    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True
    )
    python: ast.Module
    native_data: tuple[NativePayload, ...]

    def equivalent(self, other: ProgramAST) -> bool:
        """Compare represented programs without source-location attributes.

        Compiler-generated basis labels and external-geometry indentation are
        canonicalized during lowering. Original external data is retained.
        All user identifiers and Python literal values remain significant.
        This does not promise identical source introspection or tracebacks.

        Args:
            other: Program to compare with this one.

        Returns:
            Whether Python structure and every retained native payload agree.
        """
        return self.native_data == other.native_data and ast.compare(
            self.python, other.python, compare_attributes=False
        )


def build_ast(source: str | ParseResult) -> ProgramAST:
    """Build a complete program AST after successful ANTLR validation.

    Args:
        source: Native input text or an existing result from parse().

    Returns:
        Lowered Python AST and native information required for equivalence checks.

    Raises:
        InvalidInputError: ANTLR reports invalid syntax or static constraints.
        ValueError: The parse result has no complete Python lowering.
    """
    result = parse(source) if isinstance(source, str) else source
    if result.diagnostics:
        raise InvalidInputError(result.diagnostics)
    if result.python_source is None:
        raise ValueError("Parse result has no complete Python lowering")
    # Lexical warnings do not make already-validated input invalid. Do not emit
    # duplicate compiler warnings while a formatter constructs comparison trees.
    with warnings.catch_warnings(action="ignore", category=SyntaxWarning):
        python = ast.parse(result.python_source, filename="<psithon>")
    return ProgramAST(python=python, native_data=result.native_data)
