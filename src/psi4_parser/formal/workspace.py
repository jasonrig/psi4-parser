"""Save immutable scientific records and expose compact construction workflows."""

import hashlib
import re
from collections import Counter
from pathlib import Path

from pydantic import JsonValue

from psi4_parser._files import atomic_replace
from psi4_parser.builder.components import MoleculeDeclaration
from psi4_parser.builder.molecular import Molecule
from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import (
    CapabilityCatalog,
    MethodCapability,
    discover_products,
)
from psi4_parser.formal.catalogs import load_catalog
from psi4_parser.formal.construction import VerificationError
from psi4_parser.formal.discovery import RECORD_MODELS, page_end, record_value
from psi4_parser.formal.exporting import export_bundle
from psi4_parser.formal.intent import ScientificRequest
from psi4_parser.formal.interface_models import (
    CapabilityQuery,
    ChoiceSummary,
    DiscoveryPage,
    ExplanationItem,
    ExplanationPage,
    ExplanationSection,
    ExportSummary,
    ProposalSummary,
    RecordKind,
    RecordReference,
    VerificationSummary,
)
from psi4_parser.formal.models import Calculation, Limits, Plan, Report
from psi4_parser.formal.planning import Proposal, SearchLimits, propose
from psi4_parser.formal.reuse import PlanningPreferences
from psi4_parser.formal.stored_inputs import RequestTemplate, StoredMolecule
from psi4_parser.formal.verification import verify

_HANDLE = re.compile(
    r"^(molecule|request_template|request|capabilities|plan|proposal|verification):"
    r"([a-f0-9]{64})$"
)
_CHOICE_PREVIEW = 10
_TEXT_PREVIEW = 1000
_DEFAULT_RECORD_BYTES = 16 * 1024 * 1024


def _kind(value: str) -> RecordKind:
    match value:
        case (
            "molecule"
            | "request_template"
            | "request"
            | "capabilities"
            | "plan"
            | "proposal"
            | "verification"
        ):
            return value
        case _:
            raise ValueError(f"Unknown scientific record kind: {value}")


def _item(  # noqa: PLR0913 - Mirrors the explanation record's distinct fields.
    *,
    path: tuple[str | int, ...],
    record_path: tuple[str | int, ...],
    code: str,
    status: str,
    message: str,
    counterexamples: int = 0,
) -> ExplanationItem:
    return ExplanationItem(
        path=path,
        record_path=record_path,
        code=code,
        status=status,
        message=message[:_TEXT_PREVIEW],
        truncated=len(message) > _TEXT_PREVIEW,
        counterexample_count=counterexamples,
    )


def _report_items(
    report: Report, section: ExplanationSection, prefix: tuple[str | int, ...]
) -> tuple[ExplanationItem, ...]:
    if section == "assumptions":
        return tuple(
            _item(
                path=(),
                record_path=(*prefix, "assumptions", index),
                code="assumption",
                status="assumed",
                message=message,
            )
            for index, message in enumerate(report.assumptions)
        )
    if section == "coverage":
        return tuple(
            _item(
                path=("goals", entry.goal),
                record_path=(*prefix, "coverage", index),
                code="goal_coverage",
                status=entry.status,
                message=(
                    f"Goal {entry.goal}; implementing steps: {', '.join(entry.steps)}"
                ),
            )
            for index, entry in enumerate(report.coverage)
        )
    findings = [
        _item(
            path=entry.path,
            record_path=(*prefix, "diagnostics", index),
            code=entry.code,
            status=entry.status,
            message=entry.message,
        )
        for index, entry in enumerate(report.diagnostics)
    ]
    findings.extend(
        _item(
            path=entry.path,
            record_path=(*prefix, "obligations", index),
            code="solver_obligation",
            status=entry.status,
            message=entry.message,
            counterexamples=len(entry.counterexample),
        )
        for index, entry in enumerate(report.obligations)
        if entry.status != "proved"
    )
    return tuple(findings)


def _proposal_items(
    proposal: Proposal, section: ExplanationSection
) -> tuple[ExplanationItem, ...]:
    if section == "reuse":
        indices = (
            {step.id: index for index, step in enumerate(proposal.plan.steps)}
            if proposal.plan
            else {}
        )
        return tuple(
            _item(
                path=("steps", indices[entry.calculation], "satisfies")
                if entry.calculation in indices
                else (),
                record_path=("reuses", index),
                code="permitted_reuse",
                status="selected",
                message=(
                    f"Call {entry.calculation} covers {len(entry.goals)} authorized "
                    f"goals: {', '.join(entry.goals[:_CHOICE_PREVIEW])}"
                )
                + (
                    "; remaining goals are in the saved record."
                    if len(entry.goals) > _CHOICE_PREVIEW
                    else "."
                ),
            )
            for index, entry in enumerate(proposal.reuses)
        )
    if section == "choices":
        return tuple(
            _item(
                path=("goals", entry.goal),
                record_path=("choices", index),
                code="permitted_choice",
                status="selected",
                message=(
                    f"{entry.model.method}/{entry.model.basis}/"
                    f"{entry.model.reference}; route {entry.derivative_route}; "
                    f"allowed rank {entry.preference_rank}"
                ),
            )
            for index, entry in enumerate(proposal.choices)
        )
    findings = (
        _report_items(proposal.report, section, ("report",)) if proposal.report else ()
    )
    if section != "issues":
        return findings
    seen = (
        {
            (entry.path, entry.message, entry.status)
            for entry in proposal.report.diagnostics
        }
        | {
            (entry.path, entry.message, entry.status)
            for entry in proposal.report.obligations
            if entry.status != "proved"
        }
        if proposal.report
        else set()
    )
    extra = tuple(
        _item(
            path=entry.path,
            record_path=("diagnostics", index),
            code=entry.code,
            status=entry.status,
            message=entry.message,
        )
        for index, entry in enumerate(proposal.diagnostics)
        if (entry.path, entry.message, entry.status) not in seen
    )
    return (*extra, *findings)


def _capability_entry(item: Record, query: CapabilityQuery) -> JsonValue:
    if isinstance(item, MethodCapability) and not query.include_products:
        value = record_value(item, exclude={"products"})
        if isinstance(value, dict):
            value["product_count"] = len(item.products)
        return value
    return record_value(item)


class PlanningWorkspace:
    """Keep checked records on disk and pass their content hashes between calls.

    Imported files are copied into this directory after structural validation.
    Every read checks the saved bytes against its handle. Handles are local to
    this workspace; they do not grant scientific acceptance. CLI workspaces are
    persistent; an MCP workspace is removed when its server shuts down.

    Attributes:
        directory: Absolute workspace directory, containing immutable JSON records.
        max_record_bytes: Positive size limit for each imported or generated record.
    """

    def __init__(
        self, directory: Path, *, max_record_bytes: int = _DEFAULT_RECORD_BYTES
    ) -> None:
        """Open or create a planning workspace without changing existing records.

        Args:
            directory: Workspace path whose parent exists.
            max_record_bytes: Positive per-record byte limit, default 16 MiB.

        Raises:
            ValueError: The record byte limit is not positive.
        """
        if max_record_bytes < 1:
            raise ValueError("max_record_bytes must be positive")
        self.directory = directory.absolute()
        self.max_record_bytes = max_record_bytes
        self.directory.mkdir(mode=0o700, exist_ok=True)
        self._records = self.directory / "records"
        self._records.mkdir(mode=0o700, exist_ok=True)

    def _bounded(self, path: Path) -> bytes:
        with path.open("rb") as stream:
            content = stream.read(self.max_record_bytes + 1)
        if len(content) > self.max_record_bytes:
            raise ValueError(f"Record exceeds the {self.max_record_bytes}-byte limit")
        return content

    def _save(self, kind: RecordKind, record: Record) -> RecordReference:
        content = (record.model_dump_json(indent=2) + "\n").encode()
        if len(content) > self.max_record_bytes:
            raise ValueError(f"Record exceeds the {self.max_record_bytes}-byte limit")
        digest = hashlib.sha256(content).hexdigest()
        destination = self._records / f"{kind}-{digest}.json"
        if destination.exists():
            if self._bounded(destination) != content:
                raise ValueError("Saved record content no longer matches its handle")
        else:
            atomic_replace(destination, content, mode=0o600)
        return RecordReference(
            handle=f"{kind}:{digest}",
            kind=kind,
            sha256=digest,
            path=str(destination),
            bytes=len(content),
        )

    def import_json(self, kind: RecordKind, source: str | bytes) -> RecordReference:
        """Validate and save a scientific JSON record without running calculations.

        Args:
            kind: Expected document format, distinct from builder JobSpec JSON.
            source: Complete JSON text or UTF-8 bytes, within the record-size limit.

        Returns:
            Reusable content handle and complete saved JSON path.

        Raises:
            ValueError: The JSON is invalid or exceeds the record byte limit.
        """
        content = source.encode() if isinstance(source, str) else source
        if len(content) > self.max_record_bytes:
            raise ValueError(f"Record exceeds the {self.max_record_bytes}-byte limit")
        record = RECORD_MODELS[kind].model_validate_json(content)
        return self._save(kind, record)

    def import_file(self, kind: RecordKind, path: Path) -> RecordReference:
        """Return a handle to a validated copy of a bounded local JSON file."""
        return self.import_json(kind, self._bounded(path))

    def load_catalog(self, catalog_id: str = "psi4") -> RecordReference:
        """Save bundled source contracts without inspecting an execution host.

        Args:
            catalog_id: Shared collection name; defaults to psi4.

        Returns:
            Reusable evidence handle without importing or launching Psi4.

        Raises:
            ValueError: The name or packaged evidence is invalid.
        """  # noqa: DOC502 - Delegates named-catalog and packaged-evidence validation.
        return self._save("capabilities", load_catalog(catalog_id))

    def save_molecule(self, geometry: Molecule) -> RecordReference:
        """Save an exact molecule once and return a reusable content handle.

        Args:
            geometry: Complete builder molecule; naming occurs in each request.

        Returns:
            Immutable molecule record reference. Saving is structural validation,
            not scientific acceptance of the molecule or a calculation.
        """
        return self._save("molecule", StoredMolecule(geometry=geometry))

    def materialize_request(self, template: str) -> RecordReference:
        """Assemble and save a complete independent request from molecule handles.

        Every referenced molecular record is read and hash checked. Coordinates,
        states, fragments, and metadata are copied into the resulting request;
        subsequent planning and export need no template or molecule handles.

        Args:
            template: Saved request_template handle in this workspace.

        Returns:
            Self-contained request reference for propose, verify, and export.

        Raises:
            ValueError: A handle has the wrong kind, saved bytes changed, or the
                assembled request exceeds this workspace's record-size limit.
            OSError: A referenced record is missing or unreadable.
        """  # noqa: DOC502 - Delegates record, hash, and size validation.
        draft = self._read(template, "request_template", RequestTemplate)
        molecules: list[MoleculeDeclaration] = []
        molecular_bytes = 0
        for binding in draft.molecules:
            declaration = MoleculeDeclaration(
                name=binding.name,
                geometry=self._read(
                    binding.molecule, "molecule", StoredMolecule
                ).geometry,
            )
            # Compact molecular JSON is a lower bound on the complete saved
            # request. Stop expansion before repeated handles can grow it without
            # bound; _save also checks the final indented document including goals.
            molecular_bytes += len(declaration.model_dump_json().encode())
            if molecular_bytes > self.max_record_bytes:
                raise ValueError(
                    f"Record exceeds the {self.max_record_bytes}-byte limit"
                )
            molecules.append(declaration)
        return self._save(
            "request",
            ScientificRequest(
                molecules=tuple(molecules), goals=draft.goals, relations=draft.relations
            ),
        )

    def _content(self, handle: str) -> tuple[RecordReference, bytes]:
        match = _HANDLE.fullmatch(handle)
        if match is None:
            raise ValueError("Use a saved kind:SHA256 record handle")
        kind, digest = _kind(match[1]), match[2]
        path = self._records / f"{kind}-{digest}.json"
        content = self._bounded(path)
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("Saved record content no longer matches its handle")
        return RecordReference(
            handle=handle, kind=kind, sha256=digest, path=str(path), bytes=len(content)
        ), content

    def reference(self, handle: str) -> RecordReference:
        """Return a saved record's path and identity after checking its content hash."""
        reference, _ = self._content(handle)
        return reference

    def resolve(self, kind: RecordKind, source: str) -> RecordReference:
        """Return a matching saved handle, or import a local file for CLI use.

        Raises:
            ValueError: A supplied handle names a different document kind.
        """
        if ":" in source and source.split(":", 1)[0] in RECORD_MODELS:
            reference = self.reference(source)
            if reference.kind != kind:
                raise ValueError(f"Expected {kind}, received {reference.kind}")
            return reference
        return self.import_file(kind, Path(source))

    def _read[T: Record](self, handle: str, kind: RecordKind, model: type[T]) -> T:
        reference, content = self._content(handle)
        if reference.kind != kind:
            raise ValueError(f"Expected {kind}, received {reference.kind}")
        return model.model_validate_json(content)

    def _verification(self, report: Report) -> VerificationSummary:
        return VerificationSummary(
            reference=self._save("verification", report),
            status=report.status,
            runtime_policy=report.runtime_policy,
            capability_status=report.capability_status,
            scope=report.scope,
            request_complete=report.request_complete,
            coverage=dict(Counter(item.status for item in report.coverage)),
            obligations=dict(Counter(item.status for item in report.obligations)),
            diagnostic_count=len(report.diagnostics),
            assumption_count=len(report.assumptions),
            verification_digest=report.verification_digest,
            rule_version=report.rule_version,
            capability_digest=report.capability_digest,
            request_digest=report.request_digest,
            plan_digest=report.plan_digest,
            required_components=report.required_components,
        )

    def propose(
        self,
        request: str,
        capabilities: str | None = None,
        *,
        limits: SearchLimits | None = None,
        preferences: PlanningPreferences | None = None,
    ) -> ProposalSummary:
        """Save a bounded proposal and return compact accepted or rejected choices.

        Args:
            request: Handle for independent mandatory scientific work.
            capabilities: Custom catalog handle; null uses shared Psi4 contracts.
            limits: Finite search and verification bounds; null uses defaults.
            preferences: Call-sharing preference after the request's model and
                route order; null prefers fewer explicitly authorized calls.

        Returns:
            Complete proposal, optional accepted plan, and verification references.
        """
        proposal = propose(
            self._read(request, "request", ScientificRequest),
            self._read(capabilities, "capabilities", CapabilityCatalog)
            if capabilities is not None
            else None,
            limits=limits,
            preferences=preferences,
        )
        return ProposalSummary(
            proposal=self._save("proposal", proposal),
            status=proposal.status,
            attempts=proposal.attempts,
            plan=self._save("plan", proposal.plan) if proposal.plan else None,
            verification=self._verification(proposal.report)
            if proposal.report
            else None,
            choice_count=len(proposal.choices),
            choices=tuple(
                ChoiceSummary(
                    goal=item.goal,
                    method=item.model.method,
                    basis=item.model.basis,
                    reference=item.model.reference,
                    derivative_route=item.derivative_route,
                    preference_rank=item.preference_rank,
                )
                for item in proposal.choices[:_CHOICE_PREVIEW]
            ),
            calculation_count=sum(
                isinstance(step, Calculation) for step in proposal.plan.steps
            )
            if proposal.plan is not None
            else None,
            shared_call_count=len(proposal.reuses),
            last_candidate=self._save("plan", proposal.last_candidate)
            if proposal.last_candidate is not None
            else None,
        )

    def verify(
        self,
        plan: str,
        request: str,
        capabilities: str | None = None,
        *,
        limits: Limits | None = None,
    ) -> VerificationSummary:
        """Verify a plan against independent intent and save its complete report.

        Args:
            plan: Handle for the proposed calculation plan.
            request: Handle for independent scientific requirements.
            capabilities: Custom catalog handle; null uses shared Psi4 contracts.
            limits: Verification bounds; null uses defaults.

        Returns:
            Scientific acceptance, coverage counts, and complete verification path.
        """
        report = verify(
            self._read(plan, "plan", Plan),
            request=self._read(request, "request", ScientificRequest),
            catalog=self._read(capabilities, "capabilities", CapabilityCatalog)
            if capabilities
            else None,
            limits=limits,
        )
        return self._verification(report)

    def explain(
        self,
        handle: str,
        *,
        section: ExplanationSection = "issues",
        offset: int = 0,
        limit: int = 20,
    ) -> ExplanationPage:
        """Page through located findings without returning SMT queries or proof text.

        Args:
            handle: Saved proposal or verification handle.
            section: Issues, coverage, assumptions, or proposal choices/reuse.
            offset: Zero-based index, default zero.
            limit: Page size from 1 through 100, default twenty.

        Returns:
            Bounded excerpts with paths to complete evidence and exact counterexamples.

        Raises:
            ValueError: The kind, section, or pagination arguments are invalid.
        """
        page_end(0, offset, limit)
        reference, content = self._content(handle)
        if reference.kind == "proposal":
            items = _proposal_items(Proposal.model_validate_json(content), section)
        elif reference.kind == "verification" and section not in {
            "choices",
            "reuse",
        }:
            items = _report_items(Report.model_validate_json(content), section, ())
        else:
            raise ValueError(
                "Explain a proposal or verification; choices/reuse require a proposal"
            )
        end = page_end(len(items), offset, limit)
        return ExplanationPage(
            reference=reference,
            section=section,
            total=len(items),
            offset=offset,
            next_offset=end if end < len(items) else None,
            items=items[offset:end],
        )

    def capabilities(
        self,
        handle: str,
        query: CapabilityQuery | None = None,
    ) -> DiscoveryPage:
        """Page through matching capability entries without probing an application.

        Args:
            handle: Saved scientific contract catalog handle.
            query: Entry category, exact name, driver, and page; null uses defaults.

        Returns:
            Matching entries and the exact capability snapshot reference.

        Raises:
            ValueError: Pagination is invalid or a driver filters non-method entries.
        """
        selection = (
            CapabilityQuery.model_validate(query) if query else CapabilityQuery()
        )
        section, name, driver = selection.section, selection.name, selection.driver
        offset, limit = selection.offset, selection.limit
        page_end(0, offset, limit)
        if driver is not None and section not in {"methods", "products"}:
            raise ValueError("Driver filtering requires methods or products")
        if selection.product is not None and section != "products":
            raise ValueError("Product filtering requires the products section")
        catalog = self._read(handle, "capabilities", CapabilityCatalog)
        entries: tuple[Record, ...]
        if section == "methods":
            entries = tuple(
                item
                for item in catalog.methods
                if (name is None or item.method.casefold() == name.strip().casefold())
                and (driver is None or item.driver == driver)
            )
        elif section == "products":
            entries = discover_products(
                catalog, method=name, driver=driver, name=selection.product
            )
        elif section == "bases":
            entries = tuple(
                item
                for item in catalog.bases
                if name is None or item.name.casefold() == name.strip().casefold()
            )
        elif section == "options":
            entries = tuple(
                item
                for item in catalog.options
                if name is None or item.key == name.strip().casefold()
            )
        elif section == "environments":
            entries = tuple(
                item
                for item in catalog.environments
                if name is None or item.kind.casefold() == name.strip().casefold()
            )
        elif section == "components":
            entries = tuple(
                item
                for item in catalog.components
                if name is None or item.key == name.strip().casefold()
            )
        else:
            entries = tuple(
                item
                for item in catalog.evidence
                if name is None or item.id.casefold() == name.strip().casefold()
            )
        end = page_end(len(entries), offset, limit)
        return DiscoveryPage(
            section=section,
            catalog=self.reference(handle),
            total=len(entries),
            offset=offset,
            next_offset=end if end < len(entries) else None,
            items=tuple(
                _capability_entry(item, selection) for item in entries[offset:end]
            ),
        )

    def export(
        self,
        plan: str,
        request: str,
        capabilities: str | None,
        destination: Path,
        *,
        limits: Limits | None = None,
    ) -> ExportSummary:
        """Reverify and export construction artifacts to a new directory.

        Args:
            plan: Proposed plan handle, independently checked again before export.
            request: Independent scientific request handle.
            capabilities: Custom catalog handle; null uses shared Psi4 contracts.
            destination: New directory whose parent exists; never overwritten.
            limits: Verification bounds; null uses defaults.

        Returns:
            Bundle locations or a saved report explaining scientific rejection.
        """
        try:
            exported = export_bundle(
                self._read(plan, "plan", Plan),
                self._read(request, "request", ScientificRequest),
                self._read(capabilities, "capabilities", CapabilityCatalog)
                if capabilities is not None
                else None,
                destination,
                limits=limits,
            )
        except VerificationError as error:
            return ExportSummary(
                status="rejected",
                verification=self._verification(error.report),
                directory=None,
                manifest_path=None,
                manifest_digest=None,
                native_inputs=(),
            )
        directory = Path(exported.directory)
        report = Report.model_validate_json(
            self._bounded(directory / "verification.json")
        )
        return ExportSummary(
            status="exported",
            verification=self._verification(report),
            directory=exported.directory,
            manifest_path=str(directory / "manifest.json"),
            manifest_digest=exported.manifest_digest,
            backend_version=exported.manifest.backend_version,
            option_policy=exported.manifest.option_policy,
            namespace_policy=exported.manifest.namespace_policy,
            native_inputs=tuple(
                str(directory / item) for item in exported.manifest.native_inputs
            ),
        )
