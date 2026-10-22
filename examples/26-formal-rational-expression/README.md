# Preserve exact energy weights and quantity meaning

[build.py](build.py) requests two H2 electronic energies at explicit geometries
and the expression `E_short / 3 + 2 * E_long / 3`. The weights are illustrative
inputs, not Boltzmann populations or a thermochemical model. `Rational` preserves
the exact coefficients in the request, proof, and exported recipe.

From the repository root, choose a new output directory:

```sh
uv run python examples/26-formal-rational-expression/build.py --destination /tmp/psi4-rational-demo
```

The default [catalog](../formal-demo-capabilities.json) contains synthetic caller
declarations. For actual work, supply independently reviewed scientific/input
contracts with `--capabilities PATH`.

Inspect the [summary](saved/summary.json),
[request](saved/request.json), and
[manifest](saved/bundle/manifest.json). The native input contains only the two
energy calculations and their products. A separate consumer can use the
manifest's symbolic expression after execution and parsing elsewhere.

The script also proposes an electronic-energy expression relabelled as Gibbs
energy. [unsupported-meaning.json](saved/unsupported-meaning.json) records
`no_candidate` with an `unsupported` verification report: matching scalar units
and correct algebra cannot supply the missing thermochemical contract.

The manifest lists the bundle payloads. The sibling request, summary, and rejection record
are teaching artifacts outside that manifest. The example performs no
calculations and requires an unused output directory.
