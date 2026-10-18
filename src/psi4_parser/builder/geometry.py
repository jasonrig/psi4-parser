"""Apply pure geometry transformations while retaining molecular identities."""

from collections.abc import Callable
from math import radians

import numpy as np

from psi4_parser.builder._model import BOHR_ANGSTROM, Angle, Length, evolve
from psi4_parser.builder._vectors import (
    MatrixArray,
    Vector,
    VectorArray,
    bend,
    cross,
    placed,
    rotation_matrix,
    scale,
    separation,
    sub,
    torsion,
    unit,
    vector_tuple,
)
from psi4_parser.builder.molecular import (
    Cartesian,
    GeometryExpression,
    GeometryParameter,
    Molecule,
    Parameter,
    UnresolvedGeometryError,
)
from psi4_parser.builder.symmetry import reconcile_symmetry

_DIMENSIONS = 3
_STRAIGHT_ANGLE = 180

type MolecularStage = Callable[[Molecule], Molecule]
type CoordinateTransform = Callable[[MatrixArray], MatrixArray]


def _parameter(molecule: Molecule, reference: Parameter) -> Length | Angle:
    for parameter in molecule.parameters:
        if parameter.name == reference.name:
            if isinstance(parameter.value, GeometryExpression):
                break
            return evolve(
                parameter.value,
                value=parameter.value.value * (-1 if reference.negative else 1),
            )
    raise UnresolvedGeometryError(
        "Numerical geometry requires a resolved parameter: " + reference.name
    )


def _cartesian_value(
    molecule: Molecule, value: float | Parameter | GeometryExpression, unit_name: str
) -> float:
    if isinstance(value, GeometryExpression):
        raise UnresolvedGeometryError(
            "Numerical geometry requires resolved Cartesian expressions"
        )
    if isinstance(value, Parameter):
        quantity = _parameter(molecule, value)
        if not isinstance(quantity, Length):
            raise ValueError("Cartesian parameters require length values")
        return quantity.angstroms
    return value * (BOHR_ANGSTROM if unit_name == "bohr" else 1.0)


def positions(molecule: Molecule) -> dict[str, Vector]:
    """Return resolved Cartesian or mixed Z-matrix positions in angstroms.

    Raises:
        UnresolvedGeometryError: Geometry contains unresolved sources or expressions.
        ValueError: A coordinate has an incompatible dimension.
    """
    if molecule.sources or molecule.efp:
        raise UnresolvedGeometryError(
            "Numerical geometry requires resolved atoms without "
            "external sources or EFP placements"
        )
    result: dict[str, Vector] = {}
    for atom in molecule.atoms:
        coordinates = atom.coordinates
        if isinstance(coordinates, Cartesian):
            result[atom.id] = tuple3(
                tuple(
                    _cartesian_value(molecule, v, coordinates.unit)
                    for v in (coordinates.x, coordinates.y, coordinates.z)
                )
            )
        else:
            values: list[float] = []
            for index, anchor in enumerate(coordinates.anchors):
                quantity = (
                    _parameter(molecule, anchor.value)
                    if isinstance(anchor.value, Parameter)
                    else anchor.value
                )
                if isinstance(quantity, GeometryExpression):
                    raise UnresolvedGeometryError(
                        "Numerical geometry requires resolved anchor expressions"
                    )
                if index == 0:
                    if not isinstance(quantity, Length):
                        raise ValueError("Distance anchor requires a length")
                    values.append(quantity.angstroms)
                else:
                    if not isinstance(quantity, Angle):
                        raise ValueError("Angular anchor requires an angle")
                    values.append(quantity.degrees)
            result[atom.id] = placed(
                tuple(result[a.atom] for a in coordinates.anchors), tuple(values)
            )
    return result


def tuple3(values: tuple[float, ...]) -> Vector:
    """Return three values after checking the numerical adapter boundary.

    Raises:
        ValueError: The vector does not have three components.
    """
    if len(values) != _DIMENSIONS:
        raise ValueError("Expected a three-dimensional vector")
    return values[0], values[1], values[2]


def _cartesian_only(molecule: Molecule) -> dict[str, Vector]:
    if any(not isinstance(a.coordinates, Cartesian) for a in molecule.atoms):
        raise ValueError(
            "Convert explicitly to Cartesian coordinates before numerical edits"
        )
    for atom in molecule.atoms:
        coordinate = atom.coordinates
        if isinstance(coordinate, Cartesian) and any(
            not isinstance(v, float) for v in (coordinate.x, coordinate.y, coordinate.z)
        ):
            raise ValueError(
                "Resolve symbolic geometry with to_cartesian before numerical edits"
            )
    return positions(molecule)


def with_positions(molecule: Molecule, points: dict[str, Vector]) -> Molecule:
    """Return new Cartesian positions while preserving molecular metadata."""
    result = evolve(
        molecule,
        atoms=tuple(
            evolve(
                a,
                coordinates=Cartesian(
                    x=points[a.id][0], y=points[a.id][1], z=points[a.id][2]
                ),
            )
            for a in molecule.atoms
        ),
    )
    return reconcile_symmetry(result, points=points)


def to_cartesian(molecule: Molecule) -> Molecule:
    """Return the resolved geometry in Cartesian angstrom coordinates."""
    return with_positions(molecule, positions(molecule))


def _transform_positions(
    molecule: Molecule,
    points: dict[str, Vector],
    moving: tuple[str, ...],
    transform: CoordinateTransform,
) -> Molecule:
    updated = points.copy()
    if moving:
        coordinates: tuple[Vector, ...] = tuple(points[identity] for identity in moving)
        selected: MatrixArray = np.asarray(coordinates, dtype=np.float64)
        transformed = transform(selected)
        for index, identity in enumerate(moving):
            row: VectorArray = np.take(transformed, index, axis=0)
            updated[identity] = vector_tuple(row)
    return with_positions(molecule, updated)


def _translation(displacement: Vector) -> CoordinateTransform:
    offset = np.asarray(displacement, dtype=np.float64)
    return lambda coordinates: coordinates + offset


def _rotation(axis: Vector, angle: float, origin: Vector) -> CoordinateTransform:
    matrix = rotation_matrix(axis, angle)
    center = np.asarray(origin, dtype=np.float64)
    return lambda coordinates: (coordinates - center) @ matrix + center


def translate(offset: tuple[Length, Length, Length]) -> MolecularStage:
    """Return a stage that translates Cartesian geometry by a displacement."""
    transform = _translation(tuple3(tuple(v.angstroms for v in offset)))

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        return _transform_positions(molecule, points, tuple(points), transform)

    return apply


def rotate(
    axis: Vector, angle: Angle, *, origin: tuple[Length, Length, Length] | None = None
) -> MolecularStage:
    """Return a stage that rotates Cartesian geometry about an axis."""
    center = (
        (0.0, 0.0, 0.0)
        if origin is None
        else tuple3(tuple(v.angstroms for v in origin))
    )
    transform = _rotation(axis, radians(angle.degrees), center)

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        return _transform_positions(molecule, points, tuple(points), transform)

    return apply


def with_parameter(
    name: str, value: Length | Angle | GeometryExpression
) -> MolecularStage:
    """Return a stage that replaces a named geometry parameter."""

    def apply(molecule: Molecule) -> Molecule:
        previous = next((p for p in molecule.parameters if p.name == name), None)
        if previous is None:
            raise ValueError("Unknown geometry parameter: " + name)
        if (
            not isinstance(previous.value, GeometryExpression)
            and not isinstance(value, GeometryExpression)
            and type(previous.value) is not type(value)
        ):
            raise ValueError("Parameter replacement must retain its dimension")
        result = evolve(
            molecule,
            parameters=tuple(
                GeometryParameter(name=name, value=value) if p.name == name else p
                for p in molecule.parameters
            ),
        )
        return reconcile_symmetry(result)

    return apply


def reorder_atoms(order: tuple[str, ...]) -> MolecularStage:
    """Return a stage that reorders atoms within their fragments."""

    def apply(molecule: Molecule) -> Molecule:
        if len(set(order)) != len(order) or set(order) != {
            a.id for a in molecule.atoms
        }:
            raise ValueError("Atom ordering must contain every atom exactly once")
        atoms = {a.id: a for a in molecule.atoms}
        fragments = tuple(
            evolve(f, atom_ids=tuple(a for a in order if a in f.atom_ids))
            for f in molecule.fragments
        )
        if fragments and tuple(a for f in fragments for a in f.atom_ids) != order:
            raise ValueError("Atom ordering must preserve fragment order")
        return evolve(
            molecule, atoms=tuple(atoms[a] for a in order), fragments=fragments
        )

    return apply


def connected_side(molecule: Molecule, fixed: str, moving: str) -> tuple[str, ...]:
    """Return the moving side of a bond, rejecting ambiguous ring cuts.

    Raises:
        ValueError: The bond is unknown or belongs to a ring.
    """
    graph = {a.id: set[str]() for a in molecule.atoms}
    for bond in molecule.bonds:
        a, b = bond.atoms
        graph[a].add(b)
        graph[b].add(a)
    if fixed not in graph or moving not in graph[fixed]:
        raise ValueError("Selection requires an explicitly known bond")
    graph[fixed].remove(moving)
    graph[moving].remove(fixed)
    seen = {moving}
    pending = [moving]
    while pending:
        current = pending.pop()
        for neighbor in graph[current] - seen:
            seen.add(neighbor)
            pending.append(neighbor)
    if fixed in seen:
        raise ValueError("Bond lies in a ring; provide an explicit moving selection")
    return tuple(a.id for a in molecule.atoms if a.id in seen)


def _selection(
    points: dict[str, Vector], atoms: tuple[str, ...], moving: tuple[str, ...]
) -> None:
    if not set(atoms) <= points.keys() or not set(moving) <= points.keys():
        raise ValueError("Coordinate and moving selection must use known atom IDs")
    if len(set(atoms)) != len(atoms) or len(set(moving)) != len(moving):
        raise ValueError("Coordinate and moving selection must use distinct atom IDs")
    if atoms[-1] not in moving or set(atoms[:-1]) & set(moving):
        raise ValueError(
            "Moving selection must contain the final endpoint and "
            "exclude fixed reference atoms"
        )


def set_distance(
    atoms: tuple[str, str], length: Length, *, moving: tuple[str, ...]
) -> MolecularStage:
    """Return a stage that sets a distance using a moving selection.

    Raises:
        ValueError: The requested distance is not positive.
    """
    if length.angstroms <= 0:
        raise ValueError("Distance must be positive")

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        _selection(points, atoms, moving)
        a, b = (points[key] for key in atoms)
        shift = scale(unit(sub(b, a)), length.angstroms - separation(a, b))
        return _transform_positions(molecule, points, moving, _translation(shift))

    return apply


def set_angle(
    atoms: tuple[str, str, str], angle: Angle, *, moving: tuple[str, ...]
) -> MolecularStage:
    """Return a stage that sets a bend using a moving selection.

    Raises:
        ValueError: The bend lies outside the open interval (0, 180).
    """
    if not 0 < angle.degrees < _STRAIGHT_ANGLE:
        raise ValueError("Bend angles must be strictly between zero and 180 degrees")

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        _selection(points, atoms, moving)
        a, b, c = (points[key] for key in atoms)
        axis = unit(cross(sub(a, b), sub(c, b)))
        delta = radians(angle.degrees - bend(a, b, c))
        return _transform_positions(molecule, points, moving, _rotation(axis, delta, b))

    return apply


def set_dihedral(
    atoms: tuple[str, str, str, str], angle: Angle, *, moving: tuple[str, ...]
) -> MolecularStage:
    """Return a stage that sets a torsion using a moving selection."""

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        _selection(points, atoms, moving)
        a, b, c, d = (points[key] for key in atoms)
        delta = radians(angle.degrees - torsion(a, b, c, d))
        axis = sub(c, b)
        return _transform_positions(molecule, points, moving, _rotation(axis, delta, c))

    return apply
