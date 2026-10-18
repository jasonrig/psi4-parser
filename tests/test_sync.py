"""Exercise synchronization boundaries without replacing the language tests."""

import ast
import fcntl
import hashlib
import json
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from psi4_parser.maintenance import sync
from psi4_parser.maintenance.audit import compare_cases
from psi4_parser.maintenance.reference import (
    PSI4_SOURCES,
    digest_python,
    source_fingerprints,
)
from psi4_parser.maintenance.state import (
    Snapshot,
    guarded_changes,
    read_snapshot,
    refresh_inventories,
)

_GRAMMAR = (
    '_PSITHON_CORE_NAMES = (\n    "A",\n)\n'
    '_PSITHON_CONSTANT_NAMES = (\n    "x",\n)\nrule: NAME;\n'
)


def _snapshot() -> Snapshot:
    return Snapshot(
        profile={
            "psi4.version_long": "1.0+abcdef0",
            "psi4.revision": "abcdef0",
            "syntax:reader": "unchanged",
            "python.language": "3.15",
            "python.unicode": "17.0.0",
        },
        core_names=["A", "B"],
        constant_names=["y"],
    )


def _project(tmp_path: Path) -> Path:
    """Create a small working tree for transaction tests.

    Args:
        tmp_path: Isolated test directory.

    Returns:
        Minimal parser project with an accepted compatibility baseline.
    """
    for directory in ("src", "grammar", "tests", "test", "compatibility", "typings"):
        (tmp_path / directory).mkdir()
    (tmp_path / "grammar/PsithonParser.g4").write_text(_GRAMMAR)
    generated = tmp_path / "src/psi4_parser/_generated"
    generated.mkdir(parents=True)
    (generated / "PsithonLexer.py").write_text("original generated lexer\n")
    (tmp_path / "pyproject.toml").write_text("")
    (tmp_path / "uv.lock").write_text("")
    baseline: dict[str, object] = {"schema": 1, "profile": _snapshot()["profile"]}
    (tmp_path / "compatibility/psi4.json").write_text(json.dumps(baseline))
    return tmp_path


def _settings(project: Path, *, check: bool = False) -> sync.Settings:
    return sync.Settings(
        project=project,
        source=project,
        python=Path(sys.executable),
        binary=Path("/bin/false"),
        check=check,
    )


def _probe(settings: sync.Settings, work: Path) -> Snapshot:
    del settings, work
    return _snapshot()


def _verified_candidate(candidate: Path, work: Path, settings: sync.Settings) -> None:
    del work, settings
    (candidate / "src/psi4_parser/_generated/PsithonLexer.py").write_text(
        "verified lexer\n"
    )


def test_inventory_refresh_preserves_rules() -> None:
    """Refresh namespace data while retaining unrelated grammar productions."""
    grammar, changes = refresh_inventories(_GRAMMAR, _snapshot())

    assert grammar.endswith("rule: NAME;\n")
    assert changes["CORE"].added == ("B",)
    assert changes["CONSTANT"].removed == ("x",)
    assert changes["CONSTANT"].added == ("y",)
    assert refresh_inventories(grammar, _snapshot())[0] == grammar


def test_malformed_inventory_is_rejected() -> None:
    """Refuse ambiguous source edits rather than replacing multiple tables."""
    with pytest.raises(ValueError, match="exactly one"):
        refresh_inventories(_GRAMMAR + _GRAMMAR, _snapshot())


def test_snapshot_requires_ordered_names() -> None:
    """Reject an unordered inventory from a broken reference probe."""
    snapshot = _snapshot()
    snapshot["core_names"] = ["B", "A"]

    with pytest.raises(ValueError, match="ordered"):
        read_snapshot(json.dumps(snapshot))


def test_guard_ignores_comments_but_detects_behavior(tmp_path: Path) -> None:
    """Detect upstream code changes without blocking on Python comments.

    Args:
        tmp_path: Directory for the reader source.
    """
    path = tmp_path / "reader.py"
    path.write_text("value = 1\n")
    raw, semantic = source_fingerprints(path)
    path.write_text("# New explanation\nvalue = 1\n")
    new_raw, new_semantic = source_fingerprints(path)
    assert raw != new_raw
    assert semantic == new_semantic
    assert (
        guarded_changes({"syntax:reader": semantic}, {"syntax:reader": new_semantic})
        == []
    )

    path.write_text("value = 2\n")
    assert guarded_changes(
        {"syntax:reader": semantic}, {"syntax:reader": source_fingerprints(path)[1]}
    ) == ["syntax:reader"]


@pytest.mark.parametrize("check", [False, True])
def test_successful_upgrade_or_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, check: bool
) -> None:
    """Publish only verified artifacts, or leave the tree intact in check mode.

    Args:
        tmp_path: Minimal destination tree.
        monkeypatch: Controls the external reference and verification boundaries.
        check: Whether this run must preserve the destination bytes.
    """
    project = _project(tmp_path)
    monkeypatch.setattr(sync, "_verified_snapshot", _probe)
    monkeypatch.setattr(sync, "_checks", _verified_candidate)

    report = sync.synchronize(_settings(project, check=check))

    data: dict[str, object] = json.loads(report.read_text())
    assert data["status"] == ("verified" if check else "applied")
    assert (project / "grammar/PsithonParser.g4").read_text() == (
        _GRAMMAR if check else refresh_inventories(_GRAMMAR, _snapshot())[0]
    )
    assert (project / "src/psi4_parser/_generated/PsithonLexer.py").read_text() == (
        "original generated lexer\n" if check else "verified lexer\n"
    )
    assert (report.parent / "update.patch").read_text()


@pytest.mark.parametrize("failure", ["checks", "concurrent-edit", "reader-change"])
def test_failed_upgrade_preserves_baseline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    """Keep the accepted artifacts when verification or source guards fail.

    Args:
        tmp_path: Minimal destination tree.
        monkeypatch: Controls external tools to provoke observable failures.
        failure: The failure boundary exercised by this case.
    """
    project = _project(tmp_path)
    original = (project / "compatibility/psi4.json").read_bytes()

    def probe(settings: sync.Settings, work: Path) -> Snapshot:
        result = _probe(settings, work)
        if failure == "reader-change":
            result["profile"]["syntax:reader"] = "changed"
        return result

    def checks(candidate: Path, work: Path, settings: sync.Settings) -> None:
        _verified_candidate(candidate, work, settings)
        if failure == "concurrent-edit":
            (project / "src/user.py").write_text("user change\n")
        else:
            raise subprocess.CalledProcessError(
                1, ["verification"], stderr="reference failure details"
            )

    monkeypatch.setattr(sync, "_verified_snapshot", probe)
    monkeypatch.setattr(sync, "_checks", checks)

    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        sync.synchronize(_settings(project))

    assert (project / "compatibility/psi4.json").read_bytes() == original
    assert (project / "grammar/PsithonParser.g4").read_text() == _GRAMMAR
    assert (
        project / "src/psi4_parser/_generated/PsithonLexer.py"
    ).read_text() == "original generated lexer\n"
    reports = list((project / ".cache").glob("psi4-sync-*/report.json"))
    data: dict[str, object] = json.loads(reports[0].read_text())
    assert data["status"] == "failed"
    assert data["error"]
    if failure == "checks":
        assert data["stderr"] == "reference failure details"
    if failure == "concurrent-edit":
        assert (project / "src/user.py").read_text() == "user change\n"


def test_partial_promotion_is_rolled_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Restore changed files and remove new files after a failed replacement.

    Args:
        tmp_path: Destination for three artifacts.
        monkeypatch: Injects one filesystem failure during promotion.
    """
    (tmp_path / "original").write_bytes(b"before")
    replace = Path.replace
    failed = False

    def fail_once(path: Path, target: Path) -> Path:
        nonlocal failed
        if target.name == "manifest" and not failed:
            failed = True
            raise OSError("disk full")
        # PyCharm applies Path.replace's Self return to this plain function.
        # noinspection PyTypeChecker
        return replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_once)
    with pytest.raises(OSError, match="disk full"):
        sync.promote(
            tmp_path,
            {
                Path("new"): b"new",
                Path("original"): b"after",
                Path("manifest"): b"accepted",
            },
        )

    assert (tmp_path / "original").read_bytes() == b"before"
    assert not (tmp_path / "new").exists()
    assert not (tmp_path / "manifest").exists()


@pytest.mark.parametrize("error", ["newly accepted", "ModuleNotFoundError: dependency"])
def test_reference_changes_cannot_pass_as_negative_cases(error: str) -> None:
    """Report broadened syntax and infrastructure failures independently.

    Args:
        error: A changed reference outcome or missing dependency.
    """
    failures = compare_cases(
        [
            {
                "name": "negative",
                "source": "return 1\n",
                "expected": False,
                "upstream": False,
            }
        ],
        {
            "negative": {
                "name": "negative",
                "digest": "accepted" if error == "newly accepted" else "",
                "error": "" if error == "newly accepted" else error,
            }
        },
    )
    assert failures
    assert error in failures[0]["error"]


def test_generated_identifier_normalization() -> None:
    """Normalize generated basis IDs while retaining actual Python structure."""
    assert digest_python("anonymousa1b2c3d4 = 1\n") == digest_python(
        "anonymous87654321 = 1\n"
    )
    assert digest_python("value = 1\n") != digest_python("value = 2\n")


@pytest.mark.parametrize("source", [None, "answer =\n", "answer = 1\n"])
def test_corpus_cli_failure_status(tmp_path: Path, source: str | None) -> None:
    """Make empty and rejected corpora fail unattended CI checks.

    Args:
        tmp_path: Fake upstream checkout.
        source: An absent corpus, invalid input or accepted input.
    """
    if source is not None:
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests/input.dat").write_text(source)
    script = Path(sys.executable).with_name("psi4-check-corpus")

    result = subprocess.run(  # noqa: S603 - Fixed CLI and isolated test input.
        [str(script), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert (result.returncode == 0) == (source == "answer = 1\n")


@pytest.mark.parametrize("mismatch", ["revision", "dirty", "binary"])
def test_preflight_rejects_mismatched_references(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mismatch: str
) -> None:
    """Reject build identity failures before any candidate is created.

    Args:
        tmp_path: Fake reference checkout and probe output directory.
        monkeypatch: Replaces the external Git and reference launchers.
        mismatch: The build identity discrepancy to report.
    """
    snapshot = _snapshot()
    snapshot["profile"].update({"psi4.version": "1.0", "psi4.clean": "True"})
    for name in PSI4_SOURCES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"pass\n")
        snapshot["profile"]["bytes:" + name] = hashlib.sha256(b"pass\n").hexdigest()

    def capture(
        command: Sequence[str], cwd: Path, timeout: float, payload: str | None = None
    ) -> str:
        del cwd, timeout
        if command[0] == "git":
            if command[1] == "rev-parse":
                return "1234567" if mismatch == "revision" else "abcdef0"
            return " M reader.py" if mismatch == "dirty" else ""
        if payload == json.dumps("snapshot") + "\n":
            return json.dumps(snapshot)
        return "different version"

    monkeypatch.setattr(sync, "_capture", capture)
    with pytest.raises(ValueError, match=r"modifications|metadata|different versions"):
        sync._verified_snapshot(_settings(tmp_path), tmp_path)


def test_concurrent_sync_is_rejected(tmp_path: Path) -> None:
    """Reject a second writer while another synchronization holds the lock.

    Args:
        tmp_path: Destination project with an existing held lock.
    """
    project = _project(tmp_path)
    (project / ".cache").mkdir()
    with (project / ".cache/psi4-sync.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            sync.synchronize(_settings(project))


@pytest.mark.parametrize(
    "command", ["psi4-sync", "psi4-check-corpus", "psi4-regenerate"]
)
def test_installed_console_commands(command: str) -> None:
    """Expose every public maintenance command through the installed project.

    Args:
        command: Console script registered in pyproject.toml.
    """
    result = subprocess.run(  # noqa: S603 - Fixed installed console scripts.
        [str(Path(sys.executable).with_name(command)), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Usage:" in result.stdout
    assert "--help" in result.stdout


def test_inventory_refresh_preserves_unicode_names() -> None:
    """Keep Unicode exports intact through repeated grammar rendering."""
    snapshot = _snapshot()
    snapshot["constant_names"] = ["\N{GREEK SMALL LETTER ALPHA}", "ℏ"]

    grammar, changes = refresh_inventories(_GRAMMAR, snapshot)
    constants = grammar.split("_PSITHON_CONSTANT_NAMES = ", 1)[1].split("rule:", 1)[0]
    names: tuple[str, ...] = ast.literal_eval(constants.strip())

    assert names == ("\N{GREEK SMALL LETTER ALPHA}", "ℏ")
    assert changes["CONSTANT"].added == ("\N{GREEK SMALL LETTER ALPHA}", "ℏ")
    assert refresh_inventories(grammar, snapshot)[0] == grammar


def test_click_sync_preserves_launcher_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep symlink-dependent launcher modes when parsing unattended options.

    Args:
        tmp_path: Directory for launcher links and a successful report.
        monkeypatch: Captures settings instead of starting a synchronization.
    """
    python = tmp_path / "psi4-python"
    binary = tmp_path / "psi4"
    python.symlink_to(sys.executable)
    binary.symlink_to(sys.executable)
    report = tmp_path / "report.json"
    report.write_text('{"status": "verified"}\n')
    captured: list[sync.Settings] = []

    def synchronize(settings: sync.Settings) -> Path:
        captured.append(settings)
        return report

    monkeypatch.setattr(sync, "synchronize", synchronize)
    # PyCharm treats Click-decorated commands as plain callback functions.
    # noinspection PyTypeChecker
    result = CliRunner().invoke(
        sync.main,
        [
            "--project",
            str(tmp_path),
            "--source",
            str(tmp_path),
            "--reference-python",
            str(python),
            "--binary",
            str(binary),
            "--check",
            "--offline",
            "--timeout",
            "12.5",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured == [
        sync.Settings(
            project=tmp_path.resolve(),
            source=tmp_path.resolve(),
            python=python,
            binary=binary,
            check=True,
            timeout=12.5,
            offline=True,
        )
    ]
    output: dict[str, str] = json.loads(result.output)
    assert output == {"status": "verified"}


@pytest.mark.parametrize("timeout", ["0", "-1"])
def test_click_rejects_nonpositive_timeout(timeout: str) -> None:
    """Reject invalid time limits before starting any subprocesses.

    Args:
        timeout: A nonpositive stage limit supplied on the command line.
    """
    # noinspection PyTypeChecker
    result = CliRunner().invoke(sync.main, ["--timeout", timeout])

    assert result.exit_code == 2
    assert "Invalid value for '--timeout'" in result.output


def test_settings_load_prefixed_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Load and validate unattended configuration without unrelated environment names.

    Args:
        tmp_path: Reference paths supplied by the environment.
        monkeypatch: Restores environment changes after the test.
    """
    for name in ("PROJECT", "SOURCE", "PYTHON", "BINARY"):
        monkeypatch.setenv("PSI4_SYNC_" + name, str(tmp_path / name.lower()))
    monkeypatch.setenv("PSI4_SYNC_TIMEOUT", "45.5")
    monkeypatch.setenv("PSI4_SYNC_CHECK", "true")
    monkeypatch.setenv("TIMEOUT", "invalid unrelated value")

    # Required paths come from the environment through pydantic-settings.
    # noinspection PyArgumentList
    settings = sync.Settings()
    # noinspection PyArgumentList
    overridden = sync.Settings(timeout=90)

    assert settings.project == tmp_path / "project"
    assert settings.source == tmp_path / "source"
    assert settings.python == tmp_path / "python"
    assert settings.binary == tmp_path / "binary"
    assert settings.timeout == 45.5
    assert settings.check is True
    assert overridden.timeout == 90


@pytest.mark.parametrize("timeout", [0.0, -1.0, float("nan"), float("inf")])
def test_settings_reject_invalid_timeout(tmp_path: Path, timeout: float) -> None:
    """Require finite positive stage limits for direct API callers.

    Args:
        tmp_path: Explicit paths for the test settings.
        timeout: Invalid timeout value that must fail before synchronization.
    """
    with pytest.raises(ValidationError, match="timeout"):
        sync.Settings(
            project=tmp_path,
            source=tmp_path,
            python=tmp_path,
            binary=tmp_path,
            timeout=timeout,
        )


def test_click_reports_model_validation_error(tmp_path: Path) -> None:
    """Report non-finite timeouts as CLI errors without starting the pipeline.

    Args:
        tmp_path: Existing directory satisfying the CLI's path checks.
    """
    # noinspection PyTypeChecker
    result = CliRunner().invoke(
        sync.main,
        [
            "--project",
            str(tmp_path),
            "--source",
            str(tmp_path),
            "--reference-python",
            sys.executable,
            "--binary",
            sys.executable,
            "--timeout",
            "nan",
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "finite number" in result.output
    assert not (tmp_path / ".cache").exists()


def test_promotion_preserves_modes_and_creates_missing_parent_directories(
    tmp_path: Path,
) -> None:
    """Keep binary bytes and existing permissions while creating new artifacts.

    Args:
        tmp_path: Isolated destination for the promotion transaction.
    """
    existing = tmp_path / "existing.dat"
    existing.write_bytes(b"original")
    existing.chmod(0o600)
    sync.promote(
        tmp_path, {Path("existing.dat"): b"\x00\xff", Path("nested/new.dat"): b"new"}
    )
    assert existing.read_bytes() == b"\x00\xff"
    assert existing.stat().st_mode & 0o777 == 0o600
    created = tmp_path / "nested/new.dat"
    assert created.read_bytes() == b"new"
    assert created.stat().st_mode & 0o777 == 0o644
    assert set(created.parent.iterdir()) == {created}
