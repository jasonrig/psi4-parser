# Construct native and hybrid Gibbs reactions

[build.py](build.py) requests `CO + 1/2 O2 -> CO2` at 298.15 K and 101325 Pa.
It first requires separate HF optimizations, then constructs two independent
reaction plans from the optimized geometries:

- **Native:** one HF frequency call per species supplies its native Gibbs total.
- **Hybrid:** an MP2 single point supplies electronic energy and an HF frequency
  call supplies the specified Gibbs correction at the same species geometry.

CO and CO2 use RHF; triplet O2 uses UHF. Rotational symmetry numbers are 1 for CO
and 2 for O2 and CO2. They are explicit species inputs, rather than a single
reaction-wide symmetry setting. STO-3G and these electronic models illustrate
construction and are not a recommended research protocol or an accuracy claim.

From the repository root, choose a new directory:

```sh
uv run python examples/32-formal-thermal-reaction/build.py \
  --destination /tmp/psi4-thermal-reaction
```

Use `--capabilities PATH` for other independently reviewed evidence. The default
is the shared source-audited catalogue described in [example 29](../29-formal-audited-capabilities/README.md).
The script executes no quantum chemistry application.

Inspect the [summary](saved/summary.json), [native request](saved/native/scientific-request.json),
and [hybrid manifest](saved/hybrid/manifest.json). The native plan has six
calculations, including its three optimizations. The hybrid plan adds only
the three electronic single points. Both retain three distinct native
vibrational output bindings and a symbolic reaction expression for a separate
execution/result consumer.

Verification checks nuclei, isotope/mass choices, charge, and every electronic
and correction treatment independently. Temperature, pressure, thermal treatment,
and projection choices must agree across species. Each corrected molecular energy
must retain its own geometry and electronic state.

The [mixed-temperature request](saved/mixed-temperature-request.json) instead
sets CO2 to 400 K. Its species formulas and stoichiometry remain self-consistent,
but the [proposal](saved/mixed-temperature-proposal.json) is rejected because
there is no common reaction thermal state.

See [thermal reaction contracts](../../docs/formal-reactions.md) for quantities,
hybrid models, composability, and scope. Execution, reaction pathways, external
particle reservoirs, and result parsing remain separate.
