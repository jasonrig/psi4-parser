"""Probe Psi4 in its interpreter; never execute the Python contained in a job.

This file also runs as a standalone script in the reference environment. Its
structural protocols describe the small Psi4 interface used at that boundary.
"""

import ast
import contextlib
import hashlib
import importlib
import json
import re
import sys
import types
import unicodedata
from pathlib import Path
from typing import Protocol, runtime_checkable

# Source fingerprint label paired with its local path.
type NamedSource = tuple[str, Path]

PSI4_SOURCES = (
    "psi4/driver/inputparser.py",
    "psi4/driver/molutil.py",
    "psi4/driver/p4util/util.py",
    "psi4/driver/qcdb/libmintsmolecule.py",
)
"""Python readers whose installed bytes must match the source checkout."""


@runtime_checkable
class _Core(Protocol):
    def set_output_file(self, filename: str, append: bool) -> None: ...


@runtime_checkable
class _Psi4(Protocol):
    __file__: str
    __version__: str
    core: _Core
    metadata: types.ModuleType

    def process_input(self, raw_input: str, print_level: int = 1) -> str: ...


@runtime_checkable
class _Driver(Protocol):
    # Only attribute names are inspected; constant values can have many types.
    constants: object


@runtime_checkable
class _Qcelemental(Protocol):
    __file__: str
    __version__: str


class _PcmBoundary(types.ModuleType):
    @staticmethod
    def parse_pcm_input(_path: str) -> str:
        return ""


def digest_python(source: str) -> str:
    """Hash a projected Python AST, normalizing known generated identifiers.

    Args:
        source: Python emitted by either implementation of the preprocessor.

    Returns:
        SHA-256 of the normalized syntax tree.
    """
    normalized = re.sub(
        r"anonymous[0-9a-f]{8}", "anonymous00000000", source, flags=re.IGNORECASE
    )
    normalized = re.sub(
        r"@pcmsolver\.\d+\.[0-9a-f]{8}", "@pcmsolver.syntax", normalized
    )
    tree = ast.dump(ast.parse(normalized), include_attributes=False)
    return hashlib.sha256(tree.encode()).hexdigest()


def source_fingerprints(path: Path) -> tuple[str, str]:
    """Return byte and Python-AST hashes for an upstream source file.

    Args:
        path: UTF-8 Python source file.

    Returns:
        Raw SHA-256 and semantic SHA-256, excluding source positions.
    """
    content = path.read_bytes()
    semantic = ast.dump(ast.parse(content), include_attributes=False)
    return hashlib.sha256(content).hexdigest(), hashlib.sha256(
        semantic.encode()
    ).hexdigest()


def _reference() -> _Psi4:
    module: object = importlib.import_module("psi4")
    if not isinstance(module, _Psi4):
        raise TypeError("Reference interpreter does not expose the Psi4 interface")
    if (Path.home() / ".psi4rc").exists():
        raise ValueError(
            "Remove ~/.psi4rc from the reference account for reproducibility"
        )
    module.core.set_output_file("/dev/null", False)
    return module


def _metadata_field(metadata: types.ModuleType, name: str) -> str:
    value: object = getattr(metadata, name)
    if not isinstance(value, str):
        raise TypeError("Psi4 metadata field must be a string: " + name)
    return value


def _profile(reference: _Psi4) -> dict[str, str]:
    qcel: object = importlib.import_module("qcelemental")
    if not isinstance(qcel, _Qcelemental):
        raise TypeError("Reference interpreter does not expose QCEElemental metadata")
    profile = {
        "psi4.version": reference.__version__,
        "psi4.version_long": _metadata_field(reference.metadata, "__version_long"),
        "psi4.clean": _metadata_field(reference.metadata, "__version_is_clean"),
        "python.version": sys.version.split()[0],
        "python.language": f"{sys.version_info.major}.{sys.version_info.minor}",
        "python.unicode": unicodedata.unidata_version,
        "qcelemental.version": qcel.__version__,
        "pcm.validation": "preprocessor boundary with controlled empty solver output",
    }
    root = Path(reference.__file__).parent.parent
    paths: list[NamedSource] = [(name, root / name) for name in PSI4_SOURCES]
    qcel_root = Path(qcel.__file__).parent
    qcel_paths: list[NamedSource] = [
        ("qcelemental/" + str(path.relative_to(qcel_root)), path)
        for path in sorted((qcel_root / "molparse").rglob("*.py"))
    ]
    paths.extend(qcel_paths)
    for name, path in paths:
        raw, semantic = source_fingerprints(path)
        profile["bytes:" + name] = raw
        profile["syntax:" + name] = semantic
    return profile


def _install_pcm_boundary_probe() -> None:
    # This tests Psi4's wrapper and brace boundaries, not PCMSolver's schema.
    sys.modules["pcmsolver"] = _PcmBoundary("pcmsolver")


def _compile_cases(reference: _Psi4) -> None:
    _install_pcm_boundary_probe()
    text: str = sys.stdin.read()
    for line in text.splitlines():
        request: dict[str, str] = json.loads(line)
        result = {"name": request["name"], "digest": "", "error": ""}
        try:
            with contextlib.redirect_stdout(sys.stderr):
                source = request["source"].replace("\r\n", "\n").replace("\r", "\n")
                translated = reference.process_input(source, print_level=0)
            compile(translated, "<reference>", "exec")
            result["digest"] = digest_python(translated)
        except Exception as error:  # A reference error is data in this worker protocol.
            result["error"] = type(error).__name__ + ": " + str(error)
        print(json.dumps(result), flush=True)  # noqa: T201 - JSON-line worker protocol.


def snapshot() -> dict[str, object]:
    """Extract metadata, reader hashes and namespace inventories from Psi4.

    Returns:
        JSON-compatible description of the running reference environment.

    Raises:
        TypeError: The reference driver has an incompatible interface.
    """
    with contextlib.redirect_stdout(sys.stderr):
        reference = _reference()
    driver: object = importlib.import_module("psi4.driver")
    if not isinstance(driver, _Driver):
        raise TypeError("Reference driver does not expose constants")
    core_names: list[str] = dir(reference.core)
    constant_names: list[str] = dir(driver.constants)
    return {
        "profile": _profile(reference),
        "core_names": core_names,
        "constant_names": [
            name for name in constant_names if not name.startswith("__")
        ],
    }


def main() -> None:
    """Serve a snapshot or compile request from the private JSON-lines protocol.

    The first line is the request kind, followed by job records for compilation.
    No CLI dependencies are imported into the supplied reference environment.

    Raises:
        ValueError: The requested operation is unknown.
    """
    # A JSON value is unknown until validated at this process boundary.
    request: str = sys.stdin.readline()
    mode: object = json.loads(request)
    if not isinstance(mode, str):
        raise ValueError("Reference operation must be a string")
    if mode not in {"snapshot", "compile"}:
        raise ValueError("Unknown reference operation: " + repr(mode))
    if mode == "compile":
        with contextlib.redirect_stdout(sys.stderr):
            reference = _reference()
        _compile_cases(reference)
        return
    print(json.dumps(snapshot(), indent=2))  # noqa: T201 - JSON snapshot protocol.


if __name__ == "__main__":
    main()
