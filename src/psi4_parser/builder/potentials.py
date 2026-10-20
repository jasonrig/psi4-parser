"""Describe modern Psi4 external potentials using immutable physical values."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, RootModel, model_validator

from psi4_parser.builder._model import Length, Model

type MatrixRow = tuple[float, ...]
type MatrixData = tuple[MatrixRow, ...]
type ChargePosition = tuple[Length, Length, Length]


class ExternalPointCharge(Model):
    """A signed point charge at a specified position."""

    charge: float = Field(description="Signed point charge in elementary-charge units.")
    position: ChargePosition = Field(
        description="Charge x, y, and z positions, each with explicit length units."
    )


class GaussianCharge(Model):
    """A signed charge spread over a Gaussian distribution."""

    charge: float = Field(
        description=(
            "Total signed charge spread over the Gaussian, in elementary charge units."
        )
    )
    position: ChargePosition = Field(
        description=(
            "Gaussian center x, y, and z positions, each with explicit length units."
        )
    )
    exponent: float = Field(
        gt=0,
        description=(
            "Positive Gaussian exponent in inverse square bohr; larger values "
            "give narrower charges."
        ),
    )


class PotentialMatrix(RootModel[tuple[MatrixRow, ...]]):
    """An external potential matrix matching the calculation's basis functions."""

    model_config = ConfigDict(
        frozen=True, strict=True, allow_inf_nan=False, revalidate_instances="always"
    )
    root: MatrixData = Field(
        min_length=1,
        description=(
            "Square matrix in hartree, with one row and column per atomic "
            "basis function in Psi4's order."
        ),
    )

    @model_validator(mode="after")
    def _square(self) -> Self:
        if any(len(row) != len(self.root) for row in self.root):
            raise ValueError("Potential matrix must be square")
        return self


class ExternalPotential(Model):
    """Point charges, Gaussian charges, and a potential matrix for a calculation."""

    kind: Literal["external_potential"] = Field(
        default="external_potential",
        description=(
            "Selects external point, Gaussian, or matrix potentials for a calculation."
        ),
    )
    points: tuple[ExternalPointCharge, ...] = Field(
        default=(), description="External point charges and their positions."
    )
    diffuse: tuple[GaussianCharge, ...] = Field(
        default=(),
        description="External Gaussian charges, their centers, and their exponents.",
    )
    matrix: PotentialMatrix | None = Field(
        default=None,
        description=(
            "Potential matrix in hartree, in the calculation's atomic basis order."
        ),
    )


class FragmentPotential(Model):
    """An external potential assigned to one FI-SAPT fragment."""

    fragment: Literal["A", "B", "C"] = Field(
        description="FI-SAPT fragment A or B, or connecting fragment C."
    )
    potential: ExternalPotential = Field(
        description="External potential assigned to this fragment."
    )


class FragmentPotentials(Model):
    """External potentials assigned separately to FI-SAPT fragments."""

    kind: Literal["fragment_potentials"] = Field(
        default="fragment_potentials",
        description="Selects separate external potentials for FI-SAPT fragments.",
    )
    fragments: tuple[FragmentPotential, ...] = Field(
        min_length=1,
        description=(
            "Fragment potentials in order, with each of A, B, and C used at most once."
        ),
    )

    @model_validator(mode="after")
    def _distinct_fragments(self) -> Self:
        names = [entry.fragment for entry in self.fragments]
        if len(names) != len(set(names)):
            raise ValueError("External-potential subsystem labels must be distinct")
        return self
