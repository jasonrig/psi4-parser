"""Expand counterpoise and many-body interactions into primitive goals."""

from itertools import combinations
from math import comb

from pydantic import Field

from psi4_parser.builder import ElectronicState, Fragment
from psi4_parser.formal._record import Record
from psi4_parser.formal.contracts import spin_coupling_allows
from psi4_parser.formal.intent import (
    CalculationGoal,
    ExpressionGoal,
    Goal,
    GoalTerm,
    SubsystemGoal,
)
from psi4_parser.formal.models import SameModel
from psi4_parser.formal.science import Model, QuantityType


class SubsystemState(Record):
    """Choose an explicit charge and coupled spin for a set of real fragments."""

    fragments: tuple[str, ...] = Field(
        min_length=1,
        description="Distinct real fragment names, in any order.",
    )
    state: ElectronicState = Field(
        description="Charge and multiplicity of this real-fragment combination."
    )


class FragmentStudy(Record):
    """Request a full-basis interaction expansion without fixed protocol presets."""

    id: str = Field(
        min_length=1,
        description="Prefix for subsystem, energy, and final interaction goal IDs.",
    )
    geometry: str = Field(
        min_length=1,
        description="Parent geometry identity, possibly from an optimization goal.",
    )
    fragments: tuple[Fragment, ...] = Field(
        min_length=2,
        description="Named parent fragments with explicit charges and multiplicities.",
    )
    models: tuple[Model, ...] = Field(
        min_length=1, description="Permitted common models, in preference order."
    )
    max_order: int | None = Field(
        default=None,
        ge=2,
        description="Highest body order; null requests the complete interaction.",
    )
    subsystem_states: tuple[SubsystemState, ...] = Field(
        default=(),
        description="Explicit states for ambiguous open-shell combinations.",
    )
    max_subsystems: int = Field(
        default=4095,
        ge=1,
        description="Maximum nonzero subsystem energy terms in this expansion.",
    )


class FragmentExpansion(Record):
    """Compose fragment interaction goals with other requested calculations."""

    goals: tuple[Goal, ...] = Field(
        description="Subsystems, calculations, and exact interaction expression."
    )
    relations: tuple[SameModel, ...] = Field(
        description="Mandatory common-model relationships among subsystem calculations."
    )
    target: str = Field(description="Goal ID of the final symbolic interaction energy.")


def _states(specification: FragmentStudy) -> dict[frozenset[str], ElectronicState]:
    names = {fragment.name for fragment in specification.fragments}
    if len(names) != len(specification.fragments):
        raise ValueError("Fragment names must be unique")
    explicit: dict[frozenset[str], ElectronicState] = {}
    for item in specification.subsystem_states:
        key = frozenset(item.fragments)
        if len(key) != len(item.fragments) or not key <= names or key in explicit:
            raise ValueError(
                "Subsystem state keys must be distinct sets of known fragments"
            )
        explicit[key] = item.state
    return explicit


def _state(
    fragments: tuple[Fragment, ...], explicit: dict[frozenset[str], ElectronicState]
) -> ElectronicState:
    states = [fragment.state for fragment in fragments]
    if any(state is None for state in states):
        raise ValueError(
            "Every real fragment needs an explicit charge and multiplicity"
        )
    resolved = [state for state in states if state is not None]
    charge = sum(state.charge for state in resolved)
    key = frozenset(fragment.name for fragment in fragments)
    if key in explicit:
        state = explicit[key]
        if state.charge != charge:
            raise ValueError(
                "Subsystem charge must equal the sum of real-fragment charges"
            )
        if not spin_coupling_allows(
            tuple(item.multiplicity for item in resolved), state.multiplicity
        ):
            raise ValueError(
                "Requested subsystem multiplicity cannot couple the fragment spins"
            )
        return state
    open_shells = [state for state in resolved if state.multiplicity != 1]
    if len(open_shells) > 1:
        raise ValueError(
            "Supply an explicit coupled state for open-shell fragment combinations"
        )
    return ElectronicState(
        charge=charge, multiplicity=open_shells[0].multiplicity if open_shells else 1
    )


def _coefficients(count: int, order: int) -> dict[int, int]:
    if count == order:
        return {1: -1, count: 1}
    # Sum connected increments of orders 2..order. Binomial cancellation
    # removes unused subsystem calculations before any goals are generated.
    return {
        1: (1 if (order - 1) % 2 == 0 else -1) * comb(count - 2, order - 1) - 1,
        **{
            size: (1 if (order - size) % 2 == 0 else -1)
            * comb(count - size - 1, order - size)
            for size in range(2, order + 1)
        },
    }


def fragment_expansion(specification: FragmentStudy) -> FragmentExpansion:
    """Return a counterpoise or truncated many-body interaction goal expansion.

    Every energy uses the complete parent basis. Complete order reduces to
    cluster energy minus monomer energies; intermediate terms cancel before
    construction. Truncated order sums connected increments through that order.
    The parent geometry must have a fixed frame and the named fragment layout.

    Args:
        specification: Fragment identities, states, common model choices, and bounds.

    Returns:
        Primitive goals, common-model requirements, and the symbolic target ID.

    Raises:
        ValueError: Names, states, requested order, or expansion bounds are invalid.
    """
    specification = FragmentStudy.model_validate(specification)
    count = len(specification.fragments)
    order = specification.max_order or count
    if order > count:
        raise ValueError("Many-body order cannot exceed the number of fragments")
    explicit = _states(specification)
    coefficients = {
        size: value for size, value in _coefficients(count, order).items() if value
    }
    required = sum(comb(count, size) for size in coefficients)
    if required > specification.max_subsystems:
        raise ValueError(
            "Fragment expansion exceeds max_subsystems; no impossibility is implied"
        )
    goals: list[Goal] = []
    energies: list[str] = []
    terms: list[GoalTerm] = []
    serial = 0
    for size, coefficient in sorted(coefficients.items()):
        for selected in combinations(specification.fragments, size):
            geometry = f"{specification.id}:subsystem:{serial}"
            energy = f"{specification.id}:energy:{serial}"
            state = _state(selected, explicit)
            goals.append(
                SubsystemGoal(
                    id=geometry,
                    geometry=specification.geometry,
                    real_fragments=tuple(fragment.name for fragment in selected),
                    state=state,
                )
            )
            goals.append(
                CalculationGoal(
                    id=energy,
                    driver="energy",
                    geometry=geometry,
                    models=specification.models,
                    quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                )
            )
            energies.append(energy)
            terms.append(GoalTerm(goal=energy, coefficient=coefficient))
            serial += 1
    target = f"{specification.id}:interaction"
    goals.append(
        ExpressionGoal(
            id=target,
            terms=tuple(terms),
            quantity=QuantityType(meaning="interaction_energy", unit="hartree"),
            reason=f"Full-basis interaction through {order}-body order",
        )
    )
    relations = tuple(
        SameModel(calculations=(energies[0], energy)) for energy in energies[1:]
    )
    return FragmentExpansion(goals=tuple(goals), relations=relations, target=target)
