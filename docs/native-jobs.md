# Constructing native jobs

`psi4_parser.job` represents a job as ordered Pydantic models. Native statements
have explicit types; Python statements are source text checked in the context of
the complete job.

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

molecule = Molecule.from_xyz(
    "2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n",
    name="h2",
)
options = SetOptions(
    assignments=(
        OptionAssignment(
            key="basis",
            value=OptionExpression(source="sto-3g"),
        ),
    ),
)
job = Job(
    body=(
        molecule,
        options,
        Python(source="energy('scf', molecule=h2)"),
    )
)
source = emit_job(job)
```

`emit_job()` renders source and validates it with the generated parser. It raises
`JobSyntaxError` for invalid native syntax or contextual Python errors. Emission
does not execute a calculation. Psi4 remains responsible for option availability
and scientific consistency.

`read_job(source)` constructs the same model types from existing input. Native
comments and layout are regenerated during emission. For original text, comments,
and source positions, use `psi4_parser.parse()` and its CST/source helpers.

## Molecules and edits

`Molecule.records` retains the ordered specification. Its variants include atoms,
electronic states, fragment separators, geometry variables, units, frame and
symmetry directives, XYZ headers, geometry references, and EFP placements.
Atoms have `Cartesian` or `ZMatrix` coordinates. A Z-matrix's ordered `Anchor`
entries represent its distance, angle, and dihedral.

`molecule.atoms` exposes atom records, including ghosts and dummy atoms.
`molecule.fragments` exposes atom/EFP groups and their explicit states.
`Molecule.from_fragments()` composes fragments and accepts a separate overall
`ElectronicState`. Omitted charge and multiplicity remain unspecified.

`with_coordinates(atom_id, coordinates)` replaces one atom's representation.
`with_variable(name, value)` replaces a declared geometry parameter. Both return
new molecules. For example, a dihedral represented by `Variable(name="D")`
can be changed through its corresponding `GeometryVariable` declaration:

```python
from psi4_parser.job import Molecule, Number, read_job

molecule = read_job("""molecule {
H
O 1 0.96
O 2 1.45 1 100
H 3 0.96 2 100 1 D
D = 0
}
""").body[0]
assert isinstance(molecule, Molecule)
changed = molecule.with_variable("D", Number(value="60.0"))
```

The molecule must declare `D` before changing it. Constraint options belong in
`SetOptions`, using the corresponding optimizer's option names and values.
Coordinate conversion and evaluation are separate operations; these models
retain either representation and symbolic values.

Atom identities must be unique within a molecule, including when composing
fragments. `AtomReference` uses those identities, and emission resolves them to
the current one-based atom indices. Parsed and imported molecules receive IDs
`a1`, `a2`, and so on. JSON retains custom IDs; reading emitted Psithon assigns
new IDs because Psithon does not encode them.

## Files and embedded languages

`Molecule.from_xyz(text)` imports a complete XYZ document as native Cartesian
records with explicit units. Its title is treated as a file comment. Explicit
XYZ headers in existing Psithon remain available through `read_job()`.
`Molecule.from_file(path)` imports XYZ directly and other formats through the
included Open Babel support. Open Babel imports resolved charge and multiplicity,
which may include backend defaults. It does not infer Psithon fragments from
connectivity. Multi-molecule files are rejected.

`GeometrySource` retains `from_file` and PubChem references as data; reading a job
does not open those references. `Basis` exposes assignment and label records;
Gaussian basis/ECP records remain `BasisData` text. `PCM.body` and `CFour.body`
retain their complete embedded language payloads.

## JSON and Python context

```python
from psi4_parser.job import Job, read_job

job = read_job("set basis sto-3g\n")
document = job.model_dump_json()
schema = Job.model_json_schema()
restored = Job.model_validate_json(document)
```

The schema uses discriminated unions and rejects unknown fields. `kind` selects
each variant and defaults automatically when constructing its concrete Python
class. Serialized jobs include these tags; each discriminated union requires its
tag when loading JSON. Fields describe their meaning and structural constraints.
Numeric values retain their source spelling, including Fortran exponents.

JSON validation checks the model structure. Python source is checked when the
complete job is emitted, allowing a loop, function, or other compound statement
to retain its context. `PythonTemplate.parts` interleaves Python text segments
and native models for such mixed statements. A `Python` node may contain several
statements; reading emitted source groups them according to parser statements.
