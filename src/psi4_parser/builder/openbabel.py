"""Keep Open Babel objects at the molecular file and numerical adapter boundary."""

import re
from pathlib import Path

from openbabel import openbabel as ob

from psi4_parser.builder._model import evolve
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
    for index in range(1, molecule.NumAtoms() + 1):
        atom = molecule.GetAtom(index)
        if atom is None:
            raise ValueError("Open Babel returned a missing atom")
        label = ob.GetSymbol(atom.GetAtomicNum()) if atom.GetAtomicNum() else "X"
        if atom.GetIsotope():
            label = str(atom.GetIsotope()) + label
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
    """Return one imported geometry, retaining bonds and resolved states.

    Raises:
        ValueError: The format is unsupported or the file does not contain one molecule.
    """
    input_format = (
        file_format if file_format is not None else path.suffix.removeprefix(".")
    )
    if input_format.lower() == "xyz":
        return read_xyz(path.read_text(encoding="utf-8"), perceive_bonds=perceive_bonds)
    conversion = ob.OBConversion()
    if not conversion.SetInFormat(input_format):
        raise ValueError("Unsupported Open Babel input format: " + input_format)
    if not perceive_bonds:
        input_plugin = conversion.GetInFormat()
        if input_plugin is not None:
            description = input_plugin.Description()
            if re.search(r"(?mi)^\s*b\s+Disable bonding", description):
                conversion.AddOption("b", ob.OBConversion.INOPTIONS)
                if re.search(r"(?mi)^\s*B\s+Use bonds listed", description):
                    conversion.AddOption("B", ob.OBConversion.INOPTIONS)
    molecular = ob.OBMol()
    if not conversion.ReadFile(molecular, str(path)) or molecular.NumAtoms() == 0:
        raise ValueError("Open Babel could not read a molecule from " + str(path))
    if conversion.Read(ob.OBMol()):
        raise ValueError("Expected one molecule; file contains multiple records")
    if molecular.NumAtoms() > 1 and molecular.GetDimension() == 0:
        raise ValueError(
            "Molecular file has no coordinates; generate geometry explicitly "
            "before importing"
        )
    return _records(molecular, state=True)


def read_xyz(source: str, *, perceive_bonds: bool) -> Molecule:
    """Return one XYZ record without inferring electronic state.

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


def to_obmol(molecule: Molecule) -> ob.OBMol:
    """Return a numerical backend molecule with domain identities retained.

    Raises:
        ValueError: A nucleus label cannot be resolved to an element.
    """
    from psi4_parser.builder.geometry import positions  # noqa: PLC0415 - The numerical adapter consumes geometry operations.

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


def suggested_anchors(molecule: Molecule) -> AnchorRequirements:
    """Return Open Babel's suggested internal-coordinate references."""
    backend = to_obmol(molecule)
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
