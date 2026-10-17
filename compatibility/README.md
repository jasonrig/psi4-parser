# Synchronizing a Psi4 upgrade

Run from the parser checkout with a supplied, already-built reference:

```sh
uv run --locked psi4-sync \
  --source /Users/jason/CLionProjects/psi4 \
  --reference-python /Users/jason/.local/bin/psi4-python \
  --binary /Users/jason/.local/bin/psi4
```

The default command applies a verified upgrade to this working tree. `--check`
performs the same verification and produces an update patch without changing
the accepted grammar, generated artifacts or compatibility manifest.
`--offline` requires cached uv dependencies. `--timeout` sets each subprocess
stage's limit in seconds, with a default of 1,800.

The runner needs macOS or Linux, Git, uv, Python 3.15 and Java usable by
antlr4-tools. Commands receive closed standard input; a missing runtime cannot
turn an unattended job into an installation prompt. The reference account must
have no `.psi4rc`. Keep the supplied Psi4 checkout outside the parser checkout.
The pipeline does not fetch, build or install Psi4.

The Python `Settings` API uses `pydantic-settings`, validates positive finite
timeouts and preserves immutable configuration. It can load `PSI4_SYNC_PROJECT`,
`PSI4_SYNC_SOURCE`, `PSI4_SYNC_PYTHON`, `PSI4_SYNC_BINARY`, `PSI4_SYNC_CHECK`,
`PSI4_SYNC_OFFLINE` and `PSI4_SYNC_TIMEOUT` from the environment. Explicit
constructor values take precedence. The Click CLI supplies its explicit options
and documented defaults to that model.

## Verification and promotion

1. Verify a clean source revision against Psi4's build metadata and installed
   reader bytes. Probe both supplied launchers and compare their inventories,
   versions and reader fingerprints. Launcher symlink basenames are preserved.
2. Compare reader and Python language fingerprints with `psi4.json`. Python
   source hashes use ASTs, so ordinary comment and formatting changes pass.
   C++ reader files use complete byte hashes. Added or removed reader files,
   changed reader code, Python minor versions and Unicode tables stop the run.
3. Copy the parser into an isolated candidate and refresh only its two
   namespace inventories. Install the candidate with `uv sync --locked`.
4. Regenerate using ANTLR, then require Ruff, formatting, strict mypy and the
   full test suite with both real-Psi4 reference variables populated.
5. Check the *current supplied upstream checkout's* `tests/**/input.dat` files,
   including newly added inputs. Compare their translated Python ASTs with
   Psi4. Recheck reference acceptance for every curated CPython/interpolation
   fixture. Missing dependencies and newly accepted negatives fail the run.
6. Detect edits to this working tree made while verification was running. On
   success, replace the grammar and generated artifacts, publishing the new
   compatibility manifest last. Failed writes restore the previous artifacts.

Synchronization invokes the existing ANTLR regeneration command, including its
existing lexer-base import adjustment; it adds no generated-code postprocessing.
Inventories remain in the grammar. Psi4 is needed only for these maintenance
checks, not for normal parser validation.

Each run creates `.cache/psi4-sync-*/report.json`, individual stage logs and, on
success, `update.patch`. The differential report gives input counts and concrete
mismatches. Failed candidates are retained for diagnosis; successful candidates
are removed. Cache directories can be removed after reports have been collected.
The POSIX lock prevents concurrent synchronizations and releases automatically
when the process exits. Individual file replacements are atomic and ordinary
write failures roll back; a machine crash during multi-file promotion can require
rerunning the command. The accepted manifest is written last.

## Scope of unattended updates

New namespace exports, physical-constant names, unrelated Psi4 changes and Python
source comments can pass unattended. Changes to guarded preprocessing or molecule
readers require a grammar assessment. The failing report names the changed
fingerprints and reference versions. After updating the grammar and regression
cases for an assessed change, update the relevant baseline fingerprints and rerun
the entire pipeline. Never advance the baseline simply to silence an alert.

This is regression-based compatibility verification, not a proof of equivalence.
Scientific option schemas, basis contents and calculation correctness remain with
Psi4. PCM differential checks use controlled empty solver output to check wrapper
syntax and brace boundaries; they do not certify PCMSolver's scientific schema.
The baseline records this coverage mode explicitly.

## Calling from automation

Run the same command after provisioning a matching reference build. The command
is non-interactive and returns zero only on verified success; failed preflight,
reader changes, tool errors and failed tests return nonzero. Use `--check` for a
verification job that produces a proposed patch. Omit it for unattended local
working-tree promotion. Committing or publishing the resulting update belongs
to the caller's release process.

Reports and proposed patches stay in the local cache. No remote workflow,
artifact uploads, Git pushes or recurring jobs are configured by this pipeline.
