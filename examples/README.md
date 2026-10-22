# Psi4 builder examples

Examples 01–21 contain `build.py`, its rendered `input.dat`, and recorded Psi4
`1.12a1.dev43` output. Examples 01–15 and 17–21 completed successfully.
Example 16 rendered successfully, but its calculation requires the `pcmsolver`
module missing from the recorded environment.

| Example                                                                  | Demonstrates                                                                            |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| [01: peroxide](01-peroxide-constrained-opt/build.py)                     | SCF/cc-pVDZ optimization with a frozen dihedral.                                        |
| [02: water](02-water-energy-gradient-properties/build.py)                | C2v symmetry, basis assignment, energy, gradient, and dipole properties.                |
| [03: hydrogen](03-hydrogen-zmatrix-opt-frequency/build.py)               | Z-matrix conversion, parameter editing, optimization, and frequencies.                  |
| [04: fragments](04-fragment-energy/build.py)                             | Two H2 singlet fragments with an explicit overall state.                                |
| [05: isotope and ghost](05-isotope-ghost-open-shell/build.py)            | Isotope mass, a ghost basis center, and doublet UHF.                                    |
| [06: point charges](06-external-point-charges/build.py)                  | External point charges passed to a calculation.                                         |
| [07: dihedral sweep](07-dihedral-pes/build.py)                           | Five constrained peroxide optimizations from 30° to 150°.                               |
| [08: bounds](08-bounded-constraints/build.py)                            | Distance bounds in bohr and angle bounds in radians.                                    |
| [09: atom order and dummy](09-reordering-and-dummy/build.py)             | Reordering, automatic dummy insertion, and a constraint using stable IDs.               |
| [10: coordinate conversion](10-nonplanar-coordinate-conversion/build.py) | Named distance/torsion edits in Z-matrix and Cartesian forms.                           |
| [11: bonded groups](11-bonded-group-manipulation/build.py)               | SDF import, bond-based selection, internal-coordinate edits, rotation, and translation. |
| [12: symmetry relaxation](12-symmetry-relaxation/build.py)               | Automatic C2v-to-Cs relaxation and an explicit C1 request.                              |
| [13: constraint isolation](13-constraint-isolation/build.py)             | Constrained and then unconstrained optimization of one molecule.                        |
| [14: embedded basis](14-embedded-basis/build.py)                         | Catalog and embedded STO-3G basis data.                                                 |
| [15: result references](15-wavefunction-references/build.py)             | Tuple assignment, wavefunction properties, and MP2 reuse of an SCF wavefunction.        |
| [16: PCM solvation](16-pcm-solvation/build.py)                           | Gas-phase and water-PCM energies; requires PCMSolver.                                   |
| [17: external potentials](17-modern-external-potentials/build.py)        | Point, Gaussian, and matrix potentials with explicit units.                             |
| [18: fragment fields](18-fragment-external-potentials/build.py)          | FI-SAPT0/cc-pVDZ with separate fragment point charges and retained F-SAPT files.        |
| [19: nested sweeps](19-nested-method-basis-sweep/build.py)               | Basis/method loops and conditional SCF/MP2 calculations.                                |
| [20: while and with](20-while-context-manager/build.py)                  | A basis sweep in a file context manager, writing `energies.csv`.                        |
| [21: exception handling](21-exception-handling/build.py)                 | Failed and successful SCF attempts, result handling, cleanup, and option restoration.   |

Examples [22](22-formal-geometry/build.py) and
[23](23-formal-composite/build.py) use the separate formal constructor. They
retain plan and proof JSON, rejected variants, and Psi4 output. These small
examples illustrate verification; their methods are not research recommendations.
Saved calculation outputs are development runs. Rebuilding updates construction
artifacts; execute separately to refresh output for a changed input.

## Checked scientific plans

Examples 24–41 use the independent-request API; their scripts end at construction.
They contain scripts, readable guides, and [saved bundles](24-formal-planning/saved/bundle/manifest.json)
with requests, plans, capability snapshots, verification reports, symbolic
recipes, and native inputs. Separate development checks execute the generated
inputs without adding execution to the builder. The latest check rebuilt all
41 examples and executed all 42 generated inputs: 39 completed, while examples
16 and 38 require the missing PCMSolver module and example 37 requires pyddx.
The stored-molecule example uses HF/MP2 with STO-3G and cc-pVDZ for a runnable
input-reuse demonstration.

| Example | Demonstrates |
| --- | --- |
| [24: request and selection](24-formal-planning/README.md) | Independent optimization/frequency/gradient goals, permitted SCF algorithms, common models, missing evidence, and a search bound. |
| [25: counterpoise study](25-formal-counterpoise-study/README.md) | Two constrained optimization histories, future geometries, real/ghost fragments, exact interaction formulas, and rejection of omitted work. |
| [26: rational expressions](26-formal-rational-expression/README.md) | Exact one-third/two-thirds coefficients, symbolic export, and rejection of an unjustified Gibbs-energy label. |
| [27: closed reaction](27-formal-reaction/README.md) | Independent species choices, real-nucleus and charge conservation, species-specific RHF/UHF references, and rejection of internally consistent but unbalanced work. |
| [28: agent interface](28-formal-agent-interface/README.md) | Compact CLI discovery, planning, paged explanations, reusable records, independent export, and measured response sizes. |
| [29: audited capabilities](29-formal-audited-capabilities/README.md) | Shared source-audited contracts, conditional derivative cases, explicitly permitted fallback, missing algorithm settings, and optimizer requirements. |
| [30: coordinate scan](30-formal-coordinate-scan/README.md) | Independent input and future-coordinate targets, explicit tolerances, and rejection of a wrongly prepared point or unconstrained future coordinate. |
| [31: products and thermochemistry](31-formal-products-and-thermochemistry/README.md) | Named complex spectra, native tensor frames, explicit RRHO conditions, property products, preserved native records, and a hybrid Gibbs estimate. |
| [32: thermal reaction](32-formal-thermal-reaction/README.md) | Native and hybrid Gibbs reactions after optimization, shared thermal state, species-specific symmetry, separate correction treatments, and rejection of mixed temperatures. |
| [33: option isolation](33-formal-option-isolation/README.md) | Independent native option baselines, state restoration, explicit MP2 routing, and a structured export policy. |
| [34: calculation reuse](34-formal-calculation-reuse/README.md) | Explicit sharing permissions, shared future geometries and products, separate calls, and goal-to-step mappings. |
| [35: basis extrapolation](35-formal-basis-extrapolation/README.md) | Independently declared DT/TQ correction models, basis-family evidence, exact weights, shared TZ calls, and symbolic estimates. |
| [36: SAPT](36-formal-sapt/README.md) | Monomer partitions, dimer/monomer basis choices, fitted-basis roles, named components, and comparison with counterpoise HF. |
| [37: continuum solvation](37-formal-solvation/README.md) | Explicit PCM/COSMO/LPB choices, screening units, cavity and component evidence, and checked electronic shifts at a common geometry. |
| [38: PCMSolver planning](38-formal-pcmsolver/README.md) | Named or explicit equilibrium media, IEFPCM/CPCM and GePol choices, scoped solver input, and checked electronic solvation shifts. |
| [39: excited-state planning](39-formal-excited-states/README.md) | TD-SCF root/spin/equation intent, ground-reference returns, ordered products, and exact native total/excitation proofs. |
| [40: stored molecules](40-formal-stored-molecules/README.md) | One molecular upload, handle-based templates, complete independent requests, self-contained export, and measured upload sizes. |
| [41: exponential reference limits](41-formal-exponential-extrapolation/README.md) | Two exponential decay laws, certified rational weight bounds, correlation-limit composition, and permitted HF reuse. |

The shared [demonstration catalog](formal-demo-capabilities.json) contains
**synthetic caller declarations**.
It teaches capability matching and conditional proofs; it is not evidence for
any installed Psi4 build. In particular, its PK-only option contract does not
claim that Psi4 lacks DF support. For actual work, supply independently
reviewed scientific/input contracts. Example 29 uses a bundled source-audited
snapshot, whose method scope is described in
[capability evidence](../docs/formal-capabilities.md).
STO-3G examples are API illustrations,
not recommended research protocols.

Run from the repository root and choose a destination that does not exist:

```sh
uv run python examples/24-formal-planning/build.py --destination /tmp/psi4-example-24
uv run python examples/25-formal-counterpoise-study/build.py --destination /tmp/psi4-example-25
uv run python examples/26-formal-rational-expression/build.py --destination /tmp/psi4-example-26
uv run python examples/27-formal-reaction/build.py --destination /tmp/psi4-example-27
uv run python examples/28-formal-agent-interface/build.py --destination /tmp/psi4-example-28
uv run python examples/29-formal-audited-capabilities/build.py --destination /tmp/psi4-example-29
uv run python examples/30-formal-coordinate-scan/build.py --destination /tmp/psi4-example-30
uv run python examples/31-formal-products-and-thermochemistry/build.py --destination /tmp/psi4-example-31
uv run python examples/32-formal-thermal-reaction/build.py --destination /tmp/psi4-example-32
uv run python examples/33-formal-option-isolation/build.py --destination /tmp/psi4-example-33
uv run python examples/34-formal-calculation-reuse/build.py --destination /tmp/psi4-example-34
uv run python examples/35-formal-basis-extrapolation/build.py --destination /tmp/psi4-example-35
uv run python examples/36-formal-sapt/build.py --destination /tmp/psi4-example-36
uv run python examples/37-formal-solvation/build.py --destination /tmp/psi4-example-37
uv run python examples/38-formal-pcmsolver/build.py --destination /tmp/psi4-example-38
uv run python examples/39-formal-excited-states/build.py --destination /tmp/psi4-example-39
uv run python examples/40-formal-stored-molecules/build.py --destination /tmp/psi4-example-40
uv run python examples/41-formal-exponential-extrapolation/build.py --destination /tmp/psi4-example-41
```

For examples 24–28, add `--capabilities /path/to/reviewed-catalog.json` to use another catalog. The
diagnostic outcomes shown in the guides describe the default demonstration
catalog; different evidence may change selection and acceptance. Export never
overwrites an existing directory. Save a durable destination for work you need
to retain. See [scientific planning](../docs/scientific-planning.md) for guarantees
and currently unsupported contracts.

## Rebuild and run

For examples 01–23, from an example directory:

```sh
uv run python build.py
mkdir -p scratch
psi4 -i input.dat -o output.dat -n 1 --memory 512MiB -s scratch -v > console.log 2>&1
```

Install Psi4 separately. Rebuilding replaces `input.dat`; rerunning replaces the
calculation output. Remove scratch files after use and keep them out of version
control. The retained collection includes calculation outputs and F-SAPT data;
scratch files are omitted.

`output.dat` contains the calculation output and preprocessed Python.
`build.log`, `console.log`, and `output.log` retain the other logs.
`build.py` constructs and writes the input; separate checks are recorded in
[verification.log](verification.log).

## Details worth inspecting

The dihedral sweep starts every point from the original peroxide geometry.
`set_dihedral()` sets 30°, 60°, 90°, 120°, or 150°;
`freeze(dihedral(...))` holds that value during optimization. Result names are
`e_30`, `e_60`, `e_90`, `e_120`, and `e_150`.

Recorded numerical checks include a bounded H–H distance of 0.952518979206 Å
(1.8 bohr), a water angle of 90°, and an unconstrained peroxide torsion of
115.083185288° after its temporary 150° constraint was removed. Example 12's
warning records the intended adoption of Cs after an edit breaks C2v symmetry.
Example 16's [console log](16-pcm-solvation/console.log) records the missing
PCMSolver dependency.

Examples 19–21 place control flow in the generated input, so those loops and
branches run in Psi4. In example 19, both branches assign `e_result`, making it
available afterward. The sweep clears integral scratch data before changing
basis after MP2. Its separate [diagnose.py](19-nested-method-basis-sweep/diagnose.py)
shows rejection of a name assigned only inside a possibly empty loop:

```sh
uv run python examples/19-nested-method-basis-sweep/diagnose.py
```

Run that command from the repository root. Its expected diagnostic is retained
in [diagnose.log](19-nested-method-basis-sweep/diagnose.log).
Example 20 retains its computed [energies.csv](20-while-context-manager/energies.csv).
Example 21 catches a one-iteration convergence failure, then permits 50 iterations;
its output records `SCF MAXITER` restored to 37 after both attempts.
