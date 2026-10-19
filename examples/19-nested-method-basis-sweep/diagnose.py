"""Report a result reference that is not guaranteed after a loop."""

import sys

from pydantic import TypeAdapter

from psi4_parser.builder import (
    CompilationDiagnostic,
    CompilationError,
    Reference,
    call,
    compose,
    energy,
    for_each,
    render_job,
)

job = compose(
    for_each("method", ["scf"], compose(energy("scf", assign="e_result"))),
    call("print", Reference(name="e_result")),
)

try:
    render_job(job)
except CompilationError as error:
    diagnostics = TypeAdapter(tuple[CompilationDiagnostic, ...])
    sys.stdout.write(diagnostics.dump_json(error.diagnostics, indent=2).decode() + "\n")
