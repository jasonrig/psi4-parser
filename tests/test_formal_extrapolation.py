"""Check basis-limit recipes independently from self-consistent scalar algebra."""

import json
import os
import subprocess
from fractions import Fraction
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BasisCorrectionPoint,
    BasisSequence,
    Calculation,
    CalculationGoal,
    Combination,
    ExpressionGoal,
    ExtrapolationStudy,
    GoalTerm,
    InversePowerExtrapolation,
    Model,
    Plan,
    ScientificRequest,
    Setting,
    StudyCase,
    export_bundle,
    extrapolation_expansion,
    finite_study,
    load_catalog,
    propose,
    verify,
)
from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import (
    BasisCapability,
    BasisFunctions,
    CapabilityCatalog,
    DerivativeRoute,
    MethodCapability,
)
from psi4_parser.formal.intent import Goal
from psi4_parser.formal.science import QuantityType, Rational

_JSON = TypeAdapter(JsonValue)


def _edit[T: Record](record: T, path: tuple[str | int, ...], value: JsonValue) -> T:
    document = _JSON.validate_json(record.model_dump_json())
    node = document
    for component in path[:-1]:
        if isinstance(component, int):
            assert isinstance(node, list)
            node = node[component]
        else:
            assert isinstance(node, dict)
            node = node[component]
    last = path[-1]
    if isinstance(last, int):
        assert isinstance(node, list)
        node[last] = value
    else:
        assert isinstance(node, dict)
        node[last] = value
    return type(record).model_validate_json(json.dumps(document))


@pytest.fixture(name="extrapolation_profile")
def _profile(formal_profile: CapabilityCatalog) -> CapabilityCatalog:
    """Supply declared toy basis relationships for independent contract tests.

    Args:
        formal_profile: Versioned synthetic evidence shared by planner tests.

    Returns:
        Toy method and basis-series declarations for isolated tests.
    """
    return CapabilityCatalog(
        id="synthetic-extrapolation",
        evidence=formal_profile.evidence,
        options=formal_profile.options,
        methods=tuple(
            MethodCapability(
                method=name,
                driver="energy",
                reference="rhf",
                status="supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                options=("scf_type",),
                features=("frozen_core", "cartesian_basis"),
                evidence=("fixture",),
            )
            for name in ("hf", "mp2", "ccsd")
        ),
        bases=tuple(
            BasisCapability(
                name=name,
                status="supported",
                elements=("H",),
                functions=(
                    BasisFunctions(element="H", spherical=count, cartesian=count),
                ),
                sequence=BasisSequence(family="toy-valence", cardinal=cardinal),
                evidence=("fixture",),
            )
            for name, count, cardinal in (("toy-dz", 5, 2), ("toy-tz", 14, 3))
        ),
    )


def _model(method: str, basis: str) -> Model:
    return Model(
        method=method,
        basis=basis,
        reference="rhf",
        settings=(Setting(name="scf_type", value="pk"),),
    )


def _request(*, power: int = 3) -> ScientificRequest:
    expansion = extrapolation_expansion(
        ExtrapolationStudy(
            id="cbs",
            geometry="h2",
            family="toy-valence",
            power=power,
            low=BasisCorrectionPoint(
                basis="toy-dz",
                cardinal=2,
                models=(_model("mp2", "toy-dz"),),
                reference_models=(_model("hf", "toy-dz"),),
            ),
            high=BasisCorrectionPoint(
                basis="toy-tz",
                cardinal=3,
                models=(_model("mp2", "toy-tz"),),
                reference_models=(_model("hf", "toy-tz"),),
            ),
        )
    )
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),), goals=expansion.goals
    )


def test_inverse_power_correction_uses_the_declared_basis_sequence(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Require four calls and the independently known DT inverse-cube weights.

    Args:
        extrapolation_profile: Synthetic methods and basis-family evidence.
    """
    request = _request()

    proposal = propose(request, extrapolation_profile)

    assert proposal.status == "constructed", tuple(
        (item.code, item.message) for item in proposal.diagnostics
    )
    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == 4
    target = proposal.plan.steps[-1]
    assert isinstance(target, Combination)
    coefficients = tuple(
        term.coefficient.fraction
        if isinstance(term.coefficient, Rational)
        else Fraction(term.coefficient)
        for term in target.terms
    )
    assert coefficients == (Fraction(-8, 19), Fraction(27, 19))
    assert target.quantity == QuantityType(
        meaning="basis_limit_correction", unit="hartree"
    )
    assert isinstance(target.extrapolation, InversePowerExtrapolation)
    assert target.extrapolation.power == 3
    assert any("inverse-power" in item for item in proposal.report.assumptions)


@pytest.mark.parametrize(
    ("power", "weights"),
    [
        (2, (Fraction(-4, 5), Fraction(9, 5))),
        (4, (Fraction(-16, 65), Fraction(81, 65))),
    ],
)
def test_explicit_exponents_keep_exact_weights(
    extrapolation_profile: CapabilityCatalog,
    power: int,
    weights: tuple[Fraction, Fraction],
) -> None:
    """Honor scientific exponent choices with independently known rational weights.

    Args:
        extrapolation_profile: Synthetic basis and method evidence.
        power: Explicit convergence-model exponent.
        weights: Independent two-point algebra expectations.
    """
    proposal = propose(_request(power=power), extrapolation_profile)

    assert proposal.plan is not None
    target = proposal.plan.steps[-1]
    assert isinstance(target, Combination)
    assert (
        tuple(
            term.coefficient.fraction
            for term in target.terms
            if isinstance(term.coefficient, Rational)
        )
        == weights
    )


def test_self_consistent_wrong_extrapolation_is_rejected(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Reject wrong weights even when the request and generated algebra agree.

    Args:
        extrapolation_profile: Synthetic application evidence.
    """
    request = _edit(_request(), ("goals", 6, "terms", 0, "coefficient"), -1)
    request = _edit(request, ("goals", 6, "terms", 1, "coefficient"), 2)

    proposal = propose(request, extrapolation_profile)

    assert proposal.status == "no_candidate"
    assert proposal.report is not None
    assert any(
        item.code == "extrapolation_formula" for item in proposal.report.diagnostics
    )


@pytest.mark.parametrize(
    "sequence",
    [
        None,
        {"family": "augmented-toy", "cardinal": 3},
        {"family": "toy-valence", "cardinal": 4},
    ],
)
def test_family_and_cardinal_membership_need_matching_evidence(
    extrapolation_profile: CapabilityCatalog, sequence: JsonValue
) -> None:
    """Keep absent evidence unknown and reject contrary basis relationships.

    Args:
        extrapolation_profile: Synthetic basis declarations.
        sequence: Missing or contrary membership at the high point.
    """
    catalog = _edit(extrapolation_profile, ("bases", 1, "sequence"), sequence)

    proposal = propose(_request(), catalog)

    assert proposal.plan is None
    assert proposal.report is not None
    assert proposal.report.capability_status == (
        "unknown" if sequence is None else "violated"
    )
    assert any(
        item.code.startswith("extrapolation_basis_")
        for item in proposal.report.diagnostics
    )


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("goals", 3, "models", 0, "method"), "ccsd", "extrapolation_treatment"),
        (("goals", 4, "models", 0, "frozen_core"), True, "extrapolation_context"),
        (("goals", 2, "terms", 1, "coefficient"), 0, "extrapolation_sources"),
        (
            ("goals", 6, "quantity", "meaning"),
            "electronic_energy",
            "extrapolation_quantity",
        ),
    ],
)
def test_extrapolation_preserves_treatments_and_source_meaning(
    extrapolation_profile: CapabilityCatalog,
    path: tuple[str | int, ...],
    value: JsonValue,
    code: str,
) -> None:
    """Locate independently invalid model, source, and quantity choices.

    Args:
        extrapolation_profile: Synthetic application evidence.
        path: Scientific choice to damage in the independent request.
        value: Structurally valid replacement.
        code: Required scientific diagnostic.
    """
    proposal = propose(_edit(_request(), path, value), extrapolation_profile)

    assert proposal.plan is None
    assert proposal.report is not None
    assert any(item.code == code for item in proposal.report.diagnostics)


def test_recipe_cannot_be_removed_from_an_accepted_plan(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Require the independent basis model as well as the requested scalar formula.

    Args:
        extrapolation_profile: Synthetic application evidence.
    """
    request = _request()
    proposal = propose(request, extrapolation_profile)
    assert proposal.plan is not None
    plan = _edit(proposal.plan, ("steps", 6, "extrapolation"), None)

    report = verify(plan, request=request, catalog=extrapolation_profile)

    assert report.status == "violated"
    assert any(item.code == "goal_extrapolation" for item in report.diagnostics)
    assert any(item.code == "extrapolation_recipe" for item in report.diagnostics)


def test_basis_points_keep_geometry_provenance(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Reject two numerical copies as evidence of one shared extrapolation geometry.

    Args:
        extrapolation_profile: Synthetic application evidence.
    """
    base = _request()
    request = ScientificRequest(
        molecules=(*base.molecules, molecule("copied", base.molecules[0].geometry)),
        goals=base.goals,
    )
    request = _edit(request, ("goals", 3, "geometry"), "copied")
    request = _edit(request, ("goals", 4, "geometry"), "copied")

    proposal = propose(request, extrapolation_profile)

    assert proposal.report is not None
    assert proposal.report.status == "violated"
    assert any(
        item.code == "extrapolation_treatment" for item in proposal.report.diagnostics
    )


def test_extrapolation_metadata_dependencies_are_checked_before_inspection(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Reject dangling recipe references without an inspector exception.

    Args:
        extrapolation_profile: Synthetic application evidence.
    """
    base = _request()
    request = _edit(base, ("goals", 6, "extrapolation", "low", "result"), "missing")
    proposal = propose(request, extrapolation_profile)
    assert proposal.status == "invalid"
    assert any(item.code == "request_extrapolation" for item in proposal.diagnostics)
    valid = propose(base, extrapolation_profile)
    assert valid.plan is not None
    plan = _edit(valid.plan, ("steps", 6, "extrapolation", "low", "result"), "missing")

    report = verify(plan, catalog=extrapolation_profile)

    assert report.status == "invalid"
    assert any(item.code == "extrapolation_source" for item in report.diagnostics)


def test_finite_studies_translate_recipe_dependencies(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Retain each case's basis metadata and geometry history.

    Args:
        extrapolation_profile: Synthetic application evidence.
    """
    template = _request()
    request = finite_study(
        template,
        tuple(
            StudyCase(id=name, molecules=template.molecules) for name in ("one", "two")
        ),
    )

    proposal = propose(request, extrapolation_profile)

    assert proposal.plan is not None
    assert len(proposal.plan.steps) == 14
    targets = [
        step
        for step in proposal.plan.steps
        if isinstance(step, Combination) and step.extrapolation
    ]
    assert len(targets) == 2
    for target in targets:
        assert target.extrapolation is not None
        assert (
            target.extrapolation.low.result.split(":", 1)[0]
            == target.id.split(":", 1)[0]
        )


def test_electronic_composition_and_export_retain_symbolic_basis_recipe(
    tmp_path: Path, extrapolation_profile: CapabilityCatalog
) -> None:
    """Compose the correction with a reference while exporting no calculated values.

    Args:
        tmp_path: New construction-bundle directory parent.
        extrapolation_profile: Synthetic method and basis evidence.
    """
    base = _request()
    request = ScientificRequest(
        molecules=base.molecules,
        goals=(
            *base.goals,
            ExpressionGoal(
                id="estimate",
                terms=(
                    GoalTerm(goal="cbs:high:reference", coefficient=1),
                    GoalTerm(goal="cbs:basis_limit", coefficient=1),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            ),
        ),
    )
    proposal = propose(request, extrapolation_profile)
    assert proposal.plan is not None

    exported = export_bundle(
        proposal.plan, request, extrapolation_profile, tmp_path / "bundle"
    )

    assert len(exported.manifest.goal_coverage) == 8
    recipes = [
        step.extrapolation
        for step in exported.manifest.expressions
        if step.extrapolation
    ]
    assert len(recipes) == 1
    assert recipes[0].family == "toy-valence"
    native = (Path(exported.directory) / exported.manifest.native_inputs[0]).read_text()
    assert "cbs:basis_limit" not in native
    assert "estimate" not in native
    assert (
        Plan.model_validate_json(
            (Path(exported.directory) / "calculation-plan.json").read_bytes()
        )
        == proposal.plan
    )


def test_bundled_sequences_support_dt_and_tq_corrections() -> None:
    """Use independently audited D/T/Q memberships rather than name inference."""
    catalog = load_catalog("psi4")
    members = {
        item.name: item.sequence.key
        for item in catalog.bases
        if item.sequence and item.role == "basis"
    }
    assert members == {
        "cc-pvdz": ("cc-pvxz", 2),
        "cc-pvtz": ("cc-pvxz", 3),
        "cc-pvqz": ("cc-pvxz", 4),
    }


@pytest.mark.parametrize("changed_family", [False, True])
def test_fitting_basis_series_are_checked_per_role(
    extrapolation_profile: CapabilityCatalog, changed_family: bool
) -> None:
    """Allow corresponding fitting bases and reject a family switch.

    Args:
        extrapolation_profile: Synthetic methods and orbital basis evidence.
        changed_family: Give the high fitting basis an unrelated family.
    """
    catalog = CapabilityCatalog(
        id="synthetic-fitted-extrapolation",
        evidence=extrapolation_profile.evidence,
        methods=extrapolation_profile.methods,
        options=extrapolation_profile.options,
        bases=(
            *extrapolation_profile.bases,
            *(
                BasisCapability(
                    name=name,
                    role="df_basis_scf",
                    status="supported",
                    elements=("H",),
                    sequence=BasisSequence(family=family, cardinal=cardinal),
                    evidence=("fixture",),
                )
                for name, family, cardinal in (
                    ("toy-dz-jk", "toy-jk", 2),
                    ("toy-tz-jk", "unrelated-jk" if changed_family else "toy-jk", 3),
                )
            ),
        ),
    )
    for index in range(len(catalog.methods)):
        catalog = _edit(
            catalog, ("methods", index, "features"), ["auxiliary_basis:df_basis_scf"]
        )
    request = _request()
    for index, name in (
        (0, "toy-dz-jk"),
        (1, "toy-dz-jk"),
        (3, "toy-tz-jk"),
        (4, "toy-tz-jk"),
    ):
        request = _edit(
            request,
            ("goals", index, "models", 0, "auxiliary_bases"),
            [{"role": "df_basis_scf", "basis": name}],
        )

    proposal = propose(request, catalog)

    assert proposal.status == ("no_candidate" if changed_family else "constructed")
    if changed_family:
        assert proposal.report is not None
        assert any(
            item.code == "extrapolation_fitting_family"
            for item in proposal.report.diagnostics
        )


def _audited_expansion(
    name: str, low: tuple[str, int], high: tuple[str, int]
) -> tuple[Goal, ...]:
    def models(basis: str, method: str) -> tuple[Model, ...]:
        settings: tuple[Setting, ...] = (Setting(name="scf_type", value="PK"),)
        if method == "mp2":
            settings += (
                Setting(name="mp2_type", value="CONV"),
                Setting(name="qc_module", value="OCC"),
            )
        return (Model(method=method, basis=basis, reference="rhf", settings=settings),)

    expansion = extrapolation_expansion(
        ExtrapolationStudy(
            id=name,
            geometry="h2",
            family="cc-pvXZ",
            power=3,
            reuse_group="one-basis-series",
            low=BasisCorrectionPoint(
                basis=low[0],
                cardinal=low[1],
                models=models(low[0], "mp2"),
                reference_models=models(low[0], "hf"),
            ),
            high=BasisCorrectionPoint(
                basis=high[0],
                cardinal=high[1],
                models=models(high[0], "mp2"),
                reference_models=models(high[0], "hf"),
            ),
        )
    )
    return expansion.goals


def test_audited_dt_tq_composition_reuses_the_shared_tz_point() -> None:
    """Retain two complete recipes while sharing their explicitly permitted T point."""
    base = _request()
    request = ScientificRequest(
        molecules=base.molecules,
        goals=(
            *_audited_expansion("dt", ("cc-pvdz", 2), ("cc-pvtz", 3)),
            *_audited_expansion("tq", ("cc-pvtz", 3), ("cc-pvqz", 4)),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is not None
    assert len(proposal.reuses) == 2
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == 6
    assert proposal.report is not None
    assert len(proposal.report.coverage) == 14


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native extrapolation input dispatch",
)
def test_extrapolation_export_preserves_native_point_settings(tmp_path: Path) -> None:
    """Observe actual native option dispatch while leaving every energy symbolic.

    Args:
        tmp_path: Isolated native interpreter and construction bundle directory.
    """
    request = ScientificRequest(
        molecules=_request().molecules,
        goals=_audited_expansion("dt", ("cc-pvdz", 2), ("cc-pvtz", 3)),
    )
    catalog = load_catalog("psi4")
    proposal = propose(request, catalog)
    assert proposal.plan is not None
    exported = export_bundle(proposal.plan, request, catalog, tmp_path / "bundle")
    program = """import sys, psi4
psi4.core.set_output_file('dispatch.dat', False)
calls = []
def observe(method, **kwargs):
    assert psi4.core.get_global_option('SCF_TYPE') == 'PK'
    if method == 'mp2':
        assert psi4.core.get_global_option('MP2_TYPE') == 'CONV'
        assert psi4.core.get_global_option('QC_MODULE') == 'OCC'
    calls.append((method, psi4.core.get_global_option('BASIS')))
    return 0.0
psi4.energy = observe
namespace = {'psi4': psi4}
source = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(source, '<basis-points>', 'exec'), namespace)
assert calls == [
    ('mp2', 'CC-PVDZ'), ('hf', 'CC-PVDZ'),
    ('mp2', 'CC-PVTZ'), ('hf', 'CC-PVTZ'),
]
assert len(namespace['formal_results']) == 4
print('basis settings preserved')
"""

    completed = subprocess.run(  # noqa: S603 - Fixed development-only dispatch harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=(
            Path(exported.directory) / exported.manifest.native_inputs[0]
        ).read_text(),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("basis settings preserved")


@pytest.mark.parametrize(
    ("basis", "route", "expected"),
    [
        ("cc-pvtz", "analytic", "constructed"),
        ("cc-pvqz", "analytic", "constructed"),
        ("cc-pvqz", "finite_difference", "constructed"),
    ],
)
def test_reference_compilation_limits_do_not_constrain_target_inputs(
    basis: str, route: DerivativeRoute, expected: str
) -> None:
    """Construct T/Q derivatives without inheriting reference compilation limits.

    Args:
        basis: Audited orbital basis.
        route: Explicitly permitted Hessian route.
        expected: Construction outcome from the selected evidence case.
    """
    request = ScientificRequest(
        molecules=_request().molecules,
        goals=(
            CalculationGoal(
                id="hessian",
                driver="hessian",
                geometry="h2",
                models=(
                    Model(
                        method="hf",
                        basis=basis,
                        reference="rhf",
                        settings=(Setting(name="scf_type", value="PK"),),
                    ),
                ),
                derivative_routes=(route,),
            ),
        ),
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.status == expected


def test_basis_limit_proof_requires_a_profile_even_without_request(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Keep basis membership unknown when a relationship-only caller omits evidence.

    Args:
        extrapolation_profile: Evidence for constructing the initial valid graph.
    """
    proposal = propose(_request(), extrapolation_profile)
    assert proposal.plan is not None

    report = verify(proposal.plan)

    assert report.status == "unknown"
    assert report.capability_status == "unknown"
    assert any(item.code == "capability_catalog" for item in report.diagnostics)


def test_corrected_estimates_compose_with_closed_reaction_bookkeeping(
    extrapolation_profile: CapabilityCatalog,
) -> None:
    """Balance the full basis treatment for two geometries of the same species.

    Args:
        extrapolation_profile: Synthetic method and basis declarations.
    """
    template = _request()
    study = finite_study(
        template,
        (
            StudyCase(id="reactant", molecules=template.molecules),
            StudyCase(
                id="product",
                molecules=(
                    molecule(
                        "h2",
                        Molecule.from_xyz(
                            "2\nHydrogen\nH 0 0 0\nH 0 0 .9\n",
                            state=ElectronicState(charge=0, multiplicity=1),
                        ),
                    ),
                ),
            ),
        ),
    )
    totals = tuple(
        ExpressionGoal(
            id=f"{name}:estimate",
            terms=(
                GoalTerm(goal=f"{name}:cbs:high:reference", coefficient=1),
                GoalTerm(goal=f"{name}:cbs:basis_limit", coefficient=1),
            ),
            quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
        )
        for name in ("reactant", "product")
    )
    request = ScientificRequest(
        molecules=study.molecules,
        goals=(
            *study.goals,
            *totals,
            ExpressionGoal(
                id="reaction",
                terms=(
                    GoalTerm(goal=totals[1].id, coefficient=1),
                    GoalTerm(goal=totals[0].id, coefficient=-1),
                ),
                quantity=QuantityType(meaning="reaction_energy", unit="hartree"),
            ),
        ),
    )

    proposal = propose(request, extrapolation_profile)

    assert proposal.status == "constructed"
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert len(proposal.report.coverage) == 17


@pytest.mark.parametrize("reference_weight", [0, 3])
def test_correlation_correction_cannot_replace_or_rescale_the_reference(
    extrapolation_profile: CapabilityCatalog, reference_weight: int
) -> None:
    """Reject a missing or multiply counted reference despite consistent formulas.

    Args:
        extrapolation_profile: Synthetic method and basis declarations.
        reference_weight: Incorrect reference coefficient in the independent intent.
    """
    base = _request()
    request = ScientificRequest(
        molecules=base.molecules,
        goals=(
            *base.goals,
            ExpressionGoal(
                id="incorrect_total",
                terms=(
                    GoalTerm(goal="cbs:high:reference", coefficient=reference_weight),
                    GoalTerm(goal="cbs:basis_limit", coefficient=1),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            ),
        ),
    )

    proposal = propose(request, extrapolation_profile)

    assert proposal.status == "no_candidate"
    assert proposal.report is not None
    assert any(
        item.code == "extrapolation_total_formula"
        for item in proposal.report.diagnostics
    )
