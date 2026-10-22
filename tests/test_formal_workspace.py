"""Check reusable records, compact explanations, and independent export acceptance."""

import hashlib
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import JsonValue

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    CapabilityCatalog,
    CapabilityQuery,
    Model,
    PlanningWorkspace,
    Proposal,
    SameModel,
    ScientificRequest,
    Setting,
    describe_schema,
    load_catalog,
)


def _request(count: int = 1) -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=tuple(
            CalculationGoal(
                id=f"energy_{index}", driver="energy", geometry="h2", models=(model,)
            )
            for index in range(count)
        ),
    )


def test_imported_records_are_stable_copies_and_hash_checked(tmp_path: Path) -> None:
    """Retain input identity after source edits and reject modified cached bytes.

    Args:
        tmp_path: External request file and persistent workspace.
    """
    request = _request()
    path = tmp_path / "request.json"
    path.write_text(request.model_dump_json())
    workspace = PlanningWorkspace(tmp_path / "work")

    reference = workspace.import_file("request", path)
    same = workspace.import_json("request", request.model_dump_json(indent=2))

    assert reference == same
    assert (
        reference.sha256
        == hashlib.sha256(Path(reference.path).read_bytes()).hexdigest()
    )
    path.write_text("changed original")
    reopened = PlanningWorkspace(workspace.directory)
    assert reopened.reference(reference.handle) == reference
    with pytest.raises(ValueError, match="Expected plan"):
        reopened.resolve("plan", reference.handle)
    Path(reference.path).write_text("changed cached bytes")
    with pytest.raises(ValueError, match="content no longer matches"):
        reopened.reference(reference.handle)


@pytest.mark.parametrize("source", [False, True])
def test_record_limits_are_enforced_before_parsing(
    tmp_path: Path, source: bool
) -> None:
    """Reject excessive file or inline input without creating a saved record.

    Args:
        tmp_path: Workspace and oversized input path.
        source: Use inline JSON rather than a local input file.
    """
    workspace = PlanningWorkspace(tmp_path / "work", max_record_bytes=5)
    path = tmp_path / "too-big.json"
    path.write_text(" " * 20)

    if source:
        with pytest.raises(ValueError, match="5-byte limit"):
            workspace.import_json("request", " " * 20)
    else:
        with pytest.raises(ValueError, match="5-byte limit"):
            workspace.import_file("request", path)

    assert not list((workspace.directory / "records").iterdir())


def test_invalid_request_diagnostics_point_to_saved_intent(tmp_path: Path) -> None:
    """Expose a repairable request location without a rejected candidate graph.

    Args:
        tmp_path: Workspace retaining the request, proposal, and explanation.
    """
    original = _request()
    request = ScientificRequest(
        molecules=original.molecules,
        goals=original.goals,
        relations=(SameModel(calculations=("energy_0", "h2")),),
    )
    workspace = PlanningWorkspace(tmp_path / "work")
    reference = workspace.import_json("request", request.model_dump_json())

    summary = workspace.propose(reference.handle)
    page = workspace.explain(summary.proposal.handle)

    assert summary.status == "invalid"
    assert summary.attempts == 0
    assert summary.plan is None
    assert summary.verification is None
    assert page.total == 1
    item = page.items[0]
    assert item.path == ("request", "relations", 0, "calculations", 1)
    assert item.record_path == ("diagnostics", 0)
    saved = Proposal.model_validate_json(Path(summary.proposal.path).read_bytes())
    assert item.path == saved.diagnostics[0].path


def test_summary_and_pages_retain_all_mandatory_work(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Bound response size while retaining complete evidence and every coverage entry.

    Args:
        tmp_path: Workspace for a moderately sized finite request.
        formal_profile: Synthetic application evidence.
    """
    workspace = PlanningWorkspace(tmp_path / "work")
    request = workspace.import_json("request", _request(32).model_dump_json())
    catalog = workspace.import_json("capabilities", formal_profile.model_dump_json())

    summary = workspace.propose(request.handle, catalog.handle)

    assert summary.status == "constructed"
    assert summary.choice_count == 32
    assert len(summary.choices) == 10
    assert len(summary.model_dump_json()) < 8000
    assert Path(summary.proposal.path).stat().st_size > 10 * len(
        summary.model_dump_json()
    )
    assert summary.verification is not None
    assert summary.verification.coverage == {"covered": 32}
    offset = 0
    covered: list[str] = []
    while True:
        page = workspace.explain(
            summary.proposal.handle, section="coverage", offset=offset, limit=7
        )
        covered.extend(str(item.path[-1]) for item in page.items)
        if page.next_offset is None:
            break
        offset = page.next_offset
    assert covered == [f"energy_{index}" for index in range(32)]
    last_choices = workspace.explain(
        summary.proposal.handle, section="choices", offset=30, limit=5
    )
    assert last_choices.total == 32
    assert len(last_choices.items) == 2


def test_export_reverifies_the_independent_request_and_preserves_existing_files(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Reject omitted work and refuse overwrites after an accepted proposal.

    Args:
        tmp_path: Persistent record workspace and bundle destinations.
        formal_profile: Synthetic application declarations.
    """
    workspace = PlanningWorkspace(tmp_path / "work")
    request = workspace.import_json("request", _request().model_dump_json())
    catalog = workspace.import_json("capabilities", formal_profile.model_dump_json())
    proposal = workspace.propose(request.handle, catalog.handle)
    assert proposal.plan is not None
    larger = workspace.import_json("request", _request(2).model_dump_json())

    rejected = workspace.export(
        proposal.plan.handle, larger.handle, catalog.handle, tmp_path / "rejected"
    )

    assert rejected.status == "rejected"
    assert rejected.option_policy is None
    assert rejected.verification.status == "violated"
    assert not (tmp_path / "rejected").exists()
    exported = workspace.export(
        proposal.plan.handle, request.handle, catalog.handle, tmp_path / "bundle"
    )
    assert exported.status == "exported"
    assert exported.backend_version == "psi4-builder/8"
    assert exported.namespace_policy == "restore_after_calculation"
    assert exported.option_policy == "native_defaults_per_calculation"
    assert exported.verification.request_complete
    assert exported.manifest_path is not None
    manifest = Path(exported.manifest_path)
    previous = manifest.read_bytes()
    with pytest.raises(FileExistsError):
        workspace.export(
            proposal.plan.handle, request.handle, catalog.handle, manifest.parent
        )
    assert manifest.read_bytes() == previous


def test_discovery_filters_profiles_and_closes_selected_schema_references(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Return relevant catalog entries and a machine-valid selected-field schema.

    Args:
        tmp_path: Capability workspace.
        formal_profile: Synthetic declarations for several drivers.
    """
    workspace = PlanningWorkspace(tmp_path / "work")
    reference = workspace.import_json("capabilities", formal_profile.model_dump_json())

    page = workspace.capabilities(
        reference.handle, CapabilityQuery(name="SCF", driver="gradient", limit=1)
    )

    assert page.total == 1
    assert page.catalog == reference
    assert "gradient" in str(page.items)
    description = describe_schema("request", definition="Model", fields=("settings",))
    assert description.json_schema is not None
    validator = Draft202012Validator(description.json_schema)
    validator.check_schema(description.json_schema)
    valid: JsonValue = {"settings": [{"name": "scf_type", "value": "pk"}]}
    invalid: JsonValue = {"settings": [{"name": "scf_type", "value": {}}]}
    assert validator.is_valid(valid)
    assert not validator.is_valid(invalid)
    assert "$defs" in description.json_schema
    assert describe_schema("request").json_schema is None


def test_reuse_explanation_and_failed_plan_are_retrievable(tmp_path: Path) -> None:
    """Locate shared calls and retain the exact graph referenced by a failure.

    Args:
        tmp_path: Persistent workspace for complete planning records.
    """
    base = _request(2)
    request = ScientificRequest(
        molecules=base.molecules,
        goals=tuple(
            CalculationGoal(
                id=goal.id,
                driver="energy",
                geometry="h2",
                models=(
                    Model(
                        method="hf",
                        basis="sto-3g",
                        reference="rhf",
                        settings=(Setting(name="scf_type", value="PK"),),
                    ),
                ),
                reuse_group="one-evaluation",
            )
            for goal in base.goals
        ),
    )
    workspace = PlanningWorkspace(tmp_path / "workspace")
    stored = workspace.import_json("request", request.model_dump_json())
    native = load_catalog("psi4")
    catalog = workspace.import_json("capabilities", native.model_dump_json())

    accepted = workspace.propose(stored.handle, catalog.handle)

    assert accepted.calculation_count == 1
    assert accepted.shared_call_count == 1
    assert accepted.last_candidate is None
    page = workspace.explain(accepted.proposal.handle, section="reuse")
    assert page.total == 1
    assert page.items[0].path == ("steps", 0, "satisfies")
    assert page.items[0].record_path == ("reuses", 0)
    assert "energy_1" in page.items[0].message
    assert accepted.verification is not None
    assert accepted.verification.capability_status == "supported"
    failed_profile = workspace.import_json(
        "capabilities",
        CapabilityCatalog(
            id="missing-methods",
            evidence=native.evidence,
        ).model_dump_json(),
    )
    rejected = workspace.propose(stored.handle, failed_profile.handle)
    assert rejected.status == "unknown"
    assert rejected.plan is None
    assert rejected.last_candidate is not None
    assert (
        workspace.reference(rejected.last_candidate.handle) == rejected.last_candidate
    )
