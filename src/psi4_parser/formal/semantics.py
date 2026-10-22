"""Check physical quantity meanings separately from exact scalar algebra."""

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations
from math import comb

from psi4_parser.builder import Molecule
from psi4_parser.formal.algebra import Form, expression_forms
from psi4_parser.formal.environment_contracts import solvation_shift_issues
from psi4_parser.formal.excited_contracts import excited_total_issues
from psi4_parser.formal.extrapolation_contracts import extrapolation_issues
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Diagnostic,
    Plan,
    Product,
    Step,
    Subsystem,
)
from psi4_parser.formal.nuclei import Center, centers
from psi4_parser.formal.products import (
    SAPT_COMPONENTS,
    THERMAL_PRODUCTS,
    THERMAL_REACTIONS,
    THERMAL_TOTALS,
)
from psi4_parser.formal.science import ExpectedQuantity, ProductName, Rational


@dataclass(frozen=True)
class _Facts:
    steps: dict[str, Step]
    contexts: dict[str, Molecule]
    quantities: dict[str, ExpectedQuantity]
    forms: dict[str, Form]


@dataclass
class _Balance:
    nuclei: dict[tuple[str, int, str], Fraction] = field(default_factory=dict)
    charge: Fraction = Fraction(0)

    def include(
        self, sites: tuple[Center, ...], charge: int, coefficient: Fraction
    ) -> None:
        self.charge += charge * coefficient
        for site in sites:
            if site.role == "real":
                key = (site.element, site.isotope, str(site.mass))
                self.nuclei[key] = self.nuclei.get(key, Fraction(0)) + coefficient

    @property
    def residual(self) -> dict[tuple[str, int, str], Fraction]:
        return {key: value for key, value in self.nuclei.items() if value}


def _reaction_issue(path: tuple[str | int, ...], code: str, message: str) -> Diagnostic:
    return Diagnostic(path=path, code=code, message=message, status="violated")


@dataclass(frozen=True)
class _ReactionTerm:
    calculation: Calculation
    coefficient: Fraction
    channel: str


def _reaction_leaf(
    leaf: str, coefficient: Fraction, facts: _Facts, thermal: ProductName | None
) -> tuple[_ReactionTerm, ...] | None:
    source = facts.steps[leaf]
    if (
        isinstance(source, Calculation)
        and facts.quantities[leaf].quantity.meaning == "electronic_energy"
    ):
        return (_ReactionTerm(source, coefficient, "electronic_energy"),)
    if not isinstance(source, Product) or thermal is None:
        return None
    correction = THERMAL_TOTALS[thermal]
    if source.name not in {thermal, correction}:
        return None
    calculation = facts.steps[source.calculation]
    if not isinstance(calculation, Calculation):
        return None
    result: tuple[_ReactionTerm, ...] = (
        _ReactionTerm(calculation, coefficient, correction),
    )
    if source.name == thermal:
        result += (_ReactionTerm(calculation, coefficient, "electronic_energy"),)
    return result


def _reaction_sources(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[tuple[_ReactionTerm, ...], tuple[Diagnostic, ...]]:
    meaning = facts.quantities[step.id].quantity.meaning
    thermal = THERMAL_REACTIONS.get(meaning)
    if thermal is not None and any(
        (
            term.coefficient.numerator
            if isinstance(term.coefficient, Rational)
            else term.coefficient
        )
        != 0
        and facts.quantities[term.result].quantity.meaning not in {thermal, meaning}
        for term in step.terms
    ):
        return (), (
            Diagnostic(
                path=path,
                code="reaction_source",
                status="unsupported",
                message=f"A {meaning} expression requires molecular {thermal} "
                "totals or nested reactions of the same meaning.",
            ),
        )
    terms: list[_ReactionTerm] = []
    contexts: set[tuple[str, bool, bool]] = set()
    for leaf, coefficient in facts.forms[step.id].items():
        contribution = _reaction_leaf(leaf, coefficient, facts, thermal)
        if contribution is None:
            return (), (
                Diagnostic(
                    path=path,
                    code="reaction_source",
                    status="unsupported",
                    message="Reaction sources must preserve the required "
                    "electronic-energy and thermal-correction meanings.",
                ),
            )
        terms.extend(contribution)
        if thermal is not None and isinstance(facts.steps[leaf], Product):
            analysis = facts.quantities[leaf].analysis
            if analysis is None:
                return (), (
                    Diagnostic(
                        path=path,
                        code="reaction_thermal_context",
                        status="unknown",
                        message="Thermal sources need explicit analysis conditions.",
                    ),
                )
            contexts.add(
                (
                    analysis.conditions.model_dump_json(),
                    analysis.project_translations,
                    analysis.project_rotations,
                )
            )
    if thermal is not None and len(contexts) != 1:
        return (), (
            _reaction_issue(
                path,
                "reaction_thermal_context",
                "Thermal reactions require a common temperature, pressure, treatment, "
                "and projection choices; rotational symmetry remains species-specific.",
            ),
        )
    return tuple(terms), ()


def _reaction(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    balances: dict[str, _Balance] = {}
    treatments: dict[tuple[str, str], _Balance] = {}
    if not facts.forms[step.id]:
        return (
            _reaction_issue(path, "reaction_terms", "Supply nonzero reaction terms."),
        )
    sources, issues = _reaction_sources(step, facts, path)
    if issues:
        return issues
    for source in sources:
        calculation = source.calculation
        context = facts.contexts[calculation.geometry]
        if context.state is None:
            return (
                Diagnostic(
                    path=path,
                    code="reaction_state",
                    status="unknown",
                    message=f"Supply an electronic state for {calculation.id}.",
                ),
            )
        try:
            sites = centers(context)
        except ValueError as error:
            return (Diagnostic(path=path, code="reaction_nucleus", message=str(error)),)
        balances.setdefault(source.channel, _Balance()).include(
            sites, context.state.charge, source.coefficient
        )
        # The molecular request fixes each species' reference independently.
        # Other choices must balance in every component of a composite protocol.
        treatment = calculation.model.reaction_treatment_identity
        treatments.setdefault((source.channel, treatment), _Balance()).include(
            sites, context.state.charge, source.coefficient
        )
    findings = [
        issue
        for balance in balances.values()
        for issue in _reaction_balance(balance, path)
    ]
    if not findings and any(
        item.residual or item.charge for item in treatments.values()
    ):
        findings.append(
            _reaction_issue(
                path,
                "reaction_model_balance",
                "Every electronic-energy and thermal-correction treatment must "
                "balance nuclei and charge; only species-specific SCF references "
                "may differ.",
            )
        )
    return tuple(findings)


def _reaction_balance(
    balance: _Balance, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    issues: list[Diagnostic] = []
    if balance.residual:
        residual = "; ".join(
            f"{element}(isotope={isotope},mass={mass}): {weight}"
            for (element, isotope, mass), weight in sorted(balance.residual.items())
        )
        issues.append(
            _reaction_issue(
                path,
                "reaction_balance",
                f"Nonzero product-minus-reactant nuclei: {residual}.",
            )
        )
    if balance.charge:
        issues.append(
            _reaction_issue(
                path,
                "reaction_charge",
                f"Nonzero product-minus-reactant charge: {balance.charge}.",
            )
        )
    return tuple(issues)


def _interaction_expected(
    names: tuple[str, ...], order: int
) -> dict[frozenset[str], Fraction]:
    if order == len(names):
        return {
            **{frozenset((name,)): Fraction(-1) for name in names},
            frozenset(names): Fraction(1),
        }
    expected: dict[frozenset[str], Fraction] = {}
    for size in range(1, order + 1):
        # Independent finite summation of connected increments, rather than
        # the closed-form coefficient calculation used by plan construction.
        coefficient = sum(
            (1 if (body - size) % 2 == 0 else -1) * comb(len(names) - size, body - size)
            for body in range(max(2, size), order + 1)
        )
        if coefficient:
            expected.update(
                (frozenset(subset), Fraction(coefficient))
                for subset in combinations(names, size)
            )
    return expected


def _interaction_issue(
    path: tuple[str | int, ...], message: str
) -> tuple[Diagnostic, ...]:
    return (
        Diagnostic(
            path=path, code="interaction_semantics", status="violated", message=message
        ),
    )


def _interaction_coverage(
    actual: dict[frozenset[str], Fraction],
    names: tuple[str, ...],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    order = max((len(real) for real in actual), default=0)
    if (
        len(names) <= 1
        or order <= 1
        or any(not real or not real <= set(names) for real in actual)
    ):
        return _interaction_issue(
            path, "Interaction terms require at least two parent fragments."
        )
    if order < len(names) and comb(len(names), 2) > len(actual):
        return _interaction_issue(
            path, "The interaction omits required subsystem quantities."
        )
    if actual != _interaction_expected(names, order):
        return _interaction_issue(
            path, "Subsystem coefficients do not form the required interaction."
        )
    return ()


def _interaction(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    if _has_sapt_components(step, facts):
        return _sapt_composition(step, facts, path)
    actual: dict[frozenset[str], Fraction] = {}
    parents: set[str] = set()
    models: set[str] = set()
    for leaf, coefficient in facts.forms[step.id].items():
        calculation = facts.steps[leaf]
        if (
            not isinstance(calculation, Calculation)
            or calculation.driver != "energy"
            or facts.quantities[leaf].quantity.meaning != "electronic_energy"
        ):
            return _interaction_issue(
                path,
                "Interaction formulas require explicit subsystem electronic energies.",
            )
        geometry = facts.steps.get(calculation.geometry)
        if isinstance(geometry, Subsystem):
            parent = geometry.geometry
            real = frozenset(geometry.real_fragments)
        else:
            parent = calculation.geometry
            real = frozenset(
                fragment.name for fragment in facts.contexts[parent].fragments
            )
        if real in actual:
            return _interaction_issue(
                path,
                "Use one quantity per real-fragment set; independent calls can differ.",
            )
        actual[real] = coefficient
        parents.add(parent)
        models.add(calculation.model.identity)
    if len(parents) != 1 or len(models) != 1:
        return _interaction_issue(
            path,
            "Interaction terms must share one parent geometry and computational model.",
        )
    parent = next(iter(parents))
    names = tuple(fragment.name for fragment in facts.contexts[parent].fragments)
    return _interaction_coverage(actual, names, path)


def _sapt_composition(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    actual: dict[tuple[str, str], Fraction] = {}
    for leaf, coefficient in facts.forms[step.id].items():
        source = facts.steps[leaf]
        if not isinstance(source, Product) or source.name not in SAPT_COMPONENTS:
            return (
                _reaction_issue(
                    path,
                    "sapt_component_formula",
                    "SAPT decomposition requires only its four native components.",
                ),
            )
        key = (source.calculation, source.name)
        actual[key] = actual.get(key, Fraction(0)) + coefficient
    producers = {name for name, _ in actual}
    expected = {
        (name, component): Fraction(1)
        for name in producers
        for component in SAPT_COMPONENTS
    }
    if len(producers) != 1 or actual != expected:
        return (
            _reaction_issue(
                path,
                "sapt_component_formula",
                "Sum each SAPT component exactly once from one producing calculation.",
            ),
        )
    return ()


def _extrapolated_total(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    if sum(facts.forms[step.id].values(), Fraction(0)) != 1:
        return (
            _reaction_issue(
                path,
                "extrapolation_total_formula",
                "A corrected electronic estimate requires one net electronic "
                "energy; a basis-limit correction alone is not a total energy.",
            ),
        )
    geometries = {facts.quantities[leaf].geometry for leaf in facts.forms[step.id]}
    if len(geometries) == 1 and None not in geometries:
        return ()
    return (
        _reaction_issue(
            path,
            "extrapolation_total_geometry",
            "Electronic energies and basis-limit corrections "
            "must use the same geometry provenance.",
        ),
    )


def _has_sapt_components(step: Combination, facts: _Facts) -> bool:
    return any(
        facts.quantities[leaf].product in SAPT_COMPONENTS
        for leaf in facts.forms[step.id]
    )


def _special_formula_issues(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    if (
        step.extrapolation is None
        and facts.quantities[step.id].quantity.meaning == "excited_state_energy"
    ):
        return excited_total_issues(
            facts.steps, facts.forms[step.id], facts.quantities, path
        )
    if (
        step.extrapolation is None
        and facts.quantities[step.id].quantity.meaning == "electronic_solvation_shift"
    ):
        return solvation_shift_issues(
            facts.steps, facts.forms[step.id], facts.quantities, path
        )
    return extrapolation_issues(step, facts.steps, facts.forms, facts.quantities, path)


def expression_semantics(
    plan: Plan,
    contexts: dict[str, Molecule],
    quantities: dict[str, ExpectedQuantity],
) -> tuple[Diagnostic, ...]:
    """Return invalid quantity meanings, interactions, and reaction stoichiometry."""
    facts = _Facts(
        {step.id: step for step in plan.steps},
        contexts,
        quantities,
        expression_forms(plan),
    )
    issues: list[Diagnostic] = []
    for index, step in enumerate(plan.steps):
        if not isinstance(step, Combination):
            continue
        meaning = quantities[step.id].quantity.meaning
        operands = {quantities[term.result].quantity.meaning for term in step.terms}
        path: tuple[str | int, ...] = ("steps", index, "quantity")
        if step.extrapolation is not None or meaning in {
            "basis_limit_correction",
            "basis_limit_reference_energy",
            "electronic_solvation_shift",
            "excited_state_energy",
        }:
            issues.extend(_special_formula_issues(step, facts, path))
            continue
        if meaning in THERMAL_PRODUCTS:
            issues.extend(_thermal_composition(step, facts, path))
            continue
        if meaning == "reaction_energy" or meaning in THERMAL_REACTIONS:
            issues.extend(_reaction(step, facts, path))
            continue
        if operands == {meaning} or meaning in {
            "energy_difference",
            "linear_combination",
        }:
            continue
        if meaning == "interaction_energy":
            issues.extend(_interaction(step, facts, path))
        elif meaning == "electronic_energy" and operands <= {
            "electronic_energy",
            "electronic_energy_correction",
            "basis_limit_correction",
            "basis_limit_reference_energy",
        }:
            if operands & {"basis_limit_correction", "basis_limit_reference_energy"}:
                issues.extend(_extrapolated_total(step, facts, path))
            continue
        else:
            issues.append(
                Diagnostic(
                    path=path,
                    code="quantity_semantics",
                    status="unsupported",
                    message=f"No contract converts {sorted(operands)} into {meaning}.",
                )
            )
    return tuple(issues)


def _thermal_composition(
    step: Combination, facts: _Facts, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    meaning = facts.quantities[step.id].quantity.meaning
    target = next(name for name in THERMAL_PRODUCTS if name == meaning)
    needed = THERMAL_TOTALS.get(target, target)
    electronic = Fraction(0)
    corrections: dict[str, Fraction] = {}
    geometries: set[tuple[str | None, str | None, str | None]] = set()
    analyses: set[str] = set()
    for leaf, coefficient in facts.forms[step.id].items():
        product = facts.quantities[leaf]
        geometries.add(
            (
                product.system,
                product.geometry,
                product.state.model_dump_json() if product.state else None,
            )
        )
        if product.quantity.meaning == "electronic_energy":
            electronic += coefficient
            continue
        name = product.product
        if name in THERMAL_TOTALS:
            electronic += coefficient
            name = THERMAL_TOTALS[name]
        if name != needed:
            return (
                Diagnostic(
                    path=path,
                    code="thermal_formula",
                    status="unsupported",
                    message=f"No {meaning} contract for the supplied product meanings.",
                ),
            )
        if product.analysis is None:
            return (
                Diagnostic(
                    path=path,
                    code="thermal_context",
                    status="unknown",
                    message="Thermal sources need explicit analysis conditions.",
                ),
            )
        analyses.add(product.analysis.model_dump_json())
        corrections[product.producer] = (
            corrections.get(product.producer, Fraction(0)) + coefficient
        )
    required_electronic = 1 if target in THERMAL_TOTALS else 0
    if electronic != required_electronic or sum(corrections.values(), Fraction(0)) != 1:
        return (
            Diagnostic(
                path=path,
                code="thermal_formula",
                status="violated",
                message=f"A {meaning} expression needs {required_electronic} net "
                f"electronic energies and one net {needed} correction.",
            ),
        )
    if len(geometries) != 1 or any(value is None for value in next(iter(geometries))):
        return (
            Diagnostic(
                path=path,
                code="thermal_geometry",
                status="violated",
                message="A corrected molecular energy must share geometry, "
                "system, and electronic-state provenance.",
            ),
        )
    if len(analyses) != 1:
        return (
            Diagnostic(
                path=path,
                code="thermal_context",
                status="violated",
                message="A corrected molecular energy needs one common "
                "temperature, pressure, symmetry, and projection context.",
            ),
        )
    return ()
