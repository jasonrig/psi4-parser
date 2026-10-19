"""Describe modern Psi4 external potentials using immutable physical values."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, RootModel, model_validator

from psi4_parser.builder._model import Length, Model

type MatrixRow = tuple[float, ...]
type MatrixData = tuple[MatrixRow, ...]
type ChargePosition = tuple[Length, Length, Length]


class ExternalPointCharge(Model):
    """Place a point charge at a position with explicit length units."""

    charge: float = Field(description="Charge in elementary-charge units.")
    position: ChargePosition = Field(description="Cartesian x, y, and z lengths.")


class GaussianCharge(Model):
    """Spread a charge over a Gaussian centered at an explicit position."""

    charge: float = Field(description="Integrated charge in elementary-charge units.")
    position: ChargePosition = Field(description="Cartesian x, y, and z lengths.")
    exponent: float = Field(
        gt=0, description="Positive Gaussian exponent in inverse square bohr."
    )


class PotentialMatrix(RootModel[tuple[MatrixRow, ...]]):
    """Retain a finite square AO potential matrix in atomic units.

    The AO ordering and dimension must match the calculation's basis. Those
    runtime properties cannot be checked while constructing an input.
    """

    model_config = ConfigDict(
        frozen=True, strict=True, allow_inf_nan=False, revalidate_instances="always"
    )
    root: MatrixData = Field(
        min_length=1, description="Nonempty square matrix in AO order, in hartree."
    )

    @model_validator(mode="after")
    def _square(self) -> Self:
        if any(len(row) != len(self.root) for row in self.root):
            raise ValueError("Potential matrix must be square")
        return self


class ExternalPotential(Model):
    """Combine point, Gaussian, and AO-matrix contributions to a potential."""

    kind: Literal["external_potential"] = Field(
        default="external_potential", description="Modern external-potential value."
    )
    points: tuple[ExternalPointCharge, ...] = Field(
        default=(), description="External point charges."
    )
    diffuse: tuple[GaussianCharge, ...] = Field(
        default=(), description="Gaussian diffuse charges."
    )
    matrix: PotentialMatrix | None = Field(
        default=None, description="Optional AO potential matrix in atomic units."
    )


class FragmentPotential(Model):
    """Associate a potential with a Psi4 FI-SAPT subsystem."""

    fragment: Literal["A", "B", "C"] = Field(
        description="FI-SAPT monomer A, monomer B, or linker C label."
    )
    potential: ExternalPotential = Field(description="Subsystem external potential.")


class FragmentPotentials(Model):
    """Apply external potentials to explicitly named FI-SAPT subsystems."""

    kind: Literal["fragment_potentials"] = Field(
        default="fragment_potentials", description="FI-SAPT external-potential map."
    )
    fragments: tuple[FragmentPotential, ...] = Field(
        min_length=1, description="Distinct subsystem potentials, in supplied order."
    )

    @model_validator(mode="after")
    def _distinct_fragments(self) -> Self:
        names = [entry.fragment for entry in self.fragments]
        if len(names) != len(set(names)):
            raise ValueError("External-potential subsystem labels must be distinct")
        return self
