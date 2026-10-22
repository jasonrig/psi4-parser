"""Check composable proof obligations and construction of executable inputs."""

from concurrent.futures import ThreadPoolExecutor

import pytest
import z3
from jsonschema import Draft202012Validator
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser import validate
from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    Combination,
    EnergyFormula,
    EnergyTerm,
    Limits,
    Model,
    Plan,
    SameGeometry,
    SameModel,
    UsesGeometry,
    VerificationError,
    build,
    render,
    verify,
)


def hydrogen() -> Molecule:
    """Return a resolved neutral H2 geometry with an explicit singlet state."""
    return Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 0.85\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )


def optimization_plan(*, stale: bool = False) -> Plan:
    """Return optimization and frequencies using the final or stale geometry."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    return Plan(
        molecules=(molecule("h2", hydrogen()),),
        steps=(
            Calculation(id="opt", driver="optimize", geometry="h2", model=model),
            Calculation(
                id="freq",
                driver="frequency",
                geometry="h2" if stale else "opt",
                model=model,
            ),
        ),
        requirements=(UsesGeometry(calculation="freq", geometry="opt"),),
    )


def test_optimized_geometry_is_proved() -> None:
    """Prove that frequencies consume the explicitly required optimized geometry."""
    report = verify(optimization_plan())
    assert report.status == "proved"
    assert report.obligations[0].proof


def test_stale_geometry_has_a_counterexample() -> None:
    """Reject a frequency calculation that uses the pre-optimization geometry."""
    report = verify(optimization_plan(stale=True))
    assert report.status == "violated"
    assert report.obligations[0].counterexample


def test_unproved_plan_cannot_be_rendered() -> None:
    """Prevent input construction when the geometry requirement is violated."""
    with pytest.raises(VerificationError, match="violated"):
        render(optimization_plan(stale=True))


def composite_plan(*, wrong: bool = False) -> Plan:
    """Return a nested basis correction with independently specified algebra."""
    small = Model(method="scf", basis="sto-3g", reference="rhf")
    large = Model(method="scf", basis="cc-pvdz", reference="rhf")
    return Plan(
        molecules=(molecule("h2", hydrogen()),),
        steps=(
            Calculation(id="small", driver="energy", geometry="h2", model=small),
            Calculation(id="large", driver="energy", geometry="h2", model=large),
            Combination(
                id="delta",
                terms=(
                    EnergyTerm(result="large", coefficient=1),
                    EnergyTerm(result="small", coefficient=1 if wrong else -1),
                ),
            ),
            Combination(
                id="total",
                terms=(
                    EnergyTerm(result="small", coefficient=1),
                    EnergyTerm(result="delta", coefficient=1),
                ),
            ),
        ),
        requirements=(
            SameGeometry(calculations=("small", "large")),
            EnergyFormula(
                result="total", terms=(EnergyTerm(result="large", coefficient=1),)
            ),
        ),
    )


def test_nested_energy_formula_is_proved_for_arbitrary_energies() -> None:
    """Expand nested sums without requiring identical computational models."""
    assert verify(composite_plan()).status == "proved"
    report = verify(composite_plan(wrong=True))
    assert report.status == "violated"
    assert report.obligations[0].status == "proved"
    assert (
        report.obligations[1].counterexample[0].value
        != report.obligations[1].counterexample[1].value
    )


def test_proof_queries_replay_independently() -> None:
    """Replay successful and violated obligations without trusting report labels."""
    for plan in (composite_plan(), composite_plan(wrong=True)):
        for obligation in verify(plan).obligations:
            solver = z3.Solver(ctx=z3.Context())
            solver.from_string(obligation.smt2)
            assert solver.check() == (
                z3.unsat if obligation.status == "proved" else z3.sat
            )


def test_schema_and_json_preserve_requirements() -> None:
    """Expose self-contained fields and retain exact ordered plans through JSON."""
    plan = composite_plan()
    schema = TypeAdapter(JsonValue).validate_python(Plan.model_json_schema())  # type: ignore[misc]  # Pydantic schema returns Any; validate at the boundary.
    assert isinstance(schema, dict)
    validator = Draft202012Validator(schema)
    validator.check_schema(schema)
    assert Plan.model_validate_json(plan.model_dump_json()) == plan
    assert verify(plan).plan_digest != verify(composite_plan(wrong=True)).plan_digest
    for field in Plan.model_fields.values():
        assert field.description


def test_model_equality_is_explicit_and_case_insensitive() -> None:
    """Accept case changes while detecting method, basis, or reference changes."""
    for model, expected in (
        (Model(method="SCF", basis="STO-3G", reference="rhf"), "proved"),
        (Model(method="mp2", basis="sto-3g", reference="rhf"), "violated"),
        (Model(method="scf", basis="cc-pvdz", reference="rhf"), "violated"),
        (Model(method="scf", basis="sto-3g", reference="uhf"), "violated"),
    ):
        original = optimization_plan()
        first = original.steps[0]
        assert isinstance(first, Calculation)
        plan = Plan(
            molecules=original.molecules,
            steps=(
                first,
                Calculation(id="freq", driver="frequency", geometry="opt", model=model),
            ),
            requirements=(SameModel(calculations=("opt", "freq")),),
        )
        assert verify(plan).status == expected


@pytest.mark.parametrize(
    "problem", ["forward", "duplicate", "requirement", "combination", "missing_state"]
)
def test_invalid_references_and_unresolved_states_are_located(problem: str) -> None:
    """Reject invalid plans before solving and identify the offending field.

    Args:
        problem: Structural mistake introduced into a valid plan.
    """
    original = optimization_plan()
    first = original.steps[0]
    assert isinstance(first, Calculation)
    molecules = original.molecules
    steps = original.steps
    requirements = original.requirements
    if problem == "forward":
        steps = tuple(reversed(steps))
    elif problem == "duplicate":
        steps = (first, first)
    elif problem == "requirement":
        requirements = (UsesGeometry(calculation="missing", geometry="opt"),)
    elif problem == "combination":
        steps = (
            *steps,
            Combination(id="sum", terms=(EnergyTerm(result="missing", coefficient=1),)),
        )
    else:
        geometry = Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .85\n")
        molecules = (molecule("h2", geometry),)
    report = verify(Plan(molecules=molecules, steps=steps, requirements=requirements))
    assert report.status == "invalid"
    assert report.diagnostics[0].path
    assert report.obligations == ()


def test_empty_requirements_cannot_authorize_a_job() -> None:
    """Require an explicit statement of intent instead of reporting vacuous success."""
    original = optimization_plan()
    with pytest.raises(ValidationError, match="requirements"):
        Plan(molecules=original.molecules, steps=original.steps, requirements=())


def test_exhausted_solver_limit_fails_closed() -> None:
    """Preserve an undecided solver result and refuse construction."""
    plan = optimization_plan()
    limits = Limits(resource_limit=1)
    report = verify(plan, limits=limits)
    assert report.status == "unknown"
    with pytest.raises(VerificationError) as error:
        build(plan, limits=limits)
    assert error.value.report.status == "unknown"


def test_concurrent_checks_use_independent_contexts() -> None:
    """Keep proofs and counterexamples isolated across simultaneous callers."""
    plans = (optimization_plan(), optimization_plan(stale=True), composite_plan())
    with ThreadPoolExecutor(max_workers=3) as pool:
        reports = tuple(pool.map(verify, plans))
    assert tuple(report.status for report in reports) == (
        "proved",
        "violated",
        "proved",
    )


def test_build_retains_syntax_and_explicit_result_names() -> None:
    """Render a checked plan through the normal builder without executing it."""
    source = render(composite_plan())
    assert validate(source) == ()
    assert "formal_results" in source
    assert "formal_geometries" in source


def test_construction_does_not_accept_or_reject_numerical_results() -> None:
    """Leave result acceptance to a separate consumer of the exported job."""
    source = render(optimization_plan())

    assert "isfinite" not in source
    assert "ArithmeticError" not in source
    assert "formal_math" not in source


def test_geometry_sources_are_distinct_even_for_identical_coordinates() -> None:
    """Avoid claiming that separate inputs share the same geometry provenance."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    plan = Plan(
        molecules=(molecule("one", hydrogen()), molecule("two", hydrogen())),
        steps=(
            Calculation(id="a", driver="energy", geometry="one", model=model),
            Calculation(id="b", driver="energy", geometry="two", model=model),
        ),
        requirements=(SameGeometry(calculations=("a", "b")),),
    )
    assert verify(plan).status == "violated"


def test_json_cannot_add_unmodeled_calculation_behavior() -> None:
    """Reject raw Python and extra options outside the encoded plan semantics."""
    original = optimization_plan().model_dump_json()
    for field in ('"python":"raise SystemExit()"', '"kwargs":{"return_wfn":true}'):
        document = original.replace(
            '"driver":"optimize"', '"driver":"optimize",' + field
        )
        with pytest.raises(ValidationError, match="extra_forbidden"):
            Plan.model_validate_json(document)
