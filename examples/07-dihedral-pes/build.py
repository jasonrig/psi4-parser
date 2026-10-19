"""Build a relaxed peroxide PES sweep using Cartesian dihedral manipulations."""

from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    compose,
    degrees,
    dihedral,
    freeze,
    molecule,
    optimize,
    options,
    render_job,
    set_dihedral,
)

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
torsion_atoms = ("a1", "a2", "a3", "a4")
job = compose(options(basis="cc-pvdz"))

for angle in range(30, 151, 30):
    geometry = peroxide | set_dihedral(torsion_atoms, degrees(angle), moving=("a4",))
    hooh = molecule(f"hooh_{angle}", geometry).with_comment(
        f"PES point: H-O-O-H dihedral = {angle} degrees."
    )
    job += compose(
        hooh,
        optimize(
            "scf",
            molecule=hooh.ref,
            constraints=(freeze(dihedral(*torsion_atoms)),),
            local_options=(options(modules=("scf",), maxiter=100),),
            assign=f"e_{angle}",
        ),
    )

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
