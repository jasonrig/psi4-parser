# Plan calculations with compact file-backed interfaces

The `formal` CLI group, planning MCP tools, and `PlanningWorkspace` use the same
construction service. Save independent requests once, then pass file paths or
record handles. Shared scientific contracts apply by default; optional custom
catalogues extend coverage. Responses summarize
acceptance and locate complete records. Full solver queries stay in JSON files.

These interfaces end at construction export. They do not execute calculations,
parse results, or apply numerical output acceptance checks. See
[scientific planning](scientific-planning.md) for scientific contracts and
current coverage.

## Use the command line

Start with the matching runtime's help:

```sh
uv run psi4-parser formal --help
uv run psi4-parser formal schema request --definition Model --field basis
uv run psi4-parser formal contracts --driver optimize
```

Schema discovery returns field descriptions and available definition names.
Supplying `--field` returns `json_schema` for those fields, including the
transitive definitions they reference. This selected schema describes part of
a record; imports still validate the complete document. Repeating `--field`
selects additional distinct fields.

Given independently prepared `request.json` and `capabilities.json`:

```sh
uv run psi4-parser formal --workspace planning-artifacts propose request.json \
  --capabilities capabilities.json
```

The workspace persists until you remove it. Its parent must exist. The default
is `.psi4-planning` in the working directory; discovery alone does not create it.
Choose a durable destination for records you need to retain.

The proposal response includes `status`, `attempts`, `choice_count`, at most ten
choice previews, and references to the full proposal, accepted plan, and
verification. References contain `handle`, `kind`, `path`, and `bytes`.
The response also reports top-level `calculation_count` and `shared_call_count`.
A rejected checked graph is available as `last_candidate`, never as an accepted `plan`.
The `path` is absolute. A handle has the form `kind:ID`; substitute the
returned values in later commands. `formal load KIND PATH` imports a record
without starting search.

### Reuse molecular inputs

Save a `StoredMolecule` once with `formal load molecule molecule.json`. Its JSON
contains `geometry` in the builder's molecule format. The returned
`molecule:ID` handle identifies the exact molecular input, including atom IDs,
units, fragments, states, isotopes, ghosts, symmetry, and frame settings.

Prepare a `RequestTemplate` with handle bindings instead of coordinates:

```json
{
  "molecules": [{"name": "water", "molecule": "molecule:<returned ID>"}],
  "goals": [{
    "kind": "calculate", "id": "energy", "geometry": "water", "driver": "energy",
    "models": [{"method": "hf", "basis": "cc-pvdz", "reference": "rhf",
                "settings": [{"name": "scf_type", "value": "PK"}]}]
  }]
}
```

Replace the placeholder with the complete returned handle. Then assemble and plan:

```sh
uv run psi4-parser formal --workspace planning-artifacts request template.json
uv run psi4-parser formal --workspace planning-artifacts propose request:RETURNED_ID
```

`request` accepts a template path or a saved `request_template:ID` handle.
Every molecular record is structurally validated and copied into a complete
`ScientificRequest`; goals and relations are preserved. The resulting request
handle works with the ordinary propose, verify, and export operations. Exported
bundles contain full molecular inputs and need no template workspace. Imports
and assembly establish structural validity; scientific acceptance requires
planning or verification. See [example 40](../examples/40-formal-stored-molecules/README.md).

### Verify and export saved work

The following path-based commands use caller-supplied documents:

```sh
uv run psi4-parser formal --workspace planning-artifacts verify plan.json \
  --request request.json --capabilities capabilities.json
uv run psi4-parser formal --workspace planning-artifacts explain verification.json \
  --section issues --limit 10
uv run psi4-parser formal --workspace planning-artifacts explain proposal.json \
  --kind proposal --section choices --offset 10 --limit 10
uv run psi4-parser formal --workspace planning-artifacts export plan.json \
  --request request.json --capabilities capabilities.json --destination new-job-bundle
```

Every path argument above can instead use a matching workspace handle. A handle
already supplies its record kind. For a proposal file, select `--kind proposal`.
Export independently verifies the current plan, request, and catalog again.
An existing destination is never overwritten. A rejected export returns fresh
verification and creates no bundle directory.

`formal catalogs` lists shared scientific contract collections. The default
`psi4` collection needs no target version selection. `formal load-catalog psi4`
saves its entries for targeted discovery. Propose, verify, and export use these
contracts automatically when `--capabilities` is omitted. Custom catalogues
extend scientific coverage; see [input contract evidence](formal-capabilities.md).

`formal capabilities CATALOG` pages through methods, products, bases, options,
components, environments, or evidence. Method entries include the explicit option conditions under which
their evidence applies.
Method pages return `product_count` by default. Use `--section products` with
`--name METHOD --driver DRIVER --product PRODUCT` to inspect relevant product
cases, or `--include-products` for full nested method records. Producing conditions
and component requirements remain visible in product pages. Product pages also
retain feature coverage, including SAPT basis and induction modes.
Use `--section`, `--name`, `--driver`, `--offset`, and `--limit` to narrow discovery.
`--driver` applies to methods and products. Name matching is exact and case-insensitive;
options use `name` or `module.name`. Missing entries remain unknown.
Environment pages accept `--name ddx` and retain cavity and solvent lookup
reference data. Installed tables and components do not affect verification.

Use `--limits FILE` on propose for `SearchLimits` JSON, and on verify/export for
verification `Limits` JSON. Bounds remain distinct from scientific rejection.
Use `--call-reuse prefer` (default) or `avoid` on propose to rank explicitly
permitted sharing after model/route choices. Matching `reuse_group` fields in
the request grant permission; neither flag grants it. See [reuse contracts](formal-reuse.md).
For proposal explanations, `--section reuse` pages through selected shared calls.

| Exit code | Meaning |
| --- | --- |
| 0 | Construction accepted, or discovery/explanation completed. |
| 1 | Scientific work was invalid, violated, unsupported, or had no accepted finite candidate. |
| 2 | Usage, malformed JSON/schema selection, filesystem, or record-size error. |
| 3 | Verification is unknown or construction search is exhausted/undecided. |

Machine-readable scientific responses go to stdout, including nonzero scientific
outcomes. Usage and file errors go to stderr. A `no_candidate` outcome concerns
only the declared finite alternatives; exhaustion does not prove impossibility.

Accepted export summaries include `option_policy` and `namespace_policy`
alongside the manifest path. They expose the native
option and call-entry namespace restoration contracts without
loading the full manifest. Rejected exports, or older summaries without these
fields, make no option-isolation claim.

## Use MCP

Start the compact server with:

```sh
uv run psi4-parser mcp --planning-only
```

This mode exposes ten formal tools and omits the recursive builder input
schema. The default server also retains `render_psithon`. Use `--temp-parent` or
`PSI4_MCP_TEMP_PARENT` to select an existing temporary parent. Set
`PSI4_MCP_PLANNING_ONLY=true` to select compact mode through the environment.

| Tool | Purpose |
| --- | --- |
| `formal_load` | Validate and copy JSON, or load a shared scientific catalogue. |
| `formal_request` | Assemble a complete request from a saved template and molecule handles. |
| `formal_catalogs` | Discover shared scientific collections and finite coverage, without engine versions. |
| `formal_schema` | Discover fields or select a schema definition and fields. |
| `formal_contracts` | Inspect operation prerequisites and products. |
| `formal_capabilities` | Query a saved catalog with a bounded `CapabilityQuery`. |
| `formal_propose` | Search the independent request's explicitly allowed alternatives. |
| `formal_verify` | Check a saved plan against a required independent request. |
| `formal_explain` | Page through issues, coverage, assumptions, choices, or reuse. |
| `formal_export` | Reverify and create a new temporary construction bundle. |

Load documents once, using exactly one of `path`, `source`, and `catalog`, then
reuse the returned handles. `catalog` requires `kind="capabilities"` and a name
from `formal_catalogs`. Prefer file paths for large inputs. Tool input schemas describe
handles and small options rather than embedding the complete request and plan
schemas. Propose, verify, and export use shared Psi4 scientific contracts when
a custom capability handle is omitted.

For repeated molecular inputs, use `formal_load(kind="molecule", ...)` once.
Load each `RequestTemplate` with `kind="request_template"`, then call
`formal_request(template=HANDLE)`. Its returned request embeds the complete
geometry. Keep molecule handles within their workspace and server lifetime;
copy needed records or complete bundles before shutdown.

`formal_propose` accepts optional `preferences={"calculation_reuse": "avoid"}`;
omission prefers fewer permitted calls. `formal_explain` accepts `section="reuse"`
for proposal mappings. These options do not expand scientific permissions.

Scientific rejection is a structured outcome. Read `status` and
`request_complete` even when an MCP call itself succeeded. Invalid record kinds,
bad handles, malformed inputs, and file failures are tool errors.

MCP workspaces and handles last until server shutdown. Exported bundles also
remain temporary. Copy complete bundles and any needed `records/` directory to
durable storage before closing the server. A copied record directory can be
reopened as a workspace in its new location. See [MCP connection configuration](mcp.md).

## Inspect evidence without hiding failures

Verification summaries include scope, completeness, coverage counts, obligation
counts, diagnostic and assumption counts, and descriptive component names.
`runtime_policy` is
`operator_managed`: deployment is neither checked nor warned about.
Coverage records the presence and compatibility of requested work. Application
evidence can still leave a plan unknown or rejected when every goal is covered.
`capability_status` summarizes that evidence separately for represented calls.

`explain` pages use `total`, `offset`, and `next_offset`. Page sizes range from
1 through 100. Text excerpts contain at most 1000 characters and carry a
`truncated` flag. `record_path` identifies the complete JSON entry, and
`counterexample_count` identifies exact stored solver witnesses. A diagnostic's
scientific `path` is separate from its location in the report. Request additional
pages or read the located file when more evidence is needed.

Importing a report does not grant scientific acceptance. Handles identify saved
records; export always performs independent verification. Files are copied into
the workspace and structurally validated on import and use. Changing an original
source does not change its imported copy. Input and generated records have a
default 16 MiB per-record limit; the Python workspace constructor can set another positive limit.

`PlanningWorkspace` exposes the same import, propose, verify, explain,
capability-query, and export operations in Python. Inspect its signatures and
selected result `model_fields` when extending a saved builder script.
Use `save_molecule(geometry)` and `materialize_request(template_handle)` for
the molecular reuse workflow. `StoredMolecule`, `MoleculeBinding`, and
`RequestTemplate` are exported by `psi4_parser.formal` and have discoverable schemas.

## Measure agent-facing size

[Example 28](../examples/28-formal-agent-interface/README.md) retains a six-call
CLI walkthrough and measures actual UTF-8 response sizes against its complete
saved proposal. Its declarations are synthetic teaching evidence. The regression
suite also checks a 32-goal request, complete pagination, bounded choice previews,
compact MCP input schemas, and the public stdio connection.

These are response-size measures, not model token counts or research-accuracy
benchmarks. Broader agent evaluation remains part of the development roadmap.
