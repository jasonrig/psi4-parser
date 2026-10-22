"""Plan named vibrational/property products and an explicit hybrid Gibbs estimate."""

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
    Plan,
    ProductGoal,
    QuantityType,
    SameModel,
    ScientificRequest,
    Setting,
    ThermalConditions,
    VibrationalAnalysis,
    export_bundle,
    load_catalog,
    propose,
    verify,
)


class _Arguments:
    destination: Path
    capabilities: Path | None


def main() -> None:
    """Save construction artifacts and rejection of an altered thermal context.

    Raises:
        SystemExit: No accepted plan is available from the selected evidence.
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
    water = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH 0 -.757 .587\nH 0 .757 .587\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    hf = Model(
        method="hf",
        basis="cc-pvdz",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    mp2 = Model(
        method="mp2",
        basis="cc-pvdz",
        reference="rhf",
        frozen_core=True,
        settings=(
            Setting(name="scf_type", value="PK"),
            Setting(name="mp2_type", value="CONV"),
            Setting(name="qc_module", value="OCC"),
        ),
    )
    analysis = VibrationalAnalysis(
        conditions=ThermalConditions(
            temperature_kelvin=298.15, pressure_pascal=101325.0
        ),
        rotational_symmetry_number=2,
    )
    request = ScientificRequest(
        molecules=(molecule("water", water),),
        goals=(
            CalculationGoal(
                id="opt",
                driver="optimize",
                geometry="water",
                models=(hf,),
                derivative_routes=("analytic",),
            ),
            CalculationGoal(
                id="frequency",
                driver="frequency",
                geometry="opt",
                models=(hf,),
                derivative_routes=("analytic",),
                analysis=analysis,
            ),
            ProductGoal(
                id="spectrum", calculation="frequency", name="harmonic_frequencies"
            ),
            ProductGoal(id="modes", calculation="frequency", name="normal_modes"),
            ProductGoal(id="hessian", calculation="frequency", name="hessian"),
            ProductGoal(
                id="gibbs_correction", calculation="frequency", name="gibbs_correction"
            ),
            ProductGoal(
                id="hf_gibbs", calculation="frequency", name="gibbs_free_energy"
            ),
            CalculationGoal(
                id="correlated_energy", driver="energy", geometry="opt", models=(mp2,)
            ),
            ExpressionGoal(
                id="hybrid_gibbs",
                quantity=QuantityType(meaning="gibbs_free_energy", unit="hartree"),
                terms=(
                    GoalTerm(goal="correlated_energy", coefficient=1),
                    GoalTerm(goal="gibbs_correction", coefficient=1),
                ),
                reason="MP2 electronic energy plus the specified HF RRHO correction",
            ),
            CalculationGoal(
                id="properties",
                driver="properties",
                geometry="opt",
                models=(hf,),
                properties=(
                    "DIPOLE",
                    "QUADRUPOLE",
                    "MULLIKEN_CHARGES",
                    "LOWDIN_CHARGES",
                    "MAYER_INDICES",
                    "WIBERG_LOWDIN_INDICES",
                ),
            ),
            ProductGoal(id="dipole", calculation="properties", name="dipole"),
            ProductGoal(id="quadrupole", calculation="properties", name="quadrupole"),
            ProductGoal(
                id="mulliken", calculation="properties", name="mulliken_charges"
            ),
            ProductGoal(id="lowdin", calculation="properties", name="lowdin_charges"),
            ProductGoal(id="mayer", calculation="properties", name="mayer_indices"),
            ProductGoal(
                id="wiberg", calculation="properties", name="wiberg_lowdin_indices"
            ),
        ),
        relations=(
            SameModel(calculations=("opt", "frequency")),
            SameModel(calculations=("opt", "properties")),
        ),
    )
    proposal = propose(request, catalog)
    args.destination.mkdir()
    (args.destination / "request.json").write_text(
        request.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    if proposal.plan is None:
        (args.destination / "proposal.json").write_text(
            proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    # The altered implementation remains internally coherent, but contradicts intent.
    wrong = Plan.model_validate_json(
        proposal.plan.model_dump_json().replace(
            '"temperature_kelvin":298.15', '"temperature_kelvin":400.0', 1
        )
    )
    rejection = verify(wrong, request=request, catalog=catalog)
    (args.destination / "wrong-temperature.json").write_text(
        rejection.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "status": proposal.status,
        "goals": len(request.goals),
        "products": len(exported.manifest.products),
        "native_outputs": [
            {
                "producer": item.producer,
                "filename_template": item.filename_template,
                "products": list(item.products),
            }
            for item in exported.manifest.native_outputs
        ],
        "wrong_temperature": rejection.status,
        "temperature_kelvin": analysis.conditions.temperature_kelvin,
        "pressure_pascal": analysis.conditions.pressure_pascal,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(
        f"Product and thermochemistry construction artifacts: {args.destination}\n"
    )


if __name__ == "__main__":
    main()
