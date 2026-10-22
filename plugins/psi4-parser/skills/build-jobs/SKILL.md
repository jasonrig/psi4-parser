---
name: build-jobs
description: Use when constructing Psi4 input with Python, including molecular geometry changes, constraints, reusable job components, and parameter sweeps.
---

# Build Psi4 jobs with Python

Choose handwritten input, editable input records, the builder, or formal
planning using the [interface guidance](../../references/python.md#choose-how-to-author-the-input).
Prefer the builder for new programmatic inputs. Do not preflight Psi4 binaries,
dependencies, or versions, or warn about their availability. Runtime deployment
and any separately requested execution belong to the operator. Follow the
[source guidance](../../references/psi4.md) when choosing documentation.

1. Read [runtime and discovery](../../references/runtime.md). Record the parser
   identity; keep API discovery and builder commands in the same environment.
2. Follow the [Python workflow](../../references/python.md). Resolve consequential
   ambiguities, then inspect the selected helpers and model fields before coding.
   When the user gives a scientific objective requiring calculation planning,
   start with the [planning skill](../plan-calculations/SKILL.md); prepare its
   molecules with the builder, then verify and export against independent intent.
   Use the shared interface guidance for fully specified inputs and existing-input
   edits; discover builder transformations for numerical geometry work.
   Discover scientific/input contract catalogs and their explicit conditions before
   choosing settings for a checked plan. A template's accepted syntax alone
   does not establish its scientific correctness.
3. Resolve chemistry methods and options using the
   [Psi4 documentation](../../references/psi4.md) and relevant implementation.
   Use a user-specified source reference when one is supplied.
4. Construct the requested input, preferably in a saved builder script. Use
   direct Psi4 calls where they better fit the required interface or runtime work.
   Discover call-local settings and option isolation through the selected helper
   and [Python workflow](../../references/python.md) when the job requires them.
   Save the input and check it against the requested job.
5. Report the script and input paths, plus any unresolved scientific choices.
   Distinguish successful input generation from a completed calculation.
