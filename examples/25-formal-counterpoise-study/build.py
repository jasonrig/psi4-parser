"""Compose constrained optimizations and full-basis counterpoise at two inputs."""

import argparse
import json
import sys
from pathlib import Path

from psi4_parser.builder import (
    ElectronicState,
    Molecule,
    angstrom,
    assemble_fragments,
    distance,
    freeze,
    molecule,
)
from psi4_parser.formal import (
    CalculationGoal,
    CapabilityCatalog,
    CoordinateValue,
    FragmentStudy,
    Model,
    Plan,
    SameModel,
    ScientificRequest,
    Setting,
    StudyCase,
    export_bundle,
    finite_study,
    fragment_expansion,
    propose,
    verify,
)


class _Arguments:
    capabilities: Path
    destination: Path


def cluster(separation: float) -> Molecule:
    """Create two singlet H2 fragments with a fixed frame and atom IDs.

    Args:
        separation: Starting separation of corresponding H atoms in angstrom.

    Returns:
        Four-atom cluster with fragment-local IDs prefixed by A and B.
    """
    state = ElectronicState(charge=0, multiplicity=1)
    first = Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .75\n", state=state)
    second = Molecule.from_xyz(
        f"2\nH2\nH {separation} 0 0\nH {separation} 0 .75\n", state=state
    )
    assembly = assemble_fragments(("A", first), ("B", second), state=state)
    return Molecule(
        atoms=assembly.atoms,
        fragments=assembly.fragments,
        state=state,
        fixed_com=True,
        fixed_orientation=True,
    )


def main() -> None:
    """Save independent case histories, ghost provenance, and symbolic recipes.

    Raises:
        SystemExit: No accepted plan can be exported; inspect the saved proposal.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--capabilities",
        type=Path,
        default=Path(__file__).parents[1] / "formal-demo-capabilities.json",
    )
    args = parser.parse_args(namespace=_Arguments())
    catalog = CapabilityCatalog.model_validate_json(args.capabilities.read_bytes())
    parent = cluster(3.0)
    model = Model(
        method="scf",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="pk"),),
    )
    expansion = fragment_expansion(
        FragmentStudy(
            id="cp", geometry="opt", fragments=parent.fragments, models=(model,)
        )
    )
    template = ScientificRequest(
        molecules=(molecule("cluster", parent),),
        goals=(
            CalculationGoal(
                id="opt",
                driver="optimize",
                geometry="cluster",
                models=(model,),
                constraints=(freeze(distance("A:a1", "B:a1")),),
                reason="Relax other coordinates while retaining the selected distance",
            ),
            *expansion.goals,
        ),
        relations=expansion.relations,
    )
    request = finite_study(
        template,
        tuple(
            StudyCase(
                id=case,
                molecules=(molecule("cluster", cluster(separation)),),
                relations=tuple(
                    CoordinateValue(
                        geometry=geometry,
                        coordinate=distance("A:a1", "B:a1"),
                        value=angstrom(separation),
                        tolerance=angstrom(1e-7),
                    )
                    for geometry in ("cluster", "opt")
                ),
            )
            for case, separation in (("r3", 3.0), ("r4", 4.0))
        ),
    )
    args.destination.mkdir()
    (args.destination / "request.json").write_text(
        request.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    proposal = propose(request, catalog)
    if proposal.plan is None:
        (args.destination / "proposal.json").write_text(
            proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        raise SystemExit(f"Planning returned {proposal.status}; inspect proposal.json")
    exported = export_bundle(
        proposal.plan, request, catalog, args.destination / "bundle"
    )
    # A self-consistent plan still fails when it omits a requested final formula.
    incomplete = Plan(
        molecules=proposal.plan.molecules,
        steps=proposal.plan.steps[:-1],
        requirements=(SameModel(calculations=("r3:opt", "r3:opt")),),
    )
    missing_work = verify(incomplete, request=request, catalog=catalog)
    (args.destination / "omitted-goal.json").write_text(
        missing_work.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "status": proposal.status,
        "goals": len(request.goals),
        "future_geometries": [
            item.id
            for item in exported.manifest.geometries
            if not item.coordinates_known
        ],
        "expressions": [item.id for item in exported.manifest.expressions],
        "omitted_goal": missing_work.status,
    }
    (args.destination / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Construction artifacts: {args.destination}\n")


if __name__ == "__main__":
    main()
