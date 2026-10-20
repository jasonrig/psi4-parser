"""Verify computational symmetry without changing molecular coordinates."""

import warnings
from collections.abc import Callable, Iterator
from enum import StrEnum
from itertools import islice
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import Field

from psi4_parser.builder._model import Model, evolve
from psi4_parser.builder._vectors import (
    VECTOR_EPSILON,
    MatrixArray,
    Vector,
    add,
    cross,
    dot,
    norm,
    scale,
    separation,
    sub,
    unit,
    vector_tuple,
)
from psi4_parser.builder.molecular import (
    Molecule,
    SymmetrySite,
    UnresolvedGeometryError,
)
from psi4_parser.builder.molsym import point_group as molsym_point_group
from psi4_parser.builder.openbabel import to_obmol


# Psi4 supports these Abelian computational groups and their axis qualifiers.
class Psi4PointGroup(StrEnum):
    """Identify the eight supported computational point groups."""

    C1 = "c1"
    CI = "ci"
    CS = "cs"
    C2 = "c2"
    D2 = "d2"
    C2V = "c2v"
    C2H = "c2h"
    D2H = "d2h"


type AxisSigns = tuple[int, int, int]
type SymmetryFrame = tuple[Vector, Vector, Vector]
type AtomMatching = dict[int, int]
type CandidateTargets = tuple[int, ...]

# Psi4 verifies symmetry at 1e-8 bohr. Use a stricter Cartesian residual.
SYMMETRY_TOLERANCE = 1e-9  # Maximum positional mismatch in angstroms.
POINT_GROUP_TOLERANCE = 1e-6  # Full-group detection tolerance in angstroms.
_MASS_TOLERANCE = 1e-8  # Isotopic masses must agree in atomic mass units.
_FRAME_SEARCH_LIMIT = 10_000
_WORLD: SymmetryFrame = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
_OPERATIONS: dict[Psi4PointGroup, tuple[AxisSigns, ...]] = {
    Psi4PointGroup.C1: (),
    Psi4PointGroup.CI: ((-1, -1, -1),),
    Psi4PointGroup.CS: ((1, 1, -1),),
    Psi4PointGroup.C2: ((-1, -1, 1),),
    Psi4PointGroup.D2: ((1, -1, -1), (-1, 1, -1), (-1, -1, 1)),
    Psi4PointGroup.C2V: ((-1, -1, 1), (1, -1, 1), (-1, 1, 1)),
    Psi4PointGroup.C2H: ((-1, -1, 1), (-1, -1, -1), (1, 1, -1)),
    Psi4PointGroup.D2H: (
        (-1, -1, -1),
        (1, -1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
        (1, 1, -1),
        (1, -1, 1),
        (-1, 1, 1),
    ),
}
_SUBGROUPS: dict[Psi4PointGroup, tuple[Psi4PointGroup, ...]] = {
    Psi4PointGroup.C1: (Psi4PointGroup.C1,),
    Psi4PointGroup.CI: (Psi4PointGroup.C1,),
    Psi4PointGroup.CS: (Psi4PointGroup.C1,),
    Psi4PointGroup.C2: (Psi4PointGroup.C1,),
    Psi4PointGroup.D2: (Psi4PointGroup.C2, Psi4PointGroup.C1),
    Psi4PointGroup.C2V: (Psi4PointGroup.C2, Psi4PointGroup.CS, Psi4PointGroup.C1),
    Psi4PointGroup.C2H: (
        Psi4PointGroup.CI,
        Psi4PointGroup.C2,
        Psi4PointGroup.CS,
        Psi4PointGroup.C1,
    ),
    Psi4PointGroup.D2H: (
        Psi4PointGroup.D2,
        Psi4PointGroup.C2V,
        Psi4PointGroup.C2H,
        Psi4PointGroup.CI,
        Psi4PointGroup.C2,
        Psi4PointGroup.CS,
        Psi4PointGroup.C1,
    ),
}


class SymmetryChangedWarning(UserWarning):
    """Report that an edit required a different computational point group."""


class _SymmetryRequest(Model):
    group: Psi4PointGroup = Field(
        description="Point group used by Psi4 for the calculation."
    )
    axis: Literal["x", "y", "z"] | None = Field(
        default=None,
        description="Principal axis, or direction perpendicular to the mirror plane.",
    )


def _request(group: str) -> _SymmetryRequest:
    name = group.lower()
    axis = None
    if name[-1:] in {"x", "y", "z"}:
        name, axis = name[:-1], name[-1]
    if axis is not None and name not in {"cs", "c2", "c2h", "c2v"}:
        raise ValueError("Unsupported Psi4 symmetry request: " + group)
    try:
        parsed = Psi4PointGroup(name)
    except ValueError as error:
        raise ValueError("Unsupported Psi4 symmetry request: " + group) from error
    values: dict[str, str | None] = {"group": parsed, "axis": axis}
    return _SymmetryRequest.model_validate(values)


def _sites(
    geometry: Molecule, *, points: dict[str, Vector] | None = None
) -> tuple[SymmetrySite, ...]:
    backend = to_obmol(geometry, points=points)
    sites: list[SymmetrySite] = []
    for index, source in enumerate(geometry.atoms, 1):
        if source.nucleus.dummy:
            continue
        atom = backend.GetAtom(index)
        if atom is None:
            raise ValueError("Open Babel returned a missing symmetry site")
        sites.append(
            SymmetrySite(
                position=(atom.GetX(), atom.GetY(), atom.GetZ()),
                element=atom.GetAtomicNum(),
                mass=source.nucleus.mass
                if source.nucleus.mass is not None
                else atom.GetExactMass(),
                ghost=source.nucleus.ghost != "none",
            )
        )
    if not sites:
        raise ValueError("Symmetry verification requires at least one non-dummy atom")
    center: Vector = (0.0, 0.0, 0.0)
    if not geometry.fixed_com:
        coordinates: tuple[Vector, ...] = tuple(site.position for site in sites)
        center = vector_tuple(
            np.mean(np.asarray(coordinates, dtype=np.float64), axis=0)
        )
    return tuple(evolve(site, position=sub(site.position, center)) for site in sites)


def _equivalent(first: SymmetrySite, second: SymmetrySite) -> bool:
    return (
        first.element == second.element
        and first.ghost == second.ghost
        and abs(first.mass - second.mass) <= _MASS_TOLERANCE
    )


def _directions(sites: tuple[SymmetrySite, ...]) -> tuple[Vector, ...]:
    directions: dict[Vector, Vector] = {}

    def include(vector: Vector) -> None:
        if norm(vector) <= VECTOR_EPSILON:
            return
        direction = unit(vector)
        leading = next(value for value in direction if abs(value) > VECTOR_EPSILON)
        if leading < 0:
            direction = scale(direction, -1)
        key = vector_tuple(np.round(np.asarray(direction, dtype=np.float64), 10))
        directions[key] = direction

    for axis in _WORLD:
        include(axis)
    for index, first in enumerate(sites):
        include(first.position)
        for second in sites[index + 1 :]:
            include(cross(first.position, second.position))
            if _equivalent(first, second):
                include(add(first.position, second.position))
                include(sub(first.position, second.position))
    return tuple(directions.values())


def _frames(
    geometry: Molecule, sites: tuple[SymmetrySite, ...], request: _SymmetryRequest
) -> Iterator[SymmetryFrame]:
    if request.axis is not None and not geometry.fixed_orientation:
        return
    for index in range(3):
        if request.axis is None or index == {"x": 0, "y": 1, "z": 2}[request.axis]:
            yield _WORLD[(index + 1) % 3], _WORLD[(index + 2) % 3], _WORLD[index]
    if geometry.fixed_orientation:
        return
    # Axis suffixes refer to Psi4's chosen symmetry frame. Without a fixed
    # frame, their orientation cannot be verified independently of Psi4.
    if request.axis is not None:
        return
    directions = _directions(sites)
    for z_axis in directions:
        for direction in directions:
            projected = sub(direction, scale(z_axis, dot(direction, z_axis)))
            if norm(projected) > VECTOR_EPSILON:
                x_axis = unit(projected)
                yield x_axis, cross(z_axis, x_axis), z_axis


def _transformed(position: Vector, frame: SymmetryFrame, signs: AxisSigns) -> Vector:
    basis: MatrixArray = np.asarray(frame, dtype=np.float64)
    local = np.asarray(position, dtype=np.float64) @ basis.T
    return vector_tuple((local * np.asarray(signs, dtype=np.float64)) @ basis)


def _matches(
    sites: tuple[SymmetrySite, ...], frame: SymmetryFrame, signs: AxisSigns
) -> bool:
    candidates: list[CandidateTargets] = []
    for source_site in sites:
        transformed = _transformed(source_site.position, frame, signs)
        candidates.append(
            tuple(
                index
                for index, target in enumerate(sites)
                if _equivalent(source_site, target)
                and separation(transformed, target.position) <= SYMMETRY_TOLERANCE
            )
        )
    matching: AtomMatching = {}

    def assign(source_index: int, seen: set[int]) -> bool:
        for target in candidates[source_index]:
            if target not in seen:
                seen.add(target)
                if target not in matching or assign(matching[target], seen):
                    matching[target] = source_index
                    return True
        return False

    return all(assign(index, set()) for index in range(len(sites)))


def _supports(
    geometry: Molecule, sites: tuple[SymmetrySite, ...], request: _SymmetryRequest
) -> bool:
    if request.group == Psi4PointGroup.C1:
        return True
    return any(
        all(
            _matches(sites, frame, operation)
            for operation in _OPERATIONS[request.group]
        )
        for frame in islice(_frames(geometry, sites, request), _FRAME_SEARCH_LIMIT)
    )


def reconcile_symmetry(
    geometry: Molecule, *, points: dict[str, Vector] | None = None
) -> Molecule:
    """Return an edited molecule with a verified symmetry request, warning on change.

    Coordinates and atom records are retained. Unresolved geometry uses C1
    because its requested symmetry cannot be verified numerically.

    Args:
        geometry: Edited molecule whose computational group is checked.
        points: Optional already-resolved positions for this geometry in angstroms.
    """
    if geometry.symmetry is None or geometry.symmetry.lower() == "c1":
        return geometry
    request = _request(geometry.symmetry)
    try:
        sites = _sites(geometry, points=points)
    except UnresolvedGeometryError:
        replacement: Psi4PointGroup = Psi4PointGroup.C1
        reason = "cannot be verified for unresolved geometry"
    else:
        if _supports(geometry, sites, request):
            return geometry
        replacement = next(
            group
            for group in _SUBGROUPS[request.group]
            if _supports(geometry, sites, _SymmetryRequest(group=group))
        )
        reason = "is not verified for the edited geometry and reference frame"
    warnings.warn(
        f"Requested symmetry {geometry.symmetry!r} {reason}; "
        f"using {replacement.value!r}. "
        "Atom records and parameter references are retained.",
        SymmetryChangedWarning,
        skip_file_prefixes=(str(Path(__file__).parent),),
    )
    return evolve(geometry, symmetry=replacement.value)


def with_symmetry(group: str | None) -> Callable[[Molecule], Molecule]:
    """Create a transformation that selects Psi4's computational point group.

    Args:
        group: c1, ci, cs, c2, d2, c2v, c2h, or d2h. Use c1 for fully relaxed
            symmetry, a compatible lower group for partial relaxation, or None
            to let Psi4 detect symmetry. Supported axis qualifiers include c2x
            and csz.

    Returns:
        A function used as ``geometry | with_symmetry("c1")``. Atom coordinates,
        parameter relationships, and metadata are retained. Groups other than c1
        are checked against the resolved geometry and requested frame.

    Raises:
        ValueError: The group is unsupported or cannot be verified when applied.
    """  # noqa: DOC502 - The returned stage and request parser raise ValueError.
    request = None if group is None else _request(group)

    def apply(geometry: Molecule) -> Molecule:
        if (
            request is not None
            and request.group != Psi4PointGroup.C1
            and not _supports(geometry, _sites(geometry), request)
        ):
            raise ValueError(
                "Requested symmetry is not verified for this geometry: " + str(group)
            )
        return evolve(geometry, symmetry=None if group is None else group.lower())

    return apply


def detect_point_group(geometry: Molecule) -> str:
    """Identify a molecule's full point group, such as C2v or Td.

    Args:
        geometry: Resolved geometry with element, isotope, and ghost information.

    Returns:
        A Schoenflies symbol. Linear groups use Cinfv and Dinfh; a single atom
        uses Kh. MolSym uses a 1e-6 angstrom tolerance and excludes dummy atoms.
        Use with_symmetry() separately to choose a Psi4 computational subgroup.

    Raises:
        ValueError: Geometry is unresolved, or equal-mass sites have different
            elements or ghost roles that MolSym cannot distinguish.
        RuntimeError: MolSym cannot classify the geometry.
    """  # noqa: DOC502 - Numerical adapters raise these documented errors.
    return molsym_point_group(_sites(geometry), tolerance=POINT_GROUP_TOLERANCE)
