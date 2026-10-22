"""Plan optimization, frequencies, and a gradient from independent intent."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    CapabilityCatalog,
    Model,
    SameModel,
    ScientificRequest,
    SearchLimits,
    Setting,
    export_bundle,
    propose,
    verify,
)


class _Arguments:
    capabilities: Path
    destination: Path


def main() -> None:
    """Save a new bundle and examples of missing evidence and bounded search.

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
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    # These alternatives are explicitly permitted for this teaching example.
    # The demonstration evidence covers PK only; it makes no claim about DF.
    alternatives = tuple(
        Model(
            method="scf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="scf_type", value=algorithm),),
        )
        for algorithm in ("df", "pk")
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="opt",
                driver="optimize",
                geometry="h2",
                models=alternatives,
                reason="Supply the relaxed geometry for subsequent calculations",
            ),
            CalculationGoal(
                id="freq",
                driver="frequency",
                geometry="opt",
                models=alternatives,
                reason="Request a frequency calculation at the optimized geometry",
            ),
            CalculationGoal(
                id="gradient",
                driver="gradient",
                geometry="opt",
                models=alternatives,
                reason="Request the primary gradient tensor on the same geometry",
            ),
        ),
        relations=(
            SameModel(calculations=("opt", "freq")),
            SameModel(calculations=("opt", "gradient")),
        ),
    )
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
    # Removing all capability entries preserves the version/evidence identity,
    # but must leave scientific verification unknown. Never bypass that status.
    missing = CapabilityCatalog(
        id="demonstration-without-capability-entries",
        evidence=catalog.evidence,
    )
    no_evidence = verify(proposal.plan, request=request, catalog=missing)
    (args.destination / "missing-evidence.json").write_text(
        no_evidence.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    bounded = propose(request, catalog, limits=SearchLimits(max_candidates=1))
    (args.destination / "bounded-search.json").write_text(
        bounded.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "status": proposal.status,
        "attempts": proposal.attempts,
        "choices": [
            {
                "goal": choice.goal,
                "method": choice.model.method,
                "basis": choice.model.basis,
                "settings": [
                    {"name": setting.name, "value": setting.value}
                    for setting in choice.model.settings
                ],
                "derivative_route": choice.derivative_route,
                "preference_rank": choice.preference_rank,
            }
            for choice in proposal.choices
        ],
        "missing_evidence": no_evidence.status,
        "one_candidate_budget": bounded.status,
        "manifest_digest": exported.manifest_digest,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
