"""Compare point, Gaussian, and AO-matrix external potentials for H2."""

from pathlib import Path

from psi4_parser.builder import (
    ExternalPointCharge,
    ExternalPotential,
    GaussianCharge,
    Molecule,
    PotentialMatrix,
    angstrom,
    bohr,
    call,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

geometry = Molecule(
    atoms=Molecule.from_xyz("2\nH2\nH 0 0 -.37\nH 0 0 .37\n").atoms,
    symmetry="c1",
    fixed_com=True,
    fixed_orientation=True,
)
hydrogen = molecule("hydrogen", geometry)
point = ExternalPointCharge(
    charge=0.05,
    position=(angstrom(0), angstrom(0), angstrom(2.5)),
)
gaussian = GaussianCharge(
    charge=-0.05,
    position=(bohr(0), bohr(0), bohr(-5)),
    exponent=0.7,
)
combined = ExternalPotential(
    points=(point,),
    diffuse=(gaussian,),
    matrix=PotentialMatrix(((0.01, 0.0), (0.0, -0.01))),
)
reference = energy("scf", molecule=hydrogen.ref, assign="e_reference")
point_energy = energy(
    "scf",
    molecule=hydrogen.ref,
    external_potentials=ExternalPotential(points=(point,)),
    assign="e_point",
)
gaussian_energy = energy(
    "scf",
    molecule=hydrogen.ref,
    external_potentials=ExternalPotential(diffuse=(gaussian,)),
    assign="e_gaussian",
)
combined_energy = energy(
    "scf",
    molecule=hydrogen.ref,
    external_potentials=combined,
    assign="e_combined",
).with_comment("STO-3G has two AO functions, so the potential matrix is 2 by 2.")
job = compose(
    hydrogen,
    options(basis="sto-3g", scf_type="pk"),
    reference,
    point_energy,
    gaussian_energy,
    combined_energy,
    call(
        "print",
        "Reference, point, Gaussian, combined energies (hartree):",
        reference.ref,
        point_energy.ref,
        gaussian_energy.ref,
        combined_energy.ref,
    ),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
