"""Choose Z-matrix layouts with requested coordinates and verified reconstruction."""

from collections.abc import Callable, Iterator
from itertools import permutations, product
from typing import Literal, overload

from pydantic import Field

from psi4_parser.builder._model import Model, angstrom, degrees, evolve
from psi4_parser.builder._vectors import (
    DegenerateGeometryError,
    Vector,
    add,
    alignment_error,
    bend,
    cross,
    norm,
    perpendicular,
    scale,
    separation,
    sub,
    torsion,
)
from psi4_parser.builder.constraints import Coordinate
from psi4_parser.builder.geometry import positions, with_positions
from psi4_parser.builder.molecular import (
    Anchor,
    AnchorReferences,
    AnchorRequirements,
    Atom,
    Cartesian,
    GeometryParameter,
    Molecule,
    Nucleus,
    Parameter,
    ZMatrix,
)
from psi4_parser.builder.openbabel import suggested_anchors
from psi4_parser.builder.symmetry import reconcile_symmetry

MINIMUM_DUMMY_REFERENCES = 2
DISTANCE_ANGLE_REFERENCES = 2
FULL_INTERNAL_REFERENCES = 3
DIHEDRAL_ATOMS = 4
GEOMETRY_EPSILON = 1e-12


# The slot identifies an atom and its zero-based distance/angle/dihedral column.
class CoordinateSlot(Model):
    """Identify a distance, angle, or dihedral column on one Z-matrix atom."""

    atom: str = Field(description="Stable identity of the atom being placed.")
    column: int = Field(
        ge=0, le=2, description="Zero-based distance, angle, or dihedral column."
    )


type VariableNames = dict[CoordinateSlot, str]


class OrientedCoordinate(Model):
    """Choose the atom to place and its ordered reference atoms."""

    atom: str = Field(description="Stable identity of the atom being placed.")
    references: AnchorReferences = Field(
        description="Distance, angle, and dihedral reference identities."
    )


class LayoutRequirements(Model):
    """Group anchor dependencies with requested geometry-variable names."""

    anchors: AnchorRequirements = Field(
        description="Required reference prefix for each constrained atom."
    )
    variables: VariableNames = Field(
        description="Requested variable name for each constrained coordinate slot."
    )


class ReconstructionPolicy(Model):
    """Set finite reconstruction tolerances and the explicit frame choice."""

    frame: Literal["canonical", "preserve"] = Field(
        description="Accept canonical placement or require the laboratory frame."
    )
    position_tolerance: float = Field(
        gt=0,
        description="Maximum position residual in angstroms after proper alignment.",
    )
    angle_tolerance: float = Field(
        gt=0, description="Maximum angular residual in degrees."
    )


class IncompatibleCoordinatesError(ValueError):
    """Report coordinate requests that cannot share a Z-matrix layout."""


class LayoutSearchExhaustedError(ValueError):
    """Report exhaustion of the explicit automatic-layout search budget."""


class NamedCoordinate(Model):
    """Require an internal coordinate to become a named Z-matrix parameter."""

    name: str = Field(
        min_length=1, description="Name of the emitted geometry variable."
    )
    coordinate: Coordinate = Field(description="Distance, bend, or dihedral to expose.")


class AnchorLayout(Model):
    """Prescribe one atom's complete ordered Z-matrix reference list."""

    atom: str = Field(min_length=1, description="Stable atom ID being placed.")
    references: tuple[str, ...] = Field(
        max_length=3, description="Distance, angle, and dihedral reference IDs."
    )


class _Budget:
    def __init__(self, limit: int) -> None:
        if limit < 1:
            raise ValueError("Layout search budget must be positive")
        self.remaining = limit

    def consume(self) -> None:
        self.remaining -= 1
        if self.remaining < 0:
            raise LayoutSearchExhaustedError(
                "Z-matrix layout search exhausted its candidate-state "
                "budget; increase max_states or supply a layout"
            )


class _LayoutContext:
    def __init__(
        self, molecule: Molecule, points: dict[str, Vector], budget: _Budget
    ) -> None:
        self.suggestions = suggested_anchors(molecule, points=points)
        self.points = points
        self.budget = budget


def _orientations(request: NamedCoordinate) -> tuple[OrientedCoordinate, ...]:
    coord = request.coordinate
    if coord.kind not in {"distance", "angle", "dihedral"}:
        raise IncompatibleCoordinatesError(
            "Z-matrix variables support distances, angles, and dihedrals"
        )
    return (
        OrientedCoordinate(atom=coord.atoms[0], references=coord.atoms[1:]),
        OrientedCoordinate(
            atom=coord.atoms[-1], references=tuple(reversed(coord.atoms[:-1]))
        ),
    )


def _requirements(
    requests: tuple[NamedCoordinate, ...], budget: _Budget
) -> Iterator[LayoutRequirements]:
    for orientations in product(*(_orientations(request) for request in requests)):
        budget.consume()
        required: AnchorRequirements = {}
        names: VariableNames = {}
        for request, orientation in zip(requests, orientations, strict=True):
            atom, refs = orientation.atom, orientation.references
            existing = required.get(atom, ())
            overlap = min(len(existing), len(refs))
            if (
                existing[:overlap] != refs[:overlap]
                or CoordinateSlot(atom=atom, column=len(refs) - 1) in names
            ):
                break
            required[atom] = refs if len(refs) > len(existing) else existing
            names[CoordinateSlot(atom=atom, column=len(refs) - 1)] = request.name
        else:
            yield LayoutRequirements(anchors=required, variables=names)


def _orders(
    molecule: Molecule, required: AnchorRequirements, *, reorder: bool, budget: _Budget
) -> Iterator[tuple[str, ...]]:
    original = tuple(a.id for a in molecule.atoms)
    if not reorder:
        indices = {atom: i for i, atom in enumerate(original)}
        if all(
            all(indices[ref] < indices[atom] for ref in refs)
            for atom, refs in required.items()
        ):
            yield original
        return
    groups = tuple(f.atom_ids for f in molecule.fragments) or (original,)

    def visit(
        completed: tuple[str, ...], group_index: int
    ) -> Iterator[tuple[str, ...]]:
        if group_index == len(groups):
            yield completed
            return
        pending = tuple(atom for atom in groups[group_index] if atom not in completed)
        if not pending:
            yield from visit(completed, group_index + 1)
            return
        for atom in pending:
            if set(required.get(atom, ())) <= set(completed):
                budget.consume()
                yield from visit((*completed, atom), group_index)

    yield from visit((), 0)


def _measured(point: Vector, refs: tuple[Vector, ...]) -> tuple[float, ...]:
    values = [separation(point, refs[0])] if refs else []
    if values and values[0] < GEOMETRY_EPSILON:
        raise DegenerateGeometryError("Coincident atoms cannot form a distance anchor")
    if len(refs) >= DISTANCE_ANGLE_REFERENCES:
        values.append(bend(point, refs[0], refs[1]))
    if len(refs) == FULL_INTERNAL_REFERENCES:
        try:
            values.append(torsion(point, *refs))
        except DegenerateGeometryError:
            # An unrequested linear bend has no torsion, but any torsion places
            # the same point if the reference plane itself is defined.
            if (
                norm(cross(sub(refs[0], refs[1]), sub(refs[1], refs[2])))
                < GEOMETRY_EPSILON
            ):
                raise
            values.append(0.0)
    return tuple(values)


def _choose_refs(
    atom: str,
    prior: tuple[str, ...],
    required: tuple[str, ...],
    context: _LayoutContext,
) -> tuple[str, ...]:
    suggestions, points, budget = context.suggestions, context.points, context.budget
    count = min(3, len(prior))
    if len(required) > count:
        raise IncompatibleCoordinatesError(
            "Not enough preceding atoms for a requested coordinate"
        )
    preferred = suggestions.get(atom, ())[:count]
    candidates: tuple[AnchorReferences, ...] = (
        (preferred,)
        if len(preferred) == count
        and set(preferred) <= set(prior)
        and preferred[: len(required)] == required
        else ()
    )
    remaining = tuple(a for a in reversed(prior) if a not in required)
    for refs in candidates:
        try:
            _measured(points[atom], tuple(points[a] for a in refs))
        except DegenerateGeometryError:
            pass
        else:
            return refs
    for tail in permutations(remaining, count - len(required)):
        budget.consume()
        refs = required + tail
        try:
            _measured(points[atom], tuple(points[a] for a in refs))
        except DegenerateGeometryError:
            continue
        return refs
    raise DegenerateGeometryError(
        "No nondegenerate Z-matrix reference frame; "
        "allow_dummies=True may supply a reference plane"
    )


def _layout(
    order: tuple[str, ...],
    required: AnchorRequirements,
    context: _LayoutContext,
) -> tuple[AnchorLayout, ...]:
    return tuple(
        AnchorLayout(
            atom=atom,
            references=_choose_refs(
                atom, order[:index], required.get(atom, ()), context
            ),
        )
        for index, atom in enumerate(order)
    )


def _build(
    molecule: Molecule,
    layout: tuple[AnchorLayout, ...],
    names: VariableNames,
    points: dict[str, Vector],
) -> Molecule:
    atoms = {a.id: a for a in molecule.atoms}
    result: list[Atom] = []
    parameters = list(molecule.parameters)
    for row in layout:
        measured = _measured(points[row.atom], tuple(points[a] for a in row.references))
        anchors: list[Anchor] = []
        for index, (ref, number) in enumerate(
            zip(row.references, measured, strict=True)
        ):
            quantity = angstrom(number) if index == 0 else degrees(number)
            name = names.get(CoordinateSlot(atom=row.atom, column=index))
            if name is not None:
                parameters.append(GeometryParameter(name=name, value=quantity))
            anchors.append(
                Anchor(
                    atom=ref, value=quantity if name is None else Parameter(name=name)
                )
            )
        result.append(
            evolve(atoms[row.atom], coordinates=ZMatrix(anchors=tuple(anchors)))
        )
    order = tuple(a.id for a in result)
    fragments = tuple(
        evolve(f, atom_ids=tuple(a for a in order if a in f.atom_ids))
        for f in molecule.fragments
    )
    return evolve(
        molecule,
        atoms=tuple(result),
        parameters=tuple(parameters),
        fragments=fragments,
        xyz_header=None,
    )


def _validate_requests(
    molecule: Molecule,
    requested: tuple[NamedCoordinate, ...],
    points: dict[str, Vector],
) -> None:
    ids = set(points)
    existing = {p.name for p in molecule.parameters}
    names = tuple(r.name for r in requested)
    if len(set(names)) != len(names) or existing.intersection(names):
        raise IncompatibleCoordinatesError(
            "Requested geometry variable names must be new and unique"
        )
    for request in requested:
        if not set(request.coordinate.atoms) <= ids:
            raise IncompatibleCoordinatesError(
                "Requested coordinate references an unknown atom"
            )
        _orientations(request)
        coordinates = tuple(points[a] for a in request.coordinate.atoms)
        if request.coordinate.kind == "dihedral":
            torsion(coordinates[0], coordinates[1], coordinates[2], coordinates[3])
        elif request.coordinate.kind == "angle":
            bend(coordinates[0], coordinates[1], coordinates[2])
        elif separation(coordinates[0], coordinates[1]) < GEOMETRY_EPSILON:
            raise DegenerateGeometryError(
                "Requested distance is undefined for coincident atoms"
            )


def _add_dummy(molecule: Molecule, points: dict[str, Vector]) -> Molecule:
    if len(molecule.atoms) < MINIMUM_DUMMY_REFERENCES:
        raise DegenerateGeometryError(
            "Dummy insertion requires two distinct reference atoms"
        )
    first, second = molecule.atoms[:2]
    offset = perpendicular(sub(points[second.id], points[first.id]))
    position = add(points[first.id], scale(offset, 1.0))
    index = 1
    while f"dummy{index}" in points:
        index += 1
    dummy = Atom(
        id=f"dummy{index}",
        nucleus=Nucleus(label="X"),
        coordinates=Cartesian(x=position[0], y=position[1], z=position[2]),
    )
    atoms = (*molecule.atoms[:2], dummy, *molecule.atoms[2:])
    fragments = []
    for fragment in molecule.fragments:
        members = tuple(
            a.id
            for a in atoms
            if a.id in fragment.atom_ids
            or (a.id == dummy.id and second.id in fragment.atom_ids)
        )
        fragments.append(evolve(fragment, atom_ids=members))
    return evolve(molecule, atoms=atoms, fragments=tuple(fragments))


def _automatic(
    molecule: Molecule,
    requested: tuple[NamedCoordinate, ...],
    points: dict[str, Vector],
    *,
    reorder: bool,
    budget: _Budget,
) -> Molecule:
    context = _LayoutContext(molecule, points, budget)
    degenerate: DegenerateGeometryError | None = None
    for requirements in _requirements(requested, budget):
        required, names = requirements.anchors, requirements.variables
        for order in _orders(molecule, required, reorder=reorder, budget=budget):
            try:
                layout = _layout(order, required, context)
                return _build(molecule, layout, names, points)
            except DegenerateGeometryError as error:
                degenerate = error
    if degenerate is not None:
        raise degenerate
    raise IncompatibleCoordinatesError(
        "Requested coordinates cannot share a Z-matrix layout "
        "under the selected ordering"
    )


def _explicit(
    molecule: Molecule,
    requested: tuple[NamedCoordinate, ...],
    layout: tuple[AnchorLayout, ...],
    points: dict[str, Vector],
    *,
    reorder: bool,
) -> Molecule:
    original = tuple(a.id for a in molecule.atoms)
    order = tuple(row.atom for row in layout)
    if len(set(order)) != len(order) or set(order) != set(original):
        raise IncompatibleCoordinatesError(
            "Explicit layout must contain every atom exactly once"
        )
    if not reorder and order != original:
        raise IncompatibleCoordinatesError(
            "Explicit atom reordering requires reorder=True"
        )
    preceding: set[str] = set()
    for index, row in enumerate(layout):
        if (
            len(row.references) != min(FULL_INTERNAL_REFERENCES, index)
            or len(set(row.references)) != len(row.references)
            or not set(row.references) <= preceding
        ):
            raise IncompatibleCoordinatesError(
                "Explicit layout requires distinct preceding references "
                "for each coordinate column"
            )
        preceding.add(row.atom)
    names: VariableNames = {}
    rows = {row.atom: row.references for row in layout}
    for request in requested:
        for orientation in _orientations(request):
            atom, refs = orientation.atom, orientation.references
            if rows[atom][: len(refs)] == refs:
                names[CoordinateSlot(atom=atom, column=len(refs) - 1)] = request.name
                break
        else:
            raise IncompatibleCoordinatesError(
                "Explicit layout does not expose requested coordinate: " + request.name
            )
    return _build(molecule, layout, names, points)


def _verify(
    before: dict[str, Vector],
    result: Molecule,
    *,
    settings: ReconstructionPolicy,
    requested: tuple[NamedCoordinate, ...],
) -> dict[str, Vector]:
    if settings.frame == "preserve" and len(before) > 1:
        raise IncompatibleCoordinatesError(
            "Psi4 normalizes Z-matrix orientation; retain Cartesian geometry "
            "to preserve a laboratory frame"
        )
    after = positions(result)
    ids = tuple(before)
    error = alignment_error(tuple(before[a] for a in ids), tuple(after[a] for a in ids))
    if error > settings.position_tolerance:
        raise DegenerateGeometryError(
            "Z-matrix reconstruction failed proper-alignment verification"
        )
    if (
        settings.frame == "preserve"
        and max((separation(before[a], after[a]) for a in ids), default=0.0)
        > settings.position_tolerance
    ):
        raise IncompatibleCoordinatesError(
            "Plain Z-matrix cannot retain this laboratory frame; "
            "choose frame='canonical' or retain Cartesian "
            "coordinates"
        )
    for request in requested:
        atoms = request.coordinate.atoms
        if len(atoms) == DIHEDRAL_ATOMS:
            delta = torsion(*(before[a] for a in atoms)) - torsion(
                *(after[a] for a in atoms)
            )
            if abs((delta + 180) % 360 - 180) > settings.angle_tolerance:
                raise DegenerateGeometryError(
                    "Requested dihedral failed reconstruction verification"
                )
        elif (
            len(atoms) == FULL_INTERNAL_REFERENCES
            and abs(
                bend(*(before[a] for a in atoms)) - bend(*(after[a] for a in atoms))
            )
            > settings.angle_tolerance
        ):
            raise DegenerateGeometryError(
                "Requested angle failed reconstruction verification"
            )
    return after


@overload
def to_zmatrix(
    molecule: Molecule,
    *,
    frame: Literal["canonical", "preserve"],
    requested: tuple[NamedCoordinate, ...] = (),
    reorder: bool = False,
    allow_dummies: bool = False,
    max_states: int = 10_000,
    layout: tuple[AnchorLayout, ...] | None = None,
    position_tolerance: float = 1e-8,
    angle_tolerance: float = 1e-6,
) -> Molecule: ...


@overload
def to_zmatrix(
    molecule: None = None,
    *,
    frame: Literal["canonical", "preserve"],
    requested: tuple[NamedCoordinate, ...] = (),
    reorder: bool = False,
    allow_dummies: bool = False,
    max_states: int = 10_000,
    layout: tuple[AnchorLayout, ...] | None = None,
    position_tolerance: float = 1e-8,
    angle_tolerance: float = 1e-6,
) -> Callable[[Molecule], Molecule]: ...


def to_zmatrix(  # noqa: PLR0913 - Independent conversion choices are explicit keyword-only controls.
    molecule: Molecule | None = None,
    *,
    frame: Literal["canonical", "preserve"],
    requested: tuple[NamedCoordinate, ...] = (),
    reorder: bool = False,
    allow_dummies: bool = False,
    max_states: int = 10_000,
    layout: tuple[AnchorLayout, ...] | None = None,
    position_tolerance: float = 1e-8,
    angle_tolerance: float = 1e-6,
) -> Molecule | Callable[[Molecule], Molecule]:
    """Return verified internal coordinates, or a pure conversion pipeline stage.

    Requested coordinates become named variables. Atom reordering and dummy
    insertion require separate opt-ins. An explicit layout bypasses search.
    """
    settings = ReconstructionPolicy(
        frame=frame,
        position_tolerance=position_tolerance,
        angle_tolerance=angle_tolerance,
    )

    def apply(source: Molecule) -> Molecule:
        points = positions(source)
        if not points:
            raise ValueError("Coordinate conversion requires at least one atom")
        _validate_requests(source, requested, points)
        cartesian = with_positions(source, points)
        if layout is not None:
            result = _explicit(cartesian, requested, layout, points, reorder=reorder)
        else:
            budget = _Budget(max_states)
            try:
                result = _automatic(
                    cartesian, requested, points, reorder=reorder, budget=budget
                )
            except DegenerateGeometryError:
                if not allow_dummies:
                    raise
                augmented = _add_dummy(cartesian, points)
                result = _automatic(
                    augmented,
                    requested,
                    positions(augmented),
                    reorder=reorder,
                    budget=budget,
                )
        result_points = _verify(
            points,
            result,
            settings=settings,
            requested=requested,
        )
        return reconcile_symmetry(result, points=result_points)

    return apply if molecule is None else apply(molecule)
