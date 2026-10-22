"""Check explicit SAPT intent, fragment contracts, and component handoffs."""

import json
import os
import subprocess
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import (
    Atom,
    Cartesian,
    ElectronicState,
    Molecule,
    Nucleus,
    assemble_fragments,
    molecule,
)
from psi4_parser.formal import (
    AuxiliaryBasis,
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    EnergyFormula,
    EnergyTerm,
    Evidence,
    ExpressionGoal,
    GoalTerm,
    Model,
    OptionCapability,
    Plan,
    ProductCapability,
    ProductGoal,
    SAPTAnalysis,
    ScientificRequest,
    Setting,
    StudyCase,
    discover_products,
    export_bundle,
    finite_study,
    load_catalog,
    product_quantity,
    propose,
    render,
    verify,
)
from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import (
    BasisCapability,
    BasisFunctions,
    MethodCapability,
    Reference,
)
from psi4_parser.formal.products import SAPT_COMPONENTS, SAPT_VARIABLES
from psi4_parser.formal.science import QuantityType

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


def _request(
    *,
    open_shell: bool = False,
    midbond: bool = False,
    reference: Reference = "rhf",
    coupled: bool = True,
) -> ScientificRequest:
    monomer = Molecule.from_xyz(
        "1\nHydrogen\nH 0 0 0\n" if open_shell else "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=2 if open_shell else 1),
    )
    partner = Molecule.from_xyz(
        "1\nHydrogen\nH 0 0 3\n" if open_shell else "2\nHydrogen\nH 0 0 3\nH 0 0 3.8\n",
        state=ElectronicState(charge=0, multiplicity=2 if open_shell else 1),
    )
    parts = [("a", monomer), ("b", partner)]
    if midbond:
        parts.append(
            (
                "mid",
                Molecule(
                    atoms=(
                        Atom(
                            id="g",
                            nucleus=Nucleus(label="H", ghost="at"),
                            coordinates=Cartesian(x=0.0, y=0.0, z=1.5),
                        ),
                    ),
                    state=ElectronicState(charge=0, multiplicity=1),
                ),
            )
        )
    dimer = assemble_fragments(
        *parts, state=ElectronicState(charge=0, multiplicity=3 if open_shell else 1)
    )
    model = Model(
        method="sapt0",
        basis="toy-orbital",
        reference=reference,
        settings=(Setting(name="scf_type", value="PK"),),
        auxiliary_bases=(
            AuxiliaryBasis(role="df_basis_sapt", basis="toy-ri"),
            AuxiliaryBasis(role="df_basis_elst", basis="toy-jk"),
        ),
    )
    return ScientificRequest(
        molecules=(molecule("dimer", dimer),),
        goals=(
            CalculationGoal(
                id="interaction",
                driver="energy",
                geometry="dimer",
                models=(model,),
                sapt=SAPTAnalysis(
                    fragments=("a", "b"),
                    coupled_induction=coupled,
                    midbond_fragment="mid" if midbond else None,
                ),
            ),
        ),
    )


def _profile() -> CapabilityCatalog:
    references: tuple[Reference, ...] = ("rhf", "uhf", "rohf")
    return CapabilityCatalog(
        id="synthetic-sapt",
        evidence=(
            Evidence(
                id="fixture",
                source="Synthetic SAPT test declarations",
                kind="declaration",
                application_version="fixture/1",
            ),
        ),
        methods=tuple(
            MethodCapability(
                method="sapt0",
                driver="energy",
                reference=reference,
                status="supported",
                quantity=QuantityType(meaning="interaction_energy", unit="hartree"),
                features=(
                    "sapt",
                    "sapt_basis:dimer",
                    "sapt_basis:monomer",
                    "sapt_induction:coupled",
                    "sapt_induction:uncoupled",
                    "sapt_midbond",
                    "ghost_centers",
                    "auxiliary_basis:df_basis_sapt",
                    "auxiliary_basis:df_basis_elst",
                ),
                options=("scf_type",),
                evidence=("fixture",),
                products=tuple(
                    ProductCapability(
                        name=name,
                        status="supported",
                        quantity=product_quantity(name),
                        evidence=("fixture",),
                    )
                    for name in SAPT_VARIABLES
                ),
            )
            for reference in references
        ),
        options=(
            OptionCapability(
                name="scf_type",
                status="supported",
                types=("string",),
                values=("PK",),
                evidence=("fixture",),
            ),
        ),
        bases=tuple(
            BasisCapability(
                name=name,
                role=role,
                status="supported",
                elements=("H",),
                functions=(BasisFunctions(element="H", spherical=5, cartesian=5),),
                evidence=("fixture",),
            )
            for name, role in (
                ("toy-orbital", "basis"),
                ("toy-ri", "df_basis_sapt"),
                ("toy-jk", "df_basis_elst"),
            )
        ),
    )


def test_sapt_intent_establishes_interaction_return_and_fragment_context() -> None:
    """Construct one interaction call without calling it an electronic total."""
    request = _request()

    proposal = propose(request, _profile())

    assert proposal.status == "constructed", proposal.diagnostics
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert proposal.report.quantities[0].quantity == QuantityType(
        meaning="interaction_energy", unit="hartree"
    )
    assert proposal.report.quantities[0].sapt == SAPTAnalysis(fragments=("a", "b"))


def _with_products(request: ScientificRequest) -> ScientificRequest:
    return ScientificRequest(
        molecules=request.molecules,
        goals=(
            *request.goals,
            *(
                ProductGoal(id=name, calculation="interaction", name=name)
                for name in SAPT_VARIABLES
            ),
            ExpressionGoal(
                id="sum",
                terms=tuple(
                    GoalTerm(goal=name, coefficient=1) for name in SAPT_COMPONENTS
                ),
                quantity=QuantityType(meaning="interaction_energy", unit="hartree"),
            ),
        ),
    )


def test_native_component_identity_and_declarative_export(tmp_path: Path) -> None:
    """Prove the component partition while leaving collection to another system.

    Args:
        tmp_path: New construction-bundle parent directory.
    """
    request = _with_products(_request())
    proposal = propose(request, _profile())
    assert proposal.plan is not None
    plan = Plan(
        molecules=proposal.plan.molecules,
        steps=proposal.plan.steps,
        requirements=(
            *proposal.plan.requirements,
            EnergyFormula(
                result="interaction",
                terms=tuple(
                    EnergyTerm(result=name, coefficient=1) for name in SAPT_COMPONENTS
                ),
            ),
        ),
    )

    report = verify(plan, request=request, catalog=_profile())
    exported = export_bundle(plan, request, _profile(), tmp_path / "bundle")

    assert report.request_complete, report.diagnostics
    assert all(item.status == "proved" for item in report.obligations)
    assert len(report.native_variables) == 5
    assert report.native_outputs == ()
    assert exported.manifest.native_variables == report.native_variables
    assert {item.key for item in report.native_variables} == set(
        SAPT_VARIABLES.values()
    )
    assert all(
        item.lifetime == "after_producer_before_next_calculation"
        for item in report.native_variables
    )
    source = (Path(exported.directory) / exported.manifest.native_inputs[0]).read_text()
    assert "sapt_basis='dimer'" in source
    assert "COUPLED_INDUCTION" in source
    assert "json.dump" not in source
    assert "core.variable(" not in source
    assert not list(Path(exported.directory).glob("*.qcvars.json"))


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("goals", 0, "sapt", "fragments"), ["b", "a"], "sapt_fragments"),
        (("goals", 0, "sapt"), None, "sapt_context"),
        (("goals", 0, "models", 0, "auxiliary_bases"), [], "sapt_fitting"),
        (("goals", 0, "driver"), "hessian", "sapt_driver"),
        (
            ("goals", 0, "quantity"),
            {"meaning": "electronic_energy", "unit": "hartree"},
            "quantity_type",
        ),
        (
            ("goals", 0, "models", 0, "settings"),
            [{"name": "coupled_induction", "module": "SAPT", "value": False}],
            "sapt_settings",
        ),
    ],
)
def test_sapt_choices_are_checked_against_independent_intent(
    path: tuple[str | int, ...], value: JsonValue, code: str
) -> None:
    """Locate missing context and invalid operation, partition, or routing choices.

    Args:
        path: Independent request field to replace.
        value: Structurally valid replacement.
        code: Expected construction finding.
    """
    proposal = propose(_edit(_request(), path, value), _profile())

    assert proposal.plan is None
    assert proposal.report is not None
    assert any(item.code == code for item in proposal.report.diagnostics)


@pytest.mark.parametrize("coefficient", [0, 2])
def test_self_consistent_wrong_component_sum_is_rejected(coefficient: int) -> None:
    """Reject altered component weights even when all requested algebra agrees.

    Args:
        coefficient: Wrong dispersion weight.
    """
    request = _with_products(_request())
    request = _edit(request, ("goals", 6, "terms", 3, "coefficient"), coefficient)

    proposal = propose(request, _profile())

    assert proposal.plan is None
    assert proposal.report is not None
    assert any(
        item.code == "sapt_component_formula" for item in proposal.report.diagnostics
    )


@pytest.mark.parametrize(("reference", "coupled"), [("uhf", True), ("rohf", False)])
def test_open_shell_sapt_uses_explicit_high_spin_and_induction(
    reference: Reference, coupled: bool
) -> None:
    """Accept declared open-shell monomers at their required high-spin complex.

    Args:
        reference: Explicit unrestricted or restricted-open-shell reference.
        coupled: Compatible induction request.
    """
    proposal = propose(
        _request(open_shell=True, reference=reference, coupled=coupled), _profile()
    )

    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete


def test_low_spin_coupling_is_rejected_even_when_spin_coupling_is_possible() -> None:
    """Reject a singlet complex of doublets under the native high-spin assumption."""
    request = _edit(
        _request(open_shell=True, reference="uhf"),
        ("molecules", 0, "geometry", "state", "multiplicity"),
        1,
    )

    proposal = propose(request, _profile())

    assert proposal.report is not None
    assert any(item.code == "sapt_high_spin" for item in proposal.report.diagnostics)


def test_rohf_induction_choice_cannot_be_silently_overridden() -> None:
    """Reject coupled induction before the native routine could switch it off."""
    proposal = propose(_request(open_shell=True, reference="rohf"), _profile())

    assert proposal.report is not None
    assert any(item.code == "sapt_induction" for item in proposal.report.diagnostics)


def test_midbond_partition_must_remain_all_ghost_and_dimer_centered() -> None:
    """Retain a named third ghost fragment and reject its accidental activation."""
    request = _request(midbond=True)
    accepted = propose(request, _profile())
    assert accepted.plan is not None
    request = _edit(
        request, ("molecules", 0, "geometry", "atoms", 4, "nucleus", "ghost"), "none"
    )

    rejected = propose(request, _profile())

    assert rejected.report is not None
    assert any(item.code == "sapt_centers" for item in rejected.report.diagnostics)
    with pytest.raises(ValueError, match="dimer-centered"):
        SAPTAnalysis(fragments=("a", "b"), basis="monomer", midbond_fragment="mid")


def test_finite_cases_retain_sapt_context_and_declarative_bindings() -> None:
    """Require all case products without adding collection to the native input."""
    template = _with_products(_request())
    request = finite_study(
        template,
        tuple(
            StudyCase(id=name, molecules=template.molecules)
            for name in ("first", "second")
        ),
    )

    proposal = propose(request, _profile())

    assert proposal.plan is not None
    assert proposal.report is not None
    assert len(proposal.report.coverage) == 14
    assert len(proposal.report.native_variables) == 10
    assert {item.producer for item in proposal.report.native_variables} == {
        "first:interaction",
        "second:interaction",
    }


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for SAPT input-state checks",
)
@pytest.mark.parametrize("failure", [False, True])
def test_native_sapt_arguments_and_namespace_restoration(
    tmp_path: Path, failure: bool
) -> None:
    """Observe native input settings and cleanup with a mocked SAPT driver.

    Args:
        tmp_path: Isolated native interpreter directory.
        failure: Raise from the observed driver to check cleanup.
    """
    request = _edit(
        _request(open_shell=True, reference="rohf", coupled=False),
        ("goals", 0, "sapt", "basis"),
        "monomer",
    )
    proposal = propose(request, _profile())
    assert proposal.plan is not None
    program = f"""import sys, psi4
psi4.core.set_output_file('settings.dat', False)
psi4.core.IO.set_default_namespace('ambient')
psi4.core.set_local_option('SAPT', 'COUPLED_INDUCTION', True)
calls = []
namespaces = []
def observe(method, **kwargs):
    assert method == 'sapt0'
    assert kwargs['sapt_basis'] == 'monomer'
    assert not psi4.core.get_option('SAPT', 'COUPLED_INDUCTION')
    calls.append(method)
    namespaces.append(psi4.core.IO.get_default_namespace())
    psi4.core.IO.set_default_namespace('monomerA')
    if {failure!r}:
        raise RuntimeError('deliberate driver failure')
    return 0.0
psi4.energy = observe
source = psi4.process_input(sys.stdin.read(), print_level=0)
try:
    exec(compile(source, '<sapt-settings>', 'exec'), {{'psi4': psi4}})
except RuntimeError as error:
    assert {failure!r} and str(error) == 'deliberate driver failure'
else:
    assert not {failure!r}
assert calls == ['sapt0']
assert psi4.core.IO.get_default_namespace() == namespaces[0]
assert psi4.core.get_local_option('SAPT', 'COUPLED_INDUCTION')
print('SAPT settings restored')
"""

    completed = subprocess.run(  # noqa: S603 - Fixed input-configuration harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(proposal.plan, request=request, catalog=_profile()),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("SAPT settings restored")


def _audited_request(
    *, method: str = "sapt0", algorithm: str = "DF"
) -> ScientificRequest:
    request = _request()
    settings: list[Setting] = [Setting(name="scf_type", value=algorithm)]
    if method.endswith("dmp2"):
        settings.extend(
            (
                Setting(name="mp2_type", value="CONV"),
                Setting(name="qc_module", value="OCC"),
            )
        )
    model = Model(
        method=method,
        basis="cc-pvdz",
        reference="rhf",
        settings=tuple(settings),
        auxiliary_bases=(
            AuxiliaryBasis(role="df_basis_sapt", basis="cc-pvdz-ri"),
            AuxiliaryBasis(role="df_basis_elst", basis="cc-pvdz-jkfit"),
            AuxiliaryBasis(role="df_basis_scf", basis="cc-pvdz-jkfit"),
        ),
    )
    return ScientificRequest(
        molecules=request.molecules,
        goals=(
            CalculationGoal(
                id="interaction",
                driver="energy",
                geometry="dimer",
                models=(model,),
                sapt=SAPTAnalysis(fragments=("a", "b")),
            ),
        ),
    )


@pytest.mark.parametrize(
    ("method", "algorithm"),
    [
        ("sapt0", "DF"),
        ("ssapt0", "PK"),
        ("sapt2+3", "DF"),
        ("sapt2+(3)(ccd)dmp2", "PK"),
    ],
)
def test_reviewed_sapt_cases_use_explicit_role_bindings(
    method: str, algorithm: str
) -> None:
    """Construct supported native families without inferring fitting defaults.

    Args:
        method: Reviewed native method spelling.
        algorithm: Explicit SCF algorithm covered by this case.
    """
    proposal = propose(
        _with_products(_audited_request(method=method, algorithm=algorithm)),
        load_catalog("psi4"),
    )

    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete, proposal.report.diagnostics
    assert any(item.name == "sapt" for item in proposal.report.required_components)


def test_unreviewed_fitting_pairing_stays_unknown() -> None:
    """Keep a mismatched cardinal pairing outside the reviewed method combinations."""
    request = _edit(
        _audited_request(),
        ("goals", 0, "models", 0, "auxiliary_bases", 0, "basis"),
        "cc-pvtz-ri",
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.status == "unknown"
    assert proposal.plan is None


@pytest.mark.parametrize(
    ("field", "value"), [("basis", "monomer"), ("coupled_induction", False)]
)
def test_sharing_permission_preserves_distinct_sapt_choices(
    field: str, value: JsonValue
) -> None:
    """Keep separate calls when permitted reuse has different scientific intent.

    Args:
        field: SAPT choice that distinguishes the second calculation.
        value: Explicit alternative accepted by the synthetic catalog.
    """
    request = _request()
    first = _edit(request.goals[0], ("reuse_group",), "allowed")
    second = _edit(_edit(first, ("id",), "other"), ("sapt", field), value)
    request = ScientificRequest(molecules=request.molecules, goals=(first, second))

    proposal = propose(request, _profile())

    assert proposal.plan is not None
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == 2
    assert proposal.reuses == ()


def test_component_sum_cannot_mix_independent_producers() -> None:
    """Reject a decomposition assembled from two independently computed contexts."""
    request = _with_products(_request())
    other = _edit(request.goals[0], ("id",), "other")
    combined = _edit(request.goals[-1], ("terms", 3, "goal"), "other_dispersion")
    request = ScientificRequest(
        molecules=request.molecules,
        goals=(
            *request.goals[:-1],
            other,
            ProductGoal(
                id="other_dispersion", calculation="other", name="sapt_dispersion"
            ),
            combined,
        ),
    )

    proposal = propose(request, _profile())

    assert proposal.plan is None
    assert proposal.report is not None
    assert any(
        item.code == "sapt_component_formula" for item in proposal.report.diagnostics
    )


def test_relationship_only_sapt_still_requires_application_evidence() -> None:
    """Keep native SAPT context unknown when its capability catalog is omitted."""
    proposal = propose(_request(), _profile())
    assert proposal.plan is not None

    report = verify(proposal.plan)

    assert report.status == "unknown"
    assert report.capability_status == "unknown"
    assert any(item.code == "capability_catalog" for item in report.diagnostics)


def test_product_discovery_preserves_sapt_mode_coverage() -> None:
    """Expose basis and induction evidence alongside the requested product."""
    cases = discover_products(
        load_catalog("psi4"),
        method="sapt0",
        driver="energy",
        name="sapt_total_energy",
    )

    assert any(
        case.reference == "rhf" and "sapt_basis:monomer" in case.features
        for case in cases
    )
    rohf = [case for case in cases if case.reference == "rohf"]
    assert rohf
    assert all("sapt_induction:uncoupled" in case.features for case in rohf)
    assert all("sapt_induction:coupled" not in case.features for case in rohf)


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for a separate native SAPT execution check",
)
def test_reviewed_native_sapt_input_completes_without_result_collection(
    tmp_path: Path,
) -> None:
    """Execute one small input in a separate harness and check only completion.

    Args:
        tmp_path: Isolated native output and scratch directory.
    """
    request = _audited_request()
    catalog = load_catalog("psi4")
    proposal = propose(request, catalog)
    assert proposal.plan is not None
    program = """import os, sys, psi4
psi4.set_num_threads(1)
psi4.set_memory('512 MiB')
psi4.core.set_output_file('native-sapt.dat', False)
psi4.core.IOManager.shared_object().set_default_path(os.getcwd() + os.sep)
source = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(source, '<native-sapt>', 'exec'), {'psi4': psi4})
print('native SAPT input completed')
"""

    completed = subprocess.run(  # noqa: S603 - Separate bounded native execution harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(proposal.plan, request=request, catalog=catalog),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("native SAPT input completed")
