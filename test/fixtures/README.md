# Parser fixtures

The corpus contains **2,992 `.dat` files**: 1,359 accepted inputs and 1,633
rejected inputs. Counts describe parser results; accepted files can still depend
on variables, files, or modules from their original test setup.

| Directory or file                   | Count | Expected result         |
| ----------------------------------- | ----: | ----------------------- |
| `positive/psi4/`                    |   662 | Accepted                |
| `positive/parser/`                  |    83 | Accepted                |
| `positive/helium.dat`               |     1 | Accepted                |
| `negative/parser/`                  |    27 | At least one diagnostic |
| `positive/conformance/`             |   245 | Accepted                |
| `negative/conformance/`             |   245 | At least one diagnostic |
| `positive/reference/cpython/`       |    88 | Accepted                |
| `negative/reference/cpython/`       |   633 | At least one diagnostic |
| `positive/reference/interpolation/` |   280 | Accepted                |
| `negative/reference/interpolation/` |   728 | At least one diagnostic |

## Sources and licenses

`positive/psi4/` contains unchanged `tests/**/input.dat` files from Psi4 commit
`60c9b2a773c05abc26991c5ed48cf9862cdb4978`, preserving their directory structure.
The copied [COPYING](positive/psi4/COPYING) and
[COPYING.LESSER](positive/psi4/COPYING.LESSER) files retain the upstream licenses.
`positive/helium.dat` is the HF/STO-3G input used for a calculation check.

The `parser/` directories snapshot local test inputs, including comparisons with
the installed preprocessor. Paths identify the test module, function, and case
ID or one-based parameter index. Inputs used by several tests are retained at
each corresponding path.

The CPython corpus contains 721 examples from the upstream `3.15` branch's
`test_syntax.py`, `test_named_expressions.py`, `test_patma.py`, and
`test_type_params.py`. Each was translated by Psi4 and checked by its bundled
Python compiler. [The provenance manifest](reference/cpython-provenance.json)
records origins, source hashes, and outcomes;
[CPYTHON-LICENSE](reference/CPYTHON-LICENSE) retains the license.

The interpolation corpus contains 1,008 combinations of six f/t-string prefixes,
both quote styles, single and triple quotes, 21 content patterns, and complete or
incomplete endings. Its [manifest](reference/interpolation-provenance.json)
records generation parameters, hashes, and reference outcomes.

## Coverage

Matched `conformance/` cases have identical relative paths under `positive/` and
`negative/`. They cover Python scope, bindings, parameters, annotations, exception
groups, comprehensions, patterns, calls, assignments, literals, Unicode, comments,
future imports, and Psithon fields. Reference corpora contain independent cases
and do not require matched counterparts.

Further cases exercise:

- Psi4's transformations inside strings, namespace expansion, default imports,
  `extract_subsets`, future-line order, and generated names.
- Invalid escapes and triple quotes in CFOUR, basis data, PubChem, and XYZ titles;
  f/t-string literal text, fields, and format specifications.
- Unicode names, numbers, and separators, distinguishing Psi4 regex whitespace
  from QCEElemental's geometry separators.
- Native statements used in expressions, function defaults, interpolation fields,
  and backslash continuations, including expansions to several Python calls.
- PCM's first column-zero closing brace, tested with controlled solver output
  when PCMSolver is unavailable.

Physical NULs, byte-order marks, and carriage returns in lexical cases are
intentional. Tests decode bytes without newline translation.

## Running the checks

`tests/test_fixtures.py` checks every input. Conformance statements generally use
`if False` so launcher checks compile them without evaluating undefined names;
future imports remain at module scope. Native molecule cases construct small
geometries. Reference corpus checks compare preprocessing and compilation.

The optional launcher checks require both the expected exit status and error
family, so a runtime missing-name error cannot count as a syntax rejection.
See the [upgrade workflow](../../compatibility/README.md) for checks against a
supplied Psi4 build.
