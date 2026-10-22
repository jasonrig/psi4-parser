"""Check scientific distinctions that must survive planning and serialization."""

import pytest

from psi4_parser import validate
from psi4_parser.builder import ElectronicState, Molecule, distance, freeze, molecule
from psi4_parser.formal import (
    Calculation,
    Combination,
    EnergyFormula,
    EnergyTerm,
    Limits,
    Model,
    Plan,
    Rational,
    SameModel,
    UsesGeometry,
    render,
    verify,
)


def test_core_treatment_is_part_of_model_equality() -> None:
    """Do not prove model equality across different frozen-core choices."""
    source = """{
      "molecules": [],
      "steps": [
        {"kind":"calculation", "id":"all", "driver":"energy", "geometry":"h2",
         "model":{"method":"mp2", "basis":"cc-pvdz", "reference":"rhf",
                  "frozen_core":false}},
        {"kind":"calculation", "id":"frozen", "driver":"energy", "geometry":"h2",
         "model":{"method":"mp2", "basis":"cc-pvdz", "reference":"rhf",
                  "frozen_core":true}}
      ],
      "requirements":[{"kind":"same_model", "calculations":["all","frozen"]}]
    }"""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    declaration = molecule("h2", geometry).model_dump_json()
    plan = Plan.model_validate_json(
        source.replace('"molecules": []', f'"molecules": [{declaration}]')
    )

    assert verify(plan).status == "violated"


def hydrogen_plan(*steps: Calculation | Combination) -> Plan:
    """Return a small molecular plan with a minimal geometry requirement."""
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return Plan(
        molecules=(molecule("h2", geometry),),
        steps=steps,
        requirements=(UsesGeometry(calculation="e", geometry="h2"),),
    )


def test_rational_expressions_prove_exactly_and_render_as_numbers() -> None:
    """Prove nested half-weight sums without treating model objects as Python code."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    original = hydrogen_plan(
        Calculation(id="e", driver="energy", geometry="h2", model=model),
        Combination(
            id="half",
            terms=(
                EnergyTerm(
                    result="e", coefficient=Rational(numerator=1, denominator=2)
                ),
            ),
        ),
        Combination(id="whole", terms=(EnergyTerm(result="half", coefficient=2),)),
    )
    plan = Plan(
        molecules=original.molecules,
        steps=original.steps,
        requirements=(
            EnergyFormula(
                result="whole", terms=(EnergyTerm(result="e", coefficient=1),)
            ),
        ),
    )

    assert verify(plan).status == "proved"
    source = render(plan)
    assert "numerator=" not in source
    assert validate(source) == ()
    assert Plan.model_validate_json(plan.model_dump_json()) == plan


def test_gradient_cannot_be_used_as_an_energy() -> None:
    """Reject a matrix in a scalar energy expression before invoking the backend."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    plan = hydrogen_plan(
        Calculation(id="e", driver="gradient", geometry="h2", model=model),
        Combination(id="sum", terms=(EnergyTerm(result="e", coefficient=1),)),
    )

    assert verify(plan).status == "invalid"


def test_verification_budgets_remain_undecided() -> None:
    """Preserve unknown when a plan exceeds explicit resource bounds."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    plan = hydrogen_plan(
        Calculation(id="e", driver="energy", geometry="h2", model=model),
        Calculation(id="other", driver="energy", geometry="h2", model=model),
    )

    report = verify(plan, limits=Limits(max_steps=1))

    assert report.status == "unknown"
    assert report.limits.max_steps == 1
    assert report.diagnostics[0].code == "verification_budget"


def test_private_geometry_retains_constraint_atom_identities() -> None:
    """Compile stable-atom constraints after cloning a molecule for optimization."""
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    plan = hydrogen_plan(
        Calculation(
            id="e",
            driver="optimize",
            geometry="h2",
            model=model,
            constraints=(freeze(distance("a1", "a2")),),
        )
    )

    source = render(plan)

    assert validate(source) == ()
    assert "FROZEN_DISTANCE" in source


@pytest.mark.parametrize("multiplicity", [2, 5])
def test_electron_and_spin_bookkeeping(multiplicity: int) -> None:
    """Reject impossible spin parity and more unpaired electrons than available.

    Args:
        multiplicity: Impossible spin multiplicity for neutral H2.
    """
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=0, multiplicity=multiplicity),
    )
    model = Model(method="scf", basis="sto-3g", reference="uhf")
    plan = Plan(
        molecules=(molecule("h2", geometry),),
        steps=(Calculation(id="e", driver="energy", geometry="h2", model=model),),
        requirements=(SameModel(calculations=("e", "e")),),
    )

    report = verify(plan)
    assert report.status == "violated"
    assert any(issue.code == "electronic_state" for issue in report.diagnostics)
