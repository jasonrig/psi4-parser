"""Cover native directive families and the embedded Python language."""

import pytest

from psi4_parser import validate


@pytest.mark.parametrize(
    "source",
    [
        "MEMORY 1.5 GiB\n",
        "set scf,mp2 e_convergence 8\n",
        "set basis_guess def2-SV(P)\n",
        "set {\nbasis 6-31G(d,p)\ne_convergence 1e-12,\n}\n",
        'set optking {\nfrozen_distance = ("\n    1  2\n    3  4\n  ")\n}\n',
        "molecule Mg\n{\nMg 0 0 0\n}\nset\n{\nbasis cc-pvdz\n}\n",
        "pcm =\n{\nMedium\n{\nSolverType=IEFPCM\n  }\n}\n",
        "molecule {\nefp NH3,1.0,,2.0, 3.0 4.0 5.0 6.0\n}\n",
        "set globals {\nbasis cc-pvdz\ndocc [1,\n 0, 0]\n}\n",
        "basis custom {\nassign cc-pvdz\nassign H1 aug-cc-pvdz\n}\n",
        "basis {\n[custom]\nspherical\n****\nH 0\nS 1 1.0\n1.0 1.0\n****\n}\n",
        "external charges {\nunits bohr\n1.0 0.0 0.0 0.0\n--\nH 0.0 0.0 0.0\n}\n",
        "pcm {\nUnits = Angstrom\nMedium {\nSolverType = IEFPCM\n  }\n}\n",
        "cfour {\n*CFOUR(CALC=CCSD)\n# literal solver content\n}\n",
        "molecule {\n@13C@13.003 0.0 0.0 0.0\nGh(H) 1 r\nr = 1.0\n}\n",
        "molecule {\n0 1\nH\n--\n1 2\nH\nunits=bohr\nno_com\nsymmetry c1\n}\n",
        "molecule {\npubchem: ethanol\n}\n",
        "molecule {\nfrom_file: /path/to/geometry.xyz\n}\n",
        "molecule {\nfrom_file: \\#geometry.xyz\n}\n",
        "molecule {\nfrom_file: $1geometry.xyz\n}\n",
        "molecule {\nH\nH 1 -r\n-r = 0.74\nunits a.u.\n}\n",
        "external {\nunits a.u.\nGh(H) 0.0 0.0 0.0\n}\n",
        "molecule {\nefp water 0 0 0 0 0 0\n}\n",
        "molecule {\nefp water\n0 0 0\n1 0 0\n0 1 0\n}\n",
        "molecule {\n2\nHydrogen molecule\nH 0 0 0\nH 0 0 1\n}\n",
        "for r in [0.7, 0.8]:\n    molecule h2 {\nH\nH 1 r\n}\n    energy('scf')\n",
        "set basis $basis_name\nset matrix [[1, 2],\n[3, 4]]\n",
        "set = 3\nmolecule = 4\nvalues = set([1, 2])\n",
        'text = """molecule {\\nnot a directive\\n}"""\n',
    ],
    ids=[
        "binary-memory",
        "module-list",
        "inline-parenthesized-basis",
        "option-commas",
        "multiline-option-string",
        "multiline-headers",
        "multiline-pcm-headers",
        "efp-permissive-commas",
        "option-block",
        "basis-assignments",
        "inline-gbs",
        "external-potential",
        "nested-pcm",
        "literal-cfour",
        "isotopes-ghosts-zmatrix",
        "fragments",
        "pubchem",
        "geometry-file",
        "geometry-file-hash",
        "geometry-file-dollar",
        "atomic-units-and-signed-variable",
        "external-ghost",
        "efp-placement",
        "efp-three-points",
        "xyz",
        "native-block-in-loop",
        "references-and-matrices",
        "python-identifiers",
        "python-string",
    ],
)
def test_native_syntax(source: str) -> None:
    """Accept each native family without running a calculation.

    Args:
        source: One complete native or mixed input example.
    """
    assert not validate(source)


@pytest.mark.parametrize(
    "role",
    [
        "basis",
        "basis_relativistic",
        "df_basis_scf",
        "df_basis_mp2",
        "df_basis_cc",
        "df_basis_sapt",
        "df_basis_sad",
        "df_basis_dct",
    ],
)
def test_all_basis_roles(role: str) -> None:
    """Accept every basis block role recognized by the Psi4 preprocessor.

    Args:
        role: Basis role from the preprocessor's complete role list.
    """
    assert not validate(f"{role} custom {{\nassign cc-pvdz\n}}\n")


@pytest.mark.parametrize(
    "source",
    [
        "lazy import math\nlazy from math import sqrt\nlazy = 1\n",
        "items = [*x for x in sequences]\nlookup = {**d for d in dictionaries}\n",
        "values = (*x for x in sequences)\n",
        'result = f"{data["key"]!r:>{width}}"\n',
        'message = t"Energy: {energy:.8f}"\n',
        "type Vector[T = float] = list[T]\n",
        "def choose[T](x: T, /, *, fallback: T | None = None) -> T:\n    return x\n",
        "match result:\n    case {'energy': e, **rest} if e < 0:\n        pass\n",
        "try:\n    run()\nexcept* ValueError, TypeError:\n    pass\n",
        "async def run():\n"
        "    async with manager() as session:\n"
        "        return [x async for x in session]\n",
        "@decorator(1)\nclass Result(Base, metaclass=Meta):\n    value: float = 1.0\n",
    ],
    ids=[
        "lazy-imports-315",
        "unpacking-comprehensions-315",
        "unpacking-generator-315",
        "pep701-fstring",
        "template-string",
        "generic-alias-default",
        "generic-function",
        "match",
        "exception-groups",
        "async",
        "decorated-class",
    ],
)
def test_python_language(source: str) -> None:
    """Parse Python constructs with the imported and extended ANTLR rules.

    Args:
        source: Python syntax that is valid on the target Python 3.15 runtime.
    """
    compile(source, "<fixture>", "exec")

    assert not validate(source)


@pytest.mark.parametrize(
    "source",
    [
        "molecule {\nH 1 2 3 4 5\n}\n",
        "set basis [1, 2\n",
        "pcm {\nMedium {\nSolverType=IEFPCM\n}\n  }\n",
        "cfour {\n*CFOUR(CALC=CCSD)\n",
        "for r in values\n    energy('scf')\n",
        "pcm {\nMedium {\nSolverType=IEFPCM\n}\n}\n",
    ],
)
def test_malformed_input_is_rejected(source: str) -> None:
    """Reject malformed native bodies, array boundaries, and Python suites.

    Args:
        source: Input containing a specific structural error.
    """
    assert validate(source)
