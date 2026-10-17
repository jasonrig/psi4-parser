"""Check real ANTLR generation and preserve working files on compiler failure."""

import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from psi4_parser.maintenance.generate import main


def _project(tmp_path: Path) -> Path:
    """Copy maintained grammars and generated files into an isolated checkout.

    Args:
        tmp_path: Isolated directory for this generation attempt.

    Returns:
        Checkout containing real grammars and the previous working parser.
    """
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "grammar", tmp_path / "grammar")
    output = tmp_path / "src/psi4_parser/_generated"
    output.mkdir(parents=True)
    for path in (root / "src/psi4_parser/_generated").iterdir():
        if path.is_file():
            shutil.copy2(path, output / path.name)
    return tmp_path


def _files(project: Path) -> dict[str, bytes]:
    output = project / "src/psi4_parser/_generated"
    return {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}


@pytest.mark.parametrize(
    ("action", "error"),
    [
        (
            "# This parser's comment has an unmatched apostrophe.\n",
            subprocess.CalledProcessError,
        ),
        ("this is not valid Python\n", SyntaxError),
    ],
    ids=["antlr-action-scanner", "generated-python-syntax"],
)
def test_failed_generation_preserves_working_parser(
    tmp_path: Path, action: str, error: type[Exception]
) -> None:
    """Keep every previous artifact when compilation or Python syntax fails.

    Args:
        tmp_path: Isolated checkout with a working generated parser.
        action: Defective action inserted into the real parser grammar.
        error: Expected error from the compiler or Python syntax check.
    """
    project = _project(tmp_path)
    grammar = project / "grammar/PsithonParser.g4"
    grammar.write_text(
        grammar.read_text().replace("@members {\n", "@members {\n" + action, 1)
    )
    before = _files(project)

    result = CliRunner().invoke(main, ["--project", str(project)])

    assert isinstance(result.exception, error), result.output
    assert _files(project) == before
    assert not list((project / "src/psi4_parser").glob(".psi4-regenerate-*"))


def test_successful_generation_preserves_handwritten_files(tmp_path: Path) -> None:
    """Publish complete generated artifacts while retaining package files and stubs.

    Args:
        tmp_path: Isolated checkout with the maintained grammars and parser.
    """
    project = _project(tmp_path)
    output = project / "src/psi4_parser/_generated"
    (output / "PsithonParser.py").write_text("# Replace this stale parser.\n")
    before = _files(project)

    result = CliRunner().invoke(main, ["--project", str(project)])

    assert result.exit_code == 0, result.output
    after = _files(project)
    assert after.keys() == before.keys()
    assert b"class PsithonParser" in after["PsithonParser.py"]
    assert b"from ..lexer_base import" in after["PsithonLexer.py"]
    for name in ("__init__.py", "PsithonLexer.pyi", "PsithonParser.pyi"):
        assert after[name] == before[name]
    assert not list((project / "src/psi4_parser").glob(".psi4-regenerate-*"))
