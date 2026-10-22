"""Check named products against their producing operation and declared context."""

from psi4_parser.builder import Molecule
from psi4_parser.formal.excited_contracts import (
    tdscf_product_issues,
    tdscf_variable_binding,
)
from psi4_parser.formal.models import Calculation, Diagnostic, Plan, Product
from psi4_parser.formal.products import (
    PROPERTY_NAMES,
    SAPT_VARIABLES,
    TDSCF_PRODUCTS,
    THERMAL_PRODUCTS,
    product_quantity,
)
from psi4_parser.formal.science import (
    ExpectedQuantity,
    NativeProductBinding,
    NativeProductOutput,
    NativeVariableBinding,
    ProductName,
)


def native_product_outputs(plan: Plan) -> tuple[NativeProductOutput, ...]:
    """Declare native frequency records with one writer label per producing call.

    Returns:
        Unique filename templates and native member bindings for requested products.
    """
    keys = {
        "electronic_energy": "E0",
        "hessian": "hessian",
        "harmonic_frequencies": "omega",
        "normal_modes": "x",
        "zero_point_energy": "ZPE_corr",
        "thermal_energy_correction": "E_corr",
        "enthalpy_correction": "H_corr",
        "gibbs_correction": "G_corr",
        "zero_k_enthalpy": "ZPE_tot",
        "thermal_energy": "E_tot",
        "enthalpy": "H_tot",
        "gibbs_free_energy": "G_tot",
    }
    products: dict[str, list[NativeProductBinding]] = {}
    for step in plan.steps:
        if isinstance(step, Product) and step.name in keys:
            products.setdefault(step.calculation, []).append(
                NativeProductBinding(
                    quantity=step.id,
                    key=keys[step.name],
                    encoding="raw_array"
                    if step.name == "hessian"
                    else "qcelemental_datum_json",
                )
            )
    return tuple(
        NativeProductOutput(
            producer=step.id,
            label=f"formal_{index}",
            filename_template=f"formal_{index}.{{pid}}.vibrec",
            bindings=tuple(products[step.id]),
        )
        for index, step in enumerate(plan.steps)
        if isinstance(step, Calculation)
        and step.driver == "frequency"
        and step.id in products
    )


def native_variable_bindings(plan: Plan) -> tuple[NativeVariableBinding, ...]:
    """Declare native product locations without reading or preserving values.

    Returns:
        Transient scalar or array bindings for a separate execution/result consumer.
    """
    sapt = tuple(
        NativeVariableBinding(
            producer=step.calculation,
            quantity=step.id,
            key=SAPT_VARIABLES[step.name],
            unit="hartree",
        )
        for step in plan.steps
        if isinstance(step, Product) and step.name in SAPT_VARIABLES
    )
    calculations = {
        step.id: step for step in plan.steps if isinstance(step, Calculation)
    }
    response = tuple(
        binding
        for step in plan.steps
        if isinstance(step, Product)
        and (binding := tdscf_variable_binding(step, calculations[step.calculation]))
        is not None
    )
    return sapt + response


def _product_driver(
    name: ProductName, calculation: Calculation, primary: ExpectedQuantity
) -> bool:
    if name in TDSCF_PRODUCTS or name in SAPT_VARIABLES:
        declared = (
            calculation.model.tdscf is not None
            if name in TDSCF_PRODUCTS
            else calculation.sapt is not None
        )
        return calculation.driver == "energy" and declared
    required = PROPERTY_NAMES.get(name)
    if required is not None:
        return calculation.driver == "properties" and required.casefold() in {
            item.casefold() for item in calculation.properties
        }
    if name in THERMAL_PRODUCTS or name in {"harmonic_frequencies", "normal_modes"}:
        return calculation.driver == "frequency"
    if name == "hessian":
        return calculation.driver in {"hessian", "frequency"}
    if name == "gradient":
        return calculation.driver == "gradient"
    return (
        calculation.driver not in {"gradient", "hessian"}
        and primary.quantity.meaning == "electronic_energy"
    )


def inspect_product(
    step: Product,
    calculation: Calculation,
    primary: ExpectedQuantity,
    molecule: Molecule,
    path: tuple[str | int, ...],
) -> tuple[ExpectedQuantity, tuple[Diagnostic, ...]]:
    """Trace a named product to its operation and declared context.

    Returns:
        Canonical expected quantity and located driver, type, or context findings.
    """
    canonical = product_quantity(step.name, frame=calculation.id)
    quantity = ExpectedQuantity(
        id=step.id,
        producer=calculation.id,
        quantity=canonical,
        system=primary.system,
        geometry=primary.geometry,
        model=calculation.model,
        state=primary.state,
        product=step.name,
        electronic_target=step.electronic_target,
        analysis=calculation.analysis
        if step.name in THERMAL_PRODUCTS | {"harmonic_frequencies", "normal_modes"}
        else None,
        sapt=calculation.sapt if step.name in SAPT_VARIABLES else None,
    )
    issues: list[Diagnostic] = list(tdscf_product_issues(step, calculation, path))
    if calculation.driver == "frequency" and any(
        (item.name.casefold() == "writer_file_label" and not item.module)
        or (item.name.casefold() == "hessian_write" and item.key[0] in {"", "findif"})
        for item in calculation.model.settings
    ):
        issues.append(
            Diagnostic(
                path=path,
                code="product_output_settings",
                message="Named frequency products reserve writer labels "
                "and HESSIAN_WRITE; remove conflicting model settings.",
            )
        )
    if step.quantity is not None and step.quantity != canonical:
        issues.append(
            Diagnostic(
                path=(*path, "quantity"),
                code="product_quantity",
                status="violated",
                message="Product type must match canonical units, layout, "
                "numeric domain, and producing calculation frame.",
            )
        )
    if not _product_driver(step.name, calculation, primary):
        issues.append(
            Diagnostic(
                path=(*path, "calculation"),
                code="product_driver",
                status="unsupported",
                message=f"Product {step.name} needs a compatible "
                "explicitly requested operation.",
            )
        )
    if step.name in THERMAL_PRODUCTS and calculation.analysis is None:
        issues.append(
            Diagnostic(
                path=path,
                code="product_thermal_context",
                status="unknown",
                message="Thermal products need explicit temperature, pressure, "
                "symmetry number, and projection settings on the frequency call.",
            )
        )
    if (
        step.name in THERMAL_PRODUCTS
        or step.name in {"harmonic_frequencies", "normal_modes"}
    ) and any(
        atom.nucleus.dummy or atom.nucleus.ghost != "none" for atom in molecule.atoms
    ):
        issues.append(
            Diagnostic(
                path=path,
                code="product_vibrational_centers",
                status="unsupported",
                message="Vibrational products currently need real atoms "
                "without dummy or ghost centers.",
            )
        )
    return quantity, tuple(issues)
