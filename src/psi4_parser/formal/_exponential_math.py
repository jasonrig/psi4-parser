"""Construct decimal weights and certify them independently with rational bounds."""

from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext
from fractions import Fraction
from math import isqrt

from psi4_parser.formal.extrapolation_models import ExponentialExtrapolation

# Bounded alpha has magnitude at least 2**-256. These outward grids leave ample
# precision for inverse growth factors and the maximum 30-digit weight bound.
_GRID = 10**320
_SQRT_GRID = 10**160
_TERMS = 64


def _outward(lower: Fraction, upper: Fraction) -> tuple[Fraction, Fraction]:
    lower_integer = lower.numerator * _GRID // lower.denominator
    upper_integer = -(-upper.numerator * _GRID // upper.denominator)
    return Fraction(lower_integer, _GRID), Fraction(upper_integer, _GRID)


def _expm1_bounds(argument: Fraction) -> tuple[Fraction, Fraction]:
    """Return exp(argument)-1 bounds from positive terms and a geometric tail."""
    halvings = 0
    while argument > 1:
        argument /= 2
        halvings += 1
    lower = upper = Fraction(0)
    term_lower = term_upper = Fraction(1)
    for index in range(1, _TERMS + 1):
        term_lower, term_upper = _outward(
            term_lower * argument / index, term_upper * argument / index
        )
        lower += term_lower
        upper += term_upper
    # For n >= TERMS+1, successive positive terms have ratio <= x/(TERMS+2).
    tail = term_upper * argument / (_TERMS + 1) / (1 - argument / (_TERMS + 2))
    lower, upper = _outward(lower, upper + tail)
    for _ in range(halvings):
        # exp(2x)-1 = 2*(exp(x)-1) + (exp(x)-1)**2, increasing for x >= 0.
        lower, upper = _outward(2 * lower + lower**2, 2 * upper + upper**2)
    return lower, upper


def _sqrt_bounds(cardinal: int) -> tuple[Fraction, Fraction]:
    scaled = cardinal * _SQRT_GRID**2
    root = isqrt(scaled)
    return (
        Fraction(root, _SQRT_GRID),
        Fraction(root if root**2 == scaled else root + 1, _SQRT_GRID),
    )


def exponential_coefficient_bounds(
    recipe: ExponentialExtrapolation,
) -> tuple[Fraction, Fraction]:
    """Return bounds on the exact low-point weight using rational arithmetic only."""
    if recipe.shape == "cardinal":
        delta_lower = delta_upper = Fraction(recipe.high.cardinal - recipe.low.cardinal)
    else:
        low_lower, low_upper = _sqrt_bounds(recipe.low.cardinal)
        high_lower, high_upper = _sqrt_bounds(recipe.high.cardinal)
        delta_lower, delta_upper = high_lower - low_upper, high_upper - low_lower
    growth_lower, _ = _expm1_bounds(recipe.alpha.fraction * delta_lower)
    _, growth_upper = _expm1_bounds(recipe.alpha.fraction * delta_upper)
    return -1 / growth_lower, -1 / growth_upper


def exponential_weights(recipe: ExponentialExtrapolation) -> tuple[Fraction, Fraction]:
    """Return a rounded decimal low weight and an exact complementary high weight."""
    fraction = recipe.alpha.fraction
    magnitude = max(
        len(str(fraction.denominator)) - len(str(fraction.numerator)) + 1, 0
    )
    # Tiny alpha needs extra digits for exp(delta)-1 and its reciprocal. A private
    # context also keeps caller Decimal precision/rounding from changing a plan.
    precision = recipe.coefficient_digits + 2 * magnitude + 40
    with localcontext(Context(prec=precision, rounding=ROUND_HALF_EVEN)):
        alpha = Decimal(fraction.numerator) / Decimal(fraction.denominator)
        low, high = Decimal(recipe.low.cardinal), Decimal(recipe.high.cardinal)
        delta = high - low if recipe.shape == "cardinal" else high.sqrt() - low.sqrt()
        weight = -1 / ((alpha * delta).exp() - 1)
        rounded = weight.quantize(Decimal(1).scaleb(-recipe.coefficient_digits))
        lower = Fraction(rounded)
        return lower, 1 - lower
