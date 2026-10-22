"""Check PCMSolver input construction without inspecting its installation."""

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
    ComponentCapability,
    DDXSolvation,
    Environment,
    ExpressionGoal,
    GoalTerm,
    Model,
    PCMSolverSolvation,
    QuantityType,
    ScientificRequest,
    Setting,
    describe_schema,
    export_bundle,
    load_catalog,
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
                        settings=(Setting(name="scf_type", value="PK"),),
                        environment=Environment(kind="pcm", solvent="Water"),
                    ),
                ),
            ),
        ),
    )


def test_pcmsolver_plan_needs_no_local_library_or_version() -> None:
    """Construct equilibrium input from scientific source contracts alone."""
    request = _request()
    catalog = load_catalog("psi4")

    proposal = propose(request, catalog)

    assert proposal.plan is not None, proposal.diagnostics
    assert proposal.report is not None
    assert proposal.report.request_complete, proposal.report.diagnostics
    assert proposal.report.runtime_policy == "operator_managed"
    assert proposal.report.diagnostics == ()
    assert [
        (item.name, item.version) for item in proposal.report.required_components
    ] == [("pcmsolver", None)]
    assert "PCM__INPUT" in render(proposal.plan, request=request, catalog=catalog)


@pytest.mark.parametrize("status", ["supported", "unsupported", "unknown"])
def test_pcmsolver_runtime_observations_never_change_acceptance(
    status: Literal["supported", "unsupported", "unknown"],
    recwarn: pytest.WarningsRecorder,
) -> None:
    """Ignore absent, differing, or unreviewed component installation metadata.

    Args:
        status: Optional observation about a reference installation.
        recwarn: All warnings emitted during construction.
    """
    catalog = load_catalog("psi4")
    component = ComponentCapability(
        name="pcmsolver",
        status=status,
        version="unrelated",
        evidence=("runtime-metadata",),
    )
    catalog = _edit(
        catalog, ("components",), [_JSON.validate_json(component.model_dump_json())]
    )

    proposal = propose(_request(), catalog)

    assert proposal.report is not None
    assert proposal.report.request_complete
    assert proposal.report.diagnostics == ()
    assert proposal.report.required_components[0].version is None
    assert list(recwarn) == []


def test_pcm_text_uses_atomic_units_and_explicit_equilibrium_choices() -> None:
    """Keep solvent parameters independent from the molecule's coordinate units."""
    medium = PCMSolverSolvation(
        solver="cpcm",
        dielectric_constant=12,
        probe_radius_bohr=2.5,
        radii_set="bondi",
        scale_radii=True,
        surface_area_bohr2=0.5,
        cpcm_correction=0.5,
    )

    text = medium.input_text("descriptive label")

    assert text == (
        "Units = AU\nMedium {\n  SolverType = CPCM\n  Solvent = Explicit\n"
        "  Nonequilibrium = False\n  DiagonalIntegrator = Collocation\n"
        "  DiagonalScaling = 1.07\n  Correction = 0.5\n  ProbeRadius = 2.5\n"
        "  Green<inside> { Type = Vacuum }\n  Green<outside> {\n"
        "    Type = UniformDielectric\n    Eps = 12.0\n  }\n}\nCavity {\n"
        "  Type = GePol\n  Mode = Implicit\n  RadiiSet = BONDI\n"
        "  Scaling = True\n  Area = 0.5\n}\n"
    )


@pytest.mark.parametrize(
    "parameters",
    [
        {"dielectric_constant": 12},
        {"probe_radius_bohr": 2},
        {"surface_area_bohr2": 0.009},
        {"dielectric_constant": 0.9, "probe_radius_bohr": 2},
        {"dielectric_constant": 12, "probe_radius_bohr": 0.01},
        {"cpcm_correction": 0.5},
        {"solver": "cpcm", "cpcm_correction": -0.5},
    ],
)
def test_pcm_choices_reject_incomplete_or_inapplicable_inputs(
    parameters: dict[str, JsonValue],
) -> None:
    """Require physically meaningful ranges and all explicit-medium parameters.

    Args:
        parameters: An independently invalid solver/cavity choice.
    """
    with pytest.raises(ValidationError):
        PCMSolverSolvation.model_validate_json(json.dumps(parameters))


@pytest.mark.parametrize(
    "solvent", ["Explicit", "Water\nScaling = True", "Water }", "Water#"]
)
def test_pcm_table_names_cannot_inject_solver_configuration(solvent: str) -> None:
    """Treat the solvent name as data while leaving table availability to Psi4.

    Args:
        solvent: A reserved selector or a name containing solver syntax.
    """
    with pytest.raises(ValidationError, match="plain solvent name"):
        Environment(kind="pcm", solvent=solvent)


def test_unknown_named_solvent_needs_no_installed_catalogue() -> None:
    """Pass a syntactically valid native lookup to the eventual execution host."""
    request = _edit(
        _request(), ("goals", 0, "models", 0, "environment", "solvent"), "MySolvent"
    )

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.report is not None
    assert proposal.report.request_complete
    assert proposal.report.diagnostics == ()


def test_inactive_solver_choices_and_raw_pcm_overrides_are_rejected() -> None:
    """Prevent ignored inputs and native options that bypass typed solvent intent."""
    with pytest.raises(ValidationError, match="DDX settings"):
        Environment(kind="pcm", solvent="Water", ddx=DDXSolvation(model="cosmo"))
    with pytest.raises(ValidationError, match="kind pcm"):
        Environment(kind="ddx", solvent="Water", pcm=PCMSolverSolvation(solver="cpcm"))
    with pytest.raises(ValidationError, match="dedicated PCM fields"):
        Environment(
            kind="pcm",
            solvent="Water",
            settings=(Setting(name="pcm_scf_type", value="separate"),),
        )
    with pytest.raises(ValidationError, match="dedicated fields"):
        Model(
            method="hf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="PCM__INPUT", value="opaque text"),),
        )


def _cycle() -> ScientificRequest:
    request = _request()
    first = request.goals[0]
    vacuum = _edit(first, ("id",), "vacuum")
    vacuum = _edit(vacuum, ("models", 0, "environment"), None)
    return ScientificRequest(
        molecules=request.molecules,
        goals=(
            first,
            vacuum,
            ExpressionGoal(
                id="shift",
                quantity=QuantityType(
                    meaning="electronic_solvation_shift", unit="hartree"
                ),
                terms=(
                    GoalTerm(goal="solvated", coefficient=1),
                    GoalTerm(goal="vacuum", coefficient=-1),
                ),
            ),
        ),
    )


def test_pcm_cycle_exports_with_independently_checked_shift(tmp_path: Path) -> None:
    """Export two driver calls and a symbolic solvent-minus-vacuum relationship.

    Args:
        tmp_path: Parent of the new construction bundle.
    """
    request = _cycle()
    catalog = load_catalog("psi4")
    proposal = propose(request, catalog)

    assert proposal.plan is not None
    bundle = export_bundle(proposal.plan, request, catalog, tmp_path / "bundle")
    source = (Path(bundle.directory) / "inputs/workflow.dat").read_text()
    assert source.count("PCM__INPUT") == 1
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == 2
    assert bundle.manifest.runtime_policy == "operator_managed"
    assert verify(proposal.plan, request=request, catalog=catalog).request_complete


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (("goals", 2, "terms", 0, "coefficient"), -1, "solvation_formula"),
        (("goals", 1, "models", 0, "basis"), "cc-pvdz", "solvation_model"),
        (("goals", 1, "geometry"), "other", "solvation_geometry"),
        (("goals", 0, "models", 0, "reference"), "rohf", "solvent_reference"),
    ],
)
def test_pcm_rejects_scientific_errors_even_in_self_consistent_requests(
    path: tuple[str | int, ...], value: JsonValue, code: str
) -> None:
    """Keep mathematical intent and source construction coverage independently checked.

    Args:
        path: Request field changed before planning.
        value: Scientifically incompatible choice.
        code: Independently expected contract finding.
    """
    request = _cycle()
    request = ScientificRequest(
        molecules=(
            *request.molecules,
            molecule("other", request.molecules[0].geometry),
        ),
        goals=request.goals,
    )
    request = _edit(request, path, value)

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is None
    assert proposal.report is not None
    assert code in {item.code for item in proposal.report.diagnostics}


def test_pcm_derivative_requires_a_separate_scientific_contract() -> None:
    """Keep the current equilibrium energy lowerer separate from derivative plans."""
    request = _edit(_request(), ("goals", 0, "driver"), "gradient")

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.report is not None
    assert "solvent_driver" in {item.code for item in proposal.report.diagnostics}


def test_pcm_schema_discovery_exposes_cavity_units() -> None:
    """Expose the new public choices through existing compact schema discovery."""
    description = describe_schema(
        "request", definition="PCMSolverSolvation", fields=("surface_area_bohr2",)
    )

    assert description.fields[0].name == "surface_area_bohr2"
    assert "square bohr" in str(description.fields[0])


@pytest.mark.parametrize(("different", "count"), [(False, 1), (True, 2)])
def test_pcm_reuse_respects_the_complete_cavity_model(
    different: bool, count: int
) -> None:
    """Share matching permitted calls while retaining distinct tessellation choices.

    Args:
        different: Whether the second goal changes the requested surface area.
        count: Independent expected number of driver calls.
    """
    request = _edit(_request(), ("goals", 0, "reuse_group"), "permitted")
    first = request.goals[0]
    other = _edit(first, ("id",), "other")
    if different:
        other = _edit(
            other, ("models", 0, "environment", "pcm", "surface_area_bohr2"), 0.6
        )
    request = ScientificRequest(molecules=request.molecules, goals=(first, other))

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.plan is not None
    assert sum(isinstance(step, Calculation) for step in proposal.plan.steps) == count


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native scope tests without chemistry execution",
)
@pytest.mark.parametrize("failure", ["none", "parser", "driver"])
def test_native_pcm_scopes_restore_options_and_dispatch_only_at_execution(
    tmp_path: Path, failure: Literal["none", "parser", "driver"]
) -> None:
    """Use Psi4's real helper with a parser double and a replaced energy driver.

    Args:
        tmp_path: Isolated scratch directory for the native helper.
        failure: Boundary to fail deliberately, or none for a complete cycle.
    """
    request = _cycle()
    catalog = load_catalog("psi4")
    proposal = propose(request, catalog)
    assert proposal.plan is not None
    program = """import os, pathlib, sys, tempfile, types, psi4
tempfile.tempdir = os.getcwd()
psi4.core.set_output_file('scope-output.dat', False)
psi4.core.IOManager.shared_object().set_default_path(os.getcwd() + os.sep)
psi4.core.set_global_option('PCM', True)
psi4.core.set_local_option('PCM', 'PCMSOLVER_PARSED_FNAME', 'ambient')
psi4.core.set_local_option('PCM', 'PCM_SCF_TYPE', 'SEPARATE')
failure = sys.argv[1]
calls = []
parses = []
def parse(path):
    text = pathlib.Path(path).read_text()
    assert 'Units = AU' in text
    assert 'SolverType = IEFPCM' in text
    assert 'Solvent = Water' in text
    assert 'Area = 0.3' in text
    parses.append(text)
    if failure == 'parser':
        raise ValueError('intentional parser failure')
    return 'parsed input marker'
module = types.ModuleType('pcmsolver')
module.parse_pcm_input = parse
sys.modules['pcmsolver'] = module
def energy(method, molecule, **kwargs):
    assert method == 'hf'
    assert not psi4.core.get_option('SCF', 'DDX')
    active = psi4.core.get_option('SCF', 'PCM')
    path = psi4.core.get_local_option('PCM', 'PCMSOLVER_PARSED_FNAME')
    if active:
        assert pathlib.Path(path).read_text() == 'parsed input marker'
        assert psi4.core.get_option('PCM', 'PCM_SCF_TYPE') == 'TOTAL'
    else:
        assert path == ''
    calls.append(active)
    if failure == 'driver':
        raise RuntimeError('intentional driver failure')
    return 0.0
psi4.energy = energy
source = psi4.process_input(sys.stdin.read(), print_level=0)
assert not parses, 'construction must not invoke the optional parser'
try:
    exec(compile(source, '<pcm-scope>', 'exec'), {'psi4': psi4})
except (ValueError, RuntimeError) as error:
    assert failure != 'none' and str(error).startswith('intentional')
else:
    assert failure == 'none'
    assert calls == [True, False]
assert len(parses) == 1
assert psi4.core.get_global_option('PCM')
assert psi4.core.get_local_option('PCM', 'PCMSOLVER_PARSED_FNAME') == 'ambient'
assert psi4.core.has_local_option_changed('PCM', 'PCMSOLVER_PARSED_FNAME')
assert psi4.core.get_local_option('PCM', 'PCM_SCF_TYPE') == 'SEPARATE'
print('native PCM scope checked')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit native interpreter; chemistry driver replaced.
        [os.environ["PSI4_PYTHON"], "-c", program, failure],
        input=render(proposal.plan, request=request, catalog=catalog),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=45,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("native PCM scope checked")
