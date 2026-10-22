"""Inspect a reviewed Psi4 build's metadata without running chemistry drivers.

Run this standalone file in the engine's interpreter. Structural protocols keep
the small metadata boundary typed without importing Psi4 into the parser runtime.
Source hashes pin every selector used in probe mode before it can be called.
"""

import hashlib
import importlib
import importlib.metadata
import json
import platform
import sys
import types
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None

AUDITED_COMMIT = "60c9b2a773c05abc26991c5ed48cf9862cdb4978"
"""Reviewed source revision; other revisions require a new source audit."""

PYTHON_SOURCES = {
    "driver/procrouting/solvent/ddx.py": (
        "d436f2365a9131b524e6f438fd816b934534b8aa362d4a54a61d8de822d652f6"
    ),
    "driver/procrouting/solvent/__init__.py": (
        "8951b2cbfd89e762a44ea9ad61b324fe4fef3d383e04d89cee9da14c73eea36d"
    ),
    "driver/procrouting/scf_proc/scf_iterator.py": (
        "4de3bf96fb09d46d2ad7cace03dbad667068e00526edf4adf4ea00df60d7aa8a"
    ),
    "driver/procrouting/proc_util.py": (
        "84d87df1244a0c06beaa9c626d108d3ed3ac80db586e81b5e2db5b589d73c12f"
    ),
    "driver/qcdb/psivardefs.py": (
        "d560503e47c53f7c3b63d88a8ff5a21fd218054ce910e1eb26a04c8e61297c16"
    ),
    "driver/driver_cbs.py": (
        "f956c0831c4023dc95b96bcbdcbab798fe58870eab4c7dfffb7f4b3319d5d869"
    ),
    "driver/driver_cbs_helper.py": (
        "1d26785aa87334267de8b1964725c21c5b659d0557406c758416396d9ee83dbc"
    ),
    "driver/qcdb/vib.py": (
        "154d637bce0be27d472c915d838e7e04cbed33b4253178267b107c20745a3b7d"
    ),
    "driver/inputparser.py": (
        "80f0ba7969b71a29ea567743eb24911550b9557f1f4883e569ca43d5a417da5a"
    ),
    "driver/driver.py": (
        "7d2485decb726bf62f18ca5f6c624b6dbc36d540dc9fbe2187a232189be13db6"
    ),
    "driver/driver_util.py": (
        "f7e8118f835d5c669526089abf03321ca33b9e0b220f0d24ed9360e0cdb6219c"
    ),
    "driver/procrouting/proc.py": (
        "98ac648d84cc4587ec034b9207d3c6fbc3cd74df4c0409a85478e5467c0dd408"
    ),
    "driver/procrouting/proc_table.py": (
        "995fb0b19407cbc17d29f3c10052f5fe2beeef331eb097250c34ddedcb9cbe73"
    ),
    "driver/p4util/python_helpers.py": (
        "0c39ba0ef11a32fb1a4e921dae64213e5af38ab69d9007170ace44113c49574f"
    ),
    "driver/p4util/exceptions.py": (
        "886800298ca7f6501b40e2826485029a9d163fcb75b9a14cc1c13463c00b56e1"
    ),
}
"""Installed Python files whose bytes must match the reviewed revision."""

BASIS_SOURCES = {
    "cc-pvdz-ri": "a121fe1f16e2fca6dced2fe6e9845d723c0220f671fb10e2bc0ac2154aef0522",
    "cc-pvtz-ri": "886b7baf1a6e96c3f2fa1439d75dc991003d6c69e91c3769b2d9c8e018d8cb73",
    "cc-pvqz-ri": "b8c2c6112b646a7ad6774e70535a78a1b05ec727b28d7bb8491f67781711be87",
    "cc-pvdz-jkfit": "0ce02adc7d0c5c517e3128131a2fe147c587b5241311f178adc21c6987b67ebf",
    "cc-pvtz-jkfit": "a7f961866b44a2112f545e919d39b5c3d5a00287b06eeea5f6405fbad980468a",
    "cc-pvqz-jkfit": "7b68da07767e81c6a3656111d77399463f37f89a40232dac1128a3c53edfeada",
    "sto-3g": ("b472adfbcd0d87e1fd054963b8073a95b5ec265e8b0fd46951a56005f0f227d7"),
    "cc-pvdz": ("9fe1562f050bc7290c98e765a4bf86dcbc1dbe6380a75d49cc835b89fd34a0e8"),
    "cc-pvtz": ("41e6452a999090bf6991b8b1f37198dfd8269f645fa1d0296609acafe83aaa99"),
    "cc-pvqz": ("45774bc7d8ab5289de40ce890430ea1d9e6736303b0e8e37bf9125d96031e4a8"),
    "def2-svp": ("6a88947cc200fd3cf8d5536f5a4a2815cc6e7e83ee7938ad0184af80ae4a2fdf"),
}
"""Orbital basis files whose definitions and dimensions are inspected."""

_ELEMENTS = (
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
)

BASIS_ROLES: dict[str, tuple[str, ...]] = {
    name: ("df_basis_sapt",)
    if name.endswith("-ri")
    else ("df_basis_scf", "df_basis_elst")
    if name.endswith("-jkfit")
    else ("basis",)
    for name in BASIS_SOURCES
}
"""Reviewed native roles; fitting sets are not advertised as orbital bases."""

BASIS_ELEMENTS: dict[str, tuple[str, ...]] = {
    name: tuple(
        element
        for element in _ELEMENTS
        if element not in {"He", "Li", "Be", "Na", "Mg"}
    )
    if name.endswith("-jkfit")
    else _ELEMENTS
    for name in BASIS_SOURCES
}
"""Reviewed H-Ar scope, including elements absent from these JKFIT definitions."""


class _Molecule(Protocol):
    def update_geometry(self) -> None: ...


class _MoleculeFactory(Protocol):
    def from_string(self, molstr: str, *, verbose: int = 0) -> _Molecule: ...


class _Basis(Protocol):
    def nbf(self) -> int: ...
    def max_am(self) -> int: ...
    def n_ecp_core(self) -> int: ...


class _BasisFactory(Protocol):
    def build(
        self, mol: _Molecule, key: str, target: str, *, puream: int, quiet: bool
    ) -> _Basis: ...


class _OEProp(Protocol):
    valid_methods: Sequence[str]


class _Core(Protocol):
    __file__: str
    Molecule: _MoleculeFactory
    BasisSet: _BasisFactory
    OEProp: _OEProp

    def clean_options(self) -> None: ...
    def set_output_file(self, path: str, append: bool) -> None: ...
    def set_global_option(self, name: str, value: str) -> None: ...
    def get_global_option(self, name: Literal["FREEZE_CORE"]) -> str: ...
    def get_datadir(self) -> str: ...


@runtime_checkable
class _Psi4(Protocol):
    __file__: str
    __version__: str
    core: _Core
    metadata: types.ModuleType


class _Selector(Protocol):
    def __call__(self, name: str, *, probe: Literal[True]) -> None: ...


@runtime_checkable
class _Procedures(Protocol):
    def select_scf_gradient(self, name: str, *, probe: Literal[True]) -> None: ...
    def select_mp2(self, name: str, *, probe: Literal[True]) -> None: ...
    def select_mp2_gradient(self, name: str, *, probe: Literal[True]) -> None: ...
    def select_mp2_property(self, name: str, *, probe: Literal[True]) -> None: ...


@runtime_checkable
class _Exceptions(Protocol):
    ManagedMethodError: type[Exception]


@runtime_checkable
class _Utilities(Protocol):
    def libint2_configuration(self) -> dict[str, list[int | None]]: ...


def _hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _metadata(module: types.ModuleType, name: str) -> str:
    # Metadata attributes are an untyped SDK boundary; only strings are accepted.
    value: object = getattr(module, name, None)
    if not isinstance(value, str):
        raise ValueError(f"Psi4 metadata {name} must be a string")
    return value


def _check_sources(root: Path, sources: dict[str, str]) -> list[Json]:
    records: list[Json] = []
    for name, expected in sources.items():
        actual = _hash(root / name)
        if actual != expected:
            raise ValueError(f"Unreviewed source bytes: {name}")
        records.append({"path": name, "sha256": actual})
    return records


def _dimensions(core: _Core) -> list[Json]:
    rows: list[Json] = []
    for name, roles in BASIS_ROLES.items():
        for number, element in enumerate(_ELEMENTS, 1):
            if element not in BASIS_ELEMENTS[name]:
                continue
            molecule = core.Molecule.from_string(
                f"0 {1 if number % 2 == 0 else 2}\n{element} 0 0 0\n"
                "symmetry c1\nno_reorient\nno_com\n",
                verbose=0,
            )
            for role in roles:
                pure = core.BasisSet.build(
                    molecule, role.upper(), name, puream=1, quiet=True
                )
                cartesian = core.BasisSet.build(
                    molecule, role.upper(), name, puream=0, quiet=True
                )
                rows.append(
                    {
                        "basis": name,
                        "role": role,
                        "element": element,
                        "spherical": pure.nbf(),
                        "cartesian": cartesian.nbf(),
                        "max_am": pure.max_am(),
                        "ecp_core": pure.n_ecp_core(),
                    }
                )
    return rows


def _routes(core: _Core) -> list[Json]:
    procedures: object = importlib.import_module("psi4.driver.procrouting.proc")
    errors: object = importlib.import_module("psi4.driver.p4util.exceptions")
    if not isinstance(procedures, _Procedures) or not isinstance(errors, _Exceptions):
        raise ValueError("The reviewed routing interfaces are unavailable")
    selectors: dict[str, _Selector] = {
        "scf.gradient": procedures.select_scf_gradient,
        "mp2.energy": procedures.select_mp2,
        "mp2.gradient": procedures.select_mp2_gradient,
        "mp2.properties": procedures.select_mp2_property,
    }
    rows: list[Json] = []
    for reference in ("RHF", "UHF", "ROHF"):
        for frozen_core in (False, True):
            core.clean_options()
            for name, value in (
                ("REFERENCE", reference),
                ("SCF_TYPE", "PK"),
                ("MP2_TYPE", "CONV"),
                ("QC_MODULE", "OCC"),
                ("FREEZE_CORE", "TRUE" if frozen_core else "FALSE"),
            ):
                core.set_global_option(name, value)
            for identity, selector in selectors.items():
                method, driver = identity.split(".")
                try:
                    selector(method, probe=True)
                    status, message = (
                        "supported",
                        "Routing probe accepted without calculation",
                    )
                except errors.ManagedMethodError as error:
                    status, message = "unsupported", str(error)
                rows.append(
                    {
                        "method": method,
                        "driver": driver,
                        "scf_type": "PK",
                        "mp2_type": "CONV",
                        "qc_module": "OCC",
                        "native_freeze_core": core.get_global_option("FREEZE_CORE"),
                        "reference": reference.lower(),
                        "frozen_core": frozen_core,
                        "status": status,
                        "message": message,
                    }
                )
    return rows


@runtime_checkable
class _Keys(Protocol):
    def __iter__(self) -> Iterator[object]: ...


def _table_keys(data: object, name: str) -> list[str]:
    table: object = getattr(data, name, None)
    if not isinstance(table, _Keys):
        raise ValueError(f"The solvent component lacks the reviewed {name} table")
    keys: list[str] = []
    for key in table:
        if not isinstance(key, str):
            raise ValueError("Solvent table keys must be strings")
        keys.append(key)
    return sorted(keys)


def inspect_build() -> dict[str, Json]:
    """Return source-pinned metadata, basis dimensions, and non-computing route probes.

    Raises:
        ValueError: Version or source bytes are outside the reviewed audit.
    """
    # Dynamic modules are unknown until their narrow SDK protocols are checked.
    psi4: object = importlib.import_module("psi4")
    if not isinstance(psi4, _Psi4):
        raise ValueError("Psi4 does not provide the inspected metadata interfaces")
    long_version = _metadata(psi4.metadata, "__version_long")
    if (
        psi4.__version__ != "1.12a1.dev43"
        or long_version != "1.12a1.dev43+60c9b2a"
        or _metadata(psi4.metadata, "__version_is_clean") != "True"
    ):
        raise ValueError("This audit only covers clean Psi4 1.12a1.dev43+60c9b2a")
    python_sources = _check_sources(Path(psi4.__file__).parent, PYTHON_SOURCES)
    basis_sources = _check_sources(
        Path(psi4.core.get_datadir()) / "basis",
        {f"{name}.gbs": digest for name, digest in BASIS_SOURCES.items()},
    )
    utilities: object = importlib.import_module("psi4.driver.p4util")
    if not isinstance(utilities, _Utilities):
        raise ValueError("Libint2 metadata interface is unavailable")
    importlib.import_module("optking")
    psi4.core.set_output_file("metadata.log", False)
    configuration: dict[str, Json] = {
        name: list(values) for name, values in utilities.libint2_configuration().items()
    }
    # A foreign SDK symbol is inspected for availability only, never called.
    sapt_api: object = getattr(psi4.core, "sapt", None)
    solvent: object = importlib.import_module("psi4.driver.procrouting.solvent")
    ddx_available: object = getattr(solvent, "_have_ddx", None)
    if not isinstance(ddx_available, bool):
        raise ValueError("The reviewed solvent availability flag is missing")
    try:
        pyddx_version = importlib.metadata.version("pyddx")
    except importlib.metadata.PackageNotFoundError:
        pyddx_version = None
    ddx_solvents: list[Json] = []
    ddx_radii: dict[str, Json] = {}
    if ddx_available:
        data: object = importlib.import_module("pyddx.data")
        ddx_solvents = list(_table_keys(data, "solvent_epsilon"))
        ddx_radii = {
            name: list(_table_keys(data, "radius_" + name)) for name in ("uff", "bondi")
        }
    return {
        "application_version": psi4.__version__,
        "version_long": long_version,
        "source_commit": AUDITED_COMMIT,
        "core_sha256": _hash(Path(psi4.core.__file__)),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "audit_sha256": _hash(Path(__file__)),
        "python_sources": python_sources,
        "basis_sources": basis_sources,
        "basis_dimensions": _dimensions(psi4.core),
        "native_sapt_available": callable(sapt_api),
        "ddx_available": ddx_available,
        "pyddx_version": pyddx_version,
        "ddx_solvents": ddx_solvents,
        "ddx_radii_elements": ddx_radii,
        "routing": _routes(psi4.core),
        "libint2": configuration,
        "optking_version": importlib.metadata.version("optking"),
        "qcelemental_version": importlib.metadata.version("qcelemental"),
        "oeprop_methods": list(psi4.core.OEProp.valid_methods),
    }


if __name__ == "__main__":
    json.dump(inspect_build(), sys.stdout, indent=2)
    sys.stdout.write("\n")
