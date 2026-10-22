"""Check excited-state intent and products without executing response solvers."""

import json
import os
import subprocess
from pathlib import Path
from typing import Literal

import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.builder._model import evolve
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    ElectronicTarget,
    EnergyFormula,
    EnergyTerm,
    ExpressionGoal,
    GoalTerm,
    Model,
    Plan,
    Product,
    ProductGoal,
    QuantityType,
    ScientificRequest,
    Setting,
    StudyCase,
    TDSCFAnalysis,
    describe_schema,
    export_bundle,
    finite_study,
    propose,
    render,
    verify,
)
from psi4_parser.formal._record import Record

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


def _model() -> Model:
    return Model(
        method="td-hf",
        basis="cc-pvdz",
        reference="rhf",
        tdscf=TDSCFAnalysis(states=2),
        settings=(Setting(name="scf_type", value="PK"),),
    )


def _spectrum() -> ScientificRequest:
    request = _request(_model())
    return ScientificRequest(
        molecules=request.molecules,
        goals=(
            *request.goals,
            ProductGoal(
                id="gap_1",
                calculation="response",
                name="excitation_energy",
                electronic_target=ElectronicTarget(root=1, multiplicity=1),
            ),
            ProductGoal(
                id="gap_2",
                calculation="response",
                name="excitation_energy",
                electronic_target=ElectronicTarget(root=2),
            ),
            ProductGoal(
                id="total_1",
                calculation="response",
                name="excited_state_energy",
                electronic_target=ElectronicTarget(root=1),
            ),
            ProductGoal(
                id="strength",
                calculation="response",
                name="oscillator_strength_length",
                electronic_target=ElectronicTarget(root=1),
            ),
            ProductGoal(
                id="moment",
                calculation="response",
                name="electric_transition_dipole_length",
                electronic_target=ElectronicTarget(root=1),
            ),
            ExpressionGoal(
                id="derived_total",
                quantity=QuantityType(meaning="excited_state_energy", unit="hartree"),
                terms=(
                    GoalTerm(goal="response", coefficient=1),
                    GoalTerm(goal="gap_1", coefficient=1),
                ),
            ),
        ),
    )


def _request(model: Model) -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    geometry = evolve(geometry, symmetry="c1")
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="response", driver="energy", geometry="h2", models=(model,)
            ),
        ),
    )


def test_tdscf_requires_explicit_root_and_response_intent() -> None:
    """Locate missing root/approximation intent before lowering a TD-SCF call."""
    request = _request(
        Model(
            method="td-hf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="scf_type", value="PK"),),
        )
    )

    proposal = propose(request)

    assert proposal.report is not None
    assert "tdscf_context" in {item.code for item in proposal.report.diagnostics}


def test_response_primary_is_reference_energy_and_products_have_explicit_roots(
    tmp_path: Path,
) -> None:
    """Export response quantities, preserving the ground return and transient storage.

    Args:
        tmp_path: Parent for the new construction bundle.
    """
    request = _spectrum()

    proposal = propose(request)

    assert proposal.plan is not None, proposal.diagnostics
    assert proposal.report is not None
    assert proposal.report.request_complete
    quantities = {item.id: item for item in proposal.report.quantities}
    assert quantities["response"].quantity.meaning == "electronic_energy"
    assert quantities["moment"].quantity.shape == (1, 3)
    assert quantities["moment"].quantity.frame == "response"
    assert quantities["gap_2"].electronic_target == ElectronicTarget(root=2)
    assert quantities["strength"].quantity.unit == "1"
    bindings = {item.quantity: item for item in proposal.report.native_variables}
    assert bindings["gap_1"].key == "TD-HF ROOT 0 -> ROOT 1 EXCITATION ENERGY"
    assert bindings["gap_2"].key == "TD-HF ROOT 0 -> ROOT 2 EXCITATION ENERGY"
    assert bindings["total_1"].key == "TD-HF ROOT 1 TOTAL ENERGY"
    assert bindings["moment"].storage == "array"
    bundle = export_bundle(proposal.plan, request, destination=tmp_path / "bundle")
    source = (Path(bundle.directory) / "inputs/workflow.dat").read_text()
    assert "core.variable(" not in source
    assert "array_variable(" not in source
    assert "E_TDM_LEN" in source
    assert bundle.manifest.native_variables == proposal.report.native_variables


@pytest.mark.parametrize(("root", "expected"), [(1, "proved"), (2, "violated")])
def test_solver_links_the_native_total_to_its_own_root_only(
    root: int, expected: str
) -> None:
    """Prove the exact total/reference/gap identity without collapsing roots.

    Args:
        root: Gap used in the independent identity for root one's native total.
        expected: Independently expected proof status.
    """
    request = _spectrum()
    proposal = propose(request)
    assert proposal.plan is not None
    plan = Plan(
        molecules=proposal.plan.molecules,
        steps=proposal.plan.steps,
        requirements=(
            *proposal.plan.requirements,
            EnergyFormula(
                result="total_1",
                terms=(
                    EnergyTerm(result="response", coefficient=1),
                    EnergyTerm(result=f"gap_{root}", coefficient=1),
                ),
            ),
        ),
    )

    report = verify(plan, request=request)

    assert report.status == expected
    checked = next(
        item
        for item in report.obligations
        if item.path == ("requirements", len(plan.requirements) - 1)
    )
    assert bool(checked.counterexample) == (root == 2)


@pytest.mark.parametrize(
    ("method", "reference", "spin"),
    [
        ("td-hf", "rhf", "singlet"),
        ("td-scf", "rhf", "triplet"),
        ("td-hf", "rhf", "both"),
        ("td-hf", "uhf", "unrestricted"),
        ("td-pbe", "rhf", "singlet"),
        ("td-b3lyp", "rhf", "singlet"),
    ],
)
def test_reviewed_reference_sectors_and_equations_construct(
    method: str,
    reference: Literal["rhf", "uhf"],
    spin: Literal["singlet", "triplet", "both", "unrestricted"],
) -> None:
    """Use source contracts for HF and supported density-functional response.

    Args:
        method: Native response method.
        reference: Explicit ground-reference orbital treatment.
        spin: Requested response sector.
    """
    model = Model(
        method=method,
        basis="cc-pvdz",
        reference=reference,
        tdscf=TDSCFAnalysis(states=2, spin=spin, approximation="tda"),
        settings=(Setting(name="scf_type", value="PK"),),
    )

    proposal = propose(_request(model))

    assert proposal.report is not None
    assert proposal.report.request_complete, proposal.report.diagnostics


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (
            ("goals", 0, "quantity"),
            {"meaning": "excitation_energy", "unit": "hartree"},
            "quantity_type",
        ),
        (("goals", 0, "models", 0, "tdscf", "spin"), "unrestricted", "tdscf_spin"),
        (("goals", 0, "models", 0, "method"), "hf", "tdscf_method"),
        (("goals", 0, "models", 0, "frozen_core"), True, "tdscf_core"),
        (("goals", 1, "electronic_target"), None, "tdscf_product_context"),
        (("goals", 1, "electronic_target", "root"), 3, "tdscf_product_root"),
        (("goals", 1, "electronic_target", "multiplicity"), 3, "tdscf_product_spin"),
        (("goals", 1, "electronic_target", "symmetry"), "A", "tdscf_product_symmetry"),
        (("goals", 6, "terms", 0, "coefficient"), 2, "excited_total_formula"),
    ],
)
def test_independent_scientific_contracts_reject_self_consistent_errors(
    path: tuple[str | int, ...], value: JsonValue, code: str
) -> None:
    """Reject altered root context, return meaning, or total-energy algebra.

    Args:
        path: Scientifically consequential request field.
        value: Independently invalid or unsupported choice.
        code: Expected located contract diagnostic.
    """
    request = _edit(_spectrum(), path, value)

    proposal = propose(request)

    assert proposal.plan is None
    assert proposal.report is not None
    assert code in {item.code for item in proposal.report.diagnostics}


def test_changed_product_root_cannot_cover_an_independent_request() -> None:
    """Require the plan to retain the requested root even when its type matches."""
    request = _spectrum()
    proposal = propose(request)
    assert proposal.plan is not None
    plan = _edit(proposal.plan, ("steps", 1, "electronic_target", "root"), 2)

    report = verify(plan, request=request)

    assert not report.request_complete
    assert any(item.status == "incompatible" for item in report.coverage)


@pytest.mark.parametrize(
    ("spin", "states", "accepted"),
    [
        ("singlet", 1, True),
        ("singlet", 2, False),
        ("both", 2, True),
        ("both", 3, False),
    ],
)
def test_root_count_fits_the_reference_single_excitation_space(
    spin: Literal["singlet", "both"], states: int, accepted: bool
) -> None:
    """Use independently known H2/STO-3G occupied/virtual dimensions.

    Args:
        spin: One restricted sector or both sectors.
        states: Total requested roots.
        accepted: Expected capacity outcome for one occupied and one virtual orbital.
    """
    model = Model(
        method="td-hf",
        basis="sto-3g",
        reference="rhf",
        tdscf=TDSCFAnalysis(states=states, spin=spin),
        settings=(Setting(name="scf_type", value="PK"),),
    )

    proposal = propose(_request(model))

    assert (proposal.plan is not None) == accepted
    if not accepted:
        assert proposal.report is not None
        assert "tdscf_root_capacity" in {
            item.code for item in proposal.report.diagnostics
        }


@pytest.mark.parametrize("states", [(0, 0), (-1, 2), (1,), 0])
def test_root_allocation_cannot_be_empty_or_ambiguous(
    states: tuple[int, ...] | int,
) -> None:
    """Reject empty/negative sectors and one-entry tuples that native code unwraps.

    Args:
        states: Invalid total or per-irrep request.
    """
    with pytest.raises(ValidationError):
        TDSCFAnalysis(states=states)


def test_finite_studies_preserve_root_selectors_and_native_frames() -> None:
    """Namespace independent response cases without changing their requested roots."""
    request = _spectrum()
    study = finite_study(
        request,
        (
            StudyCase(id="first", molecules=request.molecules),
            StudyCase(id="second", molecules=request.molecules),
        ),
    )

    proposal = propose(study)

    assert proposal.report is not None
    assert proposal.report.request_complete, proposal.report.diagnostics
    products = (
        [step for step in proposal.plan.steps if isinstance(step, Product)]
        if proposal.plan
        else []
    )
    assert {
        step.electronic_target.root for step in products if step.electronic_target
    } == {1, 2}
    assert len(proposal.report.native_variables) == 10


def test_schema_exposes_equations_and_irrep_allocation() -> None:
    """Discover only the response intent fields needed by the current task."""
    schema = describe_schema(
        "request", definition="TDSCFAnalysis", fields=("states", "approximation")
    )

    assert {item.name for item in schema.fields} == {"states", "approximation"}


@pytest.mark.parametrize(
    ("group", "states", "status"),
    [
        ("c2v", [1, 0, 0, 0], "constructed"),
        ("c1", [1, 0], "no_candidate"),
        (None, [1, 0], "unknown"),
    ],
)
def test_per_irrep_requests_need_the_declared_computational_group(
    group: str | None, states: list[int], status: str
) -> None:
    """Keep root-vector size and explicit symmetry intent consistent.

    Args:
        group: Known computational point group, or native automatic symmetry.
        states: Counts in native irrep order.
        status: Expected construction outcome.
    """
    request = _edit(
        _request(_model()),
        ("goals", 0, "models", 0, "tdscf", "states"),
        _JSON.validate_python(states),
    )
    request = _edit(request, ("molecules", 0, "geometry", "symmetry"), group)

    proposal = propose(request)

    assert proposal.status == status, proposal.diagnostics


def test_density_functional_products_use_the_native_generic_dft_namespace() -> None:
    """Declare target variables without depending on a functional's internal alias."""
    request = _edit(_spectrum(), ("goals", 0, "models", 0, "method"), "td-pbe")

    proposal = propose(request)

    assert proposal.report is not None
    assert proposal.report.request_complete
    assert all(
        item.key.startswith("TD-DFT ") for item in proposal.report.native_variables
    )


@pytest.mark.parametrize(("different", "count"), [(False, 1), (True, 2)])
def test_permitted_reuse_preserves_the_entire_response_root_set(
    different: bool, count: int
) -> None:
    """Share matching responses without shrinking an independently requested root set.

    Args:
        different: Whether the second goal requests another root count.
        count: Independently expected number of top-level calls.
    """
    request = _edit(_request(_model()), ("goals", 0, "reuse_group"), "allowed")
    first = request.goals[0]
    other = _edit(first, ("id",), "other")
    if different:
        other = _edit(other, ("models", 0, "tdscf", "states"), 3)
    request = ScientificRequest(molecules=request.molecules, goals=(first, other))

    proposal = propose(request)

    assert proposal.plan is not None
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == count


def test_response_scientific_fields_cannot_be_overridden_by_native_settings() -> None:
    """Keep root allocation and equations in the independently typed model."""
    with pytest.raises(ValidationError, match="dedicated fields"):
        Model(
            method="td-hf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="TDSCF_STATES", module="SCF", value=(9,)),),
        )


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native option dispatch without solving response",
)
def test_native_response_options_are_scoped_and_the_driver_return_stays_ground_energy(
    tmp_path: Path,
) -> None:
    """Observe native response settings without running the response solver.

    Args:
        tmp_path: Isolated native scratch and output directory.
    """
    model = Model(
        method="td-hf",
        basis="cc-pvdz",
        reference="rhf",
        tdscf=TDSCFAnalysis(
            states=2,
            spin="triplet",
            approximation="tda",
            residual_threshold=1e-6,
            max_iterations=35,
        ),
        settings=(Setting(name="scf_type", value="PK"),),
    )
    request = _request(model)
    request = ScientificRequest(
        molecules=request.molecules,
        goals=(
            *request.goals,
            ProductGoal(
                id="moment",
                calculation="response",
                name="electric_transition_dipole_length",
                electronic_target=ElectronicTarget(root=1, multiplicity=3),
            ),
        ),
    )
    proposal = propose(request)
    assert proposal.plan is not None
    program = """import os, sys, psi4
psi4.core.set_output_file('native-tdscf.dat', False)
psi4.core.IOManager.shared_object().set_default_path(os.getcwd() + os.sep)
psi4.core.set_local_option('SCF', 'TDSCF_STATES', [7])
psi4.core.set_local_option('SCF', 'TDSCF_TRIPLETS', 'ALSO')
psi4.core.set_local_option('SCF', 'TDSCF_TDM_PRINT', ['M_TDM'])
calls = []
def energy(method, molecule, **kwargs):
    assert method == 'td-hf'
    assert psi4.core.get_option('SCF', 'TDSCF_STATES') == [2]
    assert psi4.core.get_option('SCF', 'TDSCF_TRIPLETS') == 'ONLY'
    assert psi4.core.get_option('SCF', 'TDSCF_TDA')
    assert psi4.core.get_option('SCF', 'TDSCF_R_CONVERGENCE') == 1e-6
    assert psi4.core.get_option('SCF', 'TDSCF_MAXITER') == 35
    assert psi4.core.get_option('SCF', 'TDSCF_TDM_PRINT') == ['E_TDM_LEN']
    calls.append(method)
    return 0.0
psi4.energy = energy
source = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(source, '<native-tdscf>', 'exec'), {'psi4': psi4})
assert calls == ['td-hf']
assert psi4.core.get_local_option('SCF', 'TDSCF_STATES') == [7]
assert psi4.core.get_local_option('SCF', 'TDSCF_TRIPLETS') == 'ALSO'
assert psi4.core.get_local_option('SCF', 'TDSCF_TDM_PRINT') == ['M_TDM']
print('native response dispatch checked')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit native interpreter, response driver replaced.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(proposal.plan, request=request),
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        timeout=45,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("native response dispatch checked")
