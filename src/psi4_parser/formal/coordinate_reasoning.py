"""Propagate coordinate domains from inputs and declared optimizer constraints."""

from dataclasses import dataclass
from math import asin, degrees, isfinite

from psi4_parser.builder import Coordinate, Molecule
from psi4_parser.builder import _vectors as vectors
from psi4_parser.builder.constraints import Bounded, Frozen
from psi4_parser.builder.geometry import positions
from psi4_parser.formal.coordinate_models import coordinate_number
from psi4_parser.formal.models import Calculation, Plan, Subsystem

_HALF_TURN = 180.0


@dataclass(frozen=True)
class CoordinateDomain:
    """Retain a measured value or guaranteed interval in angstroms or degrees.

    Attributes:
        lower: Inclusive lower bound; null when no domain can be established.
        upper: Inclusive upper bound; null together with lower.
        message: Source of the domain or reason it remains unknown.
    """

    lower: float | None
    upper: float | None
    message: str


def _measurement(molecule: Molecule, coordinate: Coordinate) -> float:
    points = positions(molecule)
    selected = tuple(points[name] for name in coordinate.atoms)
    match coordinate.kind:
        case "distance":
            return vectors.separation(*selected)
        case "angle":
            return vectors.bend(*selected)
        case "dihedral":
            return vectors.torsion(*selected)
        case "cartesian":
            return selected[0]["xyz".index(coordinate.axes)]
        case "out_of_plane":
            a, b, c, d = selected
            normal = vectors.unit(vectors.cross(vectors.sub(c, b), vectors.sub(d, b)))
            sine = vectors.dot(vectors.unit(vectors.sub(a, b)), normal)
            return degrees(asin(max(-1.0, min(1.0, sine))))


def _input_domain(molecule: Molecule, coordinate: Coordinate) -> CoordinateDomain:
    usable = {atom.id for atom in molecule.atoms if not atom.nucleus.dummy}
    if not set(coordinate.atoms) <= usable:
        return CoordinateDomain(
            None, None, "Coordinate atoms must exist and be non-dummy centers."
        )
    if coordinate.kind == "cartesian" and not (
        molecule.fixed_com and molecule.fixed_orientation
    ):
        return CoordinateDomain(
            None,
            None,
            "Absolute Cartesian requirements need fixed_com and fixed_orientation.",
        )
    try:
        value = _measurement(molecule, coordinate)
    except ValueError as error:
        return CoordinateDomain(None, None, f"Coordinate is undefined: {error}")
    if not isfinite(value):
        return CoordinateDomain(None, None, "Coordinate measurement is not finite.")
    return CoordinateDomain(value, value, "Measured from resolved input coordinates.")


def _same_coordinate(requested: Coordinate, constrained: Coordinate) -> bool:
    if requested.kind != constrained.kind:
        return False
    if requested.kind == "cartesian":
        return (
            requested.atoms == constrained.atoms and requested.axes in constrained.axes
        )
    if requested.atoms == constrained.atoms:
        return True
    return (
        requested.kind in {"distance", "angle", "dihedral"}
        and requested.atoms == constrained.atoms[::-1]
    )


def _bound_domain(constraint: Bounded) -> CoordinateDomain:
    lower, upper = (
        coordinate_number(constraint.lower),
        coordinate_number(constraint.upper),
    )
    if not (isfinite(lower) and isfinite(upper)):
        return CoordinateDomain(
            None, None, "Converted optimizer bounds are not finite."
        )
    if constraint.coordinate.kind == "dihedral" and not (
        -_HALF_TURN <= lower < upper <= _HALF_TURN
    ):
        return CoordinateDomain(
            None,
            None,
            "Future dihedral bounds outside [-180, 180] need a checked "
            "optimizer branch contract.",
        )
    return CoordinateDomain(
        lower,
        upper,
        "Declared optimizer interval, conditional on successful optimization.",
    )


def _optimized_domain(
    step: Calculation, coordinate: Coordinate, source: CoordinateDomain
) -> CoordinateDomain:
    candidates = tuple(
        source if isinstance(item, Frozen) else _bound_domain(item)
        for item in step.constraints
        if _same_coordinate(coordinate, item.coordinate)
    )
    known = tuple(
        item for item in candidates if item.lower is not None and item.upper is not None
    )
    if not known:
        if candidates:
            messages: dict[str, None] = {item.message: None for item in candidates}
            return CoordinateDomain(None, None, "; ".join(messages))
        return CoordinateDomain(
            None,
            None,
            "No established constraint for this coordinate on future geometry "
            f"{step.id}.",
        )
    lower = max(item.lower for item in known if item.lower is not None)
    upper = min(item.upper for item in known if item.upper is not None)
    if lower > upper:
        return CoordinateDomain(
            None,
            None,
            "Coordinate constraint premises are inconsistent; no proof is allowed.",
        )
    return CoordinateDomain(
        lower,
        upper,
        f"Coordinate domain retained by constraints on optimization {step.id}.",
    )


class CoordinateReasoner:
    """Reuse coordinate domains across requirements without evaluating future jobs.

    Args:
        plan: Structurally checked plan, in geometry dependency order.
    """

    def __init__(self, plan: Plan) -> None:
        """Retain a checked plan and start an empty coordinate-domain cache."""
        self._plan = plan
        self._cache: dict[str, dict[str, CoordinateDomain]] = {}

    def domain(self, geometry: str, coordinate: Coordinate) -> CoordinateDomain:
        """Return input measurements or conservative optimizer-derived bounds.

        Unconstrained future coordinates remain unknown. A subsystem preserves
        its parent's coordinates; this does not assert a new numerical geometry.
        """
        key = coordinate.model_dump_json()
        if key not in self._cache:
            domains = {
                item.name: _input_domain(item.geometry, coordinate)
                for item in self._plan.molecules
            }
            for step in self._plan.steps:
                if isinstance(step, Subsystem):
                    domains[step.id] = domains[step.geometry]
                elif isinstance(step, Calculation) and step.driver == "optimize":
                    domains[step.id] = _optimized_domain(
                        step, coordinate, domains[step.geometry]
                    )
            self._cache[key] = domains
        return self._cache[key][geometry]
