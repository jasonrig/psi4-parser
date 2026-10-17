"""Compare representative accepted syntax with a real Psi4 preprocessor."""

import ast
import hashlib
import os
import re
import subprocess
from pathlib import Path

import pytest
from antlr4 import CommonTokenStream, InputStream

from psi4_parser import validate
from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._generated.PsithonParser import PsithonParser

_PYTHON = os.environ.get("PSI4_PYTHON")


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    ("source", "accepted"),
    [
        ("pcm {\nMedium {\nSolverType=IEFPCM\n  }\n}\n", True),
        ("pcm {\nMedium {\nSolverType=IEFPCM\n}\n}\n", False),
    ],
)
def test_pcm_preprocessor_boundary(source: str, accepted: bool, tmp_path: Path) -> None:
    """Check the reference brace boundary with controlled foreign-solver output.

    Args:
        source: PCM input differing in the inner closing-brace column.
        accepted: Whether the generated Python must compile.
        tmp_path: Isolated directory for the preprocessor's temporary file.
    """
    assert _PYTHON is not None
    program = (
        "import sys, types, psi4\n"
        "solver = types.ModuleType('pcmsolver')\n"
        "solver.parse_pcm_input = lambda path: ''\n"
        "sys.modules['pcmsolver'] = solver\n"
        "psi4.core.set_output_file('/dev/null', False)\n"
        "compile(psi4.process_input(sys.stdin.read(), print_level=0), "
        "'<reference>', 'exec')\n"
    )

    result = subprocess.run(  # noqa: S603 - Fixed program and reference interpreter.
        [_PYTHON, "-c", program],
        input=source,
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )

    assert (result.returncode == 0) == accepted, result.stderr
    assert bool(validate(source)) != accepted
    if not accepted:
        assert "SyntaxError" in result.stderr


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_namespace_inventory_matches_reference(tmp_path: Path) -> None:
    """Keep namespace substitutions aligned with the installed reference profile.

    Args:
        tmp_path: Isolated working directory for the reference interpreter.
    """
    assert _PYTHON is not None
    grammar = (
        Path(__file__).resolve().parents[1] / "grammar/PsithonParser.g4"
    ).read_text()
    expected: list[str] = []
    for name in ("CORE", "CONSTANT"):
        match = re.search(rf"_PSITHON_{name}_NAMES = (\(.*?\n\))", grammar, re.DOTALL)
        assert match is not None
        names: tuple[str, ...] = ast.literal_eval(match.group(1))
        expected.extend(names)
        if name == "CORE":
            expected.append("")
    result = subprocess.run(  # noqa: S603 - Explicit reference interpreter, fixed program.
        [
            _PYTHON,
            "-c",
            "import psi4; from psi4.driver import constants; "
            "print('\\n'.join(dir(psi4.core)) + '\\n\\n' + "
            "'\\n'.join(name for name in dir(constants) if not name.startswith('__')))",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == expected


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
@pytest.mark.parametrize(
    "source",
    [
        "molecule h2 {\nH\nH 1 0.74\n}\nset basis sto-3g\nenergy('scf')\n",
        "set scf,mp2 e_convergence 8\n",
        "set {\nbasis 6-31G(d,p)\ne_convergence 1e-12,\n}\n",
        'set optking {\nfrozen_distance = ("\n    1  2\n    3  4\n  ")\n}\n',
        "set matrix [[1,2],\n[3,4]]\n",
        "basis custom {\nassign cc-pvdz\nassign H aug-cc-pvdz\n}\n",
        "cfour {\n# literal content\n*CFOUR(CALC=CCSD)\n}\n",
        "external {\nunits bohr\n1.0 0.0 0.0 0.0\n}\n",
        "lazy import math\nitems = [*x for x in sequences]\n",
        "moleculeh2{\nH\nH 1 0.74\n}\n",
        "setscf{\ne_convergence 8\n}\n",
        "basiscustom{\nassign cc-pvdz\n}\n",
        "cfourliteral{\n*CFOUR(CALC=CCSD)\n}\n",
    ],
)
def test_real_preprocessor_accepts(source: str, tmp_path: Path) -> None:
    """Compare generated Python ASTs and compile the reference without executing it.

    Args:
        source: Input independently checked by both implementations.
        tmp_path: Isolated working directory for Psi4's timer file.
    """
    assert not validate(source)
    assert _PYTHON is not None
    parser = PsithonParser(CommonTokenStream(PsithonLexer(InputStream(source))))
    tree = parser.file_input()
    projected, _ = parser.psithon_project(tree, source)
    normalized = re.sub(
        r"anonymous[0-9a-f]{8}", "anonymous00000000", projected, flags=re.IGNORECASE
    )
    expected = hashlib.sha256(ast.dump(ast.parse(normalized)).encode()).hexdigest()
    # This launcher selects Python mode from argv[0]; resolving its symlink
    # changes its basename to psi4 and launches the job CLI instead.
    python = _PYTHON
    result = subprocess.run(  # noqa: S603 - Explicit reference interpreter, fixed program.
        [
            python,
            "-c",
            "import ast, hashlib, re, sys, psi4; "
            "psi4.core.set_output_file('/dev/null', False); "
            "code = psi4.process_input(sys.stdin.read(), print_level=0); "
            "compile(code, '<reference>', 'exec'); "
            "code = re.sub(r'anonymous[0-9a-f]{8}', 'anonymous00000000', "
            "code, flags=re.IGNORECASE); "
            "print(hashlib.sha256(ast.dump(ast.parse(code)).encode()).hexdigest())",
        ],
        input=source,
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected
