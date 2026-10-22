"""Require explicit solvent construction and independently checked energy shifts."""

import json
import os
import subprocess
from pathlib import Path
from typing import Literal

import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    CapabilityQuery,
    ComponentCapability,
    DDXSolvation,
    Environment,
    EnvironmentCapability,
    Evidence,
    ExpressionGoal,
    GoalTerm,
    MethodCapability,
    Model,
    OptionCapability,
    OptionCondition,
    PlanningWorkspace,
    QuantityType,
    ScientificRequest,
    Setting,
    StudyCase,
    describe_schema,
    export_bundle,
    finite_study,
    load_catalog,
    propose,
    render,
    verify,
)
from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import BasisCapability, BasisFunctions

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


def _request() -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="solvated",
                driver="energy",
                geometry="h2",
                models=(
                    Model(
                        method="hf",
                        basis="sto-3g",
                        reference="rhf",
                        environment=Environment(
                            kind="ddx",
                            solvent="water",
                            settings=(Setting(name="ddx_lmax", module="DDX", value=6),),
                        ),
                    ),
                ),
            ),
        ),
    )


def _profile() -> CapabilityCatalog:
    return CapabilityCatalog(
        id="synthetic-solvent",
        evidence=(
            Evidence(
                id="fixture",
                source="Synthetic solvent test declarations",
                kind="declaration",
                application_version="fixture/1",
            ),
        ),
        methods=(
            MethodCapability(
                method="hf",
                driver="energy",
                reference="rhf",
                status="supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                features=("ddx", "ddx_model:pcm", "ddx_model:cosmo", "ddx_model:lpb"),
                options=(
                    "ddx.ddx_lmax",
                    "ddx.ddx_model",
                    "ddx.ddx_solvent",
                    "ddx.ddx_radii_set",
                    "ddx.ddx_radii_scaling",
                    "ddx.ddx_solvent_epsilon",
                    "ddx.ddx_solvent_kappa",
                ),
                components=("pyddx",),
                evidence=("fixture",),
            ),
        ),
        bases=(
            BasisCapability(
                name="sto-3g",
                status="supported",
                elements=("H",),
                functions=(BasisFunctions(element="H", spherical=1, cartesian=1),),
                evidence=("fixture",),
            ),
        ),
        options=(
            OptionCapability(
                name="ddx_solvent",
                module="DDX",
                status="supported",
                types=("string",),
                evidence=("fixture",),
            ),
            *(
                OptionCapability(
                    name=name,
                    module="DDX",
                    status="supported",
                    values=values,
                    evidence=("fixture",),
                )
                for name, values in (
                    ("ddx_model", ("pcm", "cosmo", "lpb")),
                    ("ddx_radii_set", ("uff",)),
                )
            ),
            *(
                OptionCapability(
                    name=name,
                    module="DDX",
                    status="supported",
                    types=("real",),
                    minimum=minimum,
                    evidence=("fixture",),
                )
                for name, minimum in (
                    ("ddx_radii_scaling", 0),
                    ("ddx_solvent_epsilon", 1),
                    ("ddx_solvent_kappa", 0),
                )
            ),
            OptionCapability(
                name="ddx_lmax",
                module="DDX",
                status="supported",
                types=("integer",),
                minimum=0,
                evidence=("fixture",),
            ),
        ),
        components=(
            ComponentCapability(
                name="pyddx",
                version="fixture/1",
                status="supported",
                evidence=("fixture",),
            ),
        ),
        environments=(
            EnvironmentCapability(
                kind="ddx",
                radii_set="uff",
                status="supported",
                elements=("H",),
                solvents=("water",),
                evidence=("fixture",),
            ),
        ),
    )


def test_explicit_ddx_environment_lowers_into_scoped_native_options(
    tmp_path: Path,
) -> None:
    """Construct an evidenced solvent energy with an independent option scope.

    Args:
        tmp_path: Parent of a new input-construction bundle.
    """
    request = _request()

    proposal = propose(request, _profile())

    assert proposal.plan is not None, proposal.diagnostics
    exported = export_bundle(proposal.plan, request, _profile(), tmp_path / "bundle")
    source = (Path(exported.directory) / "inputs/workflow.dat").read_text()
    assert "DDX" in source
    assert "water" in source
    assert any(item.name == "pyddx" for item in exported.manifest.required_components)


def _cycle() -> ScientificRequest:
    request = _request()
    return ScientificRequest(
        molecules=request.molecules,
        goals=(
            CalculationGoal(
                id="vacuum",
                driver="energy",
                geometry="h2",
                models=(Model(method="hf", basis="sto-3g", reference="rhf"),),
            ),
            *request.goals,
            ExpressionGoal(
                id="shift",
                terms=(
                    GoalTerm(goal="solvated", coefficient=1),
                    GoalTerm(goal="vacuum", coefficient=-1),
                ),
                quantity=QuantityType(
                    meaning="electronic_solvation_shift", unit="hartree"
                ),
            ),
        ),
    )


def test_solvation_shift_preserves_one_geometry_and_electronic_treatment() -> None:
    """Prove a vertical electronic shift with its declared energy meaning."""
    request = _cycle()

    proposal = propose(request, _profile())

    assert proposal.plan is not None, proposal.diagnostics
    assert proposal.report is not None
    assert proposal.report.request_complete


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("goals", 2, "terms", 0, "coefficient"), 2, "solvation_formula"),
        (("goals", 2, "terms", 1, "coefficient"), 1, "solvation_formula"),
        (("goals", 0, "models", 0, "frozen_core"), True, "solvation_model"),
        (("goals", 0, "models", 0, "reference"), "uhf", "solvation_model"),
    ],
)
def test_self_consistent_request_cannot_change_the_solvation_contract(
    path: tuple[str | int, ...], value: JsonValue, code: str
) -> None:
    """Reject altered algebra or treatment even when intent and implementation agree.

    Args:
        path: Independent request choice to replace.
        value: Structurally valid replacement.
        code: Expected scientific finding.
    """
    proposal = propose(_edit(_cycle(), path, value), _profile())

    assert proposal.plan is None
    assert proposal.report is not None
    assert any(item.code == code for item in proposal.report.diagnostics)


def test_two_separately_declared_geometries_do_not_establish_a_vertical_shift() -> None:
    """Require shared provenance even when input coordinate arrays match."""
    request = _cycle()
    request = ScientificRequest(
        molecules=(
            *request.molecules,
            molecule("other", request.molecules[0].geometry),
        ),
        goals=request.goals,
    )
    request = _edit(request, ("goals", 0, "geometry"), "other")

    proposal = propose(request, _profile())

    assert proposal.report is not None
    assert any(
        item.code == "solvation_geometry" for item in proposal.report.diagnostics
    )


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("environments",), [], "solvent_tables"),
        (("environments", 0, "elements"), [], "solvent_radii"),
        (("environments", 0, "solvents"), [], "solvent_lookup"),
        (("components", 0, "status"), "unsupported", "component_support"),
        (("methods", 0, "components"), [], "component_support"),
    ],
)
def test_runtime_component_and_table_observations_do_not_block_construction(
    path: tuple[str | int, ...], value: JsonValue, code: str
) -> None:
    """Leave installed component and table availability to the target operator.

    Args:
        path: Capability fact to remove or negate.
        value: Changed evidence.
        code: Expected located finding.
    """
    proposal = propose(_request(), _edit(_profile(), path, value))

    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert not any(item.code == code for item in proposal.report.diagnostics)


def test_explicit_dielectric_does_not_require_a_named_solvent_lookup() -> None:
    """Allow a custom dielectric label while retaining independent cavity evidence."""
    request = _edit(
        _request(), ("goals", 0, "models", 0, "environment", "solvent"), "custom"
    )
    request = _edit(
        request,
        ("goals", 0, "models", 0, "environment", "ddx", "dielectric_constant"),
        12.0,
    )

    proposal = propose(request, _profile())

    assert proposal.plan is not None, proposal.diagnostics


@pytest.mark.parametrize(
    "ddx",
    [
        DDXSolvation(model="cosmo"),
        DDXSolvation(model="lpb", screening_inverse_bohr=0.2),
    ],
)
def test_supported_equilibrium_equations_preserve_explicit_choices(
    ddx: DDXSolvation,
) -> None:
    """Construct separately evidenced COSMO and screened LPB variants.

    Args:
        ddx: Independently chosen continuum parameters.
    """
    request = _edit(
        _request(),
        ("goals", 0, "models", 0, "environment", "ddx"),
        _JSON.validate_json(ddx.model_dump_json()),
    )

    proposal = propose(request, _profile())

    assert proposal.plan is not None, proposal.diagnostics


@pytest.mark.parametrize(
    "document",
    [
        '{"model":"lpb"}',
        '{"model":"pcm","screening_inverse_bohr":0.2}',
        '{"dielectric_constant":0.5}',
        '{"radii_scaling":0.0}',
    ],
)
def test_invalid_continuum_parameters_are_rejected(document: str) -> None:
    """Reject undefined screening or unphysical parameter domains before planning.

    Args:
        document: Invalid continuum choice.
    """
    with pytest.raises(ValidationError):
        DDXSolvation.model_validate_json(document)


def test_anonymous_settings_cannot_override_the_declared_environment() -> None:
    """Prevent opaque option blocks from silently activating a different solvent."""
    with pytest.raises(ValidationError, match="dedicated"):
        Environment(
            kind="ddx",
            solvent="water",
            settings=(Setting(name="ddx_model", value="COSMO"),),
        )
    with pytest.raises(ValidationError, match="dedicated"):
        Model(
            method="hf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="ddx", value=True),),
        )


def test_solvent_derivative_requires_its_own_lowering_contract() -> None:
    """Reject a derivative even if a caller labels its method case supported."""
    request = _edit(_request(), ("goals", 0, "driver"), "gradient")

    proposal = propose(request, _profile())

    assert proposal.report is not None
    assert any(item.code == "solvent_driver" for item in proposal.report.diagnostics)


def test_cavity_contract_excludes_ghost_basis_centers() -> None:
    """Keep ghost basis support separate from real-atom cavity construction."""
    request = _edit(
        _request(), ("molecules", 0, "geometry", "atoms", 0, "nucleus", "ghost"), "at"
    )
    request = _edit(
        request, ("molecules", 0, "geometry", "atoms", 1, "nucleus", "ghost"), "at"
    )

    proposal = propose(request, _profile())

    assert proposal.report is not None
    assert any(
        item.code == "solvent_cavity_centers" for item in proposal.report.diagnostics
    )


def test_pcmsolver_cannot_silently_reinterpret_ddx_settings() -> None:
    """Require separate scientific intent when changing solvent implementations."""
    with pytest.raises(ValidationError, match="dedicated PCM fields"):
        _edit(_request(), ("goals", 0, "models", 0, "environment", "kind"), "pcm")


def test_shared_call_permission_preserves_distinct_dielectric_choices() -> None:
    """Keep separately requested media distinct even when sharing is permitted."""
    request = _edit(_request(), ("goals", 0, "reuse_group"), "allowed")
    first = request.goals[0]
    other = _edit(first, ("id",), "other")
    other = _edit(
        other, ("models", 0, "environment", "ddx", "dielectric_constant"), 12.0
    )
    request = ScientificRequest(molecules=request.molecules, goals=(first, other))

    proposal = propose(request, _profile())

    assert proposal.plan is not None
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == 2
    assert proposal.reuses == ()


def test_relationship_mode_requires_solvent_capability_evidence() -> None:
    """Keep construction unknown without scientific solvent input contracts."""
    proposal = propose(_request(), _profile())
    assert proposal.plan is not None

    report = verify(proposal.plan)

    assert report.status == "unknown"
    assert any(item.code == "capability_catalog" for item in report.diagnostics)


def test_finite_study_keeps_each_case_solvation_context() -> None:
    """Compose two independent vacuum/solvent cycles with mandatory case coverage."""
    request = _cycle()
    study = finite_study(
        request,
        (
            StudyCase(id="one", molecules=request.molecules),
            StudyCase(id="two", molecules=request.molecules),
        ),
    )

    proposal = propose(study, _profile())

    assert proposal.report is not None
    assert proposal.report.request_complete, proposal.report.diagnostics
    assert len(proposal.report.coverage) == 6


def test_reference_binary_missing_library_does_not_block_planning() -> None:
    """Construct from source contracts without requiring the reference installation."""
    request = _edit(
        _request(), ("goals", 0, "models", 0, "environment", "settings"), []
    )
    request = _edit(
        request,
        ("goals", 0, "models", 0, "settings"),
        [{"name": "scf_type", "value": "PK"}],
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert proposal.report.runtime_policy == "operator_managed"
    assert proposal.report.diagnostics == ()


def test_environment_discovery_and_selected_schema_are_compact(tmp_path: Path) -> None:
    """Expose solvent table evidence and typed continuum parameters independently.

    Args:
        tmp_path: Isolated artifact workspace.
    """
    workspace = PlanningWorkspace(tmp_path / "work")
    reference = workspace.import_json("capabilities", _profile().model_dump_json())

    page = workspace.capabilities(
        reference.handle, CapabilityQuery(section="environments", name="DDX", limit=1)
    )
    description = describe_schema(
        "request", definition="DDXSolvation", fields=("screening_inverse_bohr",)
    )

    assert page.total == 1
    assert "uff" in str(page.items)
    assert description.json_schema is not None
    assert description.fields[0].name == "screening_inverse_bohr"


@pytest.mark.parametrize(
    ("units", "expected"), [("angstrom", 0.37794522509156564), ("bohr", 0.2)]
)
def test_screening_capability_conditions_match_the_emitted_geometry_units(
    units: Literal["angstrom", "bohr"], expected: float
) -> None:
    """Match LPB evidence to the actual native option after unit conversion.

    Args:
        units: Native molecule length unit.
        expected: Independently specified screening option in inverse native length.
    """
    request = _edit(_request(), ("molecules", 0, "geometry", "units"), units)
    ddx = DDXSolvation(model="lpb", screening_inverse_bohr=0.2)
    request = _edit(
        request,
        ("goals", 0, "models", 0, "environment", "ddx"),
        _JSON.validate_json(ddx.model_dump_json()),
    )
    condition = OptionCondition(
        name="ddx_solvent_kappa", module="DDX", values=(expected,)
    )
    catalog = _edit(
        _profile(),
        ("methods", 0, "conditions"),
        [_JSON.validate_json(condition.model_dump_json())],
    )

    proposal = propose(request, catalog)

    assert proposal.plan is not None, proposal.diagnostics
    assert proposal.report is not None
    assert proposal.report.required_components[0].name == "pyddx"


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native option dispatch without chemistry execution",
)
@pytest.mark.parametrize("units", ["angstrom", "bohr"])
def test_native_dispatch_applies_and_restores_ddx_options(
    tmp_path: Path, units: Literal["angstrom", "bohr"]
) -> None:
    """Observe native DDX flags and screening through a replaced energy driver.

    Args:
        tmp_path: Isolated native scratch directory.
        units: Native molecule length unit.
    """
    request = _edit(_request(), ("molecules", 0, "geometry", "units"), units)
    ddx = DDXSolvation(
        model="lpb", screening_inverse_bohr=0.2, dielectric_constant=12.0
    )
    request = _edit(
        request,
        ("goals", 0, "models", 0, "environment", "ddx"),
        _JSON.validate_json(ddx.model_dump_json()),
    )
    proposal = propose(request, _profile())
    assert proposal.plan is not None
    program = """import math, os, sys, psi4
from psi4.driver.constants import constants
psi4.core.set_output_file('native-options.dat', False)
psi4.core.IOManager.shared_object().set_default_path(os.getcwd() + os.sep)
psi4.core.set_global_option('DDX', False)
psi4.core.set_local_option('DDX', 'DDX_MODEL', 'COSMO')
calls = []
def energy(method, molecule, **kwargs):
    assert method == 'hf'
    assert psi4.core.get_option('SCF', 'DDX')
    assert not psi4.core.get_option('SCF', 'PCM')
    assert psi4.core.get_option('DDX', 'DDX_MODEL') == 'LPB'
    assert psi4.core.get_option('DDX', 'DDX_SOLVENT') == 'WATER'
    assert psi4.core.get_option('DDX', 'DDX_SOLVENT_EPSILON') == 12.0
    assert psi4.core.get_option('DDX', 'DDX_LMAX') == 6
    factor = constants.bohr2angstroms if molecule.units() == 'Angstrom' else 1
    assert math.isclose(
        psi4.core.get_option('DDX', 'DDX_SOLVENT_KAPPA'), .2 / factor, rel_tol=1e-12)
    calls.append(method)
    return 0.0
psi4.energy = energy
source = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(source, '<native-options>', 'exec'), {'psi4': psi4})
assert calls == ['hf']
assert not psi4.core.get_global_option('DDX')
assert psi4.core.get_local_option('DDX', 'DDX_MODEL') == 'COSMO'
print('native solvent dispatch checked')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit native interpreter; chemistry driver replaced.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(proposal.plan, request=request, catalog=_profile()),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=45,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("native solvent dispatch checked")
