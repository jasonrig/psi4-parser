# Build checked plans from scientific intent

Use `psi4_parser.formal` for independent scientific requirements, bounded model
selection, geometry and quantity provenance, exact scalar formulas, and
construction export. Prepare molecules with `psi4_parser.builder`. Keep
execution, result parsing, and numerical acceptance outside this workflow.

For a new request, start with the self-contained [construction and repair
example](formal-start.md). This reference supplies targeted discovery, compact
interfaces, and task-specific details; read only the sections needed.

## Discover the selected runtime

Follow [runtime and discovery](runtime.md). Check selected exports and signatures
before adapting an example:

```python
import inspect
import psi4_parser.formal as formal

print(inspect.getfile(formal))
print(inspect.signature(formal.propose))
print(inspect.signature(formal.verify))
print(inspect.signature(formal.export_bundle))
print(formal.CalculationGoal.model_fields["models"].description)
```

Inspect only the constructor fields needed for the task. Use
`operation_contracts(driver=...)` for prerequisites and products, and
`discover_capabilities(catalog, method=..., driver=...)` for exact catalog entries.
Read the selected function's help and relevant schema definitions when needed.
Use `psi4-parser formal --help` for compact CLI operations, or inspect the
connected server's `formal_*` tools when available. The Python workspace API is
`PlanningWorkspace`. Keep discovery and calls on the same source revision.

If the selected runtime lacks these APIs, use a source revision that contains
them. A local development checkout may contain changes absent from remote
`main`; use that checkout's environment for discovery and scripts. Never bypass
scientific verification by substituting the older relationship-only call.

## Use compact planning interfaces

Prefer the `formal` CLI group or planning MCP tools for saved requests and
catalogs. Compose new scientific requests in Python when geometry preparation or
goal expansion requires it. Read leaf-command help before adapting a command:

```sh
psi4-parser formal schema request --definition Model --field basis
psi4-parser formal contracts --driver optimize
psi4-parser formal catalogs
psi4-parser formal --workspace planning-artifacts propose request.json
```

CLI calls return compact JSON and keep full records in the persistent workspace.
Reuse the returned `kind:ID` handles, or supply local JSON paths. Use
`formal explain` for paged issues, coverage, assumptions, or choices. Interpret
exit 1 as scientific rejection, 2 as input/file failure, and 3 as unknown or
exhausted; discovery and accepted construction return 0. Read stdout even after
a scientific nonzero exit.

### Stored molecules and call reuse

Reuse molecular inputs across requests with `StoredMolecule`, `MoleculeBinding`,
and `RequestTemplate`. Save a molecule once through `formal_load(kind="molecule", ...)`
or `PlanningWorkspace.save_molecule()`. A template binds each saved handle to the
input name used by its independent goals and relations. Load the template with
`kind="request_template"`, then call `formal_request(template=HANDLE)`; the CLI
equivalent is `formal request TEMPLATE_PATH_OR_HANDLE`. Python callers use
`PlanningWorkspace.materialize_request()`. Assembly validates saved molecular records
and returns a full request with exact inputs. Propose, verify, and export use that
request; bundles retain complete coordinates without requiring the original
handles. Assembly is preparation, not scientific approval. See
[example 40](https://github.com/jasonrig/psi4-parser/tree/main/examples/40-formal-stored-molecules).

Matching explicit `CalculationGoal.reuse_group` values permit one matching call
to cover multiple goals; null requires a separate call. Never grant that
permission merely to reduce calls or pass verification. `PlanningPreferences`
and CLI `--call-reuse prefer|avoid` rank sharing after the default model/route
choices. MCP accepts `preferences={"calculation_reuse": "avoid"}`. The preference
is soft; null groups require separation. Counts describe top-level calls, not
runtime cost, statistical independence, or accuracy.

Inspect `calculation_count`, `shared_call_count`, and proposal explanations with
`section="reuse"` (`--section reuse` in the CLI). Every logical goal remains
mandatory. The manifest's `goal_coverage` maps goal aliases to implementing
steps; native result keys and product bindings use actual step IDs. Keep this
mapping for the separate execution consumer. Reuse follows geometry provenance,
translates quantity frames, and stays within each `finite_study()` case. See
the matching [reuse guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-reuse.md)
and [example 34](https://github.com/jasonrig/psi4-parser/tree/main/examples/34-formal-calculation-reuse).

### Compact MCP tools and saved evidence

Start `psi4-parser mcp --planning-only` to expose compact planning tools without
the recursive builder schema. Propose, verify, and export use the shared Psi4
contracts when `capabilities` is omitted. No release profile is required.
For targeted discovery, load the shared rules with
`formal_load(kind="capabilities", catalog="psi4")`. Supply exactly
one of `path`, `source`, and `catalog`. Loading a snapshot does not detect or
certify an installed engine. Load request documents once with `formal_load`, query
`formal_schema`, `formal_contracts`, or `formal_capabilities`, then use
`formal_propose`, `formal_verify`, `formal_explain`, and `formal_export`. Missing
capabilities stay unknown. Check scientific status even when the tool call itself
succeeded. MCP records and bundles expire at shutdown; copy needed artifacts to
durable storage. Use only tools actually exposed by the selected server.

Export always reverifies the plan, independent request, and capability catalog.
A handle identifies saved bytes; loading a report is not a scientific approval.
Summaries preview at most ten model choices and explanations expose page counts,
truncation flags, and paths to exact evidence. Retrieve additional pages instead
of silently discarding findings. The `json_schema` field contains a selected
schema only when fields were requested.

## Save independent intent and application evidence

Save the request before proposing a plan. `ScientificRequest` contains exact
molecules and ordered goals. `CalculationGoal` fixes the driver, source geometry,
allowed models, constraints, properties, derivative routes, and primary quantity.
One model fixes that choice. Multiple models explicitly authorize alternatives
in preference order; do not add alternatives without scientific authorization.

An optimization goal supplies a future geometry by ID. Later goals can depend on
it without coordinates. `ExpressionGoal` combines earlier scalar quantities with
integer or `Rational` coefficients. `SubsystemGoal` retains selected fragments
as real nuclei and all other parent fragments as ghost basis centers; explicit
state and a fixed parent frame are required.

### Basis extrapolation

`extrapolation_expansion()` supplies four energy goals, two target-minus-reference
differences, and an `InversePowerExtrapolation` recipe. Choose `ExtrapolationStudy`
family, positive integer power, and low/high basis points independently. Inspect
`BasisCapability.sequence` for each orbital and explicit fitting basis; missing
membership remains unknown. Do not infer augmentation or cardinal numbers from
spelling or weaken the scientific model to pass verification. Target/reference
treatments and geometry must remain consistent across points. An explicit study
`reuse_group` can share matching calls across purposes. Final coefficients are
checked independently from the requested convergence model and remain symbolic
in exported manifest expressions. Asymptotic behavior and physical accuracy are
assumptions. Read the matching
[basis-limit guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-extrapolation.md)
and [example 35](https://github.com/jasonrig/psi4-parser/tree/main/examples/35-formal-basis-extrapolation).
Discover the recipe with `formal schema request --definition ExpressionGoal --field extrapolation`.

For exponential HF reference limits, pass `ReferenceExtrapolationStudy` with two
`BasisEnergyPoint` records to `extrapolation_expansion()`. Choose `alpha` as a
positive rational, `shape="cardinal"` or `"sqrt_cardinal"`, and
`coefficient_digits` when overriding its default 15. `ExponentialExtrapolation`
certifies absolute rational weight error at most `10**(-coefficient_digits)`
and an exact weight sum of one. Both points must preserve HF/SCF treatment and
geometry with evidenced basis memberships. The quantity is
`basis_limit_reference_energy`; combine it with one correlation correction for
an electronic estimate. Never weaken the coefficient bound or change the decay
model just to pass. These certificates concern construction; physical convergence
and result evaluation remain separate. Read
[example 41](https://github.com/jasonrig/psi4-parser/tree/main/examples/41-formal-exponential-extrapolation)
and the matching basis-limit guide before choosing a model.

### SAPT

For SAPT, attach `SAPTAnalysis` to an energy `CalculationGoal`. Declare the
ordered real monomers, dimer/monomer basis mode, coupled-induction choice, and
optional all-ghost midbond fragment independently. Preserve explicit monomer
states and the supported high-spin complex; ROHF requires uncoupled induction.
Do not infer SAPT support from an ordinary energy route. Inspect the exact
method/reference case, explicit fitting-role conditions, and basis/induction
features on both method and product pages. The primary return means interaction
energy. Named products include its total and four grouped components. Their
sum is checked against the producing context; generic energy algebra does not
establish SAPT meaning. Read the matching
[SAPT guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-sapt.md)
and [example 36](https://github.com/jasonrig/psi4-parser/tree/main/examples/36-formal-sapt).
Discover the intent with `formal schema request --definition CalculationGoal --field sapt`.

### Implicit solvation

For equilibrium implicit solvent, attach `Environment(kind="ddx", ...)` to each
solvated model. `DDXSolvation` selects PCM, COSMO, or screened LPB, an optional
explicit dielectric, the radius table, and its positive scale. Omitted
dielectrics require a named lookup; the default cavity scale remains 1.1 even
when the table changes. LPB requires positive `screening_inverse_bohr`, converted
to the molecule's native units by construction. Keep numerical DDX settings in
`Environment.settings`; dedicated fields cannot be overridden through options.
Query `formal capabilities CATALOG --section environments --name ddx` with a
saved catalogue path or handle, and inspect the exact method input contract. Optional cavity/lookup catalogues are reference data;
their absence and local component availability do not affect verification.
Installation and execution failures belong to the operator.

For PCMSolver use `Environment(kind="pcm", pcm=PCMSolverSolvation(...), ...)`.
Select equilibrium IEFPCM/CPCM and the GePol table, scaling, and surface area.
An explicit dielectric requires a probe radius; omitted pairs use native solvent
lookup. Area uses square bohr and probe radius uses bohr regardless of molecular
units. `cpcm_correction` applies only to CPCM. Each call supplies its own
`PCM__INPUT` text inside the option scope; constructing or preprocessing the input
does not invoke the optional parser. Keep runtime failures operator-managed.

Use `electronic_solvation_shift` for exactly one solvated minus one vacuum
energy with the same geometry provenance, state, and solvent-free treatment.
Self-consistent altered weights or model choices still fail the independent
contract. Thermal, non-electrostatic, and standard-state terms require additional
contracts before claiming Gibbs solvation. Energy-only DDX/PCMSolver lowering and
remaining derivative boundaries are documented in the matching
[solvent guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-solvation.md)
and examples [37](https://github.com/jasonrig/psi4-parser/tree/main/examples/37-formal-solvation)
and [38](https://github.com/jasonrig/psi4-parser/tree/main/examples/38-formal-pcmsolver).
Discover parameters with `formal schema request --definition DDXSolvation`
or `--definition PCMSolverSolvation`.

### Finite studies, fragments, and coordinate scans

`finite_study()` composes arbitrary supported goals over explicit case inputs.
Prepare numerical geometries first. Add independent `CoordinateValue` or
`CoordinateRange` requirements through `StudyCase.relations` when scan values
matter, using template input or goal IDs. The expander namespaces these alongside
the case history. Use explicit length/angle units and tolerances. Known inputs
are measured; future optimized coordinates need matching frozen or bounded
constraints. Never infer a future coordinate from its starting geometry.
Absolute Cartesian targets require a fixed center of mass and orientation.
Read the matching [coordinate guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-coordinates.md)
for signed/periodic angles, optimizer branch limits, and measurement assumptions.
`fragment_expansion()` constructs full-basis counterpoise or truncated many-body
interaction goals. Preserve its common-model relations. Supply `SubsystemState`
when open-shell coupling is ambiguous. Bound study and subsystem expansion.

### Reaction composition

`reaction_expansion()` builds a closed reaction from explicit species and exact
signed coefficients. Its default electronic quantity yields `reaction_energy`.
For Gibbs, enthalpy, thermal energy, or zero-point totals, select
`ReactionStudy.quantity` and give every participant `ReactionThermochemistry`.
Empty correction models use one native frequency total per species; explicit
correction models request separate electronic energies and matching frequency
corrections at that species' geometry. Preserve the common temperature, pressure,
treatment, and projection choices while choosing rotational symmetry per species.
Verification checks real nuclei, isotope/mass choices, charge, and each
electronic/correction treatment independently, allowing species-specific SCF
references. Nested composites and finite studies retain these checks. Read the
[reaction guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-reactions.md)
and [example 32](https://github.com/jasonrig/psi4-parser/tree/main/examples/32-formal-thermal-reaction)
at the selected source ref. External particle reservoirs and standard-state
conversions need additional contracts; a generic `energy_difference` does not
claim closed-reaction conservation or a common thermal state.

### Capability evidence

Use a `CapabilityCatalog` for scientific and supported-input contracts.
Evidence identifies documentation, source, saved probes, or caller declarations.
Version/build labels retain provenance and never constrain the execution host.
Input support is specific to method, driver, reference, derivative
route, features, options, basis roles, elements, and orbital dimensions. Inspect
the matching [Psi4 sources](psi4.md); do not infer support from accepted syntax.
Missing evidence remains unknown. Caller declarations remain assumptions, even
when the report is proved. Never relabel a declaration as documentation or a
probe. The shipped demonstration catalog is deliberately synthetic.

Shared collections are discoverable through `available_catalogs()` or
`formal catalogs`. `load_catalog()`, `formal load-catalog psi4`, and the
MCP load operation read the same packaged evidence. No target binary, dependency,
or version inspection is needed. `runtime_policy="operator_managed"` records
this boundary in reports and manifests, without deployment warnings.

Method cases may carry `conditions`: required explicit global or module-local
option values, matched against the settings that construction emits. Inspect
relevant scientific cases with targeted capability queries. An omitted
condition or uncovered algorithm is unknown; a matching negative case is
unsupported. Optional dependency observations never affect acceptance. Component
names in manifests are descriptive and carry no version pins. Reference binary
compilation limits do not constrain plans for another machine.
Read the matching source's [capability guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-capabilities.md)
and [audited example](https://github.com/jasonrig/psi4-parser/tree/main/examples/29-formal-audited-capabilities)
for provenance and finite coverage. Maintain relevant entries when scientific
or input behavior changes; do not create catalogues for each Psi4 release.
An extension needs its own evidence; never turn a caller assertion into
source or probe evidence to obtain acceptance.

### Excited response

For excited response, attach `TDSCFAnalysis` to the model. Declare the root set,
spin sector, RPA/TDA equation, and response convergence controls independently.
The energy driver's primary return remains the ground reference. Require
`excitation_energy`, `excited_state_energy`, oscillator strengths, or transition
moments through `ProductGoal` with an explicit `electronic_target`. Product root
numbers refer to energy order within the requested set, without physical state
tracking across geometries or models. Preserve native scalar/array bindings for
the separate consumer; no value retrieval or collection writer belongs in input
construction. Read the matching
[excited-state guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-excited-states.md)
and [example 39](https://github.com/jasonrig/psi4-parser/tree/main/examples/39-formal-excited-states).
Discover `TDSCFAnalysis` and `ProductGoal.electronic_target` through selected schema
queries. Use `combine_catalogs()` to add independently evidenced contributions;
conflicts must be resolved explicitly, never overwritten to obtain acceptance.

## Propose, diagnose, and export

Create a request with the [complete example](formal-start.md), or load a saved
request with the default shared contracts:

```python
from pathlib import Path
from psi4_parser.formal import (
    ScientificRequest,
    export_bundle,
    propose,
)

request = ScientificRequest.model_validate_json(Path("request.json").read_bytes())
proposal = propose(request)
Path("proposal.json").write_text(proposal.model_dump_json(indent=2), encoding="utf-8")
print(proposal.status, proposal.attempts)
if proposal.plan is not None:
    exported = export_bundle(proposal.plan, request, destination=Path("new-job-bundle"))
    print(exported.directory)
```

`SearchLimits` bounds alternatives, candidates, solver calls, and time. Selection
follows declared preference order. Every complete candidate is independently
verified. `no_candidate` concerns only the finite declared alternatives;
`exhausted` is a search limit, not proof of impossibility.

For an existing plan, call `verify(plan, request=request)`.
Inspect `Report.status`, `scope`, `request_complete`, goal `coverage`, located
`diagnostics`, and non-proved `obligations` with their counterexamples.
A failed relationship can appear only in obligations, even when diagnostics are
empty and `capability_status` is supported. `Limits` bounds independent
verification. Correct the plan or obtain missing evidence while retaining the
independent intent. Intent changes require a scientific reason, not merely a
failed check.

An unsuccessful proposal may save `last_candidate`, the checked graph matching
its report's diagnostic paths. It is not an accepted plan. `capability_status`
summarizes evidence for represented calls independently from coverage and other
contracts. Exact report replay uses the saved report limits as part of context.

| Verification status | Next action |
| --- | --- |
| `proved` | Require `scope="scientific_request"` and `request_complete=True`; inspect coverage, assumptions, and scientific/input evidence before export. |
| `invalid` | Correct malformed inputs or references at the reported path. |
| `violated` | Inspect failed obligations as well as diagnostics; repair the counterexample, missing work, or scientific contract violation against the saved request. |
| `unsupported` | Explain the unsupported evidence or lowering contract; do not claim acceptance. |
| `unknown` | Obtain missing evidence or address the reported verification limit. |

Proposal status is a separate result: `constructed` supplies an accepted plan;
`invalid` needs a request/reference repair; `unknown` needs the reported evidence
or undecided check addressed; `exhausted` reached a declared search bound; and
`no_candidate` means none of the finite declared choices was accepted. Inspect
proposal diagnostics and its matching report before choosing a repair. Search
limits are not scientific evidence against every possible protocol.

For a recoverable implementation error, change the located field and reverify
against the same request. For missing evidence, inspect the exact method,
product, and condition using targeted discovery; add a scientific extension only
with appropriate provenance. A caller declaration remains an assumption and is
not a substitute for documentation/source evidence. Increase a search or solver
bound only when its diagnostic identifies that limit and the task warrants the
additional work. Do not repeatedly retry unchanged inputs, add unapproved
fallbacks, remove goals, or invent evidence. When progress needs a scientific
decision or unavailable evidence, report the blocked goal and exact gap.

See the [geometry-dependency repair](formal-start.md#diagnose-and-repair-an-incorrect-geometry-dependency)
for a complete rejected-plan example that preserves its independent request.

Keep proof queries and complete reports in files. Return compact status, choices,
missing goal IDs, diagnostic paths/codes, and artifact paths to the AI. Avoid
repeatedly printing whole schemas, capabilities, or SMT expressions.

Export requires complete accepted intent and a new destination whose parent
exists. It saves the request, plan, capability snapshot, verification, native
input, and a manifest containing dependencies, expected products, symbolic
recipes, assumptions, and payload paths. Existing directories are never overwritten.

### Named products and thermochemistry

Named `ProductGoal` declarations require combination-specific product evidence.
Use `discover_products()` or `formal_capabilities` with `section="products"`,
a producing method/driver filter, and an exact `product` name. Method pages
return `product_count` by default; request nested evidence explicitly when needed.
Attach `VibrationalAnalysis` to full frequency goals for thermal products, with
explicit kelvin, pascal, rotational symmetry number, and projection choices.
Keep the same context and geometry when composing corrected molecular energies.

The manifest records native frequency output templates and member encodings for
separate collection and parsing. Native inputs request distinct `.vibrec` files
so later calls cannot erase transient thermochemistry data. Read the matching
[product guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-products.md)
and [example 31](https://github.com/jasonrig/psi4-parser/tree/main/examples/31-formal-products-and-thermochemistry)
for canonical layouts, exact correction formulas, native output handling, and
remaining scope. These declarations do not perform result retrieval or validation.
SAPT `native_variables` bindings identify a producer, quantity, native key, unit,
and transient lifetime. Export emits no variable retrieval or collection writer.
The separate consumer must collect after the producer and before a later call
overwrites the variables; these bindings do not promise durable results.
The input carries future geometries in memory; expressions stay symbolic for a
separate consumer. The lowering implementation is tested rather than formally proved.

### Export option and namespace policies

Formal calls start from native option defaults and then apply the declared model,
analysis settings, and constraints. Export records
`option_policy="native_defaults_per_calculation"`; captured native/named module
values and changed flags are restored even after failure. Keep resource settings
and unlisted plugin state as separate requirements. Read the matching
[isolation guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-isolation.md)
and [example 33](https://github.com/jasonrig/psi4-parser/tree/main/examples/33-formal-option-isolation).
Resetting options does not satisfy a capability condition that requires an
explicit setting. A missing manifest policy makes no isolation claim.
`namespace_policy="restore_after_calculation"` also restores the native IO
namespace at call entry, including after SAPT and failures. Native molecule
declarations may change the namespace before that boundary. Compact export
summaries retain both policies.

## Keep the claims precise

`verify(plan)` alone checks supplied relationships and operation prerequisites.
It cannot establish completeness against omitted scientific intent. `Plan` JSON,
`ScientificRequest` JSON, and builder `JobSpec` JSON are distinct formats.

Quantity meaning matters as well as shape, units, numeric domain, and frame.
A frequency call's primary return is electronic energy. Require named products
for its spectrum, modes, or thermal quantities. Do not label electronic energy
as Gibbs energy. Some represented features,
including additional solvent drivers, state-specific Model.electronic_target,
and per-center basis
assignments, currently have unsupported formal lowering. Keep those boundaries
explicit and report any use of the ordinary builder outside the checked plan.

Proofs are conditional on evidence and listed assumptions, including successful
engine behavior. They do not establish convergence, physical accuracy, or
research suitability. Choose the scientific model separately.

Read the [planning guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/scientific-planning.md),
[interface guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-interfaces.md),
[relationship guide](https://github.com/jasonrig/psi4-parser/blob/main/docs/formal-jobs.md),
and [examples](https://github.com/jasonrig/psi4-parser/tree/main/examples) at the
same source ref as the runtime. Installed docstrings remain the first reference.
