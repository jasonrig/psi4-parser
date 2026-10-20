"""Share immutable validation and dimensioned quantities across builder models."""

from math import degrees as to_degrees
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    """Reject unknown fields and retain immutable, finite domain values."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
        allow_inf_nan=False,
        revalidate_instances="always",
    )


def evolve[T: Model](original: T, **changes: object) -> T:
    """Return a validated copy with selected model fields replaced.

    Field values are heterogeneous and are checked by the concrete model.
    """
    return type(original).model_validate(original.model_copy(update=changes))


class Length(Model):
    """A distance expressed in angstroms or bohr."""

    kind: Literal["length"] = Field(
        default="length", description="Selects a length with explicit units."
    )
    value: float = Field(description="Signed distance in the chosen unit.")
    unit: Literal["angstrom", "bohr"] = Field(description="Unit used for the distance.")

    @property
    def angstroms(self) -> float:
        """Return the distance in angstroms, using Psi4's conversion factor."""
        return self.value if self.unit == "angstrom" else self.value * BOHR_ANGSTROM


class Angle(Model):
    """An angle expressed in degrees or radians."""

    kind: Literal["angle"] = Field(
        default="angle", description="Selects an angle with explicit units."
    )
    value: float = Field(description="Signed angle in the chosen unit.")
    unit: Literal["degrees", "radians"] = Field(description="Unit used for the angle.")

    @property
    def degrees(self) -> float:
        """Return this angle converted to degrees."""
        return self.value if self.unit == "degrees" else to_degrees(self.value)


# Psi4's qcelemental physical constants express one bohr in angstroms.
BOHR_ANGSTROM = 0.52917721067


def angstrom(value: float) -> Length:
    """Express a finite signed distance or displacement in angstroms.

    Returns:
        A length value, for example ``angstrom(0.74)`` for a bond length.
    """
    return Length(value=value, unit="angstrom")


def bohr(value: float) -> Length:
    """Express a finite signed distance or displacement in bohr.

    Returns:
        A length value, for example ``bohr(1.4)``; 1 bohr is about 0.529 angstrom.
    """
    return Length(value=value, unit="bohr")


def degrees(value: float) -> Angle:
    """Express a finite signed angle in degrees.

    Returns:
        An angle value, for example ``degrees(90)`` for a torsion edit.
    """
    return Angle(value=value, unit="degrees")


def radians(value: float) -> Angle:
    """Express a finite signed angle in radians.

    Returns:
        An angle value, for example ``radians(math.pi / 2)`` for a quarter turn.
    """
    return Angle(value=value, unit="radians")
