"""Compose nested basis and method loops with a conditional calculation."""

from pathlib import Path

from psi4_parser.builder import (
    Expression,
    Molecule,
    Reference,
    call,
    compose,
    energy,
    for_each,
    if_else,
    molecule,
    options,
    render_job,
)

hydrogen = molecule("hydrogen", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
method = Reference(name="method")
basis = Reference(name="basis_name")
calculation = if_else(
    Expression(source="method == 'scf'"),
    compose(energy(method, molecule=hydrogen.ref, assign="e_result")),
    otherwise=compose(
        energy(method, molecule=hydrogen.ref, freeze_core=True, assign="e_result")
    ),
)
methods = for_each(
    "method",
    ["scf", "mp2"],
    compose(
        calculation,
        call("print", basis, method, Reference(name="e_result")),
    ),
).with_comment("Both conditional branches bind e_result before it is used.")
job = compose(
    hydrogen,
    options(scf_type="pk", mp2_type="conv"),
    for_each(
        "basis_name",
        ["sto-3g", "6-31g"],
        compose(
            options(basis=basis),
            methods,
            call("psi4.core.clean").with_comment(
                "Clear correlated integral files before changing basis."
            ),
        ),
    ).with_comment("The basis and method loops run in the generated Psi4 input."),
)

source = render_job(job)
Path(__file__).with_name("input.dat").write_text(source, encoding="utf-8")
