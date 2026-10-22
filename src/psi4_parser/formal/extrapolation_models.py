"""Declare basis sequences, correction models, and exponential reference recipes."""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from psi4_parser.formal._record import Record
from psi4_parser.formal.science import Rational

_MAX_ALPHA = 32
_ALPHA_BITS = 256


class BasisSequence(Record):
    """Identify a basis family's cardinal member using supplied capability evidence.

    Family names distinguish augmentation, core/valence, relativistic, and other
    variants. They are evidence labels, not inferred from basis-name spelling.
    """

    family: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Case-insensitive basis-family identity.",
    )
    cardinal: int = Field(
        ge=1, le=32, description="Positive cardinal number, from 1 through 32."
    )

    @property
    def key(self) -> tuple[str, int]:
        """Return the normalized family and cardinal number."""
        return self.family.strip().casefold(), self.cardinal


class ExtrapolationPoint(Record):
    """Bind an earlier scalar energy or correction to its requested basis member."""

    result: str = Field(
        min_length=1, description="Earlier scalar energy or energy-difference ID."
    )
    basis: str = Field(min_length=1, pattern=r"\S", description="Orbital basis name.")
    cardinal: int = Field(
        ge=1, le=32, description="Requested basis cardinal number, from 1 through 32."
    )


class InversePowerExtrapolation(Record):
    """Estimate a correction's basis limit from two explicitly chosen basis points.

    The model is C(X) = C(infinity) + A / X**power. The integer power keeps
    coefficients exact rational numbers. Its physical suitability is an assumption.
    """

    scheme: Literal["inverse_power"] = Field(
        default="inverse_power", description="Two-point inverse-power correction model."
    )
    family: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Required common orbital-basis family from capability evidence.",
    )
    low: ExtrapolationPoint = Field(description="Lower-cardinal correction point.")
    high: ExtrapolationPoint = Field(description="Higher-cardinal correction point.")
    power: int = Field(
        ge=1,
        le=16,
        description="Explicit positive integer exponent, from 1 through 16.",
    )

    @model_validator(mode="after")
    def check_order(self) -> Self:
        """Return two distinct, strictly increasing basis points.

        Raises:
            ValueError: Results or bases repeat, or cardinal numbers do not increase.
        """
        if (
            self.low.result == self.high.result
            or self.low.basis.strip().casefold() == self.high.basis.strip().casefold()
            or self.low.cardinal >= self.high.cardinal
        ):
            raise ValueError("Use distinct results and bases with increasing cardinals")
        return self


class ExponentialExtrapolation(Record):
    """Estimate an HF reference limit with an explicit exponential decay law.

    E(X) = E(infinity) + A exp(-alpha f(X)), where f(X) is X or sqrt(X).
    Rational coefficients approximate this model within 10**(-coefficient_digits)
    in each weight and sum exactly to one. Verification certifies that coefficient
    bound using rational intervals; physical convergence remains an assumption.
    """

    scheme: Literal["exponential"] = Field(
        default="exponential", description="Two-point exponential reference model."
    )
    family: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Common orbital-basis family from capability evidence.",
    )
    low: ExtrapolationPoint = Field(description="Lower-cardinal HF energy point.")
    high: ExtrapolationPoint = Field(description="Higher-cardinal HF energy point.")
    alpha: Rational = Field(
        description="Explicit positive decay constant, at most 32. The reduced "
        "numerator and denominator each use at most 256 bits for bounded arithmetic.",
    )
    shape: Literal["cardinal", "sqrt_cardinal"] = Field(
        default="cardinal", description="Decay coordinate f(X): X or sqrt(X)."
    )
    coefficient_digits: int = Field(
        default=15,
        ge=6,
        le=30,
        description="Absolute error bound 10**(-digits) on each rational weight, "
        "from 6 through 30 decimal digits. Weights must sum exactly to one.",
    )

    @model_validator(mode="after")
    def check_parameters(self) -> Self:
        """Return an ordered pair with a bounded positive decay constant.

        Raises:
            ValueError: Points repeat or do not increase, or alpha is out of range.
        """
        if (
            self.low.result == self.high.result
            or self.low.basis.strip().casefold() == self.high.basis.strip().casefold()
            or self.low.cardinal >= self.high.cardinal
        ):
            raise ValueError("Use distinct results and bases with increasing cardinals")
        alpha = self.alpha.fraction
        if (
            not 0 < alpha <= _MAX_ALPHA
            or max(alpha.numerator.bit_length(), alpha.denominator.bit_length())
            > _ALPHA_BITS
        ):
            raise ValueError(
                "Alpha must be positive, at most 32, with a reduced "
                "numerator and denominator of at most 256 bits"
            )
        return self


type ExtrapolationRecipe = Annotated[
    InversePowerExtrapolation | ExponentialExtrapolation,
    Field(discriminator="scheme"),
]


def translate_extrapolation(
    recipe: ExtrapolationRecipe | None, mapping: dict[str, str]
) -> ExtrapolationRecipe | None:
    """Translate goal or step references while retaining scientific basis choices.

    Returns:
        The mapped recipe, or null when no extrapolation was requested.
    """
    if recipe is None:
        return None
    low = ExtrapolationPoint(
        result=mapping.get(recipe.low.result, recipe.low.result),
        basis=recipe.low.basis,
        cardinal=recipe.low.cardinal,
    )
    high = ExtrapolationPoint(
        result=mapping.get(recipe.high.result, recipe.high.result),
        basis=recipe.high.basis,
        cardinal=recipe.high.cardinal,
    )
    if isinstance(recipe, InversePowerExtrapolation):
        return InversePowerExtrapolation(
            family=recipe.family,
            power=recipe.power,
            low=low,
            high=high,
        )
    return ExponentialExtrapolation(
        family=recipe.family,
        low=low,
        high=high,
        alpha=recipe.alpha,
        shape=recipe.shape,
        coefficient_digits=recipe.coefficient_digits,
    )
