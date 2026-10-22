"""Check fragment formulas against independent inclusion-exclusion identities."""

from collections import Counter
from itertools import combinations, product

import pytest

from psi4_parser.builder import ElectronicState, Fragment
from psi4_parser.formal import (
    CalculationGoal,
    ExpressionGoal,
    FragmentStudy,
    Model,
    SubsystemGoal,
    SubsystemState,
    fragment_expansion,
)
from psi4_parser.formal.contracts import spin_coupling_allows


@pytest.mark.parametrize(
    ("count", "order"),
    [(count, order) for count in range(2, 6) for order in range(2, count + 1)],
)
def test_fragment_coefficients_match_independent_connected_increments(
    count: int, order: int
) -> None:
    """Compare simplified energy terms with explicit connected-increment enumeration.

    Args:
        count: Number of fragments in a small independent reference expansion.
        order: Highest connected many-body order to include.
    """
    names = tuple(f"F{index}" for index in range(count))
    fragments = tuple(
        Fragment(name=name, state=ElectronicState(charge=0, multiplicity=1))
        for name in names
    )
    study = FragmentStudy(
        id="interaction",
        geometry="cluster",
        fragments=fragments,
        models=(Model(method="scf", basis="sto-3g", reference="rhf"),),
        max_order=order,
    )
    expected: Counter[frozenset[str]] = Counter()
    for size in range(2, order + 1):
        for cluster in combinations(names, size):
            for subset_size in range(1, size + 1):
                for subset in combinations(cluster, subset_size):
                    expected[frozenset(subset)] += (
                        1 if (size - subset_size) % 2 == 0 else -1
                    )
    expected = Counter(
        {key: coefficient for key, coefficient in expected.items() if coefficient}
    )

    expanded = fragment_expansion(study)

    geometries = {
        goal.id: frozenset(goal.real_fragments)
        for goal in expanded.goals
        if isinstance(goal, SubsystemGoal)
    }
    energies = {
        goal.id: geometries[goal.geometry]
        for goal in expanded.goals
        if isinstance(goal, CalculationGoal)
    }
    expression = expanded.goals[-1]
    assert isinstance(expression, ExpressionGoal)
    actual: Counter[frozenset[str]] = Counter()
    for term in expression.terms:
        assert isinstance(term.coefficient, int)
        actual[energies[term.goal]] += term.coefficient
    assert actual == expected
    assert len(energies) == len(expected)
    assert len(expanded.relations) == len(energies) - 1


def test_ambiguous_open_shell_coupling_requires_a_choice() -> None:
    """Require an explicit coupled spin rather than summing fragment multiplicities."""
    fragments = tuple(
        Fragment(name=name, state=ElectronicState(charge=0, multiplicity=2))
        for name in ("A", "B")
    )
    model = Model(method="scf", basis="sto-3g", reference="uhf")
    study = FragmentStudy(
        id="cp", geometry="dimer", fragments=fragments, models=(model,)
    )

    with pytest.raises(ValueError, match="explicit coupled state"):
        fragment_expansion(study)

    chosen = FragmentStudy(
        id="cp",
        geometry="dimer",
        fragments=fragments,
        models=(model,),
        subsystem_states=(
            SubsystemState(
                fragments=("A", "B"), state=ElectronicState(charge=0, multiplicity=1)
            ),
        ),
    )
    assert fragment_expansion(chosen).target == "cp:interaction"


def test_expansion_bound_is_checked_before_constructing_subsets() -> None:
    """Refuse an oversized finite expansion with an actionable bound diagnostic."""
    fragments = tuple(
        Fragment(name=str(index), state=ElectronicState(charge=0, multiplicity=1))
        for index in range(8)
    )
    study = FragmentStudy(
        id="large",
        geometry="cluster",
        fragments=fragments,
        models=(Model(method="scf", basis="sto-3g", reference="rhf"),),
        max_order=3,
        max_subsystems=10,
    )

    with pytest.raises(ValueError, match="max_subsystems"):
        fragment_expansion(study)


def test_spin_coupling_matches_independent_enumeration() -> None:
    """Compare bounded spin-addition sets and avoid enumeration for very large spins."""
    for count in range(1, 5):
        for multiplicities in product(range(1, 5), repeat=count):
            allowed = {0}
            for multiplicity in multiplicities:
                spin = multiplicity - 1
                allowed = {
                    value
                    for left in allowed
                    for value in range(abs(left - spin), left + spin + 1, 2)
                }
            for overall in range(1, 15):
                assert spin_coupling_allows(multiplicities, overall) == (
                    overall - 1 in allowed
                )
    assert spin_coupling_allows((1000000000, 1000000000), 1)
