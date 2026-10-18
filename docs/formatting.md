# Formatting style and preservation contract

`format_source()` accepts the same complete Psithon language as `parse()`. It
formats whitespace through the ANTLR CST and its original-source spans. It never
executes the input, imports Psi4, reads referenced geometries, or invokes solvers.

## Style

### Indentation and block boundaries

Python suites and native molecule, option, and basis-assignment bodies use four
spaces per level. Hanging continuations use four additional spaces relative to
their opening line. Continuations after inline arguments align vertically with
the first argument; function parameters with no
inline argument use eight additional spaces to distinguish them from the body.
Closing delimiters align with the line that opened the construct. Explicit
backslash continuations outside parentheses use one extra level.
Aligned numeric tables use the first row's field columns instead of ordinary
continuation indentation, including when that row follows code on the same line.

A standalone native braced block (`molecule`, `set`, `basis`, `external`, `pcm`,
`cfour`) has **exactly one empty line on each side when another statement is
present in the same Python suite**. This applies to transitions between native
blocks and Python calculations, as well as between two native blocks. Missing
separators are inserted; extra empty lines at those boundaries are collapsed.

| Boundary between neighboring statements                                  | Empty lines              |
| ------------------------------------------------------------------------ | ------------------------ |
| Native braced block and native braced block                              | Exactly one              |
| Native braced block and Python statement, in either order                | Exactly one              |
| Two Python statements, or an inline directive and a calculation          | Preserve existing layout |
| Suite header and its first statement, or its last statement and a clause | Preserve existing layout |

For example, both boundaries of this options block have one empty line:

```text
cisd_energy, cisd_wfn = energy("CISD", return_wfn=True)

set {
    icore  0
}

casscf_energy = energy('casscf', ref_wfn=cisd_wfn)
```

An inline comment stays on its statement's closing line. Leading comments stay
with the following statement; its separator goes above the comment group. Blank
lines within that comment group remain. The rule adds no padding at file or
suite edges, between a decorator and its definition, or before `else`, `except`
or `finally` clauses. Native blocks used inside Python expressions retain their
physical rows. Inline directives such as `set icore 1` remain grouped with a
following calculation unless the source already separates them.

Other physical row breaks and blank lines remain in place. The formatter does
not wrap lines or impose a line-length limit. Existing newline spellings remain;
new block separators use the surrounding newline spelling. Nonempty output gains
a final newline if needed, using its first newline spelling or LF. Trailing
horizontal whitespace outside protected data and comments is removed. For an
echoed input in a Psi4 output log, only the input section is editable.

### Molecules

- Cartesian atom labels align on their left edge. Numeric columns align at the
  decimal point, with at least two spaces between fields. Integers use an
  implicit decimal point after their last digit. Signs, precision, exponents,
  isotope and ghost labels retain their spelling. Column widths are shared
  across fragments in the same molecule.
- Z-matrix labels align left, reference indices align right, and numeric values
  align at their decimal point. A column containing symbolic values aligns
  complete fields on the right. A reference and its value have one separating
  space; consecutive pairs have at least two. Short rows end at their last field.
- Geometry variable assignments align their equals signs within each adjacent
  section, with one following space. Blank and comment-only lines delimit
  sections. Charge/multiplicity records, fragment separators and directives use
  body indentation and ordinary single separators, outside the atom table.
- Numeric EFP coordinate triples receive the same numeric-column alignment.
  XYZ title lines, reader references, complete atom-label interiors and unit
  spellings remain literal data.

For example, the coordinate columns below share widths without changing values:

```text
molecule water {
    O   0.0    0.000  0.0
    H  -0.757  0.586  0.0
    H   0.757  0.586  0.0
}

set {
    basis      cc-pvdz
    reference  rhf
}
```

### Options and arrays

Keys and value starts align within each contiguous `set` section, with at least
two spaces between a bare key and value. Existing equals signs remain, with
aligned value starts and one space after the equals run. Blank and comment-only
lines delimit alignment sections. Adjacent numeric option vectors of matching
length align corresponding cells; matching wrapped segments align independently.

Numeric Python lists and tuples, and native option arrays, align decimal columns
across matching physical rows. Padding may precede a comma or closing delimiter.
Nested rows must have matching lengths and wrapping to share columns; higher-rank
containers align their numeric planes separately. Flat arrays with repeated,
equal-length physical rows use those rows as layout hints. The formatter never
inserts brackets or changes an array's shape. Ragged, symbolic and expression-heavy
arrays use ordinary spacing. Basis-name option values retain their original text
because Psi4 gives them special quoting behavior.

### Python spacing and literal data

Python whitespace follows [PEP 8](https://peps.python.org/pep-0008/) within the
agreed physical rows. Numeric table alignment and source-sensitive text are
explicit exceptions. Existing line breaks mean that line lengths, blank lines
around Python definitions, import grouping, and same-line statements remain as
written. Names, imports, comment wording and docstrings are not rewritten to enforce
non-formatting recommendations.

- Assignment, binary arithmetic, comparison, and return-annotation operators have
  one space on each side. Unary and unpacking operators bind to their operand.
  Unannotated parameter defaults and keyword argument equals signs have no
  surrounding spaces; annotated defaults use one space on each side.
  Exception groups use `except* Exception`.
- Commas and semicolons have one following space and no preceding space, except
  numeric table padding before commas. Delimiters have no interior spaces except
  numeric column padding. Attribute dots and slice colons have no surrounding
  spaces for simple slice bounds. Compound slice bounds use balanced spaces
  around each colon, omitting spaces beside missing bounds. Other colons have
  one following space and none before.
- Function calls and indexing have no space before the opening delimiter.
  Control-flow keywords retain a separating space. Relative import dots keep
  their lexer grouping; spaces prevent separate dots from becoming an ellipsis.
  Spaced `psi4` and `.extract_subsets` lookups retain their dot separation because
  joining them can trigger a different native rewrite.
- Significant tokens keep their spelling, case and order: parentheses, commas,
  semicolons, quote choices, numeric spellings and statements remain intact.
- Inline comments have exactly two spaces between the statement and comment
  marker, and one space between the hash and nonempty text. Standalone comments
  align with their enclosing Python suite, native body, or continuation. There
  is no extra padding before the marker. Comment wording, physical attachment,
  and line breaks remain; an empty comment is a bare `#`. An initial shebang and
  hashes within protected literals and foreign payloads retain their spelling.
  Escaped comment markers retain their backslash.
  Psi4's preprocessing consumes the character immediately before an unescaped
  `#`. If that character is code, its existing gap is preserved: changing
  `x=12# note` to `x=12  # note` would change the interpreted value from 1 to 12.
- Ordinary strings, f-strings and t-strings retain their interior text, including
  debug and template expression text. Basis records, external-potential bodies,
  PCM and CFOUR payloads retain their exact original text, including indentation.
  These foreign data readers do not follow Python suite indentation.

Literal-data preservation is required. A candidate that fails preservation checks
raises `FormattingError`; it is never returned as successfully formatted.

## AST and equivalence

`build_ast()` requires successful ANTLR validation and consumes the Python
lowering specified in `PsithonParser.g4`. Python's standard `ast` module constructs
the complete Python AST. There is no second handwritten Python AST schema or
alternative validation path.

`ProgramAST.python` is an ordinary `ast.Module`, treated as read-only. It retains
Python node types, fields, literal values, evaluation order, debug f-string text
and t-string interpolation text. Locations refer to generated analysis Python;
original locations remain available through the CST in `ParseResult`.

`ProgramAST.native_data` retains information omitted by syntax-only lowering:
PCM payloads, external geometry filenames and original external-potential bodies.
It follows preprocessing order and includes anonymous basis declaration markers.
Anonymous basis identifiers are deterministic, distinct, and avoid source names,
including Unicode-normalized names. Explicit names and user strings are unchanged.
PCM's temporary filename has a stable representation; its payload remains data.

External-potential lowering omits the wrapper's generated suite padding in its
geometry string while retaining the entire original body in native data. Reference
auditing retains the original wrapper spelling. This does not normalize ordinary
Python strings.

`ProgramAST.equivalent()` compares all Python fields with `ast.compare()` and
native payloads in order, excluding source-location attributes. Molecule bodies
are strings in the lowered AST, so this method also distinguishes their whitespace.
Use `verify_format()` to compare layouts under the formatter's molecule-reader
contract:

```python
from psi4_parser import format_source, verify_format

formatted = format_source(source)
verify_format(source, formatted)
```

Every call to `format_source()` requires:

1. Original and candidate inputs pass ANTLR syntax and static constraints.
2. Ordered CST rule structure and significant terminal types/text agree. Layout
   spelling and token locations are excluded; indentation and newline token
   structure remain significant.
3. Retained native payloads agree exactly. Native molecule fields agree through
   the CST, with additional exact checks for atom labels, units, XYZ title lines
   and reader references, including trailing filename spaces. Only then are the
   original molecule bodies restored in a comparison copy of the candidate.
4. Complete lowered Python ASTs and native data agree for that comparison copy.
   Ordinary Python strings and interpolation contents remain strict.
5. Rendering the candidate again produces exactly the same source.

`verify_format(original, candidate)` exposes checks 1–4 independently. It checks
preservation, without requiring the candidate to follow the canonical style.
Molecule layout equivalence relies on the pinned reader's field parsing contract.
Independent integration tests compare complete QCEElemental molecule records
before and after formatting, alongside the real Psi4 preprocessor's Python AST.

These checks establish equality of the represented program under the pinned
lowering and reader contract. They exclude observations of source text, source
positions, tracebacks and generated identifiers or temporary paths. They do not
prove arbitrary Python runtime behavior under source inspection or modified
bindings. The AST is an analysis representation; execute native input through
Psi4. Option availability, molecular consistency, referenced files and solver
schemas remain Psi4's responsibility.

## Implementation guide

`formatting.py` builds ordinary spacing and indentation edits, then applies the
explicit style passes in this order:

1. `_formatting/python.py`: PEP 8 whitespace and continuation indentation.
2. `_formatting/molecules.py`: molecule records and variables.
3. `_formatting/options.py`: option key/value starts.
4. `_formatting/arrays.py`: numeric rows and wrapped segments.
5. `_formatting/options.py`: corresponding occupation-vector columns.
6. `_formatting/comments.py`: comment spacing and standalone scope alignment.
7. `_formatting/blocks.py`: blank lines around standalone native block statements.

Each pass returns an independent edit plan over the same read-only source and
CST. Later, more specific passes own matching whitespace gaps. Shared field
spans and decimal-column calculations live in `_formatting/layout.py`; numeric
spellings are never converted or rounded. Block separation runs last so column
calculations operate on the original physical rows. Edits apply once, followed
by validation, preservation and idempotence checks. Molecule verification is
isolated in `_formatting/verification.py`.
