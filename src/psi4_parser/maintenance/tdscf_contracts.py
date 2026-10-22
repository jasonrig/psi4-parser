"""Contribute reviewed TD-SCF contracts without inspecting any engine installation."""

from psi4_parser.formal.capabilities import (
    CapabilityCatalog,
    Evidence,
    MethodCapability,
    OptionCapability,
    OptionCondition,
    ProductCapability,
    Reference,
)
from psi4_parser.formal.products import TDSCF_PRODUCTS, product_quantity
from psi4_parser.formal.science import ProductName, QuantityType

_SOURCE = "https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/"
_FILES = {
    "response": "psi4/driver/procrouting/response/scf_response.py",
    "procedure": "psi4/driver/procrouting/proc.py",
    "driver": "psi4/driver/driver.py",
    "routing": "psi4/driver/procrouting/proc_table.py",
    "hf-definition": "psi4/driver/procrouting/dft/hyb_functionals.py",
    "gga-definition": "psi4/driver/procrouting/dft/gga_functionals.py",
    "hybrid-definition": "psi4/driver/procrouting/dft/libxc_functionals.py",
    "options": "psi4/src/read_options.cc",
    "manual": "doc/sphinxman/source/tdscf.rst",
}


def tdscf_catalog() -> CapabilityCatalog:
    """Return independently sourced HF/PBE/B3LYP response construction rules.

    These entries describe scientific/input relationships across releases. Their
    source revision is provenance; no binary or dependency audit is required.
    Basis dimensions and orbital coverage can be supplied by another contribution.
    """
    evidence = tuple(
        Evidence(id="source-tdscf-" + name, source=_SOURCE + path, kind="source")
        for name, path in _FILES.items()
    )
    references: tuple[Reference, ...] = ("rhf", "uhf", "rohf")
    names: tuple[ProductName, ...] = ("electronic_energy", *sorted(TDSCF_PRODUCTS))
    methods: list[MethodCapability] = []
    for method in ("td-hf", "td-scf", "td-pbe", "td-b3lyp"):
        for reference in references:
            supported = reference == "rhf" or (
                reference == "uhf" and method in {"td-hf", "td-scf"}
            )
            spin_features = (
                ("tdscf_spin:unrestricted",)
                if reference == "uhf"
                else ("tdscf_spin:singlet", "tdscf_spin:triplet", "tdscf_spin:both")
                if method in {"td-hf", "td-scf"}
                else ("tdscf_spin:singlet",)
            )
            sources = (
                "source-tdscf-response",
                "source-tdscf-procedure",
                "source-tdscf-driver",
                "source-tdscf-routing",
                "source-tdscf-manual",
                "source-tdscf-"
                + (
                    "hf-definition"
                    if method in {"td-hf", "td-scf"}
                    else "gga-definition"
                    if method == "td-pbe"
                    else "hybrid-definition"
                ),
            )
            methods.append(
                MethodCapability(
                    method=method,
                    driver="energy",
                    reference=reference,
                    status="supported" if supported else "unsupported",
                    quantity=QuantityType(meaning="electronic_energy", unit="hartree"),
                    features=(
                        "tdscf",
                        "tdscf_approximation:rpa",
                        "tdscf_approximation:tda",
                        "cartesian_basis",
                        *spin_features,
                    ),
                    conditions=(
                        OptionCondition(
                            name="scf_type", values=("PK",), case_sensitive=False
                        ),
                        OptionCondition(name="ddx", values=(False,)),
                        OptionCondition(name="pcm", values=(False,)),
                    ),
                    options=("scf_type", "maxiter", "e_convergence", "d_convergence"),
                    products=tuple(
                        ProductCapability(
                            name=name,
                            status="supported" if supported else "unsupported",
                            quantity=product_quantity(name),
                            evidence=("source-tdscf-response", "source-tdscf-driver"),
                        )
                        for name in names
                    ),
                    evidence=sources,
                )
            )
    return CapabilityCatalog(
        id="tdscf-source-rules",
        evidence=evidence,
        methods=tuple(methods),
        options=(
            OptionCapability(
                name="tdscf_triplets",
                module="SCF",
                status="supported",
                values=("NONE", "ONLY", "ALSO"),
                evidence=("source-tdscf-options",),
            ),
            OptionCapability(
                name="tdscf_tda",
                module="SCF",
                status="supported",
                types=("boolean",),
                evidence=("source-tdscf-options",),
            ),
        ),
    )
