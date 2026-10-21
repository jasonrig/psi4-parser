# Python job workflow

Prefer `psi4_parser.builder` for constructing and revising inputs. Explore its
public exports and the specific helpers needed for the task. Its docstrings
describe geometry units, atom selections, symmetry, references, constraints,
and control flow.

Use an available Psi4 executable or Python API for targeted runtime inspection
and calculation execution. Direct Python API use is also appropriate when it is
clearer for a required interface. Choose the approach that fits the task and
retain inspectable scripts and inputs.

Before expanding a large job, resolve ambiguities in essential inputs, requested
outputs, and choices that materially affect the result. Use the user's context
and prior decisions; ask only about consequential choices that remain unresolved.

A typical script reads a molecule, creates a named declaration, composes settings
and calculations in execution order, renders the job, and writes the input.
Inspect the current signatures before adapting this small example:

```python
from pathlib import Path

from psi4_parser.builder import Molecule, compose, energy, molecule, options, render_job

geometry = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n")
h2 = molecule("h2", geometry)
job = compose(h2, options(basis="sto-3g"), energy("scf", molecule=h2.ref))
Path(__file__).with_name("input.dat").write_text(render_job(job), encoding="utf-8")
```

Use named references from preceding declarations. Geometry operations return
new molecules; retain the original when generating independent variations.
Inspect the selected operation's help for moving atoms, units, frame changes,
and symmetry handling. Use explicit units and electronic states when the task
requires them. Rendering validates and formats the complete input; see the
[validation path](cli.md#check-input-without-running-calculations) for checking
saved input and distinguishing syntax checks from runtime inspection.

For existing input, explore `psi4_parser.job`, starting with `read_job()` and
`emit_job()`. Its editable records serve a different purpose from builder
components. Keep the appropriate model when editing or loading JSON; inspect
its own JSON Schema.

Check that the rendered input expresses the requested molecule, charge, spin,
method, basis, geometry changes, constraints, and calculation order. Syntax
validation alone cannot establish scientific suitability or installed Psi4
capabilities. Run calculations when the task calls for results or execution
checks, using the configured Psi4 environment. Retain relevant output and report
execution results separately from input validation. For input-only tasks,
construction and validation are sufficient.

Read fuller examples and explanations at the selected repository ref:

- [Building jobs](https://github.com/jasonrig/psi4-parser/blob/main/docs/building-jobs.md)
- [Runnable examples](https://github.com/jasonrig/psi4-parser/tree/main/examples)
- [Reading and editing input](https://github.com/jasonrig/psi4-parser/blob/main/docs/native-jobs.md)

Use the installed docstrings as the first reference; read only the guide sections
and examples needed for the task.
