"""Require first-class AST and JSON round trips across the accepted corpus."""

from pathlib import Path

import pytest

from psi4_parser.job import Job, emit_job, read_job

_ROOT = Path(__file__).resolve().parents[1] / "test/fixtures/positive"
_INPUTS = sorted(_ROOT.rglob("*.dat"))


@pytest.mark.parametrize(
    "path", _INPUTS, ids=[str(path.relative_to(_ROOT)) for path in _INPUTS]
)
def test_job_fixture(path: Path) -> None:
    """Retain the complete native structure through JSON and emitted Psithon.

    Args:
        path: Accepted upstream, regression, or Python conformance input.
    """
    job = read_job(path.read_bytes().decode("utf-8"))

    restored = Job.model_validate_json(job.model_dump_json())
    source = emit_job(restored, validate=False)
    reparsed = read_job(source)

    assert restored == job
    assert reparsed == job
