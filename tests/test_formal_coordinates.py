"""Check scan intent against prepared and constrained future geometries."""

import os
import subprocess
from math import pi
from pathlib import Path

import pytest
import z3
from pydantic import TypeAdapter, ValidationError

from psi4_parser.builder import (
    Angle,
    Atom,
    Cartesian,
    Coordinate,
    ElectronicState,
    Length,
    Molecule,
    Nucleus,
    angle,
    angstrom,
    bohr,
    bound,
    cartesian,
    degrees,
    dihedral,
    distance,
    freeze,
    molecule,
    out_of_plane,
    radians,
)
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    CoordinateRange,
    CoordinateValue,
    Model,
    Plan,
    SameModel,
    ScientificRequest,
    StudyCase,
    export_bundle,
    finite_study,
    propose,
    verify,
)


def _hydrogen() -> Molecule:
    return Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )


def _plan(
    geometry: Molecule,
    requirement: CoordinateValue | CoordinateRange,
    *preceding: Calculation,
) -> Plan:
    return Plan(
        molecules=(molecule("geometry", geometry),),
        steps=(
            *preceding,
            Calculation(
                id="energy",
                driver="energy",
                geometry="geometry",
                model=Model(method="scf", basis="sto-3g", reference="rhf"),
            ),
        ),
        requirements=(requirement,),
    )


def test_prepared_scan_point_must_meet_its_independent_coordinate_target() -> None:
    """Reject an incorrect point even when the request's own geometry is consistent."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    plan = Plan(
        molecules=(molecule("h2", geometry),),
        steps=(
            Calculation(
                id="energy",
                driver="energy",
                geometry="h2",
                model=Model(method="scf", basis="sto-3g", reference="rhf"),
            ),
        ),
        requirements=(
            CoordinateValue(
                geometry="h2",
                coordinate=distance("a1", "a2"),
                value=angstrom(1.1),
                tolerance=angstrom(1e-8),
            ),
        ),
    )

    report = verify(plan)

    assert report.status == "violated"
    assert report.obligations[0].counterexample


@pytest.mark.parametrize(
    ("coordinate", "target"),
    [
        (distance("a1", "a2"), bohr(2.0)),
        (angle("a1", "a2", "a3"), radians(pi / 2)),
        (dihedral("a1", "a2", "a3", "a4"), degrees(450)),
        (dihedral("a4", "a3", "a2", "a1"), degrees(90)),
        (cartesian("a4", "z"), bohr(2.0)),
    ],
)
def test_coordinate_targets_retain_units_order_and_periodicity(
    coordinate: Coordinate,
    target: Length | Angle,
) -> None:
    """Use independent right-angle geometry to check conversions and signed torsions.

    Args:
        coordinate: Stable atoms and order to measure.
        target: Independently specified target with explicit units.
    """
    geometry = Molecule(
        atoms=tuple(
            Atom(
                id=f"a{index}",
                nucleus=Nucleus(label="H"),
                coordinates=Cartesian(x=x, y=y, z=z, unit="bohr"),
            )
            for index, (x, y, z) in enumerate(
                ((0.0, 2.0, 0.0), (0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 0.0, 2.0)), 1
            )
        ),
        state=ElectronicState(charge=0, multiplicity=1),
        fixed_com=True,
        fixed_orientation=True,
    )
    tolerance = angstrom(1e-8) if isinstance(target, Length) else degrees(1e-8)
    requirement = CoordinateValue(
        geometry="geometry", coordinate=coordinate, value=target, tolerance=tolerance
    )

    report = verify(_plan(geometry, requirement))

    assert report.status == "proved"
    solver = z3.Solver()
    solver.from_string(report.obligations[0].smt2)
    assert solver.check() == z3.unsat
    assert report.obligations[0].proof
    assert any("floating-point geometry" in item for item in report.assumptions)


def test_signed_out_of_plane_measurement_uses_the_declared_plane_order() -> None:
    """Keep signed plane orientation separate from an unsigned ordinary bond angle."""
    geometry = Molecule.from_xyz(
        "4\nPlane\nH 1 0 1\nH 0 0 0\nH 1 0 0\nH 0 1 0\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    requirement = CoordinateValue(
        geometry="geometry",
        coordinate=out_of_plane("a1", "a2", "a3", "a4"),
        value=degrees(45),
        tolerance=degrees(1e-8),
    )
    reversed_plane = CoordinateValue(
        geometry="geometry",
        coordinate=out_of_plane("a1", "a2", "a4", "a3"),
        value=degrees(45),
        tolerance=degrees(1e-8),
    )

    assert verify(_plan(geometry, requirement)).status == "proved"
    assert verify(_plan(geometry, reversed_plane)).status == "violated"


def test_dihedral_interval_can_cross_the_signed_angle_branch_cut() -> None:
    """Treat 170 to 190 as a continuous requested arc containing either sign of 180."""
    geometry = Molecule.from_xyz(
        "4\nPlane\nH 0 1 0\nH 0 0 0\nH 1 0 0\nH 1 -1 0\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    requirement = CoordinateRange(
        geometry="geometry",
        coordinate=dihedral("a1", "a2", "a3", "a4"),
        lower=degrees(170),
        upper=degrees(190),
        tolerance=degrees(1e-8),
    )

    assert verify(_plan(geometry, requirement)).status == "proved"


@pytest.mark.parametrize(
    ("constrained", "expected"), [(False, "unknown"), (True, "proved")]
)
def test_future_geometry_needs_an_enforced_coordinate_contract(
    constrained: bool, expected: str
) -> None:
    """Never treat a future optimized geometry's placeholder input as measured output.

    Args:
        constrained: Whether the coordinate is explicitly frozen.
        expected: Expected construction-level coordinate conclusion.
    """
    opt = Calculation(
        id="relaxed",
        driver="optimize",
        geometry="geometry",
        model=Model(method="scf", basis="sto-3g", reference="rhf"),
        constraints=(freeze(distance("a2", "a1")),) if constrained else (),
    )
    requirement = CoordinateValue(
        geometry="relaxed",
        coordinate=distance("a1", "a2"),
        value=angstrom(0.85),
        tolerance=angstrom(1e-8),
    )

    assert verify(_plan(_hydrogen(), requirement, opt)).status == expected


def test_a_bounded_future_coordinate_must_fit_the_entire_requested_interval() -> None:
    """Find a permitted violating value outside the requested interval."""
    coordinate = distance("a1", "a2")
    opt = Calculation(
        id="relaxed",
        driver="optimize",
        geometry="geometry",
        model=Model(method="scf", basis="sto-3g", reference="rhf"),
        constraints=(bound(coordinate, angstrom(0.8), angstrom(0.9)),),
    )
    enclosing = CoordinateRange(
        geometry="relaxed",
        coordinate=coordinate,
        lower=angstrom(0.75),
        upper=angstrom(0.95),
        tolerance=angstrom(0),
    )
    narrow = CoordinateValue(
        geometry="relaxed",
        coordinate=coordinate,
        value=angstrom(0.85),
        tolerance=angstrom(0.01),
    )

    accepted = verify(_plan(_hydrogen(), enclosing, opt))
    rejected = verify(_plan(_hydrogen(), narrow, opt))

    assert accepted.status == "proved"
    assert rejected.status == "violated"
    solver = z3.Solver()
    solver.from_string(rejected.obligations[0].smt2)
    assert solver.check() == z3.sat
    assert rejected.obligations[0].counterexample


def test_freezing_after_an_unconstrained_optimization_does_not_recover_a_value() -> (
    None
):
    """Propagate unknown initial values across later frozen-coordinate histories."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    first = Calculation(id="first", driver="optimize", geometry="geometry", model=model)
    second = Calculation(
        id="second",
        driver="optimize",
        geometry="first",
        model=model,
        constraints=(freeze(distance("a1", "a2")),),
    )
    requirement = CoordinateValue(
        geometry="second",
        coordinate=distance("a1", "a2"),
        value=angstrom(0.85),
        tolerance=angstrom(1e-8),
    )

    assert verify(_plan(_hydrogen(), requirement, first, second)).status == "unknown"


def test_absolute_cartesian_coordinates_require_a_fixed_frame() -> None:
    """Avoid claims about an absolute position that Psi4 is free to rotate or center."""
    requirement = CoordinateValue(
        geometry="geometry",
        coordinate=cartesian("a2", "z"),
        value=angstrom(0.85),
        tolerance=angstrom(1e-8),
    )

    assert verify(_plan(_hydrogen(), requirement)).status == "unknown"


def test_undefined_torsions_remain_unknown() -> None:
    """Do not silently substitute an angle for coincident or collinear references."""
    geometry = Molecule.from_xyz(
        "4\nLine\nH 0 0 0\nH 1 0 0\nH 2 0 0\nH 3 0 0\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    requirement = CoordinateValue(
        geometry="geometry",
        coordinate=dihedral("a1", "a2", "a3", "a4"),
        value=degrees(0),
        tolerance=degrees(1e-8),
    )

    report = verify(_plan(geometry, requirement))

    assert report.status == "unknown"
    assert "undefined" in report.obligations[0].message


def test_case_specific_coordinate_intent_cannot_be_omitted_from_the_plan(
    formal_profile: CapabilityCatalog,
    tmp_path: Path,
) -> None:
    """Derive independent case targets even after plan assertions are removed.

    Args:
        formal_profile: Synthetic method and basis evidence.
        tmp_path: Fresh construction-bundle parent.
    """
    template = ScientificRequest(
        molecules=(molecule("h2", _hydrogen()),),
        goals=(
            CalculationGoal(
                id="energy",
                driver="energy",
                geometry="h2",
                models=(Model(method="scf", basis="sto-3g", reference="rhf"),),
            ),
        ),
    )
    target = CoordinateValue(
        geometry="h2",
        coordinate=distance("a1", "a2"),
        value=angstrom(0.85),
        tolerance=angstrom(1e-8),
    )
    request = finite_study(
        template,
        (StudyCase(id="point", molecules=template.molecules, relations=(target,)),),
    )
    assert ScientificRequest.model_validate_json(request.model_dump_json()) == request
    proposed = propose(request, formal_profile)
    assert proposed.plan is not None

    exported = export_bundle(
        proposed.plan, request, formal_profile, tmp_path / "bundle"
    )

    assert (
        "point:h2" in (Path(exported.directory) / "scientific-request.json").read_text()
    )
    assert any(
        "Coordinate measurements" in item for item in exported.manifest.assumptions
    )
    wrong = CoordinateValue(
        geometry="point:h2",
        coordinate=target.coordinate,
        value=angstrom(1.1),
        tolerance=target.tolerance,
    )
    wrong_request = ScientificRequest(
        molecules=request.molecules, goals=request.goals, relations=(wrong,)
    )
    weakened = Plan(
        molecules=proposed.plan.molecules,
        steps=proposed.plan.steps,
        requirements=(SameModel(calculations=("point:energy", "point:energy")),),
    )
    rejected = verify(weakened, request=wrong_request, catalog=formal_profile)
    assert rejected.status == "violated"
    assert rejected.obligations[-1].path[0] == "request"


def test_coordinate_schemas_reject_incompatible_dimensions_and_axes() -> None:
    """Reject invalid requirements at their public construction boundary."""
    with pytest.raises(ValidationError, match="dimensions"):
        CoordinateValue(
            geometry="g",
            coordinate=distance("a", "b"),
            value=degrees(90),
            tolerance=degrees(1e-8),
        )
    with pytest.raises(ValidationError, match="one axis"):
        CoordinateValue(
            geometry="g",
            coordinate=cartesian("a", "xyz"),
            value=angstrom(1),
            tolerance=angstrom(1e-8),
        )
    with pytest.raises(ValidationError, match="nonnegative"):
        CoordinateValue(
            geometry="g",
            coordinate=distance("a", "b"),
            value=angstrom(1),
            tolerance=angstrom(-1),
        )


def test_inconsistent_coordinate_domains_never_produce_a_vacuous_proof() -> None:
    """Keep an empty optimizer interval from establishing arbitrary target ranges."""
    coordinate = distance("a1", "a2")
    opt = Calculation(
        id="relaxed",
        driver="optimize",
        geometry="geometry",
        model=Model(method="scf", basis="sto-3g", reference="rhf"),
        constraints=(
            bound(coordinate, angstrom(0.8), angstrom(0.9)),
            bound(coordinate, angstrom(1.0), angstrom(1.1)),
        ),
    )
    requirement = CoordinateRange(
        geometry="relaxed",
        coordinate=coordinate,
        lower=angstrom(0),
        upper=angstrom(2),
        tolerance=angstrom(0),
    )

    report = verify(_plan(_hydrogen(), requirement, opt))

    assert report.status == "unknown"
    assert "inconsistent" in report.obligations[0].message
    assert not report.obligations[0].proof


def test_future_dihedral_branch_tracking_requires_additional_evidence() -> None:
    """Retain a located explanation when optimizer bounds cross an unaudited branch."""
    geometry = Molecule.from_xyz(
        "4\nPlane\nH 0 1 0\nH 0 0 0\nH 1 0 0\nH 1 -1 0\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    coordinate = dihedral("a1", "a2", "a3", "a4")
    opt = Calculation(
        id="relaxed",
        driver="optimize",
        geometry="geometry",
        model=Model(method="scf", basis="sto-3g", reference="rhf"),
        constraints=(bound(coordinate, degrees(170), degrees(190)),),
    )
    requirement = CoordinateRange(
        geometry="relaxed",
        coordinate=coordinate,
        lower=degrees(160),
        upper=degrees(200),
        tolerance=degrees(0),
    )

    report = verify(_plan(geometry, requirement, opt))

    assert report.status == "unknown"
    assert "optimizer branch contract" in report.obligations[0].message


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for Optking convention checks",
)
def test_coordinate_conventions_agree_with_native_optimizer_helpers(
    tmp_path: Path,
) -> None:
    """Compare measurement conventions without running a quantum chemistry driver.

    Args:
        tmp_path: Isolated native interpreter working directory.
    """
    executable = os.environ["PSI4_PYTHON"]
    program = """import json, math
import numpy as np
from optking import v3d
a,b,c,d = np.array([[0.,1.,0.],[0.,0.,0.],[1.,0.,0.],[1.,0.,1.]])
e,f,g,h = np.array([[1.,0.,1.],[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
print(json.dumps([v3d.dist(a,b), math.degrees(v3d.angle(a,b,c)),
                  math.degrees(v3d.tors(a,b,c,d,[0,1,2,3])),
                  math.degrees(v3d.oofp(e,f,g,h))]))
"""
    completed = subprocess.run(  # noqa: S603 - Explicit configured interpreter; fixed geometry-helper program.
        [executable, "-c", program],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    values = TypeAdapter(tuple[float, ...]).validate_json(completed.stdout)
    assert values == pytest.approx((1.0, 90.0, 90.0, 45.0))
