"""Expose the complete lowered Python AST and native data omitted by lowering."""

import ast
import warnings

from pydantic import BaseModel, ConfigDict, Field

from psi4_parser._diagnostics import DiagnosticError
from psi4_parser.api import NativePayload, ParseResult, parse


class InvalidInputError(DiagnosticError):
    """Reject AST construction or formatting of an invalid input.

    Attributes:
        diagnostics: The original parser's syntax and static-constraint errors.
    """


class ProgramAST(BaseModel):
    """The Python structure and Psi4-specific data of a complete input."""

    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True
    )
    python: ast.Module = Field(
        description="Python syntax tree representing the complete input."
    )
    native_data: tuple[NativePayload, ...] = Field(
        description="Psi4-specific data retained alongside the Python syntax tree."
    )

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
    with warnings.catch_warnings(record=False, action="ignore", category=SyntaxWarning):
        python = ast.parse(result.python_source, filename="<psithon>")
    return ProgramAST(python=python, native_data=result.native_data)
