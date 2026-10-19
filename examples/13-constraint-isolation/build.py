"""Build constrained and unconstrained optimizations of the same molecule."""

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

geometry = Molecule.from_xyz(
    "4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n"
) | set_dihedral(("a1", "a2", "a3", "a4"), degrees(150), moving=("a4",))
peroxide = molecule("peroxide", geometry)
job = compose(
    peroxide,
    options(basis="cc-pvdz"),
    options(modules=("scf",), maxiter=37),
    optimize(
        "scf",
        molecule=peroxide.ref,
        constraints=(freeze(dihedral("a1", "a2", "a3", "a4")),),
        local_options=(options(modules=("scf",), maxiter=100),),
        assign="e_constrained",
    ),
    optimize("scf", molecule=peroxide.ref, assign="e_unconstrained"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
