# Runtime and API discovery

The builder and CLI normally run without a Psi4 binary or Python module. Continue
building, rendering, validating, and formatting inputs when neither is available.
An accessible Psi4 environment is useful for checking its version and directly
inspecting behavior, especially its Python interface. Use the
[version guidance](psi4.md) to choose documentation when that access is absent.

Use the parser environment for builder scripts and CLI operations, and a
configured Psi4 environment for its executable or Python API. They may use
different Python interpreters. Keep discovery and use consistent within each
environment; the task determines whether calculation execution is needed.

Use the user's existing environment if it already supplies the intended
`psi4_parser` version. Otherwise, with uv and Git available, run from the user's
working directory:

```sh
PSI4_PARSER_SOURCE='git+https://github.com/jasonrig/psi4-parser.git@main'
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" python build.py
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser --help
```

The variable above is a shell convenience; set it in each new shell or substitute
the literal source URL. `uvx` fetches the package and dependencies into an isolated,
cached environment. Python scripts run with that environment's interpreter and
the current working directory. Plugin installation itself supplies instructions;
the first runtime command supplies the library. See
[uv's tool guide](https://docs.astral.sh/uv/guides/tools/).

Use a Git commit or tag instead of `main` when reproducibility matters. Keep the
same source for inspection, script runs, and CLI checks. To refresh an existing
branch-based cache, add `--refresh-package psi4-parser` to the `uvx` options.

## Identify the runtime and inspect the API

At the start of the task, record the parser package version, resolved Git commit
when available, and intended Psi4 version in the task notes. Mark an assumed Psi4
version as such. Use these identities for subsequent commands and documentation.

Create a short discovery script, or pass Python on standard input:

```sh
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" python - <<'PY'
import importlib.metadata
import inspect
import json
import psi4_parser.builder as builder

distribution = importlib.metadata.distribution("psi4-parser")
origin = json.loads(distribution.read_text("direct_url.json") or "{}")
print("Parser version:", distribution.version)
print("Parser commit:", origin.get("vcs_info", {}).get("commit_id", "not recorded"))
print("Parser source:", inspect.getfile(builder))
print(builder.__all__)
print(inspect.signature(builder.render_job))
help(builder.Molecule.from_xyz)
PY
```

If installation metadata records no commit, retain the package version and
source location; a different checkout's HEAD does not identify this runtime.
Use the [Psi4 version guidance](psi4.md) to establish the intended Psi4 version.

Use `dir(module)` to find names and `inspect.signature(object)` for arguments,
types, and defaults. Use `help()` primarily for functions and methods, and
`inspect.getsource()` when implementation detail matters.

For a model, inspect its constructor signature and field descriptions instead of
reading inherited model documentation. Replace the class below with the one
needed for the task:

```python
import inspect
import psi4_parser.builder as builder

model = builder.ElectronicState
print(inspect.signature(model))
for name, field in model.model_fields.items():
    print(name, "required" if field.is_required() else "optional", field.description)
```

Read only the relevant fields. Use `model_json_schema()` when JSON structure or
constraints need inspection, selecting the relevant definitions for large models.

The installed package contains readable Python source. Guides and example build
scripts live in the [repository](https://github.com/jasonrig/psi4-parser); use a
matching ref in GitHub URLs when inspecting a pinned runtime.
