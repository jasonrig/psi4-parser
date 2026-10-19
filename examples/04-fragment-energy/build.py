"""Build a single-point calculation for two explicit H2 fragments."""

from pathlib import Path

from psi4_parser.builder import (
    ElectronicState,
    Molecule,
    angstrom,
    assemble_fragments,
    energy,
    molecule,
    options,
    render_job,
    translate,
)

singlet = ElectronicState(charge=0, multiplicity=1)
left = Molecule.from_xyz("2\nHydrogen\nH 0 0 -.37\nH 0 0 .37\n", state=singlet)
right = left | translate((angstrom(3.0), angstrom(0.0), angstrom(0.0)))
geometry = assemble_fragments(("left", left), ("right", right), state=singlet)
dimer = molecule("dimer", geometry)
job = (
    dimer
    + options(basis="sto-3g", scf_type="pk")
    + energy("scf", molecule=dimer.ref, assign="e_dimer")
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
