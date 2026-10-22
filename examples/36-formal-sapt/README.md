# Construct SAPT and counterpoise comparisons

[build.py](build.py) prepares two H2 fragments at one geometry and requires:

- Dimer-centered SAPT0 with all four components and the total interaction.
- Monomer-centered SAPT0 with the same declared orbital model.
- A full-basis counterpoise HF interaction.
- Symbolic comparisons of the basis treatments and interaction methods.

```sh
uv run python examples/36-formal-sapt/build.py \
  --destination /tmp/psi4-sapt-construction
```

Choose a new destination. The script constructs inputs without executing Psi4.
It defaults to the shared source-audited catalogue, or accepts independently
reviewed contracts with `--capabilities PATH`. The molecule and models illustrate
construction and do not establish research accuracy.

Inspect the [summary](saved/summary.json),
[request](saved/bundle/scientific-request.json), and
[manifest](saved/bundle/manifest.json). Seventeen mandatory goals use five
top-level calls. The request independently requires the native component
partition, and the verifier proves its relation to the SAPT return.

The manifest declares five transient native QCVariable locations. Collection
and parsing belong to a separate consumer. Export adds no component snapshots
or output-reading code, and this example has no declared native product files.
A later application call can replace those native variables. Scalar return
values retain their ordinary native-input bindings.

The [wrong-partition request](saved/wrong-partition-request.json) reverses the
logical A/B roles and is [rejected](saved/wrong-partition-proposal.json). The
[wrong-sum request](saved/wrong-sum-request.json) doubles a component consistently
in its own algebra but is [rejected](saved/wrong-sum-proposal.json) against the
independent component definition.

The [input](saved/bundle/inputs/workflow.dat) carries explicit basis-center and
induction choices. Its native option scope also restores the call's entry
scratch namespace; it does not undo preceding molecule-declaration effects.
See [SAPT contracts](../../docs/formal-sapt.md) for open-shell states, midbond
centers, fitting evidence, transient products, and remaining scope.
