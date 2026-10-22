"""Compose closed-reaction energies from explicitly requested species calculations."""

from typing import Literal

from pydantic import Field

from psi4_parser.formal._record import Record
from psi4_parser.formal.intent import (
    CalculationGoal,
    ExpressionGoal,
    Goal,
    GoalTerm,
    ProductGoal,
)
from psi4_parser.formal.products import THERMAL_TOTALS
from psi4_parser.formal.science import (
    Model,
    QuantityType,
    Rational,
    VibrationalAnalysis,
)

type ReactionQuantity = Literal[
    "electronic_energy",
    "zero_k_enthalpy",
    "thermal_energy",
    "enthalpy",
    "gibbs_free_energy",
]
"""Molecular energy meanings supported by closed-reaction expansion."""


class ReactionThermochemistry(Record):
    """Specify a species' frequency analysis and optional hybrid correction model.

    With no separate models, one frequency call supplies the electronic energy
    and native thermal total. Supplying models requests a separate electronic
    energy with the participant's models and a frequency correction with these
    models, both at the participant's geometry.
    """

    analysis: VibrationalAnalysis = Field(
        description="Explicit conditions, rotational symmetry, and projection choices."
    )
    models: tuple[Model, ...] = Field(
        default=(),
        description="Permitted correction models in preference order; empty uses "
        "the participant's models for one native frequency total.",
    )
    derivative_routes: tuple[
        Literal["automatic", "analytic", "finite_difference"], ...
    ] = Field(
        default=("automatic",),
        min_length=1,
        description="Permitted frequency derivative routes in preference order.",
    )


class ReactionParticipant(Record):
    """Specify one species' electronic model, thermal analysis, and coefficient."""

    id: str = Field(
        min_length=1, description="Unique species name within this reaction expansion."
    )
    geometry: str = Field(
        min_length=1,
        description="Input or preceding optimization geometry for this species.",
    )
    coefficient: int | Rational = Field(
        description="Nonzero exact coefficient; negative consumes, positive produces."
    )
    models: tuple[Model, ...] = Field(
        min_length=1,
        description="Permitted models for this species, in preference order.",
    )
    thermochemistry: ReactionThermochemistry | None = Field(
        default=None,
        description="Species-specific frequency analysis for a thermal reaction; "
        "required for thermal quantities and omitted for electronic reactions.",
    )


class ReactionStudy(Record):
    """Describe a closed reaction whose species energies remain symbolic."""

    id: str = Field(min_length=1, description="Prefix for generated reaction goal IDs.")
    participants: tuple[ReactionParticipant, ...] = Field(
        min_length=2,
        description="Consumed and produced species in the supplied order.",
    )
    quantity: ReactionQuantity = Field(
        default="electronic_energy",
        description="Molecular energy meaning combined into the reaction quantity.",
    )
    max_species: int = Field(
        default=1000, ge=2, description="Maximum number of species to expand."
    )


class ReactionExpansion(Record):
    """Compose species calculations and their exact reaction-energy expression."""

    goals: tuple[Goal, ...] = Field(
        description="Species calculations and thermal products followed by "
        "the exact reaction expression."
    )
    target: str = Field(description="Goal ID of the symbolic reaction energy.")


def _species_goals(
    specification: ReactionStudy, participant: ReactionParticipant
) -> tuple[Goal, ...]:
    prefix = specification.id
    name = participant.id
    quantity = specification.quantity
    energy = CalculationGoal(
        id=f"{prefix}:energy:{name}",
        driver="energy",
        geometry=participant.geometry,
        models=participant.models,
        reason=f"Species {name} in reaction {prefix}",
    )
    thermal = participant.thermochemistry
    if quantity == "electronic_energy":
        if thermal is not None:
            raise ValueError("Electronic reactions must omit thermochemistry")
        return (energy,)
    if thermal is None:
        raise ValueError("Every thermal reaction species needs thermochemistry")
    frequency = CalculationGoal(
        id=f"{prefix}:frequency:{name}",
        driver="frequency",
        geometry=participant.geometry,
        models=thermal.models or participant.models,
        analysis=thermal.analysis,
        derivative_routes=thermal.derivative_routes,
        reason=f"Thermal analysis of {name} in reaction {prefix}",
    )
    total = f"{prefix}:total:{name}"
    if not thermal.models:
        return (
            frequency,
            ProductGoal(
                id=total,
                calculation=frequency.id,
                name=quantity,
                reason=f"Native {quantity} of {name} in reaction {prefix}",
            ),
        )
    correction = ProductGoal(
        id=f"{prefix}:correction:{name}",
        calculation=frequency.id,
        name=THERMAL_TOTALS[quantity],
        reason=f"Specified thermal correction of {name} in reaction {prefix}",
    )
    return (
        energy,
        frequency,
        correction,
        ExpressionGoal(
            id=total,
            terms=(
                GoalTerm(goal=energy.id, coefficient=1),
                GoalTerm(goal=correction.id, coefficient=1),
            ),
            quantity=QuantityType(meaning=quantity, unit="hartree"),
            reason=f"Electronic energy plus thermal correction of {name} in {prefix}",
        ),
    )


def reaction_expansion(specification: ReactionStudy) -> ReactionExpansion:
    """Require species energies and a checked product-minus-reactant expression.

    Compose the returned goals with molecular inputs and optional preceding
    optimizations in a ScientificRequest. Verification independently checks real
    nuclei, explicit isotope and mass choices, charge, and each computational
    treatment. Species-specific SCF references and rotational symmetry numbers
    may differ. Thermal reactions require one common temperature, pressure,
    treatment, and projection choices. Each species uses one native frequency
    total, or an explicitly chosen electronic model plus frequency correction.
    External particle reservoirs require a separate contract.

    Args:
        specification: Ordered species, nonzero exact coefficients, and allowed models.

    Returns:
        Primitive calculation and expression goals for the independent request.

    Raises:
        ValueError: Species repeat, coefficients omit a reaction side, the bound
            is exceeded, or thermal configuration disagrees with the quantity.
    """
    specification = ReactionStudy.model_validate(specification)
    species = specification.participants
    if len(species) > specification.max_species:
        raise ValueError("Reaction exceeds max_species")
    if len({item.id for item in species}) != len(species):
        raise ValueError("Reaction species IDs must be unique")
    coefficients = tuple(
        item.coefficient.numerator
        if isinstance(item.coefficient, Rational)
        else item.coefficient
        for item in species
    )
    if (
        any(value == 0 for value in coefficients)
        or not any(value < 0 for value in coefficients)
        or not any(value > 0 for value in coefficients)
    ):
        raise ValueError("Supply nonzero consumed and produced species coefficients")
    species_goals = tuple(_species_goals(specification, item) for item in species)
    target = f"{specification.id}:reaction"
    expression = ExpressionGoal(
        id=target,
        terms=tuple(
            GoalTerm(goal=goals[-1].id, coefficient=item.coefficient)
            for goals, item in zip(species_goals, species, strict=True)
        ),
        quantity=QuantityType(
            meaning="reaction_energy"
            if specification.quantity == "electronic_energy"
            else f"reaction_{specification.quantity}",
            unit="hartree",
        ),
        reason=f"Closed {specification.quantity} reaction {specification.id}",
    )
    return ReactionExpansion(
        goals=(*(goal for goals in species_goals for goal in goals), expression),
        target=target,
    )
