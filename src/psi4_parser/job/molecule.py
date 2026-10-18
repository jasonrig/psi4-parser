"""Represent complete molecular specifications with addressable atom records."""

from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field

from psi4_parser.job.model import (
    FragmentSeparator,
    Model,
    Nucleus,
    Number,
    Scalar,
    Units,
)

_ATOM_ID_EXAMPLES: list[str] = ["a1"]
_SYMMETRY_GROUP_EXAMPLES: list[str] = ["c1", "c2v"]
_MOLECULE_NAME_EXAMPLES: list[str] = ["water", "dimer"]
_XYZ_HEADER_LINES = 2


class AtomReference(Model):
    """Reference an atom by stable identity rather than its emitted index.

    Attributes:
        atom_id: Identity of a molecule's atom, including dummy atom records.
    """

    kind: Literal["atom_reference"] = Field(
        default="atom_reference",
        description="Discriminator identifying the AtomReference variant.",
    )
    atom_id: str = Field(
        description="Identity of a molecule's atom, including dummy atom records.",
        min_length=1,
    )


class LabelReference(Model):
    """Retain an unresolved native anchor label or numeric spelling.

    Attributes:
        label: Reference passed to the geometry reader without evaluation.
    """

    kind: Literal["label_reference"] = Field(
        default="label_reference",
        description="Discriminator identifying the LabelReference variant.",
    )
    label: str = Field(
        description="Reference passed to the geometry reader without evaluation.",
        min_length=1,
    )


type AnchorReference = Annotated[
    AtomReference | LabelReference,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Anchor(Model):
    """Define one distance, angle, or dihedral in a Z-matrix atom entry.

    Attributes:
        atom: Stable atom reference or unresolved source label.
        value: Numeric coordinate or symbolic geometry variable.
    """

    atom: AnchorReference = Field(
        description="Stable atom reference or unresolved source label."
    )
    value: Scalar = Field(
        description="Numeric coordinate or symbolic geometry variable."
    )


class Cartesian(Model):
    """Specify three Cartesian coordinates in the molecule's declared units.

    Attributes:
        x: First coordinate, possibly symbolic.
        y: Second coordinate, possibly symbolic.
        z: Third coordinate, possibly symbolic.
    """

    kind: Literal["cartesian"] = Field(
        default="cartesian",
        description="Discriminator identifying the Cartesian variant.",
    )
    x: Scalar = Field(description="First coordinate, possibly symbolic.")
    y: Scalar = Field(description="Second coordinate, possibly symbolic.")
    z: Scalar = Field(description="Third coordinate, possibly symbolic.")


class ZMatrix(Model):
    """Specify an ordered set of zero to three internal-coordinate anchors.

    Attributes:
        anchors: Distance, angle, and dihedral anchors, in that order.
    """

    kind: Literal["z_matrix"] = Field(
        default="z_matrix", description="Discriminator identifying the ZMatrix variant."
    )
    anchors: tuple[Anchor, ...] = Field(
        default=(),
        max_length=3,
        description="Distance, angle, and dihedral anchors, in that order.",
    )


type Coordinates = Annotated[
    Cartesian | ZMatrix,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Atom(Model):
    """Associate a nucleus and coordinate specification with a stable identity.

    Attributes:
        id: Identity retained through coordinate changes and atom reordering.
        nucleus: Element, label, ghost status, and optional isotope mass.
        coordinates: Cartesian or internal-coordinate specification.
    """

    kind: Literal["atom"] = Field(
        default="atom", description="Discriminator identifying the Atom variant."
    )
    id: str = Field(
        description="Identity retained through coordinate changes and atom reordering.",
        min_length=1,
        examples=_ATOM_ID_EXAMPLES,
    )
    nucleus: Nucleus = Field(
        description="Element, label, ghost status, and optional isotope mass."
    )
    coordinates: Coordinates = Field(
        description="Cartesian or internal-coordinate specification."
    )


class ElectronicState(Model):
    """Retain an explicitly supplied overall or fragment electronic state.

    Attributes:
        charge: Native charge value; scientific validation belongs to the reader.
        multiplicity: Native spin multiplicity value.
    """

    kind: Literal["electronic_state"] = Field(
        default="electronic_state",
        description="Discriminator identifying the ElectronicState variant.",
    )
    charge: Number = Field(
        description="Native charge value; scientific validation belongs to the reader."
    )
    multiplicity: Number = Field(description="Native spin multiplicity value.")


class GeometryVariable(Model):
    """Declare a geometry parameter without resolving external Python names.

    Attributes:
        name: Variable name, including a source-level leading minus if present.
        value: Numeric value or the native reader's special symbolic value.
    """

    kind: Literal["geometry_variable"] = Field(
        default="geometry_variable",
        description="Discriminator identifying the GeometryVariable variant.",
    )
    name: str = Field(
        description="Variable name, including a source-level leading minus if present.",
        min_length=1,
    )
    value: Scalar = Field(
        description="Numeric value or the native reader's special symbolic value."
    )


class Symmetry(Model):
    """Specify the requested point-group symmetry.

    Attributes:
        group: Native symmetry label.
    """

    kind: Literal["symmetry"] = Field(
        default="symmetry",
        description="Discriminator identifying the Symmetry variant.",
    )
    group: str = Field(
        description="Native symmetry label.",
        min_length=1,
        examples=_SYMMETRY_GROUP_EXAMPLES,
    )


class FrameDirective(Model):
    """Retain the requested treatment of the molecular reference frame.

    Attributes:
        name: Disable center-of-mass translation or automatic reorientation.
    """

    kind: Literal["frame_directive"] = Field(
        default="frame_directive",
        description="Discriminator identifying the FrameDirective variant.",
    )
    name: Literal["no_com", "no_reorient"] = Field(
        description="Disable center-of-mass translation or automatic reorientation."
    )


class GeometrySource(Model):
    """Reference external geometry without reading a file or contacting PubChem.

    Attributes:
        provider: Native source directive.
        value: Exact path or query supplied to that provider.
    """

    kind: Literal["geometry_source"] = Field(
        default="geometry_source",
        description="Discriminator identifying the GeometrySource variant.",
    )
    provider: Literal["from_file", "pubchem"] = Field(
        description="Native source directive."
    )
    value: str = Field(description="Exact path or query supplied to that provider.")


class XYZHeader(Model):
    """Retain an XYZ count record and its literal title.

    Attributes:
        count: Explicit atom count as supplied to the native reader.
        units: Optional unit marker on the count record.
        title: Literal second XYZ line, including hashes and apostrophes.
    """

    kind: Literal["xyz_header"] = Field(
        default="xyz_header",
        description="Discriminator identifying the XYZHeader variant.",
    )
    count: str = Field(
        description="Explicit atom count as supplied to the native reader.",
        pattern=r"^\d+$",
    )
    units: str | None = Field(
        default=None, description="Optional unit marker on the count record."
    )
    title: str = Field(
        description="Literal second XYZ line, including hashes and apostrophes."
    )


type NumericTriple = tuple[Number, Number, Number]


class EFPFragment(Model):
    """Specify an effective fragment using six coordinates or three points.

    Attributes:
        name: EFP fragment identifier.
        points: Two numeric triples for placement, or three reference points.
    """

    kind: Literal["efp_fragment"] = Field(
        default="efp_fragment",
        description="Discriminator identifying the EFPFragment variant.",
    )
    name: str = Field(description="EFP fragment identifier.", min_length=1)
    points: tuple[NumericTriple, ...] = Field(
        min_length=2,
        max_length=3,
        description="Two numeric triples for placement, or three reference points.",
    )


type MoleculeRecord = Annotated[
    Atom
    | ElectronicState
    | FragmentSeparator
    | GeometryVariable
    | Units
    | Symmetry
    | FrameDirective
    | GeometrySource
    | XYZHeader
    | EFPFragment,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Fragment(Model):
    """Expose a molecular fragment without inferring its electronic state.

    Attributes:
        state: Explicit fragment state, if present.
        records: Ordered atom and EFP records belonging to this fragment.
    """

    state: ElectronicState | None = Field(
        default=None, description="Explicit fragment state, if present."
    )
    records: tuple[MoleculeRecord, ...] = Field(
        default=(),
        description="Ordered atom and EFP records belonging to this fragment.",
    )


class Molecule(Model):
    """Represent a native molecule declaration without evaluating its geometry.

    Attributes:
        name: Optional Python binding created by the declaration.
        records: Complete ordered specification, including mixed coordinates,
            fragment boundaries, variables, and explicit or omitted states.
    """

    kind: Literal["molecule"] = Field(
        default="molecule",
        description="Discriminator identifying the Molecule variant.",
    )
    name: str | None = Field(
        default=None,
        description="Optional Python binding created by the declaration.",
        min_length=1,
        examples=_MOLECULE_NAME_EXAMPLES,
    )
    records: tuple[MoleculeRecord, ...] = Field(
        default=(),
        description=(
            "Complete ordered specification, including mixed coordinates, "
            "fragment boundaries, variables, and explicit or omitted states."
        ),
    )

    @property
    def atoms(self) -> tuple[Atom, ...]:
        """Return all atom records, including ghosts and dummy atoms."""
        return tuple(record for record in self.records if isinstance(record, Atom))

    @property
    def fragments(self) -> tuple[Fragment, ...]:
        """Return explicit fragments while preserving unspecified states."""
        fragments: list[Fragment] = []
        state: ElectronicState | None = None
        records: list[MoleculeRecord] = []
        for record in self.records:
            if isinstance(record, FragmentSeparator):
                if records:
                    fragments.append(Fragment(state=state, records=tuple(records)))
                state, records = None, []
            elif isinstance(record, ElectronicState):
                state = record
            elif isinstance(record, (Atom, EFPFragment)):
                records.append(record)
        if records:
            fragments.append(Fragment(state=state, records=tuple(records)))
        return tuple(fragments)

    @classmethod
    def from_fragments(
        cls,
        fragments: tuple[Fragment, ...],
        *,
        name: str | None = None,
        state: ElectronicState | None = None,
    ) -> Self:
        """Compose fragments with an independently specified overall spin state.

        Args:
            fragments: Ordered fragments with explicit or unspecified states.
            name: Optional binding for the molecule declaration.
            state: Optional overall charge and multiplicity, separate from those
                of the fragments; multiplicities are never added together.

        Returns:
            Molecular specification with explicit native fragment boundaries.
        """
        records: list[MoleculeRecord] = []
        if state is not None:
            records.extend((state, FragmentSeparator()))
        for index, fragment in enumerate(fragments):
            if index:
                records.append(FragmentSeparator())
            if fragment.state is not None:
                records.append(fragment.state)
            records.extend(fragment.records)
        return cls(name=name, records=tuple(records))

    def with_coordinates(self, atom_id: str, coordinates: Coordinates) -> Self:
        """Replace one atom's representation while retaining its identity and state.

        Args:
            atom_id: Stable identity of the atom to update.
            coordinates: New Cartesian or internal-coordinate specification.

        Returns:
            Independent molecule with every other record retained.

        Raises:
            ValueError: The atom identity is not present exactly once.
        """
        if sum(atom.id == atom_id for atom in self.atoms) != 1:
            raise ValueError("Expected one atom with identity: " + atom_id)
        records = tuple(
            Atom(
                id=record.id,
                nucleus=record.nucleus,
                coordinates=coordinates,
            )
            if isinstance(record, Atom) and record.id == atom_id
            else record
            for record in self.records
        )
        return self.__class__(name=self.name, records=records)

    @classmethod
    def from_xyz(cls, source: str, *, name: str | None = None) -> Self:
        """Import XYZ coordinates as native atom records with explicit units.

        The XYZ title is file metadata. Omitting it from generated geometry
        avoids Psi4's removal of blank and comment-only title lines.

        Args:
            source: Complete XYZ document with atom count and title.
            name: Optional Python binding for the resulting declaration.

        Returns:
            Structured molecule with stable atom identities.

        Raises:
            ValueError: Input does not describe exactly one molecule.
        """
        # Import the reader lazily so the independent data models have no cycle.
        from psi4_parser.job.reader import JobSyntaxError, read_job  # noqa: PLC0415

        lines = source.splitlines()
        if len(lines) < _XYZ_HEADER_LINES:
            raise ValueError("XYZ input requires a count and title line")
        geometry = "\n".join(
            (lines[0], "Imported geometry", *lines[_XYZ_HEADER_LINES:])
        )
        try:
            job = read_job("molecule {\n" + geometry + "\n}\n")
        except JobSyntaxError as error:
            raise ValueError("Invalid XYZ document: " + str(error)) from error
        if len(job.body) != 1:
            raise ValueError("XYZ input must describe one molecule")
        molecule = job.body[0]
        if not isinstance(molecule, Molecule):
            raise ValueError("XYZ input must describe one molecule")
        records = molecule.records
        header = records[0] if records else None
        if not isinstance(header, XYZHeader):
            raise ValueError(
                "XYZ input requires a count, title, and Cartesian atom rows"
            )
        if (
            int(header.count) != len(molecule.atoms)
            or len(records) != len(molecule.atoms) + 1
            or any(
                not isinstance(atom.coordinates, Cartesian) for atom in molecule.atoms
            )
        ):
            raise ValueError(
                "XYZ input requires a count, title, and Cartesian atom rows"
            )
        units = Units(name=header.units or "angstrom")
        return cls(name=name, records=(*molecule.atoms, units))

    @classmethod
    def from_file(
        cls, path: Path, *, file_format: str | None = None, name: str | None = None
    ) -> Self:
        """Import a molecular file explicitly; source references remain unread.

        XYZ uses the native grammar. Other formats use Open Babel
        and preserve the information that backend exposes to this adapter.

        Args:
            path: Molecular file explicitly selected for import.
            file_format: Input format, or the file extension when omitted.
            name: Optional Python binding for the imported molecule.

        Returns:
            Molecule constructed from the file contents.

        Raises:
            ImportError: The required Open Babel dependency is unavailable.
            ModuleNotFoundError: The installed backend has a missing dependency.
            OSError: The selected XYZ file cannot be read.
            ValueError: Input is invalid or the backend does not support its format.
        """  # noqa: DOC502 - File readers and the adapter raise these errors.
        input_format = (
            file_format if file_format is not None else path.suffix.removeprefix(".")
        )
        if input_format.casefold() == "xyz":
            return cls.from_xyz(path.read_text(encoding="utf-8"), name=name)
        try:
            # Load the file-format adapter only for non-XYZ imports.
            from psi4_parser.job.openbabel import read_molecule  # noqa: PLC0415
        except ModuleNotFoundError as error:
            if error.name not in {"openbabel", "openbabel.openbabel"}:
                raise
            raise ImportError(
                "Open Babel is required; reinstall psi4-parser dependencies"
            ) from error
        molecule = read_molecule(path, file_format=input_format, name=name)
        return cls(name=molecule.name, records=molecule.records)

    def with_variable(self, name: str, value: Scalar) -> Self:
        """Return a molecule with a declared geometry parameter replaced.

        Args:
            name: Exact declaration name to update.
            value: New numeric value or native symbolic value.

        Returns:
            Independent molecular specification with the updated parameter.

        Raises:
            ValueError: The requested parameter is not declared.
        """
        if not any(
            isinstance(record, GeometryVariable) and record.name == name
            for record in self.records
        ):
            raise ValueError("Undeclared geometry variable: " + name)
        records = tuple(
            GeometryVariable(name=record.name, value=value)
            if isinstance(record, GeometryVariable) and record.name == name
            else record
            for record in self.records
        )
        return self.__class__(name=self.name, records=records)
