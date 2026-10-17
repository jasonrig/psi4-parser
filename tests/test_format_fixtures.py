"""Check formatting and semantic preservation across the accepted input corpus."""

import re
from pathlib import Path

import pytest

from psi4_parser import format_source

_FIXTURES = Path(__file__).resolve().parents[1] / "test/fixtures/positive"
_INPUTS = sorted(_FIXTURES.rglob("*.dat"))


@pytest.mark.parametrize(
    "path", _INPUTS, ids=[str(path.relative_to(_FIXTURES)) for path in _INPUTS]
)
def test_format_fixture(path: Path) -> None:
    """Format every accepted grammar fixture and preserve its complete program.

    Args:
        path: Accepted upstream or conformance input.
    """
    source = path.read_bytes().decode("utf-8")

    formatted = format_source(source)

    # Block separation may add or remove empty lines. Every nonblank data,
    # Python and comment row keeps its original physical newline spelling.
    before = _record_breaks(source)
    after = _record_breaks(formatted)
    assert len(after) == len(before)
    for original, candidate in zip(before, after, strict=True):
        assert original == candidate or (
            not original and candidate in {"\n", "\r", "\r\n"}
        )


def _record_breaks(source: str) -> list[str]:
    return [
        source[match.start(2) : match.end(2)]
        for match in re.finditer(r"([^\r\n]*)(\r\n|\r|\n|$)", source)
        if source[match.start(1) : match.end(1)].strip()
    ]
