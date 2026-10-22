"""Compose independent scientific contract contributions without release profiles."""

from collections.abc import Iterable

from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import CapabilityCatalog


def _unique[T: Record](records: Iterable[T]) -> tuple[T, ...]:
    return tuple({item.model_dump_json(): item for item in records}.values())


def combine_catalogs(
    *catalogs: CapabilityCatalog, name: str = "psi4"
) -> CapabilityCatalog:
    """Combine scientific contributions, retaining evidence and rejecting conflicts.

    Identical entries are deduplicated. Conflicting evidence IDs, duplicate
    scientific keys, and overlapping method conditions are rejected rather than
    overwritten. Entries can cite different revisions and reference audits.

    Args:
        *catalogs: Validated independent contract contributions.
        name: Identity of the resulting scientific collection; defaults to psi4.

    Returns:
        One immutable catalog containing every distinct contribution.

    Raises:
        ValueError: No contribution was supplied, or entries conflict.
    """
    if not catalogs:
        raise ValueError("Supply at least one scientific contract contribution")
    return CapabilityCatalog(
        id=name,
        evidence=_unique(item for catalog in catalogs for item in catalog.evidence),
        methods=_unique(item for catalog in catalogs for item in catalog.methods),
        bases=_unique(item for catalog in catalogs for item in catalog.bases),
        options=_unique(item for catalog in catalogs for item in catalog.options),
        components=_unique(item for catalog in catalogs for item in catalog.components),
        environments=_unique(
            item for catalog in catalogs for item in catalog.environments
        ),
    )
