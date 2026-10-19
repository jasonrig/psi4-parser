"""Build SCF and MP2 calculations connected by explicit wavefunction references."""

from pathlib import Path

from psi4_parser.builder import (
    Molecule,
    Reference,
    call,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

hydrogen = molecule("hydrogen", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
job = compose(
    hydrogen,
    options(basis="sto-3g", scf_type="pk", mp2_type="conv"),
    energy("scf", molecule=hydrogen.ref, return_wfn=True, assign=("e_hf", "wfn")),
    call("psi4.oeprop", Reference(name="wfn"), "DIPOLE"),
    energy(
        "mp2",
        molecule=hydrogen.ref,
        ref_wfn=Reference(name="wfn"),
        return_wfn=True,
        assign=("e_mp2", "mp2_wfn"),
    ),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
