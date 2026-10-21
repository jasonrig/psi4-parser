---
name: build-jobs
description: Use when constructing Psi4 input with Python, including molecular geometry changes, constraints, reusable job components, and parameter sweeps.
---

# Build Psi4 jobs with Python

1. Read [runtime and discovery](../../references/runtime.md). Use one package
   source throughout API discovery and script execution.
2. Follow the [Python workflow](../../references/python.md). Inspect exports,
   signatures, and `help()` for the operations the task needs before writing code.
3. Resolve chemistry methods and options using the
   [Psi4 documentation](../../references/psi4.md) for the intended Psi4 version.
4. Write and execute a builder script in the user's working directory. Save the
   rendered input beside it and check the result against the requested job.
5. Report the script and input paths, plus any unresolved scientific choices.
   Distinguish successful input generation from a completed calculation.
