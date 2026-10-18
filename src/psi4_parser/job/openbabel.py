"""Adapt explicit molecular-file imports through optional Open Babel bindings."""

from pathlib import Path

from openbabel import openbabel as ob

from psi4_parser.job.model import Nucleus, Number, Units
from psi4_parser.job.molecule import (
    Atom,
    Cartesian,
    ElectronicState,
    Molecule,
    MoleculeRecord,
)


def _records(molecule: ob.OBMol) -> tuple[MoleculeRecord, ...]:
    # Preserve Open Babel's resolved state, including a charge without an
    # independently recorded multiplicity in formats such as MDL mol files.
    records: list[MoleculeRecord] = [
        ElectronicState(
            charge=Number(value=str(molecule.GetTotalCharge())),
            multiplicity=Number(value=str(molecule.GetTotalSpinMultiplicity())),
        )
    ]
    for index in range(1, molecule.NumAtoms() + 1):
        atom = molecule.GetAtom(index)
        if atom is None:
            raise ValueError("Open Babel returned a missing atom")
        label = ob.GetSymbol(atom.GetAtomicNum())
        if atom.GetAtomicNum() == 0:
            label = "X"
        isotope = atom.GetIsotope()
        if isotope:
            label = str(isotope) + label
        records.append(
            Atom(
                id=f"a{index}",
                nucleus=Nucleus(label=label),
                coordinates=Cartesian(
                    x=Number(value=repr(atom.GetX())),
                    y=Number(value=repr(atom.GetY())),
                    z=Number(value=repr(atom.GetZ())),
                ),
            )
        )
    records.append(Units(name="angstrom"))
    return tuple(records)


def read_molecule(
    path: Path, *, file_format: str | None = None, name: str | None = None
) -> Molecule:
    """Import one molecular file using an explicitly invoked optional backend.

    Open Babel interprets the file's chemical format. Atom order, isotopic
    identity, and Cartesian positions are imported without generating coordinates
    or inferring Psithon fragments from connectivity. Charge and multiplicity
    use the backend's resolved values, which can include its inferred defaults.

    Args:
        path: File explicitly selected for import.
        file_format: Open Babel input format, or the file's final extension.
        name: Optional Python binding for the resulting molecule declaration.

    Returns:
        First-class molecular specification in angstroms.

    Raises:
        ValueError: The format is unsupported, the file cannot be read, or it
            contains zero or multiple molecules.
    """
    conversion = ob.OBConversion()
    input_format = (
        file_format if file_format is not None else path.suffix.removeprefix(".")
    )
    if not conversion.SetInFormat(input_format):
        raise ValueError("Unsupported Open Babel input format: " + input_format)
    molecule = ob.OBMol()
    # OBConversion owns the input stream and closes it with the conversion object.
    if not conversion.ReadFile(molecule, str(path)) or not molecule.NumAtoms():
        raise ValueError("Open Babel could not read a molecule from " + str(path))
    if conversion.Read(ob.OBMol()):
        raise ValueError("Expected one molecule; file contains multiple records")
    return Molecule(name=name, records=_records(molecule))
