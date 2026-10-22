# Compose a constrained counterpoise study

[build.py](build.py) prepares two H2 dimers with starting fragment separations
of 3 and 4 angstrom. Each case requires an optimization with the distance between
`A:a1` and `B:a1` frozen. A full-basis counterpoise expansion then uses that case's
future optimized geometry. The parent has a fixed center of mass and orientation
so subsystem atom order and frames remain explicit.

From the repository root, choose a new output directory:

```sh
uv run python examples/25-formal-counterpoise-study/build.py --destination /tmp/psi4-cp-demo
```

The default [capabilities](../formal-demo-capabilities.json) are synthetic teaching
declarations. Use `--capabilities PATH` for separately reviewed evidence for an
intended real build. The small SCF/STO-3G model illustrates composition.

`fragment_expansion()` supplies the subsystem goals, energy goals, interaction
formula, and common-model relations. `finite_study()` namespaces the complete
request into `r3` and `r4` cases; it does not require a catalogued protocol.
The [saved request](saved/request.json) contains 16 mandatory goals. Each case
has one optimization and three energy calculations, including the parent and
both monomers in the complete parent basis.
Each case also independently requires its selected distance on the input and
future optimized geometry. Coordinate checks measure the input and use the
matching frozen constraint to establish the future-coordinate contract.

Inspect the [summary](saved/summary.json),
[manifest](saved/bundle/manifest.json), and
[native input](saved/bundle/inputs/workflow.dat). Each interaction recipe is
`E_AB^(AB) - E_A^(AB) - E_B^(AB)`. Non-real fragments retain ghost basis centers.
The manifest records eight future geometries across the two cases, without
pretending their coordinates are known. Expressions remain symbolic for a
separate result consumer.

[omitted-goal.json](saved/omitted-goal.json) shows that a plan which omits the final
requested expression is `violated`, even when its own assertion is trivially
consistent. Independent request coverage supplies the missing obligation.

Verification checks the declared geometries, constraints, common models,
subsystems, formula, and independent scan-coordinate requirements. Future
coordinate bounds are conditional on successful optimizer enforcement; measured
inputs use the stated tolerances. It does not prove the numerical optimization
outcome. Execution and result parsing remain
separate. The bundle lists its payloads; sibling teaching files are outside the
manifest. Rebuilding requires an unused destination.
