"""Validate, convert, and format Psi4 inputs from the command line."""

import difflib
import json
import stat
import sys
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

import click
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from psi4_parser._cli_types import INPUT_FILE, OUTPUT_STREAM, SOURCE_FORMAT
from psi4_parser._files import atomic_replace
from psi4_parser.api import validate
from psi4_parser.ast import InvalidInputError
from psi4_parser.formatting import FormattingError, format_source
from psi4_parser.job import Job, emit_job, read_job
from psi4_parser.mcp import command as mcp_command

type SourceFormat = Literal["psithon", "json"]


class PreparedInput(BaseModel):
    """An input file and its proposed replacement text."""

    model_config = ConfigDict(frozen=True, strict=True)
    path: Path = Field(description="Input file path, or - for standard input.")
    original: str = Field(description="Input text as read from the source.")
    formatted: str = Field(description="Replacement text produced by the formatter.")


class _Failure(click.ClickException):
    """Distinguish an operation failure from a formatting difference."""

    exit_code = 2


@click.group()
def main() -> None:
    """Validate, convert, and format Psi4 jobs without running calculations."""


@click.command(name="validate")
@click.argument("path", type=INPUT_FILE, default="-")
@click.option(
    "--from", "input_format", type=SOURCE_FORMAT, default="psithon", show_default=True
)
def validate_input(path: Path, input_format: SourceFormat) -> None:
    """Check Psithon or AST JSON, including the complete job's Python syntax.

    Read standard input when PATH is omitted or is a dash. Exit 0 for valid
    input, 1 for invalid input, and 2 for usage or file errors.

    \f

    Args:
        path: Input file, or a dash for standard input.
        input_format: Psithon source or the high-level job's JSON representation.

    Raises:
        click.ClickException: A JSON job has invalid structure or syntax.
        click.exceptions.Exit: Psithon validation reports diagnostics.
    """  # noqa: D301 - Click separates CLI help from API documentation with a form feed.
    source = _read(path)
    if input_format == "json":
        try:
            emit_job(Job.model_validate_json(source))
        except ValueError as error:
            raise click.ClickException(f"{_label(path)}: {error}") from error
        return
    diagnostics = validate(source)
    for diagnostic in diagnostics:
        click.echo(
            f"{_label(path)}:{diagnostic.line}:{diagnostic.column}: "
            f"{diagnostic.message}",
            err=True,
        )
    if diagnostics:
        raise click.exceptions.Exit(1)


@click.command(name="convert")
@click.argument("path", type=INPUT_FILE, default="-")
@click.option("--from", "input_format", type=SOURCE_FORMAT, required=True)
@click.option("--to", "output_format", type=SOURCE_FORMAT, required=True)
@click.option("--output", "-o", type=OUTPUT_STREAM, default="-", show_default=True)
def convert(
    path: Path, input_format: SourceFormat, output_format: SourceFormat, output: Path
) -> None:
    """Convert between Psithon and high-level AST JSON after validating the job.

    Read PATH or standard input and write to --output or standard output.
    Conversion regenerates native layout and does not preserve syntax comments.

    \f

    Args:
        path: Input file, or a dash for standard input.
        input_format: Representation to read.
        output_format: Representation to write.
        output: Destination file, or a dash for standard output.

    Raises:
        click.UsageError: Input and output formats are the same.
        _Failure: The job has invalid structure or syntax.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    if input_format == output_format:
        raise click.UsageError("Choose different input and output formats")
    source = _read(path)
    try:
        job = (
            read_job(source)
            if input_format == "psithon"
            else Job.model_validate_json(source)
        )
        psithon = emit_job(job)
        result = (
            job.model_dump_json(indent=2) + "\n" if output_format == "json" else psithon
        )
    except ValueError as error:
        raise _Failure(f"{_label(path)}: {error}") from error
    _write(output, result)


@click.command(name="schema")
@click.option("--output", "-o", type=OUTPUT_STREAM, default="-", show_default=True)
def schema(output: Path) -> None:
    """Export the JSON Schema for high-level job documents.

    \f

    Args:
        output: Destination file, or a dash for standard output.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    document: dict[str, JsonValue] = Job.model_json_schema()
    _write(output, json.dumps(document, indent=2) + "\n")


@click.group(name="format")
def format_command() -> None:
    """Show, diff, check, or write verified Psithon formatting."""


@click.command(name="show")
@click.argument("path", type=INPUT_FILE, default="-")
def show(path: Path) -> None:
    """Print formatted PATH, or read standard input when PATH is omitted.

    \f

    Args:
        path: Input file, or a dash for standard input.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    _write(Path("-"), _prepare(path).formatted)


@click.command(name="diff")
@click.argument("paths", nargs=-1, type=INPUT_FILE)
def diff(paths: tuple[Path, ...]) -> None:
    """Show formatting changes for files, or read standard input without paths.

    \f

    Args:
        paths: Input files, or a single dash for standard input.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    for prepared in _prepare_all(paths):
        path, before, after = prepared.path, prepared.original, prepared.formatted
        if before != after:
            _show_diff(_label(path), before, after)


@click.command(name="check")
@click.argument("paths", nargs=-1, type=INPUT_FILE)
def check(paths: tuple[Path, ...]) -> None:
    """Check formatting without writing files, or read standard input without paths.

    Exit 0 when unchanged, 1 when formatting is needed, and 2 if checking fails.

    \f

    Args:
        paths: Input files, or a single dash for standard input.

    Raises:
        click.exceptions.Exit: At least one valid input needs formatting.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    changed = False
    for prepared in _prepare_all(paths):
        path, before, after = prepared.path, prepared.original, prepared.formatted
        if before != after:
            changed = True
            click.echo("Would reformat " + _label(path), err=True)
    if changed:
        raise click.exceptions.Exit(1)


@click.command(name="write")
@click.argument("paths", nargs=-1, type=INPUT_FILE, required=True)
def write(paths: tuple[Path, ...]) -> None:
    """Replace files with formatted input after every input has verified.

    Preserve file permissions and newline conventions. Standard input is not
    accepted. Each changed file is replaced atomically.

    \f

    Args:
        paths: Files to format in place.

    Raises:
        click.UsageError: Standard input is requested.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    if Path("-") in paths:
        raise click.UsageError("write requires file paths")
    for prepared in _prepare_all(paths):
        path, before, after = prepared.path, prepared.original, prepared.formatted
        if before != after:
            _write(path, after)


@runtime_checkable
class _BinaryStream(Protocol):
    def read(self) -> bytes: ...
    def write(self, data: bytes) -> int: ...


def _binary_stream(stream: object) -> _BinaryStream:
    if not isinstance(stream, _BinaryStream):
        raise _Failure("A binary standard stream is required")
    return stream


def _label(path: Path) -> str:
    return "stdin" if path == Path("-") else str(path)


def _read(path: Path) -> str:
    try:
        if path == Path("-"):
            # TextIO.buffer is dynamically typed in typeshed; check its binary API.
            buffer: object = sys.stdin.buffer
            content = _binary_stream(buffer).read()
        else:
            content = path.read_bytes()
        return content.decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise _Failure(f"{_label(path)}: {error}") from error


def _write(path: Path, source: str) -> None:
    try:
        if path == Path("-"):
            buffer: object = sys.stdout.buffer
            _binary_stream(buffer).write(source.encode("utf-8"))
        else:
            _replace(path, source)
    except OSError as error:
        raise _Failure(f"{path}: {error}") from error


def _prepare_all(paths: tuple[Path, ...]) -> list[PreparedInput]:
    inputs = paths or (Path("-"),)
    if len(inputs) > 1 and Path("-") in inputs:
        raise click.UsageError("Standard input must be the only input")
    return [_prepare(path) for path in inputs]


def _prepare(path: Path) -> PreparedInput:
    before = _read(path)
    try:
        return PreparedInput(
            path=path, original=before, formatted=format_source(before)
        )
    except (InvalidInputError, FormattingError) as error:
        raise _Failure(f"{_label(path)}: {error}") from error


def _show_diff(label: str, before: str, after: str) -> None:
    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=label,
        tofile=label + " (formatted)",
    )
    delta = "".join(
        line
        if line.endswith(("\r", "\n"))
        else line + "\n\\ No newline at end of file\n"
        for line in lines
    )
    _write(Path("-"), delta)


def _replace(path: Path, source: str) -> None:
    target = path.resolve()
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else None
    atomic_replace(target, source.encode("utf-8"), mode=mode)


main.add_command(validate_input)
main.add_command(convert)
main.add_command(schema)
main.add_command(format_command)
main.add_command(mcp_command)
format_command.add_command(show)
format_command.add_command(diff)
format_command.add_command(check)
format_command.add_command(write)
