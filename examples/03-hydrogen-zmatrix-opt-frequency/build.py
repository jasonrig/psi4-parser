"""Build an H2 optimization and frequency job from an edited Z-matrix."""

from pathlib import Path

from psi4_parser.builder import (
    JobSpec,
    Molecule,
    NamedCoordinate,
    angstrom,
    distance,
    frequency,
    molecule,
    optimize,
    options,
    render_job,
    to_zmatrix,
    with_parameter,
)

geometry = (
    Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 .74\n")
    | to_zmatrix(
        frame="canonical",
        requested=(NamedCoordinate(name="R", coordinate=distance("a1", "a2")),),
    )
    | with_parameter("R", angstrom(0.85))
)
hydrogen = molecule("hydrogen", geometry)
job = (
    JobSpec()
    | hydrogen
    | options(basis="sto-3g", scf_type="pk")
    | optimize("scf", molecule=hydrogen.ref, assign="e_opt")
    | frequency("scf", molecule=hydrogen.ref, assign="e_freq")
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
