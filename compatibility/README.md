# Verify and apply a Psi4 upgrade

From the parser checkout, supply a clean Psi4 source checkout and matching,
already-built launchers:

```sh
uv run --locked psi4-sync \
  --source /path/to/psi4-source \
  --reference-python /path/to/psi4-python \
  --binary /path/to/psi4
```

The default command applies a verified upgrade to the working tree. Add `--check`
to verify and produce a patch while leaving the accepted grammar, generated
files, and compatibility manifest in place. `--offline` uses cached uv
dependencies; `--timeout` limits each subprocess stage, defaulting to 1,800 seconds.

The runner requires macOS or Linux, Git, uv, Python 3.15, and Java available to
`antlr4-tools`. Provision the runtimes before an unattended run; regeneration
stages receive closed standard input. Keep the Psi4 checkout outside this parser checkout and
use a reference account without `.psi4rc`. Fetching and building Psi4 belongs to
the caller's setup.

## What is checked

1. Match the clean source revision to Psi4's build metadata and installed reader
   files. Compare both launchers' versions, exported names, and reader fingerprints,
   preserving launcher symlink basenames.
2. Compare reader and language fingerprints with [psi4.json](psi4.json).
   Python hashes describe parsed code, so comments and formatting can change.
   C++ reader hashes use complete file bytes. Reader-code changes, added or removed
   readers, Python minor-version changes, and Unicode changes require assessment.
3. Copy the parser into an isolated candidate, refresh the two namespace-name
   tables, and install its locked dependencies.
4. Regenerate with ANTLR and run Ruff, formatting checks, strict mypy, and the full
   test suite against the supplied Psi4 launchers.
5. Check all `tests/**/input.dat` files in the supplied upstream checkout, including
   new inputs. Compare translated Python abstract syntax trees (ASTs) with Psi4,
   recheck curated reference fixtures, and require JSON and Psithon round trips
   for accepted job models.
   Missing dependencies and newly accepted negative cases fail verification.
6. Check that the parser working tree stayed unchanged during verification.
   Publish accepted artifacts and write the compatibility manifest last.
   Ordinary write failures restore the previous files.

Generation uses `psi4-regenerate`, including its lexer-base import adjustment.
The refreshed name tables remain in the grammar. Normal parser use relies on
the recorded compatibility data; Psi4 is required for these upgrade checks.

## Reports and recovery

Each run writes `.cache/psi4-sync-*/report.json` and stage logs. Successful runs
also write `update.patch`, including when `--check` is used. Reports identify
reference versions, changed fingerprints, input counts, and mismatches.
Failed candidates remain available for diagnosis; successful candidates are
removed. Collect the reports before removing cache directories.

A process lock prevents concurrent synchronizations. File replacements are atomic
individually, with rollback for ordinary write failures. A machine crash during
publication can require another run; the accepted manifest is written last.

## Which updates can run unattended

New exported names, physical-constant names, unrelated Psi4 changes, and Python
source comments can pass verification automatically. Changes to guarded
preprocessing or molecule readers require reviewing the grammar and adding
regression cases. Update baseline fingerprints after that assessment, then run
the full pipeline again. Advancing fingerprints alone bypasses the evidence the
baseline is meant to preserve.

Verification provides regression evidence. Psi4 remains responsible for scientific
option schemas, basis contents, and calculation results. PCM checks use controlled
empty solver output to test preprocessing and brace boundaries; the manifest
records that mode separately from scientific PCMSolver validation.

## Automation and Python settings

The command is noninteractive and returns 0 only after verified success.
Use `--check` to produce a proposed patch; omit it to update the local working
tree. The caller controls committing and publishing the result.

For Python callers, `Settings` accepts the environment variables
`PSI4_SYNC_PROJECT`, `PSI4_SYNC_SOURCE`, `PSI4_SYNC_PYTHON`, `PSI4_SYNC_BINARY`,
`PSI4_SYNC_CHECK`, `PSI4_SYNC_OFFLINE`, and `PSI4_SYNC_TIMEOUT`. Explicit constructor
values take precedence. The CLI supplies its required paths and command-line
defaults explicitly.
