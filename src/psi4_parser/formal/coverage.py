"""Derive required checks from an independent scientific request."""

from dataclasses import dataclass

from psi4_parser.formal.contracts import primary_quantity
from psi4_parser.formal.coordinate_models import CoordinateRange, CoordinateValue
from psi4_parser.formal.extrapolation_models import translate_extrapolation
from psi4_parser.formal.intent import (
    CalculationGoal,
    ExpressionGoal,
    Goal,
    ProductGoal,
    ScientificRequest,
    SubsystemGoal,
)
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Diagnostic,
    EnergyFormula,
    EnergyTerm,
    Plan,
    Product,
    Requirement,
    SameGeometry,
    SameModel,
    Step,
    Subsystem,
    UsesGeometry,
)
from psi4_parser.formal.products import product_quantity
from psi4_parser.formal.science import GoalCoverage, QuantityType


@dataclass(frozen=True)
class Coverage:
    """Retain request findings and its derived mandatory obligations.

    Attributes:
        diagnostics: Missing or incompatible scientific work.
        goals: Coverage of each requested goal.
        requirements: Relationships the verifier must prove independently.
    """

    diagnostics: tuple[Diagnostic, ...]
    goals: tuple[GoalCoverage, ...]
    requirements: tuple[Requirement, ...]


def requirement_reference_issues(
    requirement: Requirement,
    path: tuple[str | int, ...],
    calculations: set[str],
    geometries: set[str],
    quantities: set[str],
) -> list[Diagnostic]:
    """Return unknown or wrong-kind reference findings at the supplied field path."""
    references: list[tuple[tuple[str | int, ...], str, set[str]]] = []
    if isinstance(requirement, UsesGeometry):
        references.extend(
            [
                (("calculation",), requirement.calculation, calculations),
                (("geometry",), requirement.geometry, geometries),
            ]
        )
    elif isinstance(requirement, EnergyFormula):
        references.append((("result",), requirement.result, quantities))
        references.extend(
            (("terms", index, "result"), term.result, quantities)
            for index, term in enumerate(requirement.terms)
        )
    elif isinstance(requirement, (CoordinateValue, CoordinateRange)):
        references.append((("geometry",), requirement.geometry, geometries))
    else:
        references.extend(
            (("calculations", index), name, calculations)
            for index, name in enumerate(requirement.calculations)
        )
    return [
        Diagnostic(path=(*path, *suffix), message=f"Unknown reference: {name}")
        for suffix, name, known in references
        if name not in known
    ]


def _expression_request_issues(
    goal: ExpressionGoal,
    quantities: set[str],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    issues = [
        Diagnostic(
            path=(*path, "terms"),
            code="request_expression",
            message=f"Scalar quantity must precede use: {term.goal}.",
        )
        for term in goal.terms
        if term.goal not in quantities
    ]
    if goal.extrapolation is not None:
        issues.extend(
            Diagnostic(
                path=(*path, "extrapolation", name, "result"),
                code="request_extrapolation",
                message=f"Extrapolation source must precede use: {point.result}.",
            )
            for name, point in (
                ("low", goal.extrapolation.low),
                ("high", goal.extrapolation.high),
            )
            if point.result not in quantities
        )
    if goal.quantity.shape:
        issues.append(
            Diagnostic(
                path=(*path, "quantity"),
                code="request_expression",
                message="Expression goals require scalar quantities.",
            )
        )
    return tuple(issues)


def _register_goal(
    goal: Goal,
    geometries: set[str],
    quantities: set[str],
    calculations: set[str],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    issues: list[Diagnostic] = []
    if isinstance(goal, ProductGoal):
        if goal.calculation not in calculations:
            issues.append(
                Diagnostic(
                    path=(*path, "calculation"),
                    code="request_product",
                    message="A named product requires a preceding calculation goal.",
                )
            )
        if not product_quantity(goal.name).shape:
            quantities.add(goal.id)
    elif isinstance(goal, (CalculationGoal, SubsystemGoal)):
        if goal.geometry not in geometries:
            issues.append(
                Diagnostic(
                    path=(*path, "geometry"),
                    code="request_dependency",
                    message="Name an input or preceding optimization as geometry.",
                )
            )
        if isinstance(goal, SubsystemGoal) or goal.driver == "optimize":
            geometries.add(goal.id)
        if isinstance(goal, CalculationGoal):
            calculations.add(goal.id)
            if goal.driver not in {"gradient", "hessian"}:
                quantities.add(goal.id)
    else:
        issues.extend(_expression_request_issues(goal, quantities, path))
        quantities.add(goal.id)
    return tuple(issues)


def request_diagnostics(request: ScientificRequest) -> tuple[Diagnostic, ...]:
    """Return duplicate identities and invalid goal or relationship references."""
    if not any(isinstance(goal, CalculationGoal) for goal in request.goals):
        return (
            Diagnostic(
                path=("request", "goals"),
                code="request_calculation",
                message="A scientific calculation request must require a calculation.",
            ),
        )
    issues: list[Diagnostic] = []
    names = [item.name for item in request.molecules]
    if len(names) != len(set(names)):
        issues.append(
            Diagnostic(
                path=("request", "molecules"),
                code="request_identity",
                message="Molecular input identities must be unique.",
            )
        )
    known = set(names)
    geometries = set(names)
    quantities: set[str] = set()
    calculations: set[str] = set()
    for index, goal in enumerate(request.goals):
        path: tuple[str | int, ...] = ("request", "goals", index)
        if goal.id in known:
            issues.append(
                Diagnostic(
                    path=(*path, "id"),
                    code="request_identity",
                    message="Goal identities must be unique across inputs and goals.",
                )
            )
        issues.extend(_register_goal(goal, geometries, quantities, calculations, path))
        known.add(goal.id)
    for index, relation in enumerate(request.relations):
        issues.extend(
            requirement_reference_issues(
                relation,
                ("request", "relations", index),
                calculations,
                geometries,
                quantities,
            )
        )
    return tuple(issues)


def _translate_coordinate(
    requirement: CoordinateValue | CoordinateRange, geometry: str
) -> CoordinateValue | CoordinateRange:
    if isinstance(requirement, CoordinateValue):
        return CoordinateValue(
            geometry=geometry,
            coordinate=requirement.coordinate,
            tolerance=requirement.tolerance,
            value=requirement.value,
        )
    return CoordinateRange(
        geometry=geometry,
        coordinate=requirement.coordinate,
        tolerance=requirement.tolerance,
        lower=requirement.lower,
        upper=requirement.upper,
    )


def translate_requirement(
    requirement: Requirement,
    mapping: dict[str, str],
) -> Requirement | None:
    """Return a requirement with mapped identities, or null for an unknown reference."""
    if isinstance(requirement, (CoordinateValue, CoordinateRange)):
        return (
            _translate_coordinate(requirement, mapping[requirement.geometry])
            if requirement.geometry in mapping
            else None
        )
    if isinstance(requirement, UsesGeometry):
        return (
            UsesGeometry(
                calculation=mapping[requirement.calculation],
                geometry=mapping[requirement.geometry],
            )
            if requirement.calculation in mapping and requirement.geometry in mapping
            else None
        )
    if isinstance(requirement, EnergyFormula):
        if requirement.result not in mapping or any(
            term.result not in mapping for term in requirement.terms
        ):
            return None
        return EnergyFormula(
            result=mapping[requirement.result],
            terms=tuple(
                EnergyTerm(result=mapping[term.result], coefficient=term.coefficient)
                for term in requirement.terms
            ),
        )
    left, right = requirement.calculations
    if left not in mapping or right not in mapping:
        return None
    pair = (mapping[left], mapping[right])
    return (
        SameGeometry(calculations=pair)
        if isinstance(requirement, SameGeometry)
        else SameModel(calculations=pair)
    )


def _calculation_issues(
    goal: CalculationGoal,
    step: Calculation,
    mapping: dict[str, str],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    requested = translate_quantity(goal.quantity, mapping) if goal.quantity else None
    expected = Calculation(
        id=goal.id,
        driver=goal.driver,
        geometry=mapping[goal.geometry],
        model=goal.models[0],
        quantity=requested,
        sapt=goal.sapt,
    )
    comparisons = (
        ("driver", step.driver == goal.driver),
        ("model", step.model.identity in {item.identity for item in goal.models}),
        ("constraints", step.constraints == goal.constraints),
        (
            "quantity",
            primary_quantity(step) == primary_quantity(expected)
            and (requested is None or primary_quantity(step) == requested),
        ),
        ("derivative_route", step.derivative_route in goal.derivative_routes),
        ("properties", set(step.properties) == set(goal.properties)),
        ("analysis", step.analysis == goal.analysis),
        ("sapt", step.sapt == goal.sapt),
    )
    return tuple(
        Diagnostic(
            path=(*path, name),
            code="goal_contract",
            status="violated",
            message=f"Step {step.id}: goal {goal.id} requires a matching {name}.",
        )
        for name, valid in comparisons
        if not valid
    )


def translate_quantity(quantity: QuantityType, mapping: dict[str, str]) -> QuantityType:
    """Return the same quantity type with its named frame translated."""
    return QuantityType(
        meaning=quantity.meaning,
        unit=quantity.unit,
        shape=quantity.shape,
        frame=mapping.get(quantity.frame, quantity.frame) if quantity.frame else None,
        number_kind=quantity.number_kind,
    )


def _implementations(
    plan: Plan,
    request: ScientificRequest,
) -> tuple[dict[str, list[Step]], tuple[Diagnostic, ...]]:
    issues: list[Diagnostic] = []
    declarations: dict[str, list[Step]] = {}
    goals = {goal.id for goal in request.goals}
    for index, step in enumerate(plan.steps):
        for goal_id in step.satisfies:
            if goal_id not in goals:
                issues.append(
                    Diagnostic(
                        path=("steps", index, "satisfies"),
                        code="unknown_goal",
                        message=f"Unknown scientific goal: {goal_id}.",
                    )
                )
            declarations.setdefault(goal_id, []).append(step)
    return declarations, tuple(issues)


def _goal_requirements(
    goal: Goal,
    step: Step,
    mapping: dict[str, str],
    path: tuple[str | int, ...],
) -> tuple[tuple[Diagnostic, ...], tuple[Requirement, ...]]:
    if isinstance(goal, ProductGoal) and isinstance(step, Product):
        source = mapping.get(goal.calculation)
        requested = goal.quantity
        if requested is not None and requested.frame in mapping:
            requested = translate_quantity(requested, mapping)
        expected = requested or product_quantity(goal.name, frame=source)
        actual = step.quantity or product_quantity(step.name, frame=step.calculation)
        valid = (
            source == step.calculation
            and goal.name == step.name
            and expected == actual
            and goal.electronic_target == step.electronic_target
        )
        return (
            ()
            if valid
            else (
                Diagnostic(
                    path=path,
                    code="product_goal",
                    status="violated",
                    message="Product, quantity type, or calculation provenance "
                    "differs from the independent request.",
                ),
            )
        ), ()
    if isinstance(goal, SubsystemGoal) and isinstance(step, Subsystem):
        comparisons = (
            ("geometry", step.geometry == mapping.get(goal.geometry)),
            ("real_fragments", set(step.real_fragments) == set(goal.real_fragments)),
            ("state", step.state == goal.state),
        )
        return tuple(
            Diagnostic(
                path=(*path, name),
                code="subsystem_goal",
                status="violated",
                message=f"Subsystem {step.id} differs from goal {goal.id}: {name}.",
            )
            for name, valid in comparisons
            if not valid
        ), ()
    if isinstance(goal, CalculationGoal) and isinstance(step, Calculation):
        geometry = mapping.get(goal.geometry)
        if geometry is None:
            return (
                (
                    Diagnostic(
                        path=path,
                        code="goal_dependency",
                        status="violated",
                        message=f"Geometry goal is not covered: {goal.geometry}.",
                    ),
                ),
                (),
            )
        return (
            _calculation_issues(goal, step, mapping, path),
            (UsesGeometry(calculation=step.id, geometry=geometry),),
        )
    if isinstance(goal, ExpressionGoal) and isinstance(step, Combination):
        issues: list[Diagnostic] = []
        if step.extrapolation != translate_extrapolation(goal.extrapolation, mapping):
            issues.append(
                Diagnostic(
                    path=(*path, "extrapolation"),
                    code="goal_extrapolation",
                    status="violated",
                    message="Extrapolation recipe differs from independent intent.",
                )
            )
        requirements: tuple[Requirement, ...] = ()
        if any(term.goal not in mapping for term in goal.terms):
            issues.append(
                Diagnostic(
                    path=path,
                    code="goal_dependency",
                    status="violated",
                    message="An expression dependency is not covered.",
                )
            )
        else:
            requirements = (
                EnergyFormula(
                    result=step.id,
                    terms=tuple(
                        EnergyTerm(
                            result=mapping[term.goal],
                            coefficient=term.coefficient,
                        )
                        for term in goal.terms
                    ),
                ),
            )
        if step.quantity != translate_quantity(goal.quantity, mapping):
            issues.append(
                Diagnostic(
                    path=path,
                    code="goal_quantity",
                    status="violated",
                    message="Expression meaning or unit differs from the request.",
                )
            )
        return tuple(issues), requirements
    return (
        (
            Diagnostic(
                path=path,
                code="goal_operation",
                status="violated",
                message="Calculation and expression goals need matching operations.",
            ),
        ),
        (),
    )


def _cover_goal(
    goal: Goal,
    candidates: list[Step],
    mapping: dict[str, str],
    path: tuple[str | int, ...],
    permissions: dict[str, str | None],
) -> Coverage:
    if len(candidates) != 1:
        issue = Diagnostic(
            path=path,
            code="goal_coverage",
            status="violated",
            message=(
                f"Goal {goal.id} needs one implementing step; found {len(candidates)}."
            ),
        )
        coverage = GoalCoverage(
            goal=goal.id,
            steps=tuple(step.id for step in candidates),
            status="missing" if not candidates else "incompatible",
        )
        return Coverage((issue,), (coverage,), ())
    step = candidates[0]
    issues, requirements = _goal_requirements(goal, step, mapping, path)
    if isinstance(goal, CalculationGoal) and isinstance(step, Calculation):
        shared = tuple(name for name in step.satisfies if name in permissions)
        groups = {permissions[name] for name in shared}
        if len(shared) > 1 and (None in groups or len(groups) != 1):
            issues += (
                Diagnostic(
                    path=(*path, "reuse_group"),
                    code="unauthorized_reuse",
                    status="violated",
                    message="A shared call requires the same explicit reuse_group "
                    "on every calculation goal it addresses.",
                ),
            )
    coverage = GoalCoverage(
        goal=goal.id,
        steps=(step.id,),
        status="incompatible" if issues else "covered",
    )
    return Coverage(issues, (coverage,), requirements)


def derive_coverage(plan: Plan, request: ScientificRequest) -> Coverage:
    """Return mandatory request checks without trusting caller-supplied assertions."""
    issues = list(request_diagnostics(request))
    if issues:
        return Coverage(tuple(issues), (), ())
    if plan.molecules != request.molecules:
        issues.append(
            Diagnostic(
                path=("molecules",),
                code="request_inputs",
                status="violated",
                message="Plan molecular inputs differ from the independent request.",
            )
        )
    declarations, declaration_issues = _implementations(plan, request)
    issues.extend(declaration_issues)
    mapping = {item.name: item.name for item in request.molecules}
    mapping.update(
        {
            goal_id: steps[0].id
            for goal_id, steps in declarations.items()
            if len(steps) == 1
        }
    )
    coverage: list[GoalCoverage] = []
    requirements: list[Requirement] = []
    permissions = {
        goal.id: goal.reuse_group
        for goal in request.goals
        if isinstance(goal, CalculationGoal)
    }
    for index, goal in enumerate(request.goals):
        path: tuple[str | int, ...] = ("request", "goals", index)
        checked = _cover_goal(
            goal, declarations.get(goal.id, []), mapping, path, permissions
        )
        issues.extend(checked.diagnostics)
        coverage.extend(checked.goals)
        requirements.extend(checked.requirements)
    for index, relation in enumerate(request.relations):
        translated = translate_requirement(relation, mapping)
        if translated is None:
            issues.append(
                Diagnostic(
                    path=("request", "relations", index),
                    code="goal_relation",
                    status="violated",
                    message="A relation references an unknown or uncovered goal.",
                )
            )
        else:
            requirements.append(translated)
    return Coverage(tuple(issues), tuple(coverage), tuple(requirements))
