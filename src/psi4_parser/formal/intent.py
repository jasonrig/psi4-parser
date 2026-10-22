"""State desired calculations independently from a proposed implementation plan."""

from typing import Annotated, Literal

from pydantic import Field

from psi4_parser.builder import ElectronicState, MoleculeDeclaration
from psi4_parser.builder.constraints import Constraint
from psi4_parser.formal._record import Record
from psi4_parser.formal.extrapolation_models import ExtrapolationRecipe
from psi4_parser.formal.models import Requirement
from psi4_parser.formal.science import (
    Driver,
    ElectronicTarget,
    Model,
    ProductName,
    QuantityType,
    Rational,
    SAPTAnalysis,
    VibrationalAnalysis,
)


class CalculationGoal(Record):
    """Require one calculation using a declared geometry and permitted model.

    A geometry may name an input molecule or a preceding optimization goal.
    Supplying multiple models explicitly permits the planner to choose among
    them; a single model fixes that scientific choice.
    """

    kind: Literal["calculate"] = Field(
        default="calculate",
        description="Require a calculation and its expected products.",
    )
    id: str = Field(min_length=1, description="Unique scientific goal identity.")
    driver: Driver = Field(description="Operation needed to address this goal.")
    geometry: str = Field(
        min_length=1, description="Input molecule or preceding optimization goal ID."
    )
    models: tuple[Model, ...] = Field(
        min_length=1,
        description="Permitted models in preference order; one entry fixes the model.",
    )
    quantity: QuantityType | None = Field(
        default=None,
        description="Required primary quantity; null uses the driver default.",
    )
    constraints: tuple[Constraint, ...] = Field(
        default=(),
        description="Coordinates that the requested optimization must constrain.",
    )
    derivative_routes: tuple[
        Literal["automatic", "analytic", "finite_difference"], ...
    ] = Field(
        default=("automatic",),
        min_length=1,
        description="Permitted derivative routes in preference order.",
    )
    properties: tuple[str, ...] = Field(
        default=(), description="Required property names for the properties driver."
    )
    reason: str = Field(
        default="Requested calculation",
        description="Scientific purpose shown in explanations.",
    )
    analysis: VibrationalAnalysis | None = Field(
        default=None,
        description="Required full-frequency projection and thermal settings.",
    )
    reuse_group: str | None = Field(
        default=None,
        min_length=1,
        pattern=r"\S",
        description="Goals with the same non-null group may share a matching call. "
        "Null requires a separate top-level driver call. Sharing is permission, "
        "not a requirement or a claim of numerical equivalence.",
    )
    sapt: SAPTAnalysis | None = Field(
        default=None,
        description="Required SAPT partition and basis/induction treatment; "
        "null makes no SAPT operation claim.",
    )


class ProductGoal(Record):
    """Require a named product with provenance from a preceding calculation goal."""

    kind: Literal["product"] = Field(
        default="product", description="Require a named secondary calculation product."
    )
    id: str = Field(
        min_length=1, description="Unique scientific product goal identity."
    )
    calculation: str = Field(
        min_length=1,
        description="Preceding calculation goal that must supply this product.",
    )
    name: ProductName = Field(
        description="Named product required separately from the primary return value."
    )
    electronic_target: ElectronicTarget | None = Field(
        default=None,
        description="Independent root selector for an excited-state product; "
        "null for ordinary products.",
    )
    quantity: QuantityType | None = Field(
        default=None,
        description="Required canonical type and frame; "
        "null derives the built-in product type.",
    )
    reason: str = Field(
        default="Requested calculation product",
        description="Scientific purpose of requiring this product.",
    )


class GoalTerm(Record):
    """Reference a preceding requested scalar quantity in an exact formula."""

    goal: str = Field(
        min_length=1, description="Earlier calculation or expression goal ID."
    )
    coefficient: int | Rational = Field(description="Signed exact formula coefficient.")


class ExpressionGoal(Record):
    """Require a specified scalar expression without evaluating its future values."""

    kind: Literal["expression"] = Field(
        default="expression",
        description="Require an exact combination of requested quantities.",
    )
    id: str = Field(min_length=1, description="Unique scientific expression identity.")
    terms: tuple[GoalTerm, ...] = Field(
        min_length=1,
        description="Earlier goal quantities and their exact coefficients.",
    )
    quantity: QuantityType = Field(
        description="Required physical meaning and scalar unit."
    )
    extrapolation: ExtrapolationRecipe | None = Field(
        default=None,
        description="Required basis-limit model, separate from formula "
        "coefficients; null requests an ordinary expression.",
    )
    reason: str = Field(
        default="Requested expression",
        description="Scientific purpose shown in explanations.",
    )


class SubsystemGoal(Record):
    """Require selected real fragments in the complete parent basis."""

    kind: Literal["subsystem"] = Field(
        default="subsystem", description="Require a subsystem in the full parent basis."
    )
    id: str = Field(min_length=1, description="Unique subsystem goal identity.")
    geometry: str = Field(
        min_length=1,
        description="Input or preceding geometry goal supplying the parent.",
    )
    real_fragments: tuple[str, ...] = Field(
        min_length=1, description="Fragment names that must retain real nuclei."
    )
    state: ElectronicState = Field(
        description="Required subsystem charge and multiplicity."
    )
    reason: str = Field(
        default="Requested full-basis subsystem",
        description="Scientific purpose of the subsystem.",
    )


type Goal = Annotated[
    CalculationGoal | ExpressionGoal | SubsystemGoal | ProductGoal,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class ScientificRequest(Record):
    """Describe finite scientific work and derive mandatory plan obligations.

    Goals compose through stable references. Each calculation, dependency,
    model restriction, expected quantity, and formula becomes a required check.
    Additional relations use molecular input or goal IDs rather than implementation
    step names. Coordinate targets can constrain prepared scan inputs and the
    declared behavior of future optimized geometries.
    """

    schema_version: Literal["1"] = Field(
        default="1", description="Scientific-request serialization format version."
    )
    molecules: tuple[MoleculeDeclaration, ...] = Field(
        min_length=1, description="Exact molecular inputs the plan must preserve."
    )
    goals: tuple[Goal, ...] = Field(
        min_length=1,
        description="Required calculations and expressions in dependency order.",
    )
    relations: tuple[Requirement, ...] = Field(
        default=(),
        description=(
            "Additional mandatory relationships using input or scientific goal IDs. "
            "References must identify the geometry, calculation, or scalar quantity "
            "required by each relationship."
        ),
    )
