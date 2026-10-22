# Check scientific and input contracts

A `CapabilityCatalog` describes method/driver combinations, options, basis facts,
quantity types, and their source evidence. Use it to check that a proposed plan
preserves its scientific intent and can be lowered through the supported input
API. [Example 29](../examples/29-formal-audited-capabilities/README.md) illustrates
algorithm conditions and an explicitly permitted derivative fallback.

Planning uses the shared Psi4 catalogue by default:

```python
from pathlib import Path
from psi4_parser.formal import propose, verify, export_bundle

proposal = propose(request)
if proposal.plan is not None:
    report = verify(proposal.plan, request=request)
    bundle = export_bundle(proposal.plan, request, destination=Path("new-job-bundle"))
```

There is no per-version profile to select, create, or certify. A Psi4 release
does not require a new catalogue or a complete re-audit. The catalogue itself
has no application-version or binary-build fields. Each rule cites its own
evidence, and sources from different revisions may coexist. Maintain a rule
when its scientific meaning or input contract changes.

Use `load_catalog()` to inspect the built-in collection, or pass an explicit
`catalog=` when extending contracts for a scientific feature. Custom catalogues
are optional extensions, never descriptions of an installed engine. CLI/MCP
propose, verify, and export also use the shared collection when `capabilities`
is omitted.

## Leave deployment to the operator

Formal verification never checks installed components, target binaries, or
version compatibility, and emits no dependency or version warnings. The builder
can run without Psi4 and construct inputs for a different machine. Compilation,
installation, optional libraries, and execution failures belong to the operator.

Reports and manifests state `runtime_policy="operator_managed"`.
`capability_status` describes scientific/input contracts, not runtime readiness.
Version strings, build hashes, and component observations in individual evidence
are provenance only. They do not need to match the target machine or one another.
`required_components` retains descriptive names with unpinned versions; it is
not a preflight check. Optional component and solvent-table catalogues can be
queried for reference, but their absence or status never blocks verification.

Artifact hashes still bind a request, plan, rules, and source evidence. Checking
saved bytes for corruption is independent of checking an execution environment.
An accepted construction does not establish convergence or scientific accuracy.

## Preserve explicit scientific choices

Method evidence identifies the driver, reference, derivative route, expected
quantity, features, and supported input settings. Missing scientific or lowering
contracts remain unknown; documented incompatible choices remain unsupported.
Molecular state, geometry provenance, basis dimensions, and exact formulas still
have their own mandatory checks.

`OptionCondition` restricts a source contract to explicit option values, such as
`SCF_TYPE=PK` or `MP2_TYPE=CONV` with `QC_MODULE=OCC`. Conditions match the settings
that construction emits, including unit conversion for DDX screening. A missing
condition remains unknown. String comparison can ignore case; integers and
booleans retain distinct types. Ambiguous overlapping method cases are rejected.

`OptionCapability` records literal types, enumerated choices, and numerical
bounds. Additional numerical options require method-specific input evidence.
These checks concern the requested input, rather than an installed option table.

Named product evidence remains separate from method evidence. A frequency call's
primary energy does not imply that a requested spectrum, tensor, or thermal
quantity was declared. Query products independently to keep discovery compact.

## Use bundled source evidence

The shared catalogue `psi4` retains per-entry source references and optional
historical reference observations. It contains 382 method cases and 1657 named
product cases for HF/SCF, conventional MP2, legacy SAPT, DDX, PCMSolver, and TD-SCF
energy input contracts. Recorded compilation limits do not restrict planning.

Five orbital bases cover H–Ar with pure/Cartesian dimensions. Explicit D/T/Q
family memberships support [basis-limit contracts](formal-extrapolation.md).
SAPT retains explicit fitting-role pairings and monomer/induction choices;
see [SAPT contracts](formal-sapt.md). DDX keeps typed equation, dielectric,
cavity, and screening choices; see [solvent contracts](formal-solvation.md).
The reference build's missing pyddx does not prevent DDX construction.

Inspect the retained [source review](../src/psi4_parser/formal/catalogs/psi4/README.md).
Source/probe records differ from caller declarations, which remain explicit
assumptions. A bundled catalogue is finite and does not exhaust research
protocols. Broader scientific contracts and lowering remain on the roadmap.

## Maintain rules and their evidence

Extend method/driver/reference cases, option domains, basis facts, and product
contracts as needed. Give each addition its own documentation, source, or
separately collected evidence IDs. The loader checks packaged evidence hashes
individually; it does not require all entries to share one revision or audit.
Scientific rules are reusable across releases. Review affected entries when a
known behavior changes instead of producing catalogues for every existing version.

`combine_catalogs(base, contribution, ...)` composes independently sourced
contracts. Identical records are deduplicated; conflicting identities, keys,
and overlapping method cases are rejected. The response contribution provides
an example: its source facts join the shared catalogue without inspecting or
re-auditing any binary. Caller declarations retain their assumption status.

The optional reference collector reproduces the retained historical contribution:

```sh
uv run python -m psi4_parser.maintenance.capabilities \
  --engine-python /path/to/reference-psi4-python --destination new-capability-audit
```

This developer tool fingerprints reviewed source and basis files, records
metadata, and calls reviewed route selectors with `probe=True`. It executes no
chemistry drivers. Its source-identity checks prevent mislabelling evidence and
are not invoked by planning or verification. Neither this collector nor access
to any Psi4 binary is a prerequisite for building jobs. It is not a required
maintenance step for a new Psi4 release.
