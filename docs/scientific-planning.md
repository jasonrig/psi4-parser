# Construct plans from independent scientific requests

Use `ScientificRequest` to specify mandatory work independently from the steps
proposed by an AI. Call `propose(request)` to use shared scientific contracts,
or `verify(plan, request=request)` to check an existing plan. `export_bundle()`
saves construction artifacts for a separate execution system.

The framework ends at construction. It has no engine launcher, result parser,
numerical acceptance checks, scheduler, or retry policy.

For compact CLI, MCP, and reusable file handles, see
[planning interfaces](formal-interfaces.md). Python remains useful for composing
new requests from builder geometry operations.
Use [coordinate contracts](formal-coordinates.md) to require independently
specified scan values on prepared inputs and constrained future geometries.
Use [product contracts](formal-products.md) for named spectra, derivatives,
properties, and explicit thermal conditions and corrected-energy expressions.
Use [option isolation](formal-isolation.md) to understand the per-call native
baseline, restoration, module coverage, and separate process resources.
Use [calculation reuse](formal-reuse.md) to permit one matching call to cover
multiple goals while retaining independent intent, dependencies, and frames.
Use [basis extrapolation](formal-extrapolation.md) for independently declared
correction models, basis-family evidence, and exact extrapolation recipes.
Use [SAPT contracts](formal-sapt.md) for explicit monomer partitions, basis and
induction choices, fitting roles, and component sums.
Use [solvent contracts](formal-solvation.md) for equilibrium DDX energies,
explicit continuum/cavity choices, and checked electronic solvation shifts.

Runnable construction examples cover
[model selection and missing evidence](../examples/24-formal-planning/README.md),
[a constrained counterpoise study](../examples/25-formal-counterpoise-study/README.md),
and [exact rational expressions](../examples/26-formal-rational-expression/README.md).
An additional [reaction example](../examples/27-formal-reaction/README.md)
checks stoichiometry independently from energy algebra.
Each retains a request, bundle, compact summary, and rejected variants. Their
shared capability catalog contains explicitly synthetic teaching declarations.
For actual work, use independently reviewed contracts for the intended methods
and settings.
[Example 29](../examples/29-formal-audited-capabilities/README.md) uses a bundled,
source-audited snapshot with explicit algorithm conditions and component names.

## Keep intent independent from implementation

A request contains exact molecular inputs and ordered goals. `CalculationGoal`
specifies the operation, geometry, permitted models, constraints, expected
quantity, properties, and derivative routes. One model fixes the choice;
several explicitly permit selection among them.

`ExpressionGoal` specifies an exact scalar formula using preceding goals.
Coefficients may be integers or `Rational` values. `SubsystemGoal` retains
selected parent fragments as real nuclei and every other fragment as ghost
basis centers. It requires explicit charge and spin and a fixed parent frame.

Goals compose through stable references. An optimization supplies a future
geometry under its goal ID. A frequency calculation can require that geometry
without knowing its coordinates. Expected quantities describe meaning, units,
shape, state, and provenance; they contain no calculated values.

Steps declare goal IDs through `satisfies`. Verification checks every mandatory
goal and derives geometry and formula requirements. Omitting a calculation
cannot pass through a trivial assertion. A model change must remain within the
independent request.

Calculation goals require separate calls by default. The same explicit
`reuse_group` permits matching calls to share an implementation; a planner
preference cannot grant that permission. `PlanningPreferences` ranks sharing
after scientific model and route choices. The manifest retains every goal's
implementing steps, including aliases. See [example 34](../examples/34-formal-calculation-reuse/README.md).

## Use reusable scientific contracts

The shared catalogue describes scientific and input relationships across Psi4
releases. `propose(request)` and `verify(plan, request=request)` use it by default;
no version-specific profile is selected or maintained. An explicit
`CapabilityCatalog` can extend coverage for a scientific feature. Evidence
references identify documentation, source, saved probes, or caller declarations.
Method entries cover exact method/driver/reference/route combinations. Basis
entries cover roles, elements, ECP associations, and orbital function counts. Option entries constrain
literal values and applicable methods. Orbital dimensions constrain electron
occupancy and external-matrix shape; missing dimension evidence stays unknown.

The planner does not launch Psi4 to discover these facts. Source versions and
builds belong to individual evidence records;
they never constrain the execution host. Declarations remain assumptions in
reports. Missing evidence stays `unknown`; explicit negative evidence stays
`unsupported`. The fixture in `tests/conftest.py` is synthetic, not evidence for
a real build. Existing syntax compatibility metadata also does not establish
scientific method support.
Named product support is separately recorded within each producing method case.
Missing product or native-record evidence remains unknown even when the method
itself is supported. `ProductGoal` coverage cannot be replaced by the producing
calculation's primary return value.

Method evidence can require explicit `OptionCondition` values; unmatched or
omitted settings leave support unknown. Disjoint cases can express different
outcomes for core treatments or algorithms. Component observations are optional
reference metadata. Missing dependencies, versions, and reference compilation
limits generate neither verification failures nor warnings.
Use `available_catalogs()` and `load_catalog()` to discover and load bundled
source-contract evidence without importing Psi4. See [capability evidence](formal-capabilities.md)
for scope, provenance, source review, and the separate maintenance collector.

## Compose studies and fragment calculations

`finite_study()` repeats an arbitrary supported request over explicitly supplied
`StudyCase` inputs. Each case has independent geometry history and mandatory
coverage. `CaseModels` permits explicit model replacements.
`StudyCase.relations` adds mandatory case-specific requirements, including
`CoordinateValue` and `CoordinateRange`. Use template input and goal IDs; the
expander namespaces them for each case. Unconstrained future coordinates remain
unknown, while matching frozen or bounded constraints can establish a contract.

`fragment_expansion()` expands a `FragmentStudy` into full-basis subsystem
calculations and an exact interaction expression. Complete order simplifies to
cluster minus monomers; truncated orders retain the required connected
increments. Ambiguous open-shell coupling requires `SubsystemState` choices.
These goals compose with optimization, constraints, and finite studies.

Matching units do not establish physical meaning. The verifier rejects
unsupported relabelling, such as an electronic energy presented as Gibbs energy.
Full-basis interaction formulas have independent subsystem, model, geometry,
and coefficient checks. Broader thermochemical contracts remain unfinished.

## Construct closed reaction energies

`reaction_expansion()` turns a `ReactionStudy` into species calculations and an
exact `reaction_energy` expression. Each `ReactionParticipant` names a geometry,
explicitly permitted models, and a nonzero integer or `Rational` coefficient.
Negative coefficients consume species; positive coefficients produce them.
Compose the returned goals with exact molecular inputs and optional preceding
optimizations in a `ScientificRequest`.

The verifier independently expands nested energy expressions and checks real
nuclei, isotope labels, explicit masses, and charge. Ghost and dummy centers do
not contribute real nuclei. Unspecified label defaults remain distinct from
explicit isotope or mass choices; supply consistent declarations when those
choices are intended to match.

Each computational treatment must separately balance its nuclei and charge.
This supports nested composite energies while rejecting one-sided method, basis,
or core-treatment changes. A species' explicit RHF/UHF/ROHF reference can differ;
all other normalized model fields remain part of treatment identity. Capability
checks still cover the exact reference separately for every calculation.

For a thermal reaction, select `ReactionStudy.quantity` and supply
`ReactionThermochemistry` for each participant. A single frequency call supplies
a native total, or explicit correction models compose a hybrid molecular energy.
Temperature, pressure, treatment, and projection choices must agree across
species; rotational symmetry stays species-specific. Electronic and correction
treatments balance independently. See [reaction contracts](formal-reactions.md)
and [example 32](../examples/32-formal-thermal-reaction/README.md).

An ionization expression that omits an electron reservoir is not a
charge-conserving closed reaction. An ordinary `energy_difference` can describe a
requested comparison without claiming reaction balance or a shared thermal state.
External particle reservoirs, pathways, and kinetic feasibility need more contracts.

## Construct and export

This example uses request and capability documents supplied by the caller:

```python
from pathlib import Path

from psi4_parser.formal import (
    CapabilityCatalog,
    ScientificRequest,
    export_bundle,
    propose,
)

request = ScientificRequest.model_validate_json(
    Path("scientific-request.json").read_text(encoding="utf-8")
)
catalog = CapabilityCatalog.model_validate_json(
    Path("psi4-capabilities.json").read_text(encoding="utf-8")
)
proposal = propose(request, catalog)
print(proposal.status, proposal.attempts)
if proposal.plan is not None:
    exported = export_bundle(proposal.plan, request, catalog, Path("job-bundle"))
    print(exported.directory, exported.manifest_digest)
```

Selection defaults to finite alternatives in the request's preference order. Z3 enforces
selection constraints, including model relationships. Each complete candidate
passes through the independent verifier. `SearchLimits` bounds alternatives,
candidate attempts, solver calls, and time. Exhaustion does not prove
impossibility. `no_candidate` refers only to declared finite alternatives.

For an existing plan, call `verify(plan, request=request, catalog=catalog)`.
Inspect `status`, `coverage`, `diagnostics`, and `request_complete`. Save full proof
queries rather than repeatedly sending them through an AI. `Limits` bounds
verification steps, obligations, solver resources, and time.
`capability_status` separately summarizes application evidence for represented
calls. A failed proposal can save `last_candidate` so its diagnostic paths remain
inspectable; only `plan` denotes an accepted construction.

Calling `verify(plan)` retains the original relationship-only API. It checks
supplied relationships and operation prerequisites without claiming complete
scientific intent coverage. Only an accepted independent request sets
`request_complete`.

## Hand construction artifacts to a separate consumer

Export creates a new directory without overwriting an existing one:

```text
scientific-request.json
calculation-plan.json
capabilities.json
verification.json
manifest.json
inputs/workflow.dat
```

The manifest records expected quantities, dependencies, symbolic expressions,
assumptions, engine requirements, and payload hashes. Its own hash is returned.
Verification identity binds the plan, request, capability snapshot, rule and
solver versions, and limits. Hashes establish artifact identity; Python lowering
remains a tested component rather than a formally proved compiler.

Native input passes future geometries in memory. Symbolic expressions remain
recipes for a separate result consumer. Bundles contain no execution status or
parsed results. The manifest is written last; an I/O failure may leave an
incomplete directory.

Discover relevant fields through constructor signatures and selected
`model_fields`. Use `operation_contracts()` and `discover_capabilities()` for
targeted queries. JSON schemas describe saved records. Some scientific fields
have representations while their lowering remains unsupported; verification
reports these boundaries. See [the roadmap](formal-development.md) for remaining work.
