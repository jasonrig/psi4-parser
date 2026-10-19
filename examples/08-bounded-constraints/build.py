"""Build bond-length and bond-angle optimizations with bounds in mixed units."""

from math import pi
from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    angle,
    bohr,
    bound,
    compose,
    degrees,
    distance,
    molecule,
    optimize,
    options,
    radians,
    render_job,
    set_angle,
)

hydrogen = molecule("hydrogen", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 1.0\n"))
geometry = Molecule.from_xyz("3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n")
water = molecule(
    "water", geometry | set_angle(("a2", "a1", "a3"), degrees(85), moving=("a3",))
)
job = compose(
    options(basis="sto-3g", scf_type="pk"),
    hydrogen,
    optimize(
        "scf",
        molecule=hydrogen.ref,
        assign="e_bounded_bond",
        constraints=(bound(distance("a1", "a2"), bohr(1.8), bohr(2.0)),),
    ),
    water,
    optimize(
        "scf",
        molecule=water.ref,
        assign="e_bounded_angle",
        constraints=(
            bound(angle("a2", "a1", "a3"), radians(4 * pi / 9), radians(pi / 2)),
        ),
    ),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
