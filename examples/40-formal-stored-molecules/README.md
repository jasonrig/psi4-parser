# Reuse molecular inputs across independent plans

This example saves one 18-atom molecular input and reuses its handle for four
independent HF/MP2 energy requests with STO-3G and cc-pVDZ orbital bases. The water array and
methods illustrate the API; they are not a recommended research protocol.

```sh
uv run python examples/40-formal-stored-molecules/build.py --destination /tmp/psi4-example-40
```

`StoredMolecule` retains exact builder molecular data. Each `RequestTemplate`
binds its handle to the name used by independently chosen goals and relations.
`PlanningWorkspace.materialize_request()` validates saved records and returns a
complete `ScientificRequest`. The example compares every assembled request to
an independently constructed request with explicit coordinates, then plans each
using shared scientific contracts. It exports the final plan as a self-contained
construction bundle. No calculation is executed or parsed.

The compact CLI equivalents are:

```sh
psi4-parser formal --workspace planning-artifacts load molecule saved/molecule.json
psi4-parser formal --workspace planning-artifacts request template.json
psi4-parser formal --workspace planning-artifacts propose request:RETURNED_ID
```

Write `template.json` using the returned molecule handle; the saved templates
refer to the generated example workspace. MCP callers load records with
`formal_load(kind="molecule", ...)` and `formal_load(kind="request_template", ...)`,
then assemble with `formal_request(template=HANDLE)`. A successful assembly is
structural preparation; scientific acceptance still requires propose or verify.

[Measurements](saved/measurements.json) compare compact JSON upload bytes for
one molecule plus four templates against four complete inline requests. They
also retain proposal response sizes and equivalent tool-call counts. These
measurements describe this construction fixture, not model token counts or
agent reliability. Record handles reduce repeated coordinate uploads but require
assembly calls. For a small molecule used once, a complete request is simpler.
Read the retained measurements for current byte totals.

Molecule handles are local to the workspace. CLI workspaces persist; MCP files
expire at shutdown. A completed request embeds the molecular data and can be
verified without the source records. The [bundle](saved/bundle/manifest.json)
contains complete intent, evidence, proof, input, and payload paths. Copy
complete bundles to retain them. For storage and error behavior, see
[planning interfaces](../../docs/formal-interfaces.md).
