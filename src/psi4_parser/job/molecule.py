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
    """An earlier atom selected by its unique ID."""

    kind: Literal["atom_reference"] = Field(
        default="atom_reference",
        description="Selects an atom by its ID.",
    )
    atom_id: str = Field(
        description="ID of an earlier atom in this molecule, including dummy atoms.",
        min_length=1,
    )


class LabelReference(Model):
    """An atom reference written in Psi4 geometry notation."""

    kind: Literal["label_reference"] = Field(
        default="label_reference",
        description="Selects an atom reference written as input text.",
    )
    label: str = Field(
        description="Atom label or atom number as Psi4 geometry input text.",
        min_length=1,
    )


type AnchorReference = Annotated[
    AtomReference | LabelReference,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="An earlier atom selected by its ID, label, or input number.",
    ),
]


class Anchor(Model):
    """An earlier atom and the distance or angle it defines."""

    atom: AnchorReference = Field(
        description="Earlier atom used to define this distance or angle."
    )
    value: Scalar = Field(description="Distance, angle, or named geometry value.")


class Cartesian(Model):
    """An atom position expressed as x, y, and z values."""

    kind: Literal["cartesian"] = Field(
        default="cartesian",
        description="Selects x, y, and z coordinates.",
    )
    x: Scalar = Field(
        description="X coordinate in the molecule's length unit, or a named value."
    )
    y: Scalar = Field(
        description="Y coordinate in the molecule's length unit, or a named value."
    )
    z: Scalar = Field(
        description="Z coordinate in the molecule's length unit, or a named value."
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


type Coordinates = Annotated[
    Cartesian | ZMatrix,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="An x/y/z position or distances and angles to earlier atoms.",
    ),
]


class Atom(Model):
    """An atom with a unique name, element, and position."""

    kind: Literal["atom"] = Field(
        default="atom", description="Selects an atom and its coordinates."
    )
    id: str = Field(
        description="Unique atom name retained when atoms move or change order.",
        min_length=1,
        examples=_ATOM_ID_EXAMPLES,
    )
    nucleus: Nucleus = Field(
        description="Element label and any isotope or ghost-center settings."
    )
    coordinates: Coordinates = Field(
        description=(
            "Atom position as x/y/z values or distances and angles to earlier atoms."
        )
    )


class ElectronicState(Model):
    """Net charge and spin multiplicity for a molecule or fragment."""

    kind: Literal["electronic_state"] = Field(
        default="electronic_state",
        description="Selects charge and spin multiplicity settings.",
    )
    charge: Number = Field(
        description="Net charge in elementary-charge units, written as a number."
    )
    multiplicity: Number = Field(
        description="Spin multiplicity, 2S + 1, written as a number."
    )


class GeometryVariable(Model):
    """A named value used in molecular coordinates."""

    kind: Literal["geometry_variable"] = Field(
        default="geometry_variable",
        description="Selects a named geometry value.",
    )
    name: str = Field(
        description="Name used by geometry coordinates to reference this value.",
        min_length=1,
    )
    value: Scalar = Field(
        description="Number or Psi4 geometry expression assigned to this name."
    )


class Symmetry(Model):
    """The requested molecular point group."""

    kind: Literal["symmetry"] = Field(
        default="symmetry",
        description="Selects a molecular symmetry setting.",
    )
    group: str = Field(
        description="Point-group label, such as c2v; c1 imposes no symmetry.",
        min_length=1,
        examples=_SYMMETRY_GROUP_EXAMPLES,
    )


class FrameDirective(Model):
    """A setting that keeps the input molecular position or orientation."""

    kind: Literal["frame_directive"] = Field(
        default="frame_directive",
        description="Selects a molecular position or orientation setting.",
    )
    name: Literal["no_com", "no_reorient"] = Field(
        description=(
            "no_com keeps the input center of mass; no_reorient keeps its orientation."
        )
    )


class GeometrySource(Model):
    """Geometry to obtain from a file or PubChem."""

    kind: Literal["geometry_source"] = Field(
        default="geometry_source",
        description="Selects geometry loaded from a file or PubChem.",
    )
    provider: Literal["from_file", "pubchem"] = Field(
        description="Load geometry from a file or look it up in PubChem."
    )
    value: str = Field(
        description="File path for from_file, or search text for pubchem."
    )


class XYZHeader(Model):
    """The atom-count line and title of XYZ geometry input."""

    kind: Literal["xyz_header"] = Field(
        default="xyz_header",
        description="Selects an XYZ atom-count line and title.",
    )
    count: str = Field(
        description="Number of atoms declared on the first XYZ line.",
        pattern=r"^\d+$",
    )
    units: str | None = Field(
        default=None, description="Optional length-unit label on the atom-count line."
    )
    title: str = Field(
        description="Title on the second XYZ line, kept exactly as supplied."
    )


type NumericTriple = tuple[Number, Number, Number]


class EFPFragment(Model):
    """Placement of an effective fragment potential from a Psi4 library."""

    kind: Literal["efp_fragment"] = Field(
        default="efp_fragment",
        description="Selects an effective fragment potential and its placement.",
    )
    name: str = Field(
        description="Fragment name in the effective fragment potential library.",
        min_length=1,
    )
    points: tuple[NumericTriple, ...] = Field(
        min_length=2,
        max_length=3,
        description=(
            "Six placement values in two triples, or three x/y/z reference points."
        ),
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
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "An atom, fragment boundary, charge/spin setting, variable, or "
            "geometry directive."
        ),
    ),
]


class Fragment(Model):
    """Atoms and effective fragment potentials grouped as one fragment."""

    state: ElectronicState | None = Field(
        default=None,
        description="Charge and spin multiplicity for this fragment, if specified.",
    )
    records: tuple[MoleculeRecord, ...] = Field(
        default=(),
        description=(
            "Atoms and effective fragment potentials in this fragment, in input order."
        ),
    )


class Molecule(Model):
    """A Psi4 molecule block containing geometry and molecular settings."""

    kind: Literal["molecule"] = Field(
        default="molecule",
        description="Selects a molecule block.",
    )
    name: str | None = Field(
        default=None,
        description="Optional Python name for later references to this molecule.",
        min_length=1,
        examples=_MOLECULE_NAME_EXAMPLES,
    )
    records: tuple[MoleculeRecord, ...] = Field(
        default=(),
        description=(
            "Molecule contents in input order, including atoms, fragment "
            "boundaries, variables, charge, spin, and directives."
        ),
    )

    @property
    def atoms(self) -> tuple[Atom, ...]:
        """Return atoms in input order, including ghost centers and dummy atoms."""
        return tuple(record for record in self.records if isinstance(record, Atom))

    @property
    def fragments(self) -> tuple[Fragment, ...]:
        """Return fragment atoms, effective potentials, and charge/spin settings.

        Fragment separators define each group. Unspecified charge and multiplicity
        remain None. Geometry variables and frame directives stay in records.
        """
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
        """Create a molecule block from ordered fragments.

        Args:
            fragments: Fragments containing atom records and optional charge and spin
                settings. Atom IDs must be distinct across the entire molecule.
            name: Optional Python name for subsequent references to this molecule.
            state: Optional overall charge and multiplicity, specified independently
                of fragment states. Choose the combined multiplicity explicitly.

        Returns:
            A new molecule with fragment boundaries and supplied electronic states.
            Use Units and frame records to set geometry-wide directives as needed.
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
        """Replace one atom's coordinates, keeping its ID and nuclear metadata.

        Args:
            atom_id: ID of the atom to update, such as a1. IDs are independent of
                nucleus labels and row numbers.
            coordinates: Cartesian values in the molecule's length unit, or ZMatrix
                anchors with distances in that unit and angles in degrees. References
                must point to earlier atoms, including any dummy atoms.

        Returns:
            A new molecule with other records retained; call emit_job() to check
            the complete edited input.

        Raises:
            ValueError: Exactly one atom with this ID does not exist.
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
        r"""Read one XYZ document into a molecule block.

        Args:
            source: Atom count, title line, and Cartesian atom rows. Units default to
                angstroms; the count line may include Psi4's bohr unit label.
            name: Optional Python name for subsequent references to this molecule.

        Returns:
            A molecule with IDs a1, a2, and so on in row order, plus an explicit units
            record. The title is treated as file metadata. Add ElectronicState records
            to specify charge and multiplicity.

        Raises:
            ValueError: The text is invalid or contains more than one geometry.

        Example:
            ``h2 = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n", name="h2")``
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
        """Read one molecular file into a molecule block.

        Args:
            path: File containing exactly one molecular structure.
            file_format: Format name; defaults to the file extension. XYZ uses Psi4
                geometry notation; other formats use Open Babel.
            name: Optional Python name for subsequent references to this molecule.

        Returns:
            A molecule with atom IDs a1, a2, and so on in file order. Other formats
            supply positions in angstroms, isotope labels, and Open Babel's resolved
            charge and multiplicity, including its inferred defaults.

        Raises:
            ImportError: Open Babel needs to be installed for the selected format.
            ModuleNotFoundError: The installed file reader has a missing dependency.
            OSError: The XYZ file cannot be read.
            ValueError: The format or molecular contents are invalid.
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
        """Replace a declared geometry variable while retaining its references.

        Args:
            name: Exact declaration name, such as R or D.
            value: Number or Variable. Distances use the molecule's length unit;
                angles use degrees. For example, Number(value="90") sets a torsion.

        Returns:
            A new molecule with the declaration replaced and other records retained.

        Raises:
            ValueError: This molecule has no declaration with the supplied name.
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
