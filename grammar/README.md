# Parser design and grammar maintenance

`PsithonParser.file_input` recognizes complete Psithon input. The native grammars
import Python productions and generate one lexer and one parser. Grammar
predicates and lexer support implement syntax and static checks;
`psi4_parser.api` exposes their results and source positions.

## Where the rules live

| Concern                           | Implementation                                              | Reference                                               |
| --------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------- |
| Python syntax and interpolation   | `PythonParser.g4`, `PythonLexer.g4`, `PythonLexerBase`      | CPython grammar; grammars-v4 Python 3.14                |
| Python 3.15 changes               | Overrides in `PsithonParser.g4`                             | Lazy imports, unpacking comprehensions, parameter rules |
| Native headers and boundaries     | `PsithonLexer.g4`, `NativeLexerSupport`                     | Psi4 `driver/inputparser.py`                            |
| Molecules and external potentials | Native productions, `psithon_native_constraint`             | Psi4 preprocessor and QCEElemental molecule reader      |
| Options and generated Python      | `set_option_*`, `psithon_*_python`, `psithon_project`       | Psi4 `process_*` functions and filter order             |
| Python scope and bindings         | `psithon_scope`, `psithon_bindings`, comprehension helpers  | CPython symbol table and code generation                |
| Patterns, literals, imports       | `psithon_pattern`, literal, future, and lazy-import helpers | CPython syntax checks and compiler rules                |
| Unicode fields                    | Unicode 17 tables, normalization, and field checks          | Python 3.15 identifiers and native reader expressions   |

The Python grammar and lexer-base provenance is recorded in the
[project README](../README.md#compatibility-and-provenance). Keep upstream license
notices when editing imported files.

## Parsing passes

1. Prepare the input: normalize line endings, add a terminal newline if needed,
   and extract echoed input from a Psi4 output log. Record positions in the
   original text throughout preparation.
2. Recognize the mixed Python/native structure and check native fields.
3. Translate the complete input using Psi4's preprocessing rules.
4. Parse that Python translation through the same `file_input` rule with native
   preprocessing disabled, applying Python scope and static checks.

Python context checks run after translation because rewrites can change names,
literals, and scope. For example, an unqualified constant in a capture pattern
can become an attribute value pattern after namespace expansion.
The returned tree describes the mixed input; the second tree is used internally
for validation.

`psithon_project` follows Psi4's filter order: protect CFOUR text, remove comments,
flatten arrays, quote options, expand blocks, handle newlines and `extract_subsets`,
rewrite memory and basis commands, restore literals, move future imports, prepend
default imports, and expand namespaces. Position mappings follow each rewrite.
Some rewrites also affect quoted text, so Python token boundaries alone are
insufficient to reproduce them.

The namespace-name tables are extracted by `psi4-sync`. Their accepted source
fingerprints are in [the compatibility manifest](../compatibility/psi4.json).
The [upgrade workflow](../compatibility/README.md) verifies changes before
publishing regenerated artifacts.

## Original source access

`parse()` returns the original text, mixed-input tree, token stream, and diagnostics.
`ParseResult.source_span(node)` returns an original-text interval with an exclusive
end; `source_text(node)` returns its text. Context spans follow the first and last
tokens, excluding surrounding comments and whitespace. Recovery tokens without
an original position have no interval.

The tree and token text describe prepared input. Use the source helpers, rather
than a token stream's `getText()`, to recover original text. For output logs,
`source` retains the whole log and `input_span` locates the extracted job.
Mappings account for CRLF/CR normalization, added terminal newlines, comment
masking, and split interpolation tokens.

`build_ast()` separately turns the validated Python translation into a standard
Python abstract syntax tree (AST). The formatter compares that AST, retained
native data, and the mixed syntax tree. See [formatting verification](../docs/formatting.md#program-comparison).

## Python and native interactions

`native_expression` permits native constructs in Python expressions, including
parentheses, function defaults, and interpolation fields. The translated Python
determines whether an expansion to one or several calls fits that position.
Inline options stop before the enclosing Python newline.

Execution scopes and binding owners are tracked separately. A named expression
inside a comprehension can assign to an enclosing scope; definition headers and
the first comprehension iterable execute outside the new body. Bindings are
collected before resolving forward `nonlocal` declarations and class-private names.
Imports follow CPython's `DEF_IMPORT` rule: an import alone permits a later
`global` or `nonlocal`, while an earlier read or local assignment may forbid it.

Checks include names introduced by Psi4. For example, `global core` after `set`
conflicts with the generated call's earlier read of `core`. Default imports read
`core` and assign `psi4_io` before user statements. Future-import placement is
checked after hoisting, including statements sharing the moved line.

Literal data uses its reader's rules. File paths may contain dollar signs;
basis/ECP and solver bodies retain their language syntax. Generated Python
wrappers still require valid quoting and escapes. Geometry separators follow
QCEElemental's ASCII spaces, tabs, and commas; some Psi4 regex fields allow wider
Unicode whitespace.

Two preprocessing details need particular care: Psi4 passes `re.MULTILINE` as a
replacement count when removing blank lines, so space-only lines survive; its
PCM regex ends at the first column-zero closing brace regardless of nesting.
The lexer also guards malformed short f/t-strings before their first field so
validation returns diagnostics instead of an empty-stack error.

## Validation boundaries

Parsing retains geometry file and PubChem references as data. Their readers
resolve them when an input runs. PCM syntax checks use a representative empty
solver result to validate Python wrappers; PCMSolver checks its own settings.
Psi4 also resolves runtime names, options, electronic states, and basis libraries.

Compatibility tests compare translated Python ASTs and reader results against
the supplied Psi4 build. Anonymous basis names are normalized for comparison.
This provides regression evidence under the recorded versions.

## Change and regenerate the grammar

Add a rejected input and a nearby accepted input under
`test/fixtures/{negative,positive}/conformance`, using the same relative path.
Check the supplied Psi4 launcher's outcome and exception family, then edit `.g4`
sources and regenerate:

```sh
uv run psi4-regenerate
PSI4_BINARY=/path/to/psi4 PSI4_PYTHON=/path/to/psi4-python uv run pytest
```

Fix grammar behavior in the maintained sources and regenerate the Python files.
Generation stages its output in a temporary directory and checks every expected
artifact and both generated Python modules before replacing files. Grammar or
syntax failures leave the existing parser in place. Publication replaces files
individually; handwritten stubs and package files remain.

ANTLR 4.13.2 scans embedded actions using C/Java comment rules. A Python `#`
comment containing an unmatched quote, apostrophe, or brace can confuse that
scanner. Keep delimiters balanced in action comments. This restriction concerns
grammar generation; ordinary Psithon comments use the input language's rules.
See ANTLR's [`NESTED_ACTION` rule](https://github.com/antlr/antlr4/blob/4.13.2/tool/src/org/antlr/v4/parse/ANTLRLexer.g#L337-L402).
