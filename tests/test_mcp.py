"""Exercise job rendering, temporary output, and cleanup through MCP clients."""

import json
import shutil
from pathlib import Path
from typing import Literal

import pytest
from anyio import Path as AsyncPath
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport
from jsonschema import Draft202012Validator
from mcp_types import CallToolResult, TextContent
from pydantic import BaseModel, JsonValue, TypeAdapter, ValidationError

from psi4_parser.builder import (
    JobSpec,
    Molecule,
    Python,
    Reference,
    compose,
    energy,
    for_each,
    molecule,
    options,
    render_job,
)
from psi4_parser.mcp import RenderResult, Settings, create_server

_JSON = TypeAdapter(JsonValue)


@pytest.fixture(name="anyio_backend")
def _anyio_backend() -> Literal["asyncio"]:
    """Return the asyncio backend required by FastMCP's client."""
    return "asyncio"


def _json_object(model: BaseModel) -> dict[str, JsonValue]:
    document = _JSON.validate_json(model.model_dump_json(by_alias=True))
    assert isinstance(document, dict)
    return document


def _arguments(job: JobSpec, **extra: JsonValue) -> dict[str, JsonValue]:
    return {"job": _json_object(job), **extra}


def _render_result(result: CallToolResult) -> RenderResult:
    assert not result.is_error
    document = _json_object(result)
    return RenderResult.model_validate_json(json.dumps(document["structuredContent"]))


def _error_message(result: CallToolResult) -> str:
    assert result.is_error
    return "\n".join(
        item.text for item in result.content if isinstance(item, TextContent)
    )


@pytest.mark.anyio
async def test_server_exposes_one_job_spec_tool(tmp_path: Path) -> None:
    """Advertise the complete recursive input schema and the two-field result.

    Args:
        tmp_path: Parent for the server's private output directory.
    """
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        tools = await client.list_tools()

    assert [tool.name for tool in tools] == ["render_psithon"]
    document = _json_object(tools[0])
    schema = document["inputSchema"]
    assert isinstance(schema, dict)
    validator = Draft202012Validator(schema)
    validator.check_schema(schema)
    definitions = schema["$defs"]
    assert isinstance(definitions, dict)
    assert {"JobSpec", "ForLoop", "Molecule", "ExternalPotential"} <= definitions.keys()
    output = document["outputSchema"]
    assert isinstance(output, dict)
    assert isinstance(output["properties"], dict)
    assert set(output["properties"]) == {"path", "source"}


@pytest.mark.parametrize(
    ("path", "source"), [(None, None), ("/jobs/job.dat", "set basis sto-3g\n")]
)
def test_result_requires_one_populated_field(
    path: str | None, source: str | None
) -> None:
    """Reject ambiguous results with either both fields absent or both present.

    Args:
        path: Candidate file path.
        source: Candidate rendered source.
    """
    with pytest.raises(ValidationError, match="Exactly one"):
        RenderResult(path=path, source=source)


def test_empty_source_is_a_valid_result() -> None:
    """Represent an empty job without confusing an empty string with None."""
    assert RenderResult(source="").model_dump_json() == '{"path":null,"source":""}'


@pytest.mark.anyio
async def test_nested_job_renders_directly_without_execution(tmp_path: Path) -> None:
    """Accept nested JSON arrays, retain formatting, and leave Python unexecuted.

    Args:
        tmp_path: Temporary parent and location of a marker for accidental execution.
    """
    execution_marker = tmp_path / "must-not-exist"
    hydrogen = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
    job = compose(
        hydrogen,
        options(basis="sto-3g"),
        for_each(
            "method",
            ["scf", "mp2"],
            compose(energy(Reference(name="method"), molecule=hydrogen.ref)),
        ).with_comment("Evaluate both methods."),
        Python(source=f"open({str(execution_marker)!r}, 'w').write('not executed')"),
    )
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        result = _render_result(
            await client.call_tool_mcp("render_psithon", _arguments(job))
        )

    assert result.path is None
    assert result.source == render_job(job)
    assert not await AsyncPath(execution_marker).exists()
    assert not [entry async for entry in AsyncPath(tmp_path).iterdir()]


@pytest.mark.anyio
async def test_files_share_the_server_lifetime_and_support_explicit_overwrite(
    tmp_path: Path,
) -> None:
    """Keep readable files in one private directory and remove it on shutdown.

    Args:
        tmp_path: Parent of the server's temporary directory.
    """
    original = compose(options(basis="sto-3g"))
    replacement = compose(options(basis="cc-pvdz"))
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        first = _render_result(
            await client.call_tool_mcp(
                "render_psithon", _arguments(original, path="job.dat")
            )
        )
        assert first.path is not None
        target = Path(first.path)
        assert target.is_absolute()
        assert target.parent.parent == tmp_path
        assert first.source is None
        assert await AsyncPath(target).read_text() == render_job(original)
        duplicate = await client.call_tool_mcp(
            "render_psithon", _arguments(replacement, path="job.dat")
        )
        assert "File exists" in _error_message(duplicate)
        assert await AsyncPath(target).read_text() == render_job(original)
        overwritten = _render_result(
            await client.call_tool_mcp(
                "render_psithon",
                _arguments(replacement, path="job.dat", overwrite=True),
            )
        )
        assert overwritten.path == first.path
        assert await AsyncPath(target).read_text() == render_job(replacement)
        second = _render_result(
            await client.call_tool_mcp(
                "render_psithon", _arguments(original, path="second.dat")
            )
        )
        assert second.path is not None
        assert Path(second.path).parent == target.parent

    assert not await AsyncPath(target.parent).exists()
    assert not [entry async for entry in AsyncPath(tmp_path).iterdir()]


@pytest.mark.anyio
async def test_output_symlink_does_not_redirect_writes(tmp_path: Path) -> None:
    """Keep a symlink's target untouched during exclusive or replacement writes.

    Args:
        tmp_path: Parent of the server directory and the external target file.
    """
    external = AsyncPath(tmp_path / "external.dat")
    await external.write_text("Original external content")
    job = compose(options(basis="sto-3g"))
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        first = _render_result(
            await client.call_tool_mcp(
                "render_psithon", _arguments(JobSpec(), path="first.dat")
            )
        )
        assert first.path is not None
        link = AsyncPath(Path(first.path).with_name("link.dat"))
        await link.symlink_to(external)

        blocked = await client.call_tool_mcp(
            "render_psithon", _arguments(job, path="link.dat")
        )
        assert _error_message(blocked)
        assert await external.read_text() == "Original external content"

        replaced = _render_result(
            await client.call_tool_mcp(
                "render_psithon", _arguments(job, path="link.dat", overwrite=True)
            )
        )
        assert replaced.path == str(link)
        assert not await link.is_symlink()
        assert await link.read_text() == render_job(job)
        assert await external.read_text() == "Original external content"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "filename",
    [
        "",
        ".",
        "..",
        "../escape.dat",
        "nested/job.dat",
        r"nested\job.dat",
        "/jobs/job.dat",
        r"C:\job.dat",
        "bad\x00name",
        "bad\nname",
    ],
)
async def test_only_file_names_are_accepted(tmp_path: Path, filename: str) -> None:
    """Reject directory traversal, absolute paths, separators, and control characters.

    Args:
        tmp_path: Parent for the server's private output directory.
        filename: Invalid output name received over MCP.
    """
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        result = await client.call_tool_mcp(
            "render_psithon", _arguments(JobSpec(), path=filename)
        )
        assert "path" in _error_message(result)
        directories = [entry async for entry in AsyncPath(tmp_path).iterdir()]
        assert len(directories) == 1
        assert not [entry async for entry in directories[0].iterdir()]

    assert not [entry async for entry in AsyncPath(tmp_path).iterdir()]


@pytest.mark.anyio
async def test_compilation_failure_does_not_change_an_existing_file(
    tmp_path: Path,
) -> None:
    """Return component diagnostics and retain the previous valid output.

    Args:
        tmp_path: Parent for the server's private output directory.
    """
    good = compose(options(basis="sto-3g"))
    bad = compose(energy(Reference(name="missing")))
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        written = _render_result(
            await client.call_tool_mcp(
                "render_psithon", _arguments(good, path="job.dat")
            )
        )
        assert written.path is not None
        failure = await client.call_tool_mcp(
            "render_psithon", _arguments(bad, path="job.dat", overwrite=True)
        )
        assert "components[0].method" in _error_message(failure)
        assert "missing" in _error_message(failure)
        assert await AsyncPath(written.path).read_text() == render_job(good)


@pytest.mark.anyio
async def test_strict_model_errors_are_returned_to_the_agent(tmp_path: Path) -> None:
    """Reject coercible numeric strings and unsupported lower-level documents.

    Args:
        tmp_path: Parent for the server's private output directory.
    """
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        number_arguments: dict[str, JsonValue] = {
            "job": {"components": [{"kind": "memory", "amount": "1.0"}]}
        }
        invalid_number = await client.call_tool_mcp("render_psithon", number_arguments)
        assert "amount" in _error_message(invalid_number)
        native_arguments: dict[str, JsonValue] = {"job": {"body": []}}
        native = await client.call_tool_mcp("render_psithon", native_arguments)
        assert "body" in _error_message(native)


@pytest.mark.anyio
async def test_client_failure_still_cleans_up_the_workspace(tmp_path: Path) -> None:
    """Release the temporary directory when a connected client exits with an error.

    Args:
        tmp_path: Parent for the server's private output directory.
    """
    server = create_server(Settings(temp_parent=tmp_path))
    with pytest.raises(RuntimeError, match="client stopped"):
        await _interrupted_client(server)

    assert not [entry async for entry in AsyncPath(tmp_path).iterdir()]


async def _interrupted_client(server: FastMCP[None]) -> None:
    """Simulate a client failure after writing an output file.

    Raises:
        RuntimeError: The client stops after confirming its output exists.
    """
    client = Client(server)
    async with client:
        written = _render_result(
            await client.call_tool_mcp(
                "render_psithon", _arguments(JobSpec(), path="empty.dat")
            )
        )
        assert written.path is not None
        assert await AsyncPath(written.path).is_file()
        raise RuntimeError("client stopped")


def test_settings_use_the_environment_and_require_an_existing_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Read the parent setting without silently creating an arbitrary directory.

    Args:
        tmp_path: Existing parent directory.
        monkeypatch: Restore the environment after checking settings.
    """
    monkeypatch.setenv("PSI4_MCP_TEMP_PARENT", str(tmp_path))
    assert Settings().temp_parent == tmp_path
    monkeypatch.setenv("PSI4_MCP_TEMP_PARENT", str(tmp_path / "absent"))
    with pytest.raises(ValidationError, match="directory"):
        Settings()


@pytest.mark.anyio
async def test_public_stdio_command_writes_and_cleans_up(tmp_path: Path) -> None:
    """Use the installed CLI over stdio and prefer its parent over the environment.

    Args:
        tmp_path: Parent for the server's private output directory and stderr log.
    """
    executable = shutil.which("psi4-parser")
    assert executable is not None
    transport = StdioTransport(
        command=executable,
        args=["mcp", "--temp-parent", str(tmp_path)],
        env={"PSI4_MCP_TEMP_PARENT": str(tmp_path / "absent")},
        keep_alive=False,
        log_file=tmp_path / "server.log",
    )
    client = Client(transport)
    async with client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools] == ["render_psithon"]
        response = _render_result(
            await client.call_tool_mcp(
                "render_psithon",
                _arguments(compose(options(basis="sto-3g")), path="hydrogen.dat"),
            )
        )
        assert response.path is not None
        target = Path(response.path)
        assert target.parent.parent == tmp_path
        assert "sto-3g" in await AsyncPath(target).read_text()

    assert not await AsyncPath(target.parent).exists()
