"""Specify comment spacing, scope alignment, and source-sensitive exceptions."""

import pytest

from psi4_parser import format_source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "set guess core    #  With this guess, un-accelerated DIIS will fail.\n",
            "set guess core  # With this guess, un-accelerated DIIS will fail.\n",
        ),
        ("x=1 #note\n", "x = 1  # note\n"),
        ("x=1\t#\t note\r\n", "x = 1  # note\r\n"),
        ("x=1  #\n", "x = 1  #\n"),
        ("  #  heading\nx=1\n", "# heading\nx = 1\n"),
        (
            "def f():\n  #before\n  x=1 #body\n  #after\n#root\nx=2\n",
            "def f():\n    # before\n    x = 1  # body\n    # after\n# root\nx = 2\n",
        ),
        (
            "if True:\n #outer\n molecule h2 {\n#atoms\nH #first\nH 1 0.74\n}\n",
            (
                "if True:\n    # outer\n    molecule h2 {\n"
                "        # atoms\n        H  # first\n        H  1 0.74\n    }\n"
            ),
        ),
        (
            "set {\n#options\nbasis sto-3g    #  minimal\n#end\n}\n",
            "set {\n    # options\n    basis  sto-3g  # minimal\n    # end\n}\n",
        ),
        (
            "if True:\n #first\n x=1\nelse:\n #second\n x=2\n",
            "if True:\n    # first\n    x = 1\nelse:\n    # second\n    x = 2\n",
        ),
        (
            "values=[\n#rows\n[1,2], #first\n[30,4]] #last\n",
            "values = [\n    # rows\n    [ 1, 2],  # first\n    [30, 4]]  # last\n",
        ),
        ("x=12#note\n", "x = 12# note\n"),
        ("x=1\\#note\n", "x = 1  \\# note\n"),
        ("#!/usr/bin/env psi4\nx=1\n", "#!/usr/bin/env psi4\nx = 1\n"),
    ],
)
def test_comment_style(source: str, expected: str) -> None:
    """Normalize actual comments while preserving their physical attachment.

    Args:
        source: Accepted input with noncanonical comment layout.
        expected: Independently specified spacing and scope indentation.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual


def test_literal_hashes_and_foreign_data_are_preserved() -> None:
    """Distinguish comment markers from hashes in retained literals and payloads."""
    source = (
        'text="\\#literal" #actual\n'
        'multiline="""\\# literal\n  text"""\n'
        "cfour {\n #literal\n *CFOUR(CALC=CCSD)\n}\n"
        "pcm {\n #literal\n Medium { SolverType=IEFPCM }\n}\n"
    )

    actual = format_source(source)

    assert 'text = "\\#literal"  # actual\n' in actual
    assert '"""\\# literal\n  text"""' in actual
    assert "cfour {\n #literal\n *CFOUR(CALC=CCSD)\n}" in actual
    assert "pcm {\n #literal\n Medium { SolverType=IEFPCM }\n}" in actual
