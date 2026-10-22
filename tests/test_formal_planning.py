"""Construct plans from permitted choices while preserving scientific intent."""

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    Model,
    SameModel,
    ScientificRequest,
    SearchLimits,
    propose,
)


def request_with_alternatives() -> ScientificRequest:
    """Return one energy goal whose second explicitly allowed model is supported."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="energy",
                driver="energy",
                geometry="h2",
                models=(
                    Model(method="unlisted", basis="sto-3g", reference="rhf"),
                    Model(method="scf", basis="sto-3g", reference="rhf"),
                ),
            ),
        ),
    )


def test_plan_construction_selects_an_explicitly_permitted_alternative(
    formal_profile: CapabilityCatalog,
) -> None:
    """Find a supported alternative without changing the independent request.

    Args:
        formal_profile: Synthetic capability declarations.
    """
    request = request_with_alternatives()

    proposal = propose(request, formal_profile)

    assert proposal.status == "constructed"
    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    step = proposal.plan.steps[0]
    assert isinstance(step, Calculation)
    assert step.model.method == "scf"
    assert proposal.choices[0].preference_rank == 1
    assert request.goals[0] == request_with_alternatives().goals[0]


def test_a_search_bound_is_not_a_proof_of_impossibility(
    formal_profile: CapabilityCatalog,
) -> None:
    """Report exhaustion when a supported alternative lies beyond the search bound.

    Args:
        formal_profile: Synthetic capability declarations.
    """
    proposal = propose(
        request_with_alternatives(),
        formal_profile,
        limits=SearchLimits(max_candidates=1),
    )

    assert proposal.status == "exhausted"
    assert proposal.plan is None
    assert proposal.attempts == 1


def test_conflicting_fixed_models_explain_the_finite_conflict(
    formal_profile: CapabilityCatalog,
) -> None:
    """Explain an inconsistent model relationship without changing fixed chemistry.

    Args:
        formal_profile: Synthetic capability declarations.
    """
    original = request_with_alternatives()
    first = Model(method="scf", basis="sto-3g", reference="rhf")
    second = Model(method="scf", basis="sto-3g", reference="rhf", frozen_core=True)
    request = ScientificRequest(
        molecules=original.molecules,
        goals=(
            CalculationGoal(id="a", driver="energy", geometry="h2", models=(first,)),
            CalculationGoal(id="b", driver="energy", geometry="h2", models=(second,)),
        ),
        relations=(SameModel(calculations=("a", "b")),),
    )

    proposal = propose(request, formal_profile)

    assert proposal.status == "no_candidate"
    assert proposal.attempts == 0
    assert proposal.diagnostics[0].code == "finite_choices"
    assert proposal.plan is None
