"""Construct independent PCMSolver media and checked electronic solvation shifts."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    Environment,
    ExpressionGoal,
    GoalTerm,
    Model,
    PCMSolverSolvation,
    QuantityType,
    ScientificRequest,
    Setting,
    export_bundle,
    propose,
)


class Arguments(argparse.Namespace):
    """Locate the new directory for construction artifacts."""

    destination: Path


def request(*, wrong_weight: bool = False) -> ScientificRequest:
    """Return three explicitly chosen media and a common vacuum reference.

    Args:
        wrong_weight: Deliberately request twice the solvated energy in one shift.

    Returns:
        Independent calculation intent, with no execution-host requirements.
    """
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    environments: tuple[tuple[str, Environment | None], ...] = (
        ("vacuum", None),
        ("water", Environment(kind="pcm", solvent="Water")),
        (
            "explicit_iefpcm",
            Environment(
                kind="pcm",
                solvent="example-medium",
                pcm=PCMSolverSolvation(dielectric_constant=12, probe_radius_bohr=2.5),
            ),
        ),
        (
            "explicit_cpcm",
            Environment(
                kind="pcm",
                solvent="example-medium",
                pcm=PCMSolverSolvation(
                    solver="cpcm",
                    dielectric_constant=12,
                    probe_radius_bohr=2.5,
                    cpcm_correction=0.5,
                ),
            ),
        ),
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            *(
                CalculationGoal(
                    id=name,
                    driver="energy",
                    geometry="h2",
                    models=(
                        Model(
                            method="hf",
                            basis="sto-3g",
                            reference="rhf",
                            settings=(Setting(name="scf_type", value="PK"),),
                            environment=environment,
                        ),
                    ),
                )
                for name, environment in environments
            ),
            *(
                ExpressionGoal(
                    id=f"{name}_shift",
                    quantity=QuantityType(
                        meaning="electronic_solvation_shift", unit="hartree"
                    ),
                    terms=(
                        GoalTerm(
                            goal=name,
                            coefficient=2 if wrong_weight and name == "water" else 1,
                        ),
                        GoalTerm(goal="vacuum", coefficient=-1),
                    ),
                )
                for name, _ in environments[1:]
            ),
            ExpressionGoal(
                id="equation_comparison",
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
                terms=(
                    GoalTerm(goal="explicit_cpcm_shift", coefficient=1),
                    GoalTerm(goal="explicit_iefpcm_shift", coefficient=-1),
                ),
            ),
        ),
    )


def main() -> None:
    """Save a checked bundle and an independently invalid solvation request.

    Raises:
        SystemExit: Valid construction fails or an incorrect shift is accepted.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(namespace=Arguments())
    scientific = request()
    proposal = propose(scientific)
    if proposal.plan is None:
        raise SystemExit(f"Planning returned {proposal.status}: {proposal.diagnostics}")
    damaged = request(wrong_weight=True)
    rejected = propose(damaged)
    if rejected.status != "no_candidate":
        raise SystemExit(f"Expected formula rejection; observed {rejected.status}")
    args.destination.mkdir()
    bundle = export_bundle(
        proposal.plan, scientific, destination=args.destination / "bundle"
    )
    for name, record in (
        ("proposal", proposal),
        ("wrong-weight-request", damaged),
        ("wrong-weight-proposal", rejected),
    ):
        (args.destination / f"{name}.json").write_text(
            record.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    summary = {
        "status": proposal.status,
        "goals": len(scientific.goals),
        "calls": sum(isinstance(step, Calculation) for step in proposal.plan.steps),
        "runtime_policy": bundle.manifest.runtime_policy,
        "required_components": [
            {"name": item.name, "version": item.version}
            for item in bundle.manifest.required_components
        ],
        "wrong_weight_status": rejected.status,
        "backend_version": bundle.manifest.backend_version,
        "manifest_digest": bundle.manifest_digest,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
