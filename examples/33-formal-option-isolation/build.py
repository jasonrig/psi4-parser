"""Save a checked MP2/HF comparison with explicit native option isolation."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    CapabilityCatalog,
    ExpressionGoal,
    GoalTerm,
    Model,
    QuantityType,
    SameGeometry,
    ScientificRequest,
    Setting,
    export_bundle,
    load_catalog,
    propose,
)


class _Arguments:
    destination: Path
    capabilities: Path | None


def main() -> None:
    """Save a construction bundle whose calls use independent native option scopes.

    Raises:
        SystemExit: The selected evidence cannot construct an accepted plan.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--capabilities", type=Path, default=None)
    args = parser.parse_args(namespace=_Arguments())
    catalog = (
        CapabilityCatalog.model_validate_json(args.capabilities.read_bytes())
        if args.capabilities
        else load_catalog("psi4")
    )
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    hf = Model(
        method="hf",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    mp2 = Model(
        method="mp2",
        basis="sto-3g",
        reference="rhf",
        settings=(
            Setting(name="scf_type", value="PK"),
            Setting(name="mp2_type", value="CONV"),
            Setting(name="qc_module", value="OCC"),
        ),
    )
    request = ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(id="mp2", driver="energy", geometry="h2", models=(mp2,)),
            CalculationGoal(id="hf", driver="energy", geometry="h2", models=(hf,)),
            ExpressionGoal(
                id="difference",
                terms=(
                    GoalTerm(goal="mp2", coefficient=1),
                    GoalTerm(goal="hf", coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            ),
        ),
        relations=(SameGeometry(calculations=("mp2", "hf")),),
    )
    proposal = propose(request, catalog)
    args.destination.mkdir()
    if proposal.plan is None:
        (args.destination / "proposal.json").write_text(
            proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    summary: dict[str, str | int | None] = {
        "status": proposal.status,
        "goals": len(request.goals),
        "option_policy": exported.manifest.option_policy,
        "namespace_policy": exported.manifest.namespace_policy,
        "backend_version": exported.manifest.backend_version,
        "manifest_digest": exported.manifest_digest,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(
            summary,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
