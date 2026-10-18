"""Verify the installed formatter command's input and file-write contracts."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from psi4_parser.cli import main

# PyCharm treats Click-decorated commands as plain callback functions.


def test_stdin_output() -> None:
    """Format standard input without adding status text to standard output."""
    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "show"], input="x=1")

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

    # noinspection PyTypeChecker
    check = runner.invoke(main, ["format", "check", str(path)])
    # noinspection PyTypeChecker
    diff = runner.invoke(main, ["format", "diff", str(path)])

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

    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "write", str(path)])

    assert result.exit_code == 0, result.output
    assert path.read_bytes() == b"x = 1\r\n"
    assert path.stat().st_mode & 0o777 == 0o640
    assert not list(tmp_path.glob(".psi4-parser-*"))
    # noinspection PyTypeChecker
    assert CliRunner().invoke(main, ["format", "check", str(path)]).exit_code == 0


def test_invalid_later_input_prevents_all_writes(tmp_path: Path) -> None:
    """Validate every input before modifying any file in a batch.

    Args:
        tmp_path: Isolated input directory.
    """
    good, bad = tmp_path / "good.dat", tmp_path / "bad.dat"
    good.write_text("x=1\n")
    bad.write_text("return 1\n")

    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "write", str(good), str(bad)])

    assert result.exit_code == 2
    assert "bad.dat" in result.stderr
    assert good.read_text() == "x=1\n"
    assert bad.read_text() == "return 1\n"


def test_write_requires_real_paths() -> None:
    """Reject a write request for standard input before consuming it."""
    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "write", "-"], input="x=1")

    assert result.exit_code == 2
    assert "requires file paths" in result.stderr


@pytest.mark.parametrize(
    ("source", "expected"), [("x = 1\n", 0), ("x=1", 1), ("return 1", 2)]
)
def test_check_distinguishes_changes_from_invalid_input(
    source: str, expected: int
) -> None:
    """Distinguish formatted input, formatting differences, and failed validation.

    Args:
        source: Standard input covering each check outcome.
        expected: Exit status promised by the formatting command.
    """
    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "check", "-"], input=source)

    assert result.exit_code == expected
    assert result.stdout == ""


def test_format_operations_cannot_be_combined() -> None:
    """Reject an operation flag rather than treating it as a modifier of check."""
    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "check", "--diff"], input="x=1")

    assert result.exit_code == 2
    assert "No such option" in result.stderr
    assert "--diff" in result.stderr


def test_diff_reports_a_missing_final_newline() -> None:
    """Show an EOF newline change when the visible source is already formatted."""
    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "diff"], input="x = 1")

    assert result.exit_code == 0, result.output
    assert "-x = 1\n\\ No newline at end of file\n+x = 1\n" in result.stdout


@pytest.mark.parametrize("operation", ["diff", "check", "write"])
def test_multiple_files_are_validated_before_any_output(
    tmp_path: Path, operation: str
) -> None:
    """Avoid partial diffs, change reports, or writes when a later input is invalid.

    Args:
        tmp_path: Isolated valid and invalid inputs.
        operation: Multi-file formatting operation under test.
    """
    good, bad = tmp_path / "good.dat", tmp_path / "bad.dat"
    good.write_text("x=1\n")
    bad.write_text("return 1\n")

    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", operation, str(good), str(bad)])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "Would reformat" not in result.stderr
    assert good.read_text() == "x=1\n"


def test_stdin_cannot_be_mixed_with_files(tmp_path: Path) -> None:
    """Reject an ambiguous multi-input stream before reading standard input.

    Args:
        tmp_path: Existing file accompanying the dash argument.
    """
    path = tmp_path / "input.dat"
    path.write_text("x=1\n")

    # noinspection PyTypeChecker
    result = CliRunner().invoke(main, ["format", "diff", "-", str(path)], input="x=2")

    assert result.exit_code == 2
    assert "Standard input must be the only input" in result.stderr
