---
name: edit-inputs
description: Use when validating or formatting Psi4 input, converting between Psithon and JSON, exporting its schema, or making structured edits to existing input.
---

# Check and edit Psi4 inputs

Choose focused text edits, editable input records, or parser/AST inspection using
[interface guidance](../../references/python.md#choose-how-to-author-the-input).
For new programmatic jobs or checked scientific plans, follow its builder or
formal planning route.

Use the parser CLI and reader for input checks and edits. Use Psi4 directly
for separately requested runtime inspection or calculation execution. Continue input
work without Psi4; follow the [source guidance](../../references/psi4.md) when
choosing documentation.

1. Read [runtime and discovery](../../references/runtime.md), then the
   [CLI workflow](../../references/cli.md).
2. Inspect the selected command's `--help`. Choose validation, formatting,
   conversion, or schema export to match the requested result.
3. For structured edits, inspect `psi4_parser.job` with `dir()`, `help()`, and
   `inspect.signature()`; use its reader and emitter in a saved Python script.
4. Run the chosen operation, inspect its output and exit status, and report the
   resulting file or diagnostics. Check a formatting diff before writing changes.
5. Consult [Psi4 documentation](../../references/psi4.md) when resolving method,
   option, or molecular interpretation questions.

For an input exported from a checked formal plan, revise its source request or
plan and use the [planning workflow](../plan-calculations/SKILL.md) to verify and
export again. Editing the emitted input alone does not update its proof or
manifest hashes. A scientific intent check requires the independent request and
capability evidence; accepted input syntax cannot reconstruct them.
Retain source provenance and scientific method conditions when re-exporting.
Version/build labels and installed dependencies never constrain construction or
produce deployment warnings; runtime is operator-managed.
