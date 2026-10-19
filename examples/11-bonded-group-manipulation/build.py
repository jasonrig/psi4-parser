"""Build methanol jobs after moving its bonded OH group and its full frame."""

from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    angstrom,
    bohr,
    compose,
    connected_side,
    degrees,
    energy,
    molecule,
    options,
    render_job,
    rotate,
    set_angle,
    set_distance,
    translate,
)

methanol = Molecule.from_file(Path(__file__).with_name("methanol.sdf"))
hydroxyl = connected_side(methanol, "a1", "a2")
geometry = (
    methanol
    | set_distance(("a1", "a2"), angstrom(1.5), moving=hydroxyl)
    | set_angle(("a3", "a1", "a2"), degrees(115), moving=hydroxyl)
)
moved = (
    geometry
    | rotate(
        (1.0, 2.0, 3.0),
        degrees(37),
        origin=(angstrom(0.2), angstrom(-0.4), angstrom(0.1)),
    )
    | translate((bohr(2.0), angstrom(-1.0), angstrom(0.5)))
)
changed = molecule("changed", geometry)
transformed = molecule("transformed", moved)
job = compose(
    options(basis="sto-3g", scf_type="pk", e_convergence=1e-10, d_convergence=1e-10),
    changed,
    energy("scf", molecule=changed.ref, assign="e_changed"),
    transformed,
    energy("scf", molecule=transformed.ref, assign="e_transformed"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
