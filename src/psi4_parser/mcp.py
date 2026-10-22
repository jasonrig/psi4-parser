"""Render structured Psi4 jobs through a local stdio MCP server."""

from collections.abc import AsyncIterator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Self, TypedDict

import click
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.lifespan import lifespan
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    ValidationError,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from psi4_parser._cli_types import DIRECTORY
from psi4_parser._files import atomic_replace
from psi4_parser.builder import JobSpec, render_job
from psi4_parser.formal.workspace import PlanningWorkspace
from psi4_parser.formal_mcp import register_tools


def _filename(value: str) -> str:
    if value in {".", ".."}:
        raise ValueError("path must be a file name, not a directory")
    return value


type Filename = Annotated[
    str,
    Field(
        min_length=1,
        pattern=r"^[^/\\:\x00-\x1f\x7f]+$",
        description="File name such as water.dat.",
    ),
    AfterValidator(_filename),
]


class Settings(BaseSettings):
    """Configure temporary artifacts and compact planning-tool discovery."""

    model_config = SettingsConfigDict(env_prefix="PSI4_MCP_", frozen=True)

    temp_parent: DirectoryPath | None = Field(
        default=None,
        description=(
            "Parent directory for temporary outputs; null uses the system default."
        ),
    )
    planning_only: bool = Field(
        default=False,
        description="Expose planning tools without the recursive builder schema.",
    )


class _Overrides(TypedDict, total=False):
    temp_parent: Path
    planning_only: bool


class RenderResult(BaseModel):
    """Psi4 input text or the full path of a file containing it."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    path: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Full output file path. Copy or move the file to a durable location."
        ),
    )
    source: str | None = Field(
        default=None,
        description="Psi4 input text, present when no output file name was supplied.",
    )

    @model_validator(mode="after")
    def _one_result(self) -> Self:
        if (self.path is None) == (self.source is None):
            raise ValueError("Exactly one of path and source must be non-null")
        return self


def _open_planning(
    directory: Path | None, cached: PlanningWorkspace | None
) -> PlanningWorkspace:
    if directory is None:
        raise ToolError("The server's planning workspace is not available")
    return cached if cached is not None else PlanningWorkspace(directory / "planning")


def create_server(settings: Settings | None = None) -> FastMCP[None]:
    """Return a stdio server for rendering and compact scientific planning.

    Args:
        settings: Output-directory settings, or environment defaults when omitted.
    """
    configuration = settings if settings is not None else Settings()
    directory: Path | None = None
    planning: PlanningWorkspace | None = None

    @lifespan
    async def workspace(_server: FastMCP[None]) -> AsyncIterator[None]:
        nonlocal directory, planning
        with TemporaryDirectory(
            prefix="psi4-parser-", dir=configuration.temp_parent
        ) as temporary:
            directory = Path(temporary)
            try:
                yield None
            finally:
                directory = None
                planning = None

    server: FastMCP[None] = FastMCP(
        "Psi4 job builder",
        lifespan=workspace,
        strict_input_validation=True,
        dereference_schemas=False,
    )

    def render_psithon(
        job: JobSpec, path: Filename | None = None, overwrite: bool = False
    ) -> RenderResult:
        """Create Psi4 input from molecules, settings, and calculation steps.

        Return the input text, or supply a file name to receive a file path.
        Copy or move written files to a durable location.

        Args:
            job: Molecules, settings, and calculation steps in execution order.
            path: Output file name, such as water.dat; omit to receive input text.
            overwrite: Replace an existing output file with this name.

        Returns:
            Source text or the full path of the temporary output file.

        Raises:
            ToolError: Compilation fails or the output file cannot be written.
        """
        try:
            source = render_job(job)
            if path is None:
                return RenderResult(source=source)
            if directory is None:
                raise ToolError("The server's temporary directory is not available")
            destination = directory / path
            if overwrite:
                atomic_replace(destination, source.encode("utf-8"))
            else:
                with destination.open("x", encoding="utf-8") as stream:
                    stream.write(source)
            return RenderResult(path=str(destination))
        except (ValueError, OSError) as error:
            raise ToolError(str(error)) from error

    if not configuration.planning_only:
        server.tool(render_psithon)

    def planning_workspace() -> PlanningWorkspace:
        nonlocal planning
        planning = _open_planning(directory, planning)
        return planning

    register_tools(server, planning_workspace)
    return server


@click.option("--temp-parent", type=DIRECTORY, default=None)
@click.option("--planning-only", is_flag=True, default=None)
def _serve(temp_parent: Path | None, planning_only: bool | None) -> None:
    """Serve construction and planning; remove temporary files on shutdown.

    Set PSI4_MCP_TEMP_PARENT or --temp-parent to choose an existing parent
    directory. The server creates its own private temporary directory inside it.
    Otherwise it uses the system temporary directory.

    Args:
        temp_parent: Explicit temporary parent, overriding the environment.
        planning_only: Expose only compact planning tools; null uses the environment.

    Raises:
        click.ClickException: Configuration or temporary-directory creation fails.
    """
    try:
        overrides: _Overrides = {}
        if temp_parent is not None:
            overrides["temp_parent"] = temp_parent
        if planning_only is not None:
            overrides["planning_only"] = planning_only
        settings = Settings(**overrides)
        create_server(settings).run(transport="stdio", show_banner=False)
    except (ValidationError, OSError) as error:
        raise click.ClickException(str(error)) from error


command: click.Command = click.command(
    name="mcp",
    help=(
        "Plan calculations and create Psi4 input through a stdio MCP server.\n\n"
        "Use --planning-only for compact planning tools without the builder schema. "
        "Set --temp-parent or PSI4_MCP_TEMP_PARENT to choose an existing parent "
        "directory for temporary outputs; otherwise use the system temporary "
        "directory. Copy or move written files to a durable location."
    ),
)(_serve)

if __name__ == "__main__":
    command()
