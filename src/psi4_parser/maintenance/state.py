"""Describe and update the small, versioned synchronization data files."""

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import TypedDict

from pydantic import BaseModel, ConfigDict


class Snapshot(TypedDict):
    """Record names and source fingerprints emitted by the reference worker."""

    profile: dict[str, str]
    core_names: list[str]
    constant_names: list[str]


class Baseline(TypedDict):
    """Pin the upstream behavior accepted by a successful synchronization."""

    schema: int
    profile: dict[str, str]


class InventoryChange(BaseModel):
    """Describe additions and removals in one namespace table.

    Attributes:
        added: New names, in the reference inventory's order.
        removed: Names that disappeared from the previous inventory.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    added: tuple[str, ...]
    removed: tuple[str, ...]


def read_snapshot(text: str) -> Snapshot:
    """Decode and validate the reference's JSON snapshot.

    Args:
        text: Serialized worker response.

    Returns:
        Validated reference profile and inventories.

    Raises:
        ValueError: Required profile fields or inventory invariants are missing.
    """
    snapshot: Snapshot = json.loads(text)
    if not snapshot["profile"].get("psi4.version_long"):
        raise ValueError("Reference snapshot has no Psi4 build identity")
    for field in ("core_names", "constant_names"):
        names = snapshot[field]
        if not names or names != sorted(set(names)):
            raise ValueError(
                "Reference inventories must be nonempty, ordered and unique"
            )
        if any(not isinstance(name, str) for name in names):
            raise ValueError("Reference inventories must contain strings")
    return snapshot


def read_baseline(path: Path) -> Baseline:
    """Read a supported compatibility manifest.

    Args:
        path: Versioned baseline JSON file.

    Returns:
        The baseline's profile and schema.

    Raises:
        ValueError: The manifest uses an unsupported schema.
    """
    baseline: Baseline = json.loads(path.read_text())
    if baseline["schema"] != 1:
        raise ValueError("Unsupported compatibility manifest schema")
    return baseline


def guarded_changes(previous: dict[str, str], current: dict[str, str]) -> list[str]:
    """Find reader or language changes requiring a grammar assessment.

    Args:
        previous: Previously accepted reference profile.
        current: Candidate reference profile.

    Returns:
        Changed semantic-source keys or Python language/Unicode versions.
    """
    keys = set(previous) | set(current)
    return sorted(
        key
        for key in keys
        if (key.startswith("syntax:") or key in {"python.language", "python.unicode"})
        and previous.get(key) != current.get(key)
    )


def refresh_inventories(
    grammar: str, snapshot: Snapshot
) -> tuple[str, dict[str, InventoryChange]]:
    """Replace only the two grammar-owned namespace inventories.

    Args:
        grammar: Current Psithon parser grammar source.
        snapshot: Reference inventories to render.

    Returns:
        Updated grammar text and the additions/removals for each table.

    Raises:
        ValueError: An inventory definition is missing or duplicated.
    """
    changes: dict[str, InventoryChange] = {}
    for name, names in (
        ("CORE", snapshot["core_names"]),
        ("CONSTANT", snapshot["constant_names"]),
    ):
        pattern = re.compile(r"_PSITHON_" + name + r"_NAMES = (\(.*?\n\))", re.DOTALL)
        matches = list(pattern.finditer(grammar))
        if len(matches) != 1:
            raise ValueError("Expected exactly one namespace inventory: " + name)
        match = matches[0]
        previous: tuple[str, ...] = ast.literal_eval(match.group(1))
        changes[name] = InventoryChange(
            added=tuple(value for value in names if value not in previous),
            removed=tuple(value for value in previous if value not in names),
        )
        rendered = (
            "(\n"
            + "".join(
                "    " + json.dumps(value, ensure_ascii=False) + ",\n"
                for value in names
            )
            + ")"
        )
        grammar = grammar[: match.start(1)] + rendered + grammar[match.end(1) :]
    return grammar, changes


def content_hash(path: Path) -> str:
    """Return the SHA-256 of a file.

    Args:
        path: File to fingerprint.

    Returns:
        Hexadecimal SHA-256 digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()
