"""Execute checked inputs in a separately configured Psi4 environment."""

import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser.builder import ElectronicState, Molecule, assemble_fragments, molecule
from psi4_parser.formal import (
    Calculation,
    Model,
    Plan,
    Setting,
    Subsystem,
    UsesGeometry,
    render,
)

_PYTHON = os.environ.get("PSI4_PYTHON")


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for execution checks")
def test_optimized_geometry_and_options_are_isolated(tmp_path: Path) -> None:
    """Preserve geometry snapshots and restore settings in the real engine.

    Args:
        tmp_path: Isolated directory for Psi4 scratch and output files.
    """
    assert _PYTHON is not None
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .85\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    model = Model(
        method="scf",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    plan = Plan(
        molecules=(molecule("h2", geometry),),
        steps=(
            Calculation(id="first", driver="optimize", geometry="h2", model=model),
            Calculation(id="second", driver="optimize", geometry="first", model=model),
            Calculation(id="freq", driver="frequency", geometry="first", model=model),
            Calculation(id="initial", driver="energy", geometry="h2", model=model),
        ),
        requirements=(
            UsesGeometry(calculation="freq", geometry="first"),
            UsesGeometry(calculation="initial", geometry="h2"),
        ),
    )
    program = """import sys, psi4, numpy as np
psi4.core.set_output_file('psi4-output.dat', False)
psi4.set_memory('256MiB')
psi4.set_num_threads(1)
psi4.set_options({'basis': '6-31g', 'reference': 'uhf', 'scf_type': 'pk'})
original_basis = psi4.core.get_global_option('BASIS')
original_reference = psi4.core.get_option('SCF', 'REFERENCE')
namespace = {'psi4': psi4}
translated = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(translated, '<formal>', 'exec'), namespace)
molecules = namespace['formal_geometries']
energies = namespace['formal_results']
def bond(molecule):
    xyz = molecule.geometry().np
    return float(np.linalg.norm(xyz[1] - xyz[0]))
assert molecules['first'] is not molecules['second']
assert molecules['h2'] is not molecules['first']
assert abs(bond(molecules['h2']) - 0.85 / psi4.constants.bohr2angstroms) < 1e-8
assert abs(bond(molecules['first']) - bond(molecules['h2'])) > 0.01
assert abs(energies['first'] - energies['freq']) < 1e-8
assert energies['initial'] > energies['first']
assert psi4.core.get_global_option('BASIS') == original_basis
assert psi4.core.get_option('SCF', 'REFERENCE') == original_reference
print('isolated')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit reference interpreter and fixed test program.
        [_PYTHON, "-c", program],
        input=render(plan),
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("isolated")


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for execution checks")
def test_composite_energy_matches_independent_formula(tmp_path: Path) -> None:
    """Check the generated mixed-model energy expression in the real engine.

    Args:
        tmp_path: Isolated directory for Psi4 scratch and output files.
    """
    assert _PYTHON is not None
    example = Path(__file__).parents[1] / "examples" / "23-formal-composite"
    plan = Plan.model_validate_json((example / "plan.json").read_text())
    source = render(plan)
    assert source == (example / "input.dat").read_text()
    program = """import sys, psi4, math
psi4.core.set_output_file('psi4-output.dat', False)
psi4.set_memory('256MiB')
psi4.set_num_threads(1)
namespace = {'psi4': psi4}
translated = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(translated, '<formal>', 'exec'), namespace)
energies = namespace['formal_results']
expected = energies['hf_large'] + energies['mp2_small'] - energies['hf_small']
assert math.isclose(energies['estimate'], expected, rel_tol=0, abs_tol=1e-12)
assert energies['mp2_small'] < energies['hf_small']
print('combined')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit reference interpreter and fixed test program.
        [_PYTHON, "-c", program],
        input=source,
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("combined")


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for execution checks")
def test_full_basis_subsystem_preserves_centers_and_parent(tmp_path: Path) -> None:
    """Check actual ghost-center assignments in a separate real-engine harness.

    Args:
        tmp_path: Isolated directory for Psi4 scratch and output.
    """
    assert _PYTHON is not None
    left = Molecule.from_xyz(
        "1\nHe\nHe 0 0 0\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    right = Molecule.from_xyz(
        "1\nHe\nHe 0 0 3\n", state=ElectronicState(charge=0, multiplicity=1)
    )
    assembled = assemble_fragments(
        ("A", left), ("B", right), state=ElectronicState(charge=0, multiplicity=1)
    )
    geometry = Molecule(
        atoms=assembled.atoms,
        fragments=assembled.fragments,
        state=assembled.state,
        fixed_com=True,
        fixed_orientation=True,
    )
    model = Model(
        method="scf",
        basis="sto-3g",
        reference="rhf",
        settings=(Setting(name="scf_type", value="PK"),),
    )
    plan = Plan(
        molecules=(molecule("dimer", geometry),),
        steps=(
            Subsystem(
                id="a",
                geometry="dimer",
                real_fragments=("A",),
                state=ElectronicState(charge=0, multiplicity=1),
            ),
            Calculation(id="ea", driver="energy", geometry="a", model=model),
            Subsystem(
                id="b",
                geometry="dimer",
                real_fragments=("B",),
                state=ElectronicState(charge=0, multiplicity=1),
            ),
            Calculation(id="eb", driver="energy", geometry="b", model=model),
        ),
        requirements=(
            UsesGeometry(calculation="ea", geometry="a"),
            UsesGeometry(calculation="eb", geometry="b"),
        ),
    )
    program = """import sys, psi4, numpy as np
psi4.core.set_output_file('psi4-output.dat', False)
psi4.set_memory('256MiB')
psi4.set_num_threads(1)
psi4.set_options({'scf_type': 'pk'})
namespace = {'psi4': psi4}
translated = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(translated, '<formal-fragments>', 'exec'), namespace)
geometries = namespace['formal_geometries']
parent, a, b = (geometries[name] for name in ('dimer', 'a', 'b'))
assert [parent.Z(i) for i in range(2)] == [2, 2]
assert [a.Z(i) for i in range(2)] == [2, 0]
assert [b.Z(i) for i in range(2)] == [0, 2]
assert np.allclose(parent.geometry().np, a.geometry().np, rtol=0, atol=1e-12)
assert np.allclose(parent.geometry().np, b.geometry().np, rtol=0, atol=1e-12)
assert a.molecular_charge() == b.molecular_charge() == 0
assert a.multiplicity() == b.multiplicity() == 1
print('fragment-layout')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit reference interpreter and fixed test program.
        [_PYTHON, "-c", program],
        input=render(plan),
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("fragment-layout")
