"""Check case coverage and independent histories in finite studies."""

from psi4_parser.builder import (
    ElectronicState,
    Molecule,
    assemble_fragments,
    distance,
    freeze,
    molecule,
)
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    ExpressionGoal,
    FragmentStudy,
    GoalTerm,
    Model,
    Plan,
    SameModel,
    ScientificRequest,
    StudyCase,
    finite_study,
    fragment_expansion,
    propose,
    verify,
)


def test_finite_cases_have_independent_optimization_histories(
    formal_profile: CapabilityCatalog,
) -> None:
    """Compose optimization and frequencies at two independently supplied structures.

    Args:
        formal_profile: Synthetic capability declarations.
    """
    first = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .75\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    second = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    template = ScientificRequest(
        molecules=(molecule("h2", first),),
        goals=(
            CalculationGoal(
                id="opt", driver="optimize", geometry="h2", models=(model,)
            ),
            CalculationGoal(
                id="freq", driver="frequency", geometry="opt", models=(model,)
            ),
        ),
    )
    request = finite_study(
        template,
        (
            StudyCase(id="short", molecules=(molecule("h2", first),)),
            StudyCase(id="long", molecules=(molecule("h2", second),)),
        ),
    )

    proposal = propose(request, formal_profile)

    assert proposal.status == "constructed"
    assert proposal.plan is not None
    assert proposal.report is not None
    assert len(proposal.report.coverage) == 4
    calculations = [
        step for step in proposal.plan.steps if isinstance(step, Calculation)
    ]
    assert [step.geometry for step in calculations] == [
        "short:h2",
        "short:opt",
        "long:h2",
        "long:opt",
    ]
    assert [
        item.id for item in proposal.report.geometries if not item.coordinates_known
    ] == ["short:opt", "long:opt"]

    damaged = Plan(
        molecules=request.molecules,
        steps=proposal.plan.steps[:-1],
        requirements=(SameModel(calculations=("short:opt", "short:opt")),),
    )
    assert verify(damaged, request=request, catalog=formal_profile).status == "violated"


def test_a_finite_constrained_optimization_and_counterpoise_study_composes(
    formal_profile: CapabilityCatalog,
) -> None:
    """Check cases, constraints, future geometries, ghosts, and formulas together.

    Args:
        formal_profile: Test support for constraints and ghost centers.
    """
    state = ElectronicState(charge=0, multiplicity=1)
    a = Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .75\n", state=state)
    b = Molecule.from_xyz("2\nH2\nH 3 0 0\nH 3 0 .75\n", state=state)
    assembly = assemble_fragments(("A", a), ("B", b), state=state)
    parent = Molecule(
        atoms=assembly.atoms,
        fragments=assembly.fragments,
        state=state,
        fixed_com=True,
        fixed_orientation=True,
    )
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    expansion = fragment_expansion(
        FragmentStudy(
            id="cp", geometry="opt", fragments=parent.fragments, models=(model,)
        )
    )
    optimization = CalculationGoal(
        id="opt",
        driver="optimize",
        geometry="cluster",
        models=(model,),
        constraints=(freeze(distance("A:a1", "B:a1")),),
    )
    template = ScientificRequest(
        molecules=(molecule("cluster", parent),),
        goals=(optimization, *expansion.goals),
        relations=expansion.relations,
    )
    request = finite_study(
        template,
        (
            StudyCase(id="first", molecules=template.molecules),
            StudyCase(id="second", molecules=template.molecules),
        ),
    )

    proposal = propose(request, formal_profile)

    assert proposal.status == "constructed"
    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert len(proposal.report.coverage) == 16
    subsystems = [
        item
        for item in proposal.report.geometries
        if item.producer and "subsystem" in item.id
    ]
    assert len(subsystems) == 6
    assert all(not item.coordinates_known for item in subsystems)
    assert {item.source for item in subsystems} == {"first:opt", "second:opt"}

    final = request.goals[-1]
    assert isinstance(final, ExpressionGoal)
    first_term = final.terms[0]
    assert isinstance(first_term.coefficient, int)
    wrong_formula = ExpressionGoal(
        id=final.id,
        quantity=final.quantity,
        terms=(
            GoalTerm(goal=first_term.goal, coefficient=first_term.coefficient + 2),
            *final.terms[1:],
        ),
    )
    wrong_request = ScientificRequest(
        molecules=request.molecules,
        goals=(*request.goals[:-1], wrong_formula),
        relations=request.relations,
    )

    rejected = propose(wrong_request, formal_profile)

    assert rejected.plan is None
    assert rejected.report is not None
    assert rejected.report.status == "violated"
    assert any(
        issue.code == "interaction_semantics" for issue in rejected.report.diagnostics
    )
