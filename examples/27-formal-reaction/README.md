# Construct a closed electronic-energy reaction

[build.py](build.py) expands `H2 -> 2 H` into two species calculations and an
exact product-minus-reactant energy expression. The singlet molecule uses RHF;
the doublet atom uses UHF. The independent request fixes both choices.
`reaction_expansion()` works from supplied species and coefficients rather than
requiring a named protocol.

From the repository root, choose a new output directory:

```sh
uv run python examples/27-formal-reaction/build.py --destination /tmp/psi4-reaction-demo
```

The shared [catalog](../formal-demo-capabilities.json) contains synthetic teaching
declarations. For actual work, supply independently reviewed scientific/input
contracts with `--capabilities PATH`.
SCF/STO-3G here illustrates the API and is not a recommended dissociation protocol.

Inspect the [request](saved/request.json), [summary](saved/summary.json), and
[manifest](saved/bundle/manifest.json). Verification checks exact real-nucleus
and charge conservation and balances every computational treatment, allowing
the explicitly selected species-specific SCF references. Isotope labels and
explicit mass choices are retained; unspecified defaults are kept distinct.
Ghost centers and dummy atoms are not counted as real nuclei. Exact rational
coefficients and nested composite electronic energies use the same checks.

The [rejected request](saved/unbalanced-request.json) instead asks for `H2 -> H`.
Its proposed algebra agrees exactly with that request, but
[verification rejects it](saved/unbalanced-proposal.json) because one real
hydrogen nucleus is missing. Algebraic consistency alone cannot supply the
scientific contract.

This example describes closed electronic-energy reactions. See
[example 32](../32-formal-thermal-reaction/README.md) for native and hybrid thermal
reaction contracts. External particle reservoirs and reaction pathways need more
contracts. The native input contains only species calculations. The reaction
expression stays symbolic for a separate consumer; no calculations or output
validation run in this example. Bundle hashes cover its payloads; sibling
teaching records are outside the manifest. Rebuilding requires a new destination.
