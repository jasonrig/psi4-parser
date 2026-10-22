"""Export construction artifacts without executing jobs or accepting their results."""

import hashlib
from pathlib import Path

import pytest

from psi4_parser import validate
from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BundleManifest,
    CalculationGoal,
    CapabilityCatalog,
    ExpressionGoal,
    GoalTerm,
    Model,
    Plan,
    QuantityType,
    Report,
    ScientificRequest,
    export_bundle,
    propose,
)


def expression_request() -> ScientificRequest:
    """Return two scalar calculations and an independently stated formula."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(id="a", driver="energy", geometry="h2", models=(model,)),
            CalculationGoal(id="b", driver="energy", geometry="h2", models=(model,)),
            ExpressionGoal(
                id="difference",
                terms=(
                    GoalTerm(goal="a", coefficient=1),
                    GoalTerm(goal="b", coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            ),
        ),
    )


def test_bundle_binds_request_plan_proof_and_native_input(
    tmp_path: Path, formal_profile: CapabilityCatalog
) -> None:
    """Export dependencies and recipes with independently checked hashes.

    Args:
        tmp_path: Isolated parent for the exported bundle.
        formal_profile: Synthetic application capability declarations.
    """
    request = expression_request()
    proposal = propose(request, formal_profile)
    assert proposal.plan is not None
    destination = tmp_path / "bundle"

    exported = export_bundle(proposal.plan, request, formal_profile, destination)

    manifest_bytes = (destination / "manifest.json").read_bytes()
    manifest = BundleManifest.model_validate_json(manifest_bytes)
    assert manifest.option_policy == "native_defaults_per_calculation"
    assert (
        BundleManifest.model_validate_json(
            manifest.model_dump_json(exclude={"option_policy"})
        ).option_policy
        is None
    )
    assert exported.manifest_digest == hashlib.sha256(manifest_bytes).hexdigest()
    for item in manifest.files:
        assert (
            hashlib.sha256((destination / item.path).read_bytes()).hexdigest()
            == item.sha256
        )
    assert (
        Plan.model_validate_json((destination / "calculation-plan.json").read_text())
        == proposal.plan
    )
    report = Report.model_validate_json((destination / "verification.json").read_text())
    assert report.request_complete
    assert report.verification_digest == manifest.verification_digest
    assert manifest.expressions[0].id == "difference"
    assert manifest.quantities[-1].operands == ("a", "b")
    assert manifest.quantities[-1].system is None
    source = (destination / "inputs" / "workflow.dat").read_text()
    assert validate(source) == ()
    assert "'difference':" not in source
    assert not (destination / "results.json").exists()


def test_export_never_overwrites_an_existing_directory(
    tmp_path: Path, formal_profile: CapabilityCatalog
) -> None:
    """Preserve existing files when a caller reuses an export destination.

    Args:
        tmp_path: Isolated output parent.
        formal_profile: Synthetic capability declarations.
    """
    request = expression_request()
    proposal = propose(request, formal_profile)
    assert proposal.plan is not None
    destination = tmp_path / "existing"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_text("existing work")

    with pytest.raises(FileExistsError):
        export_bundle(proposal.plan, request, formal_profile, destination)

    assert marker.read_text() == "existing work"
    assert not (destination / "manifest.json").exists()


def test_electronic_energies_cannot_be_relabelled_as_gibbs_energy(
    formal_profile: CapabilityCatalog,
) -> None:
    """Require semantic evidence for thermochemical quantities beyond matching units.

    Args:
        formal_profile: Synthetic support for electronic energies only.
    """
    original = expression_request()
    request = ScientificRequest(
        molecules=original.molecules,
        goals=(
            original.goals[0],
            ExpressionGoal(
                id="gibbs",
                terms=(GoalTerm(goal="a", coefficient=1),),
                quantity=QuantityType(meaning="gibbs_energy", unit="hartree"),
            ),
        ),
    )

    proposal = propose(request, formal_profile)

    assert proposal.plan is None
    assert proposal.report is not None
    assert proposal.report.status == "unsupported"
    assert any(
        item.code == "quantity_semantics" for item in proposal.report.diagnostics
    )
