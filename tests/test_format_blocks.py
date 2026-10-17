"""Specify blank lines around native block statements and their leading comments."""

import pytest

from psi4_parser import format_source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "molecule {\nH\n}\nset {\nbasis sto-3g\n}\n",
            "molecule {\n    H\n}\n\nset {\n    basis  sto-3g\n}\n",
        ),
        (
            "set {\na 1\n}\n\n  \n\nset {\nb 2\n}\n",
            "set {\n    a  1\n}\n\nset {\n    b  2\n}\n",
        ),
        (
            "set {\na 1\n}  # previous\n# next\nset {\nb 2\n}\n",
            "set {\n    a  1\n}  # previous\n\n# next\nset {\n    b  2\n}\n",
        ),
        (
            "if True:\n set {\na 1\n}\n set {\nb 2\n}\n",
            (
                "if True:\n    set {\n        a  1\n    }\n\n"
                "    set {\n        b  2\n    }\n"
            ),
        ),
        (
            "set {\na 1\n}\nx=1\nset {\nb 2\n}\n",
            "set {\n    a  1\n}\n\nx = 1\n\nset {\n    b  2\n}\n",
        ),
        (
            "set {\na 1\n}\r\nset {\nb 2\n}\n",
            "set {\n    a  1\n}\r\n\r\nset {\n    b  2\n}\n",
        ),
    ],
    ids=[
        "adjacent",
        "extra-blank-lines",
        "attached-comments",
        "nested",
        "intervening-code",
        "newline-spelling",
    ],
)
def test_block_separation(source: str, expected: str) -> None:
    """Surround standalone native blocks with one empty line between statements.

    Args:
        source: Adjacent native blocks or a boundary that must remain unchanged.
        expected: Explicitly agreed spacing, including comments and newlines.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            'cisd_energy,cisd_wfn=energy("CISD",return_wfn=True)\n\n\n'
            "set {\nicore 0\n}\n"
            "casscf_energy=energy('casscf',ref_wfn=cisd_wfn)\n",
            'cisd_energy, cisd_wfn = energy("CISD", return_wfn=True)\n\n'
            "set {\n    icore  0\n}\n\n"
            "casscf_energy = energy('casscf', ref_wfn=cisd_wfn)\n",
        ),
        (
            "x=1\n# next block\nset {\na 1\n}  # result\n# calculation\ny=2\n",
            "x = 1\n\n# next block\nset {\n    a  1\n}  # result\n\n"
            "# calculation\ny = 2\n",
        ),
        (
            "if True:\n set {\na 1\n}\n x=1\nelse:\n x=2\n",
            "if True:\n    set {\n        a  1\n    }\n\n    x = 1\nelse:\n    x = 2\n",
        ),
        (
            "if True:\n x=1\n set {\na 1\n}\nelse:\n x=2\n",
            "if True:\n    x = 1\n\n    set {\n        a  1\n    }\nelse:\n    x = 2\n",
        ),
        (
            "if True:\n x=1\nset {\na 1\n}\n@decorator\ndef f():\n pass\n",
            "if True:\n    x = 1\n\nset {\n    a  1\n}\n\n"
            "@decorator\ndef f():\n    pass\n",
        ),
        (
            "set icore 1\ncasscf_energy=energy('casscf')\n\n\nx=1\n",
            "set icore 1\ncasscf_energy = energy('casscf')\n\n\nx = 1\n",
        ),
        (
            "x=1\r\nset {\r\na 1\r\n}\r\ny=2\r\n",
            "x = 1\r\n\r\nset {\r\n    a  1\r\n}\r\n\r\ny = 2\r\n",
        ),
    ],
    ids=[
        "reported-calculation-boundaries",
        "attached-comments-at-both-boundaries",
        "first-statement-in-suite",
        "last-statement-before-else",
        "compound-and-decorated-neighbors",
        "inline-directives-and-python-only-gaps",
        "crlf-on-both-boundaries",
    ],
)
def test_native_block_neighbors(source: str, expected: str) -> None:
    """Normalize both block boundaries while respecting Python statement suites.

    Args:
        source: Native blocks surrounded by computation or suite boundaries.
        expected: Canonical empty lines without splitting directives or clauses.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual


def test_native_expression_does_not_create_statement_separators() -> None:
    """Keep a braced option expression attached to its Python delimiters."""
    source = "if False:\n x=(\n set {\nbasis sto-3g\n}\n )\n y=1\n"
    expected = (
        "if False:\n    x = (\n        set {\n            basis  sto-3g\n"
        "        }\n    )\n    y = 1\n"
    )

    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual
