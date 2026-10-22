"""Check response intent and root provenance without solving an electronic problem."""

from fractions import Fraction

from psi4_parser.builder import Molecule
from psi4_parser.formal.algebra import Form
from psi4_parser.formal.models import Calculation, Diagnostic, Plan, Product, Step
from psi4_parser.formal.products import TDSCF_PRODUCTS
from psi4_parser.formal.science import ExpectedQuantity, NativeVariableBinding

_IRREPS = {"c1": 1, "ci": 2, "cs": 2, "c2": 2, "d2": 4, "c2v": 4, "c2h": 4, "d2h": 8}
_TOTAL_TERMS = 2


def tdscf_issues(
    step: Calculation, molecule: Molecule, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    """Return located missing intent or incompatible response-operation choices."""
    analysis = step.model.tdscf
    is_td = step.model.method.strip().casefold().startswith("td-")
    if analysis is None:
        return (
            (
                Diagnostic(
                    path=(*path, "model", "tdscf"),
                    code="tdscf_context",
                    message="Declare TD-SCF roots, spin sector, and equations.",
                ),
            )
            if is_td
            else ()
        )
    checks = (
        (is_td, "tdscf_method", "Use a td- prefixed method for a TD-SCF response."),
        (
            step.driver == "energy" and step.sapt is None and step.analysis is None,
            "tdscf_driver",
            "TD-SCF construction requires an ordinary energy call.",
        ),
        (
            step.model.reference in {"rhf", "uhf"},
            "tdscf_reference",
            "The TD-SCF contract covers RHF and UHF references.",
        ),
        (
            (analysis.spin == "unrestricted") == (step.model.reference == "uhf"),
            "tdscf_spin",
            "Use unrestricted response for UHF and singlet/triplet sectors for RHF.",
        ),
        (
            not step.model.frozen_core,
            "tdscf_core",
            "TD-SCF response includes all occupied reference orbitals; "
            "frozen-core response is not established.",
        ),
        (
            analysis.spin not in {"triplet", "both"}
            or step.model.method.strip().casefold() in {"td-hf", "td-scf"},
            "tdscf_triplet_kernel",
            "The restricted triplet response contract covers Hartree-Fock kernels.",
        ),
    )
    issues = [
        Diagnostic(path=(*path, "model", "tdscf"), code=code, message=message)
        for valid, code, message in checks
        if not valid
    ]
    if not isinstance(analysis.states, int):
        group = (molecule.symmetry or "").casefold().split("_", 1)[0]
        count = _IRREPS.get(group)
        if count is None or count != len(analysis.states):
            issues.append(
                Diagnostic(
                    path=(*path, "model", "tdscf", "states"),
                    code="tdscf_irreps",
                    status="unknown" if count is None else "violated",
                    message="Per-irrep roots require an explicit computational "
                    "point group and one count per native irrep.",
                )
            )
    return tuple(issues)


def tdscf_capacity_issues(
    step: Calculation, orbitals: int, alpha: int, beta: int, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    """Return requests exceeding the complete occupied-virtual response space."""
    analysis = step.model.tdscf
    if analysis is None:
        return ()
    capacity = alpha * (orbitals - alpha)
    if step.model.reference == "uhf":
        capacity += beta * (orbitals - beta)
    if max(analysis.sector_counts) <= max(0, capacity):
        return ()
    return (
        Diagnostic(
            path=(*path, "tdscf", "states"),
            code="tdscf_root_capacity",
            message=f"Each response sector has at most {max(0, capacity)} "
            "occupied-virtual roots in the declared basis.",
        ),
    )


def tdscf_product_issues(
    step: Product, calculation: Calculation, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    """Return root membership and spin findings for an expected response product."""
    target = step.electronic_target
    if step.name not in TDSCF_PRODUCTS:
        return (
            (
                Diagnostic(
                    path=(*path, "electronic_target"),
                    code="product_target",
                    message="Root selectors apply only to excited-state products.",
                ),
            )
            if target is not None
            else ()
        )
    analysis = calculation.model.tdscf
    if target is None or analysis is None:
        return (
            Diagnostic(
                path=(*path, "electronic_target"),
                code="tdscf_product_context",
                message="Declare an explicit root and a TD-SCF product producer.",
            ),
        )
    issues: list[Diagnostic] = []
    if target.root > analysis.state_count:
        issues.append(
            Diagnostic(
                path=(*path, "electronic_target", "root"),
                code="tdscf_product_root",
                message="The selected root exceeds the producer's requested root set.",
            )
        )
    if target.symmetry is not None:
        issues.append(
            Diagnostic(
                path=(*path, "electronic_target", "symmetry"),
                code="tdscf_product_symmetry",
                status="unsupported",
                message="Select global energy order within the requested set; "
                "symmetry-resolved selection needs a separate contract.",
            )
        )
    multiplicity = {"singlet": 1, "triplet": 3}.get(analysis.spin)
    if target.multiplicity is not None and target.multiplicity != multiplicity:
        issues.append(
            Diagnostic(
                path=(*path, "electronic_target", "multiplicity"),
                code="tdscf_product_spin",
                message="A claimed spin must follow a single restricted spin sector. "
                "Mixed or unrestricted roots have no guaranteed multiplicity.",
            )
        )
    return tuple(issues)


def tdscf_variable_binding(
    step: Product, calculation: Calculation
) -> NativeVariableBinding | None:
    """Return a transient native binding, or null for an unrelated product."""
    target = step.electronic_target
    if step.name not in TDSCF_PRODUCTS or target is None:
        return None
    namespace = (
        "HF"
        if calculation.model.method.strip().casefold() in {"td-hf", "td-scf"}
        else "DFT"
    )
    suffixes = {
        "excitation_energy": "EXCITATION ENERGY",
        "oscillator_strength_length": "OSCILLATOR STRENGTH (LEN)",
        "oscillator_strength_velocity": "OSCILLATOR STRENGTH (VEL)",
        "electric_transition_dipole_length": "ELECTRIC TRANSITION DIPOLE MOMENT (LEN)",
    }
    key = (
        f"TD-{namespace} ROOT {target.root} TOTAL ENERGY"
        if step.name == "excited_state_energy"
        else f"TD-{namespace} ROOT 0 -> ROOT {target.root} {suffixes[step.name]}"
    )
    return NativeVariableBinding(
        producer=calculation.id,
        quantity=step.id,
        key=key,
        unit="1"
        if step.name.startswith("oscillator_strength")
        else "e*bohr"
        if step.name == "electric_transition_dipole_length"
        else "hartree",
        storage="array"
        if step.name == "electric_transition_dipole_length"
        else "scalar",
    )


def excited_total_issues(
    steps: dict[str, Step],
    form: Form,
    quantities: dict[str, ExpectedQuantity],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    """Return invalid total aliases or reference-plus-excitation formulas."""
    leaves = [(steps[name], weight) for name, weight in form.items()]
    if len(leaves) == 1:
        source, weight = leaves[0]
        if (
            isinstance(source, Product)
            and source.name == "excited_state_energy"
            and weight == 1
        ):
            return ()
    references = [
        source
        for source, weight in leaves
        if isinstance(source, Calculation)
        and source.model.tdscf is not None
        and weight == 1
    ]
    gaps = [
        source
        for source, weight in leaves
        if isinstance(source, Product)
        and source.name == "excitation_energy"
        and weight == Fraction(1)
    ]
    if (
        len(leaves) == _TOTAL_TERMS
        and len(references) == len(gaps) == 1
        and gaps[0].calculation == references[0].id
        and quantities[gaps[0].id].electronic_target is not None
    ):
        return ()
    return (
        Diagnostic(
            path=path,
            code="excited_total_formula",
            message="An excited-state total is one TD-SCF reference plus one "
            "excitation from the same producer, or a native total alias.",
        ),
    )


def tdscf_assumptions(plan: Plan) -> tuple[str, ...]:
    """Return physical and symmetry-space assumptions for response construction."""
    if not any(
        isinstance(step, Calculation) and step.model.tdscf is not None
        for step in plan.steps
    ):
        return ()
    return (
        "TD-SCF roots are energy-ordered within the requested spin/irrep allocation, "
        "without physical state tracking. Irrep-specific occupied/virtual spaces "
        "and a suitable reference are assumed; RPA also assumes the required "
        "stability. Numerical convergence and physical accuracy remain separate.",
    )
