"""Return compact planning summaries while full evidence stays in saved records."""

from typing import Literal

from pydantic import Field, JsonValue

from psi4_parser.formal._record import Record
from psi4_parser.formal.science import ComponentRequirement, Driver, ProductName

type RecordKind = Literal[
    "molecule",
    "request_template",
    "request",
    "capabilities",
    "plan",
    "proposal",
    "verification",
]
type ExplanationSection = Literal[
    "issues", "coverage", "assumptions", "choices", "reuse"
]
type CapabilitySection = Literal[
    "methods", "bases", "options", "components", "evidence", "products", "environments"
]


class CapabilityQuery(Record):
    """Select a bounded page of relevant scientific/input contracts."""

    section: CapabilitySection = Field(default="methods", description="Entry category.")
    name: str | None = Field(
        default=None,
        description="Exact method, basis, option key, component name, "
        "environment kind, or evidence ID.",
    )
    driver: Driver | None = Field(
        default=None, description="Optional driver filter for methods or products."
    )
    product: ProductName | None = Field(
        default=None, description="Exact named product filter for the products section."
    )
    include_products: bool = Field(
        default=False,
        description="Include full product evidence in method pages; "
        "otherwise return product_count.",
    )
    offset: int = Field(default=0, ge=0, description="Zero-based first matching entry.")
    limit: int = Field(
        default=20, ge=1, le=100, description="Maximum entries to return."
    )


class RecordReference(Record):
    """Locate a validated immutable record by kind and saved-content identity."""

    handle: str = Field(
        description="Workspace-local kind:SHA256 handle for later calls."
    )
    kind: RecordKind = Field(description="Scientific document format of this record.")
    sha256: str = Field(
        pattern=r"^[a-f0-9]{64}$", description="Hash of the saved bytes."
    )
    path: str = Field(description="Absolute JSON path; MCP files expire at shutdown.")
    bytes: int = Field(ge=0, description="Size of the complete saved JSON in bytes.")


class VerificationSummary(Record):
    """Report scientific acceptance and evidence counts without solver text."""

    reference: RecordReference = Field(description="Complete verification record.")
    runtime_policy: Literal["operator_managed"] | None = Field(
        default=None,
        description="Deployment is operator-managed, without checks or warnings.",
    )
    status: Literal["proved", "violated", "unknown", "invalid", "unsupported"] = Field(
        description="Outcome of independent verification, under listed assumptions."
    )
    capability_status: (
        Literal["supported", "violated", "unknown", "invalid", "unsupported"] | None
    ) = Field(
        default=None,
        description="Scientific/input contract coverage, separate from goal coverage; "
        "deployment is not checked. Null means checks were not completed.",
    )
    scope: Literal["relationships", "scientific_request"] = Field(
        description="Whether independent scientific intent was supplied."
    )
    request_complete: bool = Field(
        description="All independent scientific goals accepted."
    )
    coverage: dict[str, int] = Field(
        description="Goal counts by coverage status; absent statuses have count zero."
    )
    obligations: dict[str, int] = Field(
        description="Obligation counts by status; absent statuses have count zero."
    )
    diagnostic_count: int = Field(
        ge=0, description="Located contract findings in the record."
    )
    assumption_count: int = Field(
        ge=0, description="Assumptions available through explain."
    )
    verification_digest: str = Field(
        description="Identity of the verification context."
    )
    rule_version: str = Field(
        description="Scientific contract version used for this check."
    )
    capability_digest: str | None = Field(
        description="Verification's capability identity; null without a catalog."
    )
    request_digest: str | None = Field(
        description="Independent request identity; null for relationship scope."
    )
    plan_digest: str = Field(description="Verified calculation-plan identity.")
    required_components: tuple[ComponentRequirement, ...] = Field(
        default=(),
        description="Unpinned native component names, without runtime checks.",
    )


class ChoiceSummary(Record):
    """Identify a permitted model choice; full settings stay in the saved plan."""

    goal: str = Field(description="Calculation goal addressed by this choice.")
    method: str = Field(description="Selected method; full settings are in the plan.")
    basis: str = Field(description="Selected default orbital basis.")
    reference: str = Field(description="Selected SCF reference.")
    derivative_route: str = Field(description="Selected derivative route.")
    preference_rank: int = Field(ge=0, description="Zero-based allowed-choice rank.")


class ProposalSummary(Record):
    """Locate a complete proposal and summarize its finite search outcome."""

    proposal: RecordReference = Field(
        description="Complete search record and solver query."
    )
    status: Literal[
        "constructed", "invalid", "unknown", "exhausted", "no_candidate"
    ] = Field(
        description="Outcome within the declared finite alternatives and search bounds."
    )
    attempts: int = Field(
        ge=0, description="Complete candidates independently verified."
    )
    plan: RecordReference | None = Field(
        description="Accepted plan, or null on rejection."
    )
    verification: VerificationSummary | None = Field(
        description="Accepted or last rejected verification; null before any candidate."
    )
    choice_count: int = Field(
        ge=0, description="Total selected choices in the full proposal."
    )
    choices: tuple[ChoiceSummary, ...] = Field(
        description="First ten selected model choices."
    )
    calculation_count: int | None = Field(
        default=None,
        ge=0,
        description="Top-level calculation steps in the accepted "
        "plan; internal driver work is not counted. Null without an accepted plan.",
    )
    shared_call_count: int = Field(
        default=0,
        ge=0,
        description="Accepted calls covering multiple authorized goals.",
    )
    last_candidate: RecordReference | None = Field(
        default=None,
        description="Last checked rejected plan handle for located findings; "
        "null if none or an accepted plan is returned.",
    )


class ExplanationItem(Record):
    """Locate one finding or explanation within its complete saved record."""

    path: tuple[str | int, ...] = Field(
        description="Scientific input or obligation location."
    )
    record_path: tuple[str | int, ...] = Field(
        description="JSON location in the saved record."
    )
    code: str = Field(
        description="Stable finding category, or the selected explanation section."
    )
    status: str = Field(description="Finding, coverage, or assumption status.")
    message: str = Field(description="At most 1000 characters of the explanation.")
    truncated: bool = Field(
        description="The complete text is longer than this excerpt."
    )
    counterexample_count: int = Field(
        default=0,
        ge=0,
        description="Exact witnesses stored at record_path, when applicable.",
    )


class ExplanationPage(Record):
    """Page through findings, coverage, assumptions, or selected choices."""

    reference: RecordReference = Field(
        description="Complete record used for this explanation."
    )
    section: ExplanationSection = Field(description="Selected explanation section.")
    total: int = Field(
        ge=0, description="Total items in this section, including later pages."
    )
    offset: int = Field(ge=0, description="Zero-based starting item index.")
    next_offset: int | None = Field(
        description="Next index, or null after the final page."
    )
    items: tuple[ExplanationItem, ...] = Field(
        description="Bounded page in source-record order."
    )


class DiscoveryPage(Record):
    """Return a bounded slice of operation contracts or capability evidence."""

    section: str = Field(description="Selected discovery category.")
    catalog: RecordReference | None = Field(
        default=None, description="Capability snapshot identity, when queried."
    )
    total: int = Field(ge=0, description="Number of matching entries across all pages.")
    offset: int = Field(ge=0, description="Zero-based starting match index.")
    next_offset: int | None = Field(
        description="Next index, or null after the final page."
    )
    items: tuple[JsonValue, ...] = Field(
        description="Matching entries in catalog or contract order."
    )


class SchemaField(Record):
    """Describe one field without expanding its referenced model graph."""

    name: str = Field(description="JSON field name.")
    description: str = Field(
        description="Field meaning from the selected model's schema."
    )
    required: bool = Field(
        description="Whether the JSON document must supply this field."
    )


class SchemaDescription(Record):
    """Discover model fields and optionally obtain a selected, self-contained schema."""

    kind: RecordKind = Field(
        description="Root document whose definitions are inspected."
    )
    definition: str | None = Field(
        description="Selected definition; null denotes the root."
    )
    description: str = Field(description="Selected model's schema description.")
    definitions: tuple[str, ...] = Field(
        description="Definition names available under this root."
    )
    fields: tuple[SchemaField, ...] = Field(
        description="Selected or available object fields."
    )
    json_schema: dict[str, JsonValue] | None = Field(
        description="Selected schema with its reference closure; null for discovery.",
    )


class ExportSummary(Record):
    """Locate an accepted construction bundle or explain why export was rejected."""

    status: Literal["exported", "rejected"] = Field(
        description="Construction export outcome."
    )
    verification: VerificationSummary = Field(
        description="Fresh independent export verification."
    )
    directory: str | None = Field(
        description="New bundle directory, or null after rejection."
    )
    manifest_path: str | None = Field(
        description="Saved manifest path, or null after rejection."
    )
    manifest_digest: str | None = Field(
        description="Manifest SHA-256, or null after rejection."
    )
    native_inputs: tuple[str, ...] = Field(
        description="Absolute input paths, empty after rejection."
    )
    backend_version: str | None = Field(
        default=None,
        description="Lowering contract version; null when no accepted bundle exists.",
    )
    option_policy: Literal["native_defaults_per_calculation"] | None = Field(
        default=None,
        description="Native option baseline/restoration policy; null makes no claim.",
    )
    namespace_policy: Literal["restore_after_calculation"] | None = Field(
        default=None,
        description="Native scratch namespace restoration; null makes no claim.",
    )
