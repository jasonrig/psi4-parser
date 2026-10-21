---
name: edit-inputs
description: Use when validating or formatting Psi4 input, converting between Psithon and JSON, exporting its schema, or making structured edits to existing input.
---

# Check and edit Psi4 inputs

Use the parser CLI and reader for input checks and edits. Use Psi4 directly
when runtime inspection or calculation execution serves the task. Continue input
work without Psi4; follow the [version guidance](../../references/psi4.md) when
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
