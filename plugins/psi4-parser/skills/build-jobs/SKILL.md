---
name: build-jobs
description: Use when constructing Psi4 input with Python, including molecular geometry changes, constraints, reusable job components, and parameter sweeps.
---

# Build Psi4 jobs with Python

Prefer the builder for constructing inputs. Use an available Psi4 executable or
Python API for runtime inspection and execution when appropriate to the task.
Continue constructing inputs when Psi4 is unavailable; follow the
[version guidance](../../references/psi4.md) when choosing documentation.

1. Read [runtime and discovery](../../references/runtime.md). Record the parser
   identity and intended Psi4 version; keep each tool's environment consistent.
2. Follow the [Python workflow](../../references/python.md). Resolve consequential
   ambiguities, then inspect the selected helpers and model fields before coding.
3. Resolve chemistry methods and options using the
   [Psi4 documentation](../../references/psi4.md) for the intended Psi4 version.
4. Construct the requested input, preferably in a saved builder script. Use
   direct Psi4 calls where they better fit the required interface or runtime work.
   Save the input and check it against the requested job.
5. Report the script and input paths, plus any unresolved scientific choices.
   Distinguish successful input generation from a completed calculation.
