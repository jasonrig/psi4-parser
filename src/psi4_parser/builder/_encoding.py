"""Encode Python arguments for the Psi4 input preprocessor."""

import ast
import keyword
from typing import assert_never

from psi4_parser.builder import components as c
from psi4_parser.builder._model import BOHR_ANGSTROM
from psi4_parser.builder.diagnostics import compilation_context
from psi4_parser.builder.potentials import (
    ExternalPointCharge,
    ExternalPotential,
    FragmentPotentials,
)
from psi4_parser.builder.values import (
    Assignment,
    Expression,
    InputValue,
    LiteralValue,
    MappingEntry,
    MappingValue,
    Reference,
    SequenceValue,
    Value,
    assignment_names,
    value,
)

# This namespace belongs to generated helper variables, never user bindings.
GENERATED_PREFIX = "_psi4_builder_"


def name(identifier: str) -> str:
    """Return a valid, non-reserved Python identifier.

    Raises:
        ValueError: The identifier is invalid or reserved.
    """
    if (
        not identifier.isidentifier()
        or keyword.iskeyword(identifier)
        or identifier.startswith(GENERATED_PREFIX)
    ):
        raise ValueError("Invalid or reserved Python binding: " + identifier)
    return identifier


def expression(source: str) -> str:
    """Return a syntactically valid Python expression."""
    ast.parse(source, mode="eval")
    return source


def literal(item: str | bool | int | float | None) -> str:
    """Return a literal encoded safely across Psi4 preprocessor substitutions."""
    return repr(item).replace("#", r"\x23").replace("psi", r"\x70si")


def encode_value(item: Value, bindings: set[str]) -> str:
    """Return Python source for a value after checking its binding references.

    Raises:
        ValueError: A reference has no preceding declaration.
    """
    if isinstance(item, (ExternalPotential, FragmentPotentials)):
        item = _potential_value(item)
    match item:
        case LiteralValue():
            return literal(item.value)
        case Reference():
            name(item.name)
            if item.name not in bindings:
                raise ValueError("Reference must follow its declaration: " + item.name)
            return item.name
        case Expression():
            return "(" + expression(item.source) + ")"
        case SequenceValue():
            return _sequence_value(item, bindings)
        case MappingValue():
            return _mapping_value(item, bindings)
        case _:
            assert_never(item)


def _sequence_value(item: SequenceValue, bindings: set[str]) -> str:
    values: list[str] = []
    for index, entry in enumerate(item.items):
        with compilation_context("items", index):
            values.append(encode_value(entry, bindings))
    content = ", ".join(values)
    if item.style == "list":
        return "[" + content + "]"
    return "(" + content + ("," if len(item.items) == 1 else "") + ")"


def _mapping_value(item: MappingValue, bindings: set[str]) -> str:
    entries: list[str] = []
    for index, entry in enumerate(item.entries):
        with compilation_context("entries", index):
            with compilation_context("key"):
                key = encode_value(entry.key, bindings)
            with compilation_context("value"):
                content = encode_value(entry.value, bindings)
            entries.append(key + ": " + content)
    return "{" + ", ".join(entries) + "}"


def _potential_value(item: ExternalPotential | FragmentPotentials) -> MappingValue:
    if isinstance(item, FragmentPotentials):
        return MappingValue(
            entries=tuple(
                MappingEntry(
                    key=LiteralValue(value=entry.fragment),
                    value=_fragment_potential(entry.potential),
                )
                for entry in item.fragments
            )
        )
    payload: dict[str, InputValue] = {}
    if item.points:
        payload["points"] = _point_rows(item.points)
    if item.diffuse:
        payload["diffuse"] = [
            [
                point.charge,
                *(
                    coordinate.angstroms / BOHR_ANGSTROM
                    for coordinate in point.position
                ),
                point.exponent,
            ]
            for point in item.diffuse
        ]
    if item.matrix is not None:
        payload["matrix"] = [list(row) for row in item.matrix.root]
    return MappingValue(
        entries=tuple(
            MappingEntry(key=LiteralValue(value=key), value=value(item))
            for key, item in payload.items()
        )
    )


def _point_rows(points: tuple[ExternalPointCharge, ...]) -> list[InputValue]:
    return [
        [
            point.charge,
            *(coordinate.angstroms / BOHR_ANGSTROM for coordinate in point.position),
        ]
        for point in points
    ]


def _fragment_potential(item: ExternalPotential) -> Value:
    # FI-SAPT's field-file exporter accepts point lists, but not mode dictionaries.
    if item.points and not item.diffuse and item.matrix is None:
        return value(_point_rows(item.points))
    return _potential_value(item)


def keywords(arguments: tuple[c.Keyword, ...], bindings: set[str]) -> list[str]:
    """Return distinct call keywords encoded with individual field paths.

    Raises:
        ValueError: A keyword name or argument value is invalid.
    """
    names: set[str] = set()
    result: list[str] = []
    for index, argument in enumerate(arguments):
        with compilation_context("kwargs", index):
            with compilation_context("name"):
                keyword_name = name(argument.name)
                if keyword_name in names:
                    raise ValueError("Duplicate call keyword argument: " + keyword_name)
            with compilation_context("value"):
                argument_value = encode_value(argument.value, bindings)
            names.add(keyword_name)
            result.append(keyword_name + "=" + argument_value)
    return result


def assignment(assign: Assignment) -> str:
    """Return a named assignment or nonempty tuple-unpacking target.

    Raises:
        ValueError: The target is empty or contains duplicate names.
    """
    if assign is None:
        return ""
    names = assignment_names(assign)
    if not names or len(set(names)) != len(names):
        raise ValueError("Assignment requires distinct binding names")
    return (
        ", ".join(name(n) for n in names)
        + ("," if len(names) == 1 and isinstance(assign, tuple) else "")
        + " = "
    )
