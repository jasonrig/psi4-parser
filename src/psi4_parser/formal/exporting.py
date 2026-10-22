"""Export verified scientific plans and native inputs for a separate consumer."""

from pathlib import Path
from typing import Literal

from pydantic import Field

from psi4_parser import builder
from psi4_parser._files import atomic_replace
from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import CapabilityCatalog
from psi4_parser.formal.catalogs import load_catalog
from psi4_parser.formal.construction import VerificationError, _lower
from psi4_parser.formal.intent import ScientificRequest
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Limits,
    Plan,
    Product,
    Report,
    Subsystem,
)
from psi4_parser.formal.science import (
    ComponentRequirement,
    ExpectedQuantity,
    GeometryArtifact,
    GoalCoverage,
    NativeProductOutput,
    NativeVariableBinding,
)
from psi4_parser.formal.verification import verify


class Dependency(Record):
    """Describe a geometry or quantity handoff without scheduling its execution."""

    consumer: str = Field(
        description="Calculation or expression step that needs an artifact."
    )
    artifact: str = Field(
        description="Molecular input, future geometry, or quantity ID."
    )
    kind: Literal["geometry", "quantity"] = Field(
        description="Scientific type of dependency."
    )


class BundleManifest(Record):
    """Describe expected artifacts, dependencies, formulas, and bundle files."""

    runtime_policy: Literal["operator_managed"] | None = Field(
        default=None,
        description="No runtime dependency, binary, or version checks or warnings; "
        "null means an older bundle did not state this policy.",
    )
    option_policy: Literal["native_defaults_per_calculation"] | None = Field(
        default=None,
        description="Each call starts from native defaults and restores captured "
        "option values/changed flags afterward; null records no isolation claim.",
    )
    namespace_policy: Literal["restore_after_calculation"] | None = Field(
        default=None,
        description="Restore the scratch namespace captured at each call's entry; "
        "null makes no namespace-restoration claim.",
    )
    required_components: tuple[ComponentRequirement, ...] = Field(
        default=(),
        description="Native component names used by these inputs; "
        "availability is not checked and versions are not pinned.",
    )
    files: tuple[str, ...] = Field(
        description="Payload paths relative to the bundle directory."
    )
    native_inputs: tuple[str, ...] = Field(
        description="Native input paths in dependency order."
    )
    native_outputs: tuple[NativeProductOutput, ...] = Field(
        default=(),
        description="Declared native files to collect after separate execution.",
    )
    native_variables: tuple[NativeVariableBinding, ...] = Field(
        default=(),
        description="Transient native QCVariable locations for a separate consumer; "
        "the generated input does not collect or snapshot them.",
    )
    dependencies: tuple[Dependency, ...] = Field(
        description="Required geometry and quantity relationships."
    )
    geometries: tuple[GeometryArtifact, ...] = Field(
        description="Known and future geometry provenance."
    )
    quantities: tuple[ExpectedQuantity, ...] = Field(
        description="Expected products and meanings, with no numerical results."
    )
    expressions: tuple[Combination, ...] = Field(
        description="Exact symbolic recipes for a separate result consumer."
    )
    products: tuple[Product, ...] = Field(
        default=(),
        description="Named products for a separate consumer; "
        "no values or parsers are included.",
    )
    goal_coverage: tuple[GoalCoverage, ...] = Field(
        default=(),
        description="Accepted request goals and their actual implementing steps, "
        "including shared calls; empty in older bundles.",
    )
    assumptions: tuple[str, ...] = Field(
        description="Assumptions that qualify the construction guarantees."
    )


class ExportedBundle(Record):
    """Locate a complete construction bundle and its scientific handoffs."""

    directory: str = Field(
        description="Absolute directory containing the saved construction bundle."
    )
    manifest: BundleManifest = Field(
        description="Expected artifacts, dependencies, products, and formulas."
    )


def _dependencies(plan: Plan) -> tuple[Dependency, ...]:
    dependencies: list[Dependency] = []
    for step in plan.steps:
        if isinstance(step, Product):
            dependencies.append(
                Dependency(consumer=step.id, artifact=step.calculation, kind="quantity")
            )
        elif isinstance(step, (Calculation, Subsystem)):
            dependencies.append(
                Dependency(consumer=step.id, artifact=step.geometry, kind="geometry")
            )
        else:
            dependencies.extend(
                Dependency(consumer=step.id, artifact=term.result, kind="quantity")
                for term in step.terms
            )
    return tuple(dependencies)


def _manifest(
    plan: Plan,
    report: Report,
    files: tuple[str, ...],
) -> BundleManifest:
    if not report.request_complete:
        raise ValueError(
            "A construction bundle requires request and capability verification"
        )
    return BundleManifest(
        runtime_policy="operator_managed",
        option_policy="native_defaults_per_calculation",
        namespace_policy="restore_after_calculation",
        required_components=report.required_components,
        files=files,
        native_inputs=("inputs/workflow.dat",),
        native_outputs=report.native_outputs,
        native_variables=report.native_variables,
        dependencies=_dependencies(plan),
        geometries=report.geometries,
        quantities=report.quantities,
        expressions=tuple(step for step in plan.steps if isinstance(step, Combination)),
        products=tuple(step for step in plan.steps if isinstance(step, Product)),
        goal_coverage=report.coverage,
        assumptions=(
            *report.assumptions,
            "The builder preserves declared operations and dependencies; "
            "this lowering implementation is tested rather than formally proved.",
            "Native inputs retain future geometries in memory. "
            "Symbolic expressions are recipes for a separate result consumer.",
        ),
    )


def export_bundle(
    plan: Plan,
    request: ScientificRequest,
    catalog: CapabilityCatalog | None = None,
    destination: Path | None = None,
    *,
    limits: Limits | None = None,
) -> ExportedBundle:
    """Save a checked request, plan, proof report, manifest, and native Psi4 input.

    Named product recipes and symbolic expressions remain in the manifest.
    Required native frequency records have explicit writer labels and expected
    file declarations, without retrieval or validation. The native input contains
    calculations and geometry handoffs without evaluating those expressions.
    The function verifies and compiles before creating the destination. It
    writes the manifest last; an I/O failure may leave an incomplete directory.

    Args:
        plan: Proposed calculation graph to verify independently.
        request: Scientific work that every accepted plan must address.
        catalog: Scientific/input contracts; omission uses the shared Psi4 catalog.
        destination: Required new bundle directory whose parent already exists.
        limits: Verification bounds; null uses the standard limits.

    Returns:
        Absolute bundle path and its scientific handoff manifest.

    Raises:
        ValueError: No destination was supplied.
        VerificationError: The plan is not accepted against the independent request.
        FileExistsError: The destination already exists; files are never overwritten.
        OSError: The bundle directory or one of its files cannot be written.
        builder.CompilationError: The backend cannot compile the accepted plan.
    """  # noqa: DOC502 - Verification and builder compilation propagate failures.
    plan = Plan.model_validate(plan)
    request = ScientificRequest.model_validate(request)
    if destination is None:
        raise ValueError("Supply a destination for the construction bundle")
    catalog = (
        CapabilityCatalog.model_validate(catalog)
        if catalog is not None
        else load_catalog()
    )
    report = verify(plan, request=request, catalog=catalog, limits=limits)
    if not report.request_complete:
        raise VerificationError(report)
    source = builder.render_job(_lower(plan, expressions=False))
    payloads = {
        "scientific-request.json": request.model_dump_json(indent=2) + "\n",
        "calculation-plan.json": plan.model_dump_json(indent=2) + "\n",
        "capabilities.json": catalog.model_dump_json(indent=2) + "\n",
        "verification.json": report.model_dump_json(indent=2) + "\n",
        "inputs/workflow.dat": source,
    }
    files = tuple(payloads)
    manifest = _manifest(plan, report, files)
    manifest_bytes = (manifest.model_dump_json(indent=2) + "\n").encode()
    destination = destination.absolute()
    destination.mkdir(mode=0o700)
    (destination / "inputs").mkdir(mode=0o700)
    for name, content in payloads.items():
        atomic_replace(destination / name, content.encode(), mode=0o600)
    atomic_replace(destination / "manifest.json", manifest_bytes, mode=0o600)
    return ExportedBundle(directory=str(destination), manifest=manifest)
