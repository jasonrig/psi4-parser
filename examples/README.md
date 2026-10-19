# Psi4 builder examples

Each example contains a minimal `build.py`, its rendered `input.dat`, and the
recorded output from running that input with Psi4 `1.12a1.dev43`.
Examples 01–15 completed successfully. Example 16 renders successfully; its
recorded run could not execute because that Psi4 environment lacked the
`pcmsolver` module.

| Example                                                                 | Job                                                                                                                        |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| [01: peroxide](01-peroxide-constrained-opt/build.py)                    | The supplied SCF/cc-pVDZ optimization with a frozen dihedral.                                                              |
| [02: water](02-water-energy-gradient-properties/build.py)               | C2v symmetry, native basis assignment, energy, gradient, and dipole properties.                                            |
| [03: hydrogen](03-hydrogen-zmatrix-opt-frequency/build.py)              | Cartesian-to-Z-matrix conversion, parameter editing, optimization, and frequency.                                          |
| [04: fragments](04-fragment-energy/build.py)                            | Two explicit singlet H2 fragments and a single-point energy.                                                               |
| [05: isotope and ghost](05-isotope-ghost-open-shell/build.py)           | Explicit isotope mass, ghost basis center, and doublet UHF energy.                                                         |
| [06: point charges](06-external-point-charges/build.py)                 | An energy calculation with external point-charge arguments.                                                                |
| [07: dihedral PES](07-dihedral-pes/build.py)                            | Five constrained peroxide optimizations at 30°, 60°, 90°, 120°, and 150°, using `set_dihedral` for each starting geometry. |
| [08: bounded constraints](08-bounded-constraints/build.py)              | Bond-length bounds supplied in bohr and angle bounds supplied in radians, with optima outside the permitted ranges.        |
| [09: atom order and dummy](09-reordering-and-dummy/build.py)            | Reordered acetylene, automatic Z-matrix dummy insertion, and a frozen C-C bond addressed by stable IDs.                    |
| [10: nonplanar conversion](10-nonplanar-coordinate-conversion/build.py) | Peroxide with named distance/torsion parameter edits, evaluated as both a Z-matrix and Cartesian geometry.                 |
| [11: bonded groups](11-bonded-group-manipulation/build.py)              | Methanol SDF import, connected OH selection, distance/angle edits, rotation, and translation.                              |
| [12: symmetry relaxation](12-symmetry-relaxation/build.py)              | Automatic C2v-to-Cs relaxation after a bond edit, compared with explicitly requested C1.                                   |
| [13: constraint isolation](13-constraint-isolation/build.py)            | Constrained and subsequently unconstrained optimizations of the same molecule.                                             |
| [14: embedded basis](14-embedded-basis/build.py)                        | Catalog STO-3G compared with the same hydrogen basis supplied through native embedded basis records.                       |
| [15: wavefunction references](15-wavefunction-references/build.py)      | Tuple assignment, OEProp through a structured reference, and MP2 reuse of the SCF wavefunction.                            |
| [16: PCM solvation](16-pcm-solvation/build.py)                          | Gas-phase and water-PCM energies; execution unavailable because Psi4 cannot import `pcmsolver`.                            |

The PES sweep starts every point from the original peroxide molecule. It uses
`set_dihedral` to change the coordinates and `freeze(dihedral(...))` to retain
the selected angle during optimization. Energies are assigned to `e_30`, `e_60`,
`e_90`, `e_120`, and `e_150` in the rendered input.

`output.dat` contains the full calculation output and preprocessed Python.
`console.log`, `output.log`, and `build.log` retain the other execution logs.

To rebuild and run an example from its directory:

```sh
uv run python build.py
mkdir -p scratch
psi4 -i input.dat -o output.dat -n 1 --memory 512MiB -s scratch -v > console.log 2>&1
```

Psi4 must be installed separately to run calculations. Re-running an example
replaces its recorded input and output files. Scratch files are ignored by Git.

The builder scripts only construct jobs, render them, and save `input.dat`.

Independent numerical checks for the new cases are recorded in
[verification.log](verification.log). They measure actual coordinates and
energies from Psi4's output; the builder scripts contain no verification code.
For example, the bounded H-H distance reached 0.952518979206 Å (1.8 bohr), the
bounded water angle reached 90°, and the unconstrained peroxide torsion moved
from 150° to 115.083185288° after its temporary constraint was removed.

The symmetry warning in example 12 is intentional: it confirms that the molecule
edit adopts Cs when the original C2v request no longer fits.

Example 16's dependency failure is retained in
[its console log](16-pcm-solvation/console.log). It has not been counted as a
successful calculation.
