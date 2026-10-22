"""Check bundled, source-audited facts without requiring a Psi4 installation."""

import json
import sys
from importlib.resources import files
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    CapabilityCatalog,
    Evidence,
    MethodCapability,
    Model,
    QuantityType,
    ScientificRequest,
    Setting,
    available_catalogs,
    combine_catalogs,
    discover_capabilities,
    export_bundle,
    load_catalog,
    propose,
    verify,
)
from psi4_parser.formal.capabilities import DerivativeRoute
from psi4_parser.formal.science import Driver
from psi4_parser.maintenance.capabilities import CapabilityAudit, curate_catalog


def _audit() -> CapabilityAudit:
    return CapabilityAudit.model_validate_json(
        files("psi4_parser.formal.catalogs")
        .joinpath("psi4", "reference-audit.json")
        .read_bytes()
    )


def test_bundled_contracts_need_no_engine_release() -> None:
    """Select shared scientific contracts without choosing a version or binary."""
    catalog = load_catalog()

    assert catalog.id == "psi4"
    assert "application_version" not in type(catalog).model_fields
    assert "build" not in type(catalog).model_fields


def test_independent_contributions_can_extend_contracts_without_a_binary_audit(
    tmp_path: Path,
) -> None:
    """Discover, construct and export an extension while retaining its assumption.

    Args:
        tmp_path: Parent directory for the construction-only extension bundle.
    """
    catalog = load_catalog()
    extension = CapabilityCatalog(
        id="caller-extension",
        evidence=(
            Evidence(
                id="caller-method",
                source="Explicit caller scientific assumption",
                kind="declaration",
            ),
        ),
        methods=(
            MethodCapability(
                method="caller-method",
                driver="energy",
                reference="rhf",
                status="supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                evidence=("caller-method",),
            ),
        ),
    )

    combined = combine_catalogs(catalog, extension, catalog, name="extended-science")

    assert len(combined.methods) == len(catalog.methods) + 1
    assert combined.id == "extended-science"
    assert len(combined.evidence) == len(catalog.evidence) + 1
    assert combined.evidence[-1].kind == "declaration"
    assert len(catalog.methods) == 382
    assert discover_capabilities(combined, method="caller-method") == extension.methods
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="energy",
                driver="energy",
                geometry="h2",
                models=(
                    Model(method="caller-method", basis="sto-3g", reference="rhf"),
                ),
            ),
        ),
    )

    missing = propose(request, catalog)
    proposal = propose(request, combined)

    assert missing.plan is None
    assert missing.report is not None
    assert missing.report.capability_status == "unknown"
    assert proposal.plan is not None
    report = verify(proposal.plan, request=request, catalog=combined)
    assert report.request_complete
    assert any(
        "caller-method" in assumption
        and "Explicit caller scientific assumption" in assumption
        for assumption in report.assumptions
    )
    exported = export_bundle(
        proposal.plan, request, combined, destination=tmp_path / "extension-bundle"
    )
    saved = CapabilityCatalog.model_validate_json(
        (Path(exported.directory) / "capabilities.json").read_bytes()
    )
    assert saved == combined
    assert exported.manifest.goal_coverage == report.coverage
    assert (
        exported.manifest.assumptions[: len(report.assumptions)] == report.assumptions
    )


def test_contributions_cannot_overwrite_an_existing_evidence_identity() -> None:
    """Reject source conflicts instead of changing established rules."""
    original = CapabilityCatalog(
        evidence=(Evidence(id="source", source="First source", kind="declaration"),)
    )
    changed = CapabilityCatalog(
        evidence=(Evidence(id="source", source="Other source", kind="declaration"),)
    )

    with pytest.raises(ValueError, match="Evidence IDs must be unique"):
        combine_catalogs(original, changed)


def test_shared_contracts_are_used_without_any_catalog_selection(
    tmp_path: Path,
) -> None:
    """Construct, reverify, and export without an engine-specific evidence argument.

    Args:
        tmp_path: Parent of the construction bundle.
    """
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n", state=ElectronicState(charge=0, multiplicity=1)
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
                        method="hf",
                        basis="sto-3g",
                        reference="rhf",
                        settings=(Setting(name="scf_type", value="PK"),),
                    ),
                ),
            ),
        ),
    )

    proposal = propose(request)

    assert proposal.plan is not None
    assert verify(proposal.plan, request=request).request_complete
    bundle = export_bundle(proposal.plan, request, destination=tmp_path / "bundle")
    saved = CapabilityCatalog.model_validate_json(
        (Path(bundle.directory) / "capabilities.json").read_bytes()
    )
    assert saved == load_catalog()
    assert "application_version" not in type(bundle.manifest).model_fields
    assert "application_build" not in type(bundle.manifest).model_fields


def test_shared_catalog_keeps_source_provenance_without_selecting_a_binary() -> None:
    """Retain source evidence while leaving the running engine uninspected."""
    before = "psi4" in sys.modules

    collections = available_catalogs()
    catalog = load_catalog("psi4")

    assert ("psi4" in sys.modules) == before
    assert [item.id for item in collections] == [catalog.id]
    assert any(
        item.kind == "source" and item.source.startswith("https://github.com/psi4/")
        for item in catalog.evidence
    )
    assert {"scf", "hf", "mp2", "sapt0", "ssapt0", "sapt2+3"} <= {
        item.method for item in catalog.methods
    }
    assert len(catalog.methods) == 382
    assert not any(item.kind == "declaration" for item in catalog.evidence)
    oxygen = next(item for item in catalog.bases if item.name == "cc-pvdz")
    dimensions = next(item for item in oxygen.functions if item.element == "O")
    assert dimensions.spherical == 14
    assert dimensions.cartesian == 15
    assert len(oxygen.elements) == 18
    with pytest.raises(ValueError, match="Unknown bundled"):
        load_catalog("../../private")


@pytest.mark.parametrize(
    ("driver", "route", "frozen", "expected"),
    [
        ("gradient", "analytic", False, "constructed"),
        ("gradient", "analytic", True, "no_candidate"),
        ("gradient", "automatic", True, "constructed"),
    ],
)
def test_audited_mp2_cases_distinguish_analytic_and_automatic_routes(
    driver: Driver,
    route: DerivativeRoute,
    frozen: bool,
    expected: str,
) -> None:
    """Check core-dependent MP2 support using real source and non-computing probes.

    Args:
        driver: Requested derivative operation.
        route: Explicit derivative strategy.
        frozen: Declared core treatment.
        expected: Construction result within the recorded cases.
    """
    model = Model(
        method="mp2",
        basis="cc-pvdz",
        reference="rhf",
        frozen_core=frozen,
        settings=(
            Setting(name="scf_type", value="pk"),
            Setting(name="mp2_type", value="conv"),
            Setting(name="qc_module", value="occ"),
        ),
    )
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    goal = CalculationGoal(
        id="derivative",
        driver=driver,
        geometry="h2",
        models=(model,),
        derivative_routes=(route,),
    )
    request = ScientificRequest(molecules=(molecule("h2", geometry),), goals=(goal,))

    proposal = propose(request, load_catalog("psi4"))

    assert proposal.status == expected


def test_audited_profile_and_probe_are_reproducible_from_retained_evidence() -> None:
    """Rebuild the scientific facts from retained basis and routing observations."""
    audit = _audit()

    assert curate_catalog(audit) == load_catalog("psi4")


def test_reference_compiled_limits_do_not_change_input_contracts() -> None:
    """Keep execution-host compilation separate from scientific source contracts."""
    audit = _audit()
    document = TypeAdapter(JsonValue).validate_json(audit.model_dump_json())
    assert isinstance(document, dict)
    document["libint2"] = {name: [None, None, None] for name in audit.libint2}
    changed = CapabilityAudit.model_validate_json(json.dumps(document))

    assert curate_catalog(changed).methods == curate_catalog(audit).methods


def test_default_empty_module_is_not_an_explicitly_settable_option() -> None:
    """Retain the distinction discovered by the real metadata inspection."""
    catalog = load_catalog("psi4")
    option = next(item for item in catalog.options if item.name == "qc_module")

    assert option.accepts("occ")
    assert not option.accepts("")


@pytest.mark.parametrize(
    "missing",
    ["basis_dimensions", "routing", "libint2"],
)
def test_curation_rejects_incomplete_metadata(missing: str) -> None:
    """Require the full evidence inventory before deriving broader support cases.

    Args:
        missing: Audit category to empty at its public JSON boundary.
    """
    document = TypeAdapter(JsonValue).validate_json(_audit().model_dump_json())
    assert isinstance(document, dict)
    document[missing] = {} if missing == "libint2" else []
    changed = CapabilityAudit.model_validate_json(json.dumps(document))
    with pytest.raises(ValueError, match="Curation requires"):
        curate_catalog(changed)
