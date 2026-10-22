"""Describe calculations and the relationships a constructed input must satisfy."""

from typing import Annotated, Literal

from pydantic import Field

from psi4_parser.builder import ElectronicState, MoleculeDeclaration
from psi4_parser.builder.constraints import Constraint
from psi4_parser.formal._record import Record
from psi4_parser.formal.coordinate_models import CoordinateRange, CoordinateValue
from psi4_parser.formal.extrapolation_models import ExtrapolationRecipe
from psi4_parser.formal.science import (
    ComponentRequirement,
    Driver,
    ElectronicTarget,
    ExpectedQuantity,
    GeometryArtifact,
    GoalCoverage,
    Model,
    NativeProductOutput,
    NativeVariableBinding,
    ProductName,
    QuantityType,
    Rational,
    SAPTAnalysis,
    VibrationalAnalysis,
)


class Calculation(Record):
    """Request a quantity or produce an optimized geometry.

    Each calculation uses a private molecule clone. An optimization exposes its
    final geometry under its id; energy and frequency steps leave their source
    geometry unchanged. The primary quantity follows the driver's return
    contract. In particular, frequency() returns electronic energy rather
    than a thermal correction; gradients and Hessians return tensors.
    """

    kind: Literal["calculation"] = Field(
        default="calculation",
        description="Selects a calculation through a Psi4 driver.",
    )
    id: str = Field(
        min_length=1,
        description=(
            "Unique result name; an optimization also supplies geometry under "
            "this name."
        ),
    )
    driver: Driver = Field(
        description="Energy, optimization, frequency, derivative, or property driver."
    )
    sapt: SAPTAnalysis | None = Field(
        default=None,
        description="Explicit SAPT partition, basis treatment, and induction choice.",
    )
    geometry: str = Field(
        min_length=1,
        description=(
            "Earlier molecule declaration or optimization id supplying "
            "coordinates and electronic state."
        ),
    )
    model: Model = Field(
        description="Explicit method, orbital basis, and SCF reference for this step."
    )
    constraints: tuple[Constraint, ...] = Field(
        default=(),
        description="Stable-atom coordinates to constrain during optimization.",
    )
    quantity: QuantityType | None = Field(
        default=None,
        description="Expected primary product; null uses the ordinary driver product.",
    )
    derivative_route: Literal["automatic", "analytic", "finite_difference"] = Field(
        default="automatic", description="Derivative route to request, if applicable."
    )
    properties: tuple[str, ...] = Field(
        default=(), description="Property names explicitly requested from the driver."
    )
    satisfies: tuple[str, ...] = Field(
        default=(), description="Scientific-request goal IDs addressed by this step."
    )
    analysis: VibrationalAnalysis | None = Field(
        default=None,
        description="Full-frequency projection and thermal settings; "
        "null uses defaults without establishing a thermal context.",
    )


class Product(Record):
    """Name an expected product of a preceding calculation, without reading results."""

    kind: Literal["product"] = Field(
        default="product",
        description="Declare a named product for a separate result consumer.",
    )
    id: str = Field(min_length=1, description="Unique expected quantity identity.")
    calculation: str = Field(
        min_length=1,
        description="Preceding calculation that must produce this quantity.",
    )
    name: ProductName = Field(
        description="Named product, such as harmonic_frequencies or gibbs_correction."
    )
    electronic_target: ElectronicTarget | None = Field(
        default=None,
        description="Required ordered root for an excited-state product; "
        "null for ordinary products.",
    )
    quantity: QuantityType | None = Field(
        default=None,
        description="Required type; null derives canonical units, layout, "
        "numeric domain, and producing calculation frame.",
    )
    satisfies: tuple[str, ...] = Field(
        default=(),
        description="Independent product goal IDs addressed by this declaration.",
    )


class EnergyTerm(Record):
    """Add an exact rational multiple of an earlier scalar quantity."""

    result: str = Field(
        min_length=1,
        description="Earlier scalar quantity or expression referenced by this term.",
    )
    coefficient: int | Rational = Field(
        description="Signed exact multiplier; repeated terms are added algebraically."
    )


class Combination(Record):
    """Combine earlier scalar quantities with exact rational coefficients."""

    kind: Literal["combination"] = Field(
        default="combination",
        description="Selects an energy sum or difference.",
    )
    id: str = Field(
        min_length=1,
        description="Unique name for the resulting scalar quantity.",
    )
    terms: tuple[EnergyTerm, ...] = Field(
        min_length=1,
        description="Earlier scalar results and their signed exact multipliers.",
    )
    quantity: QuantityType | None = Field(
        default=None, description="Meaning and unit of the combined scalar quantity."
    )
    extrapolation: ExtrapolationRecipe | None = Field(
        default=None,
        description="Independent basis-limit model; null makes no "
        "basis-extrapolation claim.",
    )
    satisfies: tuple[str, ...] = Field(
        default=(),
        description="Scientific-request expression goals addressed by this step.",
    )


class UsesGeometry(Record):
    """Require a calculation to consume a particular input or optimized geometry."""

    kind: Literal["uses_geometry"] = Field(
        default="uses_geometry",
        description="Checks the source geometry of a calculation.",
    )
    calculation: str = Field(
        min_length=1, description="Calculation id whose input geometry must be checked."
    )
    geometry: str = Field(
        min_length=1,
        description="Molecule declaration or optimization id required as the source.",
    )


class SameGeometry(Record):
    """Require two calculations to consume the same geometry and electronic state.

    Equality means a shared input or optimization result, not numerical similarity
    between independently declared structures.
    """

    kind: Literal["same_geometry"] = Field(
        default="same_geometry",
        description="Checks that two calculations consume the same geometry source.",
    )
    calculations: tuple[str, str] = Field(
        description="The two calculation ids whose input geometries must agree."
    )


class SameModel(Record):
    """Require two calculations to use the same method, basis, and reference."""

    kind: Literal["same_model"] = Field(
        default="same_model",
        description="Checks method, basis, and SCF reference equality.",
    )
    calculations: tuple[str, str] = Field(
        description="The two calculation ids whose explicit models must agree."
    )


class EnergyFormula(Record):
    """Require an energy result to equal a stated linear energy formula.

    The checker expands nested combinations and proves equality for all possible
    energy values over the real numbers. Floating-point roundoff is
    outside this algebraic claim. Terms may reference any declared energy result.
    """

    kind: Literal["energy_formula"] = Field(
        default="energy_formula",
        description="Checks a result against an independently supplied energy formula.",
    )
    result: str = Field(
        min_length=1,
        description=("Calculation or combination id whose energy formula is checked."),
    )
    terms: tuple[EnergyTerm, ...] = Field(
        min_length=1,
        description=(
            "Expected energy terms, independent of the combination being checked."
        ),
    )


class Subsystem(Record):
    """Select real fragments and retain all other fragments as ghost basis centers.

    This constructs a subsystem in the complete parent basis. It retains atom
    IDs and parent coordinate provenance, including future optimized coordinates.
    """

    kind: Literal["subsystem"] = Field(
        default="subsystem", description="Selects a subsystem in the full parent basis."
    )
    id: str = Field(
        min_length=1, description="New subsystem geometry and system identity."
    )
    geometry: str = Field(
        min_length=1, description="Earlier parent geometry with named fragments."
    )
    real_fragments: tuple[str, ...] = Field(
        min_length=1, description="Parent fragment names to retain as real nuclei."
    )
    state: ElectronicState = Field(
        description="Explicit overall subsystem charge and multiplicity."
    )
    satisfies: tuple[str, ...] = Field(
        default=(), description="Scientific subsystem goal IDs addressed by this step."
    )


type Step = Annotated[
    Calculation | Combination | Subsystem | Product,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]
type Requirement = Annotated[
    UsesGeometry
    | SameGeometry
    | SameModel
    | EnergyFormula
    | CoordinateValue
    | CoordinateRange,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Plan(Record):
    """Construct a sequence of calculations and prove specified relationships.

    Declare molecules first, then steps in execution order. Names must be unique
    across molecules and steps. Requirements describe the intended relationships
    independently of the implementation. Use verify() to inspect them, build()
    to obtain a checked builder job, or render() to produce Psi4 input.
    """

    schema_version: Literal["2"] = Field(
        default="2", description="Scientific-plan serialization format version."
    )
    molecules: tuple[MoleculeDeclaration, ...] = Field(
        min_length=1,
        description=(
            "Named molecular inputs, with resolved geometry and an explicit "
            "overall electronic state."
        ),
    )
    steps: tuple[Step, ...] = Field(
        min_length=1,
        description=(
            "Calculations and energy combinations in execution order; references "
            "must precede use."
        ),
    )
    requirements: tuple[Requirement, ...] = Field(
        min_length=1,
        description=(
            "Relationships to prove; at least one explicit requirement is required."
        ),
    )


class Limits(Record):
    """Bound each solver check; an exhausted limit produces an unknown result."""

    timeout_ms: int = Field(
        default=1000,
        ge=1,
        le=2**32 - 1,
        description=(
            "Maximum milliseconds for each solver check, including premise consistency."
        ),
    )
    resource_limit: int = Field(
        default=0,
        ge=0,
        le=2**32 - 1,
        description="Z3 resource limit per check; zero leaves this limit unrestricted.",
    )
    max_steps: int = Field(
        default=10000,
        ge=1,
        description="Maximum plan steps inspected in one verification.",
    )
    max_obligations: int = Field(
        default=10000,
        ge=1,
        description="Maximum caller and derived solver obligations.",
    )
    total_timeout_ms: int = Field(
        default=30000,
        ge=1,
        description="Total verification time budget in milliseconds.",
    )


class Diagnostic(Record):
    """Locate a plan reference or geometry that prevents verification."""

    path: tuple[str | int, ...] = Field(
        description="Field names and zero-based indices locating the problem."
    )
    message: str = Field(description="Reason the supplied plan cannot be verified.")
    code: str = Field(
        default="structure", description="Stable rule code for targeted repairs."
    )
    status: Literal["invalid", "violated", "unsupported", "unknown"] = Field(
        default="invalid",
        description="Whether the issue is malformed, false, or uncovered.",
    )


class Witness(Record):
    """Show an actual or expected symbolic value in a counterexample."""

    name: str = Field(
        description="Meaning of this counterexample value, such as actual or expected."
    )
    value: str = Field(
        description="Value expressed in Z3 notation; geometry sources are quoted names."
    )


class Obligation(Record):
    """Report one requirement and its replayable counterexample query.

    An unsatisfiable query establishes that the requirement cannot be violated
    under the encoded plan semantics. A satisfiable query supplies a witness.
    """

    index: int = Field(
        ge=0,
        description="Index among caller requirements followed by derived requirements.",
    )
    path: tuple[str | int, ...] = Field(
        default=(), description="Caller or derived-requirement path for this check."
    )
    status: Literal["proved", "violated", "unknown"] = Field(
        description=(
            "Whether the requirement follows, has a counterexample, "
            "or remains undecided."
        )
    )
    message: str = Field(
        description=(
            "Relationship checked, or the solver's reason for an undecided check."
        )
    )
    smt2: str = Field(
        description="SMT-LIB query asserting the plan and a violation; replay with Z3."
    )
    proof: str | None = Field(
        default=None,
        description=(
            "Z3 proof expression for an unsatisfiable query; null for other outcomes."
        ),
    )
    counterexample: tuple[Witness, ...] = Field(
        default=(),
        description="Actual and expected values when the requirement can be violated.",
    )


class Report(Record):
    """Describe exactly which relationships were proved for one immutable plan.

    Proved means all supplied requirements follow from the encoded plan. It
    assumes successful Psi4 calls with their documented molecule behavior and
    the stated method settings. It does not establish method availability,
    convergence, physical accuracy, or numerical roundoff bounds.
    """

    status: Literal["proved", "violated", "unknown", "invalid", "unsupported"] = Field(
        description="Overall result; only proved permits build() or render()."
    )
    runtime_policy: Literal["operator_managed"] | None = Field(
        default=None,
        description="Runtime availability, dependencies, and versions are left to "
        "the operator; null means an older record did not state this policy.",
    )
    capability_status: (
        Literal["supported", "violated", "unknown", "invalid", "unsupported"] | None
    ) = Field(
        default=None,
        description="Scientific/input contract coverage, separately from goal "
        "coverage; deployment is not checked. Null means checks were not completed.",
    )
    plan_digest: str = Field(
        description="SHA-256 of the complete Plan JSON checked by this report."
    )
    solver_version: str = Field(description="Z3 runtime version used for these checks.")
    diagnostics: tuple[Diagnostic, ...] = Field(
        default=(),
        description=(
            "Structural problems that prevent creating a faithful solver model."
        ),
    )
    obligations: tuple[Obligation, ...] = Field(
        default=(),
        description=(
            "One result per supplied requirement when the plan model is consistent."
        ),
    )
    assumptions: tuple[str, ...] = Field(
        description="Execution and mathematical assumptions that limit the claims."
    )
    rule_version: str = Field(
        default="legacy/1", description="Scientific contract implementation identity."
    )
    geometries: tuple[GeometryArtifact, ...] = Field(
        default=(), description="Derived known and future geometry provenance."
    )
    quantities: tuple[ExpectedQuantity, ...] = Field(
        default=(),
        description="Expected products only; these records contain no results.",
    )
    native_outputs: tuple[NativeProductOutput, ...] = Field(
        default=(),
        description="Native product files for separate execution and collection.",
    )
    native_variables: tuple[NativeVariableBinding, ...] = Field(
        default=(),
        description="Transient native product declarations for an external consumer; "
        "no collection or output preservation is performed.",
    )
    required_components: tuple[ComponentRequirement, ...] = Field(
        default=(),
        description="Native component names used by the plan, without runtime checks.",
    )
    request_digest: str | None = Field(
        default=None,
        description="SHA-256 of the independent scientific request, if checked.",
    )
    scope: Literal["relationships", "scientific_request"] = Field(
        default="relationships",
        description="Whether mandatory scientific goal coverage was checked.",
    )
    coverage: tuple[GoalCoverage, ...] = Field(
        default=(), description="Implementing steps for each mandatory scientific goal."
    )
    request_complete: bool = Field(
        default=False,
        description="Whether the complete declared request passed all checks.",
    )
    capability_digest: str | None = Field(
        default=None,
        description="SHA-256 of the supplied application capability catalog.",
    )
    limits: Limits = Field(
        default_factory=Limits,
        description="Resource bounds used for this verification.",
    )
    verification_digest: str = Field(
        default="",
        description="SHA-256 of the plan, intent, catalog, rules, solver, and limits.",
    )
