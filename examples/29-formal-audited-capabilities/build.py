"""Construct a water plan using source-audited conditional capability evidence."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    Model,
    SameModel,
    ScientificRequest,
    Setting,
    export_bundle,
    load_catalog,
    propose,
)


class _Arguments:
    destination: Path


def _request(
    *, explicit_algorithm: bool = True, allow_automatic: bool = True
) -> ScientificRequest:
    settings = (Setting(name="scf_type", value="PK"),) if explicit_algorithm else ()
    hf = Model(method="hf", basis="cc-pvdz", reference="rhf", settings=settings)
    mp2 = Model(
        method="mp2",
        basis="cc-pvdz",
        reference="rhf",
        frozen_core=True,
        settings=(
            *settings,
            Setting(name="mp2_type", value="CONV"),
            Setting(name="qc_module", value="OCC"),
        ),
    )
    water = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH 0 -.757 .587\nH 0 .757 .587\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return ScientificRequest(
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
                id="freq",
                driver="frequency",
                geometry="opt",
                models=(hf,),
                derivative_routes=("analytic",),
            ),
            CalculationGoal(
                id="correlated_energy", driver="energy", geometry="opt", models=(mp2,)
            ),
            CalculationGoal(
                id="correlated_gradient",
                driver="gradient",
                geometry="opt",
                models=(mp2,),
                derivative_routes=("analytic", "automatic")
                if allow_automatic
                else ("analytic",),
                reason=(
                    "Request a frozen-core MP2 gradient; explicitly allow the "
                    "engine's automatic derivative route"
                ),
            ),
        ),
        relations=(SameModel(calculations=("opt", "freq")),),
    )


def main() -> None:
    """Save accepted work and two diagnostic cases, without launching Psi4.

    Raises:
        SystemExit: The bundled evidence no longer accepts the example request.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(namespace=_Arguments())
    # Loading evidence targets this recorded binary; it does not detect the host engine.
    catalog = load_catalog("psi4")
    request = _request()
    proposal = propose(request, catalog)
    args.destination.mkdir()
    (args.destination / "request.json").write_text(
        request.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (args.destination / "proposal.json").write_text(
        proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    if proposal.plan is None:
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    refused = propose(_request(allow_automatic=False), catalog)
    missing = propose(_request(explicit_algorithm=False), catalog)
    for name, result in (("analytic-only", refused), ("missing-algorithm", missing)):
        (args.destination / f"{name}.json").write_text(
            result.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    summary = {
        "status": proposal.status,
        "attempts": proposal.attempts,
        "catalog": catalog.id,
        "required_components": [
            {"name": item.name} for item in exported.manifest.required_components
        ],
        "routes": {item.goal: item.derivative_route for item in proposal.choices},
        "analytic_only": refused.status,
        "missing_algorithm": missing.status,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Source-audited construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
