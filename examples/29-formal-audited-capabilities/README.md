# Plan with source-audited capability cases

This construction-only example uses the bundled `psi4`
source-contract snapshot. Loading the snapshot does
not import, detect, or launch Psi4. The scientific choices illustrate the API;
they are not a recommended water protocol.

The request requires HF/cc-pVDZ optimization and analytic frequencies, then
frozen-core conventional MP2 energy and gradient on the resulting geometry.
It explicitly sets `SCF_TYPE=PK`, `MP2_TYPE=CONV`, and `QC_MODULE=OCC` where
needed. The gradient permits analytic or automatic derivatives in that order.

The [saved summary](saved/summary.json) records:

- `constructed` after two candidate checks: the frozen-core MP2 analytic route
  is unsupported under the inspected conditions; the permitted automatic route
  is accepted. The engine selects its derivative implementation at execution.
- `no_candidate` for the [analytic-only variant](saved/analytic-only.json).
- `unknown` when [SCF_TYPE is omitted](saved/missing-algorithm.json), because
  the reviewed PK case cannot establish support for an unspecified algorithm.
- Unpinned component names in verification and the
  [bundle manifest](saved/bundle/manifest.json), with
  `runtime_policy="operator_managed"`. Dependencies and versions generate no
  checks or warnings; the operator resolves installation and execution failures.

From the repository root, choose a destination that does not exist:

```sh
uv run python examples/29-formal-audited-capabilities/build.py \
  --destination /tmp/psi4-example-29
uv run psi4-parser formal catalogs
uv run psi4-parser formal --workspace planning-artifacts \
  load-catalog psi4
```

Use the returned capability handle with `formal capabilities` to inspect
method conditions and components, then with `formal propose` or `formal verify`.
For MCP, use `formal_catalogs` followed by
`formal_load(kind="capabilities", catalog="psi4")`.
Choose contracts for the requested scientific and input choices; the target
binary does not need to match the reference build.

The snapshot covers a finite set of HF/SCF and MP2 cases, five orbital bases,
and elements H–Ar. Missing entries or unmatched conditions stay unknown.
Read [capability evidence](../../docs/formal-capabilities.md) for collection,
source review, limitations, and the retained audit. No calculations were run
to produce these construction artifacts. Frequency results, convergence,
accuracy, and interpretation belong to separate execution and analysis work.
