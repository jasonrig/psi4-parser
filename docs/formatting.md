# Formatting and verification

`format_source()` formats complete Psithon inputs. It uses the parser's syntax
tree and original-source positions, then checks that the result represents the
same program. Formatting retains literal data and Python line breaks.

## Indentation and blank lines

Python suites and molecule, option, and basis-assignment bodies use four spaces
per level. Hanging continuations use four more spaces than their opening line.
Arguments following an inline argument align with that argument. Function parameters with no inline
argument use eight extra spaces to distinguish them from the body. Closing
brackets align with their opening statement; backslash continuations use one
extra level. Aligned numeric tables follow their field columns instead.

Standalone braced blocks—`molecule`, `set`, `basis`, `external`, `pcm`, and
`cfour`—have exactly one empty line between themselves and neighboring statements
in the same Python suite:

| Neighboring statements                                          | Empty lines              |
| --------------------------------------------------------------- | ------------------------ |
| Two native braced blocks                                        | Exactly one              |
| A native braced block and a Python statement                    | Exactly one              |
| Two Python statements, or an inline directive and a calculation | Preserve existing layout |
| A suite header and its body, or the body and a following clause | Preserve existing layout |

```text
cisd_energy, cisd_wfn = energy("CISD", return_wfn=True)

set {
    icore  0
}

casscf_energy = energy('casscf', ref_wfn=cisd_wfn)
```

Leading comments stay with the following statement; its separator goes above
the comment group. Internal blank lines in that group remain. File and suite
edges receive no extra padding. Decorators and their definitions stay together,
as do `else`, `except`, and `finally` clauses and their preceding bodies.
Blocks inside Python expressions retain their physical rows.

Other line breaks and blank lines remain. The formatter keeps line lengths as
written. Existing newline spellings are retained, and new separators use the
surrounding spelling. Nonempty output gains a final newline if needed, using its
first newline spelling or LF. Trailing horizontal whitespace is removed outside
protected data and comments. For Psi4 output logs, only the echoed input section
is editable.

## Molecule alignment

- Cartesian labels align left; numeric columns align at the decimal point with
  at least two spaces between fields. Integers have an implied decimal point
  after the final digit. All fragments in a molecule share column widths.
- Z-matrix labels align left and reference indices align right. Numeric values
  align at the decimal point; columns containing variables align whole fields
  right. A reference and value have one separating space; successive pairs have
  at least two. Short rows end at their last field.
- Adjacent geometry assignments align their equals signs, with one following
  space. Blank and comment-only lines separate alignment groups.
- Charge and multiplicity, fragment separators, and directives use body
  indentation and single spaces. Numeric EFP triples use numeric-column alignment.

The formatter retains signs, precision, exponents, isotope and ghost labels,
unit spelling, XYZ titles, and file paths.

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

## Options and arrays

Option values align within each adjacent group of settings, with at least two
spaces after a bare key. Existing equals signs remain, followed by one space;
value starts align. Blank and comment-only lines separate groups. Numeric option
vectors of matching lengths align corresponding entries, including matching
wrapped segments.

Numeric Python lists, tuples, and native option arrays align decimal columns
across matching physical rows. Padding can precede commas or closing brackets.
Rows must have matching lengths and wrapping to align together; higher-dimensional
arrays align each numeric plane separately. Repeated, equal-length rows in a flat
array also guide alignment. Brackets and array shapes remain unchanged.
Ragged arrays and arrays containing variables or expressions use ordinary spacing.
Basis-name option values keep their text because Psi4 quotes them specially.

## Python spacing and comments

Spacing follows [PEP 8](https://peps.python.org/pep-0008/) within existing physical
lines, with exceptions for numeric tables and source-sensitive text. Line lengths,
blank lines around Python definitions, import grouping, and same-line statements
retain their layout. Names, imports, docstrings, and comment wording are retained.

- Assignment, binary, comparison, and return-annotation operators have one space
  on each side. Unary and unpacking operators touch their operands. Unannotated
  defaults and keyword arguments use `name=value`; annotated defaults use
  `name: type = value`. Exception groups use `except* Exception`.
- Commas and semicolons have one following space and none before, except for
  numeric-table padding. Delimiters have no interior spaces except table padding.
- Calls and indexing touch their opening delimiters. Control-flow keywords keep
  a separating space. Simple slice bounds touch their colons; compound bounds
  use balanced spaces, omitting spaces next to missing bounds. Other colons have
  one following space and none before.
- Attribute dots have no surrounding spaces. Relative-import dots retain their
  grouping. Spaced `psi4` and `.extract_subsets` lookups keep the separation that
  prevents a different Psi4 rewrite.
- Significant tokens retain their spelling, case, and order, including quotes,
  parentheses, commas, semicolons, and numeric text.

Inline comments use two spaces before `#` and one before nonempty text.
Standalone comments align with their Python suite, native body, or continuation,
with no extra padding before the hash. An empty comment is `#`. Comment attachment,
wording, and line breaks remain. Shebangs, escaped hashes, and hashes inside
protected data keep their spelling.

Psi4 can consume the character immediately before an unescaped hash. The
formatter preserves an exceptional gap when spacing would change the input's
meaning: `x=12# note` is interpreted as `x=1`, whereas adding a gap would give 12.

Strings, f-strings, and t-strings retain their contents, including debug and
template expressions. Basis data, external-potential bodies, PCM, and CFOUR keep
their original text and indentation; those readers use their own layout rules.

## Program comparison

`build_ast()` uses Python's standard `ast` module to represent the validated
Python translation of an input. `ProgramAST.python` is an `ast.Module` for
analysis. Its locations refer to translated Python; original locations are
available from `parse()`.

`ProgramAST.native_data` retains data the translation alone cannot represent:
PCM input, geometry filenames, original external-potential bodies, and anonymous
basis markers. Anonymous basis names are deterministic, distinct, and avoid
source names, including Unicode-normalized names. PCM temporary filenames have
stable analysis representations. Explicit names and ordinary string values are preserved.

External-potential geometry strings omit generated wrapper indentation in this
analysis representation. Their original bodies remain in `native_data`.
Reference comparisons also check the original wrapper spelling.

`ProgramAST.equivalent()` compares Python fields and ordered native data,
excluding source locations. Molecule bodies are strings in this AST, so their
whitespace affects that comparison. Use `verify_format()` for layout-aware
comparison:

```python
from psi4_parser import format_source, verify_format

source = "set basis sto-3g\n"
formatted = format_source(source)
verify_format(source, formatted)
```

Every `format_source()` result must pass five checks:

1. Original and candidate inputs pass syntax and static checks.
2. Syntax-tree rules and significant tokens agree in order. Whitespace spelling
   and locations are excluded; indentation and newline token structure matter.
3. Retained native data agrees exactly. Molecule fields agree, with exact checks
   for labels, units, XYZ titles, and file references, including trailing spaces.
4. Python ASTs and native data agree after restoring verified molecule layout
   in a comparison copy. Ordinary Python strings and interpolation text remain
   subject to exact comparison.
5. Formatting the candidate again returns exactly the same text.

`verify_format(original, candidate)` exposes checks 1–4 and accepts text or parse
results. It verifies preservation independently of the preferred style.
Invalid source raises `InvalidInputError`; an invalid or changed candidate raises
`FormattingError`.

These checks establish agreement under the pinned Psi4 preprocessing and molecule
reader rules. They cover the represented program, with source locations, source
inspection, tracebacks, generated names, and temporary paths excluded from the
comparison. Replacing Psi4 functions or names at runtime can also change behavior.
Psi4 checks scientific options, molecular consistency, files, and solver schemas.
Reference tests compare QCEElemental molecule records and the real preprocessor's
Python AST before and after formatting.

## Maintain the formatter

Formatting passes in `src/psi4_parser/_formatting/` plan edits over the same source
and syntax tree. They run in this order:

1. `python.py`: Python spacing and continuation indentation.
2. `molecules.py`: coordinates and geometry variables.
3. `options.py`: option values.
4. `arrays.py`: numeric rows and wrapped segments.
5. `options.py`: corresponding occupation-vector columns.
6. `comments.py`: comment spacing and scope alignment.
7. `blocks.py`: blank lines around standalone native blocks.

Later passes take ownership of matching whitespace gaps. `layout.py` supplies
field spans and decimal-column calculations; `verification.py` checks molecule
preservation. Block spacing runs last so alignment uses the original physical
rows. The combined edits are applied once, followed by validation, preservation,
and repeat-formatting checks. Numeric text is aligned without rounding.
