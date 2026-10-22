# Compare continuum equations at one geometry

[build.py](build.py) constructs a vacuum HF energy and PCM, COSMO, and screened
LPB energies at the same H2 geometry. It requires three independently checked
electronic solvation shifts and a symbolic PCM/COSMO comparison: eight goals and
four top-level calls.

```sh
uv run python examples/37-formal-solvation/build.py \
  --destination /tmp/psi4-solvent-construction
```

Choose a new destination. The default bundled catalog supplies reviewed source
contracts. Its version/build labels do not constrain the execution host, and its
reference installation's missing pyddx does not block planning. Optional
`--capabilities PATH` selects another input-contract catalog. The included
[demonstration catalog](capabilities-demonstration.json) contains explicit teaching
declarations and can be selected the same way. The molecule, basis, dielectric, screening, and
numerical choices illustrate the API and do not define a research protocol.

The script constructs inputs without executing Psi4. Inspect its
[summary](saved/summary.json), [request](saved/bundle/scientific-request.json),
[manifest](saved/bundle/manifest.json), and [input](saved/bundle/inputs/workflow.dat).
LPB screening is specified in inverse bohr and converted to the molecular input
units. Each call uses its own declared option scope.

The [reference-catalog proposal](saved/reference-catalog-proposal.json) records
accepted construction independently of the reference installation's dependencies.
Reports and manifests state `runtime_policy="operator_managed"`. Installation,
compilation, and execution failures belong to the target operator.

The [wrong-weight request](saved/wrong-weight-request.json) doubles a solvent
energy consistently in its own algebra but is [rejected](saved/wrong-weight-proposal.json)
against the independent shift definition. The
[wrong-geometry request](saved/wrong-geometry-request.json) uses another input
declaration for the vacuum call and is [rejected](saved/wrong-geometry-proposal.json),
even though its coordinates match.

These are electronic shifts. Gibbs solvation, standard-state conversions,
non-electrostatic contributions, execution, and result parsing need separate work.
See [solvent contracts](../../docs/formal-solvation.md) for evidence, cavity
coverage, parameter domains, and remaining scope.
