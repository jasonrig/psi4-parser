"""Distinguish Python literals, references, expressions, and immutable containers."""

from typing import Annotated, Literal

from pydantic import Field

from psi4_parser.builder._model import Model

type Assignment = str | tuple[str, ...] | None


class Reference(Model):
    """Reference a preceding explicit Python binding."""

    kind: Literal["reference"] = Field(
        default="reference", description="Structured binding reference."
    )
    name: str = Field(
        min_length=1, description="Previously declared Python identifier."
    )


class Expression(Model):
    """Retain an explicit Python expression for contextual validation."""

    kind: Literal["expression"] = Field(
        default="expression", description="Python expression."
    )
    source: str = Field(min_length=1, description="Python expression source.")


class LiteralValue(Model):
    """Represent a literal without interpreting strings as Python code."""

    kind: Literal["literal"] = Field(default="literal", description="Python literal.")
    value: str | bool | int | float | None = Field(description="Literal scalar value.")


class SequenceValue(Model):
    """Retain an immutable Python list or tuple expression."""

    kind: Literal["sequence"] = Field(
        default="sequence", description="Python sequence."
    )
    items: tuple[Value, ...] = Field(default=(), description="Ordered sequence values.")
    style: Literal["list", "tuple"] = Field(
        default="list", description="Emitted Python sequence type."
    )


class MappingEntry(Model):
    """Associate a Python mapping key with its value."""

    key: Value = Field(description="Mapping key expression.")
    value: Value = Field(description="Mapping value expression.")


class MappingValue(Model):
    """Retain ordered entries in a Python dictionary expression."""

    kind: Literal["mapping"] = Field(
        default="mapping", description="Python dictionary."
    )
    entries: tuple[MappingEntry, ...] = Field(
        default=(), description="Ordered mapping entries."
    )


type Value = Annotated[
    LiteralValue | Reference | Expression | SequenceValue | MappingValue,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]
type InputValue = (
    str
    | bool
    | int
    | float
    | Reference
    | Expression
    | SequenceValue
    | MappingValue
    | LiteralValue
    | tuple[InputValue, ...]
    | list[InputValue]
    | dict[str, InputValue]
    | None
)


def value(item: InputValue) -> Value:
    """Return immutable expression models for convenient Python values."""
    if isinstance(
        item, (LiteralValue, Reference, Expression, SequenceValue, MappingValue)
    ):
        return item
    if isinstance(item, (tuple, list)):
        return SequenceValue(
            items=tuple(value(v) for v in item),
            style="tuple" if isinstance(item, tuple) else "list",
        )
    if isinstance(item, dict):
        return MappingValue(
            entries=tuple(
                MappingEntry(key=LiteralValue(value=k), value=value(v))
                for k, v in item.items()
            )
        )
    return LiteralValue(value=item)


def assignment_names(assignment: Assignment) -> tuple[str, ...]:
    """Return the declared binding names while preserving their order."""
    if assignment is None:
        return ()
    return (assignment,) if isinstance(assignment, str) else assignment


def assignment_reference(assignment: Assignment) -> Reference:
    """Return a reference to an ordinary single-name assignment.

    Raises:
        ValueError: The assignment is absent or uses tuple unpacking.
    """
    if not isinstance(assignment, str):
        raise ValueError("A single named assignment is required for .ref")
    return Reference(name=assignment)
