"""Check formatter preservation against the supplied Psi4 preprocessor and readers."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser import format_source

_PYTHON = os.environ.get("PSI4_PYTHON")


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    "source",
    [
        "set {\n basis cc-pvdz\n docc [1,  0]\n}\nx=1+2\n",
        "x=psi4 . Matrix\n",
        "x=psi4. Matrix\n",
        "x=mol . extract_subsets(1)\n",
        "def job():\n  molecule h2 {\nH\nH 1 0.74\n}\n  return energy('hf')\n",
        'x=1\ns=f"{x+1=}"\nt=t"{x+1}"\n',
        "cfour {\n # literal\n *CFOUR(CALC=CCSD)\n}\nx=1\n",
        "basis custom {\n assign H cc-pvdz\n}\n",
        "from __future__ import barry_as_FLUFL\nx=1<>2\n",
        "set guess core    #  Keep this guess\nx=1 #note\nx=12#unchanged value\n",
        "def f():\n  #before\n  x=1 #body\n  #after\n#root\nx=2\n",
        "molecule h2 {\n#atoms\nH #first\nH 1 0.74\n}\n"
        "set {\n#options\nbasis sto-3g #minimal\n}\n",
    ],
)
def test_reference_python_ast_is_preserved(source: str, tmp_path: Path) -> None:
    """Compare the real preprocessor's original and formatted Python ASTs.

    Args:
        source: Input covering native syntax and source-sensitive Python.
        tmp_path: Isolated working directory for the reference process.
    """
    _assert_reference_preservation(source, tmp_path)


def _assert_reference_preservation(
    source: str, tmp_path: Path, *, python_ast: bool = True
) -> None:
    assert _PYTHON is not None
    program = (
        "import ast, json, sys, psi4, qcelemental\n"
        "psi4.core.set_output_file('/dev/null', False)\n"
        "for source in json.loads(sys.stdin.read()):\n"
        "    code = psi4.process_input(source, print_level=0)\n"
        "    if sys.argv[1] == 'python':\n"
        "        compile(code, '<reference>', 'exec')\n"
        "    tree = ast.parse(code)\n"
        "    records = []\n"
        "    for node in ast.walk(tree):\n"
        "        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)\n"
        "                and node.func.id == 'geometry'):\n"
        "            records.append(qcelemental.molparse.from_string(\n"
        "                node.args[0].value, verbose=0))\n"
        "            node.args[0].value = '<verified molecule>'\n"
        "    if sys.argv[1] == 'python':\n"
        "        output = [ast.dump(tree, include_attributes=False), records]\n"
        "    else:\n"
        "        assert records\n"
        "        output = records\n"
        "    print(json.dumps(output,\n"
        "          sort_keys=True, default=lambda value: value.tolist()))\n"
    )

    inputs = [source, format_source(source)]
    payload = json.dumps(inputs)
    result = subprocess.run(  # noqa: S603 - Supplied launcher and fixed analysis program.
        [_PYTHON, "-c", program, "python" if python_ast else "geometry"],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 2, result.stdout
    assert lines[0] == lines[1]


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_generated_external_geometry_indentation(tmp_path: Path) -> None:
    """Prove generated padding changes preserve the reference reader's molecule.

    Args:
        tmp_path: Isolated working directory for the reference process.
    """
    source = "if False:\n external {\nHe 0.0 0.0 0.0\n}\n"
    _assert_reference_preservation(source, tmp_path, python_ast=False)


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    "fixture", ["scf1", "tu5-sapt", "scf-bz2", "dft-ghost", "mcscf2", "isapt-charged"]
)
def test_reference_scientific_fixtures(fixture: str, tmp_path: Path) -> None:
    """Compare real reader records for varied geometries and scientific tables.

    Args:
        fixture: Upstream job with Cartesian, Z-matrix, fragment or ghost data.
        tmp_path: Isolated directory for the real reference interpreter.
    """
    root = Path(__file__).resolve().parents[1] / "test/fixtures/positive/psi4"
    source = (root / fixture / "input.dat").read_bytes().decode("utf-8")

    _assert_reference_preservation(source, tmp_path)


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    "source",
    [
        "molecule {\n2\n A title   with spacing\nH 0 0 0\nH 0 0 0.74\n}\n",
        "molecule {\n0 1\n13C@13.003 0.0 0.0 0.0\nGh(H) 0.0 0.0 1.0\n}\n",
        "molecule {\nefp water\n0 0 0\n1.00 -2 0\n0 1 0\n}\n",
    ],
)
def test_reference_molecule_record_variants(source: str, tmp_path: Path) -> None:
    """Preserve XYZ titles, isotope masses and effective-fragment placements.

    Args:
        source: Native molecule data with a distinct reader schema.
        tmp_path: Isolated directory for real preprocessor and reader checks.
    """
    _assert_reference_preservation(source, tmp_path)
