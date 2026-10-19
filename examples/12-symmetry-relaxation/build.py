"""Build equivalent Cs and explicitly relaxed C1 jobs for distorted water."""

from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    angstrom,
    compose,
    energy,
    molecule,
    options,
    render_job,
    set_distance,
    with_symmetry,
)

water = Molecule.from_xyz(
    "3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n"
) | with_symmetry("c2v")
changed = water | set_distance(("a1", "a2"), angstrom(1.2), moving=("a2",))
lowered = molecule("lowered", changed)
relaxed = molecule("relaxed", changed | with_symmetry("c1"))
job = compose(
    options(basis="sto-3g", scf_type="pk", e_convergence=1e-10, d_convergence=1e-10),
    lowered,
    energy("scf", molecule=lowered.ref, assign="e_cs"),
    relaxed,
    energy("scf", molecule=relaxed.ref, assign="e_c1"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
