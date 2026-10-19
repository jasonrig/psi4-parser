"""Build energy, gradient, and dipole calculations for C2v water."""

from pathlib import Path

from psi4_parser.builder import (
    Basis,
    BasisAssignment,
    Molecule,
    compose,
    energy,
    gradient,
    molecule,
    options,
    properties,
    render_job,
    with_symmetry,
)

geometry = Molecule.from_xyz(
    "3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n"
) | with_symmetry("c2v")
water = molecule("water", geometry)
job = compose(
    water,
    Basis(records=(BasisAssignment(basis="sto-3g"),)),
    options(scf_type="pk"),
    energy("scf", molecule=water.ref, assign="e_hf"),
    gradient("scf", molecule=water.ref, assign="g_hf"),
    properties("scf", molecule=water.ref, properties=["dipole"]),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
