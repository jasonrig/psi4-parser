# Grammar maintenance

`PsithonParser.file_input` recognizes the complete mixed input. The imported
Python grammars and the native overrides generate one lexer and one parser.
All validation decisions live in these grammars or their required lexer support;
the public wrapper exposes ANTLR results and collects diagnostics.

| Concern | Implementation | Primary reference |
| --- | --- | --- |
| Python productions and interpolation modes | `PythonParser.g4`, `PythonLexer.g4`, upstream `PythonLexerBase` | CPython `Grammar/python.gram`; grammars-v4 Python 3.14 |
| Python 3.15 syntax and corrected separators | Overrides at the end of `PsithonParser.g4` | Lazy imports, unpacking comprehensions, CPython parameter productions |
| Unicode character classes | Complete Unicode 17 identifier, decimal, numeric-word and whitespace ranges; NFKC and reserved-constant checks | Bundled Python 3.15 interpreter; CPython `Python/ast.c`; native Python `re` fields |
| Native headers and physical boundaries | `PsithonLexer.g4`, `NativeLexerSupport` | Psi4 `psi4/driver/inputparser.py` |
| Molecule fields and external potentials | Native productions and `psithon_native_constraint` | Psi4 input preprocessor; QCEElemental molecule reader |
| Option expressions | `set_option_*`, `psithon_option_python` | `quotify`, `process_set_command`, `process_set_commands` |
| Python wrappers for native blocks | `psithon_molecule_python`, `psithon_basis_python`, `psithon_external_python` | Corresponding `process_*_command` functions and `process_basis_block` |
| Ordered rewrites and source positions | `psithon_project`, `psithon_project_replace`, `psithon_source_error` | Reference `process_input` filter order |
| Executing scopes | `psithon_scope`, `psithon_loop`, `psithon_owner` | CPython `Python/symtable.c`, `Python/codegen.c` |
| Declarations and bindings | `psithon_bindings`, `psithon_binding_name` | Symbol-table declaration order, nonlocals, private mangling |
| Comprehensions and annotations | `psithon_comprehension`, `psithon_restricted_expression` | Comprehension binding conflicts and annotation scopes |
| Patterns, literals and control flow | `psithon_pattern`, `psithon_literal`, `psithon_interpolated_literal`, `psithon_constraints` | CPython AST validation and code generation |
| Future and lazy imports | `psithon_future`, `psithon_lazy_import` | Psi4 future-line hoisting; CPython compiler flags and lazy-import restrictions |

The public `parse()` API retains the original text, complete ANTLR token stream,
CST and diagnostics. `PsithonLexer.g4` records character-boundary offsets in its
existing input-preparation hook, covering CRLF/CR normalization, the synthetic
terminal newline and extraction of echoed input from output logs. Comment masking
preserves prepared-text width. `ParseResult.source_span()` translates ANTLR's
inclusive token boundaries to exclusive-end intervals in the original string;
`source_text()` slices that string. Hidden tokens remain in the token stream.
The tree and token text still represent prepared validation input, so a token
stream's `getText()` is not an original-file reconstruction. Context spans follow
ANTLR's first/last-token boundaries and exclude surrounding trivia. For output
logs, `source` retains the whole log while the CST covers the extracted input.
Unanchored recovery tokens have no source interval. A local vendored-helper fix
anchors split interpolation tokens after the retained prefix and accounts for
newlines in that prefix. No second lexer or bespoke syntax tree is introduced.

The first recognition pass checks native structure and fields. Python context
restrictions are deferred because rewrites can change names, scope classification
and literal values. A constant alias in a capture pattern, for example, becomes
an attribute value pattern after namespace expansion.

The namespace inventories are extracted mechanically by `uv run --locked psi4-sync`.
Its accepted reference fingerprints are in `compatibility/psi4.json`; the
maintenance runner changes these tables in an isolated candidate, regenerates
with ANTLR and promotes only after the compatibility checks pass. See
`compatibility/README.md` for the upgrade contract and source-change guards.

`psithon_project` follows the reference filter order, including changes inside
quoted text. It protects CFOUR content, removes comments, flattens arrays, quotes
options, expands native blocks, handles newlines and `extract_subsets`, rewrites
memory and basis commands, restores literals, hoists exact future lines, prepends
the default imports, then substitutes namespaces. Header inventories pin that
last step to the reference build. A character-position map follows every rewrite.

The complete projected job is recognized through another invocation of the same
`file_input` production with native preprocessing disabled. This pass applies
Python predicates and static checks. Its tree is private to validation; the
returned mixed-source tree contains no generated wrappers. Normal parser validation
uses no `eval`, `ast.parse`, `compile`, or Psi4 installation. The separate
maintenance checks use reference compilation and AST comparisons. The separate
public `build_ast()` API consumes the validated Python lowering through the
standard `ast` module; formatting compares that AST together with retained native
payloads and the original CST, allowing verified native molecule layout changes. See the [formatting contract](../docs/formatting.md).

`native_expression` serves both standalone native statements and Python atoms.
A single option or CFOUR call can therefore occur in a parenthesized expression,
function default or interpolation field. If a block expands to multiple calls,
the projected Python rules decide whether the surrounding position allows them.
Inline options use `set_command` without consuming the enclosing Python newline.

Executing-scope predicates and binding-owner lookup serve separate purposes.
Comprehensions have their own execution restrictions, while named expressions
bind in a containing scope. Definition headers and the first comprehension
iterable execute outside the new body. All bindings are collected before forward
nonlocals are resolved, including class-private names. Imports bind names but
use CPython's `DEF_IMPORT` behavior: an import alone permits a later `global` or
`nonlocal`; a prior read or local assignment does not.

Projection also models names introduced by Psi4. A `global core` after a native
`set` fails because the generated call already reads `core`. The default prelude
reads `core` and assigns `psi4_io` before user statements. Future placement is
checked on the final Python program, including other statements carried along
with a hoisted future line.

Literal payloads do not inherit option-variable restrictions. File paths can
contain dollar signs; GBS/ECP and solver text are not restricted Python-expression
subsets. Their Python wrappers still need valid quoting and escapes. Geometry
separators follow QCEElemental's ASCII spaces, tabs and commas, while native regex
fields permit wider Unicode whitespace.

Two legacy details matter: the blank-line call passes `re.MULTILINE` as a
replacement count, so space-only lines survive; the PCM regex stops at its first
column-zero closing brace regardless of depth. The vendored lexer has a small
recovery guard for malformed short f/t-strings before their first field, avoiding
an empty-stack crash.

Referenced files and scientific schemas remain with their readers. `from_file`
geometry is represented without opening the file. PCM's wrapper uses a
representative empty result; actual solver output is serialized as literal list
data, and keyword validation requires PCMSolver. The grammar does not resolve
runtime names, option availability, electronic consistency, basis libraries,
interpreter resource budgets, or user `.psi4rc` code.

An independent audit compared projected Python ASTs for all 653 upstream inputs
processable without PCMSolver. Random anonymous-basis identifiers were normalized
for comparison. These results provide compatibility evidence, not a formal proof.

For a change, first add a rejected input and a nearby accepted input under
`test/fixtures/{negative,positive}/conformance` using the same relative path.
Check the installed Psi4 launcher, including its reported exception, before
changing the grammar. Update `.g4` sources, regenerate with
`uv run psi4-regenerate`, and run the entire fixture suite with `PSI4_BINARY` and
`PSI4_PYTHON` set. Keep upstream notices and provenance. Generated Python should
never receive a manual semantic fix.

Generation runs in a temporary directory and checks every expected artifact and
both generated Python modules for syntax before replacing the working files.
Compiler and generated-Python syntax failures leave the existing parser untouched;
handwritten stubs and package files are retained. File publication is per artifact,
not a transaction across the directory.

ANTLR 4.13.2 treats embedded actions as target-language text using C/Java comment
rules. It does not recognize Python `#` comments there: an unmatched apostrophe,
quote, or brace in such a comment can confuse action-block scanning. Keep these
characters balanced in action comments. This affects compiling `.g4` files only;
it does not restrict comments in parsed Psithon inputs. See ANTLR's
[`NESTED_ACTION` rule](https://github.com/antlr/antlr4/blob/4.13.2/tool/src/org/antlr/v4/parse/ANTLRLexer.g#L337-L402).
