"""Check generated jobs against the real Psi4 preprocessor and molecule reader."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser.job import Job, Molecule, emit_job, read_job

_PYTHON = os.environ.get("PSI4_PYTHON")
_FIXTURES = Path(__file__).resolve().parents[1] / "test/fixtures/positive/psi4"


def _assert_reference_preservation(source: str, directory: Path) -> None:
    assert _PYTHON is not None
    program = (
        "import ast, json, re, sys, psi4, qcelemental\n"
        "psi4.core.set_output_file('/dev/null', False)\n"
        "for source in json.loads(sys.stdin.read()):\n"
        "    code = psi4.process_input(source, print_level=0)\n"
        "    compile(code, '<reference>', 'exec')\n"
        "    code = re.sub(r'anonymous[0-9a-f]{8}', 'anonymous00000000', code)\n"
        "    tree = ast.parse(code)\n"
        "    records = []\n"
        "    for node in ast.walk(tree):\n"
        "        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)\n"
        "                and node.func.id == 'geometry'):\n"
        "            records.append(qcelemental.molparse.from_string(\n"
        "                node.args[0].value, verbose=0))\n"
        "            node.args[0].value = '<verified molecule>'\n"
        "    print(json.dumps([ast.dump(tree, include_attributes=False), records],\n"
        "          sort_keys=True, default=lambda value: value.tolist()))\n"
    )
    inputs = [source, emit_job(read_job(source))]
    result = subprocess.run(  # noqa: S603 - Supplied interpreter, no job execution.
        [_PYTHON, "-c", program],
        input=json.dumps(inputs),
        text=True,
        capture_output=True,
        check=False,
        cwd=directory,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 2, result.stdout
    assert lines[0] == lines[1]


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    "source",
    [
        "memory 500 MiB\nset scf,mp2 e_convergence 8\n"
        "set {\nbasis 6-31G(d,p)\ndocc [1,0]\n}\n",
        "basis custom {\nassign cc-pvdz\nassign H aug-cc-pvdz\n}\n",
        "external {\nunits bohr\n1.0 0.0 0.0 0.0\nHe 1.0 0.0 0.0\n}\n",
        "cfourliteral{\n# literal content\n*CFOUR(CALC=CCSD)\n}\n",
        'if False:\n x=f"{\n cfour{\n*CFOUR(CALC=CCSD)\n}\n =}"\n',
        'if False:\n x=t"{\n cfour{\n*CFOUR(CALC=CCSD)\n}\n }"\n',
        "def job():\n molecule h2 {\nH\nH 1 R\nR=0.74\n}\n return h2\n",
        "molecule {\n2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n}\n",
    ],
)
def test_native_emission_preserves_reference_program(
    source: str, tmp_path: Path
) -> None:
    """Retain real preprocessing behavior across native blocks and Python context.

    Args:
        source: Independent native and mixed-language input.
        tmp_path: Isolated directory for the reference preprocessor's files.
    """
    _assert_reference_preservation(source, tmp_path)


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize("fixture", ["scf1", "tu5-sapt", "dft-ghost", "isapt-charged"])
def test_molecular_emission_preserves_reference_data(
    fixture: str, tmp_path: Path
) -> None:
    """Retain reader results for Z-matrices, fragments, ghosts, and charged systems.

    Args:
        fixture: Upstream calculation with a distinct molecular specification.
        tmp_path: Isolated directory for the reference preprocessor's files.
    """
    source = (_FIXTURES / fixture / "input.dat").read_bytes().decode("utf-8")

    _assert_reference_preservation(source, tmp_path)


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize("title", ["", "# comment", "Hydrogen"])
def test_imported_xyz_keeps_all_atoms_after_preprocessing(
    title: str, tmp_path: Path
) -> None:
    """Retain atom count when Psi4 strips blank or comment-only XYZ titles.

    Args:
        title: XYZ comment line, including forms removed by Psi4 preprocessing.
        tmp_path: Isolated directory for the reference process.
    """
    assert _PYTHON is not None
    molecule = Molecule.from_xyz("2\n" + title + "\nH 0 0 0\nH 0 0 0.74\n")
    source = emit_job(Job(body=(molecule,)))
    program = (
        "import ast, sys, psi4, qcelemental\n"
        "psi4.core.set_output_file('/dev/null', False)\n"
        "tree = ast.parse(psi4.process_input(sys.stdin.read(), print_level=0))\n"
        "for node in ast.walk(tree):\n"
        "    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)\n"
        "            and node.func.id == 'geometry'):\n"
        "        record = qcelemental.molparse.from_string(\n"
        "            node.args[0].value, verbose=0)['qm']\n"
        "        print(len(record['elem']))\n"
    )

    result = subprocess.run(  # noqa: S603 - Supplied interpreter, no job execution.
        [_PYTHON, "-c", program],
        input=source,
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "2"
