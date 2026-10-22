"""Register file-backed scientific planning tools without expanding plan schemas."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from psi4_parser.formal.catalogs import describe_catalogs
from psi4_parser.formal.discovery import describe_contracts, describe_schema
from psi4_parser.formal.interface_models import (
    CapabilityQuery,
    DiscoveryPage,
    ExplanationPage,
    ExplanationSection,
    ExportSummary,
    ProposalSummary,
    RecordKind,
    RecordReference,
    SchemaDescription,
    VerificationSummary,
)
from psi4_parser.formal.models import Limits
from psi4_parser.formal.planning import SearchLimits
from psi4_parser.formal.reuse import PlanningPreferences
from psi4_parser.formal.science import Driver
from psi4_parser.formal.workspace import PlanningWorkspace

type PageOffset = Annotated[int, Field(ge=0)]
type PageLimit = Annotated[int, Field(ge=1, le=100)]
type BundleName = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")]


@contextmanager
def _errors() -> Iterator[None]:
    try:
        yield
    except (OSError, ValueError) as error:
        raise ToolError(str(error)[:2000]) from error


class _PlanningTools:
    """Bind planning tools to one server-owned workspace."""

    def __init__(self, workspace: Callable[[], PlanningWorkspace]) -> None:
        self._workspace = workspace

    def formal_load(
        self,
        kind: RecordKind,
        path: str | None = None,
        source: str | None = None,
        catalog: str | None = None,
    ) -> RecordReference:
        """Validate and copy a scientific JSON record, returning a reusable handle.

        Args:
            kind: Molecule, request_template, request, capabilities, plan,
                proposal, or verification format. Molecules contain a geometry;
                templates bind their handles to input names and independent goals.
            path: Local JSON path; supply exactly one of path, source, and catalog.
            source: JSON text; normally use path for large records. Limit 16 MiB.
            catalog: Shared collection name from formal_catalogs; use psi4 for
                bundled rules. Requires kind=capabilities, without version selection.

        Returns:
            Handle and complete JSON path, removed when this server shuts down.

        Raises:
            ToolError: Inputs are ambiguous, invalid, too large, or unreadable.
        """
        with _errors():
            if sum(value is not None for value in (path, source, catalog)) != 1:
                raise ToolError("Supply exactly one of path, source, and catalog")
            if catalog is not None and kind != "capabilities":
                raise ToolError("Bundled catalogs require kind=capabilities")
            store = self._workspace()
            if catalog is not None:
                return store.load_catalog(catalog)
            if path is not None:
                return store.import_file(kind, Path(path))
            if source is None:
                raise ToolError("Supply a JSON source")
            return store.import_json(kind, source)

    def formal_request(self, template: str) -> RecordReference:
        """Assemble an independent request without resending saved coordinates.

        Args:
            template: Request-template handle returned by formal_load. Each
                molecular binding names a saved molecule:SHA256 handle.

        Returns:
            Complete request handle for planning, verification, and export. Saved
            molecular bytes are hash checked and copied into the request.
        """
        with _errors():
            return self._workspace().materialize_request(template)

    def formal_catalogs(
        self, offset: PageOffset = 0, limit: PageLimit = 20
    ) -> DiscoveryPage:
        """Discover bundled source contracts without inspecting an execution host.

        Args:
            offset: Zero-based first collection, default zero.
            limit: Maximum collections from one through one hundred, default twenty.

        Returns:
            Shared scientific/input coverage, without engine version selection.
        """
        with _errors():
            return describe_catalogs(offset=offset, limit=limit)

    def formal_propose(
        self,
        request: str,
        capabilities: str | None = None,
        limits: SearchLimits | None = None,
        preferences: PlanningPreferences | None = None,
    ) -> ProposalSummary:
        """Construct a bounded plan using independent intent and scientific contracts.

        Args:
            request: Request handle returned by formal_load.
            capabilities: Custom catalog handle; omission uses shared Psi4 contracts.
            limits: Search and verification bounds; omit for defaults.
            preferences: Call-sharing preference after the request's model and
                route order; omission prefers fewer explicitly authorized calls.

        Returns:
            Compact outcome and saved full proposal, accepted plan, and verification.
        """
        with _errors():
            return self._workspace().propose(
                request,
                capabilities,
                limits=limits,
                preferences=preferences,
            )

    def formal_verify(
        self,
        plan: str,
        request: str,
        capabilities: str | None = None,
        limits: Limits | None = None,
    ) -> VerificationSummary:
        """Check every independent scientific goal and save complete verification.

        Args:
            plan: Proposed calculation-plan handle.
            request: Independent scientific-request handle; always required.
            capabilities: Custom catalog handle; omission uses shared Psi4 contracts.
            limits: Verification bounds; omit for defaults.

        Returns:
            Acceptance, coverage counts, and a full-report handle without proof text.
        """
        with _errors():
            return self._workspace().verify(plan, request, capabilities, limits=limits)

    def formal_explain(
        self,
        record: str,
        section: ExplanationSection = "issues",
        offset: PageOffset = 0,
        limit: PageLimit = 20,
    ) -> ExplanationPage:
        """Page through findings, coverage, assumptions, choices, or call sharing.

        Args:
            record: Proposal or verification handle.
            section: Explanation category; choices/reuse require a proposal.
            offset: Zero-based first item, default zero.
            limit: Maximum items from one through one hundred, default twenty.

        Returns:
            Bounded excerpts and JSON paths to exact stored evidence and witnesses.
        """
        with _errors():
            return self._workspace().explain(
                record, section=section, offset=offset, limit=limit
            )

    def formal_export(
        self,
        plan: str,
        request: str,
        capabilities: str | None = None,
        name: BundleName = "job-bundle",
        limits: Limits | None = None,
    ) -> ExportSummary:
        """Reverify and export a construction bundle without running calculations.

        Args:
            plan: Proposed calculation-plan handle.
            request: Independent scientific-request handle.
            capabilities: Custom catalog handle; omission uses shared Psi4 contracts.
            name: New bundle directory name; never overwritten. Letters/digits first,
                then letters, digits, underscores, dots, or hyphens; maximum 128 chars.
            limits: Verification bounds; omit for defaults.

        Returns:
            Fresh verification and temporary bundle paths, or scientific rejection.
            Copy the complete bundle to durable storage before server shutdown.
        """
        with _errors():
            store = self._workspace()
            parent = store.directory / "exports"
            parent.mkdir(mode=0o700, exist_ok=True)
            return store.export(
                plan, request, capabilities, parent / name, limits=limits
            )

    def formal_contracts(self, driver: Driver | None = None) -> DiscoveryPage:
        """Discover an operation's prerequisites and expected products.

        Args:
            driver: Optional driver filter; omit to list the six built-in operations.

        Returns:
            Compact operation contracts without inspecting or launching Psi4.
        """
        return describe_contracts(driver)

    def formal_capabilities(
        self, catalog: str, query: CapabilityQuery | None = None
    ) -> DiscoveryPage:
        """Inspect a bounded page of relevant scientific/input contracts.

        Args:
            catalog: Capability-catalog handle.
            query: Category, name, driver, and page; omit for twenty method entries.

        Returns:
            Matching entries and snapshot identity; missing entries remain unknown.
        """
        with _errors():
            return self._workspace().capabilities(catalog, query)

    def formal_schema(
        self,
        kind: RecordKind,
        definition: str | None = None,
        fields: tuple[str, ...] = (),
    ) -> SchemaDescription:
        """Discover scientific record fields or request a selected-field JSON schema.

        Args:
            kind: Root scientific document format.
            definition: Optional nested definition; omit to inspect the root.
            fields: Selected JSON field names; omit for a compact field inventory.

        Returns:
            Field descriptions and optional schema with required reference definitions.
        """
        with _errors():
            return describe_schema(kind, definition=definition, fields=fields)


def register_tools(
    server: FastMCP[None], workspace: Callable[[], PlanningWorkspace]
) -> None:
    """Register compact discovery, construction, and artifact tools.

    Args:
        server: Server whose lifespan owns all planning artifacts.
        workspace: Resolve the active private workspace.
    """
    handler = _PlanningTools(workspace)
    server.tool(handler.formal_load)
    server.tool(handler.formal_request)
    server.tool(handler.formal_propose)
    server.tool(handler.formal_verify)
    server.tool(handler.formal_explain)
    server.tool(handler.formal_export)
    server.tool(handler.formal_contracts)
    server.tool(handler.formal_capabilities)
    server.tool(handler.formal_schema)
    server.tool(handler.formal_catalogs)
