"""Build modern external potentials with explicit dimensions."""

import ast
import os
import subprocess
from pathlib import Path

import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import (
    ExternalPointCharge,
    ExternalPotential,
    FragmentPotential,
    FragmentPotentials,
    GaussianCharge,
    JobSpec,
    PotentialMatrix,
    angstrom,
    bohr,
    compose,
    energy,
    render_job,
)

_PYTHON = os.environ.get("PSI4_PYTHON")
_JSON = TypeAdapter(JsonValue)


def test_modern_potential_is_a_serializable_driver_argument() -> None:
    """Recognize a point-charge potential without relying on raw argument arrays."""
    job = JobSpec.model_validate_json(
        '{"components":[{"kind":"calculation","driver":"energy",'
        '"method":{"kind":"literal","value":"scf"},"kwargs":['
        '{"name":"external_potentials","value":{"kind":"external_potential",'
        '"points":[{"charge":0.1,"position":['
        '{"value":0.0,"unit":"bohr"},{"value":0.0,"unit":"bohr"},'
        '{"value":1.0,"unit":"bohr"}]}]}}]}]}'
    )

    source = render_job(job)

    assert "external_potentials=" in source
    assert "'points': [[0.1, 0.0, 0.0, 1.0]]" in source
    assert JobSpec.model_validate_json(job.model_dump_json()) == job


def test_mixed_units_diffuse_charges_and_matrix_emit_atomic_units() -> None:
    """Convert positions without changing Gaussian exponents or AO matrices."""
    potential = ExternalPotential(
        points=(
            ExternalPointCharge(
                charge=0.5,
                position=(
                    angstrom(0.52917721067),
                    bohr(-2),
                    angstrom(0),
                ),
            ),
        ),
        diffuse=(
            GaussianCharge(
                charge=-0.5,
                position=(
                    bohr(0),
                    bohr(0),
                    bohr(3),
                ),
                exponent=0.7,
            ),
        ),
        matrix=PotentialMatrix(((1.0, 0.2), (0.2, -1.0))),
    )
    job = compose(energy("scf", external_potentials=potential))

    tree = ast.parse(render_job(job))
    statement = tree.body[0]
    assert isinstance(statement, ast.Expr)
    assert isinstance(statement.value, ast.Call)
    expected = ast.parse(
        "{'points': [[0.5, 1.0, -2.0, 0.0]], "
        "'diffuse': [[-0.5, 0.0, 0.0, 3.0, 0.7]], "
        "'matrix': [[1.0, 0.2], [0.2, -1.0]]}",
        mode="eval",
    )

    assert ast.dump(statement.value.keywords[0].value) == ast.dump(expected.body)
    assert JobSpec.model_validate_json(job.model_dump_json()) == job


def test_potential_variants_reject_invalid_physical_values() -> None:
    """Reject nonfinite charges, unitless positions, and malformed matrices."""
    with pytest.raises(ValidationError, match="finite"):
        ExternalPointCharge(charge=float("nan"), position=(bohr(0), bohr(0), bohr(0)))
    with pytest.raises(ValidationError, match="model_type"):
        ExternalPointCharge.model_validate_json(
            '{"charge":1.0,"position":[0.0,0.0,1.0]}'
        )
    with pytest.raises(ValidationError, match="greater than 0"):
        GaussianCharge(charge=1, position=(bohr(0), bohr(0), bohr(0)), exponent=0)
    with pytest.raises(ValidationError, match="square"):
        PotentialMatrix(((1.0, 2.0),))
    with pytest.raises(ValidationError, match="finite"):
        PotentialMatrix(((float("inf"),),))
    with pytest.raises(ValidationError, match="distinct"):
        FragmentPotentials(
            fragments=(
                FragmentPotential(fragment="A", potential=ExternalPotential()),
                FragmentPotential(fragment="A", potential=ExternalPotential()),
            )
        )


@pytest.mark.skipif(_PYTHON is None, reason="Set PSI4_PYTHON for reference checks")
def test_modern_potential_passes_psi4_normalization(tmp_path: Path) -> None:
    """Check the real potential reader without running a calculation.

    Args:
        tmp_path: Isolated directory for Psi4 preprocessing and validation.
    """
    potential = FragmentPotentials(
        fragments=(
            FragmentPotential(
                fragment="A",
                potential=ExternalPotential(
                    points=(
                        ExternalPointCharge(
                            charge=0.5, position=(bohr(0), bohr(0), bohr(2))
                        ),
                    ),
                    diffuse=(
                        GaussianCharge(
                            charge=-0.5,
                            position=(bohr(0), bohr(1), bohr(0)),
                            exponent=0.7,
                        ),
                    ),
                    matrix=PotentialMatrix(((1.0,),)),
                ),
            ),
        )
    )
    source = render_job(compose(energy("scf", external_potentials=potential)))
    program = """import json, sys, psi4
from psi4.driver.procrouting.proc import validate_external_potential
psi4.core.set_output_file('/dev/null', False)
def instrumented(*args, **kwargs):
    print(json.dumps(validate_external_potential(kwargs['external_potentials'])))
    return 0.0
psi4.energy = instrumented
lowered = psi4.process_input(sys.stdin.read(), print_level=0)
exec(compile(lowered, '<generated>', 'exec'), {})
"""
    assert _PYTHON is not None
    result = subprocess.run(  # noqa: S603 - Supplied interpreter and fixed program instrument the driver.
        [_PYTHON, "-c", program],
        input=source,
        text=True,
        capture_output=True,
        check=True,
        cwd=tmp_path,
        timeout=60,
    )

    assert _JSON.validate_json(result.stdout) == {
        "A": {
            "points": [[0.5, 0.0, 0.0, 2.0]],
            "diffuse": [[-0.5, 0.0, 1.0, 0.0, 0.7]],
            "matrix": [[1.0]],
        },
    }


def test_point_only_fragment_uses_fisapt_charge_list() -> None:
    """Keep point-only fragments compatible with FI-SAPT's field-file exporter."""
    potential = FragmentPotentials(
        fragments=(
            FragmentPotential(
                fragment="A",
                potential=ExternalPotential(
                    points=(
                        ExternalPointCharge(
                            charge=0.5, position=(bohr(0), bohr(0), bohr(2))
                        ),
                    ),
                ),
            ),
        )
    )

    source = render_job(compose(energy("fisapt0", external_potentials=potential)))
    statement = ast.parse(source).body[0]
    assert isinstance(statement, ast.Expr)
    assert isinstance(statement.value, ast.Call)

    expected = ast.parse("{'A': [[0.5, 0.0, 0.0, 2.0]]}", mode="eval")
    assert ast.dump(statement.value.keywords[0].value) == ast.dump(expected.body)
