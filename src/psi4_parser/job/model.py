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
    """A number in Psi4 input notation."""

    kind: Literal["number"] = Field(
        default="number", description="Selects a number written as text."
    )
    value: str = Field(
        description="Number as input text, such as 0.74 or 1.2D-3.",
        pattern=r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[dDeE][+-]?\d+)?$",
        examples=_NUMBER_VALUE_EXAMPLES,
    )

    def as_float(self) -> float:
        """Return this number as a Python float, accepting Psi4's D exponents.

        For example, ``Number(value="1.2D-3").as_float()`` returns 0.0012.
        """
        return float(self.value.lower().replace("d", "e"))


class Variable(Model):
    """Use a named distance or angle from the molecule."""

    kind: Literal["variable"] = Field(
        default="variable",
        description="Selects a named geometry value.",
    )
    name: str = Field(
        description="Name of the distance or angle variable used in the molecule.",
        min_length=1,
        examples=_VARIABLE_NAME_EXAMPLES,
    )
    negative: bool = Field(
        default=False, description="Use the negative of this variable's value."
    )


type Scalar = Annotated[
    Number | Variable,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="A number written as text or a named geometry value.",
    ),
]


class Units(Model):
    """The length unit for molecular coordinates."""

    kind: Literal["units"] = Field(
        default="units", description="Selects the molecule's length unit."
    )
    name: str = Field(
        description="Length-unit name, such as angstrom, bohr, or a.u.",
        min_length=1,
        examples=_UNITS_NAME_EXAMPLES,
    )


class FragmentSeparator(Model):
    """A boundary between molecular fragments."""

    kind: Literal["fragment_separator"] = Field(
        default="fragment_separator",
        description=(
            "Starts a new fragment after any overall charge and spin settings."
        ),
    )


class Nucleus(Model):
    """An element label with optional isotope or ghost-center settings."""

    label: str = Field(
        description=(
            "Element or atom label, such as H, O1, 13C, or X for a dummy atom."
        ),
        min_length=1,
        examples=_NUCLEUS_LABEL_EXAMPLES,
    )
    ghost: Literal["none", "at", "gh"] = Field(
        default="none",
        description=(
            "none selects a real atom; at and gh select basis-only ghost centers."
        ),
    )
    mass: Number | None = Field(
        default=None,
        description="Optional isotope mass in atomic mass units.",
    )
