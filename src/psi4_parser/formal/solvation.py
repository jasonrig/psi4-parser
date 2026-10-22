"""Describe equilibrium PCMSolver media and cavities as scientific inputs."""

import re
from typing import Literal, Self

from pydantic import Field, model_validator

from psi4_parser.formal._record import Record


class PCMSolverSolvation(Record):
    """Choose equilibrium IEFPCM or CPCM with an implicit GePol cavity.

    Lengths and areas in the solver block use bohr independently of the molecule's
    coordinate units. An explicit dielectric also requires a solvent probe radius;
    omitting both requests the named solvent's native table values.
    """

    solver: Literal["iefpcm", "cpcm"] = Field(
        default="iefpcm", description="Boundary-element continuum equation."
    )
    dielectric_constant: float | None = Field(
        default=None,
        ge=1,
        description="Static relative permittivity; null uses the named solvent table.",
    )
    probe_radius_bohr: float | None = Field(
        default=None,
        ge=0.1,
        le=100,
        description="Solvent probe radius in bohr, required with explicit dielectric.",
    )
    radii_set: Literal["uff", "bondi", "allinger"] = Field(
        default="uff", description="Native atom-centered cavity radius table."
    )
    scale_radii: bool = Field(
        default=False, description="Whether to multiply tabulated atomic radii by 1.2."
    )
    surface_area_bohr2: float = Field(
        default=0.3,
        ge=0.01,
        description="Average GePol surface element area in square bohr.",
    )
    cpcm_correction: float = Field(
        default=0,
        ge=0,
        description="CPCM denominator correction k; must be zero for IEFPCM.",
    )
    diagonal_scaling: float = Field(
        default=1.07,
        gt=0,
        description="Scaling for the diagonal collocation matrix elements.",
    )
    scf_type: Literal["total", "separate"] = Field(
        default="total",
        description="Treat nuclear/electronic polarization together or separately.",
    )

    @model_validator(mode="after")
    def check_medium(self) -> Self:
        """Return medium choices that will all affect the requested construction.

        Raises:
            ValueError: Dielectric/probe choices are incomplete or IEFPCM has a
                nonzero CPCM correction.
        """
        if (self.dielectric_constant is None) != (self.probe_radius_bohr is None):
            raise ValueError(
                "Supply dielectric_constant and probe_radius_bohr together"
            )
        if self.solver != "cpcm" and self.cpcm_correction != 0:
            raise ValueError("cpcm_correction applies only to the CPCM solver")
        return self

    def input_text(self, solvent: str) -> str:
        """Return a complete equilibrium solver block in atomic units.

        Args:
            solvent: Native table name, or a descriptive label for explicit media.

        Returns:
            Configuration for Psi4's PCM__INPUT option, without an outer pcm block.

        Raises:
            ValueError: A table name contains solver syntax or requests Explicit
                without supplying dielectric and probe choices.
        """
        explicit = self.dielectric_constant is not None
        if not explicit and (
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._,+\-]*", solvent) is None
            or solvent.strip().casefold() == "explicit"
        ):
            raise ValueError(
                "Use a plain solvent name or explicit dielectric/probe fields"
            )
        medium = [
            f"  SolverType = {self.solver.upper()}",
            f"  Solvent = {'Explicit' if explicit else solvent.strip()}",
            "  Nonequilibrium = False",
            "  DiagonalIntegrator = Collocation",
            f"  DiagonalScaling = {self.diagonal_scaling}",
        ]
        if self.solver == "cpcm":
            medium.append(f"  Correction = {self.cpcm_correction}")
        else:
            medium.append("  MatrixSymm = True")
        if explicit:
            medium.extend(
                (
                    f"  ProbeRadius = {self.probe_radius_bohr}",
                    "  Green<inside> { Type = Vacuum }",
                    "  Green<outside> {",
                    "    Type = UniformDielectric",
                    f"    Eps = {self.dielectric_constant}",
                    "  }",
                )
            )
        return "\n".join(
            (
                "Units = AU",
                "Medium {",
                *medium,
                "}",
                "Cavity {",
                "  Type = GePol",
                "  Mode = Implicit",
                f"  RadiiSet = {self.radii_set.upper()}",
                f"  Scaling = {self.scale_radii}",
                f"  Area = {self.surface_area_bohr2}",
                "}",
                "",
            )
        )
