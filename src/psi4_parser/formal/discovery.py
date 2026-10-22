"""Discover scientific record fields and bounded operation contracts."""

from pydantic import JsonValue, TypeAdapter

from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import CapabilityCatalog
from psi4_parser.formal.contracts import operation_contracts
from psi4_parser.formal.intent import ScientificRequest
from psi4_parser.formal.interface_models import (
    DiscoveryPage,
    RecordKind,
    SchemaDescription,
    SchemaField,
)
from psi4_parser.formal.models import Plan, Report
from psi4_parser.formal.planning import Proposal
from psi4_parser.formal.science import Driver
from psi4_parser.formal.stored_inputs import RequestTemplate, StoredMolecule

RECORD_MODELS: dict[RecordKind, type[Record]] = {
    "molecule": StoredMolecule,
    "request_template": RequestTemplate,
    "request": ScientificRequest,
    "capabilities": CapabilityCatalog,
    "plan": Plan,
    "proposal": Proposal,
    "verification": Report,
}
"""Document models accepted by the planning workspace."""

_JSON = TypeAdapter(JsonValue)
_MAX_PAGE_SIZE = 100


def record_value(record: Record, *, exclude: set[str] | None = None) -> JsonValue:
    """Return a precisely typed JSON value without untyped dictionary conversion."""
    return _JSON.validate_json(record.model_dump_json(exclude=exclude))


def page_end(total: int, offset: int, limit: int) -> int:
    """Return a bounded page end, rejecting negative offsets and excessive limits.

    Raises:
        ValueError: Offset is negative or limit is outside 1 through 100.
    """
    if offset < 0 or not 1 <= limit <= _MAX_PAGE_SIZE:
        raise ValueError("Use offset >= 0 and 1 <= limit <= 100")
    return min(total, offset + limit)


def describe_contracts(driver: Driver | None = None) -> DiscoveryPage:
    """Return the compact built-in operation contracts, optionally for one driver."""
    contracts = operation_contracts(driver)
    return DiscoveryPage(
        section="contracts",
        total=len(contracts),
        offset=0,
        next_offset=None,
        items=tuple(record_value(item) for item in contracts),
    )


def _references(value: JsonValue) -> set[str]:
    if isinstance(value, dict):
        reference = value.get("$ref")
        found = (
            {reference.removeprefix("#/$defs/")}
            if isinstance(reference, str) and reference.startswith("#/$defs/")
            else set()
        )
        for child in value.values():
            found.update(_references(child))
        return found
    if isinstance(value, list):
        return set().union(*(_references(child) for child in value))
    return set()


def _closed_schema(
    node: dict[str, JsonValue],
    definitions: dict[str, JsonValue],
    fields: tuple[str, ...],
) -> dict[str, JsonValue]:
    properties = node.get("properties")
    if len(fields) != len(set(fields)):
        raise ValueError("Requested schema field names must be unique")
    if not isinstance(properties, dict) or not set(fields) <= properties.keys():
        raise ValueError(
            "Requested fields must exist on the selected object definition"
        )
    selected: dict[str, JsonValue] = {name: properties[name] for name in fields}
    required = node.get("required", [])
    result: dict[str, JsonValue] = {
        "type": "object",
        "properties": selected,
        "additionalProperties": False,
        "required": [
            name for name in fields if isinstance(required, list) and name in required
        ],
    }
    pending = _references(selected)
    closure: dict[str, JsonValue] = {}
    while pending:
        name = min(pending)
        pending.remove(name)
        if name not in closure:
            closure[name] = definitions[name]
            pending.update(_references(closure[name]) - closure.keys())
    if closure:
        result["$defs"] = closure
    return result


def describe_schema(
    kind: RecordKind,
    *,
    definition: str | None = None,
    fields: tuple[str, ...] = (),
) -> SchemaDescription:
    """Discover record fields or request a selected schema with resolved references.

    Omit fields for a compact inventory. Supplying fields returns only their
    schema and the transitive definitions required to validate those fields.

    Args:
        kind: Root scientific document format.
        definition: Nested definition name; null selects the root object.
        fields: Selected JSON field names; empty returns discovery metadata only.

    Returns:
        Field descriptions and optional self-contained selected schema.

    Raises:
        ValueError: The definition or requested fields do not exist.
    """
    document: dict[str, JsonValue] = RECORD_MODELS[kind].model_json_schema()
    definitions = document.get("$defs", {})
    if not isinstance(definitions, dict):
        raise ValueError("Record schema definitions must be objects")
    node = document if definition is None else definitions.get(definition)
    if not isinstance(node, dict):
        raise ValueError(f"Unknown object definition: {definition}")
    properties = node.get("properties", {})
    if not isinstance(properties, dict):
        raise ValueError("Select an object definition with named fields")
    selected = _closed_schema(node, definitions, fields) if fields else None
    required = node.get("required", [])
    descriptions: list[SchemaField] = []
    for name, value in properties.items():
        if isinstance(value, dict) and (not fields or name in fields):
            description = value.get("description", "")
            descriptions.append(
                SchemaField(
                    name=name,
                    description=description if isinstance(description, str) else "",
                    required=isinstance(required, list) and name in required,
                )
            )
    description = node.get("description", "")
    return SchemaDescription(
        kind=kind,
        definition=definition,
        description=description if isinstance(description, str) else "",
        definitions=tuple(sorted(definitions)),
        fields=tuple(descriptions),
        json_schema=selected,
    )
