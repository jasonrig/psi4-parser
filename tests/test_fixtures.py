"""Validate the curated fixture corpus and compare paired cases with Psi4."""

import os
import subprocess
from pathlib import Path

import pytest

from psi4_parser import parse

_FIXTURES = Path(__file__).resolve().parents[1] / "test/fixtures"
_INPUTS = sorted(_FIXTURES.glob("**/*.dat"))
_PAIRS = [
    path for path in _INPUTS if path.relative_to(_FIXTURES).parts[1] == "conformance"
]
_BINARY = os.environ.get("PSI4_BINARY")


def test_conformance_pairs() -> None:
    """Require a positive counterpart for every negative conformance input."""
    positive = _FIXTURES / "positive/conformance"
    negative = _FIXTURES / "negative/conformance"

    assert {path.relative_to(positive) for path in positive.rglob("*.dat")} == {
        path.relative_to(negative) for path in negative.rglob("*.dat")
    }


@pytest.mark.parametrize(
    "path", _INPUTS, ids=[str(path.relative_to(_FIXTURES)) for path in _INPUTS]
)
def test_fixture(path: Path) -> None:
    """Enforce the expected result recorded by each fixture directory.

    Args:
        path: Curated input in the positive or negative directory.
    """
    expected_rejection = path.relative_to(_FIXTURES).parts[0] == "negative"

    source = path.read_bytes().decode("utf-8")
    result = parse(source)

    assert bool(result.diagnostics) == expected_rejection, (path, result.diagnostics)
    assert result.source == source
    for token in result.tokens.tokens:
        start, stop = result.source_span(token)
        assert 0 <= start <= stop <= len(source), (path, token)


@pytest.mark.skipif(_BINARY is None, reason="Set PSI4_BINARY for launcher checks")
@pytest.mark.parametrize(
    "path", _PAIRS, ids=[str(path.relative_to(_FIXTURES)) for path in _PAIRS]
)
def test_psi4_launcher(path: Path, tmp_path: Path) -> None:
    """Check paired language constraints through the actual Psi4 launcher.

    Args:
        path: Paired input with guarded Python or a small native geometry.
        tmp_path: Isolated output and scratch directory for the launcher.
    """
    assert _BINARY is not None
    expected_rejection = path.relative_to(_FIXTURES).parts[0] == "negative"
    output = tmp_path / "output.dat"

    result = subprocess.run(  # noqa: S603 - Explicit reference binary and curated inputs.
        [
            _BINARY,
            "-i",
            str(path),
            "-o",
            str(output),
            "-s",
            str(tmp_path),
            "-n",
            "1",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    log = result.stdout + result.stderr + output.read_text()

    if expected_rejection:
        assert result.returncode == 1, log
        errors = (
            "SyntaxError:",
            "MoleculeFormatError:",
            "TestComparisonError:",
            "ValidationError:",
            "ValueError:",
            "TabError:",
            "IndentationError:",
        )
        assert any(error in log for error in errors), log
    else:
        assert result.returncode == 0, log
