"""Build gas-phase and water-PCM single-point energies for the same water molecule."""

from pathlib import Path

from psi4_parser.builder import (
    PCM,
    Molecule,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

water = molecule(
    "water", Molecule.from_xyz("3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n")
)
solvent = PCM(
    body=(
        "\n  Units = Angstrom\n"
        "  Medium {\n    SolverType = IEFPCM\n    Solvent = Water\n  }\n"
        "  Cavity {\n    RadiiSet = UFF\n    Type = GePol\n    Scaling = False\n"
        "    Area = 0.3\n    Mode = Implicit\n  }\n"
    )
)
job = compose(
    water,
    options(basis="sto-3g", scf_type="pk"),
    energy("scf", molecule=water.ref, assign="e_gas"),
    solvent,
    options(pcm=True, pcm_scf_type="total"),
    energy("scf", molecule=water.ref, assign="e_pcm"),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
