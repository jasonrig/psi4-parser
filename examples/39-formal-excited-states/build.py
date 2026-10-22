"""Construct response spectra with independent root and energy-product contracts."""

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

from psi4_parser.builder import ElectronicState, Molecule, molecule, with_symmetry
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    ElectronicTarget,
    EnergyFormula,
    EnergyTerm,
    ExpressionGoal,
    GoalTerm,
    Model,
    ProductGoal,
    QuantityType,
    ScientificRequest,
    Setting,
    TDSCFAnalysis,
    export_bundle,
    propose,
)
from psi4_parser.formal.intent import Goal
from psi4_parser.formal.science import ProductName


class Arguments(argparse.Namespace):
    """Locate the new directory for construction artifacts."""

    destination: Path


def request(*, wrong_weight: bool = False) -> ScientificRequest:
    """Return independent HF/RPA, HF/TDA, and PBE response comparisons.

    Args:
        wrong_weight: Deliberately double a reference in an excited-state total.

    Returns:
        Finite root/product requirements with no engine-version selection.
    """
    geometry = with_symmetry("c1")(
        Molecule.from_xyz(
            "4\nFormaldehyde\nC 0 0 0\nO 0 0 1.21\nH 0 .94 -.58\nH 0 -.94 -.58\n",
            state=ElectronicState(charge=0, multiplicity=1),
        )
    )
    goals: list[Goal] = []
    relations: list[EnergyFormula] = []
    choices: tuple[tuple[str, str, Literal["rpa", "tda"]], ...] = (
        ("hf_rpa", "td-hf", "rpa"),
        ("hf_tda", "td-hf", "tda"),
        ("pbe_rpa", "td-pbe", "rpa"),
    )
    products: tuple[tuple[str, ProductName, int], ...] = (
        ("gap_1", "excitation_energy", 1),
        ("gap_2", "excitation_energy", 2),
        ("total_1", "excited_state_energy", 1),
        ("strength_1", "oscillator_strength_length", 1),
        ("moment_1", "electric_transition_dipole_length", 1),
    )
    for name, method, approximation in choices:
        analysis = TDSCFAnalysis(
            states=3,
            spin="singlet",
            approximation=approximation,
            residual_threshold=1e-6,
            max_iterations=60,
        )
        goals.append(
            CalculationGoal(
                id=name,
                driver="energy",
                geometry="molecule",
                models=(
                    Model(
                        method=method,
                        basis="cc-pvdz",
                        reference="rhf",
                        settings=(Setting(name="scf_type", value="PK"),),
                        tdscf=analysis,
                    ),
                ),
            )
        )
        for suffix, product, root in products:
            goals.append(
                ProductGoal(
                    id=f"{name}_{suffix}",
                    calculation=name,
                    name=product,
                    electronic_target=ElectronicTarget(root=root, multiplicity=1),
                )
            )
        goals.append(
            ExpressionGoal(
                id=f"{name}_derived_total",
                quantity=QuantityType(meaning="excited_state_energy", unit="hartree"),
                terms=(
                    GoalTerm(
                        goal=name,
                        coefficient=2 if wrong_weight and name == "hf_rpa" else 1,
                    ),
                    GoalTerm(goal=f"{name}_gap_1", coefficient=1),
                ),
            )
        )
        relations.append(
            EnergyFormula(
                result=f"{name}_total_1",
                terms=(
                    EnergyTerm(result=name, coefficient=1),
                    EnergyTerm(result=f"{name}_gap_1", coefficient=1),
                ),
            )
        )
    goals.append(
        ExpressionGoal(
            id="rpa_tda_gap_comparison",
            quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            terms=(
                GoalTerm(goal="hf_rpa_gap_1", coefficient=1),
                GoalTerm(goal="hf_tda_gap_1", coefficient=-1),
            ),
        )
    )
    return ScientificRequest(
        molecules=(molecule("molecule", geometry),),
        goals=tuple(goals),
        relations=tuple(relations),
    )


def main() -> None:
    """Save response construction, exact product proofs, and a damaged request.

    Raises:
        SystemExit: Valid intent fails or the damaged formula is accepted.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(namespace=Arguments())
    scientific = request()
    proposal = propose(scientific)
    if proposal.plan is None or proposal.report is None:
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
        "coverage": len(proposal.report.coverage),
        "native_variables": len(bundle.manifest.native_variables),
        "runtime_policy": bundle.manifest.runtime_policy,
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
