"""Construct equilibrium continuum comparisons and checked electronic shifts."""

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
    DDXSolvation,
    Environment,
    ExpressionGoal,
    GoalTerm,
    Model,
    QuantityType,
    ScientificRequest,
    Setting,
    export_bundle,
    load_catalog,
    propose,
)

_JSON = TypeAdapter(JsonValue)


class Arguments(argparse.Namespace):
    """Locate a new construction directory and independently supplied evidence."""

    destination: Path
    capabilities: Path | None


def request() -> ScientificRequest:
    """Return three continuum comparisons against one common vacuum reference."""
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    choices = (
        ("pcm", DDXSolvation(model="pcm", dielectric_constant=12.0)),
        ("cosmo", DDXSolvation(model="cosmo", dielectric_constant=12.0)),
        (
            "lpb",
            DDXSolvation(
                model="lpb", dielectric_constant=12.0, screening_inverse_bohr=0.2
            ),
        ),
    )
    vacuum = CalculationGoal(
        id="vacuum",
        driver="energy",
        geometry="h2",
        models=(
            Model(
                method="hf",
                basis="sto-3g",
                reference="rhf",
                settings=(Setting(name="scf_type", value="PK"),),
            ),
        ),
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            vacuum,
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
                            environment=Environment(
                                kind="ddx",
                                solvent="example-medium",
                                ddx=parameters,
                                settings=(
                                    Setting(name="ddx_lmax", module="DDX", value=6),
                                ),
                            ),
                        ),
                    ),
                )
                for name, parameters in choices
            ),
            *(
                ExpressionGoal(
                    id=f"{name}_shift",
                    terms=(
                        GoalTerm(goal=name, coefficient=1),
                        GoalTerm(goal="vacuum", coefficient=-1),
                    ),
                    quantity=QuantityType(
                        meaning="electronic_solvation_shift", unit="hartree"
                    ),
                )
                for name, _ in choices
            ),
            ExpressionGoal(
                id="equation_comparison",
                terms=(
                    GoalTerm(goal="cosmo_shift", coefficient=1),
                    GoalTerm(goal="pcm_shift", coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            ),
        ),
    )


def _damaged(original: ScientificRequest, *, geometry: bool) -> ScientificRequest:
    if geometry:
        changed = ScientificRequest(
            molecules=(
                *original.molecules,
                molecule("other", original.molecules[0].geometry),
            ),
            goals=original.goals,
        )
        document = _JSON.validate_json(changed.model_dump_json())
    else:
        document = _JSON.validate_json(original.model_dump_json())
    if not isinstance(document, dict):
        raise ValueError("Expected a request object")
    goals = document["goals"]
    if not isinstance(goals, list):
        raise ValueError("Expected request goals")
    goal = goals[0 if geometry else 4]
    if not isinstance(goal, dict):
        raise ValueError("Expected a goal object")
    if geometry:
        goal["geometry"] = "other"
    else:
        terms = goal["terms"]
        if not isinstance(terms, list):
            raise ValueError("Expected expression terms")
        term = terms[0]
        if not isinstance(term, dict):
            raise ValueError("Expected a term object")
        term["coefficient"] = 2
    return ScientificRequest.model_validate_json(json.dumps(document))


def main() -> None:
    """Save a construction bundle, damaged requests, and source-catalog acceptance.

    Raises:
        SystemExit: The selected evidence cannot support construction or a damaged
            scientific request unexpectedly succeeds.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--capabilities",
        type=Path,
        default=None,
    )
    args = parser.parse_args(namespace=Arguments())
    scientific = request()
    catalog = (
        CapabilityCatalog.model_validate_json(args.capabilities.read_bytes())
        if args.capabilities
        else load_catalog("psi4")
    )
    proposal = propose(scientific, catalog)
    if proposal.plan is None:
        raise SystemExit(f"Planning returned {proposal.status}: {proposal.diagnostics}")
    args.destination.mkdir()
    exported = export_bundle(
        proposal.plan, scientific, catalog, args.destination / "bundle"
    )
    (args.destination / "proposal.json").write_text(
        proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    rejected: dict[str, JsonValue] = {}
    for name, geometry in (("wrong-weight", False), ("wrong-geometry", True)):
        damaged = _damaged(scientific, geometry=geometry)
        result = propose(damaged, catalog)
        (args.destination / f"{name}-request.json").write_text(
            damaged.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        (args.destination / f"{name}-proposal.json").write_text(
            result.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        if result.status != "no_candidate":
            raise SystemExit(f"Expected {name} rejection; observed {result.status}")
        rejected[name] = result.status
    audited = propose(scientific, load_catalog("psi4"))
    (args.destination / "reference-catalog-proposal.json").write_text(
        audited.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    summary: dict[str, JsonValue] = {
        "status": proposal.status,
        "goals": len(scientific.goals),
        "calls": sum(isinstance(step, Calculation) for step in proposal.plan.steps),
        "catalog": catalog.id,
        "runtime_policy": exported.manifest.runtime_policy,
        "required_components": [
            _JSON.validate_json(item.model_dump_json())
            for item in exported.manifest.required_components
        ],
        "reference_profile_status": audited.status,
        "rejected": rejected,
        "backend_version": exported.manifest.backend_version,
        "manifest_digest": exported.manifest_digest,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
