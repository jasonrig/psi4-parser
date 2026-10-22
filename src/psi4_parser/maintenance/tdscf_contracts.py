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
    "response": (
        "psi4/driver/procrouting/response/scf_response.py",
        "4bd88655499b4fb55e70ed494d7b64875e63b30ec62d25e65d935561b191e78d",
    ),
    "procedure": (
        "psi4/driver/procrouting/proc.py",
        "98ac648d84cc4587ec034b9207d3c6fbc3cd74df4c0409a85478e5467c0dd408",
    ),
    "driver": (
        "psi4/driver/driver.py",
        "7d2485decb726bf62f18ca5f6c624b6dbc36d540dc9fbe2187a232189be13db6",
    ),
    "routing": (
        "psi4/driver/procrouting/proc_table.py",
        "995fb0b19407cbc17d29f3c10052f5fe2beeef331eb097250c34ddedcb9cbe73",
    ),
    "hf-definition": (
        "psi4/driver/procrouting/dft/hyb_functionals.py",
        "9f675874fa289d39f2542c34c7f7ccd659e97f5cbdf63fd53cbde493f0b1d22c",
    ),
    "gga-definition": (
        "psi4/driver/procrouting/dft/gga_functionals.py",
        "035704c9d548a89709611e3f825e38a6e1d550317b6a7c1650c10f9e12d301e7",
    ),
    "hybrid-definition": (
        "psi4/driver/procrouting/dft/libxc_functionals.py",
        "d3e5f17f1e19788ecc21c1a8e3967c4fd77f5b6ec510b4f61d60b4033c5c5726",
    ),
    "options": (
        "psi4/src/read_options.cc",
        "4c90f0223e9a0203b8dc626ec0976ccb27dbd555d0f2f7c2d5070d590c26f093",
    ),
    "manual": (
        "doc/sphinxman/source/tdscf.rst",
        "c4f4bef8e0421d3fa72b7fc941e0d886f25baf4ebfe611a34ae07a4870b5d1ee",
    ),
}


def tdscf_catalog() -> CapabilityCatalog:
    """Return independently sourced HF/PBE/B3LYP response construction rules.

    These entries describe scientific/input relationships across releases. Their
    source revision is provenance; no binary or dependency audit is required.
    Basis dimensions and orbital coverage can be supplied by another contribution.
    """
    evidence = tuple(
        Evidence(
            id="source-tdscf-" + name,
            source=_SOURCE + path,
            kind="source",
            digest=digest,
        )
        for name, (path, digest) in _FILES.items()
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
