"""Regenerate the Python parser from the checked-in ANTLR grammars."""

import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

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
    output.parent.mkdir(parents=True, exist_ok=True)
    # ANTLR can emit some files before reporting an error in a later grammar.
    # Keep all compiler output private until compilation and Python syntax pass.
    with TemporaryDirectory(prefix=".psi4-regenerate-", dir=output.parent) as work:
        staging = Path(work)
        subprocess.run(  # noqa: S603 - Fixed compiler; never executes input jobs.
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
                str(staging),
                "grammar/PythonLexer.g4",
                "grammar/PythonParser.g4",
                "grammar/PsithonLexer.g4",
                "grammar/PsithonParser.g4",
            ],
            cwd=root,
            check=True,
        )
        lexer = staging / "PsithonLexer.py"
        lexer.write_text(
            lexer.read_text(encoding="utf-8").replace(
                "from .PsithonLexerBase import", "from ..lexer_base import"
            ),
            encoding="utf-8",
        )
        artifacts = tuple(
            staging / (name + suffix)
            for name in ("PsithonLexer", "PsithonParser")
            for suffix in (".py", ".interp", ".tokens")
        )
        for artifact in artifacts:
            # Read every expected artifact before publishing any of them.
            content = artifact.read_bytes()
            if artifact.suffix == ".py":
                compile(content, str(artifact), "exec", dont_inherit=True)
        output.mkdir(exist_ok=True)
        for artifact in artifacts:
            artifact.replace(output / artifact.name)
        # Imported Python grammars supply the token vocabulary. Their duplicate
        # classes stay in staging and disappear with the temporary directory.


if __name__ == "__main__":
    main()
