"""Define JSON-compatible values shared by the native job models."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

_NUMBER_VALUE_EXAMPLES: list[str] = ["0", "1.0", "-0.5", "1.2D-3"]
_VARIABLE_NAME_EXAMPLES: list[str] = ["R", "D"]
_UNITS_NAME_EXAMPLES: list[str] = ["angstrom", "bohr", "a.u."]
_NUCLEUS_LABEL_EXAMPLES: list[str] = ["H", "C1", "13C", "X"]


class Model(BaseModel):
    """Use immutable, strictly typed values for native jobs."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
    )


class Number(Model):
    """Preserve a native number, including Fortran exponents and Unicode digits.

    Attributes:
        value: Numeric spelling interpreted by the relevant Psi4 reader.
    """

    kind: Literal["number"] = Field(
        default="number", description="Discriminator identifying the Number variant."
    )
    value: str = Field(
        description="Numeric spelling interpreted by the relevant Psi4 reader.",
        pattern=r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[dDeE][+-]?\d+)?$",
        examples=_NUMBER_VALUE_EXAMPLES,
    )

    def as_float(self) -> float:
        """Convert the native numeric spelling to a Python float.

        Returns:
            Numeric value with Fortran exponent markers normalized.
        """
        return float(self.value.lower().replace("d", "e"))


class Variable(Model):
    """Reference a geometry variable without evaluating it.

    Attributes:
        name: Variable name as specified in the molecule.
        negative: Whether the reference negates that variable.
    """

    kind: Literal["variable"] = Field(
        default="variable",
        description="Discriminator identifying the Variable variant.",
    )
    name: str = Field(
        description="Variable name as specified in the molecule.",
        min_length=1,
        examples=_VARIABLE_NAME_EXAMPLES,
    )
    negative: bool = Field(
        default=False, description="Whether the reference negates that variable."
    )


type Scalar = Annotated[
    Number | Variable,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Units(Model):
    """Specify native geometry units without silently choosing defaults.

    Attributes:
        name: Native unit spelling, such as angstrom, bohr, or a.u.
    """

    kind: Literal["units"] = Field(
        default="units", description="Discriminator identifying the Units variant."
    )
    name: str = Field(
        description="Native unit spelling, such as angstrom, bohr, or a.u.",
        min_length=1,
        examples=_UNITS_NAME_EXAMPLES,
    )


class FragmentSeparator(Model):
    """Retain a fragment boundary, including a leading overall-state boundary."""

    kind: Literal["fragment_separator"] = Field(
        default="fragment_separator",
        description="Discriminator identifying the FragmentSeparator variant.",
    )


class Nucleus(Model):
    """Describe a native nucleus independently of its position.

    Attributes:
        label: Element, atomic number, isotope prefix, and optional atom label.
        ghost: Original ghost notation, or none for an ordinary nucleus.
        mass: Explicit isotope mass following the nucleus label, if supplied.
    """

    label: str = Field(
        description="Element, atomic number, isotope prefix, and optional atom label.",
        min_length=1,
        examples=_NUCLEUS_LABEL_EXAMPLES,
    )
    ghost: Literal["none", "at", "gh"] = Field(
        default="none",
        description="Original ghost notation, or none for an ordinary nucleus.",
    )
    mass: Number | None = Field(
        default=None,
        description="Explicit isotope mass following the nucleus label, if supplied.",
    )
