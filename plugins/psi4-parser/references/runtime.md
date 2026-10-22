# Runtime and API discovery

The builder and CLI run in the parser's Python environment. Build, render,
validate, and format inputs without inspecting target binaries, dependencies,
or versions. Use the [source guidance](psi4.md) to choose chemistry documentation.

Use one parser environment for API discovery, builder scripts, and CLI operations.
For separately requested runtime work, use the operator's configured Psi4
environment. It may use another interpreter or run on another machine.

Use the user's existing environment if it already supplies the intended
`psi4_parser` version. For a local development checkout, run its own environment;
this includes local source changes that a remote Git install cannot fetch:

```sh
uv run --project /path/to/psi4-parser python /path/to/build.py
```

Check `inspect.getfile()` in that environment and use it for both discovery and
scripts. Otherwise, with uv and Git available, run from the user's working directory:

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

Record the parser package version and resolved Git commit when available. Use
that same parser source for subsequent discovery and construction commands.

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
Use the [Psi4 source guidance](psi4.md) for consequential method and option choices.

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

Read only the relevant fields. Some recursive model constructor signatures omit
fields; use `model_fields` and selected schema definitions for the complete
contract. Use `model_json_schema()` when JSON structure or constraints need
inspection, selecting the relevant definitions for large models.

The installed package contains readable Python source. Guides and example build
scripts live in the [repository](https://github.com/jasonrig/psi4-parser); use a
matching ref in GitHub URLs when inspecting a pinned runtime.
