"""Require basis-point calculations and an explicit symbolic extrapolation recipe."""

from fractions import Fraction
from itertools import repeat
from math import prod
from typing import Literal

from pydantic import Field

from psi4_parser.formal._exponential_math import exponential_weights
from psi4_parser.formal._record import Record
from psi4_parser.formal.extrapolation_models import (
    ExponentialExtrapolation,
    ExtrapolationPoint,
    InversePowerExtrapolation,
)
from psi4_parser.formal.intent import CalculationGoal, ExpressionGoal, Goal, GoalTerm
from psi4_parser.formal.science import Model, QuantityType, Rational


class BasisCorrectionPoint(Record):
    """Choose a target and reference treatment at one orbital-basis cardinal.

    Each point is the target electronic energy minus the reference electronic
    energy. HF subtraction defines a correlation estimate; other explicitly
    chosen methods define a method correction.
    """

    basis: str = Field(min_length=1, pattern=r"\S", description="Common orbital basis.")
    cardinal: int = Field(
        ge=1, le=32, description="Basis-series cardinal number, from 1 through 32."
    )
    models: tuple[Model, ...] = Field(
        min_length=1, description="Permitted target models in preference order."
    )
    reference_models: tuple[Model, ...] = Field(
        min_length=1,
        description="Permitted subtracted reference models in preference order.",
    )


class ExtrapolationStudy(Record):
    """Request an inverse-power basis-limit correction at one fixed geometry."""

    id: str = Field(min_length=1, description="Prefix for generated goal identities.")
    geometry: str = Field(
        min_length=1, description="Input or preceding optimization geometry goal."
    )
    family: str = Field(
        min_length=1, pattern=r"\S", description="Required common orbital-basis family."
    )
    low: BasisCorrectionPoint = Field(
        description="Lower-cardinal target/reference pair."
    )
    high: BasisCorrectionPoint = Field(
        description="Higher-cardinal target/reference pair."
    )
    power: int = Field(
        ge=1, le=16, description="Explicit positive integer inverse-power exponent."
    )
    reuse_group: str | None = Field(
        default=None,
        min_length=1,
        pattern=r"\S",
        description="Permission to share matching point calls with calculations "
        "in this same group; null requires separate calls.",
    )


class ExtrapolationExpansion(Record):
    """Retain basis-point work and its explicitly requested basis-limit recipe."""

    goals: tuple[Goal, ...] = Field(
        description="Energy calls, optional point corrections, and the limit estimate."
    )
    target: str = Field(description="Goal ID of the extrapolated energy or correction.")


class BasisEnergyPoint(Record):
    """Choose permitted reference models at one evidenced orbital-basis cardinal."""

    basis: str = Field(
        min_length=1, pattern=r"\S", description="Uniform orbital basis."
    )
    cardinal: int = Field(
        ge=1, le=32, description="Basis-series cardinal from 1 through 32."
    )
    models: tuple[Model, ...] = Field(
        min_length=1, description="Permitted HF/SCF energy models in preference order."
    )


class ReferenceExtrapolationStudy(Record):
    """Require two HF reference energies and a certified exponential limit estimate."""

    id: str = Field(min_length=1, description="Prefix for generated goal identities.")
    geometry: str = Field(
        min_length=1, description="Input or optimization geometry ID."
    )
    family: str = Field(
        min_length=1, pattern=r"\S", description="Common orbital-basis family."
    )
    low: BasisEnergyPoint = Field(description="Lower-cardinal reference point.")
    high: BasisEnergyPoint = Field(description="Higher-cardinal reference point.")
    alpha: Rational = Field(
        description="Explicit positive decay constant at most 32; reduced numerator "
        "and denominator each use at most 256 bits."
    )
    shape: Literal["cardinal", "sqrt_cardinal"] = Field(
        default="cardinal", description="Decay coordinate: X or sqrt(X)."
    )
    coefficient_digits: int = Field(
        default=15,
        ge=6,
        le=30,
        description="Absolute rational weight error at most 10**(-digits); "
        "6 through 30 decimal digits, with an exact sum of one.",
    )
    reuse_group: str | None = Field(
        default=None,
        min_length=1,
        pattern=r"\S",
        description="Permission to share matching calls in this group; "
        "null requires separate calls.",
    )


def _reference_expansion(
    specification: ReferenceExtrapolationStudy,
) -> ExtrapolationExpansion:
    calls: list[CalculationGoal] = []
    for label, point in (("low", specification.low), ("high", specification.high)):
        if any(
            model.basis.strip().casefold() != point.basis.strip().casefold()
            for model in point.models
        ):
            raise ValueError("Every point model must use its declared orbital basis")
        calls.append(
            CalculationGoal(
                id=f"{specification.id}:{label}",
                driver="energy",
                geometry=specification.geometry,
                models=point.models,
                reuse_group=specification.reuse_group,
                reason=f"Reference energy at {point.basis}",
            )
        )
    recipe = ExponentialExtrapolation(
        family=specification.family,
        low=ExtrapolationPoint(
            result=calls[0].id,
            basis=specification.low.basis,
            cardinal=specification.low.cardinal,
        ),
        high=ExtrapolationPoint(
            result=calls[1].id,
            basis=specification.high.basis,
            cardinal=specification.high.cardinal,
        ),
        alpha=specification.alpha,
        shape=specification.shape,
        coefficient_digits=specification.coefficient_digits,
    )
    goal = ExpressionGoal(
        id=f"{specification.id}:basis_limit",
        terms=tuple(
            GoalTerm(
                goal=call.id,
                coefficient=Rational(
                    numerator=weight.numerator, denominator=weight.denominator
                ),
            )
            for call, weight in zip(calls, exponential_weights(recipe), strict=True)
        ),
        quantity=QuantityType(meaning="basis_limit_reference_energy", unit="hartree"),
        extrapolation=recipe,
        reason=f"Exponential reference estimate for {specification.id}",
    )
    return ExtrapolationExpansion(goals=(*calls, goal), target=goal.id)


def _point_goals(
    specification: ExtrapolationStudy, point: BasisCorrectionPoint, label: str
) -> tuple[Goal, ...]:
    if any(
        model.basis.strip().casefold() != point.basis.strip().casefold()
        for model in (*point.models, *point.reference_models)
    ):
        raise ValueError("Every point model must use its declared orbital basis")
    prefix = f"{specification.id}:{label}"
    return (
        CalculationGoal(
            id=f"{prefix}:target",
            driver="energy",
            geometry=specification.geometry,
            models=point.models,
            reuse_group=specification.reuse_group,
            reason=f"Target treatment at {point.basis}",
        ),
        CalculationGoal(
            id=f"{prefix}:reference",
            driver="energy",
            geometry=specification.geometry,
            models=point.reference_models,
            reuse_group=specification.reuse_group,
            reason=f"Subtracted reference treatment at {point.basis}",
        ),
        ExpressionGoal(
            id=f"{prefix}:correction",
            terms=(
                GoalTerm(goal=f"{prefix}:target", coefficient=1),
                GoalTerm(goal=f"{prefix}:reference", coefficient=-1),
            ),
            quantity=QuantityType(meaning="energy_difference", unit="hartree"),
            reason=f"Target minus reference correction at {point.basis}",
        ),
    )


def extrapolation_expansion(
    specification: ExtrapolationStudy | ReferenceExtrapolationStudy,
) -> ExtrapolationExpansion:
    """Require consistent basis-point work and its independently checked limit model.

    Compose returned goals with molecular inputs and preceding optimizations.
    The independent verifier checks basis-family/cardinal evidence, geometry,
    target/reference treatments, and formula weights. The chosen convergence
    model is an explicit scientific assumption. Values remain symbolic.

    Args:
        specification: Inverse-power correction or exponential HF reference study,
            with fixed geometry, permitted models, basis family, and decay choices.

    Returns:
        Inverse-power studies yield four calls, two differences, and a correction.
        Exponential studies yield two calls and a reference-energy estimate with
        certified rational coefficient error. Physical convergence is assumed.

    Raises:
        ValueError: Basis labels disagree, or points do not define an ordered pair.
    """  # noqa: DOC502 - Recipe validation rejects unordered point declarations.
    if isinstance(specification, ReferenceExtrapolationStudy):
        return _reference_expansion(
            ReferenceExtrapolationStudy.model_validate(specification)
        )
    specification = ExtrapolationStudy.model_validate(specification)
    low = _point_goals(specification, specification.low, "low")
    high = _point_goals(specification, specification.high, "high")
    recipe = InversePowerExtrapolation(
        family=specification.family,
        power=specification.power,
        low=ExtrapolationPoint(
            result=low[-1].id,
            basis=specification.low.basis,
            cardinal=specification.low.cardinal,
        ),
        high=ExtrapolationPoint(
            result=high[-1].id,
            basis=specification.high.basis,
            cardinal=specification.high.cardinal,
        ),
    )
    lower = prod(repeat(specification.low.cardinal, specification.power))
    higher = prod(repeat(specification.high.cardinal, specification.power))
    coefficients = (Fraction(-lower, higher - lower), Fraction(higher, higher - lower))
    target = f"{specification.id}:basis_limit"
    goal = ExpressionGoal(
        id=target,
        terms=tuple(
            GoalTerm(
                goal=point[-1].id,
                coefficient=Rational(
                    numerator=coefficient.numerator, denominator=coefficient.denominator
                ),
            )
            for point, coefficient in zip((low, high), coefficients, strict=True)
        ),
        quantity=QuantityType(meaning="basis_limit_correction", unit="hartree"),
        extrapolation=recipe,
        reason=f"Inverse-power correction estimate for {specification.id}",
    )
    return ExtrapolationExpansion(goals=(*low, *high, goal), target=target)
