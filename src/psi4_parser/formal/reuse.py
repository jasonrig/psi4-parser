"""Select explicitly permitted shared calls without weakening scientific intent."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import z3
from pydantic import Field

from psi4_parser.formal._record import Record
from psi4_parser.formal.contracts import primary_quantity
from psi4_parser.formal.intent import CalculationGoal, ScientificRequest, SubsystemGoal
from psi4_parser.formal.models import Calculation
from psi4_parser.formal.science import Driver

type ReusePreference = Literal["prefer", "avoid"]
"""Rank authorized call sharing without changing scientific alternatives."""


class PlanningPreferences(Record):
    """Choose shared or separate calls after the request's model and route order.

    Reuse always requires matching explicit groups in the independent request.
    Call counts describe construction, not execution cost or numerical accuracy.
    """

    calculation_reuse: ReusePreference = Field(
        default="prefer",
        description="Prefer fewer calls after the request's model and route order, "
        "or try independent calls first. Neither value grants sharing permission "
        "or changes scientific permissions.",
    )


class CalculationReuse(Record):
    """Locate one verified call that addresses multiple explicitly shareable goals."""

    calculation: str = Field(
        description="Implementing calculation ID in the accepted plan."
    )
    goals: tuple[str, ...] = Field(
        min_length=2, description="Calculation goals covered by this one call."
    )


@dataclass(frozen=True)
class _Signature:
    driver: Driver
    constraints: tuple[str, ...]
    properties: frozenset[str]
    analysis: str | None
    sapt: str | None
    quantity: str


@dataclass(frozen=True)
class _PossibleCall:
    goal: str
    geometry: frozenset[str]
    choices: frozenset[tuple[str, str]] | None


@dataclass(frozen=True)
class _SubsystemSignature:
    fragments: frozenset[str]
    state: str


@dataclass(frozen=True)
class _ReuseContract:
    key: tuple[str, _Signature] | _SubsystemSignature | None
    choices: frozenset[tuple[str, str]] | None
    produces_geometry: bool


def _metadata_ancestors(request: ScientificRequest) -> set[str]:
    producers = {
        goal.id: goal
        for goal in request.goals
        if isinstance(goal, SubsystemGoal)
        or (isinstance(goal, CalculationGoal) and goal.driver == "optimize")
    }
    pending = [
        goal.geometry
        for goal in request.goals
        if isinstance(goal, CalculationGoal) and goal.reuse_group is not None
    ]
    visited: set[str] = set()
    result: set[str] = set()
    while pending:
        name = pending.pop()
        if name in visited:
            continue
        visited.add(name)
        producer = producers.get(name)
        if producer is not None:
            pending.append(producer.geometry)
            if isinstance(producer, SubsystemGoal):
                result.add(name)
    return result


def _reuse_contract(
    goal: CalculationGoal | SubsystemGoal, active_metadata: set[str]
) -> _ReuseContract:
    if isinstance(goal, SubsystemGoal):
        key = _SubsystemSignature(
            frozenset(goal.real_fragments), goal.state.model_dump_json()
        )
        return _ReuseContract(key if goal.id in active_metadata else None, None, True)
    quantity = primary_quantity(
        Calculation(
            id=goal.id,
            driver=goal.driver,
            geometry=goal.geometry,
            model=goal.models[0],
            quantity=goal.quantity,
            sapt=goal.sapt,
        )
    )
    signature = _Signature(
        goal.driver,
        tuple(item.model_dump_json() for item in goal.constraints),
        frozenset(goal.properties),
        goal.analysis.model_dump_json() if goal.analysis else None,
        goal.sapt.model_dump_json() if goal.sapt else None,
        quantity.model_dump_json(exclude={"frame"}),
    )
    choices = frozenset(
        (model.identity, route)
        for model in goal.models
        for route in goal.derivative_routes
    )
    return _ReuseContract(
        (goal.reuse_group, signature) if goal.reuse_group is not None else None,
        choices,
        goal.driver == "optimize",
    )


def _compatible(left: _PossibleCall, right: _PossibleCall) -> bool:
    if not left.geometry & right.geometry:
        return False
    if left.choices is None or right.choices is None:
        return left.choices is None and right.choices is None
    return bool(left.choices & right.choices)


def reuse_targets(
    request: ScientificRequest, remaining_choices: int
) -> dict[str, tuple[str, ...]] | None:
    """Return bounded candidate roots; null means the encoding budget is exceeded."""
    geometries = {item.name: frozenset((item.name,)) for item in request.molecules}
    previous: dict[
        tuple[str, _Signature] | _SubsystemSignature, list[_PossibleCall]
    ] = {}
    targets: dict[str, tuple[str, ...]] = {}
    count = 0
    active_metadata = _metadata_ancestors(request)
    for goal in request.goals:
        if not isinstance(goal, (CalculationGoal, SubsystemGoal)):
            continue
        contract = _reuse_contract(goal, active_metadata)
        possible = _PossibleCall(goal.id, geometries[goal.geometry], contract.choices)
        roots: list[str] = []
        if contract.key is not None:
            bucket = previous.setdefault(contract.key, [])
            for prior in bucket:
                if _compatible(prior, possible):
                    roots.append(prior.goal)
                    if count + len(roots) + 1 > remaining_choices:
                        return None
            bucket.append(possible)
        targets[goal.id] = tuple(roots)
        if roots:
            count += len(roots) + 1
        if contract.produces_geometry:
            geometries[goal.id] = frozenset((goal.id, *roots))
    return targets


@dataclass(frozen=True)
class _SelectionSymbols:
    """Share one private solver context and the selected scientific variables."""

    context: z3.Context
    solver: z3.Solver
    models: dict[str, z3.SeqRef]
    routes: dict[str, z3.SeqRef]


@dataclass(frozen=True)
class _ReuseGroup:
    goal: str
    targets: tuple[str, ...]
    symbols: tuple[z3.BoolRef, ...]
    calculation: bool


class _ReuseSelection:
    """Encode finite call identities, including dependencies on shared optimizations."""

    def __init__(
        self,
        request: ScientificRequest,
        targets: dict[str, tuple[str, ...]],
        selection: _SelectionSymbols,
    ) -> None:
        self.selection = selection
        self.groups: list[_ReuseGroup] = []
        self.roots = {
            goal.id: z3.String(f"goal_{index}_call", selection.context)
            if targets[goal.id]
            else z3.StringVal(goal.id, selection.context)
            for index, goal in enumerate(request.goals)
            if isinstance(goal, (CalculationGoal, SubsystemGoal))
        }
        calculations = {
            goal.id: goal
            for goal in request.goals
            if isinstance(goal, (CalculationGoal, SubsystemGoal))
        }
        for index, goal in enumerate(calculations.values()):
            if not targets[goal.id]:
                continue
            choices = (goal.id, *targets[goal.id])
            symbols = tuple(
                z3.Bool(f"call_{index}_root_{rank}", selection.context)
                for rank in range(len(choices))
            )
            self.groups.append(
                _ReuseGroup(
                    goal.id, choices, symbols, isinstance(goal, CalculationGoal)
                )
            )
            selection.solver.add(z3.Or(*symbols), z3.AtMost(*symbols, 1))
            for target, symbol in zip(choices, symbols, strict=True):
                conditions = [
                    self._equal(
                        self.roots[goal.id], z3.StringVal(target, selection.context)
                    )
                ]
                if target != goal.id:
                    other = calculations[target]
                    conditions.extend(
                        (
                            self._equal(
                                self.roots[target],
                                z3.StringVal(target, selection.context),
                            ),
                            self._equal(
                                self._geometry(goal.geometry),
                                self._geometry(other.geometry),
                            ),
                        )
                    )
                    if isinstance(goal, CalculationGoal):
                        conditions.extend(
                            (
                                self._equal(
                                    selection.models[goal.id], selection.models[target]
                                ),
                                self._equal(
                                    selection.routes[goal.id], selection.routes[target]
                                ),
                            )
                        )
                selection.solver.add(z3.Implies(symbol, z3.And(*conditions)))

    @staticmethod
    def _equal(left: z3.SeqRef, right: z3.SeqRef) -> z3.BoolRef:
        return z3.Not(z3.Distinct(left, right))

    def _geometry(self, name: str) -> z3.SeqRef:
        return self.roots.get(name, z3.StringVal(name, self.selection.context))

    def _feasible(
        self, condition: z3.BoolRef, check: Callable[[], z3.CheckSatResult]
    ) -> bool:
        self.selection.solver.push()
        try:
            self.selection.solver.add(condition)
            return check() == z3.sat
        finally:
            self.selection.solver.pop()

    def select(
        self,
        check: Callable[[], z3.CheckSatResult],
        preferences: PlanningPreferences,
    ) -> tuple[dict[str, str], tuple[z3.BoolRef, ...]]:
        """Return call identities and selected symbols using bounded solver checks."""
        independent = tuple(
            group.symbols[0] for group in self.groups if group.calculation
        )
        if independent and preferences.calculation_reuse == "prefer":
            low, high = 0, len(independent)
            while low < high:
                middle = (low + high) // 2
                if self._feasible(z3.AtMost(*independent, middle), check):
                    high = middle
                else:
                    low = middle + 1
            self.selection.solver.add(z3.AtMost(*independent, low))
        implementation = {name: name for name in self.roots}
        selected: list[z3.BoolRef] = []
        for group in self.groups:
            indices = tuple(range(len(group.targets)))
            if preferences.calculation_reuse == "prefer":
                indices = (*indices[1:], 0)
            for index in indices:
                symbol = group.symbols[index]
                if self._feasible(symbol, check):
                    self.selection.solver.add(symbol)
                    selected.append(symbol)
                    implementation[group.goal] = group.targets[index]
                    break
        return implementation, tuple(selected)
