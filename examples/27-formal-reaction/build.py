"""Construct a closed reaction and reject missing nuclei despite exact algebra."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CapabilityCatalog,
    Model,
    ReactionParticipant,
    ReactionStudy,
    ScientificRequest,
    Setting,
    export_bundle,
    propose,
    reaction_expansion,
)


class _Arguments:
    capabilities: Path
    destination: Path


def dissociation(product_count: int) -> ScientificRequest:
    """Return an independent closed-reaction request for H2 -> product_count H.

    Args:
        product_count: Number of produced neutral hydrogen atoms.

    Returns:
        Explicit molecular inputs, species calculations, and reaction formula.
    """
    dimer = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .74\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    atom = Molecule.from_xyz(
        "1\nH\nH 0 0 0\n", state=ElectronicState(charge=0, multiplicity=2)
    )
    expansion = reaction_expansion(
        ReactionStudy(
            id="dissociation",
            participants=(
                ReactionParticipant(
                    id="H2",
                    geometry="h2",
                    coefficient=-1,
                    models=(
                        Model(
                            method="scf",
                            basis="sto-3g",
                            reference="rhf",
                            settings=(Setting(name="scf_type", value="pk"),),
                        ),
                    ),
                ),
                ReactionParticipant(
                    id="H",
                    geometry="h",
                    coefficient=product_count,
                    models=(
                        Model(
                            method="scf",
                            basis="sto-3g",
                            reference="uhf",
                            settings=(Setting(name="scf_type", value="pk"),),
                        ),
                    ),
                ),
            ),
        )
    )
    return ScientificRequest(
        molecules=(molecule("h2", dimer), molecule("h", atom)), goals=expansion.goals
    )


def main() -> None:
    """Save a reaction bundle and a self-consistent but unbalanced request.

    Raises:
        SystemExit: No accepted plan can be exported; inspect the saved proposal.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--capabilities",
        type=Path,
        default=Path(__file__).parents[1] / "formal-demo-capabilities.json",
    )
    args = parser.parse_args(namespace=_Arguments())
    catalog = CapabilityCatalog.model_validate_json(args.capabilities.read_bytes())
    request = dissociation(2)
    args.destination.mkdir()
    (args.destination / "request.json").write_text(
        request.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    proposal = propose(request, catalog)
    if proposal.plan is None:
        (args.destination / "proposal.json").write_text(
            proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    wrong_request = dissociation(1)
    (args.destination / "unbalanced-request.json").write_text(
        wrong_request.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    rejected = propose(wrong_request, catalog)
    (args.destination / "unbalanced-proposal.json").write_text(
        rejected.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "status": proposal.status,
        "target": "dissociation:reaction",
        "formula": "2 * E(H, UHF) - E(H2, RHF)",
        "unbalanced_proposal": rejected.status,
        "unbalanced_verification": (
            rejected.report.status if rejected.report is not None else None
        ),
        "manifest_digest": exported.manifest_digest,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
