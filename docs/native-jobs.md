# Read and construct Psi4 input

`psi4_parser.job` represents input as ordered molecule, settings, basis, and
other native blocks alongside Python source text. Use `read_job()` to inspect an
existing input or construct a `Job` directly. For calculation helpers and
molecular transformations, use the [builder](building-jobs.md).

```python
from psi4_parser.job import (
    Job,
    Molecule,
    OptionAssignment,
    OptionExpression,
    Python,
    SetOptions,
    emit_job,
)

h2 = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n", name="h2")
basis = SetOptions(
    assignments=(
        OptionAssignment(key="basis", value=OptionExpression(source="sto-3g")),
    ),
)
job = Job(body=(h2, basis, Python(source="energy('scf', molecule=h2)")))
source = emit_job(job)
```

`emit_job()` returns Psithon text and checks its complete syntax, including Python
scope rules. Invalid syntax raises `JobSyntaxError`. Psi4 checks method and option
availability and the scientific consistency of the calculation.

Emission rebuilds native layout. Use `psi4_parser.parse()` for original source,
syntax comments, and character positions.

## Molecules and atom references

`Molecule.records` keeps the input order of atoms, electronic states, fragment
separators, variables, units, symmetry and frame settings, XYZ headers, geometry
sources, and effective fragment potentials (EFPs).

Atoms have `Cartesian` or `ZMatrix` coordinates. Z-matrix `Anchor` entries are
ordered as distance, bond angle, and dihedral. Distances use the molecule's length
unit; angles use degrees. `Number` retains input spelling such as `1.2D-3`;
`Variable` refers to a named geometry value.

Each atom has a unique ID independent of its element label and row number.
`AtomReference` uses that ID, which emission resolves to a one-based atom index,
including dummy atoms. Parsed and imported atoms receive IDs `a1`, `a2`, and so on.
JSON retains custom IDs; reading emitted Psithon assigns new ones.

`molecule.atoms` returns all atoms, including ghosts and dummies.
`molecule.fragments` returns atom/EFP groups and their charge and multiplicity.
`Molecule.from_fragments()` combines fragments and accepts a separate overall
`ElectronicState`. Supply distinct atom IDs across fragments and choose the
combined multiplicity explicitly. Omitted states remain unspecified.

## Edit geometry

`with_coordinates(atom_id, coordinates)` replaces an atom's coordinate
representation. `with_variable(name, value)` replaces a declared geometry value.
Both return new molecules with the other records retained.

```python
from psi4_parser.job import Molecule, Number, read_job

job = read_job("""molecule {
H
O 1 0.96
O 2 1.45 1 100
H 3 0.96 2 100 1 D
D = 0
}
""")
molecule = job.body[0]
assert isinstance(molecule, Molecule)
changed = molecule.with_variable("D", Number(value="60.0"))
```

The variable must already be declared. Coordinate edits retain symbolic values;
use the builder for [numerical transformations](building-jobs.md#transform-molecules)
and [coordinate conversion](building-jobs.md#convert-coordinate-representations).
Optimizer settings can be written through `SetOptions`; the builder provides
[constraints addressed by atom ID](building-jobs.md#configure-optimization-constraints).

## Import molecular files

`Molecule.from_xyz(text)` reads one XYZ document into Cartesian records with an
explicit unit setting. Its title is file metadata; explicit XYZ headers in
existing Psithon remain available through `read_job()`.

`Molecule.from_file(path)` accepts a `pathlib.Path`. XYZ is read directly;
other formats use Open Babel and retain its resolved charge and multiplicity,
including inferred defaults. Files must contain one structure. Define Psi4
fragments explicitly.

`GeometrySource` stores a `from_file` path or PubChem query for Psi4 to resolve
when the input runs. Reading or loading a job retains that reference as data.

## Basis sets, solvers, and Python blocks

`Basis` contains assignments, section labels, and `BasisData` lines for Gaussian
basis or effective core potential data. `PCM.body` contains PCMSolver text;
`CFour.body` contains CFOUR text. Their scientific settings are interpreted by
the corresponding solver.

`Python` holds source statements. `PythonTemplate.parts` places native blocks
between Python text segments, allowing them inside functions, loops, and other
compound statements. The complete job supplies the context for syntax checks.
Reading emitted Python may regroup statements into different `Python` nodes.

## Save and load JSON

```python
from psi4_parser.job import Job, read_job

job = read_job("set basis sto-3g\n")
document = job.model_dump_json()
restored = Job.model_validate_json(document)
schema = Job.model_json_schema()
```

`kind` identifies each variant. Concrete Python constructors supply it by default;
JSON includes it and requires it wherever several variants are possible.
The schema rejects unknown fields and describes each field's meaning and
constraints. Loading checks structure; `emit_job(restored)` checks the complete
Psi4 and Python syntax.

The [CLI](../README.md#save-load-and-convert-json) reads and writes this `Job`
format. Builder specifications use the separate `JobSpec` format.
