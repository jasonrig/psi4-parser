"""Check all native input.dat files in a Psi4 source tree without executing them."""

import json
import time
from pathlib import Path
from typing import TypedDict

import click

from psi4_parser import validate


class _Report(TypedDict):
    inputs: int
    accepted: int
    seconds: float
    failures: dict[str, list[str]]


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(source: Path) -> None:
    """Print the acceptance count and source diagnostics as a JSON report.

    \f

    Args:
        source: Psi4 source checkout containing tests/**/input.dat.

    Raises:
        click.ClickException: No input files were found.
        click.exceptions.Exit: Any input failed validation.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    files = sorted((source / "tests").rglob("input.dat"))
    if not files:
        raise click.ClickException(
            "Psi4 source tree contains no tests/**/input.dat files"
        )
    started = time.monotonic()
    failures: dict[str, list[str]] = {}
    for path in files:
        errors = validate(path.read_text())
        if errors:
            failures[str(path.relative_to(source))] = [
                f"{error.line}:{error.column}: {error.message}" for error in errors[:3]
            ]
    report: _Report = {
        "inputs": len(files),
        "accepted": len(files) - len(failures),
        "seconds": round(time.monotonic() - started, 2),
        "failures": failures,
    }
    click.echo(json.dumps(report, indent=2))
    if failures:
        raise click.exceptions.Exit(1)


if __name__ == "__main__":
    main()
