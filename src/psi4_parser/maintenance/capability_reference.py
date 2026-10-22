"""Inspect a reviewed Psi4 build's metadata without running chemistry drivers.

Run this standalone file in the engine's interpreter. Structural protocols keep
the small metadata boundary typed without importing Psi4 into the parser runtime.
The collector records basis dimensions and non-computing route observations.
"""

import importlib
import json
import sys
from collections.abc import Iterator, Sequence
from typing import Literal, Protocol, runtime_checkable

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None

AUDITED_COMMIT = "60c9b2a773c05abc26991c5ed48cf9862cdb4978"
"""Source revision cited by the maintained scientific rules."""


BASIS_NAMES = (
    "cc-pvdz-ri",
    "cc-pvtz-ri",
    "cc-pvqz-ri",
    "cc-pvdz-jkfit",
    "cc-pvtz-jkfit",
    "cc-pvqz-jkfit",
    "sto-3g",
    "cc-pvdz",
    "cc-pvtz",
    "cc-pvqz",
    "def2-svp",
)
"""Orbital and fitting bases measured by the reference collector."""

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
    for name in BASIS_NAMES
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
    for name in BASIS_NAMES
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
    core: _Core


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
    """Return measured basis dimensions and non-computing routing observations.

    Raises:
        ValueError: The configured engine lacks the required inspection interfaces.
    """
    # Dynamic modules are unknown until their narrow SDK protocols are checked.
    psi4: object = importlib.import_module("psi4")
    if not isinstance(psi4, _Psi4):
        raise ValueError("Psi4 does not provide the inspected metadata interfaces")
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
    ddx_solvents: list[Json] = []
    ddx_radii: dict[str, Json] = {}
    if ddx_available:
        data: object = importlib.import_module("pyddx.data")
        ddx_solvents = list(_table_keys(data, "solvent_epsilon"))
        ddx_radii = {
            name: list(_table_keys(data, "radius_" + name)) for name in ("uff", "bondi")
        }
    return {
        "basis_dimensions": _dimensions(psi4.core),
        "native_sapt_available": callable(sapt_api),
        "ddx_available": ddx_available,
        "ddx_solvents": ddx_solvents,
        "ddx_radii_elements": ddx_radii,
        "routing": _routes(psi4.core),
        "libint2": configuration,
        "oeprop_methods": list(psi4.core.OEProp.valid_methods),
    }


if __name__ == "__main__":
    json.dump(inspect_build(), sys.stdout, indent=2)
    sys.stdout.write("\n")
