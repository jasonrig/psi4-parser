"""Check molecular-file imports through the installed Open Babel API."""

from pathlib import Path

import pytest

from psi4_parser.job import ElectronicState, Molecule


def test_import_isotopic_mol_file(tmp_path: Path) -> None:
    """Read an isotope from a molecular format beyond native XYZ.

    Args:
        tmp_path: Isolated directory for an explicitly imported molecular file.
    """
    path = tmp_path / "water.mol"
    path.write_text(
        "Water\n  Test          3D\n\n"
        "  3  2  0  0  0  0  0  0  0  0999 V2000\n"
        "    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n"
        "    0.0000    0.7500    0.5000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
        "    0.0000   -0.7500    0.5000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
        "  1  2  1  0  0  0  0\n  1  3  1  0  0  0  0\n"
        "M  ISO  1   1  18\nM  END\n"
    )

    molecule = Molecule.from_file(path, name="water")

    assert molecule.name == "water"
    assert len(molecule.atoms) == 3
    assert molecule.atoms[0].nucleus.label == "18O"


def test_import_retains_resolved_electronic_state(tmp_path: Path) -> None:
    """Keep a file's nonzero charge when multiplicity is supplied by the backend.

    Args:
        tmp_path: Isolated directory for an explicitly imported molecular file.
    """
    path = tmp_path / "sodium.mol"
    path.write_text(
        "Sodium\n  Test          3D\n\n"
        "  1  0  0  0  0  0  0  0  0  0999 V2000\n"
        "    0.0000    0.0000    0.0000 Na  0  0  0  0  0  0  0  0  0  0  0  0\n"
        "M  CHG  1   1   1\nM  END\n"
    )

    molecule = Molecule.from_file(path)

    state = molecule.records[0]
    assert isinstance(state, ElectronicState)
    assert state.charge.value == "1"
    assert state.multiplicity.value == "1"


def test_import_rejects_multiple_molecular_records(tmp_path: Path) -> None:
    """Reject a trajectory instead of silently taking its first geometry.

    Args:
        tmp_path: Isolated directory for an explicitly imported molecular file.
    """
    path = tmp_path / "trajectory.sdf"
    record = (
        "Helium\n  Test          3D\n\n"
        "  1  0  0  0  0  0  0  0  0  0  0999 V2000\n"
        "    0.0000    0.0000    0.0000 He  0  0  0  0  0  0  0  0  0  0  0  0\n"
        "M  END\n$$$$\n"
    )
    path.write_text(record + record)

    with pytest.raises(ValueError, match="multiple records"):
        Molecule.from_file(path)


@pytest.mark.parametrize("file_format", ["mol", "unsupported-format"])
def test_import_rejects_invalid_file_or_format(
    tmp_path: Path, file_format: str
) -> None:
    """Report backend import failure rather than constructing an empty molecule.

    Args:
        tmp_path: Isolated directory for an explicitly imported molecular file.
        file_format: Recognized format with invalid data, or an unknown format.
    """
    path = tmp_path / "invalid"
    path.write_text("not a molecule\n")

    with pytest.raises(ValueError, match=r"could not read|Unsupported"):
        Molecule.from_file(path, file_format=file_format)
