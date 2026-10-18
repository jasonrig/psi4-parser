"""Check atomic replacement failure cleanup and preservation of original bytes."""

import os
from pathlib import Path

import pytest

# noinspection PyProtectedMember
from psi4_parser._files import atomic_replace


def test_failed_content_synchronization_preserves_the_original_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Remove the temporary artifact when synchronizing its contents fails.

    Args:
        tmp_path: Isolated directory containing the original file.
        monkeypatch: Injects a disk-synchronization error before replacement.
    """
    target = tmp_path / "input.dat"
    target.write_bytes(b"original")

    def fail(descriptor: int) -> None:
        del descriptor
        raise OSError("synchronization failed")

    monkeypatch.setattr(os, "fsync", fail)
    with pytest.raises(OSError, match="synchronization failed"):
        atomic_replace(target, b"replacement", sync=True)
    assert target.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [target]
