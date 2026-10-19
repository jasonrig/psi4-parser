"""Build the supplied constrained peroxide optimization."""

from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    compose,
    dihedral,
    freeze,
    molecule,
    optimize,
    options,
    render_job,
)

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
hooh = molecule("hooh", peroxide)
job = compose(
    hooh,
    options(basis="cc-pvdz"),
    optimize(
        "scf",
        molecule=hooh.ref,
        constraints=(freeze(dihedral("a1", "a2", "a3", "a4")),),
        local_options=(options(modules=("scf",), maxiter=100),),
        assign="e_opt",
    ),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
