# Use compact planning interfaces

[build.py](build.py) invokes the public Click command group in process and saves
six JSON responses: targeted schema discovery, an operation contract, capability
discovery, planning, paged assumptions, and construction export. It reuses the
independent constrained-counterpoise request from example 25. The default
capability snapshot contains synthetic teaching assumptions.

From the repository root, choose a new directory:

```sh
uv run python examples/28-formal-agent-interface/build.py --destination /tmp/psi4-interface-demo
```

Use `--request PATH` and `--capabilities PATH` for other independently prepared
documents. Real jobs need reviewed scientific/input contracts; deployment is
operator-managed without binary or version checks.
The example launches no quantum chemistry application.

Inspect the [proposal summary](saved/04-proposal.json),
[paged assumptions](saved/05-assumptions.json),
[export response](saved/06-export.json), and
[measurements](saved/measurements.json). Complete records remain under
`saved/workspace/records/`; the construction bundle has its own
[manifest](saved/bundle/manifest.json). Saved response paths describe this run's
location; rerun in your checkout to obtain current absolute paths. Copied records
can be reopened in their new workspace using their content handles.

The measures report actual UTF-8 response sizes and the full saved proposal size.
They are byte counts, not model token counts, runtime guarantees, or a broad
performance benchmark. The summary previews at most ten choices; `choice_count`
and paged explanations preserve access to all choices and goals. Full proof
queries stay in records.

The equivalent shell workflow starts with:

```sh
uv run psi4-parser formal --workspace /tmp/psi4-planning propose \
  examples/25-formal-counterpoise-study/saved/request.json \
  --capabilities examples/formal-demo-capabilities.json
```

Use the returned handles in `formal verify`, `formal explain`, and `formal export`.
`formal --help` describes commands and exit codes. For an agent using MCP, start
`psi4-parser mcp --planning-only`, load the same documents with `formal_load`, and
reuse their handles. MCP files expire at server shutdown, so copy required records
and bundles to durable storage. See [the interface guide](../../docs/formal-interfaces.md).
