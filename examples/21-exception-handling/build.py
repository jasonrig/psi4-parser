"""Handle a failed SCF attempt, then run a converged calculation."""

from pathlib import Path

from psi4_parser.builder import (
    ExceptionHandler,
    Expression,
    Molecule,
    Reference,
    TryBlock,
    call,
    compose,
    energy,
    for_each,
    molecule,
    options,
    render_job,
)

water = molecule(
    "water", Molecule.from_xyz("3\nWater\nO 0 0 0\nH 0 0 .96\nH .93 0 -.24\n")
)
attempt = TryBlock(
    body=compose(
        energy(
            "scf",
            molecule=water.ref,
            local_options=(options(modules=("scf",), maxiter=Reference(name="limit")),),
            assign="e_scf",
        )
    ),
    handlers=(
        ExceptionHandler(
            exception=Expression(
                source="psi4.driver.p4util.exceptions.SCFConvergenceError"
            ),
            name="error",
            body=compose(call("print", "SCF attempt failed:", Reference(name="error"))),
        ),
    ),
    otherwise=compose(
        call("print", "Converged energy (hartree):", Reference(name="e_scf"))
    ),
    finally_body=compose(
        call("psi4.core.clean"),
        call(
            "print",
            "Restored SCF maxiter:",
            Expression(source="psi4.core.get_option('SCF', 'MAXITER')"),
        ),
    ),
).with_comment(
    "One iteration intentionally fails; the second attempt allows 50.\n\n"
    "Step-local options are restored after either outcome."
)
job = compose(
    water,
    options(basis="sto-3g", scf_type="pk"),
    options(modules=("scf",), maxiter=37),
    for_each("limit", [1, 50], compose(attempt)),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
