"""Verify the installed formatter command's input and file-write contracts."""

from pathlib import Path

from click.testing import CliRunner

from psi4_parser.cli import main


def test_stdin_output() -> None:
    """Format standard input without adding status text to standard output."""
    result = CliRunner().invoke(main, input="x=1")

    assert result.exit_code == 0, result.output
    assert result.stdout == "x = 1\n"


def test_check_and_diff_do_not_modify_files(tmp_path: Path) -> None:
    """Report source changes without writing either inspection mode.

    Args:
        tmp_path: Isolated input directory.
    """
    path = tmp_path / "input.dat"
    path.write_bytes(b"x=1\r\n")
    runner = CliRunner()

    check = runner.invoke(main, ["--check", str(path)])
    diff = runner.invoke(main, ["--diff", str(path)])

    assert check.exit_code == 1
    assert "Would reformat" in check.stderr
    assert diff.exit_code == 0
    assert "-x=1" in diff.stdout
    assert "+x = 1" in diff.stdout
    assert path.read_bytes() == b"x=1\r\n"


def test_write_preserves_permissions_and_newlines(tmp_path: Path) -> None:
    """Replace verified files while preserving physical newlines and permissions.

    Args:
        tmp_path: Isolated input directory.
    """
    path = tmp_path / "input.dat"
    path.write_bytes(b"x=1\r\n")
    path.chmod(0o640)

    result = CliRunner().invoke(main, ["--write", str(path)])

    assert result.exit_code == 0, result.output
    assert path.read_bytes() == b"x = 1\r\n"
    assert path.stat().st_mode & 0o777 == 0o640
    assert not list(tmp_path.glob(".psi4-format-*"))
    assert CliRunner().invoke(main, ["--check", str(path)]).exit_code == 0


def test_invalid_later_input_prevents_all_writes(tmp_path: Path) -> None:
    """Validate every input before modifying any file in a batch.

    Args:
        tmp_path: Isolated input directory.
    """
    good, bad = tmp_path / "good.dat", tmp_path / "bad.dat"
    good.write_text("x=1\n")
    bad.write_text("return 1\n")

    result = CliRunner().invoke(main, ["--write", str(good), str(bad)])

    assert result.exit_code != 0
    assert "bad.dat" in result.stderr
    assert good.read_text() == "x=1\n"
    assert bad.read_text() == "return 1\n"


def test_write_requires_real_paths() -> None:
    """Reject a write request for standard input before consuming it."""
    result = CliRunner().invoke(main, ["--write"], input="x=1")

    assert result.exit_code == 2
    assert "requires file paths" in result.stderr
