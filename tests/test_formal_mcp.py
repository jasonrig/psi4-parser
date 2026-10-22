"""Exercise compact scientific planning through an actual MCP client."""

import json
import shutil
from pathlib import Path
from typing import Literal

import pytest
from anyio import Path as AsyncPath
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from jsonschema import Draft202012Validator
from mcp_types import CallToolResult
from pydantic import BaseModel, JsonValue, TypeAdapter

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    BasisEnergyPoint,
    BundleManifest,
    CalculationGoal,
    CapabilityCatalog,
    ElectronicTarget,
    ExponentialExtrapolation,
    Model,
    MoleculeBinding,
    ProductGoal,
    Rational,
    ReferenceExtrapolationStudy,
    RequestTemplate,
    ScientificRequest,
    Setting,
    StoredMolecule,
    TDSCFAnalysis,
    extrapolation_expansion,
)
from psi4_parser.formal.interface_models import (
    DiscoveryPage,
    ExplanationPage,
    ExportSummary,
    ProposalSummary,
    RecordReference,
    SchemaDescription,
    VerificationSummary,
)
from psi4_parser.mcp import Settings, create_server

_JSON = TypeAdapter(JsonValue)


@pytest.fixture(name="anyio_backend")
def _anyio_backend() -> Literal["asyncio"]:
    """Return the backend used by the local FastMCP client."""
    return "asyncio"


def _object(model: BaseModel) -> dict[str, JsonValue]:
    value = _JSON.validate_json(model.model_dump_json(by_alias=True))
    assert isinstance(value, dict)
    return value


def _arguments(**values: JsonValue) -> dict[str, JsonValue]:
    return values


def _parsed[T: BaseModel](result: CallToolResult, model: type[T]) -> T:
    assert not result.is_error
    return model.model_validate_json(json.dumps(_object(result)["structuredContent"]))


def _request(*, source_contracts: bool = False) -> ScientificRequest:
    geometry = Molecule.from_xyz(
        "2\nH2\nH 0 0 0\nH 0 0 .8\n",
        state=ElectronicState(charge=0, multiplicity=1),
    )
    return ScientificRequest(
        molecules=(molecule("h2", geometry),),
        goals=(
            CalculationGoal(
                id="energy",
                driver="energy",
                geometry="h2",
                models=(
                    Model(
                        method="scf",
                        basis="sto-3g",
                        reference="rhf",
                        settings=(Setting(name="scf_type", value="PK"),)
                        if source_contracts
                        else (),
                    ),
                ),
            ),
        ),
    )


@pytest.mark.anyio
async def test_mcp_uses_shared_contracts_without_loading_a_catalog(
    tmp_path: Path,
) -> None:
    """Construct, verify, and export through the compact default workflow.

    Args:
        tmp_path: Server-owned artifact parent.
    """
    client = Client(create_server(Settings(temp_parent=tmp_path, planning_only=True)))
    async with client:
        request = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(
                    kind="request",
                    source=_request(source_contracts=True).model_dump_json(),
                ),
            ),
            RecordReference,
        )
        proposal = _parsed(
            await client.call_tool_mcp(
                "formal_propose", _arguments(request=request.handle)
            ),
            ProposalSummary,
        )
        assert proposal.plan is not None
        report = _parsed(
            await client.call_tool_mcp(
                "formal_verify",
                _arguments(plan=proposal.plan.handle, request=request.handle),
            ),
            VerificationSummary,
        )
        assert report.request_complete
        bundle = _parsed(
            await client.call_tool_mcp(
                "formal_export",
                _arguments(plan=proposal.plan.handle, request=request.handle),
            ),
            ExportSummary,
        )
        assert bundle.status == "exported"


@pytest.mark.anyio
async def test_mcp_retains_certified_exponential_coefficients(tmp_path: Path) -> None:
    """Keep large rational integers exact through JSON-text import and export.

    Args:
        tmp_path: Server-owned construction workspace.
    """
    base = _request(source_contracts=True)
    points = tuple(
        BasisEnergyPoint(
            basis=basis,
            cardinal=cardinal,
            models=(
                Model(
                    method="hf",
                    basis=basis,
                    reference="rhf",
                    settings=(Setting(name="scf_type", value="PK"),),
                ),
            ),
        )
        for basis, cardinal in (("cc-pvdz", 2), ("cc-pvtz", 3))
    )
    expansion = extrapolation_expansion(
        ReferenceExtrapolationStudy(
            id="reference",
            geometry="h2",
            family="cc-pvXZ",
            low=points[0],
            high=points[1],
            alpha=Rational(numerator=163, denominator=100),
            coefficient_digits=30,
        )
    )
    request = ScientificRequest(molecules=base.molecules, goals=expansion.goals)
    client = Client(create_server(Settings(temp_parent=tmp_path, planning_only=True)))
    async with client:
        stored = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(kind="request", source=request.model_dump_json()),
            ),
            RecordReference,
        )
        proposal = _parsed(
            await client.call_tool_mcp(
                "formal_propose", _arguments(request=stored.handle)
            ),
            ProposalSummary,
        )
        assert proposal.plan is not None
        assert proposal.calculation_count == 2
        bundle = _parsed(
            await client.call_tool_mcp(
                "formal_export",
                _arguments(plan=proposal.plan.handle, request=stored.handle),
            ),
            ExportSummary,
        )
        assert bundle.status == "exported"
        assert bundle.manifest_path is not None
        manifest = BundleManifest.model_validate_json(
            await AsyncPath(bundle.manifest_path).read_bytes()
        )
        expression = manifest.expressions[0]
        assert isinstance(expression.extrapolation, ExponentialExtrapolation)
        assert expression.extrapolation.coefficient_digits == 30
        coefficient = expression.terms[0].coefficient
        assert isinstance(coefficient, Rational)
        assert abs(coefficient.numerator) > 2**53


@pytest.mark.anyio
async def test_mcp_assembles_a_complete_request_from_saved_molecular_inputs(
    tmp_path: Path,
) -> None:
    """Reuse one molecule through compact tools and export its exact coordinates.

    Args:
        tmp_path: Server-owned molecular records and construction artifacts.
    """
    complete = _request(source_contracts=True)
    geometry = complete.molecules[0].geometry
    client = Client(create_server(Settings(temp_parent=tmp_path, planning_only=True)))
    async with client:
        saved = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(
                    kind="molecule",
                    source=StoredMolecule(geometry=geometry).model_dump_json(),
                ),
            ),
            RecordReference,
        )
        template = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(
                    kind="request_template",
                    source=RequestTemplate(
                        molecules=(MoleculeBinding(name="h2", molecule=saved.handle),),
                        goals=complete.goals,
                    ).model_dump_json(),
                ),
            ),
            RecordReference,
        )
        request = _parsed(
            await client.call_tool_mcp(
                "formal_request", _arguments(template=template.handle)
            ),
            RecordReference,
        )
        contents = await AsyncPath(request.path).read_bytes()
        assert ScientificRequest.model_validate_json(contents) == complete
        wrong_kind = await client.call_tool_mcp(
            "formal_request", _arguments(template=request.handle)
        )
        assert wrong_kind.is_error
        proposed = _parsed(
            await client.call_tool_mcp(
                "formal_propose", _arguments(request=request.handle)
            ),
            ProposalSummary,
        )
        assert proposed.plan is not None
        exported = _parsed(
            await client.call_tool_mcp(
                "formal_export",
                _arguments(
                    plan=proposed.plan.handle,
                    request=request.handle,
                    name="saved-molecule-job",
                ),
            ),
            ExportSummary,
        )
        assert exported.status == "exported"
        assert exported.manifest_path is not None
        bundle_request = await (
            AsyncPath(exported.manifest_path).parent / "scientific-request.json"
        ).read_bytes()
        assert ScientificRequest.model_validate_json(bundle_request) == complete


@pytest.mark.anyio
async def test_formal_tools_expose_compact_inputs_and_reusable_handles(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Plan without transmitting recursive record schemas or complete proof text.

    Args:
        tmp_path: Parent for lifetime-scoped planning artifacts.
        formal_profile: Synthetic application declarations.
    """
    client = Client(create_server(Settings(temp_parent=tmp_path)))
    async with client:
        tools = await client.list_tools()
        selected = [tool for tool in tools if tool.name.startswith("formal_")]
        assert {tool.name for tool in selected} == {
            "formal_load",
            "formal_request",
            "formal_propose",
            "formal_verify",
            "formal_explain",
            "formal_export",
            "formal_contracts",
            "formal_capabilities",
            "formal_schema",
            "formal_catalogs",
        }
        for tool in selected:
            assert len(json.dumps(_object(tool)["inputSchema"])) < 6000
            input_schema = _object(tool)["inputSchema"]
            assert isinstance(input_schema, dict)
            validator = Draft202012Validator(input_schema)
            validator.check_schema(input_schema)
        loaded = await client.call_tool_mcp(
            "formal_load",
            _arguments(kind="request", source=_request().model_dump_json()),
        )
        assert not loaded.is_error
        request = RecordReference.model_validate_json(
            json.dumps(_object(loaded)["structuredContent"])
        )
        evidence = await client.call_tool_mcp(
            "formal_load",
            _arguments(kind="capabilities", source=formal_profile.model_dump_json()),
        )
        assert not evidence.is_error
        catalog = RecordReference.model_validate_json(
            json.dumps(_object(evidence)["structuredContent"])
        )
        result = await client.call_tool_mcp(
            "formal_propose",
            _arguments(request=request.handle, capabilities=catalog.handle),
        )
        assert not result.is_error
        summary_json = json.dumps(_object(result)["structuredContent"])
        proposal = ProposalSummary.model_validate_json(summary_json)
        assert proposal.status == "constructed"
        assert proposal.plan is not None
        assert proposal.verification is not None
        assert proposal.verification.request_complete
        assert len(summary_json) < 5000
        assert "smt2" not in summary_json
        saved = AsyncPath(proposal.proposal.path)
        assert await saved.exists()
        assert "smt2" in await saved.read_text()

        base = _request()
        goal = base.goals[0]
        assert isinstance(goal, CalculationGoal)
        shared = ScientificRequest(
            molecules=base.molecules,
            goals=tuple(
                CalculationGoal(
                    id=name,
                    driver=goal.driver,
                    geometry=goal.geometry,
                    models=goal.models,
                    reuse_group="same-evaluation",
                )
                for name in ("first", "second")
            ),
        )
        shared_reference = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(kind="request", source=shared.model_dump_json()),
            ),
            RecordReference,
        )
        for preference, count in (("prefer", 1), ("avoid", 2)):
            chosen = _parsed(
                await client.call_tool_mcp(
                    "formal_propose",
                    _arguments(
                        request=shared_reference.handle,
                        capabilities=catalog.handle,
                        preferences={"calculation_reuse": preference},
                    ),
                ),
                ProposalSummary,
            )
            assert chosen.calculation_count == count
            page = _parsed(
                await client.call_tool_mcp(
                    "formal_explain",
                    _arguments(record=chosen.proposal.handle, section="reuse"),
                ),
                ExplanationPage,
            )
            assert page.total == (1 if count == 1 else 0)

    assert not await saved.exists()
    assert not [item async for item in AsyncPath(tmp_path).iterdir()]


@pytest.mark.anyio
async def test_planning_only_mode_checks_evidence_exports_and_cleanup(
    tmp_path: Path,
    formal_profile: CapabilityCatalog,
) -> None:
    """Use the compact server for complete handle-based planning and export.

    Args:
        tmp_path: Server-owned temporary workspace parent.
        formal_profile: Synthetic application evidence.
    """
    client = Client(create_server(Settings(temp_parent=tmp_path, planning_only=True)))
    async with client:
        tools = await client.list_tools()
        assert len(tools) == 10
        assert all(tool.name.startswith("formal_") for tool in tools)
        assert "JobSpec" not in str([_object(tool)["inputSchema"] for tool in tools])
        collections = _parsed(
            await client.call_tool_mcp("formal_catalogs", _arguments(limit=1)),
            DiscoveryPage,
        )
        assert collections.total == 1
        bundled = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(kind="capabilities", catalog="psi4"),
            ),
            RecordReference,
        )
        components = _parsed(
            await client.call_tool_mcp(
                "formal_capabilities",
                _arguments(catalog=bundled.handle, query={"section": "components"}),
            ),
            DiscoveryPage,
        )
        assert components.total == 4
        assert all(
            any(
                isinstance(item, dict) and item.get("name") == name
                for item in components.items
            )
            for name in ("pyddx", "sapt", "optking", "qcelemental")
        )
        ambiguous = await client.call_tool_mcp(
            "formal_load",
            _arguments(kind="capabilities", source="{}", catalog="psi4"),
        )
        assert ambiguous.is_error
        wrong_kind = await client.call_tool_mcp(
            "formal_load", _arguments(kind="request", catalog="psi4")
        )
        assert wrong_kind.is_error
        request = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(kind="request", source=_request().model_dump_json()),
            ),
            RecordReference,
        )
        catalog = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(
                    kind="capabilities", source=formal_profile.model_dump_json()
                ),
            ),
            RecordReference,
        )
        proposal = _parsed(
            await client.call_tool_mcp(
                "formal_propose",
                _arguments(request=request.handle, capabilities=catalog.handle),
            ),
            ProposalSummary,
        )
        assert proposal.plan is not None
        unknown = _parsed(
            await client.call_tool_mcp(
                "formal_verify",
                _arguments(plan=proposal.plan.handle, request=request.handle),
            ),
            VerificationSummary,
        )
        assert unknown.status == "unknown"
        assert not unknown.request_complete
        explained = _parsed(
            await client.call_tool_mcp(
                "formal_explain", _arguments(record=unknown.reference.handle, limit=1)
            ),
            ExplanationPage,
        )
        assert explained.total >= 1
        assert len(explained.items) == 1
        assert explained.items[0].status == "unknown"
        wrong_kind = await client.call_tool_mcp(
            "formal_verify", _arguments(plan=request.handle, request=request.handle)
        )
        assert wrong_kind.is_error
        exported = _parsed(
            await client.call_tool_mcp(
                "formal_export",
                _arguments(
                    plan=proposal.plan.handle,
                    request=request.handle,
                    capabilities=catalog.handle,
                    name="checked",
                ),
            ),
            ExportSummary,
        )
        assert exported.status == "exported"
        assert exported.backend_version == "psi4-builder/8"
        assert exported.namespace_policy == "restore_after_calculation"
        assert exported.option_policy == "native_defaults_per_calculation"
        assert exported.manifest_path is not None
        manifest = AsyncPath(exported.manifest_path)
        original = await manifest.read_bytes()
        repeated = await client.call_tool_mcp(
            "formal_export",
            _arguments(
                plan=proposal.plan.handle,
                request=request.handle,
                capabilities=catalog.handle,
                name="checked",
            ),
        )
        assert repeated.is_error
        assert await manifest.read_bytes() == original
        escaped = await client.call_tool_mcp(
            "formal_export",
            _arguments(
                plan=proposal.plan.handle,
                request=request.handle,
                capabilities=catalog.handle,
                name="../escape",
            ),
        )
        assert escaped.is_error

    assert not await manifest.exists()
    assert not [item async for item in AsyncPath(tmp_path).iterdir()]


@pytest.mark.anyio
async def test_planning_only_stdio_supports_targeted_discovery(tmp_path: Path) -> None:
    """Launch the installed command with the compact-server flag and query a schema.

    Args:
        tmp_path: Temporary parent and retained subprocess stderr log.
    """
    executable = shutil.which("psi4-parser")
    assert executable is not None
    transport = StdioTransport(
        command=executable,
        args=["mcp", "--planning-only", "--temp-parent", str(tmp_path)],
        keep_alive=False,
        log_file=tmp_path / "stdio.log",
    )
    client = Client(transport)
    async with client:
        tools = await client.list_tools()
        assert len(tools) == 10
        response = await client.call_tool_mcp(
            "formal_schema",
            _arguments(kind="request", definition="Model", fields=["basis"]),
        )
        description = _parsed(response, SchemaDescription)
        assert [field.name for field in description.fields] == ["basis"]
        assert description.json_schema is not None
        assert "$defs" not in description.json_schema
        schema_tool = next(tool for tool in tools if tool.name == "formal_schema")
        output_schema = _object(schema_tool)["outputSchema"]
        assert isinstance(output_schema, dict)
        Draft202012Validator(output_schema).validate(
            _object(response)["structuredContent"]
        )


@pytest.mark.anyio
async def test_mcp_retains_root_selectors_and_transient_response_bindings(
    tmp_path: Path,
) -> None:
    """Preserve a selected response root through the compact agent workflow.

    Args:
        tmp_path: Server-owned artifact parent.
    """
    original = _request(source_contracts=True)
    request = ScientificRequest(
        molecules=original.molecules,
        goals=(
            CalculationGoal(
                id="response",
                driver="energy",
                geometry="h2",
                models=(
                    Model(
                        method="td-hf",
                        basis="cc-pvdz",
                        reference="rhf",
                        settings=(Setting(name="scf_type", value="PK"),),
                        tdscf=TDSCFAnalysis(states=2),
                    ),
                ),
            ),
            ProductGoal(
                id="transition",
                calculation="response",
                name="excitation_energy",
                electronic_target=ElectronicTarget(root=2, multiplicity=1),
            ),
        ),
    )
    client = Client(create_server(Settings(temp_parent=tmp_path, planning_only=True)))
    async with client:
        stored = _parsed(
            await client.call_tool_mcp(
                "formal_load",
                _arguments(kind="request", source=request.model_dump_json()),
            ),
            RecordReference,
        )
        proposal = _parsed(
            await client.call_tool_mcp(
                "formal_propose", _arguments(request=stored.handle)
            ),
            ProposalSummary,
        )
        assert proposal.plan is not None
        exported = _parsed(
            await client.call_tool_mcp(
                "formal_export",
                _arguments(plan=proposal.plan.handle, request=stored.handle),
            ),
            ExportSummary,
        )
        assert exported.manifest_path is not None
        manifest = BundleManifest.model_validate_json(
            await AsyncPath(exported.manifest_path).read_bytes()
        )
        assert (
            manifest.native_variables[0].key
            == "TD-HF ROOT 0 -> ROOT 2 EXCITATION ENERGY"
        )
        product = next(item for item in manifest.quantities if item.id == "transition")
        assert product.electronic_target == ElectronicTarget(root=2, multiplicity=1)
