"""Compose structured control flow from ordinary builder components."""

import ast
import os
import subprocess
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter

from psi4_parser import format_source
from psi4_parser import job as native
from psi4_parser.builder import (
    CompilationError,
    ExceptionHandler,
    Expression,
    JobSpec,
    Molecule,
    Python,
    Reference,
    TryBlock,
    WithBlock,
    WithItem,
    call,
    compose,
    distance,
    energy,
    for_each,
    freeze,
    if_else,
    lower_job,
    molecule,
    optimize,
    options,
    render_job,
    reorder_atoms,
    while_loop,
    with_context,
)

_PYTHON = os.environ.get("PSI4_PYTHON")
_JSON = TypeAdapter(JsonValue)


def test_loop_body_is_serializable_and_uses_its_target() -> None:
    """Emit a loop whose method reference is bound by the loop header."""
    job = JobSpec.model_validate_json(
        '{"components":[{"kind":"for","target":"method",'
        '"iterable":{"kind":"sequence","items":['
        '{"kind":"literal","value":"scf"},{"kind":"literal","value":"mp2"}]},'
        '"body":{"components":[{"kind":"calculation","driver":"energy",'
        '"method":{"kind":"reference","name":"method"}}]}}]}'
    )

    source = render_job(job)

    assert "for method in ['scf', 'mp2']:" in source
    assert "    energy(method)" in source
    assert JobSpec.model_validate_json(job.model_dump_json()) == job


def test_only_exhaustive_branches_export_new_bindings() -> None:
    """Expose a result after both alternatives assign it, but reject a missing path."""
    left = compose(call("int", 1, assign="result"))
    right = compose(call("int", 2, assign="result"))
    complete = compose(
        if_else(True, left, otherwise=right), call("print", Reference(name="result"))
    )

    source = render_job(complete)

    assert "else:" in source
    assert "print)(result)" in source
    with pytest.raises(CompilationError, match=r"components\[1\].*result"):
        render_job(
            compose(if_else(True, left), call("print", Reference(name="result")))
        )


def test_loop_outputs_require_prior_bindings() -> None:
    """Permit updates of a prior result without promising that a loop executes."""
    body = compose(call("int", Reference(name="item"), assign="result"))
    loop = for_each("item", [], body)

    with pytest.raises(CompilationError, match="result"):
        render_job(compose(loop, call("print", Reference(name="result"))))
    with pytest.raises(CompilationError, match="item"):
        render_job(compose(loop, call("print", Reference(name="item"))))

    initialized = compose(
        Python(source="result = 0", provides=("result",)),
        loop,
        call("print", Reference(name="result")),
    )
    assert "result = (int)(item)" in render_job(initialized)


def test_context_suppression_does_not_export_body_assignments() -> None:
    """Account for suppressed exceptions and partially entered context lists."""
    body = compose(call("int", 1, assign="result"))
    block = with_context(Expression(source="nullcontext(1)"), body, target="entered")
    assert "with (nullcontext(1)) as entered:" in render_job(
        compose(block, call("print", Reference(name="entered")))
    )
    with pytest.raises(CompilationError, match="result"):
        render_job(compose(block, call("print", Reference(name="result"))))

    multiple = WithBlock(
        items=(
            WithItem(context=Expression(source="suppress(Exception)"), target="first"),
            WithItem(context=Expression(source="nullcontext(2)"), target="second"),
        ),
        body=JobSpec(),
    )
    with pytest.raises(CompilationError, match="second"):
        render_job(compose(multiple, call("print", Reference(name="second"))))


def test_suppressed_context_target_unpacking_is_not_definite() -> None:
    """Allow a context manager to suppress a failed tuple-target assignment."""
    block = with_context(
        Expression(source="suppress(Exception)"), JobSpec(), target=("left", "right")
    )

    with pytest.raises(CompilationError, match="left"):
        render_job(compose(block, call("print", Reference(name="left"))))


def test_try_bindings_handlers_and_cleanup_follow_reachable_paths() -> None:
    """Expose results assigned on every handled exit and always-run cleanup."""
    block = TryBlock(
        body=compose(call("int", 1, assign="result")),
        handlers=(
            ExceptionHandler(
                exception=Expression(source="ValueError"),
                name="error",
                body=compose(call("int", 2, assign="result")),
            ),
        ),
        finally_body=compose(call("int", 3, assign="cleaned")),
    )
    source = render_job(
        compose(
            block, call("print", Reference(name="result"), Reference(name="cleaned"))
        )
    )
    assert "except (ValueError) as error:" in source
    assert "finally:" in source
    with pytest.raises(CompilationError, match="error"):
        render_job(compose(block, call("print", Reference(name="error"))))

    unsafe_cleanup = TryBlock(
        body=compose(call("int", 1, assign="result")),
        finally_body=compose(call("print", Reference(name="result"))),
    )
    with pytest.raises(CompilationError, match=r"finally_body.*result"):
        render_job(compose(unsafe_cleanup))


def test_empty_bodies_and_nested_comments_are_formatted_idempotently() -> None:
    """Keep attached comments and insert pass for an otherwise empty suite."""
    branch = if_else(
        True, compose(Python(source="# body comment")), otherwise=JobSpec()
    )
    loop = for_each("item", [1], compose(branch)).with_comment(
        "Outer loop.\n\nKeep this group."
    )
    job = compose(loop)

    source = render_job(job)

    assert source.startswith("# Outer loop.\n#\n# Keep this group.\nfor item")
    assert "        # body comment\n        pass" in source
    assert format_source(source) == source
    assert render_job(JobSpec.model_validate_json(job.model_dump_json())) == source


@pytest.mark.parametrize(
    "literal",
    [
        '"""first\n  second\nthird"""',
        'f"""first {1}\n  second\nthird"""',
        't"""first {1}\n  second\nthird"""',
    ],
)
def test_nesting_preserves_multiline_literal_contents(literal: str) -> None:
    """Indent statements while preserving ordinary, formatted, and template strings.

    Args:
        literal: A multiline literal whose data includes significant indentation.
    """
    body = compose(Python(source="text = " + literal, provides=("text",)))
    tree = ast.parse(render_job(compose(for_each("item", [1], body))))
    loop = tree.body[0]
    assert isinstance(loop, ast.For)
    actual = loop.body[0]
    expected = ast.parse("text = " + literal).body[0]
    assert ast.dump(actual) == ast.dump(expected)


def test_nested_errors_retain_component_and_source_paths() -> None:
    """Locate both semantic and contextual syntax failures inside composed bodies."""
    invalid_reference = for_each(
        "item", [1], compose(if_else(True, compose(energy(Reference(name="missing")))))
    )
    with pytest.raises(CompilationError) as failure:
        render_job(compose(invalid_reference))
    assert failure.value.diagnostics[0].path == (
        "components",
        0,
        "body",
        "components",
        0,
        "body",
        "components",
        0,
        "method",
    )

    with pytest.raises(CompilationError) as failure:
        render_job(compose(for_each("item", [1], compose(Python(source="return 1")))))
    assert failure.value.diagnostics[0].path == (
        "components",
        0,
        "body",
        "components",
        0,
        "source",
    )
    assert failure.value.diagnostics[0].line == 2


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_nested_jobs_execute_with_instrumented_psi4_drivers(tmp_path: Path) -> None:
    """Check all block forms and local-option restoration without calculations.

    Args:
        tmp_path: Isolated directory for Psi4 preprocessing and driver instrumentation.
    """
    declaration = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
    calculation = optimize(
        "scf",
        molecule=declaration.ref,
        constraints=(freeze(distance("a1", "a2")),),
        local_options=(options(modules=("scf",), maxiter=5),),
    )
    job = compose(
        declaration,
        Python(
            source="from contextlib import nullcontext\ntrace = []\ncount = 0",
            provides=("nullcontext", "trace", "count"),
        ),
        options(modules=("scf",), maxiter=37),
        for_each(
            "method",
            ["scf", "mp2"],
            compose(
                if_else(
                    Expression(source="method == 'scf'"),
                    compose(calculation),
                    otherwise=compose(
                        energy(Reference(name="method"), molecule=declaration.ref)
                    ),
                )
            ),
        ),
        while_loop(
            Expression(source="count < 2"),
            compose(
                Python(source="count += 1", provides=("count",)),
                call("trace.append", Reference(name="count")),
            ),
        ),
        with_context(
            Expression(source="nullcontext('context')"),
            compose(call("trace.append", Reference(name="entered"))),
            target="entered",
        ),
        TryBlock(
            body=compose(Python(source="raise RuntimeError('handled')")),
            handlers=(
                ExceptionHandler(
                    exception=Expression(source="RuntimeError"),
                    name="error",
                    body=compose(call("trace.append", Expression(source="str(error)"))),
                ),
            ),
            finally_body=compose(call("trace.append", "cleanup")),
        ),
    )
    source = render_job(JobSpec.model_validate_json(job.model_dump_json()))
    assert format_source(source) == source
    program = """import json, sys, psi4
psi4.core.set_output_file('/dev/null', False)
events = []
def optimize(method, **kwargs):
    events.append([method, psi4.core.get_option('SCF', 'MAXITER'),
                   psi4.core.get_option('OPTKING', 'FROZEN_DISTANCE')])
    return 0.0
def energy(method, **kwargs):
    events.append([method, psi4.core.get_option('SCF', 'MAXITER')])
    return 0.0
psi4.optimize, psi4.energy = optimize, energy
namespace = {}
lowered = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(lowered, '<generated>', 'exec'), namespace)
print(json.dumps({'events': events, 'trace': namespace['trace']}))
"""
    assert _PYTHON is not None
    result = subprocess.run(  # noqa: S603 - Supplied interpreter and fixed program instrument all drivers.
        [_PYTHON, "-c", program],
        input=source,
        text=True,
        capture_output=True,
        cwd=tmp_path,
        check=True,
        timeout=60,
    )
    assert _JSON.validate_json(result.stdout) == {
        "events": [["scf", 5, "1 2"], ["mp2", 37]],
        "trace": [1, 2, "context", "handled", "cleanup"],
    }


@pytest.mark.parametrize("initialized", [False, True])
def test_finally_exception_binding_can_delete_an_existing_result(
    initialized: bool,
) -> None:
    """Reject a result that exception cleanup can delete in a finally body.

    Args:
        initialized: Whether the binding exists before entering the outer try.
    """
    initial = (
        compose(Python(source="result = 0", provides=("result",)))
        if initialized
        else JobSpec()
    )
    body = JobSpec() if initialized else compose(call("int", 1, assign="result"))
    cleanup = TryBlock(
        body=compose(Python(source="raise RuntimeError()")),
        handlers=(
            ExceptionHandler(
                exception=Expression(source="RuntimeError"),
                name="result",
                body=JobSpec(),
            ),
        ),
    )
    block = TryBlock(body=body, finally_body=compose(cleanup))

    with pytest.raises(CompilationError, match="result"):
        render_job(compose(initial, block, call("print", Reference(name="result"))))

    rebound = TryBlock(
        body=body,
        finally_body=compose(cleanup, call("int", 2, assign="result")),
    )
    assert "result = (int)(2)" in render_job(
        compose(initial, rebound, call("print", Reference(name="result")))
    )


def test_nested_molecules_remain_first_class_native_nodes() -> None:
    """Keep molecule identities and attached comments inside the lowered template."""
    declaration = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
    step = optimize(
        "scf",
        molecule=declaration.ref,
        constraints=(freeze(distance("a1", "a2")),),
        local_options=(
            options(modules=("scf",), maxiter=5).with_comment("Step settings."),
        ),
    ).with_comment("Constrained step.")
    job = compose(for_each("item", [1], compose(declaration, step)))

    lowered = lower_job(job)
    source = render_job(job)

    template = lowered.body[0]
    assert isinstance(template, native.PythonTemplate)
    molecules = [part for part in template.parts if isinstance(part, native.Molecule)]
    assert len(molecules) == 1
    assert tuple(atom.id for atom in molecules[0].atoms) == ("a1", "a2")
    assert "    # Constrained step." in source
    assert "        # Step settings." in source
    assert "psi4_parser" not in source


def test_branches_can_choose_geometry_without_losing_constraint_indices() -> None:
    """Retain a common atom layout when branch coordinates differ."""
    left = molecule("h2", Molecule.from_xyz("2\nLeft\nH 0 0 0\nH 0 0 .7\n"))
    right = molecule("h2", Molecule.from_xyz("2\nRight\nH 0 0 0\nH 0 0 .8\n"))
    selection = if_else(True, compose(left), otherwise=compose(right))
    step = optimize(
        "scf",
        molecule=Reference(name="h2"),
        constraints=(freeze(distance("a1", "a2")),),
    )

    source = render_job(compose(selection, step))

    assert "'FROZEN_DISTANCE', '1 2'" in source

    reordered = molecule("h2", right.geometry | reorder_atoms(("a2", "a1")))
    ambiguous = if_else(True, compose(left), otherwise=compose(reordered))
    with pytest.raises(CompilationError, match="consistent atom layout") as failure:
        render_job(compose(ambiguous, step))
    assert failure.value.diagnostics[0].path == ("components", 1, "molecule")
