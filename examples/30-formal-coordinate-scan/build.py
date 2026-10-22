"""Construct a constrained water scan with independently required O-H distances."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import (
    ElectronicState,
    Molecule,
    angstrom,
    distance,
    freeze,
    molecule,
    set_distance,
)
from psi4_parser.formal import (
    CalculationGoal,
    CoordinateValue,
    Model,
    ScientificRequest,
    Setting,
    StudyCase,
    export_bundle,
    finite_study,
    load_catalog,
    propose,
)


class _Arguments:
    destination: Path


def _request(*, wrong_input: bool = False, constrain: bool = True) -> ScientificRequest:
    water = Molecule.from_xyz(
        "3\nWater\nO 0 0 0\nH 0 -.757 .587\nH 0 .757 .587\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    coordinate = distance("a1", "a2")
    model = Model(
        method="hf",
        basis="cc-pvdz",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    template = ScientificRequest(
        molecules=(molecule("water", water),),
        goals=(
            CalculationGoal(
                id="relaxed",
                driver="optimize",
                geometry="water",
                models=(model,),
                constraints=(freeze(coordinate),) if constrain else (),
                derivative_routes=("analytic",),
            ),
        ),
    )
    cases: list[StudyCase] = []
    for name, value in (("short", 0.9), ("long", 1.1)):
        prepared = water | set_distance(
            ("a1", "a2"), angstrom(0.9 if wrong_input else value), moving=("a2",)
        )
        cases.append(
            StudyCase(
                id=name,
                molecules=(molecule("water", prepared),),
                relations=tuple(
                    CoordinateValue(
                        geometry=geometry,
                        coordinate=coordinate,
                        value=angstrom(value),
                        tolerance=angstrom(1e-7),
                    )
                    for geometry in ("water", "relaxed")
                ),
            )
        )
    return finite_study(template, tuple(cases))


def main() -> None:
    """Save accepted and rejected scan construction artifacts without execution.

    Raises:
        SystemExit: The reviewed catalog cannot accept the example request.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(namespace=_Arguments())
    catalog = load_catalog("psi4")
    request = _request()
    proposal = propose(request, catalog)
    args.destination.mkdir()
    if proposal.plan is None:
        (args.destination / "proposal.json").write_text(
            proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    export_bundle(proposal.plan, request, catalog, args.destination / "bundle")
    (args.destination / "request.json").write_text(
        request.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    wrong = propose(_request(wrong_input=True), catalog)
    unconstrained = propose(_request(constrain=False), catalog)
    for name, result in (("wrong-point", wrong), ("unconstrained", unconstrained)):
        (args.destination / f"{name}.json").write_text(
            result.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    summary = {
        "status": proposal.status,
        "wrong_point": wrong.status,
        "unconstrained_future": unconstrained.status,
        "coordinate_checks": len(request.relations),
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Coordinate scan construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
