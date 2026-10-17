# Parser fixtures

All 2,992 input files are curated here by expected parser result: 1,359 positive
and 1,633 negative.

| Directory or file | Count | Expected result |
| --- | ---: | --- |
| `positive/psi4/` | 662 | Accepted |
| `positive/parser/` | 83 | Accepted |
| `positive/helium.dat` | 1 | Accepted |
| `negative/parser/` | 27 | Rejected with at least one diagnostic |
| `positive/conformance/` | 245 | Accepted |
| `negative/conformance/` | 245 | Rejected with at least one diagnostic |
| `positive/reference/cpython/` | 88 | Accepted |
| `negative/reference/cpython/` | 633 | Rejected with at least one diagnostic |
| `positive/reference/interpolation/` | 280 | Accepted |
| `negative/reference/interpolation/` | 728 | Rejected with at least one diagnostic |

`positive/psi4/` contains unmodified `tests/**/input.dat` files from Psi4
commit `60c9b2a773c05abc26991c5ed48cf9862cdb4978`, preserving its test directory
structure and license files. `positive/helium.dat` is the HF/STO-3G job used
for the calculation check.

The `parser/` directories contain snapshots of the local test inputs, including
the installed-preprocessor comparisons. Their paths identify the test module,
function and case ID or one-based parameter index. Duplicate inputs used by
different tests are retained.

The `conformance/` directories contain matched pairs with identical relative
paths. They cover binding and scope rules, parameters, annotations, exception
groups, comprehensions, patterns, calls, assignment targets, literals, Unicode,
comments, future imports, and native Psithon fields. Most Python statements use an `if False` guard
so launcher checks validate compilation without evaluating undefined names.
Native molecule cases perform only small geometry construction, without energy
calculations. Every fixture is exercised directly by `tests/test_fixtures.py`.
Future-import fixtures remain at module scope to exercise the actual hoisting
and compiler-flag behavior.

The CPython corpus contains 721 independent examples from `test_syntax.py`,
`test_named_expressions.py`, `test_patma.py` and `test_type_params.py` on the
upstream `3.15` branch. Each was translated by the installed Psi4 preprocessor
and checked by its bundled compiler without executing the job. The manifest
at `reference/cpython-provenance.json` records origins, source hashes and
reference outcomes; `reference/CPYTHON-LICENSE` supplies the upstream license.
These are reference regressions, so they need not have one-to-one counterparts.

The interpolation corpus covers all six f/t-string prefixes, single and triple
quotes of both styles, 21 payload shapes, and complete/incomplete endings:
1,008 cases in total. Every result was checked by the installed Psi4 preprocessor
and bundled Python compiler without executing the job. The matrix found no
remaining mismatches or validator crashes. Generation parameters, input hashes
and reference outcomes are in `reference/interpolation-provenance.json`.

The matched conformance cases additionally exercise Python scope and binding
interactions, exact parameter separators, class-private names, open sequence
patterns, native option expression quoting, basis layout conflicts and lexical
preprocessing. Physical NULs, a BOM and carriage returns are intentional in
the lexical fixtures. Tests decode their bytes without newline translation.

Literal-wrapper pairs check incomplete escapes and broken triple quotes in
CFOUR, GBS, PubChem and XYZ comment text. Interpolated-string cases distinguish
literal chunks, format specifications and replacement expressions, including
protected CFOUR content. Native field cases cover Unicode decimals, numeric
word characters, numeric and ignored header names, generated Python identifiers,
and numeric calls that require Python number syntax. Binding pairs also account
for names that Psi4 introduces or reads while expanding native statements.

Preprocessing pairs exercise transformations inside strings, namespace aliases,
the default prelude, first-line `extract_subsets`, future-line ordering and
literal values changed by comments or blank-line handling. Native Unicode-space
cases distinguish broad regex separators from QCEElemental's narrower geometry
separators. Two local PCM positives were corrected to indent their inner closing
braces; a separate negative records the first column-zero boundary. Reference
tests isolate that boundary with controlled solver output when PCMSolver is
unavailable.

Native-expression pairs cover parenthesized calls, function defaults, f-string
fields and explicit line continuations. They distinguish single-call expansions
from multiple calls in an expression, required arguments after defaults, and
invalid conversions. Relative lazy imports of modules named `__future__` are
paired with the forbidden absolute future-import form.

The initial differential audit found 55 false accepts among 56 matched negative
cases. Those cases now fail ANTLR validation; their nearby positive variants
remain accepted. The optional launcher suite asserts both the exit status and
the reported error family, so a missing name at execution time does not count
as an expected syntax rejection.

Accepted fixtures can require variables, files or optional modules from their
test setup; parser acceptance does not imply a standalone runnable job.
