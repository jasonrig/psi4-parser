"""Build catalog and embedded STO-3G calculations for the same H2 geometry."""

from pathlib import Path

from psi4_parser.builder import (
    Basis,
    BasisAssignment,
    BasisData,
    BasisLabel,
    Molecule,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

hydrogen = molecule("hydrogen", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
basis_lines = (
    "****\nH 0\nS 3 1.00\n"
    "3.42525091 0.15432897\n"
    "0.62391373 0.53532814\n"
    "0.16885540 0.44463454\n****"
).splitlines()
embedded = Basis(
    records=(
        BasisAssignment(basis="local_h", target="H"),
        BasisLabel(name="local_h"),
        *(BasisData(text=line) for line in basis_lines),
    )
)
job = compose(
    hydrogen,
    options(basis="sto-3g", scf_type="pk", e_convergence=1e-10, d_convergence=1e-10),
    energy("scf", molecule=hydrogen.ref, assign="e_catalog"),
    embedded,
    energy("scf", molecule=hydrogen.ref, assign="e_embedded"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
