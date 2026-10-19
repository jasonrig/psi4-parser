"""Build an H2 energy calculation in an external point-charge field."""

from pathlib import Path

from psi4_parser.builder import (
    Atom,
    Cartesian,
    Molecule,
    Nucleus,
    angstrom,
    bohr,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

geometry = Molecule(
    atoms=(
        Atom(
            id="a1",
            nucleus=Nucleus(label="H"),
            coordinates=Cartesian(x=0.0, y=0.0, z=-0.37),
        ),
        Atom(
            id="a2",
            nucleus=Nucleus(label="H"),
            coordinates=Cartesian(x=0.0, y=0.0, z=0.37),
        ),
    ),
    symmetry="c1",
    fixed_com=True,
    fixed_orientation=True,
)
hydrogen = molecule("hydrogen", geometry)
z_bohr = angstrom(2.5).angstroms / bohr(1.0).angstroms
job = compose(
    hydrogen,
    options(basis="cc-pvdz", scf_type="pk"),
    energy(
        "scf",
        molecule=hydrogen.ref,
        external_potentials=[
            [0.1, [0.0, 0.0, z_bohr]],
            [-0.1, [0.0, 0.0, -z_bohr]],
        ],
        assign="e_field",
    ),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
