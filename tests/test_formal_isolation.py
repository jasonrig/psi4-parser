"""Check native option isolation in a separate development-only interpreter."""

import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser import builder
from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import Calculation, Model, Plan, Setting, UsesGeometry, render


def test_builder_isolation_is_configuration_for_all_driver_helpers() -> None:
    """Keep scope control in the saved job without forwarding it to Psi4."""
    steps = (
        builder.energy("scf", isolate_options=True),
        builder.gradient("scf", isolate_options=True),
        builder.hessian("scf", isolate_options=True),
        builder.optimize("scf", isolate_options=True),
        builder.frequency("scf", isolate_options=True),
        builder.properties("scf", isolate_options=True),
    )

    for step in steps:
        saved = builder.JobSpec.model_validate_json(
            builder.compose(step).model_dump_json()
        )
        assert saved.components == (step,)
        assert step.isolate_options
        assert not any(item.name == "isolate_options" for item in step.kwargs)
    source = builder.render_job(builder.compose(*steps))
    assert "psi4_parser" not in source
    assert not builder.energy("scf").isolate_options


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native builder option scopes",
)
def test_builder_isolation_after_an_unexecuted_branch(tmp_path: Path) -> None:
    """Make scope support available even when its first nested use is skipped.

    Args:
        tmp_path: Isolated native interpreter workspace.
    """
    skipped = builder.compose(builder.energy("skip", isolate_options=True))
    job = builder.compose(
        builder.if_else(False, skipped),
        builder.energy("active", isolate_options=True),
    )
    program = """import sys, psi4
core = psi4.core
core.set_output_file('scope.dat', False)
default = core.get_global_option('MAXITER')
core.set_global_option('MAXITER', 7)
core.get_options().set_current_module('SCF')
calls = []
def observe(name):
    assert core.get_global_option('MAXITER') == default
    calls.append(name)
psi4.energy = observe
source = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(source, '<builder-scope>', 'exec'), {'psi4': psi4})
assert core.get_options().get_current_module() == 'SCF'
assert core.get_global_option('MAXITER') == 7
assert core.has_global_option_changed('MAXITER')
assert calls == ['active']
print('nested scope available')
"""

    completed = subprocess.run(  # noqa: S603 - Fixed native scope harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=builder.render_job(job),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("nested scope available")


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for failed option setup cleanup",
)
def test_failed_local_option_setup_restores_native_state(tmp_path: Path) -> None:
    """Restore state when an invalid setting prevents the driver from starting.

    Args:
        tmp_path: Isolated native interpreter workspace.
    """
    job = builder.compose(
        builder.energy(
            "scf",
            isolate_options=True,
            local_options=(builder.options(scf_type="unsupported", maxiter=11),),
        )
    )
    program = """import sys, psi4
core = psi4.core
core.set_output_file('setup.dat', False)
core.set_global_option('MAXITER', 7)
core.set_global_option('SCF_TYPE', 'PK')
calls = []
def observe(name):
    calls.append(name)
psi4.energy = observe
source = psi4.process_input(sys.stdin.read(), print_level=0)
try:
    exec(compile(source, '<failed-setup>', 'exec'), {'psi4': psi4})
except RuntimeError as error:
    assert 'UNSUPPORTED' in str(error)
else:
    raise AssertionError('invalid setting was accepted')
assert calls == []
assert core.get_global_option('MAXITER') == 7
assert core.get_global_option('SCF_TYPE') == 'PK'
assert core.has_global_option_changed('MAXITER')
assert core.has_global_option_changed('SCF_TYPE')
print('failed setup restored')
"""

    completed = subprocess.run(  # noqa: S603 - Fixed native input-configuration harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=builder.render_job(job),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("failed setup restored")


@pytest.mark.skipif(
    os.environ.get("PSI4_PYTHON") is None,
    reason="Set PSI4_PYTHON for native option-scope checks",
)
@pytest.mark.parametrize("failure", [False, True])
def test_formal_calls_reset_and_restore_native_options(
    tmp_path: Path,
    failure: bool,
) -> None:
    """Use clean effective options and restore ambient state even after failure.

    Args:
        tmp_path: Isolated engine output directory.
        failure: Raise from the observed driver instead of completing both calls.
    """
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    plan = Plan(
        molecules=(molecule("h2", geometry),),
        steps=(
            Calculation(
                id="first",
                driver="energy",
                geometry="h2",
                model=Model(
                    method="mp2",
                    basis="sto-3g",
                    reference="rhf",
                    settings=(
                        Setting(name="scf_type", value="PK"),
                        Setting(name="qc_module", value="OCC"),
                        Setting(name="e_convergence", module="SCF", value=1e-10),
                    ),
                ),
            ),
            Calculation(
                id="second",
                driver="energy",
                geometry="h2",
                model=Model(
                    method="scf",
                    basis="sto-3g",
                    reference="rhf",
                    settings=(Setting(name="scf_type", value="PK"),),
                ),
            ),
        ),
        requirements=(UsesGeometry(calculation="second", geometry="h2"),),
    )
    program = f"""import sys, psi4
psi4.core.set_output_file('options.dat', False)
core = psi4.core
default_convergence = core.get_option('SCF', 'E_CONVERGENCE')
default_iterations = core.get_global_option('MAXITER')
default_pressure = core.get_option('THERMO', 'P')
default_beta = core.get_option('F12', 'F12_BETA')
psi4.set_options({{'basis': '6-31g', 'maxiter': 1, 'extern': True}})
core.set_local_option('SCF', 'REFERENCE', 'UHF')
core.set_local_option('SCF', 'BASIS', '6-31g')
core.set_local_option('SCF', 'SCF_TYPE', 'DF')
core.set_local_option('SCF', 'E_CONVERGENCE', 0.02)
core.revoke_local_option_changed('SCF', 'E_CONVERGENCE')
core.set_local_option('SCF', 'DOCC', [1])
core.set_local_option('THERMO', 'P', 40000.)
core.set_local_option('F12', 'F12_BETA', 7.)
core.get_options().set_current_module('SCF')
calls = []
sentinel = RuntimeError('deliberate driver failure')
def observe(name, **kwargs):
    assert core.get_option('SCF', 'REFERENCE') == 'RHF'
    assert core.get_option('SCF', 'BASIS') == 'STO-3G'
    assert core.get_option('SCF', 'SCF_TYPE') == 'PK'
    assert core.get_global_option('MAXITER') == default_iterations
    assert core.get_global_option('EXTERN') == 0
    assert core.get_option('SCF', 'DOCC') == []
    assert core.get_option('THERMO', 'P') == default_pressure
    assert core.get_option('F12', 'F12_BETA') == default_beta
    assert core.get_global_option('QC_MODULE') == ('OCC' if name == 'mp2' else '')
    convergence = 1e-10 if name == 'mp2' else default_convergence
    assert core.get_option('SCF', 'E_CONVERGENCE') == convergence
    calls.append(name)
    core.set_global_option('MAXITER', 765)
    core.set_local_option('THERMO', 'P', 20000.)
    if {failure!r}:
        raise sentinel
    return 0.
psi4.energy = observe
namespace = {{'psi4': psi4}}
translated = psi4.process_input(sys.stdin.read(), print_level=0)
try:
    exec(compile(translated, '<formal-options>', 'exec'), namespace)
except RuntimeError as error:
    assert error is sentinel
    assert {failure!r}
else:
    assert not {failure!r}
assert calls == (['mp2'] if {failure!r} else ['mp2', 'scf'])
assert core.get_global_option('BASIS') == '6-31G'
assert core.get_global_option('MAXITER') == 1
assert core.get_global_option('EXTERN') == 1
assert core.get_global_option('QC_MODULE') == ''
assert not core.has_global_option_changed('QC_MODULE')
assert core.get_local_option('SCF', 'REFERENCE') == 'UHF'
assert core.get_local_option('SCF', 'BASIS') == '6-31G'
assert core.get_local_option('SCF', 'SCF_TYPE') == 'DF'
assert core.get_local_option('SCF', 'E_CONVERGENCE') == 0.02
assert not core.has_local_option_changed('SCF', 'E_CONVERGENCE')
assert core.get_local_option('SCF', 'DOCC') == [1]
assert core.has_local_option_changed('SCF', 'DOCC')
assert core.get_local_option('THERMO', 'P') == 40000.
assert core.get_local_option('F12', 'F12_BETA') == 7.
assert core.has_local_option_changed('F12', 'F12_BETA')
print('option scope restored')
"""
    completed = subprocess.run(  # noqa: S603 - Explicit interpreter and fixed development harness.
        [os.environ["PSI4_PYTHON"], "-c", program],
        input=render(plan),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.strip().endswith("option scope restored")
