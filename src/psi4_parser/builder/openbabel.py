"""Keep Open Babel objects at the molecular file and numerical adapter boundary."""

import re
from pathlib import Path

from openbabel import openbabel as ob

from psi4_parser._openbabel import atom_label, molecule_format, read_single_molecule
from psi4_parser.builder._model import evolve
from psi4_parser.builder._vectors import Vector
from psi4_parser.builder.molecular import (
    AnchorRequirements,
    Atom,
    Bond,
    Cartesian,
    ElectronicState,
    Molecule,
    Nucleus,
)

_XYZ_HEADER_LINES = 2
_XYZ_FIELDS = 4
_MAX_ATOMIC_NUMBER = 118


def _records(molecule: ob.OBMol, *, state: bool) -> Molecule:
    atoms: list[Atom] = []
    for index, atom in enumerate(ob.OBMolAtomIter(molecule), 1):
        label = atom_label(atom)
        atoms.append(
            Atom(
                id=f"a{index}",
                nucleus=Nucleus(label=label),
                coordinates=Cartesian(x=atom.GetX(), y=atom.GetY(), z=atom.GetZ()),
            )
        )
    bonds = tuple(
        Bond(
            atoms=(f"a{b.GetBeginAtomIdx()}", f"a{b.GetEndAtomIdx()}"),
            order=b.GetBondOrder(),
            aromatic=b.IsAromatic(),
        )
        for b in ob.OBMolBondIter(molecule)
    )
    return Molecule(
        atoms=tuple(atoms),
        bonds=bonds,
        state=ElectronicState(
            charge=molecule.GetTotalCharge(),
            multiplicity=molecule.GetTotalSpinMultiplicity(),
        )
        if state
        else None,
    )


def read_molecule(
    path: Path, *, file_format: str | None, perceive_bonds: bool
) -> Molecule:
    """Read one molecular file with coordinates and optional bond perception.

    Args:
        path: File containing exactly one structure.
        file_format: Open Babel format name, or None to use the file extension.
        perceive_bonds: Infer connectivity from positions in addition to any
            bonds supplied by the file.

    Returns:
        A molecule with IDs a1, a2, and so on in file order. XYZ leaves the
        electronic state unspecified; other formats retain Open Babel's state.

    Raises:
        ValueError: The format is unsupported or the file does not contain one molecule.
    """
    input_format = molecule_format(path, file_format)
    if input_format.lower() == "xyz":
        return read_xyz(path.read_text(encoding="utf-8"), perceive_bonds=perceive_bonds)
    molecular = read_single_molecule(path, input_format, perceive_bonds=perceive_bonds)
    if molecular.NumAtoms() > 1 and molecular.GetDimension() == 0:
        raise ValueError(
            "Molecular file has no coordinates; generate geometry explicitly "
            "before importing"
        )
    return _records(molecular, state=True)


def read_xyz(source: str, *, perceive_bonds: bool) -> Molecule:
    """Read XYZ text into atoms with Cartesian coordinates in angstroms.

    Args:
        source: One XYZ document, including its atom count and title line.
        perceive_bonds: Infer bonds and bond orders from the coordinates.

    Returns:
        A molecule with atom IDs a1, a2, and so on in row order. Charge and
        multiplicity remain unspecified.

    Raises:
        ValueError: The XYZ input does not contain one complete structure.
    """
    lines = source.splitlines()
    if len(lines) < _XYZ_HEADER_LINES:
        raise ValueError("XYZ requires an atom count and title")
    count = int(lines[0].strip())
    if (
        count < 1
        or len(lines) < count + 2
        or any(line.strip() for line in lines[count + 2 :])
    ):
        raise ValueError("XYZ requires exactly one complete molecular structure")
    atoms: list[Atom] = []
    for index, line in enumerate(lines[2 : count + 2], 1):
        fields = line.split()
        if len(fields) != _XYZ_FIELDS:
            raise ValueError("XYZ atom rows require a nucleus and three coordinates")
        label = fields[0]
        ghost: str = "none"
        if label.startswith("@"):
            ghost, label = "at", label[1:]
        elif label.lower().startswith("gh(") and label.endswith(")"):
            ghost, label = "gh", label[3:-1]
        mass: float | None = None
        if "@" in label:
            label, mass_text = label.rsplit("@", 1)
            mass = float(mass_text)
        nucleus_values: dict[str, str | float | None] = {
            "label": label,
            "ghost": ghost,
            "mass": mass,
        }
        nucleus = Nucleus.model_validate(nucleus_values)
        atoms.append(
            Atom(
                id=f"a{index}",
                nucleus=nucleus,
                coordinates=Cartesian(
                    x=float(fields[1]), y=float(fields[2]), z=float(fields[3])
                ),
            )
        )
    molecule = Molecule(atoms=tuple(atoms))
    if perceive_bonds:
        backend = to_obmol(molecule)
        backend.ConnectTheDots()
        backend.PerceiveBondOrders()
        molecule = evolve(molecule, bonds=_records(backend, state=False).bonds)
    return molecule


def to_obmol(
    molecule: Molecule, *, points: dict[str, Vector] | None = None
) -> ob.OBMol:
    """Create an Open Babel molecule with atom order, coordinates, and known bonds.

    Args:
        molecule: Atoms, isotope labels, and explicit connectivity.
        points: Optional already-resolved positions in angstroms, keyed by atom ID.

    Returns:
        A separate Open Babel object containing the selected geometry and bonds.

    Raises:
        ValueError: A nucleus label cannot be resolved to an element.
    """
    if points is None:
        from psi4_parser.builder.geometry import positions  # noqa: PLC0415 - Resolve only when the numerical caller has not supplied positions.

        points = positions(molecule)
    result = ob.OBMol()
    for atom in molecule.atoms:
        target = result.NewAtom()
        label = atom.nucleus.label
        numeric = re.fullmatch(r"(\d+)(?:_\w+)?", label)
        symbolic = re.fullmatch(r"(\d+)?([A-Za-z]{1,3})(?:_\w+|\d+)?", label)
        if numeric is not None:
            number = int(numeric[1])
        elif symbolic is not None:
            element: str = symbolic.group(2)
            number = 0 if atom.nucleus.dummy else ob.GetAtomicNum(element.capitalize())
            if symbolic[1]:
                target.SetIsotope(int(symbolic[1]))
        else:
            raise ValueError("Cannot resolve nucleus label: " + label)
        if (
            number == 0 and not atom.nucleus.dummy
        ) or not 0 <= number <= _MAX_ATOMIC_NUMBER:
            raise ValueError("Unknown element: " + label)
        target.SetAtomicNum(number)
        target.SetVector(*points[atom.id])
    indices = {a.id: i for i, a in enumerate(molecule.atoms, 1)}
    for bond in molecule.bonds:
        result.AddBond(indices[bond.atoms[0]], indices[bond.atoms[1]], bond.order)
    return result


def suggested_anchors(
    molecule: Molecule, *, points: dict[str, Vector] | None = None
) -> AnchorRequirements:
    """Suggest Z-matrix reference atom IDs using Open Babel.

    Args:
        molecule: Atom order and identities used by the returned references.
        points: Optional already-resolved positions for this geometry in angstroms.

    Returns:
        Atom IDs mapped to reference IDs in distance, angle, then torsion order.
    """
    backend = to_obmol(molecule, points=points)
    coordinates = backend.GetInternalCoord()
    ids = tuple(a.id for a in molecule.atoms)
    result: AnchorRequirements = {}
    for index, coordinate in enumerate(coordinates[1:]):
        if coordinate is not None:
            # These are Open Babel OBInternalCoord's public SWIG reference fields.
            # noinspection PyProtectedMember
            result[ids[index]] = tuple(
                ids[ref.GetIdx() - 1]
                for ref in (coordinate._a, coordinate._b, coordinate._c)
                if ref is not None
            )
    return result
