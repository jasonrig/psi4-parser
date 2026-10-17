"""Check the semantic information retained by the public program AST."""

import ast

import pytest

from psi4_parser.ast import build_ast


def test_native_options_have_a_python_ast() -> None:
    """Lower native syntax into the exact option call that Psi4 would compile."""
    program = build_ast("set basis cc-pvdz\n")

    expected = ast.parse('core.set_global_option("BASIS", "cc-pvdz")')
    assert ast.compare(program.python.body[-1], expected.body[0])


@pytest.mark.parametrize(
    ("before", "after", "equivalent"),
    [
        ("x=1+2\n", "x = 1 + 2\n", True),
        ('s=f"{x+1=}"\n', 's = f"{x + 1=}"\n', False),
        ('s=t"{x+1}"\n', 's = t"{x + 1}"\n', False),
        ("x=1+2\n", "x=1-2\n", False),
        ("x=1\n", "x=True\n", False),
        ("x=1\n", "x=1.0\n", False),
    ],
)
def test_ast_equivalence(before: str, after: str, *, equivalent: bool) -> None:
    """Distinguish executable values while disregarding harmless layout.

    Args:
        before: Original program.
        after: A change to the program's layout or interpretation.
        equivalent: Whether their abstract syntax must agree.
    """
    assert build_ast(before).equivalent(build_ast(after)) is equivalent


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("pcm {\nA=1\n}\n", "pcm {\nA=2\n}\n"),
        (
            "molecule {\nfrom_file: first.xyz\n}\n",
            "molecule {\nfrom_file: second.xyz\n}\n",
        ),
        ("cfour {abc}\n", "cfour { abc}\n"),
        (
            "text = '''\nmolecule {\nfrom_file: first.xyz\n}\n'''\n",
            "text = '''\nmolecule {\nfrom_file: second.xyz\n}\n'''\n",
        ),
    ],
)
def test_native_payload_changes_are_significant(before: str, after: str) -> None:
    """Retain solver text and file references without reading or executing them.

    Args:
        before: Original input containing native data.
        after: Input with different native data.
    """
    assert not build_ast(before).equivalent(build_ast(after))


def test_anonymous_basis_labels_are_stable() -> None:
    """Compare generated basis bindings without modifying user identifiers."""
    source = "basis {\nassign cc-pvdz\n}\nbasis {\nassign sto-3g\n}\n"

    first, second = build_ast(source), build_ast(source)

    assert first.equivalent(second)
    assert len(first.native_data) == 2
    assert not first.equivalent(
        build_ast(source.replace("basis {", "basis named {", 1))
    )


def test_ast_does_not_execute_input() -> None:
    """Treat executable Python as syntax without running its statements."""
    program = build_ast("raise RuntimeError('must not execute')\n")

    assert isinstance(program.python.body[-1], ast.Raise)


def test_generated_basis_names_do_not_capture_user_bindings() -> None:
    """Choose fresh deterministic names without changing Python's nonlocal scope."""
    source = (
        "def outer():\n"
        "    basisspec_psi4_yo__anonymous00000000 = None\n"
        "    def inner():\n"
        "        basis {\nassign cc-pvdz\n}\n"
        "        nonlocal basisspec_psi4_yo__anonymous00000000\n"
    )

    program = build_ast(source)

    names = {
        node.name
        for node in ast.walk(program.python)
        if isinstance(node, ast.FunctionDef)
    }
    assert "basisspec_psi4_yo__anonymous00000000" not in names
    assert "basisspec_psi4_yo__anonymous00000001" in names
