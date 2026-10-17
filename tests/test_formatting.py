"""Exercise formatting through independently specified source examples."""

import pytest

from psi4_parser import InvalidInputError, ParseResult, formatting, parse
from psi4_parser.formatting import FormattingError, format_source, verify_format


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x=1+2", "x = 1 + 2\n"),
        (
            "# A researcher's comment: { \"\n" + "x=1\n",
            "# A researcher's comment: { \"\n" + "x = 1\n",
        ),
        ("from  ..  import  x\n", "from .. import x\n"),
        ("from . . . import x\n", "from .. . import x\n"),
        ("from . ... pkg import x\n", "from . ...pkg import x\n"),
        ("x=1 .real\n", "x = 1 .real\n"),
        ("x=psi4 . Matrix\n", "x = psi4 . Matrix\n"),
        ("x=psi4. Matrix\n", "x = psi4 . Matrix\n"),
        ("x=psi4.Matrix\n", "x = psi4.Matrix\n"),
        ("x=mol . extract_subsets(1)\n", "x = mol . extract_subsets(1)\n"),
        ("type X[T = int]=list[T]\n", "type X[T=int] = list[T]\n"),
        (
            "match x:\n case - 1:\n  pass\n",
            "match x:\n    case -1:\n        pass\n",
        ),
        (
            "if True:\n  x=1\n  if x:\n     y=-x+2\n",
            "if True:\n    x = 1\n    if x:\n        y = -x + 2\n",
        ),
        (
            "set   {\n  basis   cc-pvdz\n  docc   [1,  0]\n}\n",
            "set {\n    basis  cc-pvdz\n    docc   [1, 0]\n}\n",
        ),
        (
            "molecule   h2{\r\n H\r\n H  1  0.74\r\n}\r\nx=1\r\n",
            "molecule h2 {\r\n    H\r\n    H  1 0.74\r\n}\r\n\r\nx = 1\r\n",
        ),
        (
            "if False:\n external {\nHe 0.0 0.0 0.0\n}\n",
            "if False:\n    external {\nHe 0.0 0.0 0.0\n}\n",
        ),
        ('s=f"{x+1=}"\n', 's = f"{x+1=}"\n'),
        ('s=t"{x+1}"\n', 's = t"{x+1}"\n'),
        ("x=12# keep this exact\n", "x = 12# keep this exact\n"),
        (
            "def f( a ,b=1,*args,**kwargs ):\n  return a+b\n",
            "def f(a, b=1, *args, **kwargs):\n    return a + b\n",
        ),
    ],
)
def test_canonical_source(source: str, expected: str) -> None:
    """Apply the specified style without changing literals or native payloads.

    Args:
        source: Accepted input with inconsistent layout.
        expected: Independently written canonical source.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual


@pytest.mark.parametrize(
    ("before", "after", "reason"),
    [
        ('s=f"{x+1=}"\n', 's=f"{x + 1=}"\n', "AST"),
        ('s=t"{x+1}"\n', 's=t"{x + 1}"\n', "AST"),
        ("x=12# comment\n", "x=12 # comment\n", "AST"),
        ("x=1\n", "x=(1)\n", "CST"),
        ("x=1\n", "x =\n", "invalid"),
        ("pcm {\nA=1\n}\n", "pcm {\nA=2\n}\n", "AST"),
    ],
)
def test_reject_changed_program(before: str, after: str, reason: str) -> None:
    """Reject subtle output changes even when a candidate remains syntactically valid.

    Args:
        before: Original accepted source.
        after: A candidate that violates a preservation invariant.
        reason: The failed validation layer.
    """
    with pytest.raises(FormattingError, match=reason):
        verify_format(before, after)


def test_invalid_input_retains_parser_diagnostics() -> None:
    """Refuse recovered syntax trees and retain the original validation errors."""
    source = "return 1\n"

    with pytest.raises(InvalidInputError) as caught:
        format_source(source)

    assert caught.value.diagnostics == parse(source).diagnostics


def test_payloads_and_comment_lines_are_unchanged() -> None:
    """Preserve source-sensitive text while formatting surrounding statements."""
    source = (
        "# untouched comment  \r\n"
        's="""  text  \r\n   data  \r\n"""\r\n'
        "cfour {\r\n # literal  \r\n  *CFOUR(CALC=CCSD)  \r\n}\r\n"
        "pcm {\r\n  Medium {\r\n    SolverType=IEFPCM\r\n  }\r\n}\r\n"
    )

    actual = format_source(source)

    expected = (
        source.replace("s=", "s = ", 1)
        .replace('"""\r\ncfour {', '"""\r\n\r\ncfour {', 1)
        .replace("}\r\npcm {", "}\r\n\r\npcm {", 1)
    )
    assert actual == expected


def test_output_log_surroundings_are_preserved() -> None:
    """Format extracted input without trimming or rewriting calculation output."""
    divider = "-" * 74
    prefix = (
        "Psi4: An Open-Source Ab Initio Electronic Structure Package  \r\n"
        "  ==> Input File <==\r\n\r\n" + divider + "\r\n"
    )
    suffix = divider + "\r\nUntouched output  "

    actual = format_source(prefix + "x=1\r\n" + suffix)

    assert actual == prefix + "x = 1\r\n" + suffix


def test_formatter_checks_every_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse unsafe output even if the rendering stage produces plausible Python.

    Args:
        monkeypatch: Fixture that restores the deliberately faulty renderer.
    """

    def changed_value(_result: ParseResult) -> str:
        return "x = 2\n"

    monkeypatch.setattr(formatting, "_render", changed_value)

    with pytest.raises(FormattingError, match="AST"):
        formatting.format_source("x = 1\n")


def test_formatter_checks_idempotence(monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse a renderer that oscillates between two equivalent spellings.

    Args:
        monkeypatch: Fixture that restores the deliberately unstable renderer.
    """

    def oscillating(result: ParseResult) -> str:
        return "x = 1\n" if result.source == "x=1\n" else "x=1\n"

    monkeypatch.setattr(formatting, "_render", oscillating)

    with pytest.raises(FormattingError, match="idempotent"):
        formatting.format_source("x=1\n")


def test_output_log_leading_blank_input_lines() -> None:
    """Trim blank input lines while preserving the adjacent output-log header."""
    divider = "-" * 74
    prefix = (
        "Psi4: An Open-Source Ab Initio Electronic Structure Package  \n"
        "  ==> Input File <==\n\n" + divider + "\n"
    )
    suffix = divider + "\nUntouched output  "

    actual = format_source(prefix + " \t\nx=1 \n \n" + suffix)

    assert actual == prefix + "\nx = 1\n\n" + suffix


@pytest.mark.parametrize("prefix", ["f", "t"])
@pytest.mark.parametrize("body", ["(", ")", "{{", "}}", "[", "]"])
def test_literal_delimiters_do_not_indent_code(prefix: str, body: str) -> None:
    """Use token types rather than literal text when tracking continuation depth.

    Args:
        prefix: Python interpolation-string mode.
        body: Literal text that resembles an opening or closing delimiter.
    """
    literal = prefix + '"' + body + '"'

    actual = format_source("s=" + literal + "\nx=1\n")

    assert actual == "s = " + literal + "\nx = 1\n"


@pytest.mark.parametrize("body", ["(", ")", "[", "]", "{"])
def test_cfour_delimiters_do_not_indent_code(body: str) -> None:
    """Keep arbitrary solver data out of Python delimiter state.

    Args:
        body: Solver text consisting of one delimiter character.
    """
    source = "cfour {" + body + "}\nx=1\n"

    actual = format_source(source)

    assert actual == "cfour {" + body + "}\n\nx = 1\n"


def test_native_unicode_whitespace() -> None:
    """Normalize native whitespace permitted by the grammar's Unicode table."""
    source = "set {\n\u00a0\u00a0basis\u2003cc-pvdz\u2003\n}\n"

    actual = format_source(source)

    assert actual == "set {\n    basis  cc-pvdz\n}\n"


def test_explicit_python_continuation() -> None:
    """Indent an explicit continuation without interpreting comment text as code."""
    source = "result=1 + \\\n2\n# comment ending in a backslash\\\nx=1\n"

    actual = format_source(source)

    assert actual == (
        "result = 1 + \\\n    2\n# comment ending in a backslash\\\nx = 1\n"
    )
