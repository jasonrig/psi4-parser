"""Build a doublet deuterium calculation with a ghost hydrogen basis center."""

from pathlib import Path

from psi4_parser.builder import (
    Atom,
    Cartesian,
    ElectronicState,
    Molecule,
    Nucleus,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

geometry = Molecule(
    atoms=(
        Atom(
            id="deuterium",
            nucleus=Nucleus(label="H", mass=2.01410177812),
            coordinates=Cartesian(x=0.0, y=0.0, z=0.0),
        ),
        Atom(
            id="ghost",
            nucleus=Nucleus(label="H", ghost="at"),
            coordinates=Cartesian(x=0.0, y=0.0, z=1.5),
        ),
    ),
    state=ElectronicState(charge=0, multiplicity=2),
    symmetry="c1",
)
atom = molecule("deuterium", geometry)
job = compose(
    atom,
    options(basis="cc-pvdz", reference="uhf", scf_type="pk"),
    energy("scf", molecule=atom.ref, assign="e_atom"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
