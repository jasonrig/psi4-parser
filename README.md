# Psi4 parser

Validate, format, and build native Psi4 (**Psithon**) input files from Python.
Check handwritten or generated jobs before submitting them to Psi4, edit their
molecules and settings, or save them as JSON for later use.

These operations do not execute the input or run calculations. Psi4 and Java are
not required.

## Installation

Requires Python **3.15 or later**. From a checkout of this repository:

```sh
uv sync --locked --no-dev
```

## Validate input

```python
from psi4_parser import validate

source = """molecule h2 {
H
H 1 0.74
}
set basis sto-3g
energy('scf')
"""

diagnostics = validate(source)
for diagnostic in diagnostics:
    print(f"{diagnostic.line}:{diagnostic.column}: {diagnostic.message}")
```

`validate()` returns an empty tuple when the input passes validation. Otherwise,
each diagnostic gives a one-based `line`, a zero-based `column`, and a `message`.

Validation checks native input syntax and embedded Python, including scope rules
such as where `return` is allowed. Psi4 still checks whether the requested
calculation is valid: available methods and options, molecular consistency,
referenced files, basis/ECP data, and external solver settings.

To validate a file from the command line:

```sh
uv run psi4-parser validate input.dat
uv run psi4-parser validate job.json --from json
```

Validation exits with 0 for valid input, 1 for invalid input, and 2 for usage or
file errors. Diagnostics go to stderr; successful validation produces no output.

## Format input

```sh
uv run psi4-parser format show input.dat    # print formatted source
uv run psi4-parser format diff input.dat    # review changes
uv run psi4-parser format check input.dat   # check formatting
uv run psi4-parser format write input.dat   # verify, then replace the file
```

`show`, `diff`, and `check` read UTF-8 standard input when no path is given or the
path is `-`. `diff`, `check`, and `write` accept multiple files; standard input
must be used on its own. `write` requires file paths and verifies all inputs
before replacing any files.

`check` exits with 0 when formatting is unchanged, 1 when changes are needed, and
2 when checking fails. `show`, `diff`, and `write` exit with 0 on success and 2 on
failure.

To format input from Python:

```python
from psi4_parser import format_source

source = "set basis sto-3g\n"
formatted = format_source(source)
```

The formatter applies PEP 8 spacing and indentation while retaining existing
Python line breaks. It aligns molecule coordinates, numeric arrays, and option
values, and separates standalone native blocks from neighboring statements with
one blank line.

Inline comments use two spaces before the hash and one space before their text.
Standalone comments align with their enclosing scope. Comment wording, literal
spelling, data rows, and embedded solver text are preserved. Exceptional comment
gaps that affect Psi4's interpretation remain unchanged.
Results are validated and checked for preservation before being returned or
written. Invalid input raises `InvalidInputError`; a failed preservation check
raises `FormattingError`. See the [formatting guide](docs/formatting.md) for the
full style and the limits of these checks.

## Compose jobs with Python

Build inputs from reusable components and apply molecular transformations with
pipelines. Nothing runs until you submit the generated input to Psi4.

```python
from psi4_parser.builder import JobSpec, Molecule, energy, molecule, options, render_job

geometry = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n")
h2 = molecule("h2", geometry).with_comment("Hydrogen in a minimal basis.")
job = JobSpec() | h2 | options(basis="sto-3g") | energy("scf", molecule=h2.ref)
source = render_job(job)
```

`compose(h2, options(...), calculation)` and `h2 + options(...) + calculation`
also build ordered jobs. Components and transformations return new values, so
the originals can be reused. Use `with_comment(text)` to attach leading block
comments; multiline comments stay with their component.

The builder supports geometry edits, named Z-matrix parameters, fragments,
optimization constraints, and all native block families. Method names and extra
calculation arguments remain open. See [building jobs](docs/building-jobs.md)
for functional examples, file imports, constraints, and saving specifications
as JSON.

See the [runnable examples](examples/README.md) for builder scripts, rendered
inputs, and recorded Psi4 calculation outputs.

## Read and build jobs

Use `psi4_parser.job` to work with molecules, options, basis definitions, and
other job components. Read an existing input with `read_job(source)`, or combine
components into a new `Job`:

```python
from psi4_parser.job import (
    Job,
    Molecule,
    OptionAssignment,
    OptionExpression,
    Python,
    SetOptions,
    emit_job,
)

molecule = Molecule.from_xyz(
    "2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n",
    name="h2",
)
options = SetOptions(
    assignments=(
        OptionAssignment(key="basis", value=OptionExpression(source="sto-3g")),
    ),
)
job = Job(body=(molecule, options, Python(source="energy('scf', molecule=h2)")))
generated = emit_job(job)
```

`emit_job()` returns input text after validating the complete job, including its
Python statements. It raises `JobSyntaxError` if the input is invalid. Writing a
structured job regenerates native block layout. Comments attached to native
syntax are not retained.

Molecules support Cartesian and Z-matrix coordinates, symbolic variables,
fragments, overall and fragment charge and multiplicity, ghosts, and isotopes.
Use `Molecule.from_fragments()` to combine fragments, `with_coordinates()` to
replace an atom's coordinates, or `with_variable()` to change a declared geometry
parameter. Edits return a new molecule.

See [constructing native jobs](docs/native-jobs.md) for geometry edits, atom
references, constraints, and mixed Python/native jobs.

### Save and load jobs

Store jobs as JSON, restore them later, or export a JSON Schema for checking
documents produced by other tools:

```python
from psi4_parser.job import Job, emit_job, read_job

job = read_job("set basis sto-3g\n")
document = job.model_dump_json()
schema = Job.model_json_schema()
restored = Job.model_validate_json(document)
generated = emit_job(restored)
```

Loading JSON checks the document structure. Call `emit_job()` to also check the
complete input syntax and Python context. Reading and loading jobs do not open
referenced geometry files or execute Python statements.

The CLI can convert between Psithon and the same job JSON, or export its schema:

```sh
uv run psi4-parser convert input.dat --from psithon --to json -o job.json
uv run psi4-parser convert job.json --from json --to psithon -o input.dat
uv run psi4-parser schema -o job.schema.json
```

Omit the input path or use `-` to read stdin. Output goes to stdout unless `-o`
names a file; `-o -` also selects stdout. Conversion validates the complete job
before writing any output and exits with 2 if conversion fails. For example,
this pipeline validates the converted JSON without creating a file:

```sh
uv run psi4-parser convert input.dat --from psithon --to json \
    | uv run psi4-parser validate --from json
```

Conversion requires different input and output formats. A Psithon round trip
regenerates native layout and omits syntax comments. Custom atom IDs are
retained in JSON; reading Psithon assigns new IDs because the language does not
encode them.

### Import molecular files

Use `Molecule.from_xyz(text)` for XYZ text and `Molecule.from_file(path)` for
molecular files. Molecular symmetry detection uses MolSym, and edits warn before
lowering an incompatible computational symmetry request. Open Babel is included
in the normal installation and provides
support for additional file formats. Imports retain atom order, Cartesian
positions, isotopes, and available electronic-state information. Files must
contain one molecule; Psi4 fragments are declared explicitly.

The builder exposes bond perception as an explicit import choice. See the
[building guide](docs/building-jobs.md) for connectivity and state handling.

## Inspect source

`parse(source)` gives access to the input's syntax tree, tokens, original text,
and diagnostics. Its `source_text(node)` and `source_span(node)` helpers locate
the original text for a tree node or token, including comments and line endings.
Read files with `Path.read_bytes().decode("utf-8")` to retain their line endings.

For Python AST analysis, use `build_ast(source)`. See the
[parser API details](grammar/README.md) for source access and
the [formatting guide](docs/formatting.md) for AST contents and comparison.

## Supported input

The parser supports Python 3.15 statements and expressions alongside Psi4's
native directives:

- Molecular geometries, including Cartesian and Z-matrix coordinates,
  fragments, variables, ghost atoms, and geometry settings.
- Inline and block options, module-specific settings, and multiline arrays.
- Basis and ECP blocks, memory directives, and external potentials.
- Embedded PCM sections and literal CFOUR input.

The current compatibility target is Psi4 **1.12a1.dev43**, Python **3.15** syntax,
and QCEElemental **0.51.3**. Exact versions and source fingerprints are recorded
in the [compatibility manifest](compatibility/psi4.json).

## Provenance

The Python lexer/parser grammars and vendored
[`PythonLexerBase.py`](src/psi4_parser/_vendor/PythonLexerBase.py) derive from
Robert Einhorn's Python 3.14 grammar in
[antlr/grammars-v4](https://github.com/antlr/grammars-v4/tree/b8da12293f626bc561e5c05c4011f5b5b5e778a8/python/python3_14),
commit `b8da12293f626bc561e5c05c4011f5b5b5e778a8`. Their MIT copyright and license
notices remain in the source files. Local adaptations add Psithon and Python 3.15
support, checked against CPython's grammar and syntax regression tests.

Native syntax was audited against Psi4 commit
`60c9b2a773c05abc26991c5ed48cf9862cdb4978`, particularly its input preprocessor,
and the QCEElemental molecule reader. The fixture collection includes upstream
Psi4 inputs and CPython regression examples; its
[provenance and license references](test/fixtures/README.md) are retained with
the fixtures.

## Further documentation

- [Grammar reference and maintenance](grammar/README.md)
- [Compatibility updates and synchronization](compatibility/README.md)
