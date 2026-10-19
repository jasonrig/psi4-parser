"""Build a frozen C-C optimization after atom reordering and dummy insertion."""

from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    compose,
    distance,
    freeze,
    molecule,
    optimize,
    options,
    render_job,
    reorder_atoms,
    to_zmatrix,
)

acetylene = Molecule.from_xyz(
    "4\nAcetylene\nH 0 0 0\nC 0 0 1.06\nC 0 0 2.26\nH 0 0 3.32\n"
)
geometry = (
    acetylene
    | reorder_atoms(("a2", "a1", "a3", "a4"))
    | to_zmatrix(frame="canonical", allow_dummies=True)
)
system = molecule("acetylene", geometry)
job = compose(
    system,
    options(basis="sto-3g", scf_type="pk"),
    optimize(
        "scf",
        molecule=system.ref,
        constraints=(freeze(distance("a2", "a3")),),
        assign="e_opt",
    ),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
