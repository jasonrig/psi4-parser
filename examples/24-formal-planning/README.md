# Plan optimization, frequencies, and a gradient

[build.py](build.py) saves an independent request before asking the planner to
implement it. The request permits two SCF algorithms in preference order and
requires the same complete model for all three calculations. Both later
calculations must consume the optimization's future geometry.

With the [demonstration catalog](../formal-demo-capabilities.json), the first
candidate uses DF and falls outside the snapshot's PK-only contract. The next
accepted candidate uses PK for every goal. These are explicitly permitted
choices in this example; an agent must not invent scientific fallbacks.

From the repository root, choose a new output directory:

```sh
uv run python examples/24-formal-planning/build.py --destination /tmp/psi4-plan-demo
```

The optional `--capabilities PATH` loads a different catalog. The default is
synthetic teaching evidence, rather than a catalog for an installed Psi4 build.
Proofs remain conditional on those declarations and the report's assumptions.

Inspect the retained [summary](saved/summary.json),
[independent request](saved/request.json),
[verification](saved/bundle/verification.json), and
[native input](saved/bundle/inputs/workflow.dat). The gradient product has shape
`(atoms, 3)`, units hartree/bohr, and the optimized geometry's frame. The frequency
driver's primary product is currently electronic energy; separate frequencies
and thermal quantities are not yet represented in the manifest.

Two additional files illustrate failures without launching Psi4:

- [missing-evidence.json](saved/missing-evidence.json): the same plan is `unknown`
  after capability entries are removed. Valid relationships cannot fill that gap.
- [bounded-search.json](saved/bounded-search.json): a one-candidate budget is
  `exhausted` under the default catalog. This does not prove impossibility.

The script creates a fresh destination. Its `bundle/manifest.json` lists the
exported payloads; the sibling request, summary, and diagnostic files are teaching
artifacts outside that manifest. No execution or numerical output validation is
part of this example.
