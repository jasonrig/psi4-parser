# Psi4 parser

Validate, format, and construct Psi4 input files from Python. Psi4's input format,
**Psithon**, combines Python statements with blocks for molecules, settings,
basis sets, and solver configuration.

Use the builder to create jobs from reusable components, or read an existing
input to inspect and edit its contents. Both APIs support JSON and JSON Schema.

## Install

Requires Python **3.15 or later**. From this checkout:

```sh
uv sync --locked --no-dev
```

Psi4 is needed to execute generated inputs. Java is needed only to regenerate
the parser.

## Agent plugin

Install the [Psi4 Inputs plugin](plugins/psi4-parser/README.md) in Codex or
Claude Code to build jobs with Python scripts and check existing inputs. Its
skills discover the installed API and CLI help, with `uvx` commands that run
directly from this repository.

## Validate input

```sh
uv run psi4-parser validate input.dat
uv run psi4-parser validate job.json --from json
```

`job.json` uses the editable-input format from `psi4_parser.job`, described below.
Omit the path or use `-` to read standard input. Diagnostics go to stderr;
successful validation produces no output.

Exit codes are 0 for success, 1 for invalid Psithon or JSON jobs, and 2 for
usage or file errors.

From Python:

```python
from psi4_parser import validate

source = """molecule h2 {
H
H 1 0.74
}
set basis sto-3g
energy('scf')
"""

for diagnostic in validate(source):
    print(f"{diagnostic.line}:{diagnostic.column}: {diagnostic.message}")
```

`validate()` returns an empty tuple for valid input. Diagnostics use one-based
lines and zero-based columns. Validation checks syntax and Python scope rules,
such as where `return` is allowed. Psi4 checks method and option availability,
molecular consistency, referenced files, basis data, and solver settings.

## Format input

```sh
uv run psi4-parser format show input.dat    # print formatted input
uv run psi4-parser format diff input.dat    # show changes
uv run psi4-parser format check input.dat   # check formatting
uv run psi4-parser format write input.dat   # replace the file
```

`show`, `diff`, and `check` accept standard input when the path is omitted or `-`.
`diff`, `check`, and `write` accept multiple files; standard input must be used
alone. `write` requires file paths and verifies every input before replacing
any file.

`check` exits with 0 for unchanged input, 1 when formatting is needed, and 2 on
error. The other formatting commands exit with 0 on success and 2 on error.

```python
from psi4_parser import format_source

formatted = format_source("set basis sto-3g\n")
```

Formatting uses four-space indentation and PEP 8 spacing while retaining Python
line breaks. It aligns coordinates and numeric arrays, separates native blocks
from neighboring statements, and standardizes comment spacing. Literal data and
comment wording are retained. Every result passes syntax, program-preservation,
and repeat-formatting checks.

Invalid input raises `InvalidInputError`; a failed preservation check raises
`FormattingError`. See the [formatting guide](docs/formatting.md) for the style,
source-sensitive exceptions, and verification limits.

## Build jobs with Python

```python
from psi4_parser.builder import JobSpec, Molecule, energy, molecule, options, render_job

geometry = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n")
h2 = molecule("h2", geometry).with_comment("Hydrogen in a minimal basis.")
job = JobSpec() | h2 | options(basis="sto-3g") | energy("scf", molecule=h2.ref)
source = render_job(job)
```

Compose components in execution order using `|`, `+`, or `compose(...)`.
Molecular transformations return new geometries, so starting structures can be
reused. `with_comment(text)` attaches leading comment lines to a component.

The builder supports fragments, charge and spin, geometry edits, coordinate
conversion, symmetry, optimization constraints, external potentials, and nested
Python control flow. Method names and extra calculation arguments follow Psi4's
interfaces. Rendering checks declarations and references across the job.

See [building jobs](docs/building-jobs.md) for the API and
[runnable examples](examples/README.md) for scripts, inputs, and recorded outputs.
The API docstrings also provide units, reference rules, and examples through
Python's `help()`.

## Create inputs through MCP

```sh
uv run psi4-parser mcp
```

The `render_psithon` tool accepts molecules, settings, and calculation steps as
JSON. It returns Psi4 input text or the full path of a written file. Copy or move
written files to a durable location.

See [MCP setup and requests](docs/mcp.md).

## Read and edit existing input

```python
from psi4_parser.job import Job, Molecule, Number, emit_job, read_job

job = read_job("molecule h2 {\nH\nH 1 R\nR = 0.74\n}\nset basis sto-3g\n")
h2 = job.body[0]
assert isinstance(h2, Molecule)
changed = h2.with_variable("R", Number(value="0.8"))
source = emit_job(Job(body=(changed, *job.body[1:])))
```

`psi4_parser.job` represents native blocks as editable records and Python
statements as source text. Edits return new values. `emit_job()` rebuilds native
layout and validates the complete input; invalid syntax raises `JobSyntaxError`.
Use `parse()` when original layout and syntax comments need to be retained.

Molecular records cover Cartesian and Z-matrix coordinates, variables, fragments,
overall and fragment electronic states, isotopes, ghosts, and geometry directives.
See [reading and constructing input](docs/native-jobs.md) for details.

### Save, load, and convert JSON

```python
from psi4_parser.job import Job, read_job

job = read_job("set basis sto-3g\n")
document = job.model_dump_json()
restored = Job.model_validate_json(document)
schema = Job.model_json_schema()
```

Loading checks the JSON structure; `emit_job()` also checks the complete input
syntax. The CLI converts this same `Job` format:

```sh
uv run psi4-parser convert input.dat --from psithon --to json -o job.json
uv run psi4-parser convert job.json --from json --to psithon -o input.dat
uv run psi4-parser schema -o job.schema.json
```

Omit the input path or use `-` for standard input. Output goes to stdout unless
`-o` names a file; `-o -` also selects stdout. Conversion requires different
formats, checks the complete job before writing, and exits with 2 on error.

A Psithon round trip rebuilds native layout. JSON retains custom atom IDs;
reading Psithon assigns new IDs because the input language does not encode them.

Builder JSON uses `JobSpec`, a separate format for components, references,
constraints, and comments. Load it through the
[builder API](docs/building-jobs.md#save-specifications-and-emit-input) or pass it
to the MCP tool.

## Inspect syntax and source

`parse(source)` returns the syntax tree, tokens, original text, and diagnostics.
`source_text(node)` and `source_span(node)` locate a tree node or token in that
original text. To retain file line endings, read bytes and decode as UTF-8.

`build_ast(source)` provides a Python abstract syntax tree for analysis. See the
[parser reference](grammar/README.md) for source access and the
[formatting guide](docs/formatting.md#program-comparison) for AST comparison.

## Compatibility and provenance

The compatibility target is Psi4 **1.12a1.dev43**, Python **3.15** syntax, and
QCEElemental **0.51.3**. Exact versions and source fingerprints are recorded in
[the compatibility manifest](compatibility/psi4.json). The supported native
syntax includes molecules, options and arrays, basis/ECP blocks, memory,
external-potential blocks, PCM, and CFOUR.

The Python grammars and vendored
[`PythonLexerBase.py`](src/psi4_parser/_vendor/PythonLexerBase.py) derive from
Robert Einhorn's Python 3.14 grammar in
[antlr/grammars-v4](https://github.com/antlr/grammars-v4/tree/b8da12293f626bc561e5c05c4011f5b5b5e778a8/python/python3_14),
commit `b8da12293f626bc561e5c05c4011f5b5b5e778a8`. MIT copyright and license
notices remain in those files. Local adaptations support Psithon and Python 3.15.

Native syntax was audited against Psi4 commit
`60c9b2a773c05abc26991c5ed48cf9862cdb4978`, its input preprocessor, and the
QCEElemental molecule reader. The [fixture guide](test/fixtures/README.md) records
upstream inputs, CPython examples, and license references.

For maintenance, see the [grammar guide](grammar/README.md) and
[verified upgrade workflow](compatibility/README.md).
