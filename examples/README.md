# Psi4 builder examples

Each directory contains `build.py`, its rendered `input.dat`, and recorded Psi4
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

## Rebuild and run

From an example directory:

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
