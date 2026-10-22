"""Construct DT/TQ basis-limit corrections and preserve symbolic estimate recipes."""

import argparse
import json
import sys
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BasisCorrectionPoint,
    Calculation,
    CapabilityCatalog,
    ExpressionGoal,
    ExtrapolationStudy,
    GoalTerm,
    Model,
    QuantityType,
    ScientificRequest,
    Setting,
    export_bundle,
    extrapolation_expansion,
    load_catalog,
    propose,
)

_JSON = TypeAdapter(JsonValue)


class _Arguments:
    destination: Path
    capabilities: Path | None


def _point(basis: str, cardinal: int) -> BasisCorrectionPoint:
    hf = Model(
        method="hf",
        basis=basis,
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    mp2 = Model(
        method="mp2",
        basis=basis,
        reference="rhf",
        settings=(
            Setting(name="scf_type", value="PK"),
            Setting(name="mp2_type", value="CONV"),
            Setting(name="qc_module", value="OCC"),
        ),
    )
    return BasisCorrectionPoint(
        basis=basis, cardinal=cardinal, models=(mp2,), reference_models=(hf,)
    )


def _request(
    *, wrong_family: bool = False, wrong_weights: bool = False
) -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    d, t, q = _point("cc-pvdz", 2), _point("cc-pvtz", 3), _point("cc-pvqz", 4)
    dt = extrapolation_expansion(
        ExtrapolationStudy(
            id="dt",
            geometry="h2",
            family="cc-pvXZ",
            power=3,
            low=d,
            high=t,
            reuse_group="shared-basis-points",
        )
    )
    tq = extrapolation_expansion(
        ExtrapolationStudy(
            id="tq",
            geometry="h2",
            family="aug-cc-pvXZ" if wrong_family else "cc-pvXZ",
            power=3,
            low=t,
            high=q,
            reuse_group="shared-basis-points",
        )
    )
    tq_goals = tq.goals
    if wrong_weights:
        target = tq.goals[-1]
        if not isinstance(target, ExpressionGoal) or target.extrapolation is None:
            raise ValueError("The expansion must retain an explicit correction recipe")
        tq_goals = (
            *tq.goals[:-1],
            ExpressionGoal(
                id=target.id,
                terms=(
                    GoalTerm(goal=target.terms[0].goal, coefficient=-1),
                    GoalTerm(goal=target.terms[1].goal, coefficient=2),
                ),
                quantity=target.quantity,
                extrapolation=target.extrapolation,
            ),
        )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            *dt.goals,
            *tq_goals,
            ExpressionGoal(
                id="electronic_estimate",
                terms=(
                    GoalTerm(goal="tq:high:reference", coefficient=1),
                    GoalTerm(goal=tq.target, coefficient=1),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                reason="Finite QZ reference plus extrapolated TQ correction",
            ),
            ExpressionGoal(
                id="comparison",
                terms=(
                    GoalTerm(goal=tq.target, coefficient=1),
                    GoalTerm(goal=dt.target, coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
                reason="Symbolic comparison of two explicitly chosen estimates",
            ),
        ),
    )


def main() -> None:
    """Save a checked basis-limit construction and two independent rejection examples.

    Raises:
        SystemExit: Evidence cannot construct the accepted example or reject a defect.
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
    proposal = propose(request, catalog)
    args.destination.mkdir()
    (args.destination / "proposal.json").write_text(
        proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    if proposal.plan is None:
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    rejections: dict[str, JsonValue] = {}
    for name, damaged in (
        ("wrong-family", _request(wrong_family=True)),
        ("wrong-weights", _request(wrong_weights=True)),
    ):
        rejected = propose(damaged, catalog)
        (args.destination / f"{name}-request.json").write_text(
            damaged.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        (args.destination / f"{name}-proposal.json").write_text(
            rejected.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        if rejected.plan is not None:
            raise SystemExit(f"Unexpected acceptance of {name}")
        rejections[name] = rejected.status
    summary: dict[str, JsonValue] = {
        "status": proposal.status,
        "goals": len(request.goals),
        "top_level_calls": sum(
            isinstance(step, Calculation) for step in proposal.plan.steps
        ),
        "reuses": [
            _JSON.validate_json(item.model_dump_json()) for item in proposal.reuses
        ],
        "recipes": [
            _JSON.validate_json(item.extrapolation.model_dump_json())
            for item in exported.manifest.expressions
            if item.extrapolation
        ],
        "rejections": rejections,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
