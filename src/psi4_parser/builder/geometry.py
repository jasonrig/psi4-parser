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
    """Resolve every atom's position in angstroms, keyed by atom ID.

    Args:
        molecule: Cartesian, Z-matrix, or mixed geometry with numerical values
            or parameters whose values are lengths and angles.

    Returns:
        A new dictionary mapping each atom ID to its (x, y, z) position. A
        Z-matrix uses Psi4's conventional placement relative to its anchors.

    Raises:
        UnresolvedGeometryError: A source, expression, parameter, or effective
            fragment potential needs to be resolved before numerical work.
        ValueError: A coordinate has the wrong dimension or undefined geometry.
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
    """Return three numerical values as an (x, y, z) tuple.

    Raises:
        ValueError: The input does not contain exactly three values.
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
    """Replace all atom coordinates with Cartesian positions in angstroms.

    Args:
        molecule: Molecule whose atom IDs and other metadata are retained.
        points: New (x, y, z) values for every atom ID in the molecule.

    Returns:
        A new molecule. Incompatible requested symmetry is lowered to a verified
        subgroup and reported with SymmetryChangedWarning.
    """
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
    """Convert resolved geometry to Cartesian coordinates in angstroms.

    Args:
        molecule: Geometry whose numerical coordinates or named parameters can
            be resolved. Z-matrix anchors determine the resulting frame.

    Returns:
        A new molecule retaining atom IDs, fragments, electronic states, and
        isotope and ghost metadata. A changed symmetry request emits a warning.

    Example:
        Resolve coordinates before applying numerical edits::

            cartesian = to_cartesian(geometry)
            shifted = cartesian | translate((angstrom(1), angstrom(0), angstrom(0)))
    """
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
    """Create a transformation that moves all Cartesian atoms by an offset.

    Args:
        offset: Signed x, y, and z displacements, each created with angstrom()
            or bohr(). Resolve symbolic or Z-matrix geometry with to_cartesian()
            before applying this transformation.

    Returns:
        A function used as ``geometry | translate(offset)`` or applied directly
        to a molecule. It returns a new molecule with stable atom IDs.
    """
    transform = _translation(tuple3(tuple(v.angstroms for v in offset)))

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        return _transform_positions(molecule, points, tuple(points), transform)

    return apply


def rotate(
    axis: Vector, angle: Angle, *, origin: tuple[Length, Length, Length] | None = None
) -> MolecularStage:
    """Create a transformation that rotates all Cartesian atoms about an axis.

    Args:
        axis: Finite nonzero (x, y, z) direction; it is normalized automatically.
        angle: Rotation angle from degrees() or radians(), using the right-hand rule.
        origin: Point through which the axis passes, with explicit length units.
            Defaults to the coordinate origin.

    Returns:
        A function used as ``geometry | rotate(axis, angle)``. Apply it to
        resolved Cartesian geometry; convert first with to_cartesian() if needed.
        Atom IDs and molecular metadata are retained.
    """
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
    """Create a transformation that replaces a named geometry parameter.

    Args:
        name: Exact name of an existing parameter.
        value: Replacement Length, Angle, or GeometryExpression. A numerical
            replacement must have the same dimension as the existing value.

    Returns:
        A function used as ``geometry | with_parameter("R", angstrom(1.2))``.
        Parameter references remain connected to the updated value. Unknown
        names or incompatible dimensions fail when the function is applied;
        incompatible symmetry requests emit a warning and are lowered.
    """

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
    """Create a transformation that changes atom order while retaining IDs.

    Args:
        order: Every atom ID exactly once, in the desired order. Keep fragments
            in their original order and Z-matrix anchors before their dependents.

    Returns:
        A function used as ``geometry | reorder_atoms(order)``. Invalid orders
        fail when applied; references and connectivity continue to use stable IDs.
    """

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
    """Find the atoms on one side of a known bond.

    Args:
        molecule: Geometry with explicit connectivity, supplied by the file or
            obtained by importing with perceive_bonds=True.
        fixed: Atom ID at the fixed end of the bond to cut.
        moving: Atom ID at the moving end of that bond.

    Returns:
        Atom IDs connected to moving after cutting this bond, in molecule order,
        including moving itself. This tuple can be an edit's moving selection.

    Raises:
        ValueError: The bond is unknown or lies in a ring. For a ring, supply an
            explicit moving selection to the edit instead.
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
    """Create a transformation that sets the separation of two Cartesian atoms.

    Args:
        atoms: Pair of atom IDs; the first stays fixed and the second moves.
        length: Positive target separation from angstrom() or bohr().
        moving: Distinct atom IDs to translate together along the pair's axis.
            Include the second endpoint and exclude the first.

    Returns:
        A function used as ``geometry | set_distance(atoms, length, moving=ids)``.
        Apply it to resolved Cartesian geometry. Other atoms retain their positions;
        incompatible symmetry requests emit a warning and are lowered.

    Raises:
        ValueError: The target length is not positive. Invalid selections,
            unresolved coordinates, or coincident endpoints fail when applied.
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
    """Create a transformation that sets a Cartesian bond angle.

    Args:
        atoms: Three atom IDs (a, b, c), with the angle's vertex at b.
        angle: Target from degrees() or radians(), strictly between 0 and 180 degrees.
        moving: Distinct atom IDs rotated together about b. Include c and exclude
            a and b. Use connected_side() to select a known bond's attached atoms.

    Returns:
        A function used as ``geometry | set_angle(atoms, angle, moving=ids)``.
        Apply it to resolved Cartesian geometry with a defined starting angle.
        Incompatible symmetry requests emit a warning and are lowered.

    Raises:
        ValueError: The target angle lies outside the allowed range. Invalid
            selections or degenerate starting geometry fail when applied.
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
    """Create a transformation that sets a signed Cartesian torsion.

    Args:
        atoms: Four atom IDs (a, b, c, d); the torsion is between planes abc and
            bcd, around the b-c axis.
        angle: Target torsion from degrees() or radians(), measured modulo 360 degrees.
        moving: Distinct atom IDs rotated together about b-c. Include d and exclude
            a, b, and c. Select attached atoms explicitly or with connected_side().

    Returns:
        A function used as ``geometry | set_dihedral(atoms, angle, moving=ids)``.
        Apply it to resolved Cartesian geometry with a defined torsion. Invalid
        selections or collinear reference atoms fail when applied. Incompatible
        symmetry requests emit a warning and are lowered.
    """

    def apply(molecule: Molecule) -> Molecule:
        points = _cartesian_only(molecule)
        _selection(points, atoms, moving)
        a, b, c, d = (points[key] for key in atoms)
        delta = radians(angle.degrees - torsion(a, b, c, d))
        axis = sub(c, b)
        return _transform_positions(molecule, points, moving, _rotation(axis, delta, c))

    return apply
