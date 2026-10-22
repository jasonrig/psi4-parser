---
name: plan-calculations
description: Use when translating a scientific objective into Psi4 calculations, checking a proposed calculation plan against its requirements, or exporting formally checked inputs. Covers composable workflows rather than a fixed list of protocols.
---

# Build checked Psi4 calculation plans

Use `psi4_parser.formal` to turn a scientific objective into an independently
specified request, a checked plan, and exported Psi4 input. Checks establish
encoded construction requirements under stated assumptions. Scientific model
suitability, convergence, and numerical accuracy require separate judgment.
Requirements omitted from the request remain unchecked. Execution and result
parsing are separate tasks.

Use the shared [interface guidance](../../references/python.md#choose-how-to-author-the-input)
to decide when handwritten input, editable input records, or the builder better
fits the task, and how those approaches combine with formal planning.

## Default workflow

1. Follow [runtime and discovery](../../references/runtime.md): check uv caching,
   fetch and verify the latest code, and explain setup and execution only through
   uv/uvx. Discover the verified runtime's exports, signatures, relevant model fields,
   and command or tool help before coding. Use Python to compose new requests;
   prefer compact CLI/MCP operations for saved work. Read the
   [construction and repair example](../../references/formal-start.md) when you
   need an introduction to request composition or diagnosis. Examples illustrate
   usage; current API descriptions and schemas define accepted arguments.
2. Encode the scientific objective independently of any proposed implementation.
   Preserve molecular units and states, geometry dependencies, allowed model
   choices, required products, formulas, and other scientific relationships.
   Choose the scientific model using sources and task context; make consequential
   assumptions explicit and resolve ambiguities that change the goal. Save the
   request before proposing a plan. A calculation's primary return does not
   imply that every secondary product has been requested.
3. Propose a plan using the default shared scientific/input catalogue. Discover
   only the relevant operation contracts, model fields, and method/product
   conditions through [targeted discovery](../../references/formal.md#discover-the-selected-runtime).
   Missing evidence stays unknown; caller declarations remain assumptions.
   Target binaries, dependencies, and versions are operator-managed: do not
   inspect them, gate construction on them, or emit deployment warnings.
4. Verify against the saved independent request. Relationship-only verification
   cannot establish completeness. Inspect compact status, goal coverage,
   assumptions, diagnostics, and failed proof obligations. Follow the
   [acceptance and recovery contract](../../references/formal.md#propose-diagnose-and-export)
   for precise status fields and next actions. Repair the implementation without
   weakening requirements, inventing evidence, granting reuse, or adding
   fallbacks merely to pass. Report a missing scientific decision or evidence
   when it prevents progress; do not repeat unchanged calls.
5. Export after complete acceptance of the independent request. The export
   operation reverifies and saves a new construction bundle. Report its location,
   generated input, selected models, coverage, and consequential assumptions.
   Preserve the complete bundle for the separate execution/result consumer;
   copy temporary MCP artifacts to durable storage before shutdown.

## Read only what the task needs

Use the same request/verify/export workflow for new combinations of supported
operations; do not look for a named protocol first. Read the relevant section of
[task-specific guidance](../../references/formal.md):

| Task | Section |
| --- | --- |
| Saved JSON, compact tools, handles | [CLI and MCP](../../references/formal.md#use-compact-planning-interfaces) |
| Repeated molecules or permitted shared calls | [Stored inputs and reuse](../../references/formal.md#stored-molecules-and-call-reuse) |
| Counterpoise, many-body work, scans, finite cases | [Studies and fragments](../../references/formal.md#finite-studies-fragments-and-coordinate-scans) |
| Electronic or thermal reactions | [Reaction composition](../../references/formal.md#reaction-composition) |
| Basis extrapolation and coefficient certificates | [Basis limits](../../references/formal.md#basis-extrapolation) |
| SAPT components and monomers | [SAPT](../../references/formal.md#sapt) |
| DDX/PCMSolver and solvent shifts | [Solvation](../../references/formal.md#implicit-solvation) |
| Excitations and transition products | [Excited response](../../references/formal.md#excited-response) |
| Spectra, thermochemistry, native product bindings | [Products](../../references/formal.md#named-products-and-thermochemistry) |
| Missing catalogue coverage or scientific extensions | [Evidence](../../references/formal.md#capability-evidence) |
