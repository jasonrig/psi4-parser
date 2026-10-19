"""Build equivalent internal and Cartesian peroxide jobs after parameter edits."""

from math import pi
from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    NamedCoordinate,
    bohr,
    compose,
    dihedral,
    distance,
    energy,
    molecule,
    options,
    radians,
    render_job,
    to_cartesian,
    to_zmatrix,
    with_parameter,
)

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
geometry = (
    peroxide
    | to_zmatrix(
        frame="canonical",
        requested=(
            NamedCoordinate(name="D", coordinate=dihedral("a1", "a2", "a3", "a4")),
            NamedCoordinate(name="R", coordinate=distance("a2", "a3")),
        ),
    )
    | with_parameter("D", radians(pi / 3))
    | with_parameter("R", bohr(2.7))
)
internal = molecule("internal", geometry)
cartesian = molecule("cartesian", to_cartesian(geometry))
job = compose(
    options(basis="sto-3g", scf_type="pk", e_convergence=1e-10, d_convergence=1e-10),
    internal,
    energy("scf", molecule=internal.ref, assign="e_internal"),
    cartesian,
    energy("scf", molecule=cartesian.ref, assign="e_cartesian"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
