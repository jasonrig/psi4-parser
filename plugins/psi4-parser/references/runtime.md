# Runtime and API discovery

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

## Inspect before coding

Create a short discovery script, or pass Python on standard input:

```sh
uvx --python 3.15 --from "$PSI4_PARSER_SOURCE" python - <<'PY'
import importlib.metadata
import inspect
import psi4_parser.builder as builder

print(importlib.metadata.version("psi4-parser"))
print(builder.__all__)
print(inspect.signature(builder.render_job))
help(builder.Molecule.from_xyz)
print(inspect.getfile(builder))
PY
```

Use `dir(module)` to find names, `help(object)` for behavior and examples,
`inspect.signature(object)` for arguments, and `inspect.getsource(object)` when
implementation detail matters. For model fields, inspect `model_fields` or
`model_json_schema()` instead of guessing constructor arguments.

The installed package contains readable Python source. Guides and example build
scripts live in the [repository](https://github.com/jasonrig/psi4-parser); use a
matching ref in GitHub URLs when inspecting a pinned runtime. For an installed
Git build, `importlib.metadata.distribution("psi4-parser").read_text("direct_url.json")`
records the source URL and resolved commit.
