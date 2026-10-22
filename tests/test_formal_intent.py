"""Require scientific intent coverage independently of caller-written assertions."""

import pytest

from psi4_parser.builder import ElectronicState, Molecule, angstrom, distance, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    CoordinateRange,
    CoordinateValue,
    EnergyFormula,
    EnergyTerm,
    Model,
    Plan,
    SameGeometry,
    SameModel,
    ScientificRequest,
    UsesGeometry,
    propose,
    verify,
)
from psi4_parser.formal.models import Requirement


def refinement_request() -> ScientificRequest:
    """Return an optimization followed by a frequency calculation at that geometry."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="refine", driver="optimize", geometry="h2", models=(model,)
            ),
            CalculationGoal(
                id="vibrations", driver="frequency", geometry="refine", models=(model,)
            ),
        ),
    )


def test_a_trivial_assertion_cannot_cover_omitted_scientific_work() -> None:
    """Reject a missing frequency calculation even when the supplied assertion holds."""
    request = refinement_request()
    goal = request.goals[0]
    assert isinstance(goal, CalculationGoal)
    step = Calculation(
        id="opt",
        driver="optimize",
        geometry="h2",
        model=goal.models[0],
        satisfies=("refine",),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(step,),
        requirements=(SameModel(calculations=("opt", "opt")),),
    )

    assert verify(plan).status == "proved"
    report = verify(plan, request=request)

    assert report.status == "violated"
    assert not report.request_complete
    assert report.coverage[1].goal == "vibrations"
    assert report.coverage[1].status == "missing"


def test_request_derives_the_optimized_geometry_requirement(
    formal_profile: CapabilityCatalog,
) -> None:
    """Derive the geometry dependency from intent.

    Args:
        formal_profile: Synthetic method and basis support for the test request.
    """
    request = refinement_request()
    goal = request.goals[0]
    assert isinstance(goal, CalculationGoal)
    model = goal.models[0]
    first = Calculation(
        id="opt", driver="optimize", geometry="h2", model=model, satisfies=("refine",)
    )
    for geometry, expected in (("opt", "proved"), ("h2", "violated")):
        plan = Plan(
            molecules=request.molecules,
            steps=(
                first,
                Calculation(
                    id="freq",
                    driver="frequency",
                    geometry=geometry,
                    model=model,
                    satisfies=("vibrations",),
                ),
            ),
            requirements=(SameModel(calculations=("opt", "opt")),),
        )

        report = verify(plan, request=request, catalog=formal_profile)

        assert report.status == expected
        assert report.scope == "scientific_request"
        assert report.scope == "scientific_request"
        assert report.request_complete == (expected == "proved")


def test_model_settings_cannot_be_weakened_to_satisfy_a_request() -> None:
    """Reject a cheaper basis that the independent request did not permit."""
    request = refinement_request()
    step = Calculation(
        id="opt",
        driver="optimize",
        geometry="h2",
        model=Model(method="scf", basis="6-31g", reference="rhf"),
        satisfies=("refine",),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(step,),
        requirements=(SameModel(calculations=("opt", "opt")),),
    )

    report = verify(plan, request=request)

    assert report.status == "violated"
    assert any(
        item.code == "goal_contract" and item.path[-1] == "model"
        for item in report.diagnostics
    )


def test_shared_contracts_keep_unspecified_algorithm_support_unknown() -> None:
    """Use built-in rules without inventing an undeclared integral algorithm."""
    original = refinement_request()
    goal = original.goals[0]
    assert isinstance(goal, CalculationGoal)
    request = ScientificRequest(molecules=original.molecules, goals=(goal,))
    step = Calculation(
        id="opt",
        driver="optimize",
        geometry="h2",
        model=goal.models[0],
        satisfies=("refine",),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(step,),
        requirements=(SameModel(calculations=("opt", "opt")),),
    )

    report = verify(plan, request=request)

    assert report.status == "unknown"
    assert not report.request_complete
    assert any(item.code == "capability_condition" for item in report.diagnostics)


@pytest.mark.parametrize(
    ("relation", "suffix"),
    [
        (SameModel(calculations=("refine", "h2")), ("calculations", 1)),
        (SameGeometry(calculations=("refine", "missing")), ("calculations", 1)),
        (UsesGeometry(calculation="h2", geometry="refine"), ("calculation",)),
        (UsesGeometry(calculation="vibrations", geometry="vibrations"), ("geometry",)),
        (
            EnergyFormula(
                result="h2", terms=(EnergyTerm(result="vibrations", coefficient=1),)
            ),
            ("result",),
        ),
        (
            EnergyFormula(
                result="vibrations", terms=(EnergyTerm(result="h2", coefficient=1),)
            ),
            ("terms", 0, "result"),
        ),
        (
            CoordinateValue(
                geometry="vibrations",
                coordinate=distance("H1", "H2"),
                value=angstrom(0.85),
                tolerance=angstrom(0.001),
            ),
            ("geometry",),
        ),
        (
            CoordinateRange(
                geometry="missing",
                coordinate=distance("H1", "H2"),
                lower=angstrom(0.8),
                upper=angstrom(0.9),
                tolerance=angstrom(0.001),
            ),
            ("geometry",),
        ),
    ],
)
def test_invalid_request_relations_are_located_before_candidate_search(
    formal_profile: CapabilityCatalog,
    relation: Requirement,
    suffix: tuple[str | int, ...],
) -> None:
    """Locate unknown or wrong-kind references in the independent request.

    Args:
        formal_profile: Synthetic support for the otherwise valid calculations.
        relation: Relationship containing one invalid reference.
        suffix: Exact field path within the supplied relationship.
    """
    original = refinement_request()
    accepted = propose(original, formal_profile)
    assert accepted.plan is not None
    request = ScientificRequest(
        molecules=original.molecules, goals=original.goals, relations=(relation,)
    )

    proposed = propose(request, formal_profile)
    checked = verify(accepted.plan, request=request, catalog=formal_profile)

    assert proposed.status == "invalid"
    assert proposed.attempts == 0
    assert checked.status == "invalid"
    assert not checked.request_complete
    path = ("request", "relations", 0, *suffix)
    assert any(item.path == path for item in proposed.diagnostics)
    assert any(item.path == path for item in checked.diagnostics)
