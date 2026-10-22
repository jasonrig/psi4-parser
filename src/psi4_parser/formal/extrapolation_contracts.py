"""Check source treatments and basis-limit coefficients independently."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import repeat
from math import prod

from psi4_parser.formal._exponential_math import exponential_coefficient_bounds
from psi4_parser.formal.algebra import Form
from psi4_parser.formal.extrapolation_models import (
    ExponentialExtrapolation,
    ExtrapolationPoint,
    InversePowerExtrapolation,
)
from psi4_parser.formal.models import Calculation, Combination, Diagnostic, Step
from psi4_parser.formal.science import ExpectedQuantity, QuantityType

_POINT_SOURCES = 2


@dataclass(frozen=True)
class _Pair:
    target: Calculation
    reference: Calculation


@dataclass(frozen=True)
class _Sources:
    steps: dict[str, Step]
    forms: dict[str, Form]
    quantities: dict[str, ExpectedQuantity]


def _issue(path: tuple[str | int, ...], code: str, message: str) -> Diagnostic:
    return Diagnostic(path=path, code=code, message=message, status="violated")


def _point_pair(
    point: ExtrapolationPoint,
    steps: dict[str, Step],
    forms: dict[str, Form],
    quantities: dict[str, ExpectedQuantity],
) -> _Pair | None:
    form = forms[point.result]
    if len(form) != _POINT_SOURCES or sorted(form.values()) != [-1, 1]:
        return None
    sources = {weight: steps[name] for name, weight in form.items()}
    target, reference = sources[Fraction(1)], sources[Fraction(-1)]
    if not isinstance(target, Calculation) or not isinstance(reference, Calculation):
        return None
    if any(
        source.driver != "energy"
        or quantities[source.id].quantity
        != QuantityType(meaning="electronic_energy", unit="hartree")
        or source.model.basis.strip().casefold() != point.basis.strip().casefold()
        or source.model.basis_assignments
        for source in (target, reference)
    ):
        return None
    return _Pair(target, reference)


def _point_context(pair: _Pair) -> bool:
    fields = {
        "reference",
        "frozen_core",
        "puream",
        "ecps",
        "environment",
        "external_potential",
        "electric_field",
        "electronic_target",
        "tdscf",
    }
    return (
        pair.target.geometry == pair.reference.geometry
        and pair.target.model.model_dump_json(include=fields)
        == pair.reference.model.model_dump_json(include=fields)
        and pair.target.model.identity != pair.reference.model.identity
    )


def extrapolation_issues(
    step: Combination,
    steps: dict[str, Step],
    forms: dict[str, Form],
    quantities: dict[str, ExpectedQuantity],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    """Check a basis-limit model without assuming the requested formula is right.

    Returns:
        Located quantity, source, treatment, or exact formula findings.
    """
    recipe = step.extrapolation
    if recipe is None:
        return (
            _issue(
                path, "extrapolation_recipe", "Supply an explicit extrapolation recipe."
            ),
        )
    if isinstance(recipe, ExponentialExtrapolation):
        return _exponential_issues(
            step, recipe, _Sources(steps, forms, quantities), path
        )
    return _inverse_power_issues(step, recipe, _Sources(steps, forms, quantities), path)


def _inverse_power_issues(
    step: Combination,
    recipe: InversePowerExtrapolation,
    sources: _Sources,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    steps, forms, quantities = sources.steps, sources.forms, sources.quantities
    if quantities[step.id].quantity != QuantityType(
        meaning="basis_limit_correction", unit="hartree"
    ):
        return (
            _issue(
                path,
                "extrapolation_quantity",
                "An inverse-power correction requires a real scalar "
                "basis_limit_correction in hartree with no oriented frame.",
            ),
        )
    low = _point_pair(recipe.low, steps, forms, quantities)
    high = _point_pair(recipe.high, steps, forms, quantities)
    if low is None or high is None:
        return (
            _issue(
                path,
                "extrapolation_sources",
                "Each point must be one target energy minus one reference energy "
                "at its declared uniform orbital basis.",
            ),
        )
    if not _point_context(low) or not _point_context(high):
        return (
            _issue(
                path,
                "extrapolation_context",
                "Each target/reference pair needs the same geometry, state, core, "
                "angular representation, and environment, with distinct treatments.",
            ),
        )
    if (
        low.target.geometry != high.target.geometry
        or low.target.model.basis_treatment_identity
        != high.target.model.basis_treatment_identity
        or low.reference.model.basis_treatment_identity
        != high.reference.model.basis_treatment_identity
    ):
        return (
            _issue(
                path,
                "extrapolation_treatment",
                "Both points must keep geometry and target/reference treatments "
                "fixed while varying only evidence-backed basis names.",
            ),
        )
    lower = prod(repeat(recipe.low.cardinal, recipe.power))
    higher = prod(repeat(recipe.high.cardinal, recipe.power))
    ratio = Fraction(lower, higher - lower)
    expected: Form = dict(forms[recipe.high.result])
    # E_inf = E_high + (E_high - E_low) / ((X_high/X_low)**power - 1).
    for source, weight in ((recipe.high, ratio), (recipe.low, -ratio)):
        for leaf, coefficient in forms[source.result].items():
            expected[leaf] = expected.get(leaf, Fraction(0)) + weight * coefficient
    expected = {leaf: weight for leaf, weight in expected.items() if weight}
    return (
        (
            _issue(
                path,
                "extrapolation_formula",
                "Formula coefficients do not solve the requested two-point "
                "inverse-power correction model.",
            ),
        )
        if forms[step.id] != expected
        else ()
    )


def _reference_source(
    point: ExtrapolationPoint,
    steps: dict[str, Step],
    forms: dict[str, Form],
    quantities: dict[str, ExpectedQuantity],
) -> Calculation | None:
    form = forms[point.result]
    if len(form) != 1 or next(iter(form.values())) != 1:
        return None
    source = steps[next(iter(form))]
    if (
        not isinstance(source, Calculation)
        or source.driver != "energy"
        or source.model.method.strip().casefold() not in {"hf", "scf"}
        or source.model.tdscf is not None
        or source.sapt is not None
        or source.model.basis_assignments
        or source.model.basis.strip().casefold() != point.basis.strip().casefold()
        or quantities[source.id].quantity
        != QuantityType(meaning="electronic_energy", unit="hartree")
    ):
        return None
    return source


def _exponential_issues(
    step: Combination,
    recipe: ExponentialExtrapolation,
    sources: _Sources,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    steps, forms, quantities = sources.steps, sources.forms, sources.quantities
    if quantities[step.id].quantity != QuantityType(
        meaning="basis_limit_reference_energy", unit="hartree"
    ):
        return (
            _issue(
                path,
                "extrapolation_quantity",
                "An exponential HF estimate "
                "requires scalar basis_limit_reference_energy in hartree.",
            ),
        )
    low = _reference_source(recipe.low, steps, forms, quantities)
    high = _reference_source(recipe.high, steps, forms, quantities)
    if low is None or high is None:
        return (
            _issue(
                path,
                "exponential_reference_source",
                "Each point requires "
                "one HF/SCF electronic energy at its declared uniform basis.",
            ),
        )
    if (
        low.geometry != high.geometry
        or low.model.basis_treatment_identity != high.model.basis_treatment_identity
    ):
        return (
            _issue(
                path,
                "extrapolation_treatment",
                "Exponential points must "
                "retain one geometry and reference treatment across bases.",
            ),
        )
    form = forms[step.id]
    if set(form) - {low.id, high.id} or sum(form.values(), Fraction(0)) != 1:
        return (
            _issue(
                path,
                "extrapolation_formula",
                "Use only the two declared "
                "reference points with weights summing exactly to one.",
            ),
        )
    lower, upper = exponential_coefficient_bounds(recipe)
    actual = form.get(low.id, Fraction(0))
    tolerance = Fraction(1, prod(repeat(10, recipe.coefficient_digits)))
    if actual - tolerance <= lower <= upper <= actual + tolerance:
        return ()
    outside = actual < lower - tolerance or actual > upper + tolerance
    return (
        Diagnostic(
            path=(*path[:-1], "terms"),
            code="exponential_coefficient_bound",
            status="violated" if outside else "unknown",
            message="Rational intervals could not certify exponential weights within "
            f"absolute coefficient error 1e-{recipe.coefficient_digits}.",
        ),
    )
