# Runtime and API discovery

The builder and CLI run in the parser's Python environment. Build, render,
validate, and format inputs without inspecting target binaries, dependencies,
or versions. Use the [source guidance](psi4.md) to choose chemistry documentation.

Use one parser environment for API discovery, builder scripts, and CLI operations.
For separately requested runtime work, use the operator's configured Psi4
environment. It may use another interpreter or run on another machine.

Keep user-facing setup and execution explanations limited to the uv/uvx workflow
below. Do not mention, confirm, or deny the presence of a local development version.

## Fetch and verify the latest code

Before the first parser call in each environment, check whether uv caching or an
installed tool could affect resolution:

```sh
uv cache dir
uv tool list
```

Review relevant uv configuration and the `UV_CACHE_DIR`, `UV_NO_CACHE`, and
`UV_OFFLINE` overrides. A cache directory or installed tool is normal; neither a
successful invocation nor an unchanged package version establishes freshness.

Fetch from `main` with `--isolated --refresh` on every parser invocation, including
API discovery, Python scripts, CLI checks, and MCP startup. `--isolated` bypasses
already-installed tools; `--refresh` revalidates cached data. A branch URL alone
does not force an update. Run from the user's working directory:

```sh
PSI4_PARSER_SOURCE='git+https://github.com/jasonrig/psi4-parser.git@main'
uvx --isolated --refresh --python 3.15 --from "$PSI4_PARSER_SOURCE" python build.py
uvx --isolated --refresh --python 3.15 --from "$PSI4_PARSER_SOURCE" psi4-parser --help
```

The variable above is a shell convenience; set it in each new shell or substitute
the literal source URL. `uvx` fetches the package and dependencies into an isolated,
cached environment. Python scripts run with that environment's interpreter and
the current working directory. Plugin installation itself supplies instructions;
the first runtime command supplies the library. `uv tool run` is equivalent to
`uvx`. See [uv's tool guide](https://docs.astral.sh/uv/guides/tools/) and
[cache guidance](https://docs.astral.sh/uv/concepts/cache/).

Before API discovery, obtain the current upstream commit for comparison with the
installed distribution's `vcs_info.commit_id` in the discovery command below:

```sh
git ls-remote https://github.com/jasonrig/psi4-parser.git refs/heads/main
```

Require the commits to match. If they differ or the distribution records no
commit, retry once with `--no-cache` added to the isolated, refreshed uvx command
and compare against upstream again. If freshness still cannot be verified, or
network access/offline configuration prevents fetching, report that the latest
code could not be obtained and stop parser execution. Do not silently reuse stale
code, substitute another source, or claim a missing API from an unverified runtime.
Use uv's commands for cache recovery; do not edit or delete cache internals.

## Identify the runtime and inspect the API

Record the parser package version and verified Git commit. Keep the same source
and freshness flags for discovery and construction. If `main` changes during the
task, repeat affected discovery and regenerate artifacts with the newly fetched
revision so API inspection and construction remain consistent.

Create a short discovery script, or pass Python on standard input:

```sh
uvx --isolated --refresh --python 3.15 --from "$PSI4_PARSER_SOURCE" python - <<'PY'
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
