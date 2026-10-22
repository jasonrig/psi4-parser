"""Exercise compact scientific planning through the public command line."""

from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.cli import main
from psi4_parser.formal import (
    CalculationGoal,
    CapabilityCatalog,
    Model,
    Plan,
    Report,
    ScientificRequest,
    Setting,
    load_catalog,
)

_JSON = TypeAdapter(JsonValue)


def _invoke(arguments: list[str]) -> Result:
    return CliRunner().invoke(main, arguments)


def _document(result: Result) -> dict[str, JsonValue]:
    assert result.exit_code == 0, result.output
    value = _JSON.validate_json(result.stdout)
    assert isinstance(value, dict)
    return value


def _inputs(
    folder: Path, catalog: CapabilityCatalog, *, settings: tuple[Setting, ...] = ()
) -> tuple[Path, Path]:
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="energy",
                driver="energy",
                geometry="h2",
                models=(
                    Model(
                        method="scf", basis="sto-3g", reference="rhf", settings=settings
                    ),
                ),
            ),
        ),
    )
    request_path = folder / "request.json"
    profile_path = folder / "capabilities.json"
    request_path.write_text(request.model_dump_json())
    profile_path.write_text(catalog.model_dump_json())
    return request_path, profile_path


def test_cli_uses_shared_contracts_without_capabilities_or_version_selection(
    tmp_path: Path,
) -> None:
    """Construct and export a complete input with only its independent request.

    Args:
        tmp_path: Documents, workspace, and new bundle destination.
    """
    request, _ = _inputs(
        tmp_path, load_catalog(), settings=(Setting(name="scf_type", value="PK"),)
    )
    common = ["formal", "--workspace", str(tmp_path / "workspace")]

    proposal = _document(_invoke([*common, "propose", str(request)]))

    plan = proposal["plan"]
    assert isinstance(plan, dict)
    handle = plan["handle"]
    assert isinstance(handle, str)
    checked = _document(_invoke([*common, "verify", handle, "--request", str(request)]))
    assert checked["request_complete"] is True
    exported = _document(
        _invoke(
            [
                *common,
                "export",
                handle,
                "--request",
                str(request),
                "--destination",
                str(tmp_path / "bundle"),
            ]
        )
    )
    assert exported["status"] == "exported"
    assert "application_version" not in checked


def test_cli_materializes_saved_molecules_before_proposing(tmp_path: Path) -> None:
    """Build a self-contained request from a geometry-free template and a handle.

    Args:
        tmp_path: Saved molecule, template, workspace, and exported bundle.
    """
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    molecular_input = tmp_path / "molecule.json"
    molecular_input.write_text('{"geometry":' + geometry.model_dump_json() + "}")
    common = ["formal", "--workspace", str(tmp_path / "workspace")]

    saved = _document(_invoke([*common, "load", "molecule", str(molecular_input)]))

    handle = saved["handle"]
    assert isinstance(handle, str)
    template: JsonValue = {
        "molecules": [{"name": "hydrogen", "molecule": handle}],
        "goals": [
            {
                "kind": "calculate",
                "id": "energy",
                "driver": "energy",
                "geometry": "hydrogen",
                "models": [
                    {
                        "method": "hf",
                        "basis": "sto-3g",
                        "reference": "rhf",
                        "settings": [{"name": "scf_type", "value": "PK"}],
                    }
                ],
            }
        ],
    }
    template_path = tmp_path / "template.json"
    template_path.write_bytes(_JSON.dump_json(template))
    materialized = _document(_invoke([*common, "request", str(template_path)]))
    request_handle = materialized["handle"]
    assert isinstance(request_handle, str)
    proposal = _document(_invoke([*common, "propose", request_handle]))
    assert proposal["status"] == "constructed"
    request_path = materialized["path"]
    assert isinstance(request_path, str)
    complete = ScientificRequest.model_validate_json(Path(request_path).read_bytes())
    assert complete.molecules == (molecule("hydrogen", geometry),)


def test_cli_constructs_reusable_artifacts_without_printing_proofs(
    tmp_path: Path, formal_profile: CapabilityCatalog
) -> None:
    """Save accepted work and return small references to complete records.

    Args:
        tmp_path: Independent source documents and planning workspace.
        formal_profile: Synthetic capability evidence.
    """
    request, capabilities = _inputs(tmp_path, formal_profile)
    workspace = tmp_path / "workspace"

    document = _document(
        _invoke(
            [
                "formal",
                "--workspace",
                str(workspace),
                "propose",
                str(request),
                "--capabilities",
                str(capabilities),
            ]
        )
    )

    assert document["status"] == "constructed"
    assert "smt2" not in document
    plan_ref = document["plan"]
    assert isinstance(plan_ref, dict)
    plan_path = plan_ref["path"]
    assert isinstance(plan_path, str)
    plan_bytes = Path(plan_path).read_bytes()
    assert Plan.model_validate_json(plan_bytes).steps
    assert "sha256" not in plan_ref
    assert len(Plan.model_validate_json(plan_bytes).steps) == 1
    verification = document["verification"]
    assert isinstance(verification, dict)
    assert verification["request_complete"] is True
    reference = verification["reference"]
    assert isinstance(reference, dict)
    report_path = reference["path"]
    assert isinstance(report_path, str)
    assert Report.model_validate_json(Path(report_path).read_bytes()).request_complete
    assert len(str(document)) < 5000


def test_cli_targets_schema_fields_and_operation_contracts() -> None:
    """Discover a scalar model field without printing unrelated schema definitions."""
    schema = _document(
        _invoke(
            [
                "formal",
                "schema",
                "request",
                "--definition",
                "Model",
                "--field",
                "basis",
            ]
        )
    )
    document = schema["json_schema"]
    assert isinstance(document, dict)
    properties = document["properties"]
    assert isinstance(properties, dict)
    assert set(properties) == {"basis"}
    assert "$defs" not in document

    contracts = _document(_invoke(["formal", "contracts", "--driver", "optimize"]))
    assert contracts["total"] == 1
    assert "future optimized geometry" in str(contracts)


@pytest.mark.parametrize("preference", ["prefer", "avoid"])
def test_cli_ranks_only_authorized_reuse(
    tmp_path: Path, formal_profile: CapabilityCatalog, preference: str
) -> None:
    """Pass the CLI preference and return traceable call counts.

    Args:
        tmp_path: Request and persistent workspace directory.
        formal_profile: Synthetic engine support.
        preference: Try shared or separate implementations first.
    """
    path, capabilities = _inputs(tmp_path, formal_profile)
    base = ScientificRequest.model_validate_json(path.read_bytes())
    goal = base.goals[0]
    assert isinstance(goal, CalculationGoal)
    request = ScientificRequest(
        molecules=base.molecules,
        goals=tuple(
            CalculationGoal(
                id=name,
                driver=goal.driver,
                geometry=goal.geometry,
                models=goal.models,
                reuse_group="same-evaluation",
            )
            for name in ("first", "second")
        ),
    )
    path.write_text(request.model_dump_json())

    document = _document(
        _invoke(
            [
                "formal",
                "--workspace",
                str(tmp_path / "workspace"),
                "propose",
                str(path),
                "--capabilities",
                str(capabilities),
                "--call-reuse",
                preference,
            ]
        )
    )

    assert document["calculation_count"] == (1 if preference == "prefer" else 2)
    assert document["shared_call_count"] == (1 if preference == "prefer" else 0)


def test_cli_discovers_and_saves_a_bundled_profile(tmp_path: Path) -> None:
    """Discover without creating files, then explicitly retain exact-build evidence.

    Args:
        tmp_path: Parent of the initially absent planning workspace.
    """
    directory = tmp_path / "planning"
    common = ["formal", "--workspace", str(directory)]

    catalog = _document(_invoke([*common, "catalogs"]))

    assert catalog["total"] == 1
    assert "psi4" in str(catalog)
    assert not directory.exists()
    loaded = _document(_invoke([*common, "load-catalog", "psi4"]))
    assert loaded["kind"] == "capabilities"
    assert directory.exists()
    invalid = _invoke([*common, "load-catalog", "../unknown"])
    assert invalid.exit_code == 2


def test_cli_verification_keeps_missing_evidence_unknown(
    tmp_path: Path, formal_profile: CapabilityCatalog
) -> None:
    """Return an explicit undecided exit code and preserve the complete report.

    Args:
        tmp_path: Source documents and output workspace.
        formal_profile: Synthetic capability evidence for constructing a candidate.
    """
    request, capabilities = _inputs(tmp_path, formal_profile)
    common = ["formal", "--workspace", str(tmp_path / "workspace")]
    proposal = _document(
        _invoke(
            [
                *common,
                "propose",
                str(request),
                "--capabilities",
                str(capabilities),
            ]
        )
    )
    plan = proposal["plan"]
    assert isinstance(plan, dict)
    handle = plan["handle"]
    assert isinstance(handle, str)

    result = _invoke([*common, "verify", handle, "--request", str(request)])

    assert result.exit_code == 3
    value = _JSON.validate_json(result.stdout)
    assert isinstance(value, dict)
    assert value["status"] == "unknown"
    assert value["request_complete"] is False
    reference = value["reference"]
    assert isinstance(reference, dict)
    report = reference["path"]
    assert isinstance(report, str)
    explained = _document(_invoke([*common, "explain", report, "--limit", "1"]))
    assert isinstance(explained["total"], int)
    assert explained["total"] >= 1
    assert "capability" in str(explained).lower()


def test_cli_export_is_independently_checked_and_never_overwritten(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Export accepted work and preserve the existing bundle on a second request.

    Args:
        tmp_path: Source documents, workspace, and bundle directory.
        formal_profile: Synthetic application declarations.
    """
    request, capabilities = _inputs(tmp_path, formal_profile)
    common = ["formal", "--workspace", str(tmp_path / "workspace")]
    proposed = _document(
        _invoke(
            [
                *common,
                "propose",
                str(request),
                "--capabilities",
                str(capabilities),
            ]
        )
    )
    reference = proposed["plan"]
    assert isinstance(reference, dict)
    handle = reference["handle"]
    assert isinstance(handle, str)
    arguments = [
        *common,
        "export",
        handle,
        "--request",
        str(request),
        "--capabilities",
        str(capabilities),
        "--destination",
        str(tmp_path / "bundle"),
    ]

    exported = _document(_invoke(arguments))

    assert exported["status"] == "exported"
    manifest_path = exported["manifest_path"]
    assert isinstance(manifest_path, str)
    manifest = Path(manifest_path)
    content = manifest.read_bytes()
    repeated = _invoke(arguments)
    assert repeated.exit_code == 2
    assert manifest.read_bytes() == content


def test_cli_input_and_schema_errors_have_usage_exit_status(tmp_path: Path) -> None:
    """Distinguish record and schema input errors from scientific failure.

    Args:
        tmp_path: Invalid request and an isolated workspace.
    """
    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"not": "a scientific request"}')

    loaded = _invoke(
        [
            "formal",
            "--workspace",
            str(tmp_path / "workspace"),
            "load",
            "request",
            str(malformed),
        ]
    )
    duplicate = _invoke(
        [
            "formal",
            "schema",
            "request",
            "--definition",
            "Model",
            "--field",
            "basis",
            "--field",
            "basis",
        ]
    )

    assert loaded.exit_code == 2
    assert loaded.stdout == ""
    assert duplicate.exit_code == 2
    assert "unique" in duplicate.stderr
