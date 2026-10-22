"""Construct native and hybrid Gibbs reaction plans without executing chemistry."""

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    Model,
    Rational,
    ReactionParticipant,
    ReactionStudy,
    ReactionThermochemistry,
    SameModel,
    ScientificRequest,
    Setting,
    ThermalConditions,
    VibrationalAnalysis,
    export_bundle,
    load_catalog,
    propose,
    reaction_expansion,
)


class _Arguments:
    destination: Path
    capabilities: Path | None


def oxidation_request(
    *, hybrid: bool, co2_temperature: float = 298.15
) -> ScientificRequest:
    """Require CO + 1/2 O2 -> CO2 with explicit optimized species and thermal models.

    Args:
        hybrid: Use MP2 electronic energies plus HF corrections instead of HF totals.
        co2_temperature: CO2 analysis temperature; other species use 298.15 kelvin.

    Returns:
        Independent optimization, frequency, product, and reaction obligations.
    """
    inputs = (
        molecule(
            "co",
            Molecule.from_xyz(
                "2\nCO\nC 0 0 0\nO 0 0 1.13\n",
                state=ElectronicState(charge=0, multiplicity=1),
            ),
        ),
        molecule(
            "oxygen",
            Molecule.from_xyz(
                "2\nO2\nO 0 0 0\nO 0 0 1.21\n",
                state=ElectronicState(charge=0, multiplicity=3),
            ),
        ),
        molecule(
            "co2",
            Molecule.from_xyz(
                "3\nCO2\nO 0 0 -1.16\nC 0 0 0\nO 0 0 1.16\n",
                state=ElectronicState(charge=0, multiplicity=1),
            ),
        ),
    )
    optimizations: list[CalculationGoal] = []
    participants: list[ReactionParticipant] = []
    relations: list[SameModel] = []
    for name, symmetry, coefficient in (
        ("co", 1, -1),
        ("oxygen", 2, Rational(numerator=-1, denominator=2)),
        ("co2", 2, 1),
    ):
        reference: Literal["rhf", "uhf"] = "uhf" if name == "oxygen" else "rhf"
        hf = Model(
            method="hf",
            basis="sto-3g",
            reference=reference,
            settings=(Setting(name="scf_type", value="PK"),),
        )
        electronic = (
            Model(
                method="mp2",
                basis="sto-3g",
                reference=reference,
                frozen_core=True,
                settings=(
                    Setting(name="scf_type", value="PK"),
                    Setting(name="mp2_type", value="CONV"),
                    Setting(name="qc_module", value="OCC"),
                ),
            )
            if hybrid
            else hf
        )
        optimization = CalculationGoal(
            id=f"opt:{name}",
            driver="optimize",
            geometry=name,
            models=(hf,),
            derivative_routes=("analytic",),
        )
        optimizations.append(optimization)
        participants.append(
            ReactionParticipant(
                id=name,
                geometry=optimization.id,
                coefficient=coefficient,
                models=(electronic,),
                thermochemistry=ReactionThermochemistry(
                    analysis=VibrationalAnalysis(
                        conditions=ThermalConditions(
                            temperature_kelvin=co2_temperature
                            if name == "co2"
                            else 298.15,
                            pressure_pascal=101325.0,
                        ),
                        rotational_symmetry_number=symmetry,
                    ),
                    models=(hf,) if hybrid else (),
                    derivative_routes=("analytic",),
                ),
            )
        )
        relations.append(
            SameModel(
                calculations=(optimization.id, f"oxidation:frequency:{name}"),
            )
        )
    expansion = reaction_expansion(
        ReactionStudy(
            id="oxidation",
            participants=tuple(participants),
            quantity="gibbs_free_energy",
        )
    )
    return ScientificRequest(
        molecules=inputs,
        goals=(*optimizations, *expansion.goals),
        relations=tuple(relations),
    )


def main() -> None:
    """Save two accepted bundles and a self-consistent mixed-temperature rejection.

    Raises:
        SystemExit: A selected capability catalog cannot construct an accepted plan.
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
    args.destination.mkdir()
    summaries: dict[str, dict[str, str | int | bool]] = {}
    for name, hybrid in (("native", False), ("hybrid", True)):
        request = oxidation_request(hybrid=hybrid)
        proposal = propose(request, catalog)
        if proposal.plan is None:
            (args.destination / f"{name}-proposal.json").write_text(
                proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
            )
            raise SystemExit(f"{name}: planning returned {proposal.status}")
        exported = export_bundle(
            proposal.plan, request, catalog, args.destination / name
        )
        summaries[name] = {
            "status": proposal.status,
            "goals": len(request.goals),
            "calculations": sum(
                isinstance(step, Calculation) for step in proposal.plan.steps
            ),
            "native_records": len(exported.manifest.native_outputs),
            "target": "oxidation:reaction",
            "manifest_digest": exported.manifest_digest,
        }
    wrong = oxidation_request(hybrid=False, co2_temperature=400.0)
    rejected = propose(wrong, catalog)
    (args.destination / "mixed-temperature-request.json").write_text(
        wrong.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (args.destination / "mixed-temperature-proposal.json").write_text(
        rejected.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (args.destination / "summary.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
