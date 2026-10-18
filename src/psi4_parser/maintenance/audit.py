"""Compare the candidate parser with a matching Psi4 preprocessor and compiler."""

import json
import subprocess
from pathlib import Path
from typing import TypedDict, override

import click
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from psi4_parser._generated.PsithonLexer import PsithonLexer
from psi4_parser._generated.PsithonParser import PsithonParser
from psi4_parser.job import Job, emit_job, read_job
from psi4_parser.maintenance.reference import digest_python


class _Case(TypedDict):
    name: str
    source: str
    expected: bool
    upstream: bool


class _Result(TypedDict):
    name: str
    digest: str
    error: str


class _Errors(ErrorListener):
    def __init__(self) -> None:
        self.messages: list[str] = []

    @override
    def syntaxError(
        self,
        recognizer: object,
        offendingSymbol: object,
        line: int,
        column: int,
        msg: str,
        e: object,
    ) -> None:
        del recognizer, offendingSymbol, e
        self.messages.append(f"{line}:{column}: {msg}")


def _cases(source: Path) -> list[_Case]:
    cases: list[_Case] = [
        _Case(
            name="upstream/" + str(path.relative_to(source)),
            source=path.read_bytes().decode("utf-8"),
            expected=True,
            upstream=True,
        )
        for path in sorted((source / "tests").rglob("input.dat"))
    ]
    if not cases:
        raise ValueError("Psi4 source checkout has no tests/**/input.dat inputs")
    root = Path(__file__).resolve().parents[3] / "test/fixtures"
    for side in ("positive", "negative"):
        reference_files = sorted((root / side / "reference").rglob("*.dat"))
        if not reference_files:
            raise ValueError("Reference regression fixtures are missing: " + side)
        cases.extend(
            _Case(
                name=str(path.relative_to(root)),
                source=path.read_bytes().decode("utf-8"),
                expected=side == "positive",
                upstream=False,
            )
            for path in reference_files
        )
    return cases


def _reference_results(
    python: Path, cases: list[_Case], report: Path
) -> dict[str, _Result]:
    worker = Path(__file__).with_name("reference.py")
    payload: list[dict[str, str]] = [
        {"name": case["name"], "source": case["source"]} for case in cases
    ]
    requests = json.dumps("compile") + "\n"
    requests += "".join(json.dumps(item) + "\n" for item in payload)
    result = subprocess.run(  # noqa: S603 - Explicit reference worker, no job execution.
        [str(python), str(worker)],
        input=requests,
        capture_output=True,
        text=True,
        check=True,
        timeout=300,
        cwd=report.parent,
    )
    report.with_suffix(".reference.log").write_text(result.stderr)
    rows: list[_Result] = []
    for line in result.stdout.splitlines():
        row: _Result = json.loads(line)
        rows.append(row)
    results = {row["name"]: row for row in rows}
    if len(results) != len(cases) or len(rows) != len(cases):
        raise ValueError(
            "Reference worker returned an incomplete or duplicate result set"
        )
    if set(results) != {case["name"] for case in cases}:
        raise ValueError("Reference worker returned unexpected case names")
    return results


def _projected_digest(source: str) -> tuple[str, list[str]]:
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    lexer = PsithonLexer(InputStream(source))
    errors = _Errors()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errors)
    parser = PsithonParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(errors)
    tree = parser.file_input()
    if errors.messages:
        return "", errors.messages
    projected, _ = parser.psithon_project(tree, source)
    return digest_python(projected), errors.messages


def _native_roundtrip_error(source: str) -> str:
    try:
        original = read_job(source)
        restored = Job.model_validate_json(original.model_dump_json())
        if restored != original:
            return "native AST JSON round trip differs"
        emitted = emit_job(restored, validate=False)
        if read_job(emitted) != original:
            return "native AST Psithon round trip differs"
    except ValueError as error:
        return "native AST: " + str(error)
    return ""


def compare_cases(
    cases: list[_Case], references: dict[str, _Result]
) -> list[dict[str, str]]:
    """Collect changed reference outcomes and upstream projection mismatches.

    Args:
        cases: Current upstream inputs and compiler regression fixtures.
        references: Independently computed reference results indexed by name.

    Returns:
        Concrete case names and failure details; an empty list indicates agreement.
    """
    failures: list[dict[str, str]] = []
    for case in cases:
        reference = references[case["name"]]
        error_kind = reference["error"].split(":", 1)[0]
        permitted = {
            "SyntaxError",
            "IndentationError",
            "TabError",
            "ValueError",
            "TestComparisonError",
        }
        if reference["error"] and error_kind not in permitted:
            failures.append(
                {
                    "name": case["name"],
                    "error": "reference infrastructure: " + reference["error"],
                }
            )
        elif bool(reference["digest"]) != case["expected"]:
            failures.append(
                {"name": case["name"], "error": reference["error"] or "newly accepted"}
            )
        elif case["upstream"]:
            digest, errors = _projected_digest(case["source"])
            if errors or digest != reference["digest"]:
                failures.append(
                    {
                        "name": case["name"],
                        "error": "; ".join(errors) or "translated Python AST differs",
                    }
                )
        if case["expected"] and reference["digest"] and not reference["error"]:
            native_error = _native_roundtrip_error(case["source"])
            if native_error:
                failures.append({"name": case["name"], "error": native_error})
    return failures


@click.command()
@click.option(
    "--source",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--reference-python",
    required=True,
    type=click.Path(exists=True, dir_okay=False, executable=True, path_type=Path),
)
@click.option(
    "--report", required=True, type=click.Path(dir_okay=False, path_type=Path)
)
def main(source: Path, reference_python: Path, report: Path) -> None:
    """Write a differential report for the synchronization runner.

    \f

    Args:
        source: Current reference source checkout.
        reference_python: Interpreter exposing the matching Psi4 build.
        report: Destination for the machine-readable comparison report.

    Raises:
        click.exceptions.Exit: A reference outcome or translated AST differs.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    cases = _cases(source)
    references = _reference_results(reference_python, cases, report)
    failures = compare_cases(cases, references)
    data: dict[str, object] = {
        "inputs": len(cases),
        "upstream": sum(case["upstream"] for case in cases),
        "failures": failures,
        "pcm": "preprocessor boundaries only; controlled solver output",
    }
    report.write_text(json.dumps(data, indent=2) + "\n")
    if failures:
        raise click.exceptions.Exit(1)


if __name__ == "__main__":
    main()
