"""Exercise validation, job conversion, and schema export through the public CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from jsonschema import Draft202012Validator
from pydantic import JsonValue, TypeAdapter

from psi4_parser.cli import main
from psi4_parser.job import Molecule, SetOptions, read_job

_JSON = TypeAdapter(JsonValue)


def _invoke(arguments: list[str], stdin: str | bytes | None = None) -> Result:
    # PyCharm treats Click-decorated commands as plain callback functions.
    # noinspection PyTypeChecker
    return CliRunner().invoke(main, arguments, input=stdin)


@pytest.mark.parametrize(
    ("source", "expected"),
    [("set basis sto-3g\nenergy('scf')\n", 0), ("return 1\n", 1)],
)
def test_validate_psithon_from_stdin(source: str, expected: int) -> None:
    """Report validation failures on stderr while leaving stdout available for pipes.

    Args:
        source: Complete Psithon input with or without a Python scope error.
        expected: Validation exit status.
    """
    result = _invoke(["validate", "--from", "psithon", "-"], source)

    assert result.exit_code == expected
    assert result.stdout == ""
    if expected:
        assert "stdin:1:" in result.stderr
    else:
        assert result.stderr == ""


@pytest.mark.parametrize(
    ("document", "expected"),
    [
        ('{"body":[{"kind":"python","source":"x = 1"}]}', 0),
        ('{"body":[{"kind":"python","source":"return 1"}]}', 1),
        ('{"body":[{"source":"x = 1"}]}', 1),
        ('{"body":[],"unexpected":true}', 1),
        ('{"body":', 1),
    ],
)
def test_validate_json_checks_structure_and_python_context(
    document: str, expected: int
) -> None:
    """Check contextual Python syntax as well as JSON structure and variant tags.

    Args:
        document: Job JSON covering structural and contextual validation.
        expected: Validation exit status.
    """
    result = _invoke(["validate", "--from", "json"], document)

    assert result.exit_code == expected
    assert result.stdout == ""
    assert bool(result.stderr) == bool(expected)


def test_convert_molecular_job_through_json() -> None:
    """Expose native molecule and option components and regenerate validated Psithon."""
    source = (
        "molecule h2 {\n0 1\nH 0 0 0\nH 0 0 0.74\n}\nset basis sto-3g\nenergy('scf')\n"
    )

    encoded = _invoke(["convert", "--from", "psithon", "--to", "json"], source)

    assert encoded.exit_code == 0, encoded.output
    assert encoded.stderr == ""
    document = _JSON.validate_json(encoded.stdout)
    assert isinstance(document, dict)
    body = document["body"]
    assert isinstance(body, list)
    molecule = body[0]
    assert isinstance(molecule, dict)
    assert molecule["kind"] == "molecule"
    assert molecule["name"] == "h2"

    decoded = _invoke(["convert", "--from", "json", "--to", "psithon"], encoded.stdout)

    assert decoded.exit_code == 0, decoded.output
    assert decoded.stderr == ""
    job = read_job(decoded.stdout)
    molecule_node = job.body[0]
    assert isinstance(molecule_node, Molecule)
    assert len(molecule_node.atoms) == 2
    assert isinstance(job.body[1], SetOptions)
    assert "energy('scf')" in decoded.stdout


def test_conversion_keeps_mixed_python_scope() -> None:
    """Retain native children inside a Python function across both representations."""
    source = "def build():\n    molecule h2 {\nH\nH 1 0.74\n}\n    return h2\n"

    encoded = _invoke(["convert", "--from", "psithon", "--to", "json"], source)
    assert encoded.exit_code == 0, encoded.output
    decoded = _invoke(["convert", "--from", "json", "--to", "psithon"], encoded.stdout)

    assert decoded.exit_code == 0, decoded.output
    assert "    return h2" in decoded.stdout
    assert _invoke(["validate"], decoded.stdout).exit_code == 0


def test_schema_describes_and_validates_converted_jobs() -> None:
    """Export a usable schema with required native variant tags."""
    result = _invoke(["schema"])

    assert result.exit_code == 0, result.output
    assert result.stderr == ""
    document = _JSON.validate_json(result.stdout)
    assert isinstance(document, dict)
    validator = Draft202012Validator(document)
    valid: JsonValue = {"body": [{"kind": "python", "source": "x = 1"}]}
    invalid: JsonValue = {"body": [{"source": "x = 1"}]}
    validator.validate(valid)
    assert not validator.is_valid(invalid)


def test_file_output_preserves_permissions(tmp_path: Path) -> None:
    """Convert a file without touching its input and replace the requested output.

    Args:
        tmp_path: Source and pre-existing output files.
    """
    source = tmp_path / "input.dat"
    output = tmp_path / "job.json"
    source.write_text("set basis sto-3g\n")
    output.write_text("previous output")
    output.chmod(0o640)

    result = _invoke(
        ["convert", str(source), "--from", "psithon", "--to", "json", "-o", str(output)]
    )

    assert result.exit_code == 0, result.output
    assert result.stdout == ""
    assert result.stderr == ""
    assert isinstance(_JSON.validate_json(output.read_text()), dict)
    assert output.stat().st_mode & 0o777 == 0o640
    assert source.read_text() == "set basis sto-3g\n"
    assert not list(tmp_path.glob(".psi4-parser-*"))


@pytest.mark.parametrize("input_format", ["psithon", "json"])
def test_failed_conversion_preserves_existing_output(
    tmp_path: Path, input_format: str
) -> None:
    """Avoid replacing files or writing partial results for an invalid job.

    Args:
        tmp_path: Existing output that must survive the failed conversion.
        input_format: Source representation with a contextual Python error.
    """
    output = tmp_path / "output"
    output.write_text("keep this")
    source = (
        "return 1"
        if input_format == "psithon"
        else '{"body":[{"kind":"python","source":"return 1"}]}'
    )
    target = "json" if input_format == "psithon" else "psithon"

    result = _invoke(
        ["convert", "--from", input_format, "--to", target, "-o", str(output)], source
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert result.stderr
    assert output.read_text() == "keep this"


def test_schema_can_create_a_new_output_file(tmp_path: Path) -> None:
    """Write a complete schema to a destination that does not yet exist.

    Args:
        tmp_path: Directory for the new schema file.
    """
    output = tmp_path / "job.schema.json"

    result = _invoke(["schema", "-o", str(output)])

    assert result.exit_code == 0, result.output
    assert result.stdout == ""
    assert isinstance(_JSON.validate_json(output.read_text()), dict)


@pytest.mark.parametrize(
    "arguments",
    [
        ["convert", "--to", "json"],
        ["convert", "--from", "psithon", "--to", "python"],
        ["convert", "--from", "json", "--to", "json"],
    ],
)
def test_conversion_requires_distinct_supported_formats(arguments: list[str]) -> None:
    """Reject missing, unsupported, or identical conversion formats.

    Args:
        arguments: Missing, unsupported, or identical conversion formats.
    """
    result = _invoke(arguments, "x=1")

    assert result.exit_code == 2
    assert result.stdout == ""


def test_invalid_utf8_is_an_operation_failure() -> None:
    """Distinguish an unreadable input stream from invalid job syntax."""
    result = _invoke(["validate"], b"\xff")

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "stdin" in result.stderr


def test_output_errors_are_reported_without_partial_files(tmp_path: Path) -> None:
    """Report a missing output directory and leave the filesystem unchanged.

    Args:
        tmp_path: Existing parent of the deliberately missing output directory.
    """
    output = tmp_path / "missing" / "schema.json"

    result = _invoke(["schema", "-o", str(output)])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert str(output) in result.stderr
    assert not output.parent.exists()
