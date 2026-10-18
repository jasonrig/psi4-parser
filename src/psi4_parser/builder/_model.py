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
    """Carry a finite distance with an explicit length unit."""

    kind: Literal["length"] = Field(default="length", description="Length quantity.")
    value: float = Field(description="Finite signed length.")
    unit: Literal["angstrom", "bohr"] = Field(description="Unit of length.")

    @property
    def angstroms(self) -> float:
        """Return the distance in angstroms using Psi4's CODATA conversion."""
        return self.value if self.unit == "angstrom" else self.value * BOHR_ANGSTROM


class Angle(Model):
    """Carry a finite angle with an explicit angular unit."""

    kind: Literal["angle"] = Field(default="angle", description="Angular quantity.")
    value: float = Field(description="Finite signed angle.")
    unit: Literal["degrees", "radians"] = Field(description="Unit of angle.")

    @property
    def degrees(self) -> float:
        """Return an angle in degrees."""
        return self.value if self.unit == "degrees" else to_degrees(self.value)


# Psi4's qcelemental physical constants express one bohr in angstroms.
BOHR_ANGSTROM = 0.52917721067


def angstrom(value: float) -> Length:
    """Return a distance in angstroms."""
    return Length(value=value, unit="angstrom")


def bohr(value: float) -> Length:
    """Return a distance in bohr."""
    return Length(value=value, unit="bohr")


def degrees(value: float) -> Angle:
    """Return an angle in degrees."""
    return Angle(value=value, unit="degrees")


def radians(value: float) -> Angle:
    """Return an angle in radians."""
    return Angle(value=value, unit="radians")
