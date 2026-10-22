# Python job workflow

## Choose how to author the input

Choose the interface from the task, then discover its current exports, field
descriptions, signatures, and relevant command help. These approaches compose;
a job can use the builder for molecular preparation and formal reasoning for
its calculation plan.

| Approach | Use it when |
| --- | --- |
| Handwritten Psithon | A small, fully specified input or focused text edit is clearest, or a native feature needs direct syntax. Validate the complete input afterward. Prefer a small text edit when original comments and layout must remain intact. |
| Low-level editable input records (`psi4_parser.job`) | You need to construct or edit native blocks, symbolic coordinates, settings, or mixed Psithon/Python as structured data. This is particularly useful for existing inputs. Emission rebuilds native layout. |
| Builder (`psi4_parser.builder`) | You are generating new jobs programmatically, transforming molecular geometry, applying atom-based constraints, or composing reusable components and parameter sweeps. |
| Formal reasoning (`psi4_parser.formal`) | You need to translate scientific requirements into a plan and check goal completeness, geometry dependencies, permitted choices, quantities, or formulas against independent intent. Use the builder for molecular preparation. |

The editable input records differ from parser syntax trees and the translated
Python AST. Discover `parse()` when original source positions or syntax analysis
matter, and `build_ast()` for analysis of translated Python. These inspection
interfaces are not the normal job-authoring path.

A handwritten or builder-only section is outside a formal plan's checked scope.
If formal reasoning cannot cover a required feature, report that gap rather than
weakening the request to pass. Changing exported text requires updating the
source plan/request and reverifying before claiming the modified input is checked.

## Construct with the builder

Explore the builder's public exports and the specific helpers needed for the
task. Its docstrings describe geometry units, atom selections, symmetry,
references, constraints, and control flow.

Use Psi4's executable or Python API for separately requested runtime investigation
or execution. Construction uses inspectable builder scripts and inputs without
examining the target environment.

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

For independent scientific requirements, permitted choices, or proved
relationships between geometries, models, and quantities, use the
[planning skill](../skills/plan-calculations/SKILL.md) and
[formal workflow](formal.md). Save the scientific request independently, supply
matching capability evidence, and propose or verify a plan before export.
`ScientificRequest`, formal `Plan`, and builder `JobSpec` are distinct formats.

For a fully declared ordinary builder call, set `isolate_options=True` and put
its required options in `local_options`. That call starts from native defaults
and restores captured option state afterward. Ordinary helpers otherwise keep
ambient options available; formal construction always enables isolation. Process
resources and unlisted plugin state remain separate. See the
[isolation guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-isolation.md)
at the selected runtime ref.

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
