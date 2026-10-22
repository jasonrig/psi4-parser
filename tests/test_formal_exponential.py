"""Check exponential basis-limit estimates independently of requested weights."""

import json
import math
from decimal import ROUND_DOWN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Literal

import pytest
from jsonschema import Draft202012Validator
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BasisCorrectionPoint,
    BasisEnergyPoint,
    Calculation,
    CalculationGoal,
    Combination,
    ElectronicTarget,
    ExponentialExtrapolation,
    ExpressionGoal,
    ExtrapolationStudy,
    GoalTerm,
    Model,
    ProductGoal,
    QuantityType,
    Rational,
    ReferenceExtrapolationStudy,
    ScientificRequest,
    Setting,
    StudyCase,
    TDSCFAnalysis,
    describe_schema,
    export_bundle,
    extrapolation_expansion,
    finite_study,
    load_catalog,
    propose,
    verify,
)
from psi4_parser.formal._record import Record

_JSON = TypeAdapter(JsonValue)


def _edit[T: Record](record: T, path: tuple[str | int, ...], value: JsonValue) -> T:
    document = _JSON.validate_json(record.model_dump_json())
    node = document
    for part in path[:-1]:
        if isinstance(part, int):
            assert isinstance(node, list)
            node = node[part]
        else:
            assert isinstance(node, dict)
            node = node[part]
    last = path[-1]
    if isinstance(last, int):
        assert isinstance(node, list)
        node[last] = value
    else:
        assert isinstance(node, dict)
        node[last] = value
    return type(record).model_validate_json(json.dumps(document))


def _request() -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    declaration = molecule("h2", geometry).model_dump_json()
    source = """{
      "molecules": [MOLECULE], "goals": [
        {"kind":"calculate", "id":"low", "driver":"energy", "geometry":"h2",
         "models":[{"method":"hf", "basis":"cc-pvdz", "reference":"rhf",
                    "settings":[{"name":"scf_type", "value":"PK"}]}]},
        {"kind":"calculate", "id":"high", "driver":"energy", "geometry":"h2",
         "models":[{"method":"hf", "basis":"cc-pvtz", "reference":"rhf",
                    "settings":[{"name":"scf_type", "value":"PK"}]}]},
        {"kind":"expression", "id":"reference_limit",
         "quantity":{"meaning":"basis_limit_reference_energy", "unit":"hartree"},
         "terms":[
           {"goal":"low", "coefficient":{"numerator":-581976706869326,
                                          "denominator":1000000000000000}},
           {"goal":"high", "coefficient":{"numerator":1581976706869326,
                                           "denominator":1000000000000000}}
         ],
         "extrapolation":{"scheme":"exponential", "family":"cc-pvXZ",
           "low":{"result":"low", "basis":"cc-pvdz", "cardinal":2},
           "high":{"result":"high", "basis":"cc-pvtz", "cardinal":3},
           "alpha":{"numerator":1}, "coefficient_digits":15}}
      ]}"""
    return ScientificRequest.model_validate_json(
        source.replace("MOLECULE", declaration)
    )


def test_exponential_reference_uses_certified_rounded_weights() -> None:
    """Accept independently known E(X)=E(infinity)+A exp(-X) weights."""
    proposal = propose(_request())

    assert proposal.status == "constructed"
    assert proposal.report is not None
    assert proposal.report.request_complete


def _expanded(
    *,
    shape: Literal["cardinal", "sqrt_cardinal"] = "cardinal",
    alpha: Rational | None = None,
    digits: int = 15,
) -> ScientificRequest:
    base = _request()
    low, high, _ = base.goals
    assert isinstance(low, CalculationGoal)
    assert isinstance(high, CalculationGoal)
    specification = ReferenceExtrapolationStudy(
        id="reference",
        geometry="h2",
        family="cc-pvXZ",
        low=BasisEnergyPoint(basis="cc-pvdz", cardinal=2, models=low.models),
        high=BasisEnergyPoint(basis="cc-pvtz", cardinal=3, models=high.models),
        alpha=alpha or Rational(numerator=1),
        shape=shape,
        coefficient_digits=digits,
    )
    expansion = extrapolation_expansion(specification)
    return ScientificRequest(molecules=base.molecules, goals=expansion.goals)


@pytest.mark.parametrize("shape", ["cardinal", "sqrt_cardinal"])
@pytest.mark.parametrize(
    "alpha",
    [
        Rational(numerator=163, denominator=100),
        Rational(numerator=1, denominator=10**70),
    ],
)
def test_expansion_constructs_certified_coefficients(
    shape: Literal["cardinal", "sqrt_cardinal"],
    alpha: Rational,
) -> None:
    """Cover both decay coordinates and very small positive exponents.

    Args:
        shape: Linear or square-root cardinal decay coordinate.
        alpha: Explicit positive decay constant, including a cancellation-prone case.
    """
    request = _expanded(shape=shape, alpha=alpha, digits=30)

    proposed = propose(request)

    assert proposed.status == "constructed"
    last = request.goals[-1]
    assert isinstance(last, ExpressionGoal)
    weights = tuple(
        term.coefficient.fraction
        if isinstance(term.coefficient, Rational)
        else Fraction(term.coefficient)
        for term in last.terms
    )
    assert sum(weights) == 1
    delta = 1.0 if shape == "cardinal" else math.sqrt(3) - math.sqrt(2)
    expected = -1 / math.expm1(float(alpha.fraction) * delta)
    assert float(weights[0]) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (
            ("goals", 2, "extrapolation", "alpha", "numerator"),
            2,
            "exponential_coefficient_bound",
        ),
        (
            ("goals", 2, "extrapolation", "shape"),
            "sqrt_cardinal",
            "exponential_coefficient_bound",
        ),
        (
            ("goals", 2, "extrapolation", "coefficient_digits"),
            30,
            "exponential_coefficient_bound",
        ),
        (("goals", 2, "terms", 0, "coefficient"), -1, "extrapolation_formula"),
        (
            ("goals", 2, "quantity", "meaning"),
            "basis_limit_correction",
            "extrapolation_quantity",
        ),
        (("goals", 1, "models", 0, "frozen_core"), True, "extrapolation_treatment"),
        (("goals", 1, "models", 0, "method"), "mp2", "exponential_reference_source"),
        (
            ("goals", 2, "extrapolation", "family"),
            "augmented",
            "extrapolation_basis_sequence",
        ),
    ],
)
def test_independent_scientific_contract_rejects_consistent_wrong_intent(
    path: tuple[str | int, ...],
    value: JsonValue,
    code: str,
) -> None:
    """Reject scientific errors even when requested and constructed algebra agree.

    Args:
        path: Scientific input to alter in an otherwise accepted request.
        value: Self-consistent replacement in the independent intent.
        code: Expected independently derived contract finding.
    """
    proposal = propose(_edit(_request(), path, value))

    assert proposal.plan is None
    assert proposal.report is not None
    assert any(issue.code == code for issue in proposal.report.diagnostics)


def test_wrong_complementary_weights_are_rejected_without_a_user_relation() -> None:
    """Reject the wrong -1,2 weights even though they sum exactly to one."""
    request = _edit(_request(), ("goals", 2, "terms", 0, "coefficient"), -1)
    request = _edit(request, ("goals", 2, "terms", 1, "coefficient"), 2)

    proposed = propose(request)

    assert proposed.report is not None
    assert proposed.plan is None
    assert any(
        item.code == "exponential_coefficient_bound"
        for item in proposed.report.diagnostics
    )


@pytest.mark.parametrize(("root", "accepted"), [(1, True), (2, False)])
def test_root_aliases_cannot_change_the_meaning_of_a_reference_point(
    root: int,
    accepted: bool,
) -> None:
    """Cancel repeated aliases of one root while retaining different excitations.

    Args:
        root: Root selected by the second product alias.
        accepted: Whether the two product terms represent the same native value.
    """
    base = _request()
    altered = _edit(base, ("goals", 2, "terms", 0, "goal"), "contaminated")
    altered = _edit(
        altered, ("goals", 2, "extrapolation", "low", "result"), "contaminated"
    )
    response = CalculationGoal(
        id="response",
        driver="energy",
        geometry="h2",
        models=(
            Model(
                method="td-hf",
                basis="cc-pvdz",
                reference="rhf",
                tdscf=TDSCFAnalysis(states=2),
                settings=(Setting(name="scf_type", value="PK"),),
            ),
        ),
    )
    gaps = tuple(
        ProductGoal(
            id=f"gap_{index}",
            calculation="response",
            name="excitation_energy",
            electronic_target=ElectronicTarget(
                root=selected, multiplicity=1 if index == 2 else None
            ),
        )
        for index, selected in enumerate((1, root), 1)
    )
    request = ScientificRequest(
        molecules=base.molecules,
        goals=(
            *base.goals[:2],
            response,
            *gaps,
            ExpressionGoal(
                id="contaminated",
                terms=(
                    GoalTerm(goal="low", coefficient=1),
                    GoalTerm(goal="gap_1", coefficient=1),
                    GoalTerm(goal="gap_2", coefficient=-1),
                ),
                quantity=QuantityType(meaning="linear_combination", unit="hartree"),
            ),
            altered.goals[-1],
        ),
    )

    proposed = propose(request)

    assert (proposed.plan is not None) == accepted
    assert proposed.report is not None
    if not accepted:
        assert any(
            item.code == "exponential_reference_source"
            for item in proposed.report.diagnostics
        )


@pytest.mark.parametrize(
    ("numerator", "accepted"),
    [
        (-581976706869327, True),
        (-581976706869325, False),
    ],
)
def test_the_error_bound_is_checked_as_an_interval(
    numerator: int,
    accepted: bool,
) -> None:
    """Distinguish one-unit changes on opposite sides of the exact exponential weight.

    Args:
        numerator: Low coefficient with denominator 10**15; high is its complement.
        accepted: Whether the exact error is below 10**-15.
    """
    request = _edit(
        _request(), ("goals", 2, "terms", 0, "coefficient", "numerator"), numerator
    )
    request = _edit(
        request,
        ("goals", 2, "terms", 1, "coefficient", "numerator"),
        10**15 - numerator,
    )

    result = propose(request)

    assert (result.status == "constructed") == accepted


def test_rounded_zero_weight_preserves_both_required_points() -> None:
    """Keep the low-cardinal calculation mandatory when its rounded weight is zero."""
    request = _expanded(alpha=Rational(numerator=32), digits=6)

    result = propose(request)

    assert result.plan is not None
    assert result.report is not None
    assert result.report.request_complete
    assert sum(isinstance(step, Calculation) for step in result.plan.steps) == 2
    last = request.goals[-1]
    assert isinstance(last, ExpressionGoal)
    assert isinstance(last.terms[0].coefficient, Rational)
    assert last.terms[0].coefficient.fraction == 0


def test_reference_limit_composes_with_a_correlation_limit_and_permitted_reuse() -> (
    None
):
    """Share authorized HF calls and keep one net energy in the composite estimate."""
    reference = _edit(_expanded(), ("goals", 0, "reuse_group"), "shared-reference")
    reference = _edit(reference, ("goals", 1, "reuse_group"), "shared-reference")
    low, high, _ = reference.goals
    assert isinstance(low, CalculationGoal)
    assert isinstance(high, CalculationGoal)
    points = tuple(
        BasisCorrectionPoint(
            basis=basis,
            cardinal=cardinal,
            models=(
                Model(
                    method="mp2",
                    basis=basis,
                    reference="rhf",
                    settings=(
                        Setting(name="scf_type", value="PK"),
                        Setting(name="mp2_type", value="CONV"),
                        Setting(name="qc_module", value="OCC"),
                    ),
                ),
            ),
            reference_models=goal.models,
        )
        for basis, cardinal, goal in (("cc-pvdz", 2, low), ("cc-pvtz", 3, high))
    )
    correlation = extrapolation_expansion(
        ExtrapolationStudy(
            id="correlation",
            geometry="h2",
            family="cc-pvXZ",
            power=3,
            low=points[0],
            high=points[1],
            reuse_group="shared-reference",
        )
    )
    request = ScientificRequest(
        molecules=reference.molecules,
        goals=(
            *reference.goals,
            *correlation.goals,
            ExpressionGoal(
                id="total",
                terms=(
                    GoalTerm(goal=reference.goals[-1].id, coefficient=1),
                    GoalTerm(goal=correlation.target, coefficient=1),
                ),
                quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
            ),
        ),
    )

    result = propose(request)

    assert result.plan is not None
    assert result.report is not None
    assert result.report.request_complete
    assert sum(isinstance(step, Calculation) for step in result.plan.steps) == 4
    wrong = propose(_edit(request, ("goals", 10, "terms", 0, "coefficient"), 2))
    assert wrong.plan is None
    assert wrong.report is not None
    assert any(
        item.code == "extrapolation_total_formula" for item in wrong.report.diagnostics
    )


def test_request_and_plan_recipes_must_agree() -> None:
    """Reject a plan that drops its independently required convergence model."""
    request = _request()
    proposal = propose(request)
    assert proposal.plan is not None
    damaged = _edit(proposal.plan, ("steps", 2, "extrapolation"), None)

    report = verify(damaged, request=request)

    assert not report.request_complete
    assert {item.code for item in report.diagnostics} >= {
        "goal_extrapolation",
        "extrapolation_recipe",
    }


def test_missing_sequence_evidence_stays_unknown() -> None:
    """Require independent cardinal/family evidence instead of parsing basis names."""
    catalog = load_catalog()
    index = next(
        i for i, basis in enumerate(catalog.bases) if basis.key == ("cc-pvdz", "basis")
    )
    missing = _edit(catalog, ("bases", index, "sequence"), None)

    proposal = propose(_request(), missing)

    assert proposal.status == "unknown"
    assert proposal.report is not None
    assert any(
        item.code == "extrapolation_basis_evidence"
        for item in proposal.report.diagnostics
    )


def test_decimal_context_does_not_change_the_constructed_formula() -> None:
    """Ignore hostile caller precision and rounding while computing recipe weights."""
    expected = _expanded(shape="sqrt_cardinal")
    with localcontext() as context:
        context.prec = 3
        context.rounding = ROUND_DOWN
        context.Emax = 5
        actual = _expanded(shape="sqrt_cardinal")

    assert actual == expected


def test_finite_study_and_export_preserve_exponential_recipes(tmp_path: Path) -> None:
    """Namespace both basis points per case and export full symbolic recipes.

    Args:
        tmp_path: Construction bundle destination.
    """
    template = _expanded()
    request = finite_study(
        template,
        tuple(
            StudyCase(id=name, molecules=template.molecules) for name in ("one", "two")
        ),
    )

    proposed = propose(request)

    assert proposed.plan is not None
    assert len(proposed.plan.steps) == 6
    for step in proposed.plan.steps:
        if isinstance(step, Combination):
            assert isinstance(step.extrapolation, ExponentialExtrapolation)
            assert step.extrapolation.low.result.startswith(step.id.split(":")[0] + ":")
    exported = export_bundle(proposed.plan, request, destination=tmp_path / "bundle")
    assert len(exported.manifest.expressions) == 2
    assert all(
        isinstance(item.extrapolation, ExponentialExtrapolation)
        for item in exported.manifest.expressions
    )
    assert not exported.manifest.native_variables


@pytest.mark.parametrize(
    "alpha",
    [
        Rational(numerator=0),
        Rational(numerator=-1),
        Rational(numerator=33),
        Rational(numerator=1, denominator=2**257),
    ],
)
def test_alpha_bounds_are_explicit(alpha: Rational) -> None:
    """Reject decay choices outside the bounded arithmetic contract.

    Args:
        alpha: Invalid or excessively large rational representation.
    """
    with pytest.raises(ValidationError, match="Alpha must be positive"):
        _expanded(alpha=alpha)


def test_exponential_schema_explains_the_rounding_contract() -> None:
    """Expose decay, coefficient precision, and source point fields for discovery."""
    schema = describe_schema("request", definition="ExponentialExtrapolation")
    assert {field.name for field in schema.fields} >= {
        "shape",
        "alpha",
        "coefficient_digits",
        "low",
        "high",
    }
    selected = describe_schema(
        "request", definition="ExpressionGoal", fields=("extrapolation",)
    )
    assert selected.json_schema is not None
    validator = Draft202012Validator(selected.json_schema)
    validator.check_schema(selected.json_schema)
    expression = _request().goals[-1]
    assert validator.is_valid(
        _JSON.validate_json(expression.model_dump_json(include={"extrapolation"}))
    )
