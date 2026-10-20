"""Distinguish Python literals, references, expressions, and immutable containers."""

from typing import Annotated, Literal

from pydantic import Field

from psi4_parser.builder._model import Model
from psi4_parser.builder.potentials import ExternalPotential, FragmentPotentials

type AssignmentTarget = str | tuple[str, ...]
type Assignment = AssignmentTarget | None


class Reference(Model):
    """Use a value assigned by an earlier job step."""

    kind: Literal["reference"] = Field(
        default="reference",
        description="Selects a reference to an earlier named value.",
    )
    name: str = Field(
        min_length=1,
        description=(
            "Name assigned by an earlier step on every possible execution path."
        ),
    )


class Expression(Model):
    """A Python expression that supplies a value when the input runs."""

    kind: Literal["expression"] = Field(
        default="expression", description="Selects a Python expression."
    )
    source: str = Field(
        min_length=1,
        description="Python expression to include, such as e_scf + correction.",
    )


class LiteralValue(Model):
    """A string, number, boolean, or null passed as a value."""

    kind: Literal["literal"] = Field(
        default="literal",
        description="Selects a string, number, boolean, or null value.",
    )
    value: str | bool | int | float | None = Field(
        description="Value to pass directly; strings are treated as text."
    )


class SequenceValue(Model):
    """A Python list or tuple containing values in order."""

    kind: Literal["sequence"] = Field(
        default="sequence", description="Selects a list or tuple of values."
    )
    items: tuple[Value, ...] = Field(default=(), description="Values in list order.")
    style: Literal["list", "tuple"] = Field(
        default="list", description="Python container to create: list or tuple."
    )


class MappingEntry(Model):
    """One dictionary key and its associated value."""

    key: Value = Field(description="Dictionary key, usually a literal string.")
    value: Value = Field(description="Value associated with this key.")


class MappingValue(Model):
    """A Python dictionary built from ordered key-value pairs."""

    kind: Literal["mapping"] = Field(
        default="mapping", description="Selects a dictionary of key-value pairs."
    )
    entries: tuple[MappingEntry, ...] = Field(
        default=(), description="Dictionary entries in insertion order."
    )


type Value = Annotated[
    LiteralValue
    | Reference
    | Expression
    | SequenceValue
    | MappingValue
    | ExternalPotential
    | FragmentPotentials,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "A literal, earlier named value, Python expression, collection, "
            "or external potential."
        ),
    ),
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
    | ExternalPotential
    | FragmentPotentials
    | tuple[InputValue, ...]
    | list[InputValue]
    | dict[str, InputValue]
    | None
)


def value(item: InputValue) -> Value:
    """Convert Python argument values into reusable job values.

    Strings become literal text, lists and tuples retain their container type,
    and dictionaries retain insertion order. Reference and Expression specify
    values to look up or evaluate when the generated input runs.

    Returns:
        A serializable value accepted by calculation and call components.
    """
    if isinstance(
        item,
        (
            LiteralValue,
            Reference,
            Expression,
            SequenceValue,
            MappingValue,
            ExternalPotential,
            FragmentPotentials,
        ),
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
    """Return assigned result names in order.

    A single name becomes a one-element tuple; None gives an empty tuple.
    """
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
