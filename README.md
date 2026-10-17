# Psi4 parser

A Python library and ANTLR 4 grammar for validating native Psi4 (**Psithon**)
inputs, including embedded Python. Use it to check generated or handwritten jobs
before submitting them to Psi4.

Validation returns source diagnostics without executing the input. Psi4 and Java
are not required to use the supplied parser.

## Installation

Requires Python **3.15 or later**. From a checkout of this repository:

```sh
uv sync --locked --no-dev
```

## Usage

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

`validate()` accepts input text and returns a tuple of immutable `Diagnostic`
models. An empty tuple means the input passed validation. Each diagnostic has a
one-based `line`, a zero-based `column`, and a `message`.

For source-preserving CST access, use `parse()`:

```python
from psi4_parser import parse

result = parse(source)
tree = result.tree
tokens = result.tokens
original = result.source
```

The result includes the same diagnostics as `validate()`. `source_span(node)`
returns an exclusive-end character interval for an ANTLR token or rule context;
`source_text(node)` returns its original text, including interior comments and
physical newline spelling. Leading and trailing trivia remain in `result.source`.
The CST and token text describe the prepared validation input; use these source
helpers to locate original text. Recovered missing tokens without a source
position raise `ValueError` when queried for a span.

Pass text read with `Path.read_bytes().decode("utf-8")` to retain file line endings.

## Supported input

The parser supports Python 3.15 statements and expressions alongside Psi4's
native directives:

- Molecular geometries, including Cartesian and Z-matrix coordinates,
  fragments, variables, ghost atoms, and geometry settings.
- Inline and block options, module-specific settings, and multiline arrays.
- Basis and ECP blocks, memory directives, and external potentials.
- Embedded PCM sections and literal CFOUR input.

Validation checks syntax and static language constraints, including Python scope
rules. Psi4 and its reader libraries remain responsible for option availability,
molecular consistency, referenced files, basis/ECP contents, and external solver
keyword schemas. Parser acceptance alone does not certify a valid calculation.

The current compatibility target is Psi4 **1.12a1.dev43**, Python **3.15** syntax,
and QCEElemental **0.51.3**. Exact versions and source fingerprints are recorded
in the [compatibility manifest](compatibility/psi4.json).

## Provenance

The Python lexer/parser grammars and vendored
[`PythonLexerBase.py`](src/psi4_parser/_vendor/PythonLexerBase.py) derive from
Robert Einhorn's Python 3.14 grammar in
[antlr/grammars-v4](https://github.com/antlr/grammars-v4/tree/b8da12293f626bc561e5c05c4011f5b5b5e778a8/python/python3_14),
commit `b8da12293f626bc561e5c05c4011f5b5b5e778a8`. Their MIT copyright and license
notices remain in the source files. Local adaptations integrate Psithon headers,
update identifier support to Unicode 17, adjust generated-class imports, and
handle malformed interpolation recovery, and correct split interpolation-token
positions. Python 3.15 extensions and static
constraints are specified in the local Psithon grammars and were checked against
CPython's grammar and syntax regression tests.

Native syntax was audited against Psi4 commit
`60c9b2a773c05abc26991c5ed48cf9862cdb4978`, particularly its input preprocessor,
and the QCEElemental molecule reader. The fixture collection includes upstream
Psi4 inputs and CPython regression examples; its
[provenance and license references](test/fixtures/README.md) are retained with
the fixtures.

## Further documentation

- [Grammar reference and maintenance](grammar/README.md)
- [Compatibility updates and synchronization](compatibility/README.md)
