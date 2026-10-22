"""Prove plan relationships by asking Z3 for a violating assignment."""

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from time import monotonic
from typing import Literal

import z3

from psi4_parser.builder import Cartesian, Molecule
from psi4_parser.formal.capabilities import (
    CapabilityCatalog,
    check_capabilities,
    matching_method,
)
from psi4_parser.formal.catalogs import load_catalog
from psi4_parser.formal.contracts import RULE_VERSION, Inspection, inspect_contracts
from psi4_parser.formal.coordinate_models import (
    CoordinateRange,
    CoordinateValue,
    coordinate_number,
)
from psi4_parser.formal.coordinate_reasoning import CoordinateReasoner
from psi4_parser.formal.coverage import (
    Coverage,
    derive_coverage,
    requirement_reference_issues,
)
from psi4_parser.formal.environment_contracts import environment_assumptions
from psi4_parser.formal.excited_contracts import tdscf_assumptions
from psi4_parser.formal.extrapolation_models import (
    ExponentialExtrapolation,
    InversePowerExtrapolation,
)
from psi4_parser.formal.intent import ScientificRequest
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Diagnostic,
    EnergyFormula,
    EnergyTerm,
    Limits,
    Obligation,
    Plan,
    Product,
    Report,
    Requirement,
    SameGeometry,
    SameModel,
    Step,
    Subsystem,
    UsesGeometry,
    Witness,
)
from psi4_parser.formal.products import (
    PRIMARY_SCALAR_PRODUCTS,
    SAPT_COMPONENTS,
    THERMAL_TOTALS,
    product_identity,
    product_quantity,
)
from psi4_parser.formal.science import (
    ComponentRequirement,
    ElectronicTarget,
    ProductName,
    Rational,
)

# Every report states the assumptions that limit its claims.
_HALF_TURN = 180
_ASSUMPTIONS = (
    (
        "Psi4 calls complete successfully with documented return values and "
        "molecule updates."
    ),
    (
        "Each calculation uses a private clone and native option defaults "
        "plus the declared model and calculation settings."
    ),
    (
        "Option isolation covers native modules and explicitly named option modules. "
        "Unlisted plugin state, process resources, and concurrent option mutation "
        "remain outside this contract."
    ),
    "Geometry equality means shared provenance, not numerical or physical equivalence.",
    "Energy formulas use exact real arithmetic; floating-point errors are not bounded.",
    (
        "Primary return values have the declared quantity types; their "
        "physical interpretation depends on application capability evidence."
    ),
    (
        "Electronic-state suitability, convergence, and scientific accuracy "
        "are outside the encoded construction claims."
    ),
)


def _required_components(
    plan: Plan, catalog: CapabilityCatalog | None, inspection: Inspection | None
) -> tuple[ComponentRequirement, ...]:
    if catalog is None:
        return ()
    methods = tuple(
        matching_method(
            step,
            catalog,
            units=inspection.contexts[step.geometry].units
            if inspection is not None
            else "bohr",
        )
        for step in plan.steps
        if isinstance(step, Calculation)
    )
    names = {
        name.strip().casefold()
        for method in methods
        if method is not None
        for name in method.components
    }
    return tuple(ComponentRequirement(name=name) for name in sorted(names))


def _scalar_step(step: Step) -> bool:
    if isinstance(step, Product):
        return not product_quantity(step.name).shape
    return isinstance(step, Combination) or (
        isinstance(step, Calculation) and step.driver not in {"gradient", "hessian"}
    )


def _step_references(
    step: Step,
    geometries: set[str],
    energies: set[str],
    calculations: set[str],
    path: tuple[str | int, ...],
) -> list[Diagnostic]:
    if isinstance(step, Product):
        return (
            []
            if step.calculation in calculations
            else [
                Diagnostic(
                    path=(*path, "calculation"),
                    code="product_source",
                    message="Product source must be a preceding calculation.",
                )
            ]
        )
    if isinstance(step, (Calculation, Subsystem)):
        return (
            []
            if step.geometry in geometries
            else [
                Diagnostic(
                    path=(*path, "geometry"),
                    message=f"Geometry must precede use: {step.geometry}",
                )
            ]
        )
    issues = _term_diagnostics(step.terms, energies, path)
    if step.extrapolation is not None:
        issues.extend(
            Diagnostic(
                path=(*path, "extrapolation", name, "result"),
                code="extrapolation_source",
                message=f"Extrapolation quantity must precede use: {point.result}.",
            )
            for name, point in (
                ("low", step.extrapolation.low),
                ("high", step.extrapolation.high),
            )
            if point.result not in energies
        )
    return issues


def _diagnostics(plan: Plan) -> tuple[Diagnostic, ...]:
    problems: list[Diagnostic] = []
    names: set[str] = set()
    geometries: set[str] = set()
    energies: set[str] = set()
    preceding_calculations: set[str] = set()
    for index, declaration in enumerate(plan.molecules):
        path: tuple[str | int, ...] = ("molecules", index)
        if declaration.name in names:
            problems.append(
                Diagnostic(path=(*path, "name"), message="Plan names must be unique.")
            )
        names.add(declaration.name)
        geometries.add(declaration.name)
        problems.extend(_molecule_diagnostics(index, declaration.geometry))
    for index, step in enumerate(plan.steps):
        path = ("steps", index)
        if step.id in names:
            problems.append(
                Diagnostic(path=(*path, "id"), message="Plan names must be unique.")
            )
        names.add(step.id)
        problems.extend(
            _step_references(step, geometries, energies, preceding_calculations, path)
        )
        if isinstance(step, Subsystem) or (
            isinstance(step, Calculation) and step.driver == "optimize"
        ):
            geometries.add(step.id)
        if _scalar_step(step):
            energies.add(step.id)
        if isinstance(step, Calculation):
            preceding_calculations.add(step.id)
    calculations = {step.id for step in plan.steps if isinstance(step, Calculation)}
    for index, requirement in enumerate(plan.requirements):
        problems.extend(
            requirement_reference_issues(
                requirement,
                ("requirements", index),
                calculations,
                geometries,
                energies,
            )
        )
    return tuple(problems)


def _molecule_diagnostics(index: int, geometry: Molecule) -> list[Diagnostic]:
    problems: list[Diagnostic] = []
    path: tuple[str | int, ...] = ("molecules", index)
    if geometry.state is None:
        problems.append(
            Diagnostic(
                path=(*path, "geometry", "state"),
                message="Supply the overall charge and multiplicity explicitly.",
            )
        )
    if (
        not geometry.atoms
        or geometry.sources
        or geometry.efp
        or geometry.parameters
        or any(
            not isinstance(atom.coordinates, Cartesian)
            or not all(
                isinstance(value, float)
                for value in (
                    atom.coordinates.x,
                    atom.coordinates.y,
                    atom.coordinates.z,
                )
            )
            for atom in geometry.atoms
        )
    ):
        problems.append(
            Diagnostic(
                path=(*path, "geometry"),
                message=(
                    "Use resolved Cartesian atoms without external sources, EFPs, or "
                    "parameters; convert geometry before planning."
                ),
            )
        )
    return problems


def _term_diagnostics(
    terms: tuple[EnergyTerm, ...], energies: set[str], path: tuple[str | int, ...]
) -> list[Diagnostic]:
    return [
        Diagnostic(
            path=(*path, "terms", index, "result"),
            message=f"Unknown or forward energy reference: {term.result}",
        )
        for index, term in enumerate(terms)
        if term.result not in energies
    ]


@dataclass
class _Encoding:
    context: z3.Context
    solver: z3.Solver
    energies: dict[str, z3.ArithRef] = field(default_factory=dict)
    geometries: dict[str, z3.SeqRef] = field(default_factory=dict)
    models: dict[str, z3.SeqRef] = field(default_factory=dict)

    def terms(self, terms: tuple[EnergyTerm, ...]) -> z3.ArithRef:
        return z3.Sum(
            *(
                z3.RealVal(
                    term.coefficient.smt
                    if isinstance(term.coefficient, Rational)
                    else term.coefficient,
                    self.context,
                )
                * self.energies[term.result]
                for term in terms
            )
        )


@dataclass
class _ProductEncoding:
    encoding: _Encoding
    sources: dict[str, int]
    products: dict[tuple[str, ProductName, str], z3.ArithRef] = field(
        default_factory=dict
    )

    def value(
        self,
        calculation: str,
        name: ProductName,
        target: ElectronicTarget | None = None,
    ) -> z3.ArithRef:
        key = product_identity(calculation, name, target)
        if key not in self.products:
            if name in PRIMARY_SCALAR_PRODUCTS:
                self.products[key] = self.encoding.energies[calculation]
            elif name in THERMAL_TOTALS:
                self.products[key] = z3.Sum(
                    self.value(calculation, "electronic_energy"),
                    self.value(calculation, THERMAL_TOTALS[name]),
                )
            elif name == "excited_state_energy":
                self.products[key] = z3.Sum(
                    self.value(calculation, "electronic_energy"),
                    self.value(calculation, "excitation_energy", target),
                )
            else:
                self.products[key] = z3.Real(
                    f"product_{self.sources[calculation]}_{name}_{len(self.products)}",
                    self.encoding.context,
                )
        return self.products[key]


def _encode(plan: Plan, limits: Limits) -> _Encoding:
    context = z3.Context(proof=True)
    solver = z3.Solver(ctx=context)
    solver.set(timeout=limits.timeout_ms, rlimit=limits.resource_limit)
    encoding = _Encoding(context, solver)
    sources = {
        step.id: index
        for index, step in enumerate(plan.steps)
        if isinstance(step, Calculation)
    }
    products = _ProductEncoding(encoding, sources)

    for index, step in enumerate(plan.steps):
        if isinstance(step, Subsystem):
            continue
        if isinstance(step, Product):
            encoding.energies[step.id] = products.value(
                step.calculation, step.name, step.electronic_target
            )
            continue
        energy = z3.Real(f"energy_{index}", context)
        if isinstance(step, Calculation):
            geometry = z3.String(f"geometry_{index}", context)
            model = z3.String(f"model_{index}", context)
            model_key = step.model.identity
            solver.add(
                z3.Not(z3.Distinct(geometry, z3.StringVal(step.geometry, context)))
            )
            solver.add(z3.Not(z3.Distinct(model, z3.StringVal(model_key, context))))
            encoding.geometries[step.id] = geometry
            encoding.models[step.id] = model
        else:
            solver.add(z3.Not(z3.Distinct(energy, encoding.terms(step.terms))))
        encoding.energies[step.id] = energy
        if isinstance(step, Calculation) and step.sapt is not None:
            solver.add(
                z3.Not(
                    z3.Distinct(
                        energy,
                        z3.Sum(
                            *(products.value(step.id, name) for name in SAPT_COMPONENTS)
                        ),
                    )
                )
            )
    return encoding


def _claim(
    requirement: UsesGeometry | SameGeometry | SameModel | EnergyFormula,
    encoding: _Encoding,
) -> tuple[z3.ExprRef, z3.ExprRef, str]:
    if isinstance(requirement, UsesGeometry):
        return (
            encoding.geometries[requirement.calculation],
            z3.StringVal(requirement.geometry, encoding.context),
            (
                f"Require {requirement.calculation} to consume geometry "
                f"{requirement.geometry}."
            ),
        )
    if isinstance(requirement, EnergyFormula):
        return (
            encoding.energies[requirement.result],
            encoding.terms(requirement.terms),
            (
                f"Require {requirement.result} to equal the requested energy formula "
                "for all input energies."
            ),
        )
    left, right = requirement.calculations
    if isinstance(requirement, SameGeometry):
        return (
            encoding.geometries[left],
            encoding.geometries[right],
            f"Require {left} and {right} to consume the same geometry source.",
        )
    return (
        encoding.models[left],
        encoding.models[right],
        f"Require {left} and {right} to use the same method, basis, and reference.",
    )


def _check_requirement(
    index: int,
    requirement: Requirement,
    encoding: _Encoding,
    coordinates: CoordinateReasoner,
) -> Obligation:
    if isinstance(requirement, (CoordinateValue, CoordinateRange)):
        return _check_coordinate(index, requirement, encoding, coordinates)
    actual, expected, message = _claim(requirement, encoding)
    return _prove(
        index,
        z3.Distinct(actual, expected),
        message,
        (("actual", actual), ("expected", expected)),
        encoding,
    )


def _coordinate_intervals(
    requirement: CoordinateValue | CoordinateRange,
) -> tuple[tuple[Fraction, Fraction], ...]:
    tolerance = Fraction(str(coordinate_number(requirement.tolerance)))
    if isinstance(requirement, CoordinateValue):
        lower = upper = Fraction(str(coordinate_number(requirement.value)))
    else:
        lower = Fraction(str(coordinate_number(requirement.lower)))
        upper = Fraction(str(coordinate_number(requirement.upper)))
    if requirement.coordinate.kind != "dihedral":
        return ((lower - tolerance, upper + tolerance),)
    center = (lower + upper) / 2
    radius = (upper - lower) / 2 + tolerance
    center = (center + 180) % 360 - 180
    if radius >= _HALF_TURN:
        return ((Fraction(-180), Fraction(180)),)
    return tuple(
        (center - radius + turn, center + radius + turn) for turn in (-360, 0, 360)
    )


def _check_coordinate(
    index: int,
    requirement: CoordinateValue | CoordinateRange,
    encoding: _Encoding,
    coordinates: CoordinateReasoner,
) -> Obligation:
    domain = coordinates.domain(requirement.geometry, requirement.coordinate)
    unit = (
        "angstrom"
        if requirement.coordinate.kind in {"distance", "cartesian"}
        else "degrees"
    )
    tolerance = coordinate_number(requirement.tolerance)
    target = (
        f"{coordinate_number(requirement.value)} +/- {tolerance}"
        if isinstance(requirement, CoordinateValue)
        else f"[{coordinate_number(requirement.lower)}, "
        f"{coordinate_number(requirement.upper)}], tolerance {tolerance}"
    )
    message = (
        f"Require {requirement.geometry} {requirement.coordinate.kind} "
        f"{requirement.coordinate.atoms} {requirement.coordinate.axes}: "
        f"{target} {unit}. {domain.message}"
    )
    if domain.lower is None or domain.upper is None:
        return Obligation(index=index, status="unknown", message=message, smt2="")
    actual = z3.Real(f"coordinate_{index}", encoding.context)
    intervals = _coordinate_intervals(requirement)
    expected = z3.Or(
        *(
            z3.And(
                actual >= z3.RealVal(str(lower), encoding.context),
                actual <= z3.RealVal(str(upper), encoding.context),
            )
            for lower, upper in intervals
        )
    )
    encoding.solver.push()
    try:
        encoding.solver.add(
            actual >= z3.RealVal(str(domain.lower), encoding.context),
            actual <= z3.RealVal(str(domain.upper), encoding.context),
        )
        return _prove(index, z3.Not(expected), message, (("actual", actual),), encoding)
    finally:
        encoding.solver.pop()


def _prove(
    index: int,
    violation: z3.BoolRef,
    message: str,
    witnesses: tuple[tuple[str, z3.ExprRef], ...],
    encoding: _Encoding,
) -> Obligation:
    solver = encoding.solver
    solver.push()
    try:
        solver.add(violation)
        query = solver.to_smt2()
        result = solver.check()
        if result == z3.unsat:
            return Obligation(
                index=index,
                status="proved",
                message=message,
                smt2=query,
                proof=solver.proof().sexpr(),
            )
        if result == z3.sat:
            model = solver.model()
            witness = tuple(
                Witness(
                    name=name,
                    value=model.eval(expression, model_completion=True).sexpr(),
                )
                for name, expression in witnesses
            )
            return Obligation(
                index=index,
                status="violated",
                message=message,
                smt2=query,
                counterexample=witness,
            )
        return Obligation(
            index=index, status="unknown", message=solver.reason_unknown(), smt2=query
        )
    finally:
        solver.pop()


@dataclass
class _Audit:
    plan: Plan
    request: ScientificRequest | None
    catalog: CapabilityCatalog | None
    limits: Limits
    inspection: Inspection | None = None
    coverage: Coverage | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    obligations: tuple[Obligation, ...] = ()
    capability_status: (
        Literal["supported", "violated", "unknown", "invalid", "unsupported"] | None
    ) = None
    started: float = field(default_factory=monotonic)

    def remaining_ms(self) -> int:
        return max(
            0, self.limits.total_timeout_ms - int((monotonic() - self.started) * 1000)
        )

    def report(self) -> Report:
        status: Literal["proved", "violated", "unknown", "invalid", "unsupported"] = (
            "proved"
        )
        statuses = {item.status for item in self.diagnostics} | {
            item.status for item in self.obligations
        }
        for candidate in ("invalid", "violated", "unsupported", "unknown"):
            if candidate in statuses:
                status = candidate
                break
        assumptions: tuple[str, ...] = _ASSUMPTIONS
        if any(
            isinstance(step, Calculation) and step.sapt is not None
            for step in self.plan.steps
        ):
            assumptions += (
                "SAPT uses the declared monomer partition, basis treatment, "
                "induction choice, and native component definitions. "
                "Convergence and scientific suitability remain assumptions.",
                "Native SAPT variable bindings are declarations only. "
                "A separate consumer must collect transient values before later "
                "application state changes; export does not snapshot them.",
            )
        if any(
            isinstance(step, Combination)
            and isinstance(step.extrapolation, InversePowerExtrapolation)
            for step in self.plan.steps
        ):
            assumptions += (
                "The explicitly chosen inverse-power model estimates the requested "
                "basis-limit correction; asymptotic convergence, exponent suitability, "
                "reference-state consistency, and numerical accuracy are assumptions.",
            )
        if any(
            isinstance(step, Combination)
            and isinstance(step.extrapolation, ExponentialExtrapolation)
            for step in self.plan.steps
        ):
            assumptions += (
                "The chosen exponential law estimates the HF reference limit; "
                "decay suitability, asymptotic convergence, reference-state "
                "consistency, and physical accuracy remain assumptions.",
                "Exponential weights have a certified absolute coefficient bound, "
                "separate from physical accuracy and floating-point evaluation. "
                "The resulting two-point energy error is bounded by that coefficient "
                "error times the absolute difference between the input energies.",
            )
        if any(
            isinstance(step, Calculation) and step.analysis is not None
            for step in self.plan.steps
        ):
            assumptions += (
                "Native harmonic/thermal analysis is applied as requested; "
                "stationary-point character, imaginary-mode handling, symmetry "
                "number, and RRHO suitability remain scientific assumptions.",
            )
        if any(
            isinstance(item, (CoordinateValue, CoordinateRange))
            for item in (
                *self.plan.requirements,
                *(self.coverage.requirements if self.coverage else ()),
            )
        ):
            assumptions += (
                "Coordinate measurements use floating-point geometry and unit "
                "conversions; caller tolerances define accepted input differences. "
                "Future coordinate bounds assume successful enforcement of the "
                "declared optimizer constraints.",
            )
        assumptions += environment_assumptions(self.plan)
        assumptions += tdscf_assumptions(self.plan)
        components = _required_components(self.plan, self.catalog, self.inspection)
        if self.catalog is not None:
            assumptions += tuple(
                f"Declared capability assumption {item.id}: {item.source}"
                for item in self.catalog.evidence
                if item.kind == "declaration"
            )
        identity = json.dumps(
            (
                self.plan.model_dump_json(),
                self.request.model_dump_json() if self.request else None,
                self.catalog.model_dump_json() if self.catalog else None,
                RULE_VERSION,
                z3.get_version_string(),
                self.limits.model_dump_json(),
            ),
            separators=(",", ":"),
        )
        return Report(
            status=status,
            runtime_policy="operator_managed",
            capability_status=self.capability_status,
            plan_digest=hashlib.sha256(
                self.plan.model_dump_json().encode()
            ).hexdigest(),
            solver_version=z3.get_version_string(),
            assumptions=assumptions,
            diagnostics=self.diagnostics,
            obligations=self.obligations,
            rule_version=RULE_VERSION,
            geometries=self.inspection.geometries if self.inspection else (),
            quantities=self.inspection.quantities if self.inspection else (),
            native_outputs=self.inspection.native_outputs if self.inspection else (),
            native_variables=self.inspection.native_variables
            if self.inspection
            else (),
            required_components=components,
            request_digest=hashlib.sha256(
                self.request.model_dump_json().encode()
            ).hexdigest()
            if self.request
            else None,
            scope="scientific_request" if self.request else "relationships",
            coverage=self.coverage.goals if self.coverage else (),
            request_complete=self.request is not None and status == "proved",
            capability_digest=hashlib.sha256(
                self.catalog.model_dump_json().encode()
            ).hexdigest()
            if self.catalog
            else None,
            limits=self.limits,
            verification_digest=hashlib.sha256(identity.encode()).hexdigest(),
        )


def _solve(audit: _Audit) -> None:
    requirements = (
        *audit.plan.requirements,
        *(audit.coverage.requirements if audit.coverage else ()),
    )
    if len(requirements) > audit.limits.max_obligations:
        audit.diagnostics += (
            Diagnostic(
                path=("requirements",),
                code="verification_budget",
                status="unknown",
                message="Obligation count exceeds the verification budget.",
            ),
        )
        return
    checking = Plan(
        molecules=audit.plan.molecules,
        steps=audit.plan.steps,
        requirements=requirements,
    )
    problems = _diagnostics(checking)
    if problems:
        audit.diagnostics += problems
        return
    encoding = _encode(audit.plan, audit.limits)
    remaining = audit.remaining_ms()
    if not remaining:
        audit.diagnostics += (
            Diagnostic(
                path=(),
                code="verification_budget",
                status="unknown",
                message="Total verification time budget exhausted.",
            ),
        )
        return
    encoding.solver.set(
        timeout=min(audit.limits.timeout_ms, remaining),
        rlimit=audit.limits.resource_limit,
    )
    consistency = encoding.solver.check()
    if consistency != z3.sat:
        audit.diagnostics += (
            Diagnostic(
                path=(),
                status="invalid" if consistency == z3.unsat else "unknown",
                code="premise_consistency",
                message="Encoded premises are inconsistent."
                if consistency == z3.unsat
                else encoding.solver.reason_unknown(),
            ),
        )
        return
    obligations: list[Obligation] = []
    coordinates = CoordinateReasoner(audit.plan)
    for index, requirement in enumerate(requirements):
        remaining = audit.remaining_ms()
        if not remaining:
            audit.diagnostics += (
                Diagnostic(
                    path=("requirements", index),
                    code="verification_budget",
                    status="unknown",
                    message="Total verification time budget exhausted.",
                ),
            )
            break
        encoding.solver.set(
            timeout=min(audit.limits.timeout_ms, remaining),
            rlimit=audit.limits.resource_limit,
        )
        obligation = _check_requirement(index, requirement, encoding, coordinates)
        path: tuple[str | int, ...] = (
            ("requirements", index)
            if index < len(audit.plan.requirements)
            else (
                "request",
                "derived_requirements",
                index - len(audit.plan.requirements),
            )
        )
        obligations.append(
            Obligation(
                index=obligation.index,
                status=obligation.status,
                message=obligation.message,
                smt2=obligation.smt2,
                proof=obligation.proof,
                counterexample=obligation.counterexample,
                path=path,
            )
        )
    audit.obligations = tuple(obligations)


def verify(
    plan: Plan,
    *,
    request: ScientificRequest | None = None,
    limits: Limits | None = None,
    catalog: CapabilityCatalog | None = None,
) -> Report:
    """Return a proof or counterexample for each requested plan relationship.

    Args:
        plan: Resolved molecular inputs, ordered calculations, and requirements.
        request: Independent intent; omission checks supplied relationships only.
        catalog: Scientific/input contracts; independent requests use the shared
            Psi4 catalog when omitted. Relationship-only checks keep their scope.
        limits: Bounds on each solver check; None uses Limits defaults.

    Returns:
        A report tied to the complete plan JSON. Invalid references are reported
        before solving. Premises must be satisfiable before any requirement is
        proved. Unknown results never authorize input construction. Every call
        uses a private Z3 context, including when called concurrently.
    """
    if catalog is None and request is not None:
        catalog = load_catalog()
    audit = _Audit(
        Plan.model_validate(plan),
        ScientificRequest.model_validate(request) if request else None,
        CapabilityCatalog.model_validate(catalog) if catalog else None,
        Limits.model_validate(limits) if limits else Limits(),
    )
    if len(audit.plan.steps) > audit.limits.max_steps:
        audit.diagnostics = (
            Diagnostic(
                path=("steps",),
                code="verification_budget",
                status="unknown",
                message="Plan step count exceeds the verification budget.",
            ),
        )
        return audit.report()
    audit.diagnostics = _diagnostics(audit.plan)
    if audit.diagnostics:
        return audit.report()
    audit.coverage = (
        derive_coverage(audit.plan, audit.request) if audit.request else None
    )
    audit.inspection = inspect_contracts(audit.plan)
    audit.diagnostics = (
        *audit.inspection.diagnostics,
        *(audit.coverage.diagnostics if audit.coverage else ()),
    )
    if audit.catalog is not None:
        capability_findings = check_capabilities(
            audit.plan, audit.inspection, audit.catalog
        )
        audit.capability_status = "supported"
        for status in ("invalid", "violated", "unsupported", "unknown"):
            if any(item.status == status for item in capability_findings):
                audit.capability_status = status
                break
        audit.diagnostics += capability_findings
    elif audit.request is not None or any(
        (isinstance(step, Combination) and step.extrapolation is not None)
        or (
            isinstance(step, Calculation)
            and (step.sapt is not None or step.model.environment is not None)
        )
        for step in audit.plan.steps
    ):
        audit.capability_status = "unknown"
        audit.diagnostics += (
            Diagnostic(
                path=("catalog",),
                code="capability_catalog",
                status="unknown",
                message="Supply a scientific/input capability catalog.",
            ),
        )
    if not any(item.status == "invalid" for item in audit.diagnostics):
        _solve(audit)
    return audit.report()
