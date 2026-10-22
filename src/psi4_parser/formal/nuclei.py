"""Resolve nuclear labels, isotope choices, and real or basis-only centers."""

from typing import Literal

from openbabel import openbabel as ob
from pydantic import Field

from psi4_parser.builder import Molecule
from psi4_parser.builder.openbabel import to_obmol
from psi4_parser.formal._record import Record


class Center(Record):
    """Identify a real nucleus, ghost basis center, or coordinate-only dummy."""

    id: str = Field(description="Stable atom identity from the molecular input.")
    element: str = Field(description="Element symbol; X denotes a dummy center.")
    atomic_number: int = Field(
        ge=0, description="Nuclear atomic number before ECP replacement."
    )
    isotope: int = Field(
        ge=0, description="Isotope mass number; zero uses the label default."
    )
    mass: float | None = Field(
        default=None,
        gt=0,
        description="Explicit nuclear mass in atomic mass units; null uses the label.",
    )
    role: Literal["real", "ghost", "dummy"] = Field(
        description="Nuclear and basis role of this center."
    )


def centers(molecule: Molecule) -> tuple[Center, ...]:
    """Return nuclear labels with stable IDs and ghost/dummy roles retained.

    Raises:
        ValueError: A nucleus label or coordinate cannot be resolved.
    """  # noqa: DOC502 - The builder validates labels and coordinates.
    backend = to_obmol(molecule)
    return tuple(
        Center(
            id=source.id,
            element=ob.GetSymbol(atom.GetAtomicNum()) if atom.GetAtomicNum() else "X",
            atomic_number=atom.GetAtomicNum(),
            isotope=atom.GetIsotope(),
            mass=source.nucleus.mass,
            role="dummy"
            if source.nucleus.dummy
            else "ghost"
            if source.nucleus.ghost != "none"
            else "real",
        )
        for source, atom in zip(molecule.atoms, ob.OBMolAtomIter(backend), strict=True)
    )
