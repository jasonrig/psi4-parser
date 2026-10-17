"""Exercise grammar rejection, scope predicates, and source diagnostics."""

import pytest
from antlr4 import CommonTokenStream, InputStream, Token

from psi4_parser import validate
from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._generated.PsithonParser import PsithonParser


def test_native_job_is_accepted() -> None:
    """Accept a geometry, options, and an ordinary Python driver call."""
    source = "molecule h2 {\nH\nH 1 0.74\n}\nset basis cc-pvdz\nenergy('scf')\n"

    assert not validate(source)


def test_invalid_python_is_rejected() -> None:
    """Reject a missing expression and retain its source location."""
    errors = validate("answer =\n")

    assert errors
    assert errors[0].line == 1


@pytest.mark.parametrize(
    ("source", "line"),
    [
        ("value=1\n\ndef f(psi_hartree2ev):pass\n", 3),
        ("def f():\n set basis sto-3g\n global core\n", 3),
    ],
)
def test_projected_errors_use_original_lines(source: str, line: int) -> None:
    """Map namespace and generated-code errors back past the inserted prelude.

    Args:
        source: Input whose generated Python is invalid.
        line: Original source line of the offending declaration.
    """
    errors = validate(source)

    assert errors
    assert errors[0].line == line


@pytest.mark.parametrize(
    "source",
    [
        "set basis sto-3g\n",
        "basis named {\nassign cc-pvdz\n}\n",
        "molecule {\nHe\n}\n",
        "cfour {\n*CFOUR(CALC=CCSD)\n}\n",
        "external {\n1.0 0.0 0.0 0.0\n}\n",
    ],
)
def test_parse_tree_preserves_source_tokens(source: str) -> None:
    """Keep generated Python wrappers out of the returned native parse tree.

    Args:
        source: Native input whose validation also checks generated Python.
    """
    tokens = CommonTokenStream(PsithonLexer(InputStream(source)))
    tokens.fill()
    expected = "".join(
        token.text or ""
        for token in tokens.tokens
        if token.channel == Token.DEFAULT_CHANNEL
    )
    parser = PsithonParser(tokens)

    tree = parser.file_input()

    assert parser.getNumberOfSyntaxErrors() == 0
    assert tree.getText() == expected


@pytest.mark.parametrize(
    "source",
    [
        "molecule h2 {\nH\n",
        "molecule bad-name {\nH\n}\n",
        "return 1\n",
        "break\n",
        "continue\n",
        "yield 1\n",
        "await run()\n",
        "def f():\n    class C:\n        return 1\n",
        "for x in values:\n    def f():\n        break\n",
        "async def outer():\n    def inner():\n        await run()\n",
        "async for item in values:\n    pass\n",
        "async with session():\n    pass\n",
        "async def f():\n    yield from values\n",
        "for item in values:\n    pass\nelse:\n    break\n",
        "lambda x=(yield 1): x\n",
        "gen = (x for x in await values)\n",
        "def f():\n    gen = ((yield x) for x in values)\n",
        'set basis "cc-pvdz"\n',
        "set basis cc-pvdz extra\n",
        "set basis $1bad\n",
    ],
)
def test_invalid_scope_or_native_syntax(source: str) -> None:
    """Reject malformed native syntax and misplaced Python control constructs.

    Args:
        source: Input rejected by syntax rules or ANTLR scope predicates.
    """
    assert validate(source)


@pytest.mark.parametrize(
    "source",
    [
        "def f():\n    return 1\n",
        "for x in values:\n    if x:\n        break\n    continue\n",
        "def f():\n    yield 1\n    yield from values\n",
        "async def f():\n    await run()\n    yield 1\n",
        "def outer():\n    def f(x=(yield 1)):\n        return x\n",
        "lambda: (yield 1)\n",
        "if True: memory 500 MiB\n",
        "result = memory 500 MiB\n",
        "print(memory 500 MiB)\n",
        "async def f():\n    async for item in values:\n        await run(item)\n",
        "async def f():\n    callback = lambda x=await run(): x\n",
        "gen = (await run(x) for x in values)\n",
        "gen = (x for x in values if await check(x))\n",
        "gen = (x for x in values for y in await ys(x))\n",
        "def f():\n    gen = (x for x in (yield values))\n",
    ],
)
def test_valid_contexts(source: str) -> None:
    """Retain valid control flow and memory directives inside Python contexts.

    Args:
        source: Mixed input using a valid enclosing Python context.
    """
    assert not validate(source)


def test_unicode_molecule_name() -> None:
    """Accept a Python identifier outside the Unicode basic multilingual plane."""
    assert not validate("molecule 𝑚𝑜𝑙 {\nH\n}\n")


def test_literal_cfour_hash_is_preserved() -> None:
    """Keep hash characters and unmatched quotes in the literal CFOUR payload."""
    assert not validate('cfour {\n# " unmatched quote is literal data\n}\n')


@pytest.mark.parametrize(
    "source",
    [
        "moleculeh2{\nH\nH 1 0.74\n}\n",
        "setscf{\ne_convergence 8\n}\n",
        "basiscustom{\nassign cc-pvdz\n}\n",
        "cfourliteral{\n*CFOUR(CALC=CCSD)\n}\n",
    ],
)
def test_compact_headers(source: str) -> None:
    """Accept the zero-space block headers recognized by Psi4's regexes.

    Args:
        source: Native block whose keyword directly precedes its name or module.
    """
    assert not validate(source)
