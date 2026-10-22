"""Expand exact scalar recipes while retaining independent calculation identities."""

from fractions import Fraction

from psi4_parser.formal.models import Calculation, Combination, Plan, Product
from psi4_parser.formal.products import PRIMARY_SCALAR_PRODUCTS, product_identity
from psi4_parser.formal.science import Rational

type Form = dict[str, Fraction]


def expression_forms(plan: Plan) -> dict[str, Form]:
    """Return leaf coefficients for each quantity after reference order is checked."""
    forms: dict[str, Form] = {}
    aliases = {
        product_identity(step.calculation, step.name, step.electronic_target): step.id
        for step in plan.steps
        if isinstance(step, Product)
    }
    for step in plan.steps:
        if isinstance(step, Calculation):
            forms[step.id] = {step.id: Fraction(1)}
        elif isinstance(step, Product):
            forms[step.id] = {
                step.calculation
                if step.name in PRIMARY_SCALAR_PRODUCTS
                else aliases[
                    product_identity(
                        step.calculation, step.name, step.electronic_target
                    )
                ]: Fraction(1)
            }
        elif isinstance(step, Combination):
            terms: Form = {}
            for term in step.terms:
                coefficient = (
                    term.coefficient.fraction
                    if isinstance(term.coefficient, Rational)
                    else Fraction(term.coefficient)
                )
                for leaf, weight in forms[term.result].items():
                    terms[leaf] = terms.get(leaf, Fraction(0)) + coefficient * weight
            forms[step.id] = {leaf: weight for leaf, weight in terms.items() if weight}
    return forms
