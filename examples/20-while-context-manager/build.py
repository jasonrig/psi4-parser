"""Use a while loop to evaluate successive bases and save a results table."""

from pathlib import Path

from psi4_parser.builder import (
    Expression,
    Molecule,
    Reference,
    call,
    compose,
    energy,
    molecule,
    options,
    render_job,
    while_loop,
    with_context,
)

hydrogen = molecule("hydrogen", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
bases = call("iter", ["sto-3g", "6-31g"], assign="bases")
first_basis = call("next", bases.ref, None, assign="basis_name")
calculation = energy("scf", molecule=hydrogen.ref, assign="e_result")
sweep = while_loop(
    Expression(source="basis_name is not None"),
    compose(
        options(basis=first_basis.ref),
        calculation,
        call(
            "print",
            first_basis.ref,
            calculation.ref,
            file=Reference(name="summary"),
            sep=",",
        ),
        call("next", bases.ref, None, assign="basis_name"),
    ),
    otherwise=compose(call("print", "Basis sweep complete.")),
)
job = compose(
    hydrogen,
    options(scf_type="pk"),
    bases,
    first_basis,
    with_context(
        Expression(source="open('energies.csv', 'w', encoding='utf-8')"),
        compose(
            call("print", "basis,energy_hartree", file=Reference(name="summary")),
            sweep,
        ),
        target="summary",
    ).with_comment("The context manager closes the results file on every exit."),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
