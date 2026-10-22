"""Check nuclear and charge conservation independently of exact energy algebra."""

import pytest

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BasisCapability,
    BasisFunctions,
    Calculation,
    CalculationGoal,
    CapabilityCatalog,
    ExpressionGoal,
    GoalTerm,
    MethodCapability,
    Model,
    Plan,
    QuantityType,
    Rational,
    ReactionExpansion,
    ReactionParticipant,
    ReactionStudy,
    ScientificRequest,
    StudyCase,
    finite_study,
    propose,
    reaction_expansion,
    verify,
)


def reaction_profile(original: CapabilityCatalog) -> CapabilityCatalog:
    """Return synthetic support including open-shell energy calculations."""
    return CapabilityCatalog(
        id="reaction-fixture",
        evidence=original.evidence,
        methods=(
            *original.methods,
            MethodCapability(
                method="scf",
                driver="energy",
                reference="uhf",
                status="supported",
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                features=("ghost_centers", "frozen_core"),
                evidence=("fixture",),
            ),
        ),
        bases=original.bases,
        options=original.options,
    )


def dissociation(
    *,
    atom: str = "H",
    coefficient: int | Rational = 2,
    reactant_coefficient: int | Rational = -1,
    ghost: bool = False,
) -> ScientificRequest:
    """Return H2 dissociation with explicitly supplied stoichiometric coefficients."""
    dimer = Molecule.from_xyz(
        "3\nH2 with ghost\nH 0 0 0\nH 0 0 .75\n@H 3 0 0\n"
        if ghost
        else "2\nH2\nH 0 0 0\nH 0 0 .75\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    product = Molecule.from_xyz(
        f"1\nAtom\n{atom} 0 0 0\n",
        state=ElectronicState(charge=0, multiplicity=2),
    )
    return ScientificRequest(
        molecules=(molecule("h2", dimer), molecule("atom", product)),
        goals=(
            CalculationGoal(
                id="molecular",
                driver="energy",
                geometry="h2",
                models=(Model(method="scf", basis="sto-3g", reference="rhf"),),
            ),
            CalculationGoal(
                id="atomic",
                driver="energy",
                geometry="atom",
                models=(Model(method="scf", basis="sto-3g", reference="uhf"),),
            ),
            ExpressionGoal(
                id="dissociation",
                terms=(
                    GoalTerm(goal="molecular", coefficient=reactant_coefficient),
                    GoalTerm(goal="atomic", coefficient=coefficient),
                ),
                quantity=QuantityType(meaning="reaction_energy", unit="hartree"),
            ),
        ),
    )


@pytest.mark.parametrize("ghost", [False, True])
def test_reaction_balances_real_nuclei_with_species_specific_references(
    formal_profile: CapabilityCatalog, ghost: bool
) -> None:
    """Accept H2 -> 2 H while retaining RHF/UHF choices and ignoring ghost nuclei.

    Args:
        formal_profile: Synthetic application support.
        ghost: Include one basis-only center in the reactant.
    """
    proposal = propose(dissociation(ghost=ghost), reaction_profile(formal_profile))

    assert proposal.status == "constructed"
    assert proposal.report is not None
    assert proposal.report.request_complete


def test_fractional_stoichiometry_remains_exact(
    formal_profile: CapabilityCatalog,
) -> None:
    """Accept half a hydrogen molecule per atom without floating-point balancing.

    Args:
        formal_profile: Synthetic application support.
    """
    request = dissociation(
        coefficient=1, reactant_coefficient=Rational(numerator=-1, denominator=2)
    )

    assert propose(request, reaction_profile(formal_profile)).status == "constructed"


@pytest.mark.parametrize("atom", ["H", "2H", "H@2.0"])
def test_exact_energy_algebra_cannot_hide_missing_or_relabelled_nuclei(
    formal_profile: CapabilityCatalog, atom: str
) -> None:
    """Reject an atom deficit, isotope substitution, or explicit-mass substitution.

    Args:
        formal_profile: Synthetic application support.
        atom: Product nucleus whose stoichiometry differs from the reactant.
    """
    request = dissociation(atom=atom, coefficient=1 if atom == "H" else 2)

    proposal = propose(request, reaction_profile(formal_profile))

    assert proposal.plan is None
    assert proposal.report is not None
    assert proposal.report.status == "violated"
    assert any(item.code == "reaction_balance" for item in proposal.report.diagnostics)


def test_reaction_requires_charge_conservation(
    formal_profile: CapabilityCatalog,
) -> None:
    """Reject ionization when the requested reaction omits the electron reservoir.

    Args:
        formal_profile: Synthetic application support.
    """
    original = dissociation()
    neutral = original.molecules[0]
    ion = Molecule(
        atoms=neutral.geometry.atoms,
        state=ElectronicState(charge=1, multiplicity=2),
    )
    request = ScientificRequest(
        molecules=(neutral, molecule("atom", ion)),
        goals=(
            *original.goals[:-1],
            ExpressionGoal(
                id="ionization",
                terms=(
                    GoalTerm(goal="molecular", coefficient=-1),
                    GoalTerm(goal="atomic", coefficient=1),
                ),
                quantity=QuantityType(meaning="reaction_energy", unit="hartree"),
            ),
        ),
    )

    proposal = propose(request, reaction_profile(formal_profile))

    assert proposal.plan is None
    assert proposal.report is not None
    assert proposal.report.status == "violated"
    assert any(item.code == "reaction_charge" for item in proposal.report.diagnostics)


def test_reaction_rejects_a_computational_treatment_used_on_only_one_side(
    formal_profile: CapabilityCatalog,
) -> None:
    """Reject atom-balanced algebra whose participants use inconsistent core choices.

    Args:
        formal_profile: Synthetic application support.
    """
    original = dissociation()
    first, second, expression = original.goals
    assert isinstance(second, CalculationGoal)
    changed = CalculationGoal(
        id=second.id,
        driver=second.driver,
        geometry=second.geometry,
        models=(
            Model(method="scf", basis="sto-3g", reference="uhf", frozen_core=True),
        ),
    )
    request = ScientificRequest(
        molecules=original.molecules, goals=(first, changed, expression)
    )

    proposal = propose(request, reaction_profile(formal_profile))

    assert proposal.plan is None
    assert proposal.report is not None
    assert proposal.report.status == "violated"
    assert any(
        item.code == "reaction_model_balance" for item in proposal.report.diagnostics
    )


def test_nested_composite_reaction_balances_every_treatment(
    formal_profile: CapabilityCatalog,
) -> None:
    """Check two complete reaction channels after expanding nested energy formulas.

    Args:
        formal_profile: Synthetic application support.
    """
    original = dissociation()
    first, second, _ = original.goals
    assert isinstance(first, CalculationGoal)
    assert isinstance(second, CalculationGoal)
    request = ScientificRequest(
        molecules=original.molecules,
        goals=(
            first,
            second,
            CalculationGoal(
                id="molecular_frozen",
                driver="energy",
                geometry="h2",
                models=(
                    Model(
                        method="scf", basis="sto-3g", reference="rhf", frozen_core=True
                    ),
                ),
            ),
            CalculationGoal(
                id="atomic_frozen",
                driver="energy",
                geometry="atom",
                models=(
                    Model(
                        method="scf", basis="sto-3g", reference="uhf", frozen_core=True
                    ),
                ),
            ),
            ExpressionGoal(
                id="molecular_composite",
                terms=(
                    GoalTerm(goal="molecular", coefficient=2),
                    GoalTerm(goal="molecular_frozen", coefficient=-1),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            ),
            ExpressionGoal(
                id="atomic_composite",
                terms=(
                    GoalTerm(goal="atomic", coefficient=2),
                    GoalTerm(goal="atomic_frozen", coefficient=-1),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            ),
            ExpressionGoal(
                id="composite_reaction",
                terms=(
                    GoalTerm(goal="molecular_composite", coefficient=-1),
                    GoalTerm(goal="atomic_composite", coefficient=2),
                ),
                quantity=QuantityType(meaning="reaction_energy", unit="hartree"),
            ),
        ),
    )

    proposal = propose(request, reaction_profile(formal_profile))

    assert proposal.status == "constructed"
    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert len(proposal.report.coverage) == 7
    # Relationship-only checking must also detect the inconsistent treatment
    # rather than accepting an internally consistent algebraic formula.
    altered_steps = tuple(
        Calculation(
            id=step.id,
            driver=step.driver,
            geometry=step.geometry,
            model=Model(method="scf", basis="sto-3g", reference="uhf"),
            satisfies=step.satisfies,
        )
        if isinstance(step, Calculation) and step.id == "atomic_frozen"
        else step
        for step in proposal.plan.steps
    )
    altered = Plan(
        molecules=proposal.plan.molecules,
        steps=altered_steps,
        requirements=proposal.plan.requirements,
    )
    report = verify(altered)
    assert report.status == "violated"
    assert any(item.code == "reaction_model_balance" for item in report.diagnostics)


def test_reaction_goals_compose_without_a_protocol_catalogue(
    formal_profile: CapabilityCatalog,
) -> None:
    """Expand independently supplied species and retain mandatory reaction coverage.

    Args:
        formal_profile: Synthetic application support.
    """
    original = dissociation()
    molecular, atomic, _ = original.goals
    assert isinstance(molecular, CalculationGoal)
    assert isinstance(atomic, CalculationGoal)
    expansion = reaction_expansion(
        ReactionStudy(
            id="dissociate",
            participants=(
                ReactionParticipant(
                    id="H2", geometry="h2", coefficient=-1, models=molecular.models
                ),
                ReactionParticipant(
                    id="H", geometry="atom", coefficient=2, models=atomic.models
                ),
            ),
        )
    )
    request = ScientificRequest(
        molecules=original.molecules,
        goals=expansion.goals,
    )

    proposal = propose(request, reaction_profile(formal_profile))

    assert expansion.target == "dissociate:reaction"
    assert [goal.id for goal in expansion.goals] == [
        "dissociate:energy:H2",
        "dissociate:energy:H",
        "dissociate:reaction",
    ]
    assert (
        ReactionExpansion.model_validate_json(expansion.model_dump_json()) == expansion
    )
    assert proposal.status == "constructed"
    assert proposal.report is not None
    assert [item.goal for item in proposal.report.coverage] == [
        goal.id for goal in expansion.goals
    ]


@pytest.mark.parametrize("coefficients", [(0, 1), (1, 1), (-1, -2)])
def test_reaction_expansion_requires_both_nonzero_sides(
    coefficients: tuple[int, int],
) -> None:
    """Reject one-sided and zero-coefficient expansions before generating goals.

    Args:
        coefficients: Invalid consumed/produced coefficient pair.
    """
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    study = ReactionStudy(
        id="bad",
        participants=tuple(
            ReactionParticipant(
                id=f"s{index}",
                geometry=f"s{index}",
                coefficient=weight,
                models=(model,),
            )
            for index, weight in enumerate(coefficients)
        ),
    )

    with pytest.raises(ValueError, match="nonzero consumed and produced"):
        reaction_expansion(study)


@pytest.mark.parametrize("water_coefficient", [1, 2])
def test_multielement_reaction_checks_each_nuclear_count(
    formal_profile: CapabilityCatalog, water_coefficient: int
) -> None:
    """Accept 2 H2 + O2 -> 2 H2O and reject a single produced water molecule.

    Args:
        formal_profile: Synthetic application support.
        water_coefficient: Balanced or deliberately deficient water count.
    """
    hydrogen = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .75\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    oxygen = Molecule.from_xyz(
        "2\nO2\nO 0 0 0\nO 0 0 1.2\n",
        state=ElectronicState(charge=0, multiplicity=3),
    )
    water = Molecule.from_xyz(
        "3\nH2O\nO 0 0 0\nH .75 0 .6\nH -.75 0 .6\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    closed = Model(method="scf", basis="sto-3g", reference="rhf")
    open_shell = Model(method="scf", basis="sto-3g", reference="uhf")
    expansion = reaction_expansion(
        ReactionStudy(
            id="water",
            participants=(
                ReactionParticipant(
                    id="H2", geometry="h2", coefficient=-2, models=(closed,)
                ),
                ReactionParticipant(
                    id="O2", geometry="o2", coefficient=-1, models=(open_shell,)
                ),
                ReactionParticipant(
                    id="H2O",
                    geometry="h2o",
                    coefficient=water_coefficient,
                    models=(closed,),
                ),
            ),
        )
    )
    request = ScientificRequest(
        molecules=(
            molecule("h2", hydrogen),
            molecule("o2", oxygen),
            molecule("h2o", water),
        ),
        goals=expansion.goals,
    )
    hydrogen_profile = reaction_profile(formal_profile)
    catalog = CapabilityCatalog(
        id="multielement-fixture",
        evidence=hydrogen_profile.evidence,
        methods=hydrogen_profile.methods,
        bases=(
            BasisCapability(
                name="sto-3g",
                status="supported",
                elements=("H", "O"),
                functions=(
                    BasisFunctions(element="H", spherical=1, cartesian=1),
                    BasisFunctions(element="O", spherical=5, cartesian=5),
                ),
                evidence=("fixture",),
            ),
        ),
    )

    proposal = propose(request, catalog)

    if water_coefficient == 2:
        assert proposal.status == "constructed"
        assert proposal.report is not None
        assert proposal.report.request_complete
    else:
        assert proposal.plan is None
        assert proposal.report is not None
        assert proposal.report.status == "violated"
        issue = next(
            item
            for item in proposal.report.diagnostics
            if item.code == "reaction_balance"
        )
        assert "H(isotope=0,mass=None): -2" in issue.message
        assert "O(isotope=0,mass=None): -1" in issue.message


def test_reaction_after_optimization_composes_in_independent_cases(
    formal_profile: CapabilityCatalog,
) -> None:
    """Preserve future-geometry reaction sources and separate finite-case histories.

    Args:
        formal_profile: Synthetic application support.
    """
    original = dissociation()
    molecular, atomic, _ = original.goals
    assert isinstance(molecular, CalculationGoal)
    assert isinstance(atomic, CalculationGoal)
    expansion = reaction_expansion(
        ReactionStudy(
            id="after_opt",
            participants=(
                ReactionParticipant(
                    id="H2", geometry="opt", coefficient=-1, models=molecular.models
                ),
                ReactionParticipant(
                    id="H", geometry="atom", coefficient=2, models=atomic.models
                ),
            ),
        )
    )
    template = ScientificRequest(
        molecules=original.molecules,
        goals=(
            CalculationGoal(
                id="opt", driver="optimize", geometry="h2", models=molecular.models
            ),
            *expansion.goals,
        ),
    )
    request = finite_study(
        template,
        (
            StudyCase(id="first", molecules=original.molecules),
            StudyCase(id="second", molecules=original.molecules),
        ),
    )

    proposal = propose(request, reaction_profile(formal_profile))

    assert proposal.status == "constructed"
    assert proposal.plan is not None
    assert proposal.report is not None
    assert proposal.report.request_complete
    assert len(proposal.report.coverage) == 8
    sources = {
        step.geometry
        for step in proposal.plan.steps
        if isinstance(step, Calculation) and step.id.endswith(":energy:H2")
    }
    assert sources == {"first:opt", "second:opt"}


@pytest.mark.parametrize("duplicate", [False, True])
def test_reaction_expansion_rejects_duplicate_species_and_expansion_overflow(
    duplicate: bool,
) -> None:
    """Refuse ambiguous species IDs and enforce the explicit expansion bound.

    Args:
        duplicate: Repeat a species name instead of exceeding the species bound.
    """
    model = Model(method="scf", basis="sto-3g", reference="rhf")
    specification = ReactionStudy(
        id="bounded",
        max_species=2,
        participants=tuple(
            ReactionParticipant(
                id="same" if duplicate else f"s{index}",
                geometry=f"s{index}",
                coefficient=-1 if index == 0 else 1,
                models=(model,),
            )
            for index in range(2 if duplicate else 3)
        ),
    )

    with pytest.raises(ValueError, match="unique" if duplicate else "max_species"):
        reaction_expansion(specification)
