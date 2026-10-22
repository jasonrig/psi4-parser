"""Expose checked scientific planning with file inputs and compact JSON responses."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import click
from pydantic import TypeAdapter

from psi4_parser._cli_types import INPUT_FILE
from psi4_parser.formal._record import Record
from psi4_parser.formal.catalogs import describe_catalogs
from psi4_parser.formal.discovery import describe_contracts, describe_schema
from psi4_parser.formal.interface_models import (
    CapabilityQuery,
    CapabilitySection,
    ExplanationSection,
    RecordKind,
)
from psi4_parser.formal.models import Limits
from psi4_parser.formal.planning import SearchLimits
from psi4_parser.formal.reuse import PlanningPreferences, ReusePreference
from psi4_parser.formal.science import Driver, ProductName
from psi4_parser.formal.workspace import PlanningWorkspace

_KINDS = click.Choice(
    (
        "molecule",
        "request_template",
        "request",
        "capabilities",
        "plan",
        "proposal",
        "verification",
    )
)
_DRIVERS = click.Choice(
    ("energy", "optimize", "frequency", "gradient", "hessian", "properties")
)
_REPORT_KINDS = click.Choice(("verification", "proposal"))
_SECTIONS = click.Choice(("issues", "coverage", "assumptions", "choices", "reuse"))
_REUSE: click.Choice[ReusePreference] = click.Choice(("prefer", "avoid"))
_CAPABILITIES = click.Choice(
    (
        "methods",
        "bases",
        "options",
        "components",
        "evidence",
        "products",
        "environments",
    )
)
_PRODUCT_NAME: TypeAdapter[ProductName] = TypeAdapter(ProductName)
_DIRECTORY = click.Path(file_okay=False, path_type=Path)
_PAGE_SIZE = click.IntRange(1, 100)
_OFFSET = click.IntRange(min=0)


class _Failure(click.ClickException):
    """Distinguish malformed records or file failures from scientific rejection."""

    exit_code = 2


@contextmanager
def _errors() -> Iterator[None]:
    try:
        yield
    except (OSError, ValueError) as error:
        raise _Failure(str(error)[:2000]) from error


def _workspace(context: click.Context) -> PlanningWorkspace:
    directory = context.find_object(Path)
    if directory is None:
        raise click.UsageError("Supply a planning workspace directory")
    return PlanningWorkspace(directory)


def _emit(record: Record) -> None:
    click.echo(record.model_dump_json(by_alias=True))


def _verification_exit(status: str) -> None:
    if status != "proved":
        raise click.exceptions.Exit(3 if status == "unknown" else 1)


@click.group(name="formal")
@click.option(
    "--workspace", type=_DIRECTORY, default=Path(".psi4-planning"), show_default=True
)
@click.pass_context
def command(context: click.Context, workspace: Path) -> None:
    """Plan, verify, explain, and export calculations without executing them.

    Print compact JSON; retain full records in the persistent --workspace.
    Later commands accept either local JSON paths or returned kind:SHA256 handles.
    Discovery commands do not create a workspace. Exit 0 for accepted work,
    1 for rejected scientific work, 2 for input/file errors, and 3 for undecided
    or exhausted work.

    \f

    Args:
        context: Click context retaining the selected directory.
        workspace: Persistent artifact directory; its parent must exist.
    """  # noqa: D301 - Click separates command help from callback documentation.
    context.obj = workspace


@click.command(name="load")
@click.argument("kind", type=_KINDS)
@click.argument("path", type=INPUT_FILE)
@click.pass_context
def load(context: click.Context, kind: RecordKind, path: Path) -> None:
    """Validate and copy a local JSON record; return its reusable handle.

    Args:
        context: Selected planning workspace.
        kind: Expected scientific document format.
        path: Existing local JSON file; standard input is not supported.
    """
    with _errors():
        _emit(_workspace(context).import_file(kind, path))


@click.command(name="request")
@click.argument("template")
@click.pass_context
def request_command(context: click.Context, template: str) -> None:
    """Assemble a complete request from TEMPLATE and its saved molecule handles.

    Args:
        context: Selected planning workspace.
        template: RequestTemplate JSON path or request_template:SHA256 handle.
    """
    with _errors():
        workspace = _workspace(context)
        _emit(
            workspace.materialize_request(
                workspace.resolve("request_template", template).handle
            )
        )


@click.command(name="catalogs")
@click.option("--offset", type=_OFFSET, default=0)
@click.option("--limit", type=_PAGE_SIZE, default=20)
def catalogs_command(offset: int, limit: int) -> None:
    """List shared scientific contracts without selecting an engine version.

    Args:
        offset: Zero-based starting entry.
        limit: Maximum entries, from one through one hundred.
    """
    with _errors():
        _emit(describe_catalogs(offset=offset, limit=limit))


@click.command(name="load-catalog")
@click.argument("catalog_id")
@click.pass_context
def load_catalog_command(context: click.Context, catalog_id: str) -> None:
    """Save shared scientific/input contracts; no target version is needed.

    Args:
        context: Selected planning workspace.
        catalog_id: Collection name returned by catalogs; use psi4 for bundled rules.
    """
    with _errors():
        _emit(_workspace(context).load_catalog(catalog_id))


@click.command(name="propose")
@click.argument("request")
@click.option("--capabilities", default=None)
@click.option("--limits", type=INPUT_FILE, default=None)
@click.option(
    "--call-reuse",
    type=_REUSE,
    default="prefer",
    show_default=True,
    help="Try fewer authorized calls or independent calls after model/route choices.",
)
@click.pass_context
def propose_command(
    context: click.Context,
    *,
    request: str,
    capabilities: str | None,
    limits: Path | None,
    call_reuse: ReusePreference,
) -> None:
    """Construct a plan from REQUEST using explicitly permitted alternatives.

    Args:
        context: Selected planning workspace.
        request: Independent request JSON path or saved handle.
        capabilities: Custom catalog path/handle; omission uses shared Psi4 contracts.
        limits: Optional SearchLimits JSON file; omission uses defaults.
        call_reuse: Prefer fewer authorized calls or try independent calls first.

    Raises:
        click.exceptions.Exit: Scientific work is rejected or search remains undecided.
    """
    with _errors():
        workspace = _workspace(context)
        result = workspace.propose(
            workspace.resolve("request", request).handle,
            workspace.resolve("capabilities", capabilities).handle
            if capabilities is not None
            else None,
            limits=SearchLimits.model_validate_json(limits.read_bytes())
            if limits
            else None,
            preferences=PlanningPreferences(calculation_reuse=call_reuse),
        )
        _emit(result)
        if result.status != "constructed":
            raise click.exceptions.Exit(
                3 if result.status in {"unknown", "exhausted"} else 1
            )


@click.command(name="verify")
@click.argument("plan")
@click.option("--request", required=True)
@click.option("--capabilities", default=None)
@click.option("--limits", type=INPUT_FILE, default=None)
@click.pass_context
def verify_command(
    context: click.Context,
    plan: str,
    request: str,
    capabilities: str | None,
    limits: Path | None,
) -> None:
    """Verify PLAN against independent intent and save complete evidence.

    Args:
        context: Selected planning workspace.
        plan: Calculation-plan JSON path or saved handle.
        request: Independent request JSON path or saved handle.
        capabilities: Custom catalog path/handle; omission uses shared Psi4 contracts.
        limits: Optional verification Limits JSON file.
    """
    with _errors():
        workspace = _workspace(context)
        result = workspace.verify(
            workspace.resolve("plan", plan).handle,
            workspace.resolve("request", request).handle,
            workspace.resolve("capabilities", capabilities).handle
            if capabilities
            else None,
            limits=Limits.model_validate_json(limits.read_bytes()) if limits else None,
        )
        _emit(result)
        _verification_exit(result.status)


@click.command(name="explain")
@click.argument("record")
@click.option("--kind", type=_REPORT_KINDS, default="verification")
@click.option("--section", type=_SECTIONS, default="issues", show_default=True)
@click.option("--offset", type=_OFFSET, default=0)
@click.option("--limit", type=_PAGE_SIZE, default=20)
@click.pass_context
def explain_command(  # noqa: PLR0913 - Click supplies the named arguments and options.
    context: click.Context,
    *,
    record: str,
    kind: RecordKind,
    section: ExplanationSection,
    offset: int,
    limit: int,
) -> None:
    """Page through findings, coverage, assumptions, or proposal choices.

    Args:
        context: Selected planning workspace.
        record: Saved handle or local JSON path of a report or proposal.
        kind: Expected kind; select proposal when explaining a proposal file.
        section: Explanation category.
        offset: Zero-based starting item.
        limit: Page size from one through one hundred.
    """
    with _errors():
        workspace = _workspace(context)
        # Handles already carry their kind; file inputs use the explicit selector.
        reference = (
            workspace.reference(record)
            if record.startswith(("proposal:", "verification:"))
            else workspace.resolve(kind, record)
        )
        _emit(
            workspace.explain(
                reference.handle, section=section, offset=offset, limit=limit
            )
        )


@click.command(name="export")
@click.argument("plan")
@click.option("--request", required=True)
@click.option("--capabilities", default=None)
@click.option("--destination", type=_DIRECTORY, required=True)
@click.option("--limits", type=INPUT_FILE, default=None)
@click.pass_context
def export_command(  # noqa: PLR0913 - Click supplies the named arguments and options.
    context: click.Context,
    *,
    plan: str,
    request: str,
    capabilities: str | None,
    destination: Path,
    limits: Path | None,
) -> None:
    """Reverify a plan and create a new construction bundle; never overwrite it.

    Args:
        context: Selected planning workspace.
        plan: Proposed plan JSON path or saved handle.
        request: Independent request JSON path or saved handle.
        capabilities: Custom catalog path/handle; omission uses shared Psi4 contracts.
        destination: New bundle directory whose parent exists.
        limits: Optional verification Limits JSON file.
    """
    with _errors():
        workspace = _workspace(context)
        result = workspace.export(
            workspace.resolve("plan", plan).handle,
            workspace.resolve("request", request).handle,
            workspace.resolve("capabilities", capabilities).handle
            if capabilities is not None
            else None,
            destination,
            limits=Limits.model_validate_json(limits.read_bytes()) if limits else None,
        )
        _emit(result)
        _verification_exit(result.verification.status)


@click.command(name="contracts")
@click.option("--driver", type=_DRIVERS, default=None)
def contracts_command(driver: Driver | None) -> None:
    """Discover prerequisites and products for an operation.

    Args:
        driver: Optional operation filter; omission lists the six built-in drivers.
    """
    _emit(describe_contracts(driver))


@click.command(name="capabilities")
@click.argument("catalog")
@click.option("--section", type=_CAPABILITIES, default="methods", show_default=True)
@click.option("--name", default=None)
@click.option("--driver", type=_DRIVERS, default=None)
@click.option("--product", default=None)
@click.option("--include-products", is_flag=True)
@click.option("--offset", type=_OFFSET, default=0)
@click.option("--limit", type=_PAGE_SIZE, default=20)
@click.pass_context
def capabilities_command(  # noqa: PLR0913 - Click supplies the named arguments and options.
    context: click.Context,
    *,
    catalog: str,
    section: CapabilitySection,
    name: str | None,
    driver: Driver | None,
    product: str | None,
    include_products: bool,
    offset: int,
    limit: int,
) -> None:
    """Query relevant scientific/input contracts without probing Psi4.

    Args:
        context: Selected planning workspace.
        catalog: Capability JSON path or saved handle.
        section: Capability entry category.
        name: Optional exact method, basis, option key, component name,
            environment kind, or evidence ID.
        driver: Optional method driver filter.
        product: Optional exact product name, for the products section.
        include_products: Include full product records in method pages.
        offset: Zero-based starting match.
        limit: Page size from one through one hundred.
    """
    with _errors():
        workspace = _workspace(context)
        reference = workspace.resolve("capabilities", catalog)
        _emit(
            workspace.capabilities(
                reference.handle,
                query=CapabilityQuery(
                    section=section,
                    name=name,
                    driver=driver,
                    product=_PRODUCT_NAME.validate_python(product)
                    if product is not None
                    else None,
                    include_products=include_products,
                    offset=offset,
                    limit=limit,
                ),
            )
        )


@click.command(name="schema")
@click.argument("kind", type=_KINDS)
@click.option("--definition", default=None)
@click.option("--field", "fields", multiple=True)
def schema_command(
    kind: RecordKind, definition: str | None, fields: tuple[str, ...]
) -> None:
    """Discover fields; select --field values for a schema with required references.

    Args:
        kind: Root scientific document format.
        definition: Nested object definition; omission selects the root.
        fields: Requested field names; omission returns a compact field inventory.
    """
    with _errors():
        _emit(describe_schema(kind, definition=definition, fields=fields))


command.add_command(load)
command.add_command(request_command)
command.add_command(propose_command)
command.add_command(verify_command)
command.add_command(explain_command)
command.add_command(export_command)
command.add_command(contracts_command)
command.add_command(capabilities_command)
command.add_command(schema_command)
command.add_command(catalogs_command)
command.add_command(load_catalog_command)
