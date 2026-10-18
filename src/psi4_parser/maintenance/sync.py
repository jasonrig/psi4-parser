"""Stage, verify and promote compatible upgrades from supplied Psi4 paths."""

import contextlib
import difflib
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator, Sequence
from pathlib import Path

import click
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from psi4_parser.maintenance.reference import PSI4_SOURCES
from psi4_parser.maintenance.state import (
    Baseline,
    Snapshot,
    content_hash,
    guarded_changes,
    read_baseline,
    read_snapshot,
    refresh_inventories,
)

_DIRECTORIES = ("src", "grammar", "tests", "test", "typings")
_FILES = ("pyproject.toml", "uv.lock")
_BASELINE = Path("compatibility/psi4.json")
_GRAMMAR = Path("grammar/PsithonParser.g4")


class Settings(BaseSettings):
    """Validate synchronization inputs, with PSI4_SYNC_ environment defaults.

    Attributes:
        project: Parser project to update after successful checks.
        source: Clean Git checkout matching the reference build.
        python: Reference Python launcher; preserve its symlink basename.
        binary: Psi4 job launcher for guarded integration cases.
        check: Keep the current project unchanged after verification.
        timeout: Maximum seconds allowed for each subprocess stage.
        offline: Require uv to use already cached locked dependencies.
    """

    model_config = SettingsConfigDict(env_prefix="PSI4_SYNC_", frozen=True)

    project: Path
    source: Path
    python: Path
    binary: Path
    check: bool = False
    timeout: float = Field(default=1800, gt=0, allow_inf_nan=False)
    offline: bool = False


def _capture(
    command: Sequence[str], cwd: Path, timeout: float, payload: str | None = None
) -> str:
    return subprocess.run(  # noqa: S603 - Explicit executable and argument vector.
        command,
        cwd=cwd,
        capture_output=True,
        input=payload,
        text=True,
        check=True,
        timeout=timeout,
        env=os.environ | {"GIT_OPTIONAL_LOCKS": "0"},
    ).stdout.strip()


def _verified_snapshot(settings: Settings, work: Path) -> Snapshot:
    revision = _capture(["git", "rev-parse", "HEAD"], settings.source, 30)
    dirty = _capture(
        ["git", "status", "--porcelain", "--untracked-files=no"], settings.source, 30
    )
    if dirty:
        raise ValueError("Reference source has tracked modifications")
    worker = Path(__file__).with_name("reference.py")
    snapshot = read_snapshot(
        _capture(
            [str(settings.python), str(worker)],
            work,
            settings.timeout,
            json.dumps("snapshot") + "\n",
        )
    )
    profile = snapshot["profile"]
    build_revision = re.search(
        r"\+([0-9a-f]{7,40})(?:$|\.)", profile["psi4.version_long"]
    )
    if (
        build_revision is None
        or not revision.startswith(build_revision.group(1))
        or profile["psi4.clean"] != "True"
    ):
        raise ValueError(
            "Reference build metadata does not match the clean source revision"
        )
    for name in PSI4_SOURCES:
        if content_hash(settings.source / name) != profile["bytes:" + name]:
            raise ValueError("Installed reader differs from source checkout: " + name)
    binary_version = _capture([str(settings.binary), "--version"], work, 30)
    if binary_version != profile["psi4.version"]:
        raise ValueError("Psi4 binary and reference Python report different versions")
    _verify_binary(settings, work, snapshot)
    profile["psi4.revision"] = revision
    # C++ readers have no Python AST; conservatively guard their complete contents.
    for name in (
        "psi4/src/psi4/libmints/molecule.cc",
        "psi4/src/psi4/libmints/coordentry.cc",
    ):
        profile["syntax:" + name] = content_hash(settings.source / name)
    return snapshot


def _verify_binary(settings: Settings, work: Path, snapshot: Snapshot) -> None:
    worker = Path(__file__).with_name("reference.py")
    output = work / "binary-snapshot.json"
    probe = work / "binary-probe.dat"
    probe.write_text(
        "import json, runpy\n"
        "from pathlib import Path\n"
        + "data = runpy.run_path("
        + repr(str(worker))
        + ')["snapshot"]()\n'
        + "Path("
        + repr(str(output))
        + ").write_text(json.dumps(data))\n"
    )
    _capture(
        [
            str(settings.binary),
            "-i",
            str(probe),
            "-o",
            str(work / "binary-probe.out"),
            "-s",
            str(work),
            "-n",
            "1",
        ],
        work,
        settings.timeout,
    )
    if read_snapshot(output.read_text()) != snapshot:
        raise ValueError(
            "Psi4 binary and reference Python expose different builds or readers"
        )


def _inputs(project: Path) -> dict[str, str]:
    paths = [project / name for name in _FILES]
    paths.extend(
        path
        for directory in _DIRECTORIES
        for path in (project / directory).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    if (project / _BASELINE).exists():
        paths.append(project / _BASELINE)
    return {str(path.relative_to(project)): content_hash(path) for path in paths}


def _stage(project: Path, candidate: Path) -> None:
    candidate.mkdir()
    for name in _DIRECTORIES:
        shutil.copytree(
            project / name,
            candidate / name,
            ignore=_ignore_cache,
        )
    for name in _FILES:
        shutil.copy2(project / name, candidate / name)


def _ignore_cache(directory: str, names: list[str]) -> set[str]:
    del directory
    return {name for name in names if name == "__pycache__"}


def _phase(
    name: str,
    command: Sequence[str],
    candidate: Path,
    work: Path,
    settings: Settings,
) -> None:
    sys.stderr.write("Psi4 synchronization: " + name + "\n")
    sys.stderr.flush()
    env = os.environ | {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PSI4_BINARY": str(settings.binary),
        "PSI4_PYTHON": str(settings.python),
    }
    with (work / (name + ".log")).open("w") as output:
        subprocess.run(  # noqa: S603 - Fixed verification tools and explicit arguments.
            command,
            cwd=candidate,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            check=True,
            timeout=settings.timeout,
        )


def _checks(candidate: Path, work: Path, settings: Settings) -> None:
    uv = shutil.which("uv")
    if uv is None:
        raise FileNotFoundError(
            "uv is required to install the candidate's locked environment"
        )
    install = [uv, "sync", "--locked", "--python", sys.executable]
    if settings.offline:
        install.append("--offline")
    _phase("environment", install, candidate, work, settings)
    python = str(candidate / ".venv/bin/python")
    _phase(
        "regenerate",
        [str(candidate / ".venv/bin/psi4-regenerate")],
        candidate,
        work,
        settings,
    )
    for name, arguments in (
        ("lint", ["ruff", "check", "--no-cache", "src", "tests"]),
        (
            "format",
            ["ruff", "format", "--check", "--no-cache", "src", "tests"],
        ),
        ("types", ["mypy", "--cache-dir=/dev/null"]),
        (
            "tests",
            [
                "pytest",
                "-p",
                "no:cacheprovider",
                "--basetemp=" + str(work / "pytest"),
                "-q",
            ],
        ),
        (
            "differential",
            [
                "psi4_parser.maintenance.audit",
                "--source",
                str(settings.source),
                "--reference-python",
                str(settings.python),
                "--report",
                str(work / "differential.json"),
            ],
        ),
    ):
        _phase(name, [python, "-m", *arguments], candidate, work, settings)


def _replace(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        name = Path(temporary.name)
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
        name.chmod(path.stat().st_mode & 0o777 if path.exists() else 0o644)
    try:
        name.replace(path)
    finally:
        name.unlink(missing_ok=True)


def promote(project: Path, updates: dict[Path, bytes]) -> None:
    """Replace verified artifacts and roll back if any replacement fails.

    Args:
        project: Destination working tree.
        updates: Relative artifact paths and their verified bytes, manifest last.

    Failed writes propagate after the original artifacts have been restored.
    """
    previous = {
        path: (project / path).read_bytes() if (project / path).exists() else None
        for path in updates
    }
    try:
        for path, content in updates.items():
            _replace(project / path, content)
    except BaseException:
        for path, original_content in previous.items():
            if original_content is None:
                (project / path).unlink(missing_ok=True)
            else:
                _replace(project / path, original_content)
        raise


def _artifacts(candidate: Path) -> dict[Path, bytes]:
    paths = [_GRAMMAR]
    paths.extend(
        path.relative_to(candidate)
        for path in sorted((candidate / "src/psi4_parser/_generated").iterdir())
        if path.suffix in {".py", ".interp", ".tokens"}
    )
    paths.append(_BASELINE)
    return {path: (candidate / path).read_bytes() for path in paths}


def _patch(project: Path, updates: dict[Path, bytes]) -> str:
    chunks: list[str] = []
    for path, content in updates.items():
        original = project / path
        before = original.read_text() if original.exists() else ""
        chunks.extend(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                content.decode().splitlines(keepends=True),
                fromfile="a/" + str(path) if original.exists() else "/dev/null",
                tofile="b/" + str(path),
            )
        )
    return "".join(chunks)


@contextlib.contextmanager
def _locked(project: Path) -> Iterator[None]:
    cache = project / ".cache"
    cache.mkdir(exist_ok=True)
    with (cache / "psi4-sync.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def synchronize(settings: Settings) -> Path:
    """Verify a candidate and publish a JSON report, preserving failures for diagnosis.

    Args:
        settings: Explicit project and matching reference paths.

    Returns:
        Successful report path. Failed runs raise after writing their report.

    Preflight, verification and promotion failures propagate to the caller.
    """
    with _locked(settings.project):
        return _synchronize(settings)


def _synchronize(settings: Settings) -> Path:
    work = Path(tempfile.mkdtemp(prefix="psi4-sync-", dir=settings.project / ".cache"))
    report_path = work / "report.json"
    report: dict[str, object] = {"status": "failed", "work": str(work)}
    try:
        original = _inputs(settings.project)
        snapshot = _verified_snapshot(settings, work)
        baseline = read_baseline(settings.project / _BASELINE)
        report["profile"] = snapshot["profile"]
        changes = guarded_changes(baseline["profile"], snapshot["profile"])
        report["source_changes"] = changes
        if changes:
            raise ValueError(
                "Reader/language changes require a grammar assessment: "
                + ", ".join(changes)
            )
        candidate = work / "candidate"
        _stage(settings.project, candidate)
        grammar, inventories = refresh_inventories(
            (candidate / _GRAMMAR).read_text(), snapshot
        )
        (candidate / _GRAMMAR).write_text(grammar)
        inventory_report: dict[str, dict[str, list[str]]] = {
            name: {"added": list(value.added), "removed": list(value.removed)}
            for name, value in inventories.items()
        }
        report["inventories"] = inventory_report
        updated = Baseline(schema=1, profile=snapshot["profile"])
        (candidate / _BASELINE).parent.mkdir(exist_ok=True)
        (candidate / _BASELINE).write_text(
            json.dumps(updated, indent=2, sort_keys=True) + "\n"
        )
        _checks(candidate, work, settings)
        if original != _inputs(settings.project):
            raise ValueError(
                "Parser working tree changed during verification; no upgrade applied"
            )
        updates = _artifacts(candidate)
        (work / "update.patch").write_text(_patch(settings.project, updates))
        if not settings.check:
            promote(settings.project, updates)
        report["status"] = "verified" if settings.check else "applied"
        # Cleanup is optional once verified artifacts have been promoted.
        with contextlib.suppress(OSError):
            shutil.rmtree(candidate)
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
        if isinstance(error, subprocess.CalledProcessError):
            detail: str | bytes | None = error.stderr
            if detail:
                report["stderr"] = (
                    detail.decode(errors="replace")
                    if isinstance(detail, bytes)
                    else detail
                )
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        sys.stderr.write("Psi4 synchronization report: " + str(report_path) + "\n")
    return report_path


@click.command()
@click.option(
    "--project",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path(__file__).resolve().parents[3],
    show_default=True,
    help="Parser checkout to update.",
)
@click.option(
    "--source",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Clean Psi4 source checkout matching the supplied build.",
)
@click.option(
    "--reference-python",
    type=click.Path(exists=True, dir_okay=False, executable=True, path_type=Path),
    required=True,
    help="Psi4 Python launcher; preserve its symlink basename.",
)
@click.option(
    "--binary",
    type=click.Path(exists=True, dir_okay=False, executable=True, path_type=Path),
    required=True,
    help="Matching Psi4 job launcher.",
)
@click.option("--check", is_flag=True, help="Verify without promotion.")
@click.option("--offline", is_flag=True, help="Use uv's local cache only.")
@click.option(
    "--timeout",
    type=click.FloatRange(min=0, min_open=True),
    default=1800.0,
    show_default=True,
    help="Maximum seconds for each subprocess stage.",
)
def main(  # noqa: PLR0913 - Click passes the seven named CLI options.
    *,
    project: Path,
    source: Path,
    reference_python: Path,
    binary: Path,
    check: bool,
    offline: bool,
    timeout: float,
) -> None:
    """Verify and apply compatible upgrades from supplied Psi4 paths.

    \f

    Args:
        project: Destination parser checkout.
        source: Matching clean Psi4 source checkout.
        reference_python: Python launcher in the reference build.
        binary: Job launcher in the same build.
        check: Verify and write a patch without promotion.
        offline: Install candidate dependencies from uv's local cache.
        timeout: Maximum seconds for each subprocess stage.

    Raises:
        click.ClickException: Reference verification or candidate checks failed.
    """  # noqa: D301 - Click uses a form feed to end CLI help.
    try:
        settings = Settings(
            project=project.resolve(),
            source=source.resolve(),
            python=reference_python.absolute(),
            binary=binary.absolute(),
            check=check,
            timeout=timeout,
            offline=offline,
        )
        report = synchronize(settings)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)) from error
    click.echo(report.read_text().rstrip())


if __name__ == "__main__":
    main()
