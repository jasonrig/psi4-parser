"""Describe named driver products without retrieving or accepting their values."""

from psi4_parser.formal.science import ElectronicTarget, ProductName, QuantityType


def product_identity(
    calculation: str,
    name: ProductName,
    target: ElectronicTarget | None = None,
) -> tuple[str, ProductName, str]:
    """Return a product's producer, name, and symmetry/root identity.

    Spin qualifiers are validated separately. Specifying an allowed multiplicity
    for the same native root does not create a different quantity.
    """
    return (
        calculation,
        name,
        f"{target.symmetry or ''}/{target.root}" if target else "",
    )


THERMAL_PRODUCTS: frozenset[ProductName] = frozenset(
    {
        "zero_point_energy",
        "thermal_energy_correction",
        "enthalpy_correction",
        "gibbs_correction",
        "zero_k_enthalpy",
        "thermal_energy",
        "enthalpy",
        "gibbs_free_energy",
    }
)
"""Native full-frequency thermochemistry products needing explicit conditions."""

PROPERTY_NAMES: dict[ProductName, str] = {
    "dipole": "DIPOLE",
    "quadrupole": "QUADRUPOLE",
    "mulliken_charges": "MULLIKEN_CHARGES",
    "lowdin_charges": "LOWDIN_CHARGES",
    "mayer_indices": "MAYER_INDICES",
    "wiberg_lowdin_indices": "WIBERG_LOWDIN_INDICES",
}
"""Explicit properties-driver requests required for the corresponding product."""

SAPT_VARIABLES: dict[ProductName, str] = {
    "sapt_total_energy": "SAPT TOTAL ENERGY",
    "sapt_electrostatics": "SAPT ELST ENERGY",
    "sapt_exchange": "SAPT EXCH ENERGY",
    "sapt_induction": "SAPT IND ENERGY",
    "sapt_dispersion": "SAPT DISP ENERGY",
}
"""Declarative native QCVariable bindings for separately collected SAPT products."""

SAPT_COMPONENTS: tuple[ProductName, ...] = (
    "sapt_electrostatics",
    "sapt_exchange",
    "sapt_induction",
    "sapt_dispersion",
)
"""Native component partition whose sum defines the SAPT interaction return."""

TDSCF_PRODUCTS: frozenset[ProductName] = frozenset(
    {
        "excitation_energy",
        "excited_state_energy",
        "oscillator_strength_length",
        "oscillator_strength_velocity",
        "electric_transition_dipole_length",
    }
)
"""Explicit per-root products of a declared TD-SCF response operation."""

PRIMARY_SCALAR_PRODUCTS: frozenset[ProductName] = frozenset(
    {"electronic_energy", "sapt_total_energy"}
)
"""Named scalar products supplied by their corresponding primary driver return."""

THERMAL_TOTALS: dict[ProductName, ProductName] = {
    "zero_k_enthalpy": "zero_point_energy",
    "thermal_energy": "thermal_energy_correction",
    "enthalpy": "enthalpy_correction",
    "gibbs_free_energy": "gibbs_correction",
}
"""Total energies equal electronic energy plus their corresponding correction."""

THERMAL_REACTIONS: dict[str, ProductName] = {
    f"reaction_{name}": name for name in THERMAL_TOTALS
}
"""Closed thermal reaction meanings and their required molecular total meanings."""


def product_quantity(name: ProductName, *, frame: str | None = None) -> QuantityType:
    """Return a named product's canonical meaning, units, layout, and numeric domain.

    Args:
        name: Built-in product contract, independently gated by capability evidence.
        frame: Producing calculation frame identity; null for evidence templates.

    Returns:
        A canonical type. Frequencies include all 3N modes and may be complex;
        normal modes are normalized un-mass-weighted Cartesian columns. Quadrupoles
        use the six unique Cartesian components XX, XY, XZ, YY, YZ, ZZ in that order.
    """
    if name in TDSCF_PRODUCTS:
        return _response_quantity(name, frame)
    if name in {"gradient", "hessian"}:
        return QuantityType(
            meaning=name,
            unit="hartree/bohr" if name == "gradient" else "hartree/bohr^2",
            shape=("atoms", 3) if name == "gradient" else ("3*atoms", "3*atoms"),
            frame=frame,
        )
    if name in {"harmonic_frequencies", "normal_modes"}:
        return QuantityType(
            meaning=name,
            unit="cm^-1" if name == "harmonic_frequencies" else "bohr",
            shape=("3*atoms",)
            if name == "harmonic_frequencies"
            else ("3*atoms", "3*atoms"),
            number_kind="complex" if name == "harmonic_frequencies" else "real",
            frame=frame if name == "normal_modes" else None,
        )
    if name in {"dipole", "quadrupole"}:
        return QuantityType(
            meaning=name,
            unit="e*bohr" if name == "dipole" else "e*bohr^2",
            shape=(3,) if name == "dipole" else (6,),
            frame=frame,
        )
    if name in {
        "mulliken_charges",
        "lowdin_charges",
        "mayer_indices",
        "wiberg_lowdin_indices",
    }:
        charge = name in {"mulliken_charges", "lowdin_charges"}
        return QuantityType(
            meaning=name,
            unit="e" if charge else "1",
            shape=("atoms",) if charge else ("atoms", "atoms"),
        )
    return QuantityType(
        meaning="interaction_energy" if name == "sapt_total_energy" else name,
        unit="hartree",
    )


def _response_quantity(name: ProductName, frame: str | None) -> QuantityType:
    if name in {"oscillator_strength_length", "oscillator_strength_velocity"}:
        return QuantityType(meaning=name, unit="1")
    if name == "electric_transition_dipole_length":
        return QuantityType(meaning=name, unit="e*bohr", shape=(1, 3), frame=frame)
    return QuantityType(meaning=name, unit="hartree")
