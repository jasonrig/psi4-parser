"""Build H2 optimization and frequencies with a proved geometry dependency."""

from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    Model,
    Plan,
    SameModel,
    Setting,
    UsesGeometry,
    render,
    verify,
)

folder = Path(__file__).parent
geometry = Molecule.from_xyz(
    "2\nHydrogen\nH 0 0 0\nH 0 0 0.85\n",
    state=ElectronicState(charge=0, multiplicity=1),
)
model = Model(
    method="scf",
    basis="sto-3g",
    reference="rhf",
    settings=(Setting(name="scf_type", value="PK"),),
)
optimization = Calculation(id="opt", driver="optimize", geometry="h2", model=model)
frequencies = Calculation(id="freq", driver="frequency", geometry="opt", model=model)
plan = Plan(
    molecules=(molecule("h2", geometry),),
    steps=(optimization, frequencies),
    requirements=(
        UsesGeometry(calculation="freq", geometry="opt"),
        SameModel(calculations=("opt", "freq")),
    ),
)
folder.joinpath("plan.json").write_text(
    plan.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
folder.joinpath("proof.json").write_text(
    verify(plan).model_dump_json(indent=2) + "\n", encoding="utf-8"
)
folder.joinpath("input.dat").write_text(render(plan), encoding="utf-8")

stale = Calculation(id="freq", driver="frequency", geometry="h2", model=model)
rejected = Plan(
    molecules=plan.molecules,
    steps=(optimization, stale),
    requirements=plan.requirements,
)
folder.joinpath("rejected.json").write_text(
    verify(rejected).model_dump_json(indent=2) + "\n", encoding="utf-8"
)
