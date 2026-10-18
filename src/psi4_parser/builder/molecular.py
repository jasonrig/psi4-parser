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
    """Reference a named geometry parameter, optionally negated."""

    kind: Literal["parameter"] = Field(
        default="parameter", description="Parameter reference."
    )
    name: str = Field(min_length=1, description="Name of a geometry parameter.")
    negative: bool = Field(default=False, description="Negate the resolved value.")


class GeometryExpression(Model):
    """Retain an unresolved expression accepted by Psi4's geometry reader."""

    kind: Literal["geometry_expression"] = Field(
        default="geometry_expression", description="Unresolved geometry value."
    )
    source: str = Field(
        min_length=1, description="Native geometry expression, such as TDA."
    )


type Quantity = Annotated[
    Length | Angle,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]
type InternalValue = Annotated[
    Length | Angle | Parameter | GeometryExpression,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]
type CartesianValue = float | Parameter | GeometryExpression


class GeometryParameter(Model):
    """Define a dimensioned geometry parameter or a symbolic reader value."""

    name: str = Field(min_length=1, description="Native geometry variable name.")
    value: Annotated[
        Length | Angle | GeometryExpression,
        Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
    ] = Field(description="Parameter value and dimension, or unresolved source.")


class Cartesian(Model):
    """Specify Cartesian values in a declared length unit."""

    kind: Literal["cartesian"] = Field(
        default="cartesian", description="Cartesian position."
    )
    x: CartesianValue = Field(description="First coordinate.")
    y: CartesianValue = Field(description="Second coordinate.")
    z: CartesianValue = Field(description="Third coordinate.")
    unit: Literal["angstrom", "bohr"] = Field(
        default="angstrom", description="Unit for numerical coordinates."
    )


class Anchor(Model):
    """Associate an internal coordinate with a stable reference atom."""

    atom: str = Field(min_length=1, description="Stable ID of an earlier atom.")
    value: InternalValue = Field(description="Distance, angle, or parameter reference.")


class ZMatrix(Model):
    """Specify ordered distance, angle, and dihedral anchors."""

    kind: Literal["z_matrix"] = Field(
        default="z_matrix", description="Internal coordinates."
    )
    anchors: tuple[Anchor, ...] = Field(
        default=(),
        max_length=3,
        description="Distance, angle, and dihedral anchors in order.",
    )


class Nucleus(Model):
    """Retain an element label, ghost notation, and explicit isotope mass."""

    label: str = Field(
        min_length=1,
        description="Psi4 nucleus label, including isotope or atom labels.",
    )
    ghost: Literal["none", "at", "gh"] = Field(
        default="none", description="Ordinary nucleus, @ ghost, or Gh(...) ghost."
    )
    mass: float | None = Field(
        default=None, gt=0, description="Explicit isotope mass in atomic mass units."
    )

    @property
    def dummy(self) -> bool:
        """Identify a reference-frame dummy atom."""
        return re.fullmatch(r"X(?:_\w+|\d+)?", self.label, re.IGNORECASE) is not None


class Atom(Model):
    """Retain molecular identity independently of coordinate representation."""

    id: str = Field(
        min_length=1, description="Stable identity used by selections and constraints."
    )
    nucleus: Nucleus = Field(description="Element, isotope, ghost, and mass metadata.")
    coordinates: Annotated[
        Cartesian | ZMatrix,
        Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
    ] = Field(description="Cartesian or internal position.")


class Bond(Model):
    """Retain supplied or explicitly perceived connectivity."""

    atoms: tuple[str, str] = Field(description="Stable IDs of the bonded atoms.")
    order: int = Field(default=1, ge=1, le=3, description="Integral bond order.")
    aromatic: bool = Field(
        default=False, description="Whether the source marks the bond as aromatic."
    )


class ElectronicState(Model):
    """Specify an explicit charge and spin multiplicity."""

    charge: int = Field(description="Net charge in elementary-charge units.")
    multiplicity: int = Field(ge=1, description="Spin multiplicity, 2S + 1.")


class EFPFragment(Model):
    """Place an effective fragment with six coordinates or three points."""

    id: str = Field(
        min_length=1, description="Stable identity of the effective fragment."
    )
    name: str = Field(min_length=1, description="EFP library fragment name.")
    points: tuple[Vector, ...] = Field(
        min_length=2,
        max_length=3,
        description="Two placement triples or three reference points.",
    )


class Fragment(Model):
    """Group atom and effective-fragment identities with an explicit state."""

    name: str = Field(min_length=1, description="Unique fragment name.")
    atom_ids: tuple[str, ...] = Field(
        default=(), description="Ordered member atom IDs."
    )
    efp_ids: tuple[str, ...] = Field(
        default=(), description="Ordered effective-fragment IDs."
    )
    state: ElectronicState | None = Field(
        default=None,
        description="Explicit fragment charge and multiplicity, if supplied.",
    )


class GeometrySource(Model):
    """Retain a native external geometry request without resolving it."""

    provider: Literal["from_file", "pubchem"] = Field(
        description="Psi4 geometry provider."
    )
    value: str = Field(min_length=1, description="File path or PubChem query.")


class XYZHeader(Model):
    """Retain a native XYZ header when explicitly requested."""

    title: str = Field(default="", description="Literal XYZ title.")
    units: str | None = Field(
        default=None, description="Optional XYZ count-line unit marker."
    )


class SymmetrySite(Model):
    """Describe a resolved nucleus or ghost center for symmetry analysis."""

    position: Vector = Field(description="Resolved position in angstroms.")
    element: int = Field(
        ge=1, le=118, description="Atomic number independent of source labels."
    )
    mass: float = Field(gt=0, description="Explicit or default isotopic mass in amu.")
    ghost: bool = Field(description="Whether this is a ghost basis center.")


class Molecule(Model):
    """Represent an immutable molecule with stable atom identities.

    Numerical operations require resolved geometry. File import reads exactly
    one structure and does not infer Psi4 fragments from chemical connectivity.
    """

    atoms: tuple[Atom, ...] = Field(
        default=(), description="Ordered atoms, including ghosts and dummies."
    )
    bonds: tuple[Bond, ...] = Field(
        default=(), description="Explicit molecular connectivity."
    )
    fragments: tuple[Fragment, ...] = Field(
        default=(),
        description="Ordered explicit fragments; empty means one implicit fragment.",
    )
    state: ElectronicState | None = Field(
        default=None, description="Explicit overall charge and multiplicity."
    )
    parameters: tuple[GeometryParameter, ...] = Field(
        default=(), description="Named, dimensioned geometry variables."
    )
    sources: tuple[GeometrySource, ...] = Field(
        default=(), description="Unresolved native geometry sources."
    )
    efp: tuple[EFPFragment, ...] = Field(
        default=(), description="Effective-fragment placements."
    )
    units: Literal["angstrom", "bohr"] = Field(
        default="angstrom", description="Length unit used in emitted native geometry."
    )
    symmetry: str | None = Field(
        default=None,
        description=(
            "Requested computational point group; edits warn and relax "
            "incompatible requests."
        ),
    )
    fixed_com: bool = Field(
        default=False, description="Emit no_com to retain the center of mass."
    )
    fixed_orientation: bool = Field(
        default=False, description="Emit no_reorient to retain the orientation."
    )
    xyz_header: XYZHeader | None = Field(
        default=None, description="Optional literal XYZ title and header."
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
        """Return the result of applying a pure pipeline stage."""
        return stage(self)

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        *,
        file_format: str | None = None,
        perceive_bonds: bool = False,
    ) -> Self:
        """Return exactly one imported molecular structure."""
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
        """Return one XYZ structure without assuming an electronic state."""
        # Defer the adapter import: it consumes these domain model classes.
        from psi4_parser.builder.openbabel import read_xyz  # noqa: PLC0415

        value = read_xyz(source, perceive_bonds=perceive_bonds)
        return cls.model_validate(evolve(value, state=state))
