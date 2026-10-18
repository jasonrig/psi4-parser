"""Share molecular-file reading and atom labels at the Open Babel boundary."""

import re
from pathlib import Path

from openbabel import openbabel as ob


def molecule_format(path: Path, override: str | None) -> str:
    """Return an explicit format or the final filename extension."""
    return override if override is not None else path.suffix.removeprefix(".")


def atom_label(atom: ob.OBAtom) -> str:
    """Return an element, isotope, or dummy label from a backend atom."""
    label = ob.GetSymbol(atom.GetAtomicNum()) if atom.GetAtomicNum() else "X"
    isotope = atom.GetIsotope()
    return str(isotope) + label if isotope else label


def _bonding_options(conversion: ob.OBConversion) -> None:
    plugin = conversion.GetInFormat()
    if plugin is None:
        return
    description = plugin.Description()
    if re.search(r"(?mi)^\s*b\s+Disable bonding", description):
        conversion.AddOption("b", ob.OBConversion.INOPTIONS)
        if re.search(r"(?mi)^\s*B\s+Use bonds listed", description):
            conversion.AddOption("B", ob.OBConversion.INOPTIONS)


def read_single_molecule(
    path: Path, input_format: str, *, perceive_bonds: bool = True
) -> ob.OBMol:
    """Return exactly one nonempty molecule using the requested bonding policy.

    Args:
        path: Molecular file to read.
        input_format: Open Babel format name.
        perceive_bonds: Permit normal format-specific bond perception. False
            disables inferred bonds where the format supports that choice,
            while retaining explicitly listed connectivity.

    Raises:
        ValueError: The format is unsupported or the file contains zero or
            multiple molecular records.
    """
    conversion = ob.OBConversion()
    if not conversion.SetInFormat(input_format):
        raise ValueError("Unsupported Open Babel input format: " + input_format)
    if not perceive_bonds:
        _bonding_options(conversion)
    molecule = ob.OBMol()
    if not conversion.ReadFile(molecule, str(path)) or molecule.NumAtoms() == 0:
        raise ValueError("Open Babel could not read a molecule from " + str(path))
    if conversion.Read(ob.OBMol()):
        raise ValueError("Expected one molecule; file contains multiple records")
    return molecule
