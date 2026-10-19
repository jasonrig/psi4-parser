"""Build an FI-SAPT calculation with separate fields on two H2 fragments."""

from pathlib import Path

from psi4_parser.builder import (
    ElectronicState,
    ExternalPointCharge,
    ExternalPotential,
    FragmentPotential,
    FragmentPotentials,
    Molecule,
    angstrom,
    assemble_fragments,
    compose,
    energy,
    molecule,
    options,
    render_job,
    translate,
)

singlet = ElectronicState(charge=0, multiplicity=1)
left = Molecule.from_xyz("2\nH2\nH 0 0 -.37\nH 0 0 .37\n", state=singlet)
right = left | translate((angstrom(3), angstrom(0), angstrom(0)))
assembled = assemble_fragments(("left", left), ("right", right), state=singlet)
dimer = molecule(
    "dimer",
    Molecule(
        atoms=assembled.atoms,
        fragments=assembled.fragments,
        state=singlet,
        symmetry="c1",
        fixed_com=True,
        fixed_orientation=True,
    ),
)
fields = FragmentPotentials(
    fragments=(
        FragmentPotential(
            fragment="A",
            potential=ExternalPotential(
                points=(
                    ExternalPointCharge(
                        charge=0.05,
                        position=(angstrom(-3), angstrom(0), angstrom(0)),
                    ),
                ),
            ),
        ),
        FragmentPotential(
            fragment="B",
            potential=ExternalPotential(
                points=(
                    ExternalPointCharge(
                        charge=-0.05,
                        position=(angstrom(6), angstrom(0), angstrom(0)),
                    ),
                ),
            ),
        ),
    ),
)
job = compose(
    dimer,
    options(basis="cc-pvdz", scf_type="df", freeze_core=True),
    energy(
        "fisapt0",
        molecule=dimer.ref,
        external_potentials=fields,
        assign="e_interaction",
    ).with_comment("A and B refer to the first and second Psi4 fragments."),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
