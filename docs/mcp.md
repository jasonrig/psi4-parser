# Plan calculations and create Psi4 input through MCP

The `render_psithon` tool accepts molecules, settings, and calculation steps as
JSON. It returns complete Psi4 input text or writes a file and returns its full
path. Its input schema describes all builder components, including fragments,
constraints, comments, and nested control flow.

The server also exposes compact scientific planning tools for discovery,
independent request verification, bounded construction, paged explanations, and
export. Start with `psi4-parser mcp --planning-only` to expose those tools without
the recursive builder schema. See [planning interfaces](formal-interfaces.md) for
the complete file-handle workflow and temporary-file lifetime.
For repeated molecular inputs, save a molecule once and use `formal_request` to
assemble complete requests from handle-based templates.

## Connect an agent

Install the project with `uv sync --locked`. Example configuration for a client
that uses `mcpServers`:

```json
{
  "mcpServers": {
    "psi4": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/psi4-parser",
        "run",
        "--locked",
        "psi4-parser",
        "mcp"
      ]
    }
  }
}
```

Replace the checkout path with its location on the server machine.

## Request an input

`job` contains an ordered list of components in the same JSON format as the
[Python builder](building-jobs.md#save-specifications-and-emit-input).
This request writes an H2 energy input:

```json
{
  "job": {
    "components": [
      {
        "kind": "molecule",
        "name": "h2",
        "geometry": {
          "atoms": [
            {
              "id": "a1",
              "nucleus": {"label": "H"},
              "coordinates": {"kind": "cartesian", "x": 0.0, "y": 0.0, "z": 0.0}
            },
            {
              "id": "a2",
              "nucleus": {"label": "H"},
              "coordinates": {"kind": "cartesian", "x": 0.0, "y": 0.0, "z": 0.74}
            }
          ]
        }
      },
      {
        "kind": "options",
        "assignments": [
          {"key": "basis", "value": {"kind": "literal", "value": "sto-3g"}}
        ]
      },
      {
        "kind": "calculation",
        "driver": "energy",
        "method": {"kind": "literal", "value": "scf"},
        "molecule": {"kind": "reference", "name": "h2"}
      }
    ]
  },
  "path": "h2.dat"
}
```

The result has two nullable fields; exactly one contains a string:

```json
{"path": "/full/temporary/path/h2.dat", "source": null}
```

Omit `path` to receive the input in `source`, with `path` set to `null`.
File requests accept a single name, such as `h2.dat`. Reusing a name raises an
error unless `overwrite` is `true`. Copy or move written files to a durable
location.

The tool checks the complete input and reports construction errors by component
and field. For example, a molecule must be declared before a calculation refers
to it. The [builder guide](building-jobs.md) explains component and reference rules.

## Configure temporary storage

Outputs share a private temporary directory. Python chooses its parent by
default. To select an existing parent directory:

```sh
uv run psi4-parser mcp --temp-parent /absolute/path/to/parent
```

Alternatively, set `PSI4_MCP_TEMP_PARENT` in the client's server environment.
The command-line option takes precedence.
