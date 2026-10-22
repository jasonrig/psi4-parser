# Check the intended scan coordinates

[build.py](build.py) prepares water geometries with O–H distances of 0.9 and
1.1 angstrom, then requires a constrained optimization for each point.
`StudyCase.relations` contains independent `CoordinateValue` requirements for
both the prepared input and the future optimized geometry.

The verifier measures each input, checks its requested distance, and propagates
the matching frozen-coordinate contract through the optimization. The two
cases retain independent histories. It does not measure an uncomputed geometry.

From the repository root, choose a new directory:

```sh
uv run python examples/30-formal-coordinate-scan/build.py \
  --destination /tmp/psi4-coordinate-scan
```

The [saved summary](saved/summary.json) records four coordinate checks:

- The declared two-point study is `constructed`.
- Preparing both geometries at 0.9 angstrom leaves the second point wrong and
  produces `no_candidate`; see [wrong-point.json](saved/wrong-point.json).
  Its ordinary goal coverage and input identities are internally consistent.
  The independent coordinate requirement supplies the counterexample.
- Removing the frozen constraint leaves the future coordinate unknown; see
  [unconstrained.json](saved/unconstrained.json). The framework does not assume
  that optimization retains the starting bond length.

Inspect the [request](saved/request.json),
[verification](saved/bundle/verification.json),
[manifest](saved/bundle/manifest.json), and
[native input](saved/bundle/inputs/workflow.dat). The manifest retains the
coordinate assumptions, while the saved request retains the required values.
There are no generated numerical result-acceptance checks.

This example uses the shared source-audited contracts described in
[example 29](../29-formal-audited-capabilities/README.md). It does not detect an
installed engine. Its small water calculation illustrates the API rather than
recommending a research protocol. No calculation was run for these artifacts.
See [coordinate contracts](../../docs/formal-coordinates.md) for units, signed
angles, frames, ranges, numerical tolerances, and future-geometry boundaries.
