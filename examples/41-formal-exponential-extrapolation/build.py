"""Compose certified exponential references with an inverse-power correction."""

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BasisCorrectionPoint,
    BasisEnergyPoint,
    Calculation,
    ExpressionGoal,
    ExtrapolationStudy,
    GoalTerm,
    Model,
    QuantityType,
    Rational,
    ReferenceExtrapolationStudy,
    ScientificRequest,
    Setting,
    export_bundle,
    extrapolation_expansion,
    propose,
)
from psi4_parser.formal.extrapolation_plans import ExtrapolationExpansion


class _Arguments:
    destination: Path


def _model(method: str, basis: str) -> Model:
    settings: tuple[Setting, ...] = (Setting(name="scf_type", value="PK"),)
    if method == "mp2":
        settings = (
            *settings,
            Setting(name="mp2_type", value="CONV"),
            Setting(name="qc_module", value="OCC"),
        )
    return Model(method=method, basis=basis, reference="rhf", settings=settings)


def _reference(
    name: str,
    low: tuple[str, int],
    high: tuple[str, int],
    *,
    alpha: Rational,
    shape: Literal["cardinal", "sqrt_cardinal"],
) -> ExtrapolationExpansion:
    return extrapolation_expansion(
        ReferenceExtrapolationStudy(
            id=name,
            geometry="water",
            family="cc-pvXZ",
            low=BasisEnergyPoint(
                basis=low[0], cardinal=low[1], models=(_model("hf", low[0]),)
            ),
            high=BasisEnergyPoint(
                basis=high[0], cardinal=high[1], models=(_model("hf", high[0]),)
            ),
            alpha=alpha,
            shape=shape,
            coefficient_digits=18,
            reuse_group="common-evaluations",
        )
    )


def main() -> None:
    """Save two HF limit estimates, an MP2 correction, and checked symbolic composites.

    Raises:
        SystemExit: Planning fails, or the deliberately wrong formula is accepted.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(namespace=_Arguments())
    args.destination.mkdir()
    geometry = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH .758 0 .504\nH -.758 0 .504\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    linear = _reference(
        "linear_dt",
        ("cc-pvdz", 2),
        ("cc-pvtz", 3),
        alpha=Rational(numerator=163, denominator=100),
        shape="cardinal",
    )
    square_root = _reference(
        "sqrt_tq",
        ("cc-pvtz", 3),
        ("cc-pvqz", 4),
        alpha=Rational(numerator=63, denominator=10),
        shape="sqrt_cardinal",
    )
    points = tuple(
        BasisCorrectionPoint(
            basis=basis,
            cardinal=cardinal,
            models=(_model("mp2", basis),),
            reference_models=(_model("hf", basis),),
        )
        for basis, cardinal in (("cc-pvtz", 3), ("cc-pvqz", 4))
    )
    correction = extrapolation_expansion(
        ExtrapolationStudy(
            id="correlation_tq",
            geometry="water",
            family="cc-pvXZ",
            power=3,
            low=points[0],
            high=points[1],
            reuse_group="common-evaluations",
        )
    )
    totals = tuple(
        ExpressionGoal(
            id=name,
            terms=(
                GoalTerm(goal=reference.target, coefficient=1),
                GoalTerm(goal=correction.target, coefficient=1),
            ),
            quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            reason="Exponential HF reference plus inverse-cube correlation estimate",
        )
        for name, reference in (("linear_total", linear), ("sqrt_total", square_root))
    )
    request = ScientificRequest(
        molecules=(molecule("water", geometry),),
        goals=(
            *linear.goals,
            *square_root.goals,
            *correction.goals,
            *totals,
            ExpressionGoal(
                id="model_comparison",
                terms=(
                    GoalTerm(goal=totals[1].id, coefficient=1),
                    GoalTerm(goal=totals[0].id, coefficient=-1),
                ),
                quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            ),
        ),
    )
    (args.destination / "request.json").write_text(
        request.model_dump_json(indent=2) + "\n"
    )
    proposed = propose(request)
    (args.destination / "proposal.json").write_text(
        proposed.model_dump_json(indent=2) + "\n"
    )
    if proposed.plan is None:
        raise SystemExit(f"Inspect the {proposed.status} proposal")
    export_bundle(proposed.plan, request, destination=args.destination / "bundle")
    correct = linear.goals[-1]
    if not isinstance(correct, ExpressionGoal):
        raise SystemExit("Expected an exponential reference expression")
    wrong = ExpressionGoal(
        id=correct.id,
        terms=(
            GoalTerm(goal=linear.goals[0].id, coefficient=-1),
            GoalTerm(goal=linear.goals[1].id, coefficient=2),
        ),
        quantity=correct.quantity,
        extrapolation=correct.extrapolation,
        reason="Deliberately wrong complementary weights",
    )
    damaged = ScientificRequest(
        molecules=request.molecules,
        goals=(*linear.goals[:-1], wrong, *request.goals[3:]),
    )
    rejected = propose(damaged)
    (args.destination / "wrong-weight-request.json").write_text(
        damaged.model_dump_json(indent=2) + "\n"
    )
    (args.destination / "wrong-weight-proposal.json").write_text(
        rejected.model_dump_json(indent=2) + "\n"
    )
    if rejected.plan is not None:
        raise SystemExit("The incorrect exponential formula was accepted")
    summary = {
        "status": proposed.status,
        "mandatory_goals": len(request.goals),
        "driver_calls": sum(
            isinstance(step, Calculation) for step in proposed.plan.steps
        ),
        "shared_calls": len(proposed.reuses),
        "wrong_weight_status": rejected.status,
        "coefficient_bound": "Absolute error at most 1e-18 per exponential weight",
        "scope": "Construction and symbolic formulas; physical convergence assumed",
    }
    (args.destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sys.stdout.write(f"Exponential construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
