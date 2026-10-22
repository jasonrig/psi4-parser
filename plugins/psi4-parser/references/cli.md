# CLI workflow

For checked scientific planning, use the separate `formal` command group and
[formal workflow](formal.md). Its compact JSON responses, persistent records,
independent request coverage, and scientific exit statuses differ from ordinary
input validation. Start with `psi4-parser formal --help` in the selected runtime.

Use the runtime from [runtime and discovery](runtime.md). Inspect command help
in that same environment:

```sh
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser validate --help
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser format --help
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser convert --help
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser schema --help
```

Select the operation by the requested outcome:

| Outcome | Command arguments after `psi4-parser` |
| --- | --- |
| Check input syntax | `validate input.dat` |
| Preview formatting | `format show input.dat` |
| Review formatting changes | `format diff input.dat` |
| Check formatting in automation | `format check input.dat` |
| Apply formatting | `format write input.dat` |
| Convert input to editable JSON | `convert input.dat --from psithon --to json -o job.json` |
| Convert editable JSON to input | `convert job.json --from json --to psithon -o input.dat` |
| Export the editable JSON format | `schema -o job.schema.json` |

Inspect leaf-command help for accepted paths, standard input, output flags, and
exit codes. Capture stderr and the exit status. A nonzero formatting check can
mean that a valid file needs formatting; it is distinct from a parsing error.
Preview changes before an in-place write and retain the requested destination.

## Check input without running calculations

For a builder specification, `render_job()` checks component references, atom
selections, and constraint definitions, then validates and formats the generated
input. It returns text without executing the generated calculation statements.
To check a saved input in the same runtime:

```sh
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser validate input.dat
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser format check input.dat
```

These commands check syntax and formatting without executing the input. Report
what was checked; successful validation does not establish scientific suitability,
method availability, or runtime dependencies.

For separately requested calculation results or execution checks, use the
operator's configured Psi4 environment and retain relevant output. Input-only
validation requires no target-runtime inspection. Report input diagnostics,
runtime failures, and execution results separately; runtime availability does
not gate input construction.

## JSON formats and further reference

CLI JSON and schema commands use `psi4_parser.job.Job`, which represents existing
input as editable records. Builder specifications use `psi4_parser.builder.JobSpec`;
inspect that model's `model_dump_json()`, `model_validate_json()`, and
`model_json_schema()` in Python when working with builder JSON.

Use the installed command help for exact behavior and the repository's
[formatting guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formatting.md)
for style details. Use the same repository ref as the runtime.
