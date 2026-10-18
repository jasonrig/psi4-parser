"""Specify scientific table layout independently of the formatter algorithms."""

from collections.abc import Callable

import pytest

from psi4_parser import format_source, parse, verify_format

# noinspection PyProtectedMember
from psi4_parser._formatting.arrays import format_arrays

# noinspection PyProtectedMember
from psi4_parser._formatting.blocks import format_blocks

# noinspection PyProtectedMember
from psi4_parser._formatting.comments import format_comments

# noinspection PyProtectedMember
from psi4_parser._formatting.layout import Layout

# noinspection PyProtectedMember
from psi4_parser._formatting.molecules import format_molecules

# noinspection PyProtectedMember
from psi4_parser._formatting.options import format_occupations, format_options

# noinspection PyProtectedMember
from psi4_parser._formatting.python import format_python
from psi4_parser.formatting import FormattingError


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            (
                "molecule water {\n"
                "0 1\n"
                "O 0.000000 0.000000 -0.100000\n"
                "H 0.000000 -0.757000 0.500000\n"
                "H 0.000000 0.757000 0.500000\n"
                "\n"
                "units angstrom\n"
                "}\n"
            ),
            (
                "molecule water {\n"
                "    0 1\n"
                "    O  0.000000   0.000000  -0.100000\n"
                "    H  0.000000  -0.757000   0.500000\n"
                "    H  0.000000   0.757000   0.500000\n"
                "\n"
                "    units angstrom\n"
                "}\n"
            ),
        ),
        (
            "molecule {\nH 0 0 0\n--\n0 1\nGh(Cl) -1.00 2.0 0\n}\n",
            (
                "molecule {\n"
                "    H        0     0    0\n"
                "    --\n"
                "    0 1\n"
                "    Gh(Cl)  -1.00  2.0  0\n"
                "}\n"
            ),
        ),
        (
            "molecule {\nO\nH 1 r\nH 1 r 2 angle\n\nr=0.96\nangle=104.5\n}\n",
            (
                "molecule {\n"
                "    O\n"
                "    H  1 r\n"
                "    H  1 r  2 angle\n"
                "\n"
                "    r     = 0.96\n"
                "    angle = 104.5\n"
                "}\n"
            ),
        ),
        (
            "if True:\n molecule {\nH 0 0 0\n}\n",
            "if True:\n    molecule {\n        H  0  0  0\n    }\n",
        ),
        (
            "set mcscf {\nreference twocon\ndocc [10,1]\nsocc [0,2]\nmaxiter 140\n}\n",
            (
                "set mcscf {\n"
                "    reference  twocon\n"
                "    docc       [10, 1]\n"
                "    socc       [ 0, 2]\n"
                "    maxiter    140\n"
                "}\n"
            ),
        ),
        (
            "set {\nbasis cc-pvdz\n\n# section\ne_convergence=10\nx 1\n}\n",
            (
                "set {\n"
                "    basis  cc-pvdz\n"
                "\n"
                "    # section\n"
                "    e_convergence = 10\n"
                "    x               1\n"
                "}\n"
            ),
        ),
        (
            "values=[\n[0.0,-0.141063524007],\n[-0.026530424045,0.003443783832],\n]\n",
            (
                "values = [\n"
                "    [ 0.0           , -0.141063524007],\n"
                "    [-0.026530424045,  0.003443783832],\n"
                "]\n"
            ),
        ),
        (
            "coords=[\n0.0,-2.0,1.0,\n12.25,0.0,-0.0]\n",
            "coords = [\n     0.0 , -2.0,  1.0,\n    12.25,  0.0, -0.0]\n",
        ),
        (
            "x=[\n1.0e-3,\n-12.0E+2,\n0\n]\n",
            "x = [\n      1.0e-3,\n    -12.0E+2,\n      0\n]\n",
        ),
        (
            "set matrix [[1,2],\n[30,4]]\n",
            "set matrix [[ 1, 2],\n            [30, 4]]\n",
        ),
        (
            "molecule {\n2\n A title   with spacing\nH 0 0 0\nH 0 0 1\n}\n",
            (
                "molecule {\n"
                "    2\n"
                " A title   with spacing\n"
                "    H  0  0  0\n"
                "    H  0  0  1\n"
                "}\n"
            ),
        ),
    ],
    ids=[
        "cartesian",
        "fragments-and-labels",
        "zmatrix",
        "nested-molecule",
        "occupation-vectors",
        "option-sections",
        "matrix",
        "flat-rows",
        "exponents",
        "native-matrix",
        "xyz-title",
    ],
)
def test_scientific_style(source: str, expected: str) -> None:
    """Apply every agreed table style with unchanged row breaks and lexemes.

    Args:
        source: Accepted input before scientific alignment.
        expected: Independently specified formatted source.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ('s="H 0 0 0"\n', 's="H  0  0  0"\n'),
        ("molecule {\nH 0 0 0\n}\n", "molecule {\nH 0.0 0 0\n}\n"),
        (
            "molecule {\n2\nTitle A\nH 0 0 0\nH 0 0 1\n}\n",
            "molecule {\n2\nTitle  A\nH 0 0 0\nH 0 0 1\n}\n",
        ),
        ("molecule {\nfrom_file: a.xyz\n}\n", "molecule {\nfrom_file: b.xyz\n}\n"),
    ],
)
def test_molecule_preservation_is_specific(before: str, after: str) -> None:
    """Keep geometry fields, metadata and arbitrary Python strings significant.

    Args:
        before: Original input.
        after: A semantically or lexically significant change.
    """
    with pytest.raises(FormattingError):
        verify_format(before, after)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "x=[[1,2],\n[30,4]]\n",
            "x = [[ 1, 2],\n     [30, 4]]\n",
        ),
        (
            "x=[1,2,\n30,4]\n",
            "x = [ 1, 2,\n     30, 4]\n",
        ),
        (
            "x=(\n(1,2),\n(30,4),\n)\n",
            "x = (\n    ( 1, 2),\n    (30, 4),\n)\n",
        ),
        (
            "x=[\n[1,2,\n3,4],\n[50,6,\n7,80]]\n",
            "x = [\n    [ 1, 2,\n        3,  4],\n    [50, 6,\n        7, 80]]\n",
        ),
        (
            "x=[\n[1,2],\n[3]]\n",
            "x = [\n    [1, 2],\n    [3]]\n",
        ),
        (
            "x=[\n[1,a+2],\n[3,b]]\n",
            "x = [\n    [1, a + 2],\n    [3, b]]\n",
        ),
        (
            "set vector [ 1,2 ]\n",
            "set vector [1, 2]\n",
        ),
        (
            "set basis [1,2]\n",
            "set basis [1,2]\n",
        ),
        (
            "set {\naaa [[1,2],\n[30,4]]\nlong_key 1\n}\n",
            (
                "set {\n    aaa       [[ 1, 2],\n"
                "               [30, 4]]\n    long_key  1\n}\n"
            ),
        ),
        (
            "molecule {\n0,1\nH 0,0,0\nH 0,0,0.74\nunits=bohr\n}\n",
            (
                "molecule {\n    0, 1\n    H  0,  0,  0\n"
                "    H  0,  0,  0.74\n    units = bohr\n}\n"
            ),
        ),
        (
            "molecule {\nefp water\n0 0 0\n1.00 -2 0\n0 1 0\n}\n",
            (
                "molecule {\n    efp water\n"
                "    0      0  0\n    1.00  -2  0\n    0      1  0\n}\n"
            ),
        ),
    ],
    ids=[
        "inline-matrix-row",
        "inline-flat-row",
        "tuple-table",
        "matching-wrapped-segments",
        "ragged-array",
        "expression-array",
        "inline-native-vector",
        "basis-quoting",
        "option-matrix-columns",
        "comma-geometry",
        "efp-points",
    ],
)
def test_layout_boundaries(source: str, expected: str) -> None:
    """Keep native and Python table decisions stable at layout boundaries.

    Args:
        source: A boundary between normal syntax and table layout.
        expected: The independently specified whitespace result.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual


def test_from_file_trailing_spaces_remain_significant() -> None:
    """Retain the complete reader reference even beyond its last visible token."""
    with pytest.raises(FormattingError, match="native payloads"):
        verify_format(
            "molecule {\nfrom_file: a.xyz \n}\n",
            "molecule {\nfrom_file: a.xyz\n}\n",
        )


def test_table_comments_and_literals_remain_exact() -> None:
    """Normalize inline comment gaps while preserving text and literal interiors."""
    source = (
        "x=[\n[1,2],  # first row  \n[30,4]] # second row\n"
        'text="""H 0  0 0\n[[1,2],[30,4]]"""\n'
        'debug=f"{[[1,2],[30,4]]=}"\n'
        'template=t"{[[1,2],[30,4]]}"\n'
    )

    actual = format_source(source)

    assert "],  # first row  \n" in actual
    assert "]]  # second row\n" in actual
    assert '"""H 0  0 0\n[[1,2],[30,4]]"""' in actual
    assert 'f"{[[1,2],[30,4]]=}"' in actual
    assert 't"{[[1,2],[30,4]]}"' in actual


@pytest.mark.parametrize(
    ("style", "source"),
    [
        (format_python, "x=call(a,\nb)\n"),
        (format_molecules, "molecule {\nH\n}\n"),
        (format_blocks, "set {\na 1\n}\nset {\nb 2\n}\n"),
        (format_comments, "x=1 #note\n"),
        (format_options, "set {\na 1\n}\n"),
        (format_arrays, "x=[[1],\n[20]]\n"),
        (format_occupations, "set {\ndocc [10]\nsocc [0]\n}\n"),
    ],
)
def test_style_passes_leave_their_input_unchanged(
    style: Callable[[Layout], Layout], source: str
) -> None:
    """Return independent edit plans so style composition has no shared mutation.

    Args:
        style: One formatting transformation.
        source: Input containing the transformation's target construct.
    """
    plan = Layout(parse(source), ())
    original_edits = plan.edits.copy()

    formatted = style(plan)

    assert formatted is not plan
    assert plan.edits == original_edits
    assert formatted.result.source == source
    assert formatted.edits != original_edits


def test_higher_rank_arrays_align_each_numeric_plane() -> None:
    """Visit numeric matrices nested inside higher-rank literal containers."""
    source = "x=[\n[[1,2],[30,4]],\n[[5,6],[7,80]],\n]\n"
    expected = "x = [\n    [[ 1, 2], [30, 4]],\n    [[5,  6], [7, 80]],\n]\n"

    assert format_source(source) == expected


def test_occupation_vectors_with_matching_wrapping() -> None:
    """Align corresponding occupations even when each vector spans several lines."""
    source = "set {\ndocc [10,\n1]\nsocc [0,\n200]\n}\n"
    expected = (
        "set {\n    docc  [10,\n             1]\n    socc  [ 0,\n           200]\n}\n"
    )

    assert format_source(source) == expected


def test_repeated_native_equals_keep_value_columns_aligned() -> None:
    """Preserve each accepted equals token while aligning native option values."""
    source = "set {\na = = 1\nlong 2\n}\n"
    expected = "set {\n    a  == 1\n    long  2\n}\n"

    assert format_source(source) == expected


def test_inline_reader_reference_does_not_capture_following_python() -> None:
    """Restrict literal reference protection to the native molecule body."""
    source = "molecule {pubchem:water};x=1\n"

    assert format_source(source) == "molecule {pubchem: water}; x = 1\n"
