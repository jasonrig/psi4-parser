"""Adapt explicit molecular-file imports through Open Babel bindings."""

from pathlib import Path

from openbabel import openbabel as ob

from psi4_parser._openbabel import atom_label, molecule_format, read_single_molecule
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
    for index, atom in enumerate(ob.OBMolAtomIter(molecule), 1):
        label = atom_label(atom)
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
    """Import one molecular file using Open Babel.

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
    """  # noqa: DOC502 - The shared reader reports invalid formats and record counts.
    molecule = read_single_molecule(path, molecule_format(path, file_format))
    return Molecule(name=name, records=_records(molecule))
