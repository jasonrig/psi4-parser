"""Compose finite geometry and model studies from arbitrary scientific goals."""

import json

from pydantic import Field

from psi4_parser.builder import MoleculeDeclaration
from psi4_parser.formal._record import Record
from psi4_parser.formal.coverage import (
    request_diagnostics,
    translate_quantity,
    translate_requirement,
)
from psi4_parser.formal.extrapolation_models import translate_extrapolation
from psi4_parser.formal.intent import (
    CalculationGoal,
    ExpressionGoal,
    Goal,
    GoalTerm,
    ProductGoal,
    ScientificRequest,
    SubsystemGoal,
)
from psi4_parser.formal.models import Requirement
from psi4_parser.formal.science import Model, QuantityType


class CaseModels(Record):
    """Replace the explicitly allowed models for one calculation in a study case."""

    goal: str = Field(min_length=1, description="Calculation goal ID in the template.")
    models: tuple[Model, ...] = Field(
        min_length=1,
        description="Models explicitly permitted in this case, in preference order.",
    )


class StudyCase(Record):
    """Specify molecular inputs and permitted model choices for one finite case."""

    id: str = Field(
        min_length=1,
        description="Unique case identity used to namespace all derived goals.",
    )
    molecules: tuple[MoleculeDeclaration, ...] = Field(
        min_length=1, description="Inputs using exactly the template's molecular names."
    )
    models: tuple[CaseModels, ...] = Field(
        default=(),
        description="Explicit model replacements; empty retains the template.",
    )
    relations: tuple[Requirement, ...] = Field(
        default=(),
        description=(
            "Additional mandatory case relationships using template identities, "
            "such as independently specified coordinate values or ranges."
        ),
    )


def _quantity(
    quantity: QuantityType | None, mapping: dict[str, str]
) -> QuantityType | None:
    if quantity is None:
        return None
    return translate_quantity(quantity, mapping)


def _goal(
    goal: Goal,
    mapping: dict[str, str],
    overrides: dict[str, tuple[Model, ...]],
    case: str,
) -> Goal:
    if isinstance(goal, ProductGoal):
        return ProductGoal(
            id=mapping[goal.id],
            calculation=mapping[goal.calculation],
            name=goal.name,
            electronic_target=goal.electronic_target,
            quantity=_quantity(goal.quantity, mapping),
            reason=goal.reason,
        )
    if isinstance(goal, CalculationGoal):
        return CalculationGoal(
            id=mapping[goal.id],
            driver=goal.driver,
            geometry=mapping[goal.geometry],
            models=overrides.get(goal.id, goal.models),
            quantity=_quantity(goal.quantity, mapping),
            constraints=goal.constraints,
            derivative_routes=goal.derivative_routes,
            properties=goal.properties,
            reason=goal.reason,
            analysis=goal.analysis,
            sapt=goal.sapt,
            reuse_group=json.dumps((case, goal.reuse_group))
            if goal.reuse_group is not None
            else None,
        )
    if isinstance(goal, ExpressionGoal):
        return ExpressionGoal(
            id=mapping[goal.id],
            quantity=translate_quantity(goal.quantity, mapping),
            extrapolation=translate_extrapolation(goal.extrapolation, mapping),
            reason=goal.reason,
            terms=tuple(
                GoalTerm(goal=mapping[term.goal], coefficient=term.coefficient)
                for term in goal.terms
            ),
        )
    return SubsystemGoal(
        id=mapping[goal.id],
        geometry=mapping[goal.geometry],
        real_fragments=goal.real_fragments,
        state=goal.state,
        reason=goal.reason,
    )


def _case_overrides(
    case: StudyCase, template: ScientificRequest
) -> dict[str, tuple[Model, ...]]:
    calculations = {
        goal.id for goal in template.goals if isinstance(goal, CalculationGoal)
    }
    overrides = {item.goal: item.models for item in case.models}
    if len(overrides) != len(case.models) or not set(overrides) <= calculations:
        raise ValueError("Case model replacements must name distinct calculation goals")
    return overrides


def finite_study(
    template: ScientificRequest,
    cases: tuple[StudyCase, ...],
    *,
    max_cases: int = 1000,
) -> ScientificRequest:
    """Require every finite case of an arbitrary composable scientific request.

    Prepare numerical geometries with the builder before creating cases. A case
    can replace a calculation's permitted models and add mandatory relationships,
    including independent coordinate targets. Every input and goal receives a
    case prefix; future geometry histories remain separate.

    Args:
        template: Calculations, expressions, subsystems, and relationships to repeat.
        cases: Ordered independent inputs with unique case IDs.
        max_cases: Positive expansion bound; exceeding it raises an explicit error.

    Returns:
        An independent scientific request requiring all cases and dependencies.

    Raises:
        ValueError: The template, names, replacements, or expansion bounds are invalid.
    """
    template = ScientificRequest.model_validate(template)
    problems = request_diagnostics(template)
    if problems:
        raise ValueError(
            "Invalid study template: " + "; ".join(item.message for item in problems)
        )
    if max_cases < 1 or not cases or len(cases) > max_cases:
        raise ValueError("Supply nonempty cases within a positive max_cases bound")
    cases = tuple(StudyCase.model_validate(case) for case in cases)
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Study case IDs must be unique")
    names = {item.name for item in template.molecules}
    molecules: list[MoleculeDeclaration] = []
    goals: list[Goal] = []
    relations: list[Requirement] = []
    for case in cases:
        supplied = {item.name for item in case.molecules}
        if supplied != names or len(supplied) != len(case.molecules):
            raise ValueError(
                "Each case must supply exactly the template's molecular names"
            )
        mapping = {
            name: f"{case.id}:{name}"
            for name in (*names, *(goal.id for goal in template.goals))
        }
        molecules.extend(
            MoleculeDeclaration(
                name=mapping[item.name], geometry=item.geometry, comments=item.comments
            )
            for item in case.molecules
        )
        overrides = _case_overrides(case, template)
        goals.extend(
            _goal(goal, mapping, overrides, case.id) for goal in template.goals
        )
        for relation in (*template.relations, *case.relations):
            renamed = translate_requirement(relation, mapping)
            if renamed is None:
                raise ValueError("A template relation references an unknown goal")
            relations.append(renamed)
    request = ScientificRequest(
        molecules=tuple(molecules), goals=tuple(goals), relations=tuple(relations)
    )
    problems = request_diagnostics(request)
    if problems:
        raise ValueError(
            "Study identities conflict: " + "; ".join(item.message for item in problems)
        )
    return request
