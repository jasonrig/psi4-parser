"""Load shared scientific contracts without selecting an engine version."""

from importlib.resources import files

from pydantic import Field, JsonValue, TypeAdapter

from psi4_parser.formal._record import Record
from psi4_parser.formal.capabilities import CapabilityCatalog
from psi4_parser.formal.interface_models import DiscoveryPage
from psi4_parser.formal.science import ProductName

_CATALOG_IDS = ("psi4",)
_MAX_PAGE_SIZE = 100
_JSON = TypeAdapter(JsonValue)


class CatalogInfo(Record):
    """Discover a shared scientific contract collection and its finite coverage."""

    id: str = Field(
        description="Collection name for load_catalog; the default is psi4."
    )
    description: str = Field(
        description="Coverage summary; not a scientific recommendation."
    )
    methods: tuple[str, ...] = Field(
        description="Method names with at least one evidence case."
    )
    method_cases: int = Field(
        ge=0, description="Positive, negative, and unknown method cases."
    )
    products: tuple[ProductName, ...] = Field(
        description="Named products with at least one recorded case."
    )
    product_cases: int = Field(
        ge=0, description="Named product evidence cases across all method combinations."
    )
    bases: tuple[str, ...] = Field(
        description="Orbital basis names explicitly covered."
    )
    components: tuple[str, ...] = Field(
        description="Descriptive component names, without version constraints."
    )


def load_catalog(catalog_id: str = "psi4") -> CapabilityCatalog:
    """Load shared scientific/input contracts with their source citations.

    No engine is imported or inspected. Entries cite their own sources, which
    may span revisions; no per-release catalog or target version is required.

    Args:
        catalog_id: Collection name from available_catalogs(); defaults to psi4.

    Returns:
        Scientific/input contracts with per-entry source/probe provenance.

    Raises:
        ValueError: The collection name is unknown or the packaged catalogue is invalid.
    """
    if catalog_id not in _CATALOG_IDS:
        raise ValueError(f"Unknown bundled capability catalog: {catalog_id}")
    directory = files(__package__).joinpath(catalog_id)
    catalog = CapabilityCatalog.model_validate_json(
        directory.joinpath("catalog.json").read_bytes()
    )
    if catalog.id != catalog_id:
        raise ValueError("Bundled catalog identity differs from its resource name")
    return catalog


def available_catalogs() -> tuple[CatalogInfo, ...]:
    """Return shared contract collections without choosing an engine release."""
    result: list[CatalogInfo] = []
    for name in _CATALOG_IDS:
        catalog = load_catalog(name)
        result.append(
            CatalogInfo(
                id=catalog.id,
                description=(
                    "Reviewed PK HF/SCF, conventional MP2, explicit-basis HF-SAPT, "
                    "DDX, PCMSolver, and TD-SCF input contracts. "
                    "Shared across releases; runtime is operator-managed."
                ),
                methods=tuple(sorted({method.method for method in catalog.methods})),
                method_cases=len(catalog.methods),
                products=tuple(
                    sorted(
                        {
                            product.name
                            for method in catalog.methods
                            for product in method.products
                        }
                    )
                ),
                product_cases=sum(len(method.products) for method in catalog.methods),
                bases=tuple(
                    item.name for item in catalog.bases if item.role == "basis"
                ),
                components=tuple(
                    sorted(
                        {
                            name
                            for method in catalog.methods
                            for name in method.components
                        }
                    )
                ),
            )
        )
    return tuple(result)


def describe_catalogs(*, offset: int = 0, limit: int = 20) -> DiscoveryPage:
    """Discover reusable scientific contract collections in a bounded page.

    Args:
        offset: Zero-based starting entry, default zero.
        limit: Page size from one through one hundred, default twenty.

    Returns:
        Collection identity, finite coverage, and descriptive component names.

    Raises:
        ValueError: Pagination is outside its bounds.
    """
    if offset < 0 or not 1 <= limit <= _MAX_PAGE_SIZE:
        raise ValueError("Use offset >= 0 and limit from 1 through 100")
    catalog = available_catalogs()
    end = offset + limit
    return DiscoveryPage(
        section="catalogs",
        total=len(catalog),
        offset=offset,
        next_offset=end if end < len(catalog) else None,
        items=tuple(
            _JSON.validate_json(item.model_dump_json()) for item in catalog[offset:end]
        ),
    )
