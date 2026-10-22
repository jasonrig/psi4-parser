# Construct two basis-limit correction estimates

[build.py](build.py) requests MP2 minus HF corrections with cc-pVDZ, cc-pVTZ,
and cc-pVQZ at one H2 geometry. It explicitly chooses inverse-cube extrapolation
for both D/T and T/Q pairs, adds the T/Q correction to the finite-QZ HF energy,
and preserves a symbolic comparison of the two corrections.

```sh
uv run python examples/35-formal-basis-extrapolation/build.py \
  --destination /tmp/psi4-basis-extrapolation
```

Choose a new destination. The script constructs inputs without executing Psi4.
It defaults to the bundled shared contract catalogue, or accepts separately reviewed
evidence with `--capabilities PATH`. The molecule, model, and exponent illustrate
construction; they do not establish a recommended research protocol.

Inspect the [summary](saved/summary.json),
[request](saved/bundle/scientific-request.json), and
[manifest](saved/bundle/manifest.json). Sixteen mandatory goals use six native
calls. Explicit reuse permission shares the two T-basis calculations between
the DT and TQ purposes. Both extrapolation recipes and all goal mappings remain
in the manifest for a separate execution/result consumer.

The basis catalog supplies family/cardinal evidence independently from the
request. The [wrong-family request](saved/wrong-family-request.json) assigns an
augmented family to ordinary cc-pVXZ calculations and is
[rejected](saved/wrong-family-proposal.json). The
[wrong-weight request](saved/wrong-weights-request.json) supplies a self-consistent
linear formula that disagrees with its chosen inverse-cube model and is also
[rejected](saved/wrong-weights-proposal.json).

The [contract guide](../../docs/formal-extrapolation.md) covers model matching,
fitting bases, geometry provenance, exact weights, composition, and scope.
Asymptotic convergence, exponent suitability, and numerical accuracy remain
scientific assumptions. Execution and result parsing remain separate.
