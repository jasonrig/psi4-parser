# Plan products and a hybrid Gibbs estimate

[build.py](build.py) requires 16 scientific goals: HF optimization, a full
frequency calculation, named vibrational/thermal products, an MP2 single point,
a hybrid Gibbs expression, and six explicitly requested property products.
It uses the shared source-audited contracts from [example 29](../29-formal-audited-capabilities/README.md).
No quantum chemistry application is launched by this script.

The frequency analysis explicitly requests 298.15 K, 101325 Pa, rotational
symmetry number 2, and translation/rotation projection. Its electronic-energy
return stays separate from the spectrum, modes, Hessian, and Gibbs quantities.
The hybrid expression is MP2 electronic energy plus the HF RRHO Gibbs correction
on the same optimized geometry. These choices illustrate the API; they are not
a recommended research protocol or an accuracy claim.

From the repository root, choose a new directory:

```sh
uv run python examples/31-formal-products-and-thermochemistry/build.py \
  --destination /tmp/psi4-products
```

Use `--capabilities PATH` for other independently reviewed evidence. Inspect the
[summary](saved/summary.json), [independent request](saved/request.json), and
[construction manifest](saved/bundle/manifest.json). Eleven named products retain
their producing calculation, geometry, model, physical type, frame, and applicable
thermal conditions. The manifest declares a native vibrational record, including
its filename template and member encodings, for a separate result consumer.
Native inputs request that file; they do not parse or validate it.

[wrong-temperature.json](saved/wrong-temperature.json) changes the proposed
frequency calculation to 400 K while retaining the original independent request.
The proposal remains internally coherent but verification reports `violated`.
Other regression cases reject doubled corrections, wrong geometry provenance,
and missing product evidence.

For focused evidence discovery, load the catalog and request only a relevant page:

```sh
uv run psi4-parser formal --workspace planning-artifacts \
  load-catalog psi4
# Use the returned capability handle for CATALOG below.
uv run psi4-parser formal --workspace planning-artifacts capabilities CATALOG \
  --section products --name hf --driver frequency \
  --product gibbs_correction --limit 3
```

See [product contracts](../../docs/formal-products.md) for canonical layouts,
complex frequencies, thermal semantics, native record handling, and scope.
