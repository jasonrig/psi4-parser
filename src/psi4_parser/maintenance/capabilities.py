"""Collect reviewed engine metadata and curate a conditional capability snapshot."""

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

import click
from pydantic import Field

from psi4_parser._cli_types import EXECUTABLE
from psi4_parser._files import atomic_replace
from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import (
    BasisCapability,
    BasisFunctions,
    CapabilityCatalog,
    ComponentCapability,
    DerivativeRoute,
    EnvironmentCapability,
    Evidence,
    MethodCapability,
    OptionCapability,
    OptionCondition,
    ProductCapability,
    Reference,
    Support,
)
from psi4_parser.formal.catalog_composition import combine_catalogs
from psi4_parser.formal.extrapolation_models import BasisSequence
from psi4_parser.formal.products import (
    PROPERTY_NAMES,
    SAPT_VARIABLES,
    THERMAL_PRODUCTS,
    product_quantity,
)
from psi4_parser.formal.science import Driver, ProductName, QuantityType
from psi4_parser.maintenance.capability_reference import (
    AUDITED_COMMIT,
    BASIS_ELEMENTS,
    BASIS_ROLES,
    BASIS_SOURCES,
    PYTHON_SOURCES,
)
from psi4_parser.maintenance.tdscf_contracts import tdscf_catalog

_CATALOG_ID = "psi4"
_SOURCE_URL = f"https://github.com/psi4/psi4/blob/{AUDITED_COMMIT}/"
_OPTIONS_SHA256 = "4c90f0223e9a0203b8dc626ec0976ccb27dbd555d0f2f7c2d5070d590c26f093"
_PROBE_SOURCE = (
    f"package://psi4_parser.formal.catalogs/{_CATALOG_ID}/reference-audit.json"
)
_DERIVATIVE_LEVELS = 3


class SourceFingerprint(Record):
    """Bind an inspected engine source or basis definition to its bytes."""

    path: str = Field(
        description="Path within the installed Python or basis directory."
    )
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$", description="Source file SHA-256.")


class InspectedBasis(Record):
    """Count orbital functions without computing electronic quantities."""

    basis: str = Field(description="Inspected orbital basis name.")
    role: str = Field(default="basis", description="Orbital or inspected fitting role.")
    element: str = Field(description="Element symbol of the inspected center.")
    spherical: int = Field(ge=1, description="Spherical orbital function count.")
    cartesian: int = Field(ge=1, description="Cartesian orbital function count.")
    max_am: int = Field(ge=0, description="Largest shell angular momentum.")
    ecp_core: int = Field(ge=0, description="Automatically replaced ECP electrons.")


class InspectedRoute(Record):
    """Record the outcome of a reviewed selector called with probe=True."""

    method: Literal["scf", "mp2"] = Field(description="Inspected method.")
    driver: Literal["energy", "gradient", "properties"] = Field(
        description="Inspected selector."
    )
    reference: Reference = Field(description="Explicit SCF reference for the probe.")
    frozen_core: bool = Field(description="Explicit core treatment for the probe.")
    scf_type: str = Field(description="Explicit SCF integral algorithm.")
    mp2_type: str = Field(description="Explicit MP2 integral algorithm.")
    qc_module: str = Field(description="Explicit implementation module.")
    native_freeze_core: str = Field(
        description="Native value after Psithon-compatible setting."
    )
    status: Literal["supported", "unsupported"] = Field(
        description="Selector's outcome."
    )
    message: str = Field(description="Routing acceptance or managed-method error.")


class CapabilityAudit(Record):
    """Retain reproducible metadata evidence for one reviewed engine binary."""

    application_version: str = Field(description="Psi4 release/development version.")
    version_long: str = Field(description="Version with source revision suffix.")
    source_commit: str = Field(description="Reviewed complete source commit.")
    core_sha256: str = Field(
        pattern=r"^[a-f0-9]{64}$", description="Native core binary SHA-256."
    )
    python_version: str = Field(
        description="Interpreter version used for the inspection."
    )
    platform: str = Field(description="Operating-system and architecture description.")
    audit_sha256: str = Field(
        pattern=r"^[a-f0-9]{64}$", description="Inspection script SHA-256."
    )
    python_sources: tuple[SourceFingerprint, ...] = Field(
        description="Verified Python source bytes."
    )
    basis_sources: tuple[SourceFingerprint, ...] = Field(
        description="Verified basis definition bytes."
    )
    basis_dimensions: tuple[InspectedBasis, ...] = Field(
        description="Measured orbital dimensions."
    )
    native_sapt_available: bool = Field(
        default=False,
        description="Native SAPT entry point is callable; never executed.",
    )
    ddx_available: bool = Field(
        default=False, description="The reviewed Psi4 DDX interface imported pyddx."
    )
    pyddx_version: str | None = Field(
        default=None, description="Optional pyddx distribution version; null if absent."
    )
    ddx_solvents: tuple[str, ...] = Field(
        default=(), description="Available named static dielectric lookups."
    )
    ddx_radii_elements: dict[str, tuple[str, ...]] = Field(
        default_factory=dict,
        description="Available atom labels in each DDX cavity radius table.",
    )
    routing: tuple[InspectedRoute, ...] = Field(
        description="Non-computing routing probes."
    )
    libint2: dict[str, tuple[int | None, ...]] = Field(
        description="Compiled integral angular limits."
    )
    optking_version: str = Field(description="Imported optimizer distribution version.")
    qcelemental_version: str = Field(
        description="Native vibration-record Datum serializer distribution version."
    )
    oeprop_methods: tuple[str, ...] = Field(
        description="Registered one-electron property names."
    )


def inspect_capabilities(
    engine_python: Path, *, timeout: float = 120
) -> CapabilityAudit:
    """Inspect a reviewed Psi4 build in its own interpreter, without running jobs.

    Args:
        engine_python: Explicit engine Python executable or launcher.
        timeout: Positive inspection timeout in seconds, default 120.

    Returns:
        Validated source hashes, routing probes, basis dimensions, and build identity.

    Raises:
        ValueError: The engine, source bytes, or inspection result fails the audit.
    """
    if timeout <= 0:
        raise ValueError("Use a positive inspection timeout")
    reference = Path(__file__).with_name("capability_reference.py")
    with TemporaryDirectory(prefix="psi4-capability-audit-") as temporary:
        completed = subprocess.run(  # noqa: S603 - Explicit engine executable; fixed metadata-only script, no shell.
            [str(engine_python), str(reference)],
            cwd=temporary,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    if completed.returncode:
        raise ValueError(
            f"Engine capability inspection failed: {completed.stderr[-2000:]}"
        )
    audit = CapabilityAudit.model_validate_json(completed.stdout)
    if audit.source_commit != AUDITED_COMMIT:
        raise ValueError("Inspection did not use the reviewed source revision")
    if audit.audit_sha256 != hashlib.sha256(reference.read_bytes()).hexdigest():
        raise ValueError("Inspection script changed while the audit was running")
    return audit


def _quantity(driver: Driver) -> QuantityType:
    if driver == "gradient":
        return QuantityType(meaning="gradient", unit="hartree/bohr", shape=("atoms", 3))
    if driver == "hessian":
        return QuantityType(
            meaning="hessian", unit="hartree/bohr^2", shape=("3*atoms", "3*atoms")
        )
    return QuantityType(meaning="electronic_energy", unit="hartree")


def _conditions(method: str, frozen: bool | None = None) -> tuple[OptionCondition, ...]:
    result: tuple[OptionCondition, ...] = (
        OptionCondition(name="scf_type", values=("PK",), case_sensitive=False),
        OptionCondition(name="ddx", values=(False,)),
        OptionCondition(name="pcm", values=(False,)),
    )
    if method == "mp2":
        result += (
            OptionCondition(name="mp2_type", values=("CONV",), case_sensitive=False),
            OptionCondition(name="qc_module", values=("OCC",), case_sensitive=False),
        )
    if frozen is not None:
        result += (OptionCondition(name="freeze_core", values=(frozen,)),)
    return result


def _features(driver: Driver, oeprop: tuple[str, ...]) -> tuple[str, ...]:
    result: tuple[str, ...] = ("cartesian_basis", "frozen_core")
    if driver == "energy":
        result += ("ghost_centers",)
    if driver == "optimize":
        result += ("constraints",)
    if driver == "frequency":
        result += ("vibrational_analysis:ideal_gas_rrho", "native_vibrec")
    if driver == "properties":
        reviewed = {
            "DIPOLE",
            "QUADRUPOLE",
            "MULLIKEN_CHARGES",
            "LOWDIN_CHARGES",
            "WIBERG_LOWDIN_INDICES",
            "MAYER_INDICES",
        }
        result += tuple(
            f"property:{name.lower()}" for name in oeprop if name in reviewed
        )
    return result


@dataclass(frozen=True)
class _Case:
    method: str
    reference: Reference
    driver: Driver
    route: DerivativeRoute
    frozen: bool | None


def _case_status(audit: CapabilityAudit, case: _Case) -> Support:
    if case.method != "mp2":
        if (
            case.driver in {"hessian", "frequency"}
            and case.route != "finite_difference"
        ):
            return "unsupported" if case.reference == "rohf" else "supported"
        return "supported"
    if case.driver == "properties":
        return "unsupported"
    if case.route == "analytic":
        if case.driver in {"hessian", "frequency"}:
            return "unsupported"
        if case.driver in {"gradient", "optimize"}:
            return next(
                item.status
                for item in audit.routing
                if item.method == "mp2"
                and item.driver == "gradient"
                and item.reference == case.reference
                and item.frozen_core == case.frozen
            )
    return "supported"


def _products(
    driver: Driver, status: Support, oeprop: tuple[str, ...]
) -> tuple[ProductCapability, ...]:
    names: list[ProductName] = [
        "gradient"
        if driver == "gradient"
        else "hessian"
        if driver == "hessian"
        else "electronic_energy"
    ]
    if driver == "frequency":
        names.extend(
            (
                "hessian",
                "harmonic_frequencies",
                "normal_modes",
                *sorted(THERMAL_PRODUCTS),
            )
        )
    if driver == "properties":
        names.extend(
            name for name, requested in PROPERTY_NAMES.items() if requested in oeprop
        )
    return tuple(
        ProductCapability(
            name=name,
            status=status,
            quantity=product_quantity(name),
            evidence=("source-driver", "source-vibrations", "source-native-writer")
            if driver == "frequency"
            else ("source-oeprop",)
            if driver == "properties"
            else ("source-driver",),
        )
        for name in names
    )


def _method_case(
    audit: CapabilityAudit, case: _Case, bases: tuple[str, ...]
) -> MethodCapability:
    status = _case_status(audit, case)
    conditions = _conditions(case.method, case.frozen)
    if (
        case.method != "mp2"
        and case.driver in {"hessian", "frequency"}
        and case.route != "finite_difference"
    ):
        conditions += (
            OptionCondition(name="basis", values=bases, case_sensitive=False),
        )
    options: tuple[str, ...] = ("scf_type", "e_convergence", "d_convergence", "maxiter")
    if case.method == "mp2":
        options += ("mp2_type", "qc_module")
    return MethodCapability(
        method=case.method,
        driver=case.driver,
        reference=case.reference,
        derivative_route=case.route,
        status=status,
        quantity=_quantity(case.driver),
        products=_products(case.driver, status, audit.oeprop_methods),
        conditions=conditions,
        features=_features(case.driver, audit.oeprop_methods),
        options=options,
        bases=bases,
        components=("optking",)
        if case.driver == "optimize"
        else ("qcelemental",)
        if case.driver == "frequency"
        else (),
        evidence=("source-procedures", "source-driver", "runtime-metadata"),
    )


def _methods(audit: CapabilityAudit) -> tuple[MethodCapability, ...]:
    rows: list[MethodCapability] = []
    references: tuple[Reference, ...] = ("rhf", "uhf", "rohf")
    drivers: tuple[Driver, ...] = (
        "energy",
        "optimize",
        "frequency",
        "gradient",
        "hessian",
        "properties",
    )
    for method in ("scf", "hf", "mp2"):
        for reference in references:
            for driver in drivers:
                routes: tuple[DerivativeRoute, ...] = (
                    ("automatic",)
                    if driver in {"energy", "properties"}
                    else ("automatic", "analytic", "finite_difference")
                )
                for route in routes:
                    core_cases = (
                        (False, True)
                        if method == "mp2"
                        and route == "analytic"
                        and driver in {"gradient", "optimize"}
                        else (None,)
                    )
                    for frozen in core_cases:
                        case = _Case(method, reference, driver, route, frozen)
                        rows.extend(
                            _method_case(audit, case, bases)
                            for bases in (
                                tuple(
                                    name
                                    for name, roles in BASIS_ROLES.items()
                                    if "basis" in roles
                                ),
                            )
                        )
    return tuple(rows)


_SAPT_METHODS = (
    "sapt0",
    "ssapt0",
    "sapt2",
    "sapt2+",
    "sapt2+(3)",
    "sapt2+3",
    "sapt2+(ccd)",
    "sapt2+(3)(ccd)",
    "sapt2+3(ccd)",
    "sapt2+dmp2",
    "sapt2+(3)dmp2",
    "sapt2+3dmp2",
    "sapt2+(ccd)dmp2",
    "sapt2+(3)(ccd)dmp2",
    "sapt2+3(ccd)dmp2",
)


def _sapt_case(
    method: str,
    reference: Reference,
    basis: str,
    algorithm: str,
) -> MethodCapability:
    status: Support = (
        "supported" if reference == "rhf" or method == "sapt0" else "unsupported"
    )
    conditions: tuple[OptionCondition, ...] = (
        OptionCondition(name="scf_type", values=(algorithm,), case_sensitive=False),
        OptionCondition(name="ddx", values=(False,)),
        OptionCondition(name="pcm", values=(False,)),
        OptionCondition(name="basis", values=(basis,), case_sensitive=False),
        OptionCondition(
            name="df_basis_sapt", values=(basis + "-ri",), case_sensitive=False
        ),
        OptionCondition(
            name="df_basis_elst", values=(basis + "-jkfit",), case_sensitive=False
        ),
    )
    if algorithm == "DF":
        conditions += (
            OptionCondition(
                name="df_basis_scf", values=(basis + "-jkfit",), case_sensitive=False
            ),
        )
    options: tuple[str, ...] = ("scf_type", "maxiter", "e_convergence", "d_convergence")
    if method.endswith("dmp2"):
        conditions += (
            OptionCondition(name="mp2_type", values=("CONV",), case_sensitive=False),
            OptionCondition(name="qc_module", values=("OCC",), case_sensitive=False),
        )
        options += ("mp2_type", "qc_module")
    features: tuple[str, ...] = (
        "sapt",
        "sapt_basis:dimer",
        "sapt_midbond",
        "ghost_centers",
        "frozen_core",
        "cartesian_basis",
        "auxiliary_basis:df_basis_sapt",
        "auxiliary_basis:df_basis_elst",
        "auxiliary_basis:df_basis_scf",
    )
    if reference != "rohf":
        features += ("sapt_induction:coupled",)
    if method == "sapt0":
        features += ("sapt_induction:uncoupled",)
        if reference == "rhf":
            features += ("sapt_basis:monomer",)
    evidence = (
        "source-procedures",
        "source-sapt-molecule",
        "source-sapt-components",
        "runtime-metadata",
    )
    return MethodCapability(
        method=method,
        driver="energy",
        reference=reference,
        status=status,
        quantity=QuantityType(meaning="interaction_energy", unit="hartree"),
        features=features,
        options=options,
        bases=(basis,),
        conditions=conditions,
        components=("sapt",),
        evidence=evidence,
        products=tuple(
            ProductCapability(
                name=name,
                status=status,
                quantity=product_quantity(name),
                evidence=evidence,
            )
            for name in SAPT_VARIABLES
        ),
    )


def _sapt_methods() -> tuple[MethodCapability, ...]:
    references: tuple[Reference, ...] = ("rhf", "uhf", "rohf")
    return tuple(
        _sapt_case(method, reference, basis, algorithm)
        for method in _SAPT_METHODS
        for reference in references
        for basis in ("cc-pvdz", "cc-pvtz", "cc-pvqz")
        for algorithm in (("PK",) if method.endswith("dmp2") else ("PK", "DF"))
    )


def _check_fingerprints(audit: CapabilityAudit) -> None:
    for actual, expected in (
        (audit.python_sources, PYTHON_SOURCES),
        (
            audit.basis_sources,
            {f"{name}.gbs": value for name, value in BASIS_SOURCES.items()},
        ),
    ):
        if (
            len(actual) != len(expected)
            or {item.path: item.sha256 for item in actual} != expected
        ):
            raise ValueError("Curation requires the reviewed source fingerprints")


def _check_dimensions(audit: CapabilityAudit) -> None:
    expected = {
        (basis, role, element)
        for basis, roles in BASIS_ROLES.items()
        for role in roles
        for element in BASIS_ELEMENTS[basis]
    }
    actual = {(item.basis, item.role, item.element) for item in audit.basis_dimensions}
    if len(audit.basis_dimensions) != len(expected) or actual != expected:
        raise ValueError("Curation requires complete, unique basis dimensions")
    if any(
        item.ecp_core or item.cartesian < item.spherical
        for item in audit.basis_dimensions
    ):
        raise ValueError("Curation requires consistent non-ECP basis dimensions")


def _check_routing(audit: CapabilityAudit) -> None:
    selectors = (
        ("scf", "gradient"),
        ("mp2", "energy"),
        ("mp2", "gradient"),
        ("mp2", "properties"),
    )
    expected = {
        (method, driver, reference, frozen)
        for method, driver in selectors
        for reference in ("rhf", "uhf", "rohf")
        for frozen in (False, True)
    }
    actual = {
        (item.method, item.driver, item.reference, item.frozen_core)
        for item in audit.routing
    }
    if len(audit.routing) != len(expected) or actual != expected:
        raise ValueError("Curation requires complete, unique routing probes")
    for item in audit.routing:
        if (item.scf_type, item.mp2_type, item.qc_module) != (
            "PK",
            "CONV",
            "OCC",
        ) or item.native_freeze_core != ("TRUE" if item.frozen_core else "FALSE"):
            raise ValueError(
                "Routing probe settings differ from the reviewed conditions"
            )
        # Curation's automatic/fallback claims require these positive selectors.
        if (
            item.method == "scf" or item.driver == "energy"
        ) and item.status != "supported":
            raise ValueError("Routing probes do not support the curated fallback paths")


def _validate_audit(audit: CapabilityAudit) -> None:
    if audit.qcelemental_version != "0.51.3":
        raise ValueError(
            "Curation requires the reviewed QCEElemental Datum serialization version"
        )
    if audit.source_commit != AUDITED_COMMIT:
        raise ValueError("Curation requires the reviewed application revision")
    reference = Path(__file__).with_name("capability_reference.py")
    if audit.audit_sha256 != hashlib.sha256(reference.read_bytes()).hexdigest():
        raise ValueError("Curation requires the reviewed inspection script")
    _check_fingerprints(audit)
    _check_dimensions(audit)
    _check_routing(audit)
    if audit.ddx_available and (
        audit.pyddx_version is None
        or not audit.ddx_solvents
        or set(audit.ddx_radii_elements) != {"uff", "bondi"}
        or any(not values for values in audit.ddx_radii_elements.values())
    ):
        raise ValueError(
            "Curation requires DDX version, solvent, and cavity table metadata"
        )
    if set(audit.libint2) != {"onebody", "eri", "eri2", "eri3"} or any(
        len(limits) != _DERIVATIVE_LEVELS
        or any(limit is not None and limit < 0 for limit in limits)
        for limits in audit.libint2.values()
    ):
        raise ValueError("Curation requires complete integral derivative limits")


def _basis_sequence(name: str) -> BasisSequence | None:
    orbital = name.removesuffix("-jkfit").removesuffix("-ri")
    cardinals = {"cc-pvdz": 2, "cc-pvtz": 3, "cc-pvqz": 4}
    if orbital not in cardinals:
        return None
    suffix = (
        "-JKFIT" if name.endswith("-jkfit") else "-RI" if name.endswith("-ri") else ""
    )
    return BasisSequence(family="cc-pvXZ" + suffix, cardinal=cardinals[orbital])


def _ddx_methods(audit: CapabilityAudit) -> tuple[MethodCapability, ...]:
    names = tuple(name for name, roles in BASIS_ROLES.items() if "basis" in roles)
    references: tuple[Reference, ...] = ("rhf", "uhf", "rohf")
    return tuple(
        MethodCapability(
            method=method,
            driver="energy",
            reference=reference,
            status="supported",
            quantity=_quantity("energy"),
            bases=names,
            conditions=(
                OptionCondition(name="scf_type", values=("PK",), case_sensitive=False),
                OptionCondition(name="ddx", values=(True,)),
                OptionCondition(name="pcm", values=(False,)),
                OptionCondition(
                    name="ddx_model",
                    module="DDX",
                    values=(model,),
                    case_sensitive=False,
                ),
            ),
            features=("ddx", f"ddx_model:{model}", "cartesian_basis", "frozen_core"),
            options=(
                "scf_type",
                "maxiter",
                "e_convergence",
                "d_convergence",
                *_DDX_OPTIONS,
            ),
            products=_products("energy", "supported", audit.oeprop_methods),
            components=("pyddx",),
            evidence=(
                "source-ddx",
                "source-procedures",
                "source-scf-iteration",
                "runtime-metadata",
            ),
        )
        for method in ("scf", "hf")
        for reference in references
        for model in ("pcm", "cosmo", "lpb")
    )


_DDX_OPTIONS = (
    "ddx.ddx_lmax",
    "ddx.ddx_model",
    "ddx.ddx_solvent",
    "ddx.ddx_solvent_epsilon",
    "ddx.ddx_radii_set",
    "ddx.ddx_radii_scaling",
    "ddx.ddx_solvent_kappa",
)


def _pcm_methods(audit: CapabilityAudit) -> tuple[MethodCapability, ...]:
    names = tuple(name for name, roles in BASIS_ROLES.items() if "basis" in roles)
    references: tuple[Reference, ...] = ("rhf", "uhf")
    return tuple(
        MethodCapability(
            method=method,
            driver="energy",
            reference=reference,
            status="supported",
            quantity=_quantity("energy"),
            bases=names,
            conditions=(
                OptionCondition(name="scf_type", values=("PK",), case_sensitive=False),
                OptionCondition(name="pcm", values=(True,)),
                OptionCondition(name="ddx", values=(False,)),
            ),
            features=(
                "pcm",
                "pcm_solver:iefpcm",
                "pcm_solver:cpcm",
                "cartesian_basis",
                "frozen_core",
            ),
            options=(
                "scf_type",
                "maxiter",
                "e_convergence",
                "d_convergence",
                "pcm.pcm_scf_type",
            ),
            products=_products("energy", "supported", audit.oeprop_methods),
            components=("pcmsolver",),
            evidence=(
                "source-pcm-input",
                "documentation-pcmsolver-input",
                "source-procedures",
                "source-scf-iteration",
            ),
        )
        for method in ("scf", "hf")
        for reference in references
    )


def _ddx_options() -> tuple[OptionCapability, ...]:
    return (
        OptionCapability(
            name="ddx_lmax",
            module="DDX",
            status="supported",
            types=("integer",),
            minimum=0,
            evidence=("source-options",),
        ),
        OptionCapability(
            name="ddx_model",
            module="DDX",
            status="supported",
            values=("PCM", "COSMO", "LPB"),
            case_sensitive=False,
            evidence=("source-options",),
        ),
        OptionCapability(
            name="ddx_solvent",
            module="DDX",
            status="supported",
            types=("string",),
            evidence=("source-ddx",),
        ),
        OptionCapability(
            name="ddx_radii_set",
            module="DDX",
            status="supported",
            values=("UFF", "BONDI"),
            case_sensitive=False,
            evidence=("source-options",),
        ),
        *(
            OptionCapability(
                name=name,
                module="DDX",
                status="supported",
                types=("real", "integer"),
                minimum=minimum,
                evidence=("source-options",),
            )
            for name, minimum in (
                ("ddx_solvent_epsilon", 1),
                ("ddx_radii_scaling", 0),
                ("ddx_solvent_kappa", 0),
            )
        ),
    )


def curate_catalog(audit: CapabilityAudit) -> CapabilityCatalog:
    """Reconstruct shared contract entries from the retained reference evidence.

    This developer operation reproduces one historical evidence contribution.
    It is not a release certification workflow; engine updates need no new audit
    or catalog. Each entry retains its own source provenance.

    Args:
        audit: Metadata collected by the source-pinned standalone inspector.

    Returns:
        Release-independent scientific/input contracts from the reviewed sources.

    Raises:
        ValueError: Source fingerprints, probe conditions, or metadata are incomplete
            or differ from the reviewed scope.
    """  # noqa: DOC502 - _validate_audit enforces the documented evidence errors.
    _validate_audit(audit)
    build = f"sha256:{audit.core_sha256}"
    audit_bytes = (audit.model_dump_json(indent=2) + "\n").encode()
    hashes = {item.path: item.sha256 for item in audit.python_sources}
    evidence = (
        Evidence(
            id="documentation-pcmsolver-input",
            source="https://pcmsolver.readthedocs.io/en/stable/users/input.html",
            kind="documentation",
        ),
        Evidence(
            id="source-pcm-input",
            source=_SOURCE_URL + "psi4/driver/p4util/python_helpers.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/p4util/python_helpers.py"],
        ),
        Evidence(
            id="source-ddx",
            source=_SOURCE_URL + "psi4/driver/procrouting/solvent/ddx.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/procrouting/solvent/ddx.py"],
        ),
        Evidence(
            id="source-scf-iteration",
            source=_SOURCE_URL + "psi4/driver/procrouting/scf_proc/scf_iterator.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/procrouting/scf_proc/scf_iterator.py"],
        ),
        Evidence(
            id="source-sapt-molecule",
            source=_SOURCE_URL + "psi4/driver/procrouting/proc_util.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/procrouting/proc_util.py"],
        ),
        Evidence(
            id="source-sapt-components",
            source=_SOURCE_URL + "psi4/driver/qcdb/psivardefs.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/qcdb/psivardefs.py"],
        ),
        Evidence(
            id="source-basis-sequences",
            source=_SOURCE_URL + "psi4/driver/driver_cbs.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/driver_cbs.py"],
        ),
        Evidence(
            id="source-extrapolation",
            source=_SOURCE_URL + "psi4/driver/driver_cbs_helper.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/driver_cbs_helper.py"],
        ),
        Evidence(
            id="source-native-writer",
            source=_SOURCE_URL + "psi4/src/psi4/libmints/get_writer_file_prefix.cc",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest="53ed270125111059e6f157d7a60c5582706f4ba7300abc5f717727151bb18ed0",
        ),
        Evidence(
            id="source-vibrations",
            source=_SOURCE_URL + "psi4/driver/qcdb/vib.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/qcdb/vib.py"],
        ),
        Evidence(
            id="source-oeprop",
            source=_SOURCE_URL + "psi4/src/psi4/libmints/oeprop.cc",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest="c1f250d525d937e1a2203fabaaff48fda5b1c97f439eac3d0efb80420801e004",
        ),
        Evidence(
            id="source-procedures",
            source=_SOURCE_URL + "psi4/driver/procrouting/proc.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/procrouting/proc.py"],
        ),
        Evidence(
            id="source-driver",
            source=_SOURCE_URL + "psi4/driver/driver.py",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=hashes["driver/driver.py"],
        ),
        Evidence(
            id="source-options",
            source=_SOURCE_URL + "psi4/src/read_options.cc",
            kind="source",
            application_version=audit.application_version,
            build=build,
            digest=_OPTIONS_SHA256,
        ),
        Evidence(
            id="runtime-metadata",
            source=_PROBE_SOURCE,
            kind="probe",
            application_version=audit.application_version,
            build=build,
            digest=hashlib.sha256(audit_bytes).hexdigest(),
        ),
    )
    bases = tuple(
        BasisCapability(
            name=name,
            role=role,
            status="supported",
            elements=tuple(
                item.element
                for item in audit.basis_dimensions
                if item.basis == name and item.role == role
            ),
            functions=tuple(
                BasisFunctions(
                    element=item.element,
                    spherical=item.spherical,
                    cartesian=item.cartesian,
                )
                for item in audit.basis_dimensions
                if item.basis == name and item.role == role
            ),
            sequence=_basis_sequence(name),
            evidence=("runtime-metadata", "source-basis-sequences"),
        )
        for name, role in sorted(
            {(item.basis, item.role) for item in audit.basis_dimensions}
        )
    )
    options = (
        OptionCapability(
            name="scf_type",
            status="supported",
            case_sensitive=False,
            values=(
                "DIRECT",
                "DF",
                "MEM_DF",
                "DISK_DF",
                "PK",
                "OUT_OF_CORE",
                "CD",
                "GTFOCK",
                "DFDIRJ",
                "DFDIRJ+COSX",
                "DFDIRJ+LINK",
                "DFDIRJ+SNLINK",
            ),
            evidence=("source-options",),
        ),
        OptionCapability(
            name="mp2_type",
            status="supported",
            values=("DF", "CONV", "CD"),
            case_sensitive=False,
            evidence=("source-options",),
        ),
        OptionCapability(
            name="qc_module",
            status="supported",
            values=(
                "CCENERGY",
                "DETCI",
                "DFMP2",
                "FNOCC",
                "OCC",
                "CCT3",
                "BUILTIN",
                "MRCC",
                "F12",
            ),
            case_sensitive=False,
            evidence=("source-options",),
        ),
        OptionCapability(
            name="maxiter",
            status="supported",
            types=("integer",),
            minimum=1,
            evidence=("source-options",),
        ),
        *(
            OptionCapability(
                name=name,
                status="supported",
                types=("integer", "real"),
                minimum=0,
                evidence=("source-options",),
            )
            for name in ("e_convergence", "d_convergence")
        ),
    )
    catalog = CapabilityCatalog(
        id=_CATALOG_ID,
        evidence=evidence,
        methods=(
            *_methods(audit),
            *_sapt_methods(),
            *_ddx_methods(audit),
            *_pcm_methods(audit),
        ),
        bases=bases,
        options=(
            *options,
            *_ddx_options(),
            OptionCapability(
                name="pcm_scf_type",
                module="PCM",
                status="supported",
                values=("TOTAL", "SEPARATE"),
                case_sensitive=False,
                evidence=("source-options",),
            ),
        ),
        components=(
            ComponentCapability(
                name="pyddx",
                version=audit.pyddx_version,
                status="supported" if audit.ddx_available else "unsupported",
                evidence=("runtime-metadata",),
            ),
            ComponentCapability(
                name="sapt",
                version=audit.application_version,
                status="supported" if audit.native_sapt_available else "unsupported",
                evidence=("runtime-metadata",),
            ),
            ComponentCapability(
                name="qcelemental",
                version=audit.qcelemental_version,
                status="supported",
                evidence=("runtime-metadata",),
            ),
            ComponentCapability(
                name="optking",
                version=audit.optking_version,
                status="supported",
                evidence=("runtime-metadata",),
            ),
        ),
        environments=tuple(
            EnvironmentCapability(
                kind="ddx",
                radii_set=table,
                status="supported" if audit.ddx_available else "unknown",
                elements=audit.ddx_radii_elements.get(table, ()),
                solvents=audit.ddx_solvents,
                evidence=("source-ddx", "runtime-metadata"),
            )
            for table in ("uff", "bondi")
        ),
    )
    return combine_catalogs(catalog, tdscf_catalog())


@click.command()
@click.option("--engine-python", type=EXECUTABLE, required=True)
@click.option(
    "--destination", type=click.Path(file_okay=False, path_type=Path), required=True
)
def main(engine_python: Path, destination: Path) -> None:
    """Inspect a reviewed engine and save a new audit/catalog directory.

    Args:
        engine_python: Explicit Psi4 Python executable.
        destination: New destination whose parent exists; never overwritten.

    Raises:
        click.ClickException: Inspection, curation, or saving fails.
    """
    try:
        audit = inspect_capabilities(engine_python)
        catalog = curate_catalog(audit)
        destination.mkdir(mode=0o700)
        atomic_replace(
            destination / "reference-audit.json",
            (audit.model_dump_json(indent=2) + "\n").encode(),
            mode=0o600,
        )
        atomic_replace(
            destination / "catalog.json",
            (catalog.model_dump_json(indent=2) + "\n").encode(),
            mode=0o600,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise click.ClickException(str(error)[:2000]) from error
    click.echo(str(destination.absolute()))


if __name__ == "__main__":
    main()
