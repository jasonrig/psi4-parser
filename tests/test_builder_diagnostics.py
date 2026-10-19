"""Locate builder compilation failures within a job specification."""

import pytest

from psi4_parser.builder import (
    CompilationError,
    Expression,
    Molecule,
    Python,
    Reference,
    call,
    compose,
    distance,
    energy,
    freeze,
    lower_job,
    molecule,
    optimize,
    options,
)


def test_missing_reference_identifies_component_and_field() -> None:
    """Identify the exact method field whose reference has no declaration."""
    job = compose(options(basis="sto-3g"), energy(Reference(name="missing")))

    with pytest.raises(ValueError, match=r"components\[1\]\.method.*missing"):
        lower_job(job)


def test_nested_argument_error_keeps_its_full_path() -> None:
    """Retain the path through a mapping and a sequence to a missing reference."""
    job = compose(call("print", settings={"values": [Reference(name="missing")]}))

    with pytest.raises(CompilationError) as failure:
        lower_job(job)

    diagnostic = failure.value.diagnostics[0]
    assert diagnostic.path == (
        "components",
        0,
        "kwargs",
        0,
        "value",
        "entries",
        0,
        "value",
        "items",
        0,
    )
    assert diagnostic.line is None
    assert "missing" in diagnostic.message


def test_constraint_error_locates_unknown_atom() -> None:
    """Attach constraint-selection errors to their coordinate atom IDs."""
    declaration = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
    job = compose(
        declaration,
        optimize(
            "scf",
            molecule=declaration.ref,
            constraints=(freeze(distance("a1", "missing")),),
        ),
    )

    with pytest.raises(CompilationError) as failure:
        lower_job(job)

    assert failure.value.diagnostics[0].path == (
        "components",
        1,
        "constraints",
        0,
        "coordinate",
        "atoms",
    )
    assert "missing" in str(failure.value)


def test_python_syntax_failure_has_component_and_emitted_line() -> None:
    """Locate contextual Python failures while retaining parser coordinates."""
    job = compose(Python(source="x = 1"), Python(source="return x"))

    with pytest.raises(CompilationError) as failure:
        lower_job(job)

    diagnostic = failure.value.diagnostics[0]
    assert diagnostic.path == ("components", 1, "source")
    assert diagnostic.line == 3
    assert diagnostic.column is not None


def test_invalid_expression_has_a_method_field_path() -> None:
    """Convert expression-parser errors to structured compilation diagnostics."""
    with pytest.raises(CompilationError) as failure:
        lower_job(compose(energy(Expression(source="("))))

    assert failure.value.diagnostics[0].path == ("components", 0, "method")


def test_native_option_error_locates_assignment_value() -> None:
    """Explain invalid native values at their option assignment."""
    with pytest.raises(CompilationError) as failure:
        lower_job(compose(options(basis=None)))

    assert failure.value.diagnostics[0].path == (
        "components",
        0,
        "assignments",
        0,
        "value",
    )


def test_constraint_conflict_identifies_the_raw_option() -> None:
    """Locate a raw local option that conflicts with a typed constraint."""
    declaration = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
    step = optimize(
        "scf",
        molecule=declaration.ref,
        constraints=(freeze(distance("a1", "a2")),),
        local_options=(options(modules=("optking",), frozen_distance="1 2"),),
    )

    with pytest.raises(CompilationError) as failure:
        lower_job(compose(declaration, step))

    assert failure.value.diagnostics[0].path == (
        "components",
        1,
        "local_options",
        0,
        "assignments",
        0,
        "key",
    )
