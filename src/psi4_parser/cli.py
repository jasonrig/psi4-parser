"""Provide the verified Psithon formatter as a Click command."""

import difflib
import stat
import sys
import tempfile
from pathlib import Path
from typing import Protocol, runtime_checkable

import click

from psi4_parser.ast import InvalidInputError
from psi4_parser.formatting import FormattingError, format_source


@click.command()
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, allow_dash=True, path_type=Path),
)
@click.option("--check", is_flag=True, help="Exit 1 if an input needs formatting.")
@click.option("--diff", "show_diff", is_flag=True, help="Show a unified diff.")
@click.option("--write", is_flag=True, help="Replace files after all inputs verify.")
def main(paths: tuple[Path, ...], *, check: bool, show_diff: bool, write: bool) -> None:
    """Format Psithon files, or read UTF-8 input from stdin when no path is given.

    By default, write one formatted input to stdout. Use --check, --diff or
    --write for multiple files. Verification always precedes any file changes.

    \f

    Args:
        paths: Files to format, with a single dash denoting standard input.
        check: Check formatting without writing source.
        show_diff: Show the proposed source changes.
        write: Replace each changed file atomically, preserving its permissions.

    Raises:
        click.ClickException: Reading, verification or writing an input fails.
        click.exceptions.Exit: Check mode finds an input that needs formatting.
    """  # noqa: D301 - Click separates CLI help from API documentation with a form feed.
    inputs = _inputs(paths, check=check, show_diff=show_diff, write=write)
    prepared = [_prepare(path) for path in inputs]
    changed = False
    for path, before, after in prepared:
        label = str(path) if path is not None else "stdin"
        if before != after:
            changed = True
            if check:
                click.echo("Would reformat " + label, err=True)
            elif show_diff:
                _show_diff(label, before, after)
            elif write and path is not None:
                try:
                    _replace(path, after)
                except OSError as error:
                    raise click.ClickException(f"{label}: {error}") from error
        if not any((check, show_diff, write)):
            # TextIO.buffer is dynamically typed in typeshed; narrow its actual
            # binary capability at this standard-library boundary.
            buffer: object = sys.stdout.buffer
            _binary_stream(buffer).write(after.encode("utf-8"))
    if check and changed:
        raise click.exceptions.Exit(1)


@runtime_checkable
class _BinaryStream(Protocol):
    def read(self) -> bytes: ...
    def write(self, data: bytes) -> int: ...


def _binary_stream(stream: object) -> _BinaryStream:
    if not isinstance(stream, _BinaryStream):
        raise click.ClickException("A binary standard stream is required")
    return stream


def _inputs(
    paths: tuple[Path, ...], *, check: bool, show_diff: bool, write: bool
) -> tuple[Path | None, ...]:
    if sum((check, show_diff, write)) > 1:
        raise click.UsageError("Choose only one of --check, --diff and --write")
    inputs = tuple(None if path == Path("-") else path for path in paths) or (None,)
    if write and None in inputs:
        raise click.UsageError("--write requires file paths")
    if len(inputs) > 1 and None in inputs:
        raise click.UsageError("Standard input must be the only input")
    if len(inputs) > 1 and not any((check, show_diff, write)):
        raise click.UsageError("Multiple files require --check, --diff or --write")
    return inputs


def _prepare(path: Path | None) -> tuple[Path | None, str, str]:
    label = str(path) if path is not None else "stdin"
    try:
        if path is None:
            buffer: object = sys.stdin.buffer
            content = _binary_stream(buffer).read()
        else:
            content = path.read_bytes()
        before = content.decode("utf-8")
        return path, before, format_source(before)
    except (OSError, UnicodeDecodeError, InvalidInputError, FormattingError) as error:
        raise click.ClickException(f"{label}: {error}") from error


def _show_diff(label: str, before: str, after: str) -> None:
    lines = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=label,
        tofile=label + " (formatted)",
        lineterm="",
    )
    click.echo("\n".join(lines))


def _replace(path: Path, source: str) -> None:
    target = path.resolve()
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=target.parent, prefix=".psi4-format-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(source.encode("utf-8"))
        temporary.chmod(stat.S_IMODE(target.stat().st_mode))
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
