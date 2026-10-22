"""Construct a spectrum and thermal plan with explicitly permitted shared calls."""

import argparse
import json
import sys
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    Model,
    PlanningPreferences,
    ProductGoal,
    ScientificRequest,
    Setting,
    ThermalConditions,
    VibrationalAnalysis,
    export_bundle,
    load_catalog,
    propose,
    verify,
)

_JSON = TypeAdapter(JsonValue)


class _Arguments:
    destination: Path
    capabilities: Path | None


def _request(*, share_frequencies: bool = True) -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH 0 -.757 .587\nH 0 .757 .587\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    model = Model(
        method="hf",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    analysis = VibrationalAnalysis(
        conditions=ThermalConditions(
            temperature_kelvin=298.15, pressure_pascal=101325.0
        ),
        rotational_symmetry_number=2,
    )
    return ScientificRequest(
        molecules=(molecule("water", geometry),),
        goals=(
            CalculationGoal(
                id="spectrum_geometry",
                driver="optimize",
                geometry="water",
                models=(model,),
                reuse_group="one-water-optimization",
            ),
            CalculationGoal(
                id="thermal_geometry",
                driver="optimize",
                geometry="water",
                models=(model,),
                reuse_group="one-water-optimization",
            ),
            CalculationGoal(
                id="spectrum_analysis",
                driver="frequency",
                geometry="spectrum_geometry",
                models=(model,),
                derivative_routes=("analytic",),
                analysis=analysis,
                reuse_group="one-water-analysis" if share_frequencies else None,
            ),
            CalculationGoal(
                id="thermal_analysis",
                driver="frequency",
                geometry="thermal_geometry",
                models=(model,),
                derivative_routes=("analytic",),
                analysis=analysis,
                reuse_group="one-water-analysis",
            ),
            ProductGoal(
                id="spectrum",
                calculation="spectrum_analysis",
                name="harmonic_frequencies",
            ),
            ProductGoal(
                id="gibbs_correction",
                calculation="thermal_analysis",
                name="gibbs_correction",
            ),
            # Deliberately request two separate driver calls on the same geometry.
            CalculationGoal(
                id="first_energy",
                driver="energy",
                geometry="spectrum_geometry",
                models=(model,),
            ),
            CalculationGoal(
                id="second_energy",
                driver="energy",
                geometry="spectrum_geometry",
                models=(model,),
            ),
        ),
    )


def main() -> None:
    """Save shared and separate constructions and a rejected permission change.

    Raises:
        SystemExit: The supplied evidence cannot establish the requested work.
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
    request = _request()
    shared = propose(request, catalog)
    separate = propose(
        request, catalog, preferences=PlanningPreferences(calculation_reuse="avoid")
    )
    args.destination.mkdir()
    for name, proposal in (("shared", shared), ("separate", separate)):
        (args.destination / f"{name}-proposal.json").write_text(
            proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        if proposal.plan is None:
            raise SystemExit(f"{name}: {proposal.status}; inspect saved proposal")
    if shared.plan is None or separate.plan is None:
        raise SystemExit("Both constructions need independently accepted plans")
    exported = export_bundle(shared.plan, request, catalog, args.destination / "bundle")
    changed = _request(share_frequencies=False)
    rejection = verify(shared.plan, request=changed, catalog=catalog)
    if rejection.status != "violated" or not any(
        item.code == "unauthorized_reuse" for item in rejection.diagnostics
    ):
        raise SystemExit("The permission-change demonstration was not rejected")
    (args.destination / "changed-request.json").write_text(
        changed.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (args.destination / "changed-request-report.json").write_text(
        rejection.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    counts: dict[str, JsonValue] = {
        name: sum(isinstance(step, Calculation) for step in plan.steps)
        for name, plan in (("shared", shared.plan), ("separate", separate.plan))
    }
    summary: dict[str, JsonValue] = {
        "status": shared.status,
        "goals": len(request.goals),
        "logical_calculations": sum(
            isinstance(goal, CalculationGoal) for goal in request.goals
        ),
        "top_level_calls": counts,
        "reuses": [
            _JSON.validate_json(item.model_dump_json()) for item in shared.reuses
        ],
        "goal_coverage": [
            _JSON.validate_json(item.model_dump_json())
            for item in exported.manifest.goal_coverage
        ],
        "changed_request_status": rejection.status,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
