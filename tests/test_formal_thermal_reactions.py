"""Check thermal reaction meaning independently from exact scalar algebra."""

from pathlib import Path
from typing import Literal

import pytest

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    CalculationGoal,
    Combination,
    EnergyFormula,
    EnergyTerm,
    Model,
    Plan,
    Product,
    QuantityType,
    Rational,
    ReactionParticipant,
    ReactionStudy,
    ReactionThermochemistry,
    ScientificRequest,
    Setting,
    StudyCase,
    ThermalConditions,
    VibrationalAnalysis,
    export_bundle,
    finite_study,
    load_catalog,
    propose,
    reaction_expansion,
    verify,
)
from psi4_parser.formal.science import ProductName


def _analysis(symmetry: int, *, temperature: float = 298.15) -> VibrationalAnalysis:
    return VibrationalAnalysis(
        conditions=ThermalConditions(
            temperature_kelvin=temperature, pressure_pascal=101325.0
        ),
        rotational_symmetry_number=symmetry,
    )


def _oxidation(product: ProductName = "gibbs_free_energy") -> Plan:
    inputs = (
        molecule(
            "co",
            Molecule.from_xyz(
                "2\nCO\nC 0 0 0\nO 0 0 1.13\n",
                state=ElectronicState(charge=0, multiplicity=1),
            ),
        ),
        molecule(
            "oxygen",
            Molecule.from_xyz(
                "2\nO2\nO 0 0 0\nO 0 0 1.21\n",
                state=ElectronicState(charge=0, multiplicity=3),
            ),
        ),
        molecule(
            "co2",
            Molecule.from_xyz(
                "3\nCO2\nO 0 0 -1.16\nC 0 0 0\nO 0 0 1.16\n",
                state=ElectronicState(charge=0, multiplicity=1),
            ),
        ),
    )
    steps: list[Calculation | Product | Combination] = []
    for name, symmetry in (("co", 1), ("oxygen", 2), ("co2", 2)):
        frequency = f"{name}_frequency"
        steps.extend(
            (
                Calculation(
                    id=frequency,
                    driver="frequency",
                    geometry=name,
                    model=Model(
                        method="hf",
                        basis="sto-3g",
                        reference="uhf" if name == "oxygen" else "rhf",
                    ),
                    analysis=_analysis(symmetry),
                ),
                Product(id=f"{name}_total", calculation=frequency, name=product),
            )
        )
    steps.append(
        Combination(
            id="reaction",
            terms=(
                EnergyTerm(result="co_total", coefficient=-1),
                EnergyTerm(
                    result="oxygen_total",
                    coefficient=Rational(numerator=-1, denominator=2),
                ),
                EnergyTerm(result="co2_total", coefficient=1),
            ),
            quantity=QuantityType(meaning=f"reaction_{product}", unit="hartree"),
        )
    )
    return Plan(
        molecules=inputs,
        steps=tuple(steps),
        requirements=(
            EnergyFormula(
                result="reaction",
                terms=(
                    EnergyTerm(result="co_total", coefficient=-1),
                    EnergyTerm(
                        result="oxygen_total",
                        coefficient=Rational(numerator=-1, denominator=2),
                    ),
                    EnergyTerm(result="co2_total", coefficient=1),
                ),
            ),
        ),
    )


@pytest.mark.parametrize(
    "product", ["gibbs_free_energy", "enthalpy", "thermal_energy", "zero_k_enthalpy"]
)
def test_closed_thermal_reactions_keep_species_specific_symmetry(
    product: ProductName,
) -> None:
    """Accept CO + 1/2 O2 -> CO2 at one thermal state with distinct symmetry.

    Args:
        product: Molecular thermal total whose reaction is required.
    """
    report = verify(_oxidation(product))

    assert report.status == "proved", report.diagnostics


def _thermal_request(*, hybrid: bool = False) -> ScientificRequest:
    participants: list[ReactionParticipant] = []
    for name, symmetry, coefficient in (
        ("co", 1, -1),
        ("oxygen", 2, Rational(numerator=-1, denominator=2)),
        ("co2", 2, 1),
    ):
        reference: Literal["rhf", "uhf"] = "uhf" if name == "oxygen" else "rhf"
        frequency_model = Model(
            method="hf",
            basis="sto-3g",
            reference=reference,
            settings=(Setting(name="scf_type", value="PK"),),
        )
        energy_model = (
            Model(
                method="mp2",
                basis="sto-3g",
                reference=reference,
                frozen_core=True,
                settings=(
                    Setting(name="scf_type", value="PK"),
                    Setting(name="mp2_type", value="CONV"),
                    Setting(name="qc_module", value="OCC"),
                ),
            )
            if hybrid
            else frequency_model
        )
        participants.append(
            ReactionParticipant(
                id=name,
                geometry=name,
                coefficient=coefficient,
                models=(energy_model,),
                thermochemistry=ReactionThermochemistry(
                    analysis=_analysis(symmetry),
                    models=(frequency_model,) if hybrid else (),
                ),
            )
        )
    expansion = reaction_expansion(
        ReactionStudy(
            id="oxidation",
            participants=tuple(participants),
            quantity="gibbs_free_energy",
        )
    )
    return ScientificRequest(molecules=_oxidation().molecules, goals=expansion.goals)


@pytest.mark.parametrize("hybrid", [False, True])
def test_thermal_reaction_expansion_uses_native_or_explicit_hybrid_models(
    hybrid: bool,
) -> None:
    """Compose a checked Gibbs reaction without redundant native energy calls.

    Args:
        hybrid: Require separate MP2 electronic energies and HF RRHO corrections.
    """
    request = _thermal_request(hybrid=hybrid)

    assert (
        sum(
            isinstance(goal, CalculationGoal) and goal.driver == "frequency"
            for goal in request.goals
        )
        == 3
    )
    assert sum(
        isinstance(goal, CalculationGoal) and goal.driver == "energy"
        for goal in request.goals
    ) == (3 if hybrid else 0)
    proposal = propose(request, load_catalog("psi4"))

    assert proposal.status == "constructed", proposal.report
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert (
        proposal.report.quantities[-1].quantity.meaning == "reaction_gibbs_free_energy"
    )


def test_nested_thermal_reactions_preserve_exact_rational_weights() -> None:
    """Scale a reaction by 3/2 and ignore an exactly zero rational energy term."""
    plan = _oxidation()
    scaled = Combination(
        id="scaled",
        terms=(
            EnergyTerm(
                result="reaction", coefficient=Rational(numerator=3, denominator=2)
            ),
            EnergyTerm(result="co_frequency", coefficient=Rational(numerator=0)),
        ),
        quantity=QuantityType(meaning="reaction_gibbs_free_energy", unit="hartree"),
    )
    expected = EnergyFormula(
        result="scaled",
        terms=(
            EnergyTerm(
                result="co_total", coefficient=Rational(numerator=-3, denominator=2)
            ),
            EnergyTerm(
                result="oxygen_total", coefficient=Rational(numerator=-3, denominator=4)
            ),
            EnergyTerm(
                result="co2_total", coefficient=Rational(numerator=3, denominator=2)
            ),
        ),
    )

    report = verify(
        Plan(
            molecules=plan.molecules,
            steps=(*plan.steps, scaled),
            requirements=(*plan.requirements, expected),
        )
    )

    assert report.status == "proved", report.diagnostics


@pytest.mark.parametrize("change", ["temperature", "pressure", "projection"])
def test_thermal_reactions_reject_mixed_analysis_contexts(change: str) -> None:
    """Reject mixed thermal states even when the reaction formula stays exact.

    Args:
        change: Alter one species' temperature, pressure, or projection choices.
    """
    plan = _oxidation()
    altered = VibrationalAnalysis(
        conditions=ThermalConditions(
            temperature_kelvin=400.0 if change == "temperature" else 298.15,
            pressure_pascal=100000.0 if change == "pressure" else 101325.0,
        ),
        rotational_symmetry_number=2,
        project_rotations=change != "projection",
    )
    steps = tuple(
        Calculation(
            id=step.id,
            driver=step.driver,
            geometry=step.geometry,
            model=step.model,
            analysis=altered,
        )
        if isinstance(step, Calculation) and step.id == "co2_frequency"
        else step
        for step in plan.steps
    )

    report = verify(
        Plan(molecules=plan.molecules, steps=steps, requirements=plan.requirements)
    )

    assert report.status == "violated"
    assert any(issue.code == "reaction_thermal_context" for issue in report.diagnostics)


def test_reaction_gibbs_energy_cannot_omit_one_species_correction() -> None:
    """Reject a raw electronic energy substituted for a molecular Gibbs total."""
    plan = _oxidation()
    steps = tuple(
        Product(id=step.id, calculation=step.calculation, name="electronic_energy")
        if isinstance(step, Product) and step.id == "co2_total"
        else step
        for step in plan.steps
    )

    report = verify(
        Plan(molecules=plan.molecules, steps=steps, requirements=plan.requirements)
    )

    assert report.status == "unsupported"
    assert any(issue.code == "reaction_source" for issue in report.diagnostics)


def test_thermal_reaction_checks_nuclei_even_with_self_consistent_formula() -> None:
    """Reject CO + 1/2 O2 -> 2 CO2 despite agreeing requested and proposed algebra."""
    plan = _oxidation()
    terms = (
        EnergyTerm(result="co_total", coefficient=-1),
        EnergyTerm(
            result="oxygen_total", coefficient=Rational(numerator=-1, denominator=2)
        ),
        EnergyTerm(result="co2_total", coefficient=2),
    )
    steps = (
        *plan.steps[:-1],
        Combination(
            id="reaction",
            terms=terms,
            quantity=QuantityType(meaning="reaction_gibbs_free_energy", unit="hartree"),
        ),
    )

    report = verify(
        Plan(
            molecules=plan.molecules,
            steps=steps,
            requirements=(EnergyFormula(result="reaction", terms=terms),),
        )
    )

    assert report.status == "violated"
    assert any(issue.code == "reaction_balance" for issue in report.diagnostics)


def test_hybrid_reaction_balances_correction_models_separately() -> None:
    """Reject one changed correction basis while all electronic models still match."""
    proposal = propose(_thermal_request(hybrid=True), load_catalog("psi4"))
    assert proposal.plan is not None
    plan = proposal.plan
    steps = tuple(
        Calculation(
            id=step.id,
            driver=step.driver,
            geometry=step.geometry,
            model=Model(
                method="hf",
                basis="6-31g",
                reference="uhf",
                settings=(Setting(name="scf_type", value="PK"),),
            ),
            analysis=step.analysis,
            satisfies=step.satisfies,
        )
        if isinstance(step, Calculation) and step.id == "oxidation:frequency:oxygen"
        else step
        for step in plan.steps
    )

    report = verify(
        Plan(molecules=plan.molecules, steps=steps, requirements=plan.requirements)
    )

    assert report.status == "violated"
    assert any(issue.code == "reaction_model_balance" for issue in report.diagnostics)


def test_thermal_reaction_export_composes_with_finite_cases(tmp_path: Path) -> None:
    """Namespace product provenance and persist native bindings without retrieval.

    Args:
        tmp_path: New bundle destination parent.
    """
    template = _thermal_request()
    request = finite_study(
        template,
        (
            StudyCase(id="first", molecules=template.molecules),
            StudyCase(id="second", molecules=template.molecules),
        ),
    )
    catalog = load_catalog("psi4")
    proposal = propose(request, catalog)
    assert proposal.plan is not None

    bundle = export_bundle(proposal.plan, request, catalog, tmp_path / "bundle")

    assert len(bundle.manifest.native_outputs) == 6
    assert len({output.label for output in bundle.manifest.native_outputs}) == 6
    assert {expression.id for expression in bundle.manifest.expressions} == {
        "first:oxidation:reaction",
        "second:oxidation:reaction",
    }
    source = (Path(bundle.directory) / bundle.manifest.native_inputs[0]).read_text()
    assert ".variable(" not in source
    assert "json.load" not in source


@pytest.mark.parametrize("thermal", [False, True])
def test_reaction_expansion_requires_matching_thermal_configuration(
    thermal: bool,
) -> None:
    """Reject missing thermal analysis or analysis attached to electronic intent.

    Args:
        thermal: Request thermal intent without analysis instead of the converse.
    """
    model = Model(method="hf", basis="sto-3g", reference="rhf")
    species = tuple(
        ReactionParticipant(
            id=name,
            geometry=name,
            coefficient=coefficient,
            models=(model,),
            thermochemistry=None
            if thermal
            else ReactionThermochemistry(analysis=_analysis(2)),
        )
        for name, coefficient in (("first", -1), ("second", 1))
    )
    specification = ReactionStudy(
        id="invalid",
        participants=species,
        quantity="gibbs_free_energy" if thermal else "electronic_energy",
    )

    with pytest.raises(ValueError, match="thermochemistry"):
        reaction_expansion(specification)
