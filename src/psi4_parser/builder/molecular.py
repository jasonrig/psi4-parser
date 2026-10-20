"""Describe molecular identity, fragments, and symbolic or numerical geometry."""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from psi4_parser.builder._model import Angle, Length, Model, evolve
from psi4_parser.builder._vectors import Vector

# Atom selections use stable identities rather than geometry or optimizer indices.
type AtomIds = tuple[str, ...]
type AnchorReferences = AtomIds
type AnchorRequirements = dict[str, AnchorReferences]


class UnresolvedGeometryError(ValueError):
    """Indicate that symbolic geometry needs resolution before numerical analysis."""


class Parameter(Model):
    """Use a named distance or angle from the molecule's parameters."""

    kind: Literal["parameter"] = Field(
        default="parameter",
        description="Selects a reference to a named geometry value.",
    )
    name: str = Field(
        min_length=1, description="Name defined in the molecule's parameters list."
    )
    negative: bool = Field(
        default=False, description="Use the negative of the named value."
    )


class GeometryExpression(Model):
    """A geometry expression that Psi4 will interpret."""

    kind: Literal["geometry_expression"] = Field(
        default="geometry_expression",
        description="Selects a geometry value written as a Psi4 expression.",
    )
    source: str = Field(
        min_length=1,
        description="Psi4 geometry expression, such as TDA for the tetrahedral angle.",
    )


type Quantity = Annotated[
    Length | Angle,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="A distance or angle with its units.",
    ),
]
type InternalValue = Annotated[
    Length | Angle | Parameter | GeometryExpression,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="A distance, angle, named parameter, or Psi4 geometry expression.",
    ),
]
type CartesianValue = float | Parameter | GeometryExpression


class GeometryParameter(Model):
    """A named distance or angle used in molecular coordinates."""

    name: str = Field(
        min_length=1,
        description="Name used to reference this distance or angle in the geometry.",
    )
    value: Annotated[
        Length | Angle | GeometryExpression,
        Field(
            discriminator="kind",
            json_schema_extra={"required": ["kind"]},
            description="Distance or angle with units, or a Psi4 geometry expression.",
        ),
    ] = Field(
        description="Distance or angle with units, or a Psi4 geometry expression."
    )


class Cartesian(Model):
    """An atom position expressed as x, y, and z values."""

    kind: Literal["cartesian"] = Field(
        default="cartesian", description="Selects x, y, and z coordinates."
    )
    x: CartesianValue = Field(
        description="X coordinate in the chosen unit, or a named geometry value."
    )
    y: CartesianValue = Field(
        description="Y coordinate in the chosen unit, or a named geometry value."
    )
    z: CartesianValue = Field(
        description="Z coordinate in the chosen unit, or a named geometry value."
    )
    unit: Literal["angstrom", "bohr"] = Field(
        default="angstrom", description="Length unit for numerical x, y, and z values."
    )


class Anchor(Model):
    """An earlier atom used to define a distance or angle."""

    atom: str = Field(
        min_length=1,
        description="ID of an atom that appears earlier in the molecule's atoms list.",
    )
    value: InternalValue = Field(
        description=(
            "Distance or angle to this reference atom, or a named geometry value."
        )
    )


class ZMatrix(Model):
    """An atom position defined by a distance, bond angle, and torsion."""

    kind: Literal["z_matrix"] = Field(
        default="z_matrix",
        description="Selects distances and angles relative to earlier atoms.",
    )
    anchors: tuple[Anchor, ...] = Field(
        default=(),
        max_length=3,
        description=(
            "Reference atoms and values in distance, angle, then torsion order."
        ),
    )


class Nucleus(Model):
    """An element label with optional isotope or ghost-center settings."""

    label: str = Field(
        min_length=1,
        description=(
            "Element or atom label, such as H, O1, 13C, or X for a dummy atom."
        ),
    )
    ghost: Literal["none", "at", "gh"] = Field(
        default="none",
        description=(
            "none selects a real atom; at and gh select basis-only ghost centers."
        ),
    )
    mass: float | None = Field(
        default=None,
        gt=0,
        description=(
            "Isotope mass in atomic mass units; null uses the default for the label."
        ),
    )

    @property
    def dummy(self) -> bool:
        """Return whether the label denotes a dummy atom, such as X or X1."""
        return re.fullmatch(r"X(?:_\w+|\d+)?", self.label, re.IGNORECASE) is not None


class Atom(Model):
    """An atom with a unique name, element, and position."""

    id: str = Field(
        min_length=1,
        description=(
            "Unique atom name used by bonds, fragments, and constraints, such as a1."
        ),
    )
    nucleus: Nucleus = Field(
        description="Element label and any isotope or ghost-center settings."
    )
    coordinates: Annotated[
        Cartesian | ZMatrix,
        Field(
            discriminator="kind",
            json_schema_extra={"required": ["kind"]},
            description=(
                "Atom position as x/y/z values or distances and angles to earlier "
                "atoms."
            ),
        ),
    ] = Field(
        description=(
            "Atom position as x/y/z values or distances and angles to earlier atoms."
        )
    )


class Bond(Model):
    """A bond between two named atoms."""

    atoms: tuple[str, str] = Field(
        description="IDs of the two atoms joined by this bond."
    )
    order: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Bond order: 1 for single, 2 for double, or 3 for triple.",
    )
    aromatic: bool = Field(
        default=False, description="Whether this bond is marked as aromatic."
    )


class ElectronicState(Model):
    """Net charge and spin multiplicity for a molecule or fragment."""

    charge: int = Field(
        description="Net charge: positive for a cation, negative for an anion."
    )
    multiplicity: int = Field(
        ge=1,
        description=(
            "Spin multiplicity, 2S + 1: 1 for singlet, 2 for doublet, and so on."
        ),
    )


class EFPFragment(Model):
    """Placement of an effective fragment potential from a Psi4 library."""

    id: str = Field(
        min_length=1,
        description="Unique name used to refer to this effective fragment potential.",
    )
    name: str = Field(
        min_length=1,
        description="Fragment name in the effective fragment potential library.",
    )
    points: tuple[Vector, ...] = Field(
        min_length=2,
        max_length=3,
        description=(
            "Six placement values in two triples, or three x/y/z reference points."
        ),
    )


class Fragment(Model):
    """A named group of atoms with optional charge and spin settings."""

    name: str = Field(min_length=1, description="Unique name for this fragment.")
    atom_ids: tuple[str, ...] = Field(
        default=(),
        description="Member atom IDs in the same order as the molecule's atoms list.",
    )
    efp_ids: tuple[str, ...] = Field(
        default=(),
        description="Member effective-fragment IDs in the molecule's fragment order.",
    )
    state: ElectronicState | None = Field(
        default=None,
        description="Charge and spin multiplicity for this fragment, if specified.",
    )


class GeometrySource(Model):
    """Geometry to obtain from a file or PubChem."""

    provider: Literal["from_file", "pubchem"] = Field(
        description="Load geometry from a file or look it up in PubChem."
    )
    value: str = Field(
        min_length=1, description="File path for from_file, or search text for pubchem."
    )


class XYZHeader(Model):
    """Title and optional unit label for XYZ-style geometry input."""

    title: str = Field(
        default="", description="Title on the second line of XYZ geometry input."
    )
    units: str | None = Field(
        default=None,
        description="Optional length-unit label on the XYZ atom-count line.",
    )


class SymmetrySite(Model):
    """An atom or ghost center used to determine molecular symmetry."""

    position: Vector = Field(description="X, y, and z position in angstroms.")
    element: int = Field(
        ge=1,
        le=118,
        description="Atomic number, from 1 for hydrogen to 118 for oganesson.",
    )
    mass: float = Field(gt=0, description="Isotope mass in atomic mass units.")
    ghost: bool = Field(
        description="Whether this site supplies basis functions as a ghost center."
    )


class Molecule(Model):
    """Atoms, coordinates, fragments, charge, spin, and symmetry for one molecule."""

    atoms: tuple[Atom, ...] = Field(
        default=(),
        description="Atoms in input order, including ghost centers and dummy atoms.",
    )
    bonds: tuple[Bond, ...] = Field(
        default=(), description="Pairs of bonded atoms and their bond orders."
    )
    fragments: tuple[Fragment, ...] = Field(
        default=(),
        description=(
            "Fragments in atom order; an empty list treats the molecule as "
            "one fragment."
        ),
    )
    state: ElectronicState | None = Field(
        default=None,
        description="Overall net charge and spin multiplicity, if specified.",
    )
    parameters: tuple[GeometryParameter, ...] = Field(
        default=(), description="Named distances and angles used by the coordinates."
    )
    sources: tuple[GeometrySource, ...] = Field(
        default=(),
        description=(
            "Geometry to load from a file or PubChem when Psi4 reads the input."
        ),
    )
    efp: tuple[EFPFragment, ...] = Field(
        default=(), description="Effective fragment potentials and their positions."
    )
    units: Literal["angstrom", "bohr"] = Field(
        default="angstrom", description="Length unit for the generated molecule block."
    )
    symmetry: str | None = Field(
        default=None,
        description="Requested point group, such as c2v; c1 imposes no symmetry.",
    )
    fixed_com: bool = Field(
        default=False,
        description="Keep the input center of mass in its original position.",
    )
    fixed_orientation: bool = Field(
        default=False, description="Keep the input orientation of the molecule."
    )
    xyz_header: XYZHeader | None = Field(
        default=None,
        description="Write the geometry in XYZ style using this title and unit label.",
    )

    @model_validator(mode="after")
    def check_identities(self) -> Self:
        """Return the molecule after checking identities, fragments, and anchors.

        Raises:
            ValueError: Identities, fragments, or anchors are inconsistent.
        """
        ids = tuple(atom.id for atom in self.atoms)
        if len(set(ids)) != len(ids):
            raise ValueError("Atom IDs must be unique")
        efp_ids = tuple(item.id for item in self.efp)
        if len(set(efp_ids)) != len(efp_ids):
            raise ValueError("EFP IDs must be unique")
        if len({p.name for p in self.parameters}) != len(self.parameters):
            raise ValueError("Geometry parameter names must be unique")
        self._check_fragments(ids, efp_ids)
        for bond in self.bonds:
            if bond.atoms[0] == bond.atoms[1] or not set(bond.atoms) <= set(ids):
                raise ValueError("Bonds must connect two distinct known atoms")
        self._check_anchors(ids)
        if self.xyz_header is not None:
            self._check_xyz()
        return self

    def _check_xyz(self) -> None:
        if (
            self.state is not None
            or self.fragments
            or self.parameters
            or self.sources
            or self.efp
            or self.fixed_com
            or self.fixed_orientation
            or self.symmetry
        ):
            raise ValueError(
                "XYZ headers require plain Cartesian geometry without "
                "native metadata directives"
            )
        if any(not isinstance(a.coordinates, Cartesian) for a in self.atoms):
            raise ValueError("XYZ headers require Cartesian atom records")
        if self.xyz_header is not None and self.xyz_header.units is not None:
            expected = {"angstrom": {"ang"}, "bohr": {"bohr", "au"}}[self.units]
            if self.xyz_header.units not in expected:
                raise ValueError(
                    "XYZ header units must match the molecular length unit"
                )

    def _check_fragments(self, ids: tuple[str, ...], efp_ids: tuple[str, ...]) -> None:
        if not self.fragments:
            return
        members = tuple(a for f in self.fragments for a in f.atom_ids)
        effective = tuple(a for f in self.fragments for a in f.efp_ids)
        if members != ids or effective != efp_ids:
            raise ValueError(
                "Fragments must partition atoms and EFP records in their declared order"
            )
        if len({f.name for f in self.fragments}) != len(self.fragments):
            raise ValueError("Fragment names must be unique")

    def _check_anchors(self, ids: tuple[str, ...]) -> None:
        for index, atom in enumerate(self.atoms):
            if not isinstance(atom.coordinates, ZMatrix):
                continue
            refs = tuple(a.atom for a in atom.coordinates.anchors)
            if len(set(refs)) != len(refs) or not set(refs) <= set(ids[:index]):
                raise ValueError(
                    "Z-matrix anchors must reference distinct preceding atoms"
                )
            for position, anchor in enumerate(atom.coordinates.anchors):
                if isinstance(anchor.value, Length) and position != 0:
                    raise ValueError("Angular anchors require angles")
                if isinstance(anchor.value, Angle) and position == 0:
                    raise ValueError("Distance anchors require lengths")

    def __or__(self, stage: Callable[[Self], Self]) -> Self:
        """Return the edited molecule, as in geometry | translate(offset)."""
        return stage(self)

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        *,
        file_format: str | None = None,
        perceive_bonds: bool = False,
    ) -> Self:
        """Read one molecular geometry from a file.

        Atom IDs are a1, a2, and so on in file order. Positions are stored in
        angstroms, with isotope labels and supplied connectivity retained.
        Use ``assemble_fragments`` to define Psi4 fragments.

        Args:
            path: Molecular file containing exactly one structure with coordinates.
            file_format: Open Babel format name; defaults to the file extension.
            perceive_bonds: Infer bonds and bond orders from positions. False uses
                only connectivity supplied by the file.

        Returns:
            A reusable molecule. XYZ leaves charge and multiplicity unspecified;
            other formats use Open Babel's resolved state, including its defaults.

        Example:
            ``geometry = Molecule.from_file("water.sdf")``
        """
        # Defer the adapter import: it consumes these domain model classes.
        from psi4_parser.builder.openbabel import read_molecule  # noqa: PLC0415

        return cls.model_validate(
            read_molecule(
                Path(path), file_format=file_format, perceive_bonds=perceive_bonds
            )
        )

    @classmethod
    def from_xyz(
        cls,
        source: str,
        *,
        state: ElectronicState | None = None,
        perceive_bonds: bool = False,
    ) -> Self:
        r"""Read one XYZ geometry from text, assigning atom IDs in row order.

        Args:
            source: Atom count, title line, and atom rows containing a label and
                three coordinates in angstroms. IDs are a1, a2, and so on. Labels may
                include isotopes, ghosts such as @H or gh(H), and dummy atoms X.
            state: Overall charge and spin multiplicity; None leaves them unspecified.
            perceive_bonds: Infer bonds and bond orders from the positions; defaults
                to False. Connectivity can later supply moving-atom selections.

        Returns:
            A reusable molecule with Cartesian coordinates and optional connectivity.

        Example:
            ``h2 = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n")``
        """
        # Defer the adapter import: it consumes these domain model classes.
        from psi4_parser.builder.openbabel import read_xyz  # noqa: PLC0415

        value = read_xyz(source, perceive_bonds=perceive_bonds)
        return cls.model_validate(evolve(value, state=state))
