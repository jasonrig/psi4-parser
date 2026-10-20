"""Adapt resolved symmetry sites to MolSym's point-group detector."""

import molsym
import numpy as np

from psi4_parser.builder._vectors import Vector
from psi4_parser.builder.molecular import SymmetrySite


def point_group(sites: tuple[SymmetrySite, ...], *, tolerance: float) -> str:
    """Identify the full point group of resolved atomic sites.

    Args:
        sites: Element, mass, ghost role, and position for every real or ghost
            center, with positions in angstroms.
        tolerance: Positive position-matching tolerance in angstroms.

    Returns:
        Schoenflies symbol, with Cinfv and Dinfh for linear groups and Kh for
        a single center.

    MolSym distinguishes sites by mass. Equal-mass sites with different elements
    or ghost roles cannot be represented faithfully and are rejected.

    Raises:
        ValueError: Distinct nuclear roles share an identical mass.
        RuntimeError: MolSym cannot classify the supplied geometry.
    """
    for index, first in enumerate(sites):
        if any(
            first.mass == second.mass
            and (first.element != second.element or first.ghost != second.ghost)
            for second in sites[index + 1 :]
        ):
            raise ValueError(
                "MolSym cannot distinguish equal-mass sites with different "
                "elements or ghost roles"
            )
    if len(sites) == 1:
        return "Kh"
    labels: list[str] = [str(site.element) for site in sites]
    coordinates: list[Vector] = [site.position for site in sites]
    masses: list[float] = [site.mass for site in sites]
    geometry = molsym.Molecule(
        np.array(labels, dtype=np.str_),
        np.array(coordinates, dtype=np.float64),
        np.array(masses, dtype=np.float64),
    )
    geometry.tol = tolerance
    try:
        symbol, _axes = molsym.find_point_group(geometry)
    except (ValueError, np.linalg.LinAlgError) as error:
        raise RuntimeError(
            "MolSym could not determine the molecular point group"
        ) from error
    return {"C0v": "Cinfv", "D0h": "Dinfh"}.get(symbol, symbol)
