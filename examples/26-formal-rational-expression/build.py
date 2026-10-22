"""Preserve exact rational energy weights and reject unsupported Gibbs labels."""

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
    Rational,
    ScientificRequest,
    Setting,
    export_bundle,
    propose,
)


class _Arguments:
    capabilities: Path
    destination: Path


def main() -> None:
    """Save an exact weighted expression and an unsupported meaning conversion.

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
    state = ElectronicState(charge=0, multiplicity=1)
    model = Model(
        method="scf",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="pk"),),
    )
    request = ScientificRequest(
        molecules=tuple(
            molecule(
                name,
                Molecule.from_xyz(f"2\nH2\nH 0 0 0\nH 0 0 {length}\n", state=state),
            )
            for name, length in (("short", 0.74), ("long", 0.85))
        ),
        goals=(
            CalculationGoal(
                id="e_short", driver="energy", geometry="short", models=(model,)
            ),
            CalculationGoal(
                id="e_long", driver="energy", geometry="long", models=(model,)
            ),
            ExpressionGoal(
                id="weighted_energy",
                terms=(
                    GoalTerm(
                        goal="e_short", coefficient=Rational(numerator=1, denominator=3)
                    ),
                    GoalTerm(
                        goal="e_long", coefficient=Rational(numerator=2, denominator=3)
                    ),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                reason="Illustrate explicitly supplied rational energy weights",
            ),
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
    # Identical scalar units do not justify converting electronic energy to G.
    unsupported = ScientificRequest(
        molecules=request.molecules,
        goals=(
            *request.goals,
            ExpressionGoal(
                id="gibbs",
                terms=(GoalTerm(goal="weighted_energy", coefficient=1),),
                quantity=QuantityType(meaning="gibbs_energy", unit="hartree"),
            ),
        ),
    )
    rejected = propose(unsupported, catalog)
    (args.destination / "unsupported-meaning.json").write_text(
        rejected.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "status": proposal.status,
        "expression": {
            "id": exported.manifest.expressions[0].id,
            "terms": [
                {
                    "result": term.result,
                    "coefficient": str(term.coefficient.fraction)
                    if isinstance(term.coefficient, Rational)
                    else str(term.coefficient),
                }
                for term in exported.manifest.expressions[0].terms
            ],
        },
        "unsupported_proposal": rejected.status,
        "unsupported_verification": rejected.report.status
        if rejected.report is not None
        else None,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
