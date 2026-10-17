"""Regenerate the Python parser from the checked-in ANTLR grammars."""

import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import click


@click.command()
@click.option(
    "--project",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path(__file__).resolve().parents[3],
    show_default=True,
    help="Parser checkout containing grammar/.",
)
def main(project: Path) -> None:
    """Generate with antlr4-tools and the installed runtime's ANTLR version.

    \f

    Args:
        project: Parser checkout containing the maintained ANTLR grammars.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    root = project.resolve()
    output = root / "src/psi4_parser/_generated"
    subprocess.run(  # noqa: S603 - Fixed compiler command; never executes input jobs.
        [
            str(Path(sys.executable).with_name("antlr4")),
            "-v",
            version("antlr4-python3-runtime"),
            "-Dlanguage=Python3",
            "-no-listener",
            "-Xexact-output-dir",
            "-lib",
            "grammar",
            "-o",
            str(output),
            "grammar/PythonLexer.g4",
            "grammar/PythonParser.g4",
            "grammar/PsithonLexer.g4",
            "grammar/PsithonParser.g4",
        ],
        cwd=root,
        check=True,
    )
    lexer = output / "PsithonLexer.py"
    lexer.write_text(
        lexer.read_text().replace(
            "from .PsithonLexerBase import", "from ..lexer_base import"
        )
    )
    # Imported Python grammars are compiled for their token vocabulary. The
    # resulting Psithon classes contain their rules and need no duplicate classes.
    for name in ("PythonLexer", "PythonParser"):
        for suffix in (".py", ".interp", ".tokens"):
            (output / (name + suffix)).unlink()


if __name__ == "__main__":
    main()
