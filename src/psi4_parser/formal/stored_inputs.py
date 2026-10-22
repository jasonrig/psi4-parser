"""Reuse molecular inputs while preserving complete independent scientific intent."""

from typing import Self

from pydantic import Field, model_validator

from psi4_parser.builder.molecular import Molecule
from psi4_parser.formal._record import Record
from psi4_parser.formal.intent import Goal
from psi4_parser.formal.models import Requirement


class StoredMolecule(Record):
    """Save one exact molecular input for reuse under names chosen by each request.

    Geometry retains units, ordered atom IDs, fragments, charge, multiplicity,
    isotopes, ghost centers, and frame settings. Saving establishes structural
    validity; scientific checks occur after assembly into a ScientificRequest.
    """

    geometry: Molecule = Field(
        description="Complete builder molecule, including units, atom IDs, states, "
        "fragments, isotope and ghost data, symmetry, and frame settings."
    )


class MoleculeBinding(Record):
    """Give a saved molecule its input name within one scientific request."""

    name: str = Field(
        min_length=1,
        description="Molecular input name used by this request's goals and relations.",
    )
    molecule: str = Field(
        pattern=r"^molecule:[a-f0-9]{32}$",
        description="Workspace-local molecule:ID handle; checked when the "
        "request is assembled. The stored molecule itself has no input name.",
    )


class RequestTemplate(Record):
    """Describe independent work using saved molecule handles instead of coordinates.

    PlanningWorkspace.materialize_request() resolves every binding into an exact,
    self-contained ScientificRequest. Goals and relations use the chosen input
    names. A template is preparation material; planning and export use the
    resulting complete request.
    """

    molecules: tuple[MoleculeBinding, ...] = Field(
        min_length=1,
        description="Ordered, uniquely named bindings to exact saved molecular inputs.",
    )
    goals: tuple[Goal, ...] = Field(
        min_length=1,
        description="Required calculations and expressions in dependency order, "
        "using binding names for molecular inputs.",
    )
    relations: tuple[Requirement, ...] = Field(
        default=(),
        description="Additional mandatory relationships using binding or goal IDs.",
    )

    @model_validator(mode="after")
    def unique_names(self) -> Self:
        """Return the template after rejecting ambiguous molecule bindings.

        Raises:
            ValueError: Two bindings use the same input name.
        """
        names = tuple(binding.name for binding in self.molecules)
        if len(names) != len(set(names)):
            raise ValueError("Molecule binding names must be unique")
        return self
