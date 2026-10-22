"""Construct bounded calculation plans from independent scientific requests."""

from dataclasses import dataclass
from time import monotonic
from typing import Literal

import z3
from pydantic import Field

from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import CapabilityCatalog, DerivativeRoute
from psi4_parser.formal.catalogs import load_catalog
from psi4_parser.formal.coverage import request_diagnostics, translate_quantity
from psi4_parser.formal.extrapolation_models import translate_extrapolation
from psi4_parser.formal.intent import (
    CalculationGoal,
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
    Limits,
    Plan,
    Product,
    Report,
    Requirement,
    SameModel,
    Step,
    Subsystem,
    UsesGeometry,
)
from psi4_parser.formal.reuse import (
    CalculationReuse,
    PlanningPreferences,
    _ReuseSelection,
    _SelectionSymbols,
    reuse_targets,
)
from psi4_parser.formal.science import Model
from psi4_parser.formal.verification import verify


class SearchLimits(Record):
    """Bound finite model selection separately from independent verification."""

    max_candidates: int = Field(
        default=128, ge=1, description="Maximum complete candidate plans checked."
    )
    max_choices: int = Field(
        default=10000,
        ge=1,
        description="Maximum finite model, route, and call-reuse alternatives encoded.",
    )
    max_solver_checks: int = Field(
        default=2048,
        ge=1,
        description="Maximum selection-solver calls across the search.",
    )
    timeout_ms: int = Field(
        default=30000,
        ge=1,
        description="Total planning budget, checked between bounded solver calls.",
    )
    verification: Limits = Field(
        default_factory=Limits,
        description="Limits for independent candidate verification.",
    )


class ChosenModel(Record):
    """Explain a model choice within the alternatives explicitly permitted by intent."""

    goal: str = Field(
        description="Scientific calculation goal addressed by this choice."
    )
    model: Model = Field(description="Selected permitted scientific model.")
    derivative_route: DerivativeRoute = Field(
        description="Selected permitted derivative route."
    )
    preference_rank: int = Field(
        ge=0, description="Zero-based model/route rank in the request's order."
    )


class Proposal(Record):
    """Return a verified plan or a precise account of a finite search's limits."""

    status: Literal[
        "constructed", "invalid", "unknown", "exhausted", "no_candidate"
    ] = Field(
        description="Outcome within the finite alternatives declared by the request."
    )
    plan: Plan | None = Field(
        default=None, description="Accepted plan; null unless independently verified."
    )
    report: Report | None = Field(
        default=None,
        description="Accepted or last rejected candidate's verification report.",
    )
    attempts: int = Field(
        default=0, ge=0, description="Complete candidate plans independently checked."
    )
    choices: tuple[ChosenModel, ...] = Field(
        default=(), description="Permitted alternatives selected for the returned plan."
    )
    diagnostics: tuple[Diagnostic, ...] = Field(
        default=(),
        description="Invalid intent, missing evidence, or search-limit explanation.",
    )
    selection_smt2: str = Field(
        default="",
        description="Finite model, route, and call-reuse selection constraints.",
    )
    preferences: PlanningPreferences | None = Field(
        default=None,
        description="Applied implementation preferences; null in older records.",
    )
    reuses: tuple[CalculationReuse, ...] = Field(
        default=(), description="Verified shared calls in the accepted plan."
    )
    last_candidate: Plan | None = Field(
        default=None,
        description="Last independently checked rejected plan; null if none or "
        "when an accepted plan is returned. Diagnostic paths refer to this plan.",
    )


def _candidate(
    request: ScientificRequest,
    choices: tuple[ChosenModel, ...],
    implementations: dict[str, str],
) -> Plan:
    selected = {item.goal: item for item in choices}
    mapping = {item.name: item.name for item in request.molecules}
    mapping.update(
        {goal.id: implementations.get(goal.id, goal.id) for goal in request.goals}
    )
    addressed: dict[str, list[str]] = {}
    for goal in request.goals:
        if isinstance(goal, (CalculationGoal, SubsystemGoal)):
            addressed.setdefault(implementations[goal.id], []).append(goal.id)
    steps: list[Step] = []
    requirements: list[Requirement] = []
    for goal in request.goals:
        if isinstance(goal, ProductGoal):
            steps.append(
                Product(
                    id=goal.id,
                    calculation=mapping[goal.calculation],
                    name=goal.name,
                    electronic_target=goal.electronic_target,
                    quantity=translate_quantity(goal.quantity, mapping)
                    if goal.quantity
                    else None,
                    satisfies=(goal.id,),
                )
            )
            continue
        if isinstance(goal, SubsystemGoal):
            if implementations[goal.id] != goal.id:
                continue
            steps.append(
                Subsystem(
                    id=goal.id,
                    geometry=mapping[goal.geometry],
                    real_fragments=goal.real_fragments,
                    state=goal.state,
                    satisfies=tuple(addressed[goal.id]),
                )
            )
            continue
        if isinstance(goal, CalculationGoal):
            if implementations[goal.id] != goal.id:
                continue
            choice = selected[goal.id]
            steps.append(
                Calculation(
                    id=goal.id,
                    driver=goal.driver,
                    geometry=mapping[goal.geometry],
                    model=choice.model,
                    constraints=goal.constraints,
                    quantity=translate_quantity(goal.quantity, mapping)
                    if goal.quantity
                    else None,
                    derivative_route=choice.derivative_route,
                    properties=goal.properties,
                    analysis=goal.analysis,
                    sapt=goal.sapt,
                    satisfies=tuple(addressed[goal.id]),
                )
            )
            requirements.append(
                UsesGeometry(calculation=goal.id, geometry=mapping[goal.geometry])
            )
        else:
            terms = tuple(
                EnergyTerm(result=mapping[term.goal], coefficient=term.coefficient)
                for term in goal.terms
            )
            steps.append(
                Combination(
                    id=goal.id,
                    terms=terms,
                    quantity=translate_quantity(goal.quantity, mapping),
                    extrapolation=translate_extrapolation(goal.extrapolation, mapping),
                    satisfies=(goal.id,),
                )
            )
            requirements.append(EnergyFormula(result=goal.id, terms=terms))
    return Plan(
        molecules=request.molecules,
        steps=tuple(steps),
        requirements=tuple(requirements),
    )


class _BudgetExceededError(Exception):
    pass


class _SelectionUnknownError(Exception):
    pass


@dataclass(frozen=True)
class _Group:
    choices: tuple[ChosenModel, ...]
    symbols: tuple[z3.BoolRef, ...]


@dataclass(frozen=True)
class _Selected:
    choices: tuple[ChosenModel, ...]
    implementations: dict[str, str]
    symbols: tuple[z3.BoolRef, ...]
    model_symbols: tuple[z3.BoolRef, ...]
    query: str


class _Selection:
    def __init__(
        self,
        request: ScientificRequest,
        limits: SearchLimits,
        preferences: PlanningPreferences,
        targets: dict[str, tuple[str, ...]],
    ) -> None:
        self.limits = limits
        self.started = monotonic()
        self.checks = 0
        self.context = z3.Context()
        self.solver = z3.Solver(ctx=self.context)
        self.groups: list[_Group] = []
        self.preferences = preferences
        model_names: dict[str, z3.SeqRef] = {}
        route_names: dict[str, z3.SeqRef] = {}
        for index, goal in enumerate(request.goals):
            if not isinstance(goal, CalculationGoal):
                continue
            choices = tuple(
                ChosenModel(
                    goal=goal.id,
                    model=model,
                    derivative_route=route,
                    preference_rank=rank,
                )
                for rank, (model, route) in enumerate(
                    (model, route)
                    for model in goal.models
                    for route in goal.derivative_routes
                )
            )
            symbols = tuple(
                z3.Bool(f"goal_{index}_choice_{rank}", self.context)
                for rank in range(len(choices))
            )
            self.groups.append(_Group(choices, symbols))
            self.solver.add(z3.Or(*symbols), z3.AtMost(*symbols, 1))
            model_name = z3.String(f"goal_{index}_model", self.context)
            model_names[goal.id] = model_name
            route_name = z3.String(f"goal_{index}_route", self.context)
            route_names[goal.id] = route_name
            self.solver.add(
                *(
                    z3.Implies(
                        symbol,
                        z3.Not(
                            z3.Distinct(
                                model_name,
                                z3.StringVal(choice.model.identity, self.context),
                            )
                        ),
                    )
                    for symbol, choice in zip(symbols, choices, strict=True)
                )
            )
            self.solver.add(
                *(
                    z3.Implies(
                        symbol,
                        z3.Not(
                            z3.Distinct(
                                route_name,
                                z3.StringVal(choice.derivative_route, self.context),
                            )
                        ),
                    )
                    for symbol, choice in zip(symbols, choices, strict=True)
                )
            )
        for relation in request.relations:
            if isinstance(relation, SameModel):
                left, right = relation.calculations
                if left in model_names and right in model_names:
                    self.solver.add(
                        z3.Not(z3.Distinct(model_names[left], model_names[right]))
                    )
        self.reuse = _ReuseSelection(
            request,
            targets,
            _SelectionSymbols(self.context, self.solver, model_names, route_names),
        )

    def remaining_ms(self) -> int:
        return max(0, self.limits.timeout_ms - int((monotonic() - self.started) * 1000))

    def check(self) -> z3.CheckSatResult:
        remaining = self.remaining_ms()
        if not remaining or self.checks >= self.limits.max_solver_checks:
            raise _BudgetExceededError
        self.checks += 1
        self.solver.set(
            timeout=min(remaining, self.limits.verification.timeout_ms),
            rlimit=self.limits.verification.resource_limit,
        )
        result = self.solver.check()
        if result == z3.unknown:
            raise _SelectionUnknownError(self.solver.reason_unknown())
        return result

    def select(
        self,
    ) -> _Selected | None:
        if self.check() == z3.unsat:
            return None
        self.solver.push()
        try:
            choices, selected = self._select_models()
            implementations, reuse_symbols = self.reuse.select(
                self.check, self.preferences
            )
            return _Selected(
                choices,
                implementations,
                (*selected, *reuse_symbols),
                selected,
                self.solver.to_smt2(),
            )
        finally:
            self.solver.pop()

    def _select_models(self) -> tuple[tuple[ChosenModel, ...], tuple[z3.BoolRef, ...]]:
        choices: list[ChosenModel] = []
        selected: list[z3.BoolRef] = []
        for group in self.groups:
            for choice, symbol in zip(group.choices, group.symbols, strict=True):
                self.solver.push()
                try:
                    self.solver.add(symbol)
                    feasible = self.check() == z3.sat
                finally:
                    self.solver.pop()
                if feasible:
                    self.solver.add(symbol)
                    choices.append(choice)
                    selected.append(symbol)
                    break
        return tuple(choices), tuple(selected)


def _no_candidate(
    selection: _Selection,
    last: Report | None,
    last_plan: Plan | None,
    attempts: int,
    undecided: bool,
) -> Proposal:
    diagnostics = last.diagnostics if last else ()
    if last is not None:
        diagnostics += tuple(
            Diagnostic(
                path=item.path,
                code="candidate_obligation",
                status=item.status,
                message=item.message,
            )
            for item in last.obligations
            if item.status != "proved"
        )
    if not diagnostics:
        diagnostics = (
            Diagnostic(
                path=("request", "relations"),
                code="finite_choices",
                status="violated",
                message="No declared alternative satisfies the selection constraints.",
            ),
        )
    return Proposal(
        preferences=selection.preferences,
        status="unknown" if undecided else "no_candidate",
        report=last,
        last_candidate=last_plan,
        attempts=attempts,
        diagnostics=diagnostics,
        selection_smt2=selection.solver.to_smt2(),
    )


def _search(
    request: ScientificRequest, catalog: CapabilityCatalog, selection: _Selection
) -> Proposal:
    limits, preferences = selection.limits, selection.preferences
    last: Report | None = None
    last_plan: Plan | None = None
    attempts = 0
    undecided = False
    try:
        while attempts < limits.max_candidates:
            selected = selection.select()
            if selected is None:
                return _no_candidate(selection, last, last_plan, attempts, undecided)
            choices = selected.choices
            plan = _candidate(request, choices, selected.implementations)
            budget = limits.verification
            remaining = selection.remaining_ms()
            if not remaining:
                raise _BudgetExceededError
            bounded = Limits(
                timeout_ms=budget.timeout_ms,
                resource_limit=budget.resource_limit,
                max_steps=budget.max_steps,
                max_obligations=budget.max_obligations,
                total_timeout_ms=min(budget.total_timeout_ms, remaining),
            )
            last = verify(plan, request=request, catalog=catalog, limits=bounded)
            last_plan = plan
            attempts += 1
            if last.request_complete:
                return Proposal(
                    preferences=preferences,
                    status="constructed",
                    plan=plan,
                    report=last,
                    choices=choices,
                    attempts=attempts,
                    selection_smt2=selected.query,
                    reuses=tuple(
                        CalculationReuse(calculation=step.id, goals=step.satisfies)
                        for step in plan.steps
                        if isinstance(step, Calculation) and len(step.satisfies) > 1
                    ),
                )
            undecided |= last.status == "unknown" or last.capability_status == "unknown"
            # A permitted merge preserves model, route, molecule layout, settings,
            # and every named product. It cannot repair a capability finding.
            symbols = (
                selected.model_symbols
                if last.capability_status not in {None, "supported"}
                else selected.symbols
            )
            selection.solver.add(z3.Not(z3.And(*symbols)))
        if selection.check() == z3.unsat:
            return _no_candidate(selection, last, last_plan, attempts, undecided)
        raise _BudgetExceededError
    except _BudgetExceededError:
        return Proposal(
            preferences=preferences,
            status="exhausted",
            report=last,
            last_candidate=last_plan,
            attempts=attempts,
            diagnostics=(
                Diagnostic(
                    path=(),
                    code="search_budget",
                    status="unknown",
                    message="No accepted plan found within the declared search bounds.",
                ),
            ),
            selection_smt2=selection.solver.to_smt2(),
        )
    except _SelectionUnknownError as error:
        return Proposal(
            preferences=preferences,
            status="unknown",
            report=last,
            last_candidate=last_plan,
            attempts=attempts,
            diagnostics=(
                Diagnostic(
                    path=(),
                    code="selection_unknown",
                    status="unknown",
                    message=str(error),
                ),
            ),
            selection_smt2=selection.solver.to_smt2(),
        )


def propose(
    request: ScientificRequest,
    catalog: CapabilityCatalog | None = None,
    *,
    limits: SearchLimits | None = None,
    preferences: PlanningPreferences | None = None,
) -> Proposal:
    """Return a checked plan using only models and routes permitted by the request.

    Args:
        request: Independent finite scientific work, input molecules, and alternatives.
        catalog: Scientific/input contracts; omission uses the shared Psi4 catalog.
        limits: Search and verification bounds; null uses default bounds.
        preferences: Call-sharing preference after the request's model and route
            order; null prefers fewer explicitly authorized calls.

    Returns:
        A construction proposal without executing or inspecting calculation results.
    """
    request = ScientificRequest.model_validate(request)
    catalog = (
        CapabilityCatalog.model_validate(catalog)
        if catalog is not None
        else load_catalog()
    )
    configuration = SearchLimits.model_validate(limits) if limits else SearchLimits()
    implementation_preferences = (
        PlanningPreferences.model_validate(preferences)
        if preferences
        else PlanningPreferences()
    )
    problems = request_diagnostics(request)
    if problems:
        return Proposal(
            status="invalid",
            diagnostics=problems,
            preferences=implementation_preferences,
        )
    count = sum(
        len(goal.models) * len(goal.derivative_routes)
        for goal in request.goals
        if isinstance(goal, CalculationGoal)
    )
    if (
        count > configuration.max_choices
        or len(request.goals) > configuration.verification.max_steps
    ):
        return Proposal(
            preferences=implementation_preferences,
            status="exhausted",
            diagnostics=(
                Diagnostic(
                    path=("request", "goals"),
                    code="search_budget",
                    status="unknown",
                    message="Finite choices exceed the construction budget.",
                ),
            ),
        )
    targets = reuse_targets(request, configuration.max_choices - count)
    if targets is None:
        return Proposal(
            status="exhausted",
            preferences=implementation_preferences,
            diagnostics=(
                Diagnostic(
                    path=("request", "goals"),
                    code="search_budget",
                    status="unknown",
                    message="Finite reuse alternatives exceed the construction budget.",
                ),
            ),
        )
    return _search(
        request,
        catalog,
        _Selection(request, configuration, implementation_preferences, targets),
    )
