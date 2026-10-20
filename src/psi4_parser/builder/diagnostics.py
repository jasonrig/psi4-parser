"""Identify fields and emitted locations that fail job compilation."""

from collections.abc import Iterator
from contextlib import contextmanager

from pydantic import Field

from psi4_parser.builder._model import Model, evolve

type ComponentPath = tuple[str | int, ...]


class CompilationDiagnostic(Model):
    """An input error and the field or source position that caused it."""

    path: ComponentPath = Field(
        description=(
            "Field names and list indices locating the error; indices start at zero."
        )
    )
    message: str = Field(description="What is wrong with the input.")
    line: int | None = Field(
        default=None,
        ge=1,
        description="Line of generated input containing the error, counting from 1.",
    )
    column: int | None = Field(
        default=None,
        ge=0,
        description="Column of generated input containing the error, counting from 0.",
    )

    @property
    def location(self) -> str:
        """Return a readable field path such as components[2].method."""
        result = ""
        for part in self.path:
            if isinstance(part, int):
                result += f"[{part}]"
            else:
                result += ("." if result else "") + part
        return result or "job"


class CompilationError(ValueError):
    """Retain structured diagnostics for a job that cannot be compiled.

    Attributes:
        diagnostics: Nonempty tuple of field-aware compilation diagnostics.
    """

    def __init__(self, diagnostics: tuple[CompilationDiagnostic, ...]) -> None:
        """Retain all diagnostics and describe the first failure."""
        self.diagnostics = diagnostics
        first = diagnostics[0]
        super().__init__(first.location + ": " + first.message)


@contextmanager
def compilation_context(*path: str | int) -> Iterator[None]:
    """Add a relative field path to validation errors raised in this context.

    Raises:
        CompilationError: A nested field, expression, or component is invalid.
    """
    try:
        yield
    except CompilationError as error:
        raise CompilationError(
            tuple(
                evolve(diagnostic, path=(*path, *diagnostic.path))
                for diagnostic in error.diagnostics
            )
        ) from error
    except SyntaxError as error:
        raise CompilationError(
            (CompilationDiagnostic(path=path, message=error.msg),)
        ) from error
    except ValueError as error:
        raise CompilationError(
            (CompilationDiagnostic(path=path, message=str(error)),)
        ) from error
