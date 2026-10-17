"""Apply PEP 8 whitespace while preserving the chosen physical line breaks."""

import pytest

from psi4_parser import format_source


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "def f(x:int=1,y=2,*,z:str='a')->int:\n return x\n",
            "def f(x: int = 1, y=2, *, z: str = 'a') -> int:\n    return x\n",
        ),
        ("x=data[lower:upper:step]\n", "x = data[lower:upper:step]\n"),
        (
            "x=data[lower+offset:upper+offset:step]\n",
            "x = data[lower + offset : upper + offset : step]\n",
        ),
        ("x=data[:upper_fn(x):step_fn(x)]\n", "x = data[: upper_fn(x) : step_fn(x)]\n"),
        ("x=data[::step_fn(x)]\n", "x = data[:: step_fn(x)]\n"),
        ("x=data[-1:3,lower+1:]\n", "x = data[-1:3, lower + 1 :]\n"),
        (
            "try:\n pass\nexcept * ValueError as error:\n pass\n",
            "try:\n    pass\nexcept* ValueError as error:\n    pass\n",
        ),
        ("x=long_call(a,\nb)\n", "x = long_call(a,\n              b)\n"),
        ("x=long_call(\na,\nb,\n)\n", "x = long_call(\n    a,\n    b,\n)\n"),
        (
            "def f(\nx:int=1,\ny=2,\n):\n return x\n",
            "def f(\n        x: int = 1,\n        y=2,\n):\n    return x\n",
        ),
        (
            "if True:\n x=long_call(a,\nb)\n",
            "if True:\n    x = long_call(a,\n                  b)\n",
        ),
        (
            'x=call(f"{a+1=}",\n"b")\n',
            'x = call(f"{a+1=}",\n         "b")\n',
        ),
        (
            'x=f"{data[lower+1:upper]=}"\ny=t"{f(x=1)}"\n',
            'x = f"{data[lower+1:upper]=}"\ny = t"{f(x=1)}"\n',
        ),
    ],
    ids=[
        "annotated-defaults",
        "simple-slice",
        "compound-slice",
        "slice-calls",
        "omitted-slice-fields",
        "multidimensional-slice",
        "exception-group",
        "vertical-continuation",
        "hanging-continuation",
        "function-parameter-hanging-indent",
        "nested-continuation",
        "interpolated-argument",
        "literal-interpolations",
    ],
)
def test_python_whitespace(source: str, expected: str) -> None:
    """Follow PEP 8 spacing and indentation without splitting physical rows.

    Args:
        source: Valid input before whitespace normalization.
        expected: Independently specified Python layout.
    """
    actual = format_source(source)

    assert actual == expected
    assert format_source(actual) == actual
