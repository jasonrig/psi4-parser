"""Consume scientific/input contracts without probing or launching an engine."""

import json
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from psi4_parser.builder import Molecule
from psi4_parser.formal._record import Record
from psi4_parser.formal.algebra import expression_forms
from psi4_parser.formal.contracts import Inspection, primary_quantity
from psi4_parser.formal.excited_contracts import tdscf_capacity_issues
from psi4_parser.formal.extrapolation_models import BasisSequence
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Diagnostic,
    Plan,
    Product,
)
from psi4_parser.formal.nuclei import Center, centers
from psi4_parser.formal.products import product_quantity
from psi4_parser.formal.science import (
    ECP,
    Driver,
    ProductName,
    QuantityType,
    Setting,
    SettingValue,
    _normalize_option_module,
)

type Support = Literal["supported", "unsupported", "unknown"]
type Reference = Literal["rhf", "uhf", "rohf"]
type DerivativeRoute = Literal["automatic", "analytic", "finite_difference"]


def _literal(value: SettingValue, *, case_sensitive: bool) -> str:
    if not case_sensitive:
        if isinstance(value, str):
            value = value.casefold()
        elif isinstance(value, tuple):
            value = tuple(
                item.casefold() if isinstance(item, str) else item for item in value
            )
    return json.dumps(value)


class Evidence(Record):
    """Identify a source that supports an application capability assertion."""

    id: str = Field(
        min_length=1, description="Unique evidence identity within the catalog."
    )
    source: str = Field(
        min_length=1,
        description="Documentation URL, source path, or saved probe reference.",
    )
    kind: Literal["documentation", "source", "probe", "declaration"] = Field(
        description="Origin of this evidence; declarations remain explicit assumptions."
    )


class OptionCondition(Record):
    """Limit capability evidence to explicitly declared option values.

    An unmatched condition leaves support unknown. It does not assert that an
    unexamined algorithm is unsupported by the application.
    """

    name: str = Field(
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$", description="Application option name."
    )
    module: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
        description="Option module; GLOBAL and GLOBALS normalize to null for global.",
    )
    values: tuple[SettingValue, ...] = Field(
        min_length=1, description="Exact literal values covered by this evidence."
    )
    case_sensitive: bool = Field(
        default=True, description="Compare string literals with case retained."
    )

    @field_validator("module")
    @classmethod
    def _normalize_module(cls, value: str | None) -> str | None:
        return _normalize_option_module(value)

    @property
    def key(self) -> tuple[str, str]:
        """Return the normalized module/name identity, retaining global/local scope."""
        return ((self.module or "").casefold(), self.name.casefold())

    def accepts(self, value: SettingValue) -> bool:
        """Return whether a typed literal satisfies this evidence condition."""
        return any(
            _literal(value, case_sensitive=self.case_sensitive)
            == _literal(item, case_sensitive=self.case_sensitive)
            for item in self.values
        )


class ComponentCapability(Record):
    """Record availability of an optional application or Python component."""

    name: str = Field(min_length=1, description="Component identity, such as optking.")
    status: Support = Field(
        description="Supported, unsupported, or unknown availability."
    )
    evidence: tuple[str, ...] = Field(
        min_length=1, description="Evidence IDs for this component fact."
    )

    @property
    def key(self) -> str:
        """Return the normalized component name."""
        return self.name.strip().casefold()


class ProductCapability(Record):
    """Record a named product's actual type for one method/driver evidence case."""

    name: ProductName = Field(
        description="Named product whose availability is covered."
    )
    status: Support = Field(
        description="Supported, unsupported, or unknown product availability."
    )
    quantity: QuantityType = Field(
        description="Documented product type; the producing call supplies its frame."
    )
    evidence: tuple[str, ...] = Field(
        min_length=1, description="Evidence IDs supporting this product fact."
    )


class MethodCapability(Record):
    """Declare support for one method, driver, reference, and derivative route.

    Each entry is an explicit combination. Missing combinations remain unknown.
    Feature and option lists name the additional choices covered by this entry.
    """

    method: str = Field(
        min_length=1, description="Exact method name; aliases need their own entries."
    )
    driver: Driver = Field(description="Driver covered by this evidence.")
    reference: Reference = Field(description="SCF reference covered by this evidence.")
    derivative_route: DerivativeRoute = Field(
        default="automatic", description="Derivative route covered by this entry."
    )
    status: Support = Field(
        description="Supported, explicitly unsupported, or still unknown."
    )
    quantity: QuantityType = Field(
        description="Primary product type; the consumed geometry supplies its frame."
    )
    features: tuple[str, ...] = Field(
        default=(),
        description="Covered features, such as ghost_centers, ecp, or constraints.",
    )
    options: tuple[str, ...] = Field(
        default=(),
        description="Covered option keys, written as name or module.name.",
    )
    bases: tuple[str, ...] = Field(
        default=(),
        description="Permitted orbital bases; empty uses separate basis coverage.",
    )
    conditions: tuple[OptionCondition, ...] = Field(
        default=(),
        description="Explicit option values required for this evidence to apply.",
    )
    components: tuple[str, ...] = Field(
        default=(),
        description="Descriptive component names; availability is not checked.",
    )
    products: tuple[ProductCapability, ...] = Field(
        default=(),
        description="Named product cases; absent products remain unknown.",
    )
    evidence: tuple[str, ...] = Field(
        min_length=1, description="Evidence IDs supporting this combination."
    )

    @property
    def key(self) -> tuple[str, Driver, Reference, DerivativeRoute]:
        """Return the normalized exact combination identity."""
        return (
            self.method.strip().casefold(),
            self.driver,
            self.reference,
            self.derivative_route,
        )

    @model_validator(mode="after")
    def check_conditions(self) -> Self:
        """Return a method with unambiguous evidence conditions and dependencies.

        Raises:
            ValueError: Condition keys or normalized component dependencies repeat.
        """
        if len({item.key for item in self.conditions}) != len(self.conditions):
            raise ValueError(
                "Method option conditions must have unique module/name keys"
            )
        dependencies = {name.strip().casefold() for name in self.components}
        if "" in dependencies or len(dependencies) != len(self.components):
            raise ValueError(
                "Method component dependencies must be nonempty and unique"
            )
        if len({item.name for item in self.products}) != len(self.products):
            raise ValueError("Method named product cases must be unique")
        return self


class BasisFunctions(Record):
    """Count an element's functions in the two supported angular representations."""

    element: str = Field(
        pattern=r"^[A-Z][a-z]?$",
        description="Element symbol covered by these function counts.",
    )
    spherical: int = Field(
        ge=1, description="Number of orbital functions using pure spherical harmonics."
    )
    cartesian: int = Field(
        ge=1, description="Number of orbital functions using Cartesian shells."
    )


class BasisCapability(Record):
    """Describe explicit element coverage and ECP associations for a named basis."""

    name: str = Field(
        min_length=1, description="Basis name as passed to the application."
    )
    role: str = Field(
        default="basis",
        description="Orbital or fitting role, such as basis or df_basis_scf.",
    )
    status: Support = Field(
        description="Support status for the listed elements and role."
    )
    elements: tuple[str, ...] = Field(
        description="Element symbols explicitly covered by this entry."
    )
    ecps: tuple[ECP, ...] = Field(
        default=(),
        description="ECPs automatically associated with the listed orbital basis.",
    )
    functions: tuple[BasisFunctions, ...] = Field(
        default=(),
        description="Orbital dimensions covered by this basis evidence.",
    )
    sequence: BasisSequence | None = Field(
        default=None,
        description="Evidence-backed family and cardinal number; null leaves "
        "basis-extrapolation membership unknown.",
    )
    evidence: tuple[str, ...] = Field(
        min_length=1,
        description="Evidence IDs supporting this basis information.",
    )

    @property
    def key(self) -> tuple[str, str]:
        """Return the normalized basis and role identity."""
        return (self.name.strip().casefold(), self.role.casefold())

    @model_validator(mode="after")
    def check_elements(self) -> Self:
        """Return unambiguous basis coverage and dimension evidence.

        Raises:
            ValueError: Element evidence repeats or lacks corresponding coverage.
        """
        for values in (
            self.elements,
            tuple(item.element for item in self.ecps),
            tuple(item.element for item in self.functions),
        ):
            if len(values) != len(set(values)):
                raise ValueError("Basis element evidence must be unique")
            if not set(values) <= set(self.elements):
                raise ValueError(
                    "Basis dimension and ECP evidence need element coverage"
                )
        return self


class OptionCapability(Record):
    """Constrain literal option values using externally supplied evidence."""

    name: str = Field(min_length=1, description="Application option name.")
    module: str | None = Field(
        default=None,
        description="Module name; GLOBAL and GLOBALS normalize to null for global.",
    )
    status: Support = Field(description="Support status for this option.")
    values: tuple[SettingValue, ...] = Field(
        default=(),
        description="Accepted exact values; empty permits values of the listed types.",
    )
    types: tuple[Literal["string", "boolean", "integer", "real", "array"], ...] = Field(
        default=(),
        description="Accepted literal types when exact values are not listed.",
    )
    minimum: float | None = Field(
        default=None, description="Inclusive numerical lower bound, if specified."
    )
    maximum: float | None = Field(
        default=None, description="Inclusive numerical upper bound, if specified."
    )
    case_sensitive: bool = Field(
        default=True,
        description="Retain case when comparing declared string literal values.",
    )
    evidence: tuple[str, ...] = Field(
        min_length=1,
        description="Evidence IDs supporting this option contract.",
    )

    @field_validator("module")
    @classmethod
    def _normalize_module(cls, value: str | None) -> str | None:
        return _normalize_option_module(value)

    @property
    def key(self) -> str:
        """Return the case-insensitive module-qualified option name."""
        return (
            f"{self.module.casefold()}." + self.name.casefold()
            if self.module
            else self.name.casefold()
        )

    def accepts(self, value: SettingValue) -> bool:
        """Return whether a literal satisfies the declared values, types, and bounds."""
        if self.values:
            # Python equates True and 1; capability evidence must retain their types.
            allowed = any(
                _literal(value, case_sensitive=self.case_sensitive)
                == _literal(item, case_sensitive=self.case_sensitive)
                for item in self.values
            )
        else:
            kind = (
                "boolean"
                if isinstance(value, bool)
                else "integer"
                if isinstance(value, int)
                else "real"
                if isinstance(value, float)
                else "string"
                if isinstance(value, str)
                else "array"
            )
            allowed = kind in self.types
        if not allowed:
            return False
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return (self.minimum is None or value >= self.minimum) and (
                self.maximum is None or value <= self.maximum
            )
        return self.minimum is None and self.maximum is None


def _disjoint_cases(first: MethodCapability, second: MethodCapability) -> bool:
    left = {item.key: item for item in first.conditions}
    right = {item.key: item for item in second.conditions}
    for key in left.keys() & right.keys():
        a, b = left[key], right[key]
        retain_case = a.case_sensitive and b.case_sensitive
        if not {_literal(value, case_sensitive=retain_case) for value in a.values} & {
            _literal(value, case_sensitive=retain_case) for value in b.values
        }:
            return True
    return False


def _check_method_cases(methods: tuple[MethodCapability, ...]) -> None:
    seen: dict[
        tuple[str, Driver, Reference, DerivativeRoute], list[MethodCapability]
    ] = {}
    for method in methods:
        previous = seen.setdefault(method.key, [])
        if any(not _disjoint_cases(method, other) for other in previous):
            raise ValueError("Capability method cases overlap for the same combination")
        previous.append(method)


class EnvironmentCapability(Record):
    """Record solvent lookup and cavity-element coverage for an implicit environment."""

    kind: Literal["ddx"] = Field(description="Reviewed solvent implementation.")
    radii_set: Literal["uff", "bondi"] = Field(
        description="Reviewed cavity radius table."
    )
    status: Support = Field(description="Coverage status for these component tables.")
    elements: tuple[str, ...] = Field(
        default=(), description="Element labels with known cavity radii."
    )
    solvents: tuple[str, ...] = Field(
        default=(),
        description="Named solvents with tabulated static dielectric constants.",
    )
    evidence: tuple[str, ...] = Field(
        min_length=1, description="Evidence IDs supporting these table facts."
    )

    @property
    def key(self) -> tuple[str, str]:
        """Return the implementation and cavity-table identity."""
        return self.kind, self.radii_set


class CapabilityCatalog(Record):
    """Collect reusable scientific and input contracts independently of releases.

    Each entry cites its own evidence. Source revisions describe those sources,
    without selecting or certifying an execution target. Extend relevant entries
    as scientific coverage grows; a new Psi4 version needs no new catalog.
    """

    id: str = Field(
        default="psi4",
        min_length=1,
        description="Scientific contract collection identity.",
    )
    application: Literal["psi4"] = Field(
        default="psi4", description="Application described by this catalog."
    )
    evidence: tuple[Evidence, ...] = Field(
        min_length=1, description="Sources for every declared capability."
    )
    methods: tuple[MethodCapability, ...] = Field(
        default=(), description="Explicit method/driver/reference/route combinations."
    )
    bases: tuple[BasisCapability, ...] = Field(
        default=(), description="Explicit basis-role and element coverage."
    )
    options: tuple[OptionCapability, ...] = Field(
        default=(), description="Literal option contracts accepted by covered methods."
    )
    components: tuple[ComponentCapability, ...] = Field(
        default=(), description="Optional reference observations, never runtime gates."
    )
    environments: tuple[EnvironmentCapability, ...] = Field(
        default=(), description="Solvent lookup and cavity table coverage."
    )

    @model_validator(mode="after")
    def check_evidence(self) -> Self:
        """Return a catalog with unambiguous keys and resolved evidence references.

        Raises:
            ValueError: Keys repeat or evidence references are missing.
        """
        ids = {item.id for item in self.evidence}
        if len(ids) != len(self.evidence):
            raise ValueError("Evidence IDs must be unique")
        _check_method_cases(self.methods)
        if any(
            not set(product.evidence) <= ids
            for method in self.methods
            for product in method.products
        ):
            raise ValueError("Product evidence references must exist in the catalog")
        for entries in (self.bases, self.options, self.components, self.environments):
            if len({item.key for item in entries}) != len(entries):
                raise ValueError("Capability keys must be unique")
        for evidence_entries in (
            self.methods,
            self.bases,
            self.options,
            self.components,
            self.environments,
        ):
            if any(not set(item.evidence) <= ids for item in evidence_entries):
                raise ValueError(
                    "Capability evidence references must exist in the catalog"
                )
        return self


def _finding(
    path: tuple[str | int, ...],
    code: str,
    message: str,
    status: Literal["unknown", "unsupported", "violated"] = "unknown",
) -> Diagnostic:
    return Diagnostic(path=path, code=code, message=message, status=status)


def _basis_issues(
    step: Calculation,
    elements: set[str],
    catalog: CapabilityCatalog,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    if step.model.basis_assignments:
        return (
            _finding(
                path,
                "basis_binding",
                "Resolve per-center basis evidence before checking assignments.",
            ),
        )
    issues: list[Diagnostic] = []
    bases = {item.key: item for item in catalog.bases}
    requests = [
        (step.model.basis, "basis"),
        *((item.basis, item.role) for item in step.model.auxiliary_bases),
    ]
    for name, role in requests:
        key = (name.strip().casefold(), role.casefold())
        basis = bases.get(key)
        if basis is None:
            issues.append(
                _finding(
                    path, "basis_support", f"No capability evidence for {role} {name}."
                )
            )
        elif basis.status != "supported":
            issues.append(
                _finding(
                    path,
                    "basis_support",
                    f"{role} {name} is {basis.status}.",
                    basis.status,
                )
            )
        else:
            missing = elements - set(basis.elements)
            if missing:
                issues.append(
                    _finding(
                        path,
                        "basis_elements",
                        f"No coverage in {name} for {', '.join(sorted(missing))}.",
                    )
                )
            if role == "basis":
                expected = {
                    item.element: item
                    for item in basis.ecps
                    if item.element in elements
                }
                actual = {item.element: item for item in step.model.ecps}
                if expected != actual:
                    issues.append(
                        _finding(
                            path,
                            "ecp_association",
                            "Declared ECPs differ from the basis capability evidence.",
                            "violated",
                        )
                    )
    return tuple(issues)


def _dimension_issues(
    step: Calculation,
    sites: tuple[Center, ...],
    molecule: Molecule,
    catalog: CapabilityCatalog,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    if step.model.basis_assignments:
        return ()
    basis = next(
        (
            item
            for item in catalog.bases
            if item.key == (step.model.basis.strip().casefold(), "basis")
        ),
        None,
    )
    if basis is None or basis.status != "supported":
        return ()
    functions = {
        item.element: item.spherical if step.model.puream else item.cartesian
        for item in basis.functions
    }
    missing = {item.element for item in sites if item.role != "dummy"} - set(functions)
    if missing:
        return (
            _finding(
                path,
                "basis_dimension",
                f"No orbital dimension evidence for {sorted(missing)}.",
            ),
        )
    capacity = sum(functions[item.element] for item in sites if item.role != "dummy")
    issues: list[Diagnostic] = []
    cores = {item.element: item.core_electrons for item in step.model.ecps}
    if molecule.state is not None:
        electrons = (
            sum(
                item.atomic_number - cores.get(item.element, 0)
                for item in sites
                if item.role == "real"
            )
            - molecule.state.charge
        )
        occupied = (electrons + molecule.state.multiplicity - 1) // 2
        issues.extend(
            tdscf_capacity_issues(step, capacity, occupied, electrons - occupied, path)
        )
        if occupied > capacity:
            issues.append(
                _finding(
                    path,
                    "basis_occupancy",
                    f"Need {occupied} alpha orbitals; basis has {capacity}.",
                    "violated",
                )
            )
    potential = step.model.external_potential
    if (
        potential is not None
        and potential.matrix is not None
        and len(potential.matrix.root) != capacity
    ):
        issues.append(
            _finding(
                path,
                "potential_dimension",
                f"External matrix must have dimension {capacity}.",
                "violated",
            )
        )
    return tuple(issues)


def _option_issues(
    setting: Setting,
    method: MethodCapability,
    catalog: CapabilityCatalog,
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    module, name = setting.key
    key = f"{module}.{name}" if module else name
    option = next((item for item in catalog.options if item.key == key), None)
    if key not in {item.casefold() for item in method.options} or option is None:
        return (
            _finding(
                path,
                "option_support",
                f"No combination-specific option evidence for {key}.",
            ),
        )
    if option.status != "supported":
        return (
            _finding(
                path,
                "option_support",
                f"Option {key} is {option.status}.",
                option.status,
            ),
        )
    if not option.accepts(setting.value):
        return (
            _finding(
                path,
                "option_value",
                f"Option {key} value is outside the declared contract.",
                "unsupported",
            ),
        )
    return ()


def _features(step: Calculation, ghost: bool) -> tuple[str, ...]:
    present = (
        ("cartesian_basis", not step.model.puream),
        ("ghost_centers", ghost),
        ("ecp", bool(step.model.ecps)),
        ("frozen_core", step.model.frozen_core),
        ("constraints", bool(step.constraints)),
        ("electric_field", step.model.electric_field is not None),
        ("external_potential", step.model.external_potential is not None),
        ("excited_state", step.model.electronic_target is not None),
        ("vibrational_analysis:ideal_gas_rrho", step.analysis is not None),
        ("sapt", step.sapt is not None),
        ("tdscf", step.model.tdscf is not None),
    )
    return (
        *(name for name, enabled in present if enabled),
        *(
            (
                f"tdscf_spin:{step.model.tdscf.spin}",
                f"tdscf_approximation:{step.model.tdscf.approximation}",
            )
            if step.model.tdscf
            else ()
        ),
        *(
            f"auxiliary_basis:{item.role.casefold()}"
            for item in step.model.auxiliary_bases
        ),
        *(f"property:{name.casefold()}" for name in step.properties),
        *((step.model.environment.kind,) if step.model.environment else ()),
        *(
            (f"ddx_model:{step.model.environment.ddx.model}",)
            if step.model.environment and step.model.environment.kind == "ddx"
            else ()
        ),
        *(
            (f"pcm_solver:{step.model.environment.pcm.solver}",)
            if step.model.environment and step.model.environment.kind == "pcm"
            else ()
        ),
        *(
            (
                f"sapt_basis:{step.sapt.basis}",
                "sapt_induction:"
                + ("coupled" if step.sapt.coupled_induction else "uncoupled"),
            )
            if step.sapt
            else ()
        ),
        *(("sapt_midbond",) if step.sapt and step.sapt.midbond_fragment else ()),
    )


def _condition_issues(
    step: Calculation,
    method: MethodCapability,
    path: tuple[str | int, ...],
    units: Literal["angstrom", "bohr"] = "bohr",
) -> tuple[Diagnostic, ...]:
    if not method.conditions:
        return ()
    explicit = {
        setting.key: setting.value for setting in step.model.engine_settings_for(units)
    }
    return tuple(
        _finding(
            (*path, "settings"),
            "capability_condition",
            f"Evidence requires {condition.module or 'global'}.{condition.name} "
            f"in {condition.values!r}; observed {explicit.get(condition.key)!r}.",
        )
        for condition in method.conditions
        if condition.key not in explicit
        or not condition.accepts(explicit[condition.key])
    )


def matching_method(
    step: Calculation,
    catalog: CapabilityCatalog,
    *,
    units: Literal["angstrom", "bohr"] = "bohr",
) -> MethodCapability | None:
    """Return the unique evidence case matching a calculation's explicit options.

    Args:
        step: Declared calculation and electronic model.
        catalog: Scientific and supported-input source contracts.
        units: Molecule length units for geometry-dependent native options.

    Returns:
        Matching case, or null if explicit option conditions remain uncovered.
    """
    key = (
        step.model.method.strip().casefold(),
        step.driver,
        step.model.reference,
        step.derivative_route,
    )
    return next(
        (
            method
            for method in catalog.methods
            if method.key == key and not _condition_issues(step, method, (), units)
        ),
        None,
    )


def _resolve_method(
    step: Calculation,
    catalog: CapabilityCatalog,
    path: tuple[str | int, ...],
    units: Literal["angstrom", "bohr"],
) -> tuple[MethodCapability | None, tuple[Diagnostic, ...]]:
    key = (
        step.model.method.strip().casefold(),
        step.driver,
        step.model.reference,
        step.derivative_route,
    )
    candidates = tuple(method for method in catalog.methods if method.key == key)
    if not candidates:
        return None, (
            _finding(path, "method_support", f"No capability evidence for {key}."),
        )
    method = matching_method(step, catalog, units=units)
    if method is not None:
        return method, ()
    return None, tuple(
        issue
        for candidate in candidates
        for issue in _condition_issues(step, candidate, path, units)
    )


def _sequence_binding(
    basis: BasisCapability | None,
    expected: tuple[str, int],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    if basis is None or basis.sequence is None:
        return (
            _finding(
                path,
                "extrapolation_basis_evidence",
                "Supply basis-family/cardinal evidence.",
            ),
        )
    if basis.status != "supported":
        return (
            _finding(
                path,
                "extrapolation_basis_evidence",
                "Basis is not supported.",
                basis.status,
            ),
        )
    if basis.sequence.key != expected:
        return (
            _finding(
                path,
                "extrapolation_basis_sequence",
                "Basis-family/cardinal evidence differs from the requested sequence.",
                "violated",
            ),
        )
    return ()


def _extrapolation_capability_issues(
    plan: Plan, catalog: CapabilityCatalog
) -> tuple[Diagnostic, ...]:
    recipes = tuple(
        (index, step)
        for index, step in enumerate(plan.steps)
        if isinstance(step, Combination) and step.extrapolation is not None
    )
    if not recipes:
        return ()
    bases = {item.key: item for item in catalog.bases}
    forms = expression_forms(plan)
    steps = {item.id: item for item in plan.steps}
    issues: list[Diagnostic] = []
    for index, step in recipes:
        if step.extrapolation is None:
            continue
        recipe = step.extrapolation
        fitting_families: dict[tuple[str, str], set[str]] = {}
        for name, point in (("low", recipe.low), ("high", recipe.high)):
            path: tuple[str | int, ...] = ("steps", index, "extrapolation", name)
            issues.extend(
                _sequence_binding(
                    bases.get((point.basis.strip().casefold(), "basis")),
                    (recipe.family.strip().casefold(), point.cardinal),
                    path,
                )
            )
            for leaf, coefficient in forms[point.result].items():
                source = steps[leaf]
                if not isinstance(source, Calculation):
                    continue
                for auxiliary in source.model.auxiliary_bases:
                    role = auxiliary.role.casefold()
                    binding = bases.get((auxiliary.basis.strip().casefold(), role))
                    family = (
                        binding.sequence.family.strip().casefold()
                        if binding and binding.sequence
                        else ""
                    )
                    issues.extend(
                        _sequence_binding(binding, (family, point.cardinal), path)
                    )
                    fitting_families.setdefault((str(coefficient), role), set()).add(
                        family
                    )
        if any(len(families) != 1 for families in fitting_families.values()):
            issues.append(
                _finding(
                    ("steps", index, "extrapolation"),
                    "extrapolation_fitting_family",
                    "Each target/reference fitting role needs one common basis family.",
                    "violated",
                )
            )
    return tuple(issues)


def _sapt_context_issues(
    step: Calculation, method: MethodCapability, path: tuple[str | int, ...]
) -> tuple[Diagnostic, ...]:
    if "sapt" not in method.features or step.sapt is not None:
        return ()
    return (
        _finding(
            (*path[:-1], "sapt"),
            "sapt_context",
            "The SAPT method requires explicit partition and basis/induction intent.",
            "violated",
        ),
    )


def _declared_option_issues(
    step: Calculation,
    method: MethodCapability,
    catalog: CapabilityCatalog,
    units: Literal["angstrom", "bohr"],
    path: tuple[str | int, ...],
) -> tuple[Diagnostic, ...]:
    choices = tuple(
        (setting, (*path, "settings", index))
        for index, setting in enumerate(step.model.settings)
    )
    if step.model.environment is not None:
        choices += tuple(
            (setting, (*path, "environment", "settings", index))
            for index, setting in enumerate(
                step.model.environment.engine_settings_for(units)
            )
        )
    return tuple(
        issue
        for setting, location in choices
        for issue in _option_issues(setting, method, catalog, location)
    )


def check_capabilities(
    plan: Plan, inspection: Inspection, catalog: CapabilityCatalog
) -> tuple[Diagnostic, ...]:
    """Return unsupported and unknown application choices with their plan locations."""
    issues: list[Diagnostic] = []
    for index, step in enumerate(plan.steps):
        if not isinstance(step, Calculation):
            continue
        path: tuple[str | int, ...] = ("steps", index, "model")
        molecule = inspection.contexts[step.geometry]
        method, findings = _resolve_method(step, catalog, path, molecule.units)
        issues.extend(findings)
        if method is None:
            continue
        if method.status != "supported":
            issues.append(
                _finding(
                    path,
                    "method_support",
                    f"Method combination is {method.status}.",
                    method.status,
                )
            )
            continue
        issues.extend(_sapt_context_issues(step, method, path))
        try:
            sites = centers(molecule)
        except ValueError:
            # The operation contract has already located malformed nuclear labels.
            continue
        elements = {item.element for item in sites if item.role != "dummy"}
        issues.extend(_basis_issues(step, elements, catalog, path))
        issues.extend(_dimension_issues(step, sites, molecule, catalog, path))
        if method.bases and step.model.basis.strip().casefold() not in {
            name.casefold() for name in method.bases
        }:
            issues.append(
                _finding(
                    path,
                    "method_basis",
                    "Orbital basis is outside the method's supported combinations.",
                    "unsupported",
                )
            )
        quantity = primary_quantity(step)
        if (quantity.meaning, quantity.unit, quantity.shape) != (
            method.quantity.meaning,
            method.quantity.unit,
            method.quantity.shape,
        ):
            issues.append(
                _finding(
                    path,
                    "method_quantity",
                    "Expected quantity differs from the documented primary product.",
                    "violated",
                )
            )
        if quantity.number_kind != method.quantity.number_kind:
            issues.append(
                _finding(
                    path,
                    "method_quantity",
                    "Primary numeric domain differs from the documented return type.",
                    "violated",
                )
            )
        missing = set(
            _features(step, any(item.role == "ghost" for item in sites))
        ) - set(method.features)
        issues.extend(
            _finding(
                path,
                "feature_support",
                f"No combination-specific evidence for {feature}.",
            )
            for feature in sorted(missing)
        )
        issues.extend(
            _declared_option_issues(step, method, catalog, molecule.units, path)
        )
    issues.extend(_product_capability_issues(plan, catalog, inspection))
    issues.extend(_extrapolation_capability_issues(plan, catalog))
    return tuple(issues)


def _product_capability_issues(
    plan: Plan, catalog: CapabilityCatalog, inspection: Inspection
) -> tuple[Diagnostic, ...]:
    calculations = {
        step.id: step for step in plan.steps if isinstance(step, Calculation)
    }
    issues: list[Diagnostic] = []
    for index, step in enumerate(plan.steps):
        if not isinstance(step, Product):
            continue
        path: tuple[str | int, ...] = ("steps", index, "name")
        calculation = calculations[step.calculation]
        method = matching_method(
            calculation, catalog, units=inspection.contexts[calculation.geometry].units
        )
        entry = (
            next((item for item in method.products if item.name == step.name), None)
            if method
            else None
        )
        if (
            calculations[step.calculation].driver == "frequency"
            and method is not None
            and "native_vibrec" not in method.features
        ):
            issues.append(
                _finding(
                    path,
                    "product_output_support",
                    "No native vibrational record output contract "
                    "for this producing case.",
                )
            )
        if entry is None:
            issues.append(
                _finding(
                    path,
                    "product_support",
                    f"No combination-specific evidence for product {step.name}.",
                )
            )
        elif entry.status != "supported":
            issues.append(
                _finding(
                    path,
                    "product_support",
                    f"Product {step.name} is {entry.status}.",
                    entry.status,
                )
            )
        elif entry.quantity != product_quantity(step.name):
            issues.append(
                _finding(
                    path,
                    "product_type_evidence",
                    "Documented product type differs from the canonical contract.",
                    "violated",
                )
            )
    return tuple(issues)


class ProductCase(Record):
    """Locate product evidence within its producing method and option conditions."""

    method: str = Field(description="Producing method name.")
    driver: Driver = Field(description="Producing operation.")
    reference: Reference = Field(description="Producing SCF reference.")
    derivative_route: DerivativeRoute = Field(description="Producing derivative route.")
    method_status: Support = Field(
        description="Status of the complete producing method case."
    )
    features: tuple[str, ...] = Field(
        default=(), description="Producing-case feature coverage, including SAPT modes."
    )
    conditions: tuple[OptionCondition, ...] = Field(
        description="Explicit option conditions on the producing case."
    )
    components: tuple[str, ...] = Field(
        description="Source-case component names; deployment is operator-managed."
    )
    product: ProductCapability = Field(
        description="Product availability, type, and evidence references."
    )


def discover_products(
    catalog: CapabilityCatalog,
    *,
    method: str | None = None,
    driver: Driver | None = None,
    name: ProductName | None = None,
) -> tuple[ProductCase, ...]:
    """Return relevant named product evidence with producing conditions retained.

    Args:
        catalog: Source contracts and their provenance, without target runtime checks.
        method: Optional exact producing method filter, ignoring case.
        driver: Optional producing driver filter.
        name: Optional exact named product filter.

    Returns:
        Matching product cases; missing entries remain unknown.
    """
    return tuple(
        ProductCase(
            method=case.method,
            driver=case.driver,
            reference=case.reference,
            derivative_route=case.derivative_route,
            method_status=case.status,
            features=case.features,
            conditions=case.conditions,
            components=case.components,
            product=product,
        )
        for case in discover_capabilities(catalog, method=method, driver=driver)
        for product in case.products
        if name is None or product.name == name
    )


def discover_capabilities(
    catalog: CapabilityCatalog,
    *,
    method: str | None = None,
    driver: Driver | None = None,
) -> tuple[MethodCapability, ...]:
    """Return only capability entries relevant to a method or driver query."""
    return tuple(
        item
        for item in catalog.methods
        if (method is None or item.method.casefold() == method.strip().casefold())
        and (driver is None or item.driver == driver)
    )
