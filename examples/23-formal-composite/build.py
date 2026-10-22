"""Build an illustrative electronic-energy correction and prove its algebra."""

from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    Combination,
    EnergyFormula,
    EnergyTerm,
    Model,
    Plan,
    SameGeometry,
    Setting,
    render,
    verify,
)

folder = Path(__file__).parent
geometry = Molecule.from_xyz(
    "2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n",
    state=ElectronicState(charge=0, multiplicity=1),
)
calculations = (
    Calculation(
        id="hf_large",
        driver="energy",
        geometry="h2",
        model=Model(
            method="scf",
            basis="cc-pvdz",
            reference="rhf",
            settings=(Setting(name="scf_type", value="PK"),),
        ),
    ),
    Calculation(
        id="mp2_small",
        driver="energy",
        geometry="h2",
        model=Model(
            method="mp2",
            basis="sto-3g",
            reference="rhf",
            settings=(
                Setting(name="scf_type", value="PK"),
                Setting(name="mp2_type", value="CONV"),
                Setting(name="qc_module", value="OCC"),
            ),
        ),
    ),
    Calculation(
        id="hf_small",
        driver="energy",
        geometry="h2",
        model=Model(
            method="scf",
            basis="sto-3g",
            reference="rhf",
            settings=(Setting(name="scf_type", value="PK"),),
        ),
    ),
)
correction = Combination(
    id="correction",
    terms=(
        EnergyTerm(result="mp2_small", coefficient=1),
        EnergyTerm(result="hf_small", coefficient=-1),
    ),
)
total = Combination(
    id="estimate",
    terms=(
        EnergyTerm(result="hf_large", coefficient=1),
        EnergyTerm(result="correction", coefficient=1),
    ),
)
plan = Plan(
    molecules=(molecule("h2", geometry),),
    steps=(*calculations, correction, total),
    requirements=(
        SameGeometry(calculations=("hf_large", "mp2_small")),
        SameGeometry(calculations=("hf_large", "hf_small")),
        EnergyFormula(
            result="estimate",
            terms=(
                EnergyTerm(result="hf_large", coefficient=1),
                EnergyTerm(result="mp2_small", coefficient=1),
                EnergyTerm(result="hf_small", coefficient=-1),
            ),
        ),
    ),
)
folder.joinpath("plan.json").write_text(
    plan.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
folder.joinpath("proof.json").write_text(
    verify(plan).model_dump_json(indent=2) + "\n", encoding="utf-8"
)
folder.joinpath("input.dat").write_text(render(plan), encoding="utf-8")

# Add the HF contribution twice: the independent formula must reject this plan.
wrong = Combination(
    id="estimate", terms=(*total.terms, EnergyTerm(result="hf_small", coefficient=1))
)
rejected = Plan(
    molecules=plan.molecules,
    steps=(*calculations, correction, wrong),
    requirements=plan.requirements,
)
folder.joinpath("rejected.json").write_text(
    verify(rejected).model_dump_json(indent=2) + "\n", encoding="utf-8"
)
