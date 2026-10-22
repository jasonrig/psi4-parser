# Scientific planning implementation

The framework constructs and verifies calculation plans and exports inputs.
Execution, scheduling, retries, output parsing, and numerical result acceptance
remain outside its public API. Native inputs may pass a produced geometry to a
dependent calculation. Development tests may use a separately configured Psi4.

This record tracks the ten requested phases. A phase is complete only when its
implementation, public documentation, and independent behavior tests agree.

| Phase | Required implementation and evidence | State |
| --- | --- | --- |
| 1. Construction boundary | No generated result-validation guards or execution APIs; compatibility entry points retained; source-level boundary regression. | Complete |
| 2. Scientific model | Typed systems, model settings, expected quantities, rational expressions, provenance, constraints, frames, and versioned serialization. | Complete |
| 3. Operation contracts | Reusable preconditions, effects, products, and dependencies; molecular, geometry, model, expression, derivative, scan, and environment rules. | Complete |
| 4. Scientific intent | Independent requests generate mandatory obligations and coverage checks; omitted work cannot pass through a trivial assertion. | Complete |
| 5. Capabilities | Source catalogs for scientific/input contracts, methods, drivers, options, elements, bases, and ECPs; provenance retained; runtime dependencies, versions, binaries, and compilation remain operator-managed. | Complete |
| 6. Verification | Located structural/scientific findings, solver proofs and counterexamples, assumption accounting, coverage, budgets, and report identity including rule/capability versions. | Complete |
| 7. Construction | Bounded deterministic expansion and solver selection among permitted alternatives; preferences and search exhaustion distinguished from impossibility. | Complete |
| 8. Scientific coverage | Fundamental calculations, composites and reactions, fragments and counterpoise/many-body methods, finite studies, environments, excited states, and properties with explicit support boundaries. | Complete |
| 9. Lowering/export | Backend contracts; checked builder lowering; plan/request/proof/manifest/input bundle; hashes and explicit dependency handoffs; no execution or parsed results. | Complete |
| 10. AI interface | Targeted capability/contract discovery, construction, verification, explanations, export, CLI/MCP surfaces, concise diagnostics, docs, examples, and agent-facing measures. | Complete |

Verification must include deliberately damaged plans, JSON/schema consistency,
independent algebra and chemistry expectations, bounded construction cases,
backend preprocessing, and packaging checks. Existing builder and parser behavior
must remain covered. CI and scientific capability evidence remain distinct from
claims that a physical calculation will converge or achieve a numerical outcome.

## Current evidence

The focused tests cover:

- `test_formal.py`: proof replay, counterexamples, schemas, concurrency, and the
  construction-only boundary.
- `test_formal_science.py`: core treatment, rational algebra, tensor exclusion,
  spin bookkeeping, constraints, and budgets.
- `test_formal_intent.py`: mandatory work, optimized-geometry dependencies,
  fixed model choices, required capability evidence, and exact request locations
  for malformed relationships before candidate search.
- `test_formal_capabilities.py`: exact combinations, negative support, literal
  option values and types, orbital occupancy, catalog identity, versionless source
  records, and acceptance independent of runtime observations.
- `test_formal_planning.py`: permitted alternatives and bounded search.
- `test_formal_catalogs.py`: shared source contracts and independent contributions
  through composition, discovery, construction, verification, and export;
  caller declarations retain their assumption status.
- `test_formal_reuse.py`: explicit sharing permissions, all six drivers,
  model/route ordering, optimized and subsystem dependencies, quantity frames,
  case boundaries, scientific backtracking, budgets, retained failed graphs,
  and separate native dispatch checks.
- `test_formal_extrapolation.py`: independently derived inverse-power weights,
  basis membership and fitting roles, treatment and geometry preservation,
  self-consistent wrong formulas, omission/dangling references, finite studies,
  audited DT/TQ composition, and native point option dispatch.
- `test_formal_exponential.py`: independent exponential weights, rational interval
  certificates, square-root decay, precision bounds, tiny exponents, exact
  complements, finite-study translation, export, and combined reference/correlation
  estimates with permitted sharing.
  Source-point checks retain different excited roots during scalar expansion
  while allowing repeated aliases of one validated native root to cancel.
- `test_formal_solvent.py`: explicit equilibrium equations and cavity choices,
  screening units, runtime-independent source contracts, independent shift
  formulas, common treatment/geometry, finite cases, reuse, and native option dispatch.
- `test_formal_pcm.py`: PCMSolver IEFPCM/CPCM inputs, explicit-medium parameters,
  independent shift formulas, cavity-sensitive reuse, runtime-independent acceptance,
  and native option restoration after parser or driver failure.
- `test_formal_excited_states.py`: explicit roots/spin/equations, honest primary
  returns, root-space bounds, exact product proofs and counterexamples, reuse,
  finite studies, transient native bindings, and native option dispatch.
- `test_formal_fragments.py`: full-basis provenance and geometry-only diagnostics.
- `test_formal_fragment_expansion.py`: independent inclusion–exclusion and spin
  coupling expectations, ambiguous states, and expansion bounds.
- `test_formal_studies.py`: independent case histories and a composed constrained
  optimization/counterpoise study, including a self-consistent wrong formula.
- `test_formal_coordinates.py`: independent scan targets, unit conversion, signed
  and periodic angles, fixed Cartesian frames, complete interval containment,
  future constraint propagation, mandatory case relations, and proof replay.
- `test_formal_products.py`: named product coverage, complex frequency types,
  native tensor frames, explicit thermal contexts, exact corrected-energy algebra,
  native output preservation, scoped settings, and separate engine integration.
- `test_formal_reactions.py`: exact nuclear/isotope/mass and charge conservation,
  species-specific references, ghost centers, nested composite protocols, and
  reaction expansion from independent species choices.
- `test_formal_thermal_reactions.py`: native and hybrid reaction quantities,
  common thermal state with species-specific symmetry, independent correction
  treatments, rational nested reactions, deliberate scientific errors, and
  finite-case export with preserved native bindings.
- `test_formal_export.py`: symbolic recipes, bundle hashes, native syntax,
  and preservation of existing destinations.
- `test_formal_isolation.py`: native default baselines, hostile global/local
  settings, raw values and changed flags, additional native modules, failure
  restoration, and scope setup independent of skipped branches.
- `test_formal_workspace.py`: copied record identity, tamper detection, size bounds,
  complete pagination, selected schema closure, and independent export acceptance.
- `test_formal_stored_inputs.py`: molecular handle reuse, exact metadata and
  independent intent preservation, changed/missing records, aggregate size bounds,
  relocated workspaces, and verification/export without source handles.
- `test_formal_cli.py` and `test_formal_mcp.py`: compact public interfaces,
  scientific exit statuses, schema consistency, stdio transport, and cleanup.

A typed builder `MoleculeClone` retains atom layout for optimization constraints.
Scientific requests, capability evidence, selection, and export have Python
interfaces. Compact CLI/MCP surfaces now share a file-backed planning workspace.
The supported construction workflow is implemented. Scientific coverage remains
finite, and agent-facing measures describe retained fixtures rather than general
agent reliability.
The test capability fixture remains synthetic. A first source-audited snapshot
now covers conditional HF/SCF, conventional MP2, and legacy SAPT cases from reviewed
sources, five bases through Ar, and retained reference observations. Its metadata
audit is retained and reconstructible; missing scientific cases remain explicit.

Examples 22–23 retain the relationship-only workflow. Examples 24–26 cover
independent requests, permitted model selection, tensor provenance, missing
evidence, search limits, constrained counterpoise studies, mandatory case
coverage, rational formulas, and unsupported meaning changes. They save native
construction bundles without executing calculations. The plugin's
`plan-calculations` skill uses these APIs and keeps scientific intent, evidence,
construction, and external execution distinct.
Example 27 adds closed-reaction expansion and a scientifically unbalanced
request whose proposed algebra is internally consistent. Reaction contracts
check every computational treatment as well as the overall nuclear inventory.
Example 28 retains a compact CLI walkthrough with full evidence in files and
measured response sizes. Planning-only MCP mode omits the recursive builder
schema while preserving discovery, construction, verification, explanation, and
export. These operations stop before execution.
Example 29 adds source-audited conditions, a rejected analytic derivative route,
an explicitly permitted fallback, and missing-algorithm evidence. Catalog
discovery and loading are available through Python, CLI, and MCP.
Example 30 adds independent coordinate requirements to a constrained scan.
Example 25 now composes those requirements with its counterpoise study.
Known inputs are measured; future coordinates require established constraint
domains. These checks retain numerical and optimizer-enforcement assumptions.
Example 31 composes named vibrational/property products with a hybrid Gibbs
estimate. Frequency records retain full native data for a separate consumer;
their producing calls use distinct writer labels. The shared contract catalogue now
includes named product cases and QCElemental serialization provenance.
Example 32 adds closed thermal reactions with native totals or explicitly chosen
hybrid models, including an internally consistent mixed-temperature rejection.
Example 33 records native option isolation for an MP2/HF comparison. The backend
captures native/global and named module values and flags, resets for every call,
and restores state on success or failure. Native integration checks include
empty defaults rejected by ordinary native setters. Unlisted plugin state and
process-resource configuration remain explicit assumptions.
Example 34 adds explicitly permitted shared optimizations and analyses while
preserving separate energy calls. Reuse preferences follow scientific model and
route choices. Every candidate is independently checked; rejected sharing can
fall back to separate calls. Compact interfaces and manifests retain the mapping
from logical goals to implementing steps, and failed checked graphs remain
inspectable.
Example 35 adds DT/TQ inverse-power corrections with explicit basis memberships,
exact model-derived weights, a finite-reference electronic estimate, and shared
TZ calls. The expanded snapshot retains basis-specific method cases. Reference binary
compilation limits do not restrict construction. Fitted nonlinear extrapolations
remain open.
Example 36 adds explicit SAPT monomers and state coupling, dimer/monomer basis
choices, fitted-basis roles, grouped components, and a counterpoise comparison.
The backend restores the call-entry native IO namespace. Native SAPT product
keys remain declarative, transient bindings for the separate consumer. The
snapshot retains 222 orbital/fitting dimension rows; unsupported elements and
unreviewed modes remain explicit. A separate development harness checks a small
SAPT input completes without collecting or parsing numerical results.
Example 37 adds equilibrium DDX PCM/COSMO/LPB energies and electronic shifts at
a common geometry and treatment. Typed dielectric, cavity, and screening choices
remain independent from numerical settings. Source-audited component discovery
retains optional component metadata as provenance. The current source catalog
constructs DDX jobs despite the reference installation's missing pyddx.
Solvent/cavity catalogues are optional reference data and are independently paged.
Example 38 adds PCMSolver IEFPCM/CPCM, named solvents or explicit dielectric/probe
pairs, and GePol cavity construction. The lowerer applies `PCM__INPUT` inside each
call's option scope; preprocessing needs no optional parser. Native tests replace
the parser and chemistry driver while checking the real helper's filename/options
restoration after success and failures. Solvent derivatives, nonequilibrium response,
custom cavities, and full free-energy cycles remain unfinished.

Runtime is explicitly operator-managed. Verification performs no dependency,
version, target-binary, installed-table, or compilation-limit checks and emits no
deployment warnings. Reports and manifests state this policy; component names
are unpinned descriptions. Source labels do not need to match an execution host.

Shared scientific contracts now apply by default to Python, CLI, and MCP propose,
verify, and export workflows. `CapabilityCatalog` and `load_catalog()` replace
version-named profile selection; the shared `psi4` collection has no engine
version/build fields. Individual evidence records retain their source identities,
and may span revisions or reference audits. A new Psi4 release requires no new
catalogue or complete re-audit. Maintain the relevant scientific/input rule when
behavior changes. Testing uses affected checks during development, with the full
suite reserved for completion of the overall implementation.

See [scientific planning](scientific-planning.md) for the current workflow.

Example 39 adds TD-SCF HF/PBE/B3LYP response construction and five ordered root
products. Primary returns retain their ground-reference meaning. Exact proofs
connect each native total to its own excitation; different roots remain distinct.
Root-space bounds use electron/basis evidence. Irrep populations, stability,
and physical state tracking retain explicit assumptions or support boundaries.
`combine_catalogs()` composes independently reviewed contributions without
repeating the reference binary audit. The shared catalogue now contains 382
method and 1657 product cases. Symmetry-resolved product selection, other kernels,
additional response operations, and state-specific derivatives remain unfinished.

Example 40 saves exact molecular inputs once and reuses them across four request
templates. Python, CLI, and MCP assemble complete independent requests before
planning; verification/export continue to consume full molecular inputs.
Hashes, states, stable IDs, isotopes, ghosts, fragments, units, and frame settings
are preserved. The example compares compact upload sizes and equivalent tool calls;
it does not measure model tokens or agent reliability.

Example 41 adds exponential HF reference limits in the cardinal or square-root
coordinate. Independent rational intervals certify requested coefficient error,
while complementary weights preserve one net energy. Source basis memberships,
treatment/geometry preservation, finite-study references, composite correlation
limits, and permitted HF sharing remain independently checked.

## Completion audit

The source and focused behavior audit checks the requirements above against
current implementation and artifacts. It found and fixed malformed request
relationships being diagnosed only after candidate construction, with locations
that could refer past the retained plan. Request and plan checks now share the
same reference rule, and malformed intent points directly to its supplied field.

| Phase | Acceptance evidence |
| --- | --- |
| 1. Construction boundary | Public exports and ten formal MCP tools remain construction/discovery operations. `test_formal.py` checks relationship-only compatibility and absence of numerical acceptance guards; exported inputs retain recipes for a separate consumer. |
| 2. Scientific model | All seven complete record schemas pass JSON Schema validation. All 85 exported record classes have field descriptions. Schema/JSON, rational, metadata, nuclear, quantity and frame cases cover the typed model. |
| 3. Operation contracts | Discovery and implemented checks cover six drivers; deliberate state, scalar/tensor, constraint, environment and product errors are rejected. Supported contracts are exercised through the retained examples. |
| 4. Scientific intent | Intent/reuse tests check omitted work, fixed alternatives, unauthorized sharing and optimized dependencies. Eight malformed relationship cases now identify exact request fields before search; workspace explanations preserve those paths. |
| 5. Capabilities | An independent contribution is composed, discovered, planned, verified and exported. Removing it leaves support unknown. Its caller assumption and catalogue digest remain in the bundle. Runtime observations never gate acceptance. |
| 6. Verification | Proof replay, violated formulas, unknown/bounded outcomes, consistency checks and identity tests cover the verifier. Rejected candidates retain their matching context. Fresh verification agrees with all 19 saved bundle identities and coverage records. |
| 7. Construction | Planning/reuse tests exercise request-order selection, fixed conflicts, scientific backtracking, explicit sharing and encoding/search limits. No performance-scoring policy remains. |
| 8. Scientific coverage | All 19 retained bundles pass fresh checks across calculations, composites, reactions, fragments, studies, environments, response and products. Negative cases in the scientific test modules preserve explicit unsupported/unknown boundaries. |
| 9. Lowering/export | Every saved payload hash passes; native re-export is byte-identical for all 19 bundles. Both relationship-only examples also remain identical. All 21 native inputs preprocess and compile separately. Five native isolation checks pass with observed drivers, including restoration after failure. |
| 10. AI interface | Python examples, compact CLI/MCP tests, reusable handles and paged findings cover the agent workflow. Examples 28/40 retain actual response/upload sizes. Plugin 0.1.20 has three parsed skills; 330 repository links pass. An independent wheel import plans, verifies, exports and locates invalid intent without importing Psi4. |

The affected proof/request/catalogue/coordinate/construction/export modules pass
97 tests, and the new compact invalid-request case passes separately. Project-wide
Ruff lint and formatting pass, and strict mypy reports no issues in 161 files.
Wheel/sdist checks confirm 41 formal files/resources and both compact interfaces
match current source; removed scoring modules are absent.

The final full-project run completed successfully: **6,645 passed, 579 skipped,
one third-party deprecation warning**, in 3,066.93 seconds. The skipped cases are
optional native interpreter/binary checks whose environment variables were not
configured for this run. Five native isolation checks were run separately with
an explicit development interpreter, and every generated formal input was
preprocessed and compiled without executing calculations.

All ten phases pass the defined construction-scope acceptance checks. Scientific
support boundaries and assumptions below remain explicit. Detailed commands and
evidence are retained in [the verification log](../examples/verification.log).

## Scientific coverage boundaries

Rules compose through independent goals and relationships; complete protocol
presets are not required. Catalogue contributions add reviewed method, basis,
option, and product cases. New kinds of scientific relationships require their
own contracts and lowering checks. Missing rules must remain unknown or
unsupported rather than being replaced by generic scalar algebra.

Current boundaries include external particle reservoirs, additional thermal and
standard-state models, checked tensor-frame transformations, fitted nonlinear
and noninteger-power extrapolations, non-cardinal fitting relationships,
additional SAPT variants, joint coordinate feasibility, specialized fragment
environments, solvent derivatives and nonequilibrium response, additional
excited-state operations, and plugin-specific native state. These describe where
new scientific contracts would be needed; they are not an instruction to keep
adding unrelated features during the completion audit.

Selection follows explicitly permitted scientific alternatives in request order.
Call sharing remains subject to explicit permission and independent verification.
Cost, failure-risk, and memory scoring are outside this construction framework.

The completion gate is the final project validation above. Further scientific
extensions require their own scope and evidence.
