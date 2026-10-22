"""Preserve scientific independence while permitting checked calculation reuse."""

import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser.builder import ElectronicState, Molecule, assemble_fragments, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    ExpressionGoal,
    GoalTerm,
    Model,
    Plan,
    PlanningPreferences,
    ProductGoal,
    QuantityType,
    SameGeometry,
    SameModel,
    ScientificRequest,
    SearchLimits,
    Setting,
    StudyCase,
    SubsystemGoal,
    ThermalConditions,
    VibrationalAnalysis,
    export_bundle,
    finite_study,
    load_catalog,
    product_quantity,
    propose,
    render,
    verify,
)
from psi4_parser.formal.capabilities import DerivativeRoute
from psi4_parser.formal.reuse import ReusePreference
from psi4_parser.formal.science import Driver


@pytest.mark.parametrize("groups", [(None, None), (None, "shared"), ("one", "two")])
def test_one_call_cannot_replace_two_independent_calculation_goals(
    formal_profile: CapabilityCatalog,
    groups: tuple[str | None, str | None],
) -> None:
    """Reject a shared call unless the independent request permits sharing.

    Args:
        formal_profile: Synthetic support for the declared model.
        groups: Missing or mismatched sharing permissions.
    """
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="first",
                driver="energy",
                geometry="h2",
                models=(model,),
                reuse_group=groups[0],
            ),
            CalculationGoal(
                id="second",
                driver="energy",
                geometry="h2",
                models=(model,),
                reuse_group=groups[1],
            ),
        ),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(
            Calculation(
                id="shared",
                driver="energy",
                geometry="h2",
                model=model,
                satisfies=("first", "second"),
            ),
        ),
        requirements=(SameModel(calculations=("shared", "shared")),),
    )

    report = verify(plan, request=request, catalog=formal_profile)

    assert report.status == "violated"
    assert not report.request_complete
    assert any(issue.code == "unauthorized_reuse" for issue in report.diagnostics)


def _model(basis: str = "sto-3g") -> Model:
    return Model(
        method="hf",
        basis=basis,
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )


def _pair(
    driver: Driver = "energy", *, group: str | None = "shared"
) -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=tuple(
            CalculationGoal(
                id=name,
                driver=driver,
                geometry="h2",
                models=(_model(),),
                properties=("DIPOLE",) if driver == "properties" else (),
                reuse_group=group,
            )
            for name in ("first", "second")
        ),
    )


@pytest.mark.parametrize(
    "driver", ["energy", "optimize", "gradient", "hessian", "frequency", "properties"]
)
def test_permitted_identical_calls_share_one_verified_implementation(
    driver: Driver,
) -> None:
    """Cover both independent goals with one explicitly permitted call.

    Args:
        driver: Native operation whose complete inputs match.
    """
    proposal = propose(_pair(driver), load_catalog("psi4"))

    assert proposal.status == "constructed", proposal.report
    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 1
    assert proposal.reuses[0].calculation == "first"
    assert proposal.reuses[0].goals == ("first", "second")
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert proposal.report.capability_status == "supported"
    assert [entry.steps for entry in proposal.report.coverage] == [
        ("first",),
        ("first",),
    ]


def test_a_preference_cannot_grant_permission_to_merge_independent_goals() -> None:
    """Keep two calls when the scientific request has no reuse group."""
    proposal = propose(
        _pair(group=None),
        load_catalog("psi4"),
        preferences=PlanningPreferences(calculation_reuse="prefer"),
    )

    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 2
    assert proposal.reuses == ()


def test_reuse_does_not_treat_equal_coordinate_copies_as_shared_provenance() -> None:
    """Keep separate calls for independently declared geometries with equal numbers."""
    original = _pair()
    request = ScientificRequest(
        molecules=(
            *original.molecules,
            molecule("copy", original.molecules[0].geometry),
        ),
        goals=(
            CalculationGoal(
                id="a",
                driver="energy",
                geometry="h2",
                models=(_model(),),
                reuse_group="shared",
            ),
            CalculationGoal(
                id="b",
                driver="energy",
                geometry="copy",
                models=(_model(),),
                reuse_group="shared",
            ),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 2
    assert proposal.reuses == ()


def test_call_count_preference_preserves_the_scientific_model_order() -> None:
    """Keep the first permitted basis even when the second could enable sharing."""
    request = ScientificRequest(
        molecules=_pair().molecules,
        goals=(
            CalculationGoal(
                id="a",
                driver="energy",
                geometry="h2",
                models=(_model(), _model("cc-pvdz")),
                reuse_group="shared",
            ),
            CalculationGoal(
                id="b",
                driver="energy",
                geometry="h2",
                models=(_model("cc-pvdz"),),
                reuse_group="shared",
            ),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 2
    assert proposal.choices[0].model.basis == "sto-3g"
    assert proposal.choices[0].preference_rank == 0


@pytest.mark.parametrize(("preference", "calls"), [("prefer", 2), ("avoid", 3)])
def test_shared_optimizations_translate_future_derivative_frames(
    preference: str,
    calls: int,
) -> None:
    """Map geometry and explicit tensor frames through reused optimization goals.

    Args:
        preference: Try fewer calls or independent calls first.
        calls: Expected calls after independently checked geometry relationships.
    """
    request = ScientificRequest(
        molecules=_pair().molecules,
        goals=(
            CalculationGoal(
                id="opt_a",
                driver="optimize",
                geometry="h2",
                models=(_model(),),
                reuse_group="optimization",
            ),
            CalculationGoal(
                id="opt_b",
                driver="optimize",
                geometry="h2",
                models=(_model(),),
                reuse_group="optimization",
            ),
            *(
                CalculationGoal(
                    id=f"gradient_{name}",
                    driver="gradient",
                    geometry=f"opt_{name}",
                    models=(_model(),),
                    reuse_group="derivative",
                    quantity=QuantityType(
                        meaning="gradient",
                        unit="hartree/bohr",
                        shape=("atoms", 3),
                        frame=f"opt_{name}",
                    ),
                )
                for name in ("a", "b")
            ),
        ),
        relations=(SameGeometry(calculations=("gradient_a", "gradient_b")),),
    )
    preferences = PlanningPreferences(
        calculation_reuse="prefer" if preference == "prefer" else "avoid"
    )

    proposal = propose(request, load_catalog("psi4"), preferences=preferences)

    assert proposal.status == "constructed", proposal.report
    assert proposal.plan is not None
    assert len(proposal.plan.steps) == calls
    gradients = tuple(
        step
        for step in proposal.plan.steps
        if isinstance(step, Calculation) and step.driver == "gradient"
    )
    assert all(step.geometry == "opt_a" for step in gradients)
    assert all(
        step.quantity is not None and step.quantity.frame == "opt_a"
        for step in gradients
    )
    assert proposal.report is not None
    assert proposal.report.request_complete


@pytest.mark.parametrize("maximum", [1, 2])
def test_invalid_sharing_backtracks_to_independent_calls(maximum: int) -> None:
    """Preserve a valid unshared reaction when merging would erase its source terms.

    Args:
        maximum: Allow only the rejected shared candidate or also its fallback.
    """
    original = _pair()
    request = ScientificRequest(
        molecules=original.molecules,
        goals=(
            *original.goals,
            ExpressionGoal(
                id="reaction",
                quantity=QuantityType(meaning="reaction_energy", unit="hartree"),
                terms=(
                    GoalTerm(goal="first", coefficient=-1),
                    GoalTerm(goal="second", coefficient=1),
                ),
            ),
        ),
    )

    proposal = propose(
        request,
        load_catalog("psi4"),
        limits=SearchLimits(max_candidates=maximum),
    )

    assert proposal.attempts == maximum
    if maximum == 1:
        assert proposal.status == "exhausted"
        assert proposal.plan is None
    else:
        assert proposal.status == "constructed", proposal.report
        assert proposal.plan is not None
        assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == 2
        assert proposal.reuses == ()


def test_missing_capabilities_do_not_repeat_every_sharing_assignment() -> None:
    """Try the permitted supported model within two candidates despite many aliases."""
    unknown = Model(
        method="unlisted",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    request = ScientificRequest(
        molecules=_pair().molecules,
        goals=(
            CalculationGoal(
                id="a",
                driver="energy",
                geometry="h2",
                models=(unknown, _model()),
                reuse_group="shared",
            ),
            *(
                CalculationGoal(
                    id=name,
                    driver="energy",
                    geometry="h2",
                    models=(_model(),),
                    reuse_group="shared",
                )
                for name in ("b", "c", "d")
            ),
        ),
    )

    proposal = propose(
        request,
        load_catalog("psi4"),
        limits=SearchLimits(max_candidates=2),
    )

    assert proposal.status == "constructed", proposal.report
    assert proposal.attempts == 2
    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 1


def test_finite_cases_keep_reuse_permissions_local_to_each_history() -> None:
    """Share calls within each case while retaining independent case histories."""
    template = _pair()
    request = finite_study(
        template,
        (
            StudyCase(id="first_case", molecules=template.molecules),
            StudyCase(id="second_case", molecules=template.molecules),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 2
    assert [entry.goals for entry in proposal.reuses] == [
        ("first_case:first", "first_case:second"),
        ("second_case:first", "second_case:second"),
    ]


def test_reused_property_products_keep_call_frames_and_export_goal_mapping(
    tmp_path: Path,
) -> None:
    """Translate a named product's frame and retain every logical goal at export.

    Args:
        tmp_path: Fresh construction bundle parent.
    """
    pair = _pair("properties")
    request = ScientificRequest(
        molecules=pair.molecules,
        goals=(
            *pair.goals,
            ProductGoal(
                id="dipole",
                calculation="second",
                name="dipole",
                quantity=product_quantity("dipole", frame="second"),
            ),
        ),
    )
    catalog = load_catalog("psi4")
    proposal = propose(request, catalog)
    assert proposal.plan is not None

    exported = export_bundle(proposal.plan, request, catalog, tmp_path / "bundle")

    assert len(proposal.reuses) == 1
    assert {entry.goal: entry.steps for entry in exported.manifest.goal_coverage} == {
        "first": ("first",),
        "second": ("first",),
        "dipole": ("dipole",),
    }
    product = next(item for item in exported.manifest.quantities if item.id == "dipole")
    assert product.producer == "first"
    assert product.quantity.frame == "first"
    source = (Path(exported.directory) / exported.manifest.native_inputs[0]).read_text()
    assert ".variable(" not in source


def test_requested_derivative_frame_cannot_be_ignored() -> None:
    """Reject a canonical gradient that fails the request's explicit frame."""
    request = ScientificRequest(
        molecules=_pair().molecules,
        goals=(
            CalculationGoal(
                id="gradient",
                driver="gradient",
                geometry="h2",
                models=(_model(),),
                quantity=QuantityType(
                    meaning="gradient",
                    unit="hartree/bohr",
                    shape=("atoms", 3),
                    frame="unrelated",
                ),
            ),
        ),
    )
    plan = Plan(
        molecules=request.molecules,
        steps=(
            Calculation(
                id="gradient",
                driver="gradient",
                geometry="h2",
                model=_model(),
                satisfies=("gradient",),
            ),
        ),
        requirements=(SameModel(calculations=("gradient", "gradient")),),
    )

    report = verify(plan, request=request, catalog=load_catalog("psi4"))

    assert report.status == "violated"
    assert any(
        item.code == "goal_contract" and item.path[-1] == "quantity"
        for item in report.diagnostics
    )


def test_different_analysis_conditions_and_routes_require_separate_calls() -> None:
    """Keep different frequency analyses despite matching group labels."""
    cases: tuple[tuple[str, DerivativeRoute, float], ...] = (
        ("first", "analytic", 298.15),
        ("second", "finite_difference", 400.0),
    )
    goals = tuple(
        CalculationGoal(
            id=name,
            driver="frequency",
            geometry="h2",
            models=(_model(),),
            reuse_group="shared",
            derivative_routes=(route,),
            analysis=VibrationalAnalysis(
                conditions=ThermalConditions(
                    temperature_kelvin=temperature, pressure_pascal=101325.0
                ),
                rotational_symmetry_number=2,
            ),
        )
        for name, route, temperature in cases
    )

    proposal = propose(
        ScientificRequest(molecules=_pair().molecules, goals=goals),
        load_catalog("psi4"),
    )

    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 2
    assert proposal.reuses == ()


@pytest.mark.parametrize("shared_parent", [False, True])
def test_reuse_composes_through_equivalent_full_basis_subsystems(
    shared_parent: bool,
) -> None:
    """Share deterministic subsystem declarations and their authorized energy calls.

    Args:
        shared_parent: Start from two shareable optimization goals instead of one input.
    """
    atom = Molecule.from_xyz(
        "1\nHelium\nHe 0 0 0\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    other = Molecule.from_xyz(
        "1\nHelium\nHe 0 0 3\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    assembled = assemble_fragments(
        ("A", atom), ("B", other), state=ElectronicState(charge=0, multiplicity=1)
    )
    geometry = Molecule(
        atoms=assembled.atoms,
        fragments=assembled.fragments,
        state=assembled.state,
        fixed_com=True,
        fixed_orientation=True,
    )
    parents = (
        tuple(
            CalculationGoal(
                id=f"opt_{name}",
                driver="optimize",
                geometry="parent",
                models=(_model(),),
                reuse_group="parent",
            )
            for name in ("a", "b")
        )
        if shared_parent
        else ()
    )
    request = ScientificRequest(
        molecules=(molecule("parent", geometry),),
        goals=(
            *parents,
            *(
                SubsystemGoal(
                    id=f"sub_{name}",
                    geometry=f"opt_{name}" if shared_parent else "parent",
                    real_fragments=("A",),
                    state=ElectronicState(charge=0, multiplicity=1),
                )
                for name in ("a", "b")
            ),
            *(
                CalculationGoal(
                    id=f"energy_{name}",
                    driver="energy",
                    geometry=f"sub_{name}",
                    models=(_model(),),
                    reuse_group="subsystem_energy",
                )
                for name in ("a", "b")
            ),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.status == "constructed", proposal.report
    assert proposal.plan is not None
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == (
        2 if shared_parent else 1
    )
    assert sum(step.kind == "subsystem" for step in proposal.plan.steps) == 1
    assert proposal.report is not None
    assert proposal.report.request_complete


def test_reuse_encoding_is_bounded_before_candidate_verification() -> None:
    """Count sharing alternatives in the finite encoding budget."""
    proposal = propose(
        _pair(),
        load_catalog("psi4"),
        limits=SearchLimits(max_choices=3),
    )

    assert proposal.status == "exhausted"
    assert proposal.attempts == 0
    assert proposal.plan is None


def test_rejected_candidate_is_retained_with_the_matching_proof_context() -> None:
    """Retain the actual rejected graph so diagnostic paths can be inspected."""
    request = _pair()
    unknown = Model(method="unlisted", basis="sto-3g", reference="rhf")
    request = ScientificRequest(
        molecules=request.molecules,
        goals=(
            CalculationGoal(
                id="unknown",
                driver="energy",
                geometry="h2",
                models=(unknown,),
                reuse_group="shared",
            ),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.status == "unknown"
    assert proposal.plan is None
    assert proposal.last_candidate is not None
    assert proposal.report is not None
    fresh = verify(
        proposal.last_candidate,
        request=request,
        catalog=load_catalog("psi4"),
        limits=proposal.report.limits,
    )
    assert fresh.coverage == proposal.report.coverage
    assert fresh.status == proposal.report.status
    assert not fresh.request_complete


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native preprocessing of shared calls",
)
@pytest.mark.parametrize("preference", ["prefer", "avoid"])
def test_native_input_emits_only_the_selected_calls(
    tmp_path: Path, preference: ReusePreference
) -> None:
    """Observe native driver dispatch without running a chemistry calculation.

    Args:
        tmp_path: Isolated development interpreter directory.
        preference: Rank shared or separate permitted implementations first.
    """
    proposal = propose(
        _pair(),
        load_catalog("psi4"),
        preferences=PlanningPreferences(calculation_reuse=preference),
    )
    assert proposal.plan is not None
    expected = 1 if preference == "prefer" else 2
    program = f"""import sys, psi4
psi4.core.set_output_file('dispatch.dat', False)
calls = []
def observe(name, **kwargs):
    calls.append(name)
    return -1.0
psi4.energy = observe
namespace = {{'psi4': psi4}}
source = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(source, '<reuse-dispatch>', 'exec'), namespace)
assert len(calls) == {expected}
assert len(namespace['formal_results']) == {expected}
print('selected calls emitted')
"""
    completed = subprocess.run(  # noqa: S603 - Fixed native dispatch harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(proposal.plan),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("selected calls emitted")
