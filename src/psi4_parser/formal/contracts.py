"""Check reusable scientific operation contracts before encoding relationships."""

from dataclasses import dataclass

from pydantic import Field

from psi4_parser.builder import ElectronicState, Molecule
from psi4_parser.builder._model import evolve
from psi4_parser.builder.constraints import Bounded
from psi4_parser.formal._record import Record
from psi4_parser.formal.environment_contracts import environment_issues
from psi4_parser.formal.excited_contracts import tdscf_issues
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Diagnostic,
    Plan,
    Product,
    Subsystem,
)
from psi4_parser.formal.nuclei import Center, centers
from psi4_parser.formal.product_contracts import (
    inspect_product,
    native_product_outputs,
    native_variable_bindings,
)
from psi4_parser.formal.sapt_contracts import sapt_issues
from psi4_parser.formal.science import (
    Driver,
    ExpectedQuantity,
    GeometryArtifact,
    Model,
    NativeProductOutput,
    NativeVariableBinding,
    QuantityType,
    VibrationalAnalysis,
)
from psi4_parser.formal.semantics import expression_semantics

# Change this identity whenever the meaning or coverage of a built-in rule changes.
RULE_VERSION = "scientific-contracts/15"


class OperationContract(Record):
    """Discover an operation's prerequisites, effects, and expected products."""

    driver: Driver = Field(
        description="Application operation covered by this contract."
    )
    version: str = Field(
        default=RULE_VERSION, description="Version of the operation rules."
    )
    prerequisites: tuple[str, ...] = Field(
        description="Conditions checked before construction."
    )
    effects: tuple[str, ...] = Field(
        description="Declared changes to scientific state."
    )
    products: tuple[str, ...] = Field(
        description="Expected artifacts after successful execution."
    )


def operation_contracts(driver: Driver | None = None) -> tuple[OperationContract, ...]:
    """Return compact operation descriptions, optionally restricted to one driver."""
    drivers: tuple[Driver, ...] = (
        "energy",
        "optimize",
        "frequency",
        "gradient",
        "hessian",
        "properties",
    )
    return tuple(
        OperationContract(
            driver=item,
            prerequisites=(
                "resolved molecular identity and electronic state",
                "preceding geometry artifact",
                "explicit computational model",
                "capability evidence for scientific intent and specialized models",
                *(
                    (
                        "explicit SAPT partition, basis, induction, and high-spin "
                        "state when requested",
                        "explicit solvent equation, dielectric, cavity, and screening "
                        "choices when requested",
                        "explicit TD-SCF root allocation, spin sector, and "
                        "response equations when requested",
                    )
                    if item == "energy"
                    else ()
                ),
            ),
            effects=(
                "native options reset for the call and restored afterward",
                "native scratch namespace restored to the call's entry value",
                *(("new private geometry snapshot",) if item == "optimize" else ()),
            ),
            products=(
                ("electronic gradient",)
                if item == "gradient"
                else ("electronic Hessian",)
                if item == "hessian"
                else ("electronic energy", "future optimized geometry")
                if item == "optimize"
                else ("electronic energy", "vibrational analysis")
                if item == "frequency"
                else ("electronic energy", "requested properties")
                if item == "properties"
                else (
                    "method-defined scalar energy",
                    "declared SAPT components when requested",
                    "declared ordered response products when requested",
                )
            ),
        )
        for item in drivers
        if driver is None or item == driver
    )


def electronic_state_issues(
    sites: tuple[Center, ...],
    state: ElectronicState,
    model: Model,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    """Return violations of electron accounting and the reference's spin rules."""
    cores = {item.element: item.core_electrons for item in model.ecps}
    electrons = (
        sum(
            item.atomic_number - cores.get(item.element, 0)
            for item in sites
            if item.role == "real"
        )
        - state.charge
    )
    twice_spin = state.multiplicity - 1
    issues: list[Diagnostic] = []
    if any(cores.get(item.element, 0) > item.atomic_number for item in sites):
        issues.append(
            Diagnostic(
                path=path,
                code="ecp_core",
                status="violated",
                message="An ECP replaces more electrons than the atom contains.",
            )
        )
    if electrons < twice_spin or (electrons - twice_spin) % 2:
        issues.append(
            Diagnostic(
                path=path,
                code="electronic_state",
                status="violated",
                message=(
                    f"{electrons} explicit electrons cannot have "
                    f"multiplicity {state.multiplicity}."
                ),
            )
        )
    if model.reference == "rhf" and state.multiplicity != 1:
        issues.append(
            Diagnostic(
                path=path,
                code="reference_spin",
                status="violated",
                message="RHF requires a singlet electronic state.",
            )
        )
    return tuple(issues)


def spin_coupling_allows(multiplicities: tuple[int, ...], overall: int) -> bool:
    """Return whether fragment angular momenta can couple to an overall multiplicity.

    This checks spin addition only. Electron counts and electronic-state
    suitability require separate checks. Non-positive or empty inputs return false.
    """
    if not multiplicities or overall < 1 or any(value < 1 for value in multiplicities):
        return False
    spins = tuple(value - 1 for value in multiplicities)
    maximum = sum(spins)
    minimum = max(2 * max(spins) - maximum, maximum % 2)
    target = overall - 1
    return minimum <= target <= maximum and (target - maximum) % 2 == 0


def _fragment_issues(
    molecule: Molecule,
    sites: tuple[Center, ...],
    model: Model,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    if not molecule.fragments:
        return ()
    issues: list[Diagnostic] = []
    total_charge = 0
    multiplicities: list[int] = []
    for index, fragment in enumerate(molecule.fragments):
        location = (*path, "fragments", index, "state")
        if fragment.state is None:
            issues.append(
                Diagnostic(
                    path=location,
                    code="fragment_state",
                    status="unknown",
                    message="Supply fragment charge and multiplicity explicitly.",
                )
            )
            continue
        selected = tuple(site for site in sites if site.id in fragment.atom_ids)
        # Fragment spin bookkeeping is independent of the supermolecule reference.
        fragment_model = Model(
            method=model.method, basis=model.basis, reference="uhf", ecps=model.ecps
        )
        issues.extend(
            electronic_state_issues(selected, fragment.state, fragment_model, location)
        )
        total_charge += fragment.state.charge
        multiplicities.append(fragment.state.multiplicity)
    if any(fragment.state is None for fragment in molecule.fragments):
        return tuple(issues)
    if molecule.state is not None and (
        molecule.state.charge != total_charge
        or not spin_coupling_allows(tuple(multiplicities), molecule.state.multiplicity)
    ):
        issues.append(
            Diagnostic(
                path=(*path, "state"),
                code="fragment_coupling",
                status="violated",
                message="Overall charge or spin is incompatible with fragment states.",
            )
        )
    return tuple(issues)


def primary_quantity(step: Calculation) -> QuantityType:
    """Return the primary product, retaining an explicitly chosen scalar meaning."""
    if step.driver == "gradient":
        return QuantityType(
            meaning="gradient",
            unit="hartree/bohr",
            shape=("atoms", 3),
            frame=step.geometry,
        )
    if step.driver == "hessian":
        return QuantityType(
            meaning="hessian",
            unit="hartree/bohr^2",
            shape=("3*atoms", "3*atoms"),
            frame=step.geometry,
        )
    if step.sapt is not None:
        return QuantityType(meaning="interaction_energy", unit="hartree")
    if step.model.tdscf is not None:
        return QuantityType(meaning="electronic_energy", unit="hartree")
    if step.quantity is not None:
        return step.quantity
    return QuantityType(meaning="electronic_energy", unit="hartree")


def _quantity_issues(
    step: Calculation, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    if step.quantity is None:
        return ()
    actual = primary_quantity(step)
    if (
        step.driver in {"gradient", "hessian"}
        or step.sapt is not None
        or step.model.tdscf is not None
    ):
        valid = step.quantity == actual
    else:
        valid = (
            not step.quantity.shape
            and step.quantity.unit == "hartree"
            and step.quantity.frame is None
            and step.quantity.number_kind == "real"
        )
    if valid:
        return ()
    return (
        Diagnostic(
            path=(*path, "quantity"),
            code="quantity_type",
            message="Primary quantity is incompatible with the driver's return type.",
        ),
    )


def _driver_argument_issues(
    step: Calculation, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    issues: list[Diagnostic] = []
    if step.derivative_route != "automatic" and step.driver in {"energy", "properties"}:
        issues.append(
            Diagnostic(
                path=(*path, "derivative_route"),
                code="derivative_driver",
                message="This driver does not accept an explicit derivative route.",
            )
        )
    if bool(step.properties) != (step.driver == "properties"):
        issues.append(
            Diagnostic(
                path=(*path, "properties"),
                code="property_driver",
                message="List explicit properties when using the properties driver.",
            )
        )
    return (*issues, *_analysis_issues(step, path))


def _analysis_issues(
    step: Calculation, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    if step.analysis is None:
        return ()
    issues: list[Diagnostic] = []
    if step.driver != "frequency":
        issues.append(
            Diagnostic(
                path=(*path, "analysis"),
                code="analysis_driver",
                message="Explicit vibrational/thermal analysis requires "
                "the full frequency driver.",
            )
        )
    if any(
        item.name.casefold() in {"t", "p", "rotational_symmetry_number"}
        and item.key[0] in {"", "thermo"}
        for item in step.model.settings
    ):
        issues.append(
            Diagnostic(
                path=(*path, "model", "settings"),
                code="analysis_settings",
                message="Use analysis for thermal conditions and symmetry; "
                "do not override them in model settings.",
            )
        )
    return tuple(issues)


def _constraint_issues(
    step: Calculation,
    molecule: Molecule,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    issues: list[Diagnostic] = []
    ids = {item.id for item in molecule.atoms if not item.nucleus.dummy}
    if step.constraints and step.driver != "optimize":
        issues.append(
            Diagnostic(
                path=(*path, "constraints"),
                code="constraint_driver",
                message="Optimization constraints require the optimize driver.",
            )
        )
    for index, constraint in enumerate(step.constraints):
        location = (*path, "constraints", index)
        if not set(constraint.coordinate.atoms) <= ids:
            issues.append(
                Diagnostic(
                    path=location,
                    code="constraint_atoms",
                    message="Constraint atoms must be known, non-dummy centers.",
                )
            )
        if (
            isinstance(constraint, Bounded)
            and constraint.coordinate.kind == "cartesian"
            and not (molecule.fixed_com and molecule.fixed_orientation)
        ):
            issues.append(
                Diagnostic(
                    path=location,
                    code="constraint_frame",
                    message="Cartesian bounds require a fixed molecular frame.",
                )
            )
    return tuple(issues)


def _backend_issues(
    step: Calculation, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    pending = (
        ("electronic_target", step.model.electronic_target is not None),
        ("basis_assignments", bool(step.model.basis_assignments)),
    )
    return tuple(
        Diagnostic(
            path=(*path, "model", name),
            code="backend_coverage",
            status="unsupported",
            message=f"The Psi4 formal backend has no checked lowering for {name}.",
        )
        for name, present in pending
        if present
    )


@dataclass(frozen=True)
class Inspection:
    """Collect contract findings and expected artifacts without executing a plan.

    Attributes:
        diagnostics: Located prerequisites or coverage failures.
        geometries: Known and future geometry artifacts, in dependency order.
        quantities: Expected primary products of calculation steps.
        contexts: Molecular metadata; future coordinates are placeholders.
        native_outputs: Expected native files for separately consumed products.
        native_variables: Transient native products declared for an external consumer.
    """

    diagnostics: tuple[Diagnostic, ...]
    geometries: tuple[GeometryArtifact, ...]
    quantities: tuple[ExpectedQuantity, ...]
    contexts: dict[str, Molecule]
    native_outputs: tuple[NativeProductOutput, ...]
    native_variables: tuple[NativeVariableBinding, ...]


def _subsystem_context(
    source: Molecule,
    step: Subsystem,
    path: tuple[str | int, ...],
) -> tuple[Molecule, tuple[Diagnostic, ...]]:
    issues: list[Diagnostic] = []
    names = {item.name for item in source.fragments}
    chosen = set(step.real_fragments)
    if not chosen <= names or len(chosen) != len(step.real_fragments):
        issues.append(
            Diagnostic(
                path=(*path, "real_fragments"),
                code="subsystem_fragments",
                message="Select distinct, named parent fragments.",
            )
        )
    if not source.fixed_com or not source.fixed_orientation:
        issues.append(
            Diagnostic(
                path=(*path, "geometry"),
                code="subsystem_frame",
                message="Full-basis subsystems require a fixed parent frame.",
            )
        )
    real_ids = {
        atom_id
        for fragment in source.fragments
        if fragment.name in chosen
        for atom_id in fragment.atom_ids
    }
    if any(
        atom.nucleus.ghost != "none" for atom in source.atoms if atom.id in real_ids
    ):
        issues.append(
            Diagnostic(
                path=(*path, "real_fragments"),
                code="subsystem_ghost",
                message="An explicit ghost center cannot become a real nucleus.",
            )
        )
    atoms = tuple(
        atom
        if atom.id in real_ids
        else evolve(atom, nucleus=evolve(atom.nucleus, ghost="at"))
        for atom in source.atoms
    )
    fragments = tuple(
        fragment
        if fragment.name in chosen
        else evolve(fragment, state=ElectronicState(charge=0, multiplicity=1))
        for fragment in source.fragments
    )
    context = evolve(source, atoms=atoms, fragments=fragments, state=step.state)
    return context, tuple(issues)


def _common_analysis(products: list[ExpectedQuantity]) -> VibrationalAnalysis | None:
    analyses = {
        item.analysis.model_dump_json(): item.analysis
        for item in products
        if item.analysis is not None
    }
    return next(iter(analyses.values())) if len(analyses) == 1 else None


def _expression_quantity(
    step: Combination,
    quantities: dict[str, ExpectedQuantity],
    path: tuple[str | int, ...],
) -> tuple[ExpectedQuantity, tuple[Diagnostic, ...]]:
    terms = [quantities[term.result] for term in step.terms]
    quantity = step.quantity or terms[0].quantity
    checks = (
        (
            not any(item.quantity.shape for item in terms),
            "scalar_expression",
            "Scalar expressions cannot consume tensor quantities.",
        ),
        (
            len({item.quantity.unit for item in terms}) == 1,
            "expression_unit",
            "Expression terms must use the same explicit unit.",
        ),
        (
            not quantity.shape
            and all(
                item.quantity.unit == quantity.unit
                and item.quantity.number_kind == quantity.number_kind
                for item in terms
            ),
            "expression_type",
            "A scalar expression must preserve the terms' unit and numeric domain.",
        ),
    )
    issues = tuple(
        Diagnostic(path=(*path, "quantity"), code=code, message=message)
        for valid, code, message in checks
        if not valid
    )
    return ExpectedQuantity(
        id=step.id,
        producer=step.id,
        quantity=quantity,
        operands=tuple(term.result for term in step.terms),
        analysis=_common_analysis(terms),
    ), issues


def inspect_contracts(plan: Plan) -> Inspection:
    """Return operation findings and expected artifact provenance.

    The caller must establish reference order and resolved coordinates first.
    """
    issues: list[Diagnostic] = []
    contexts = {item.name: item.geometry for item in plan.molecules}
    geometries = {
        item.name: GeometryArtifact(
            id=item.name,
            system=item.name,
            coordinates_known=True,
            atom_ids=tuple(atom.id for atom in item.geometry.atoms),
            frame=item.name,
        )
        for item in plan.molecules
    }
    quantities: dict[str, ExpectedQuantity] = {}
    calculations = {
        step.id: step for step in plan.steps if isinstance(step, Calculation)
    }
    for index, step in enumerate(plan.steps):
        path: tuple[str | int, ...] = ("steps", index)
        if isinstance(step, Subsystem):
            parent = geometries[step.geometry]
            context, findings = _subsystem_context(contexts[step.geometry], step, path)
            contexts[step.id] = context
            issues.extend(findings)
            geometries[step.id] = GeometryArtifact(
                id=step.id,
                system=step.id,
                source=parent.id,
                producer=step.id,
                coordinates_known=parent.coordinates_known,
                atom_ids=parent.atom_ids,
                frame=parent.frame,
            )
            continue
        if isinstance(step, Product):
            source_calculation = calculations[step.calculation]
            produced_quantity, findings = inspect_product(
                step,
                source_calculation,
                quantities[step.calculation],
                contexts[source_calculation.geometry],
                path,
            )
            quantities[step.id] = produced_quantity
            issues.extend(findings)
            continue
        if isinstance(step, Combination):
            produced_quantity, findings = _expression_quantity(step, quantities, path)
            quantities[step.id] = produced_quantity
            issues.extend(findings)
            continue
        source = geometries[step.geometry]
        molecule = contexts[step.geometry]
        try:
            sites = centers(molecule)
        except ValueError as error:
            issues.append(Diagnostic(path=path, code="nucleus", message=str(error)))
            sites = ()
        if molecule.state is not None and sites:
            issues.extend(
                electronic_state_issues(
                    sites, molecule.state, step.model, (*path, "model", "reference")
                )
            )
        issues.extend(
            _fragment_issues(molecule, sites, step.model, ("molecules", source.system))
        )
        issues.extend(_constraint_issues(step, molecule, path))
        issues.extend(_quantity_issues(step, path))
        issues.extend(_driver_argument_issues(step, path))
        issues.extend(_backend_issues(step, path))
        issues.extend(environment_issues(step, molecule, path))
        issues.extend(sapt_issues(step, molecule, path))
        issues.extend(tdscf_issues(step, molecule, path))
        quantities[step.id] = ExpectedQuantity(
            id=step.id,
            producer=step.id,
            quantity=primary_quantity(step),
            system=source.system,
            geometry=step.id if step.driver == "optimize" else source.id,
            model=step.model,
            state=molecule.state,
            sapt=step.sapt,
        )
        if step.driver == "optimize":
            contexts[step.id] = molecule
            geometries[step.id] = GeometryArtifact(
                id=step.id,
                system=source.system,
                source=source.id,
                producer=step.id,
                coordinates_known=False,
                atom_ids=source.atom_ids,
                frame=source.frame,
            )
    issues.extend(expression_semantics(plan, contexts, quantities))
    return Inspection(
        tuple(issues),
        tuple(geometries.values()),
        tuple(quantities.values()),
        contexts,
        native_product_outputs(plan),
        native_variable_bindings(plan),
    )
