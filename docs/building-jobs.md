# Build Psi4 jobs with Python

Use `psi4_parser.builder` to compose inputs, transform molecules, and save job
specifications as JSON. Components describe what Psi4 should do; `render_job()`
turns them into a complete, validated input.

For a call that must start from native option defaults, supply its settings in
`local_options` and set `isolate_options=True`. See
[option isolation](formal-isolation.md) for restoration, module coverage, and
resource settings. Formal construction enables this mode for every calculation.

For explicit relationships between calculation geometries, models, or energy
expressions, use the separate [formal constructor](formal-jobs.md). It checks
the supplied requirements before producing a builder job or input text.

## Compose components

```python
from psi4_parser.builder import JobSpec, Molecule, energy, molecule, options, render_job

geometry = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n")
h2 = molecule("h2", geometry)
job = JobSpec() | h2 | options(basis="cc-pvdz") | energy("scf", molecule=h2.ref)
source = render_job(job)
```

`compose(*components)`, `a + b`, and `JobSpec() | a | b` concatenate components
in order. Existing specifications are flattened. Repeated settings and
calculations keep their positions and effects. Components and transformations
return new values, so they can be reused.

`molecule(name, geometry)` declares a named molecule. Place it before any step
using its `.ref`. Calculations can assign results with `assign="e_scf"` or unpack
several values, for example:

```python
from psi4_parser.builder import Molecule, Reference, call, energy, molecule

h2 = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
scf = energy("scf", molecule=h2.ref, return_wfn=True, assign=("e_scf", "wfn"))
dipole = call("psi4.oeprop", Reference(name="wfn"), "DIPOLE")
```

A component with one assigned result exposes `.ref`. For unpacked results, use
`Reference(name=...)` to select a name. Strings are literal values;
`Expression(source=...)` supplies Python code evaluated when the input runs.

`pipe(value, *stages)` applies functions from left to right, like `|`.
Molecule stages transform geometry; job components append themselves to a job.
Use `assemble_fragments()` to combine molecular parts.

## Nest composed jobs

Loops and branches take composed jobs as their bodies:

```python
from psi4_parser.builder import (
    Molecule,
    Reference,
    compose,
    energy,
    for_each,
    molecule,
    options,
)

h2 = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
methods = for_each(
    "method",
    ["scf", "mp2"],
    compose(energy(Reference(name="method"), molecule=h2.ref)),
)
job = compose(h2, options(basis="cc-pvdz"), methods)
```

- `for_each(target, iterable, body)` repeats steps over a sequence.
- `if_else(condition, body, otherwise=...)` chooses a branch.
- `while_loop(condition, body)` repeats while its condition is true.
- `with_context(context, body, target=...)` enters a context manager.
  `WithBlock(items=(WithItem(...), ...), body=...)` enters several.

Conditions, iterables, and context managers accept values, references, or
`Expression` objects. Use an expression for a Python test such as
`Expression(source="e_scf < -1.0")`; a string remains literal text. Empty and
comment-only bodies receive `pass`.

Loops accept `otherwise`, following Python's loop-else rule: it runs after normal
completion, including zero iterations, and is skipped by `break`.
Use nested conditionals in `otherwise` for additional branches.

For exception handling and cleanup:

```python
from psi4_parser.builder import (
    ExceptionHandler,
    Expression,
    Molecule,
    Python,
    TryBlock,
    compose,
    energy,
    molecule,
)

h2 = molecule("h2", Molecule.from_xyz("2\nH2\nH 0 0 0\nH 0 0 .74\n"))
guarded = TryBlock(
    body=compose(energy("scf", molecule=h2.ref)),
    handlers=(
        ExceptionHandler(
            exception=Expression(source="RuntimeError"),
            name="error",
            body=compose(Python(source="print(error)")),
        ),
    ),
    finally_body=compose(Python(source="print('Calculation attempt finished')")),
)
```

`TryBlock.otherwise` runs after a successful body. `finally_body` runs on success
or failure. A handler with no `exception` catches any exception and must be last.
Its exception name is available inside that handler and is deleted afterward.

### Names across branches and loops

A structured reference must name a value assigned on every path that reaches
it. Assignments in both branches of an `if_else` are available afterward. A loop
can run zero times, so initialize a result before the loop if later steps need
it. Context managers can suppress exceptions, leaving body assignments or later
context-entry targets unset. Cleanup code must also allow for a failed try body.

Nested calculations and calls may update existing names. Top-level duplicate
assignments are rejected, and molecule declarations must be unique on each path.
Branches may declare different geometries under the same name; later constraints
require the branches to agree on atom layout and frame settings.

Use `Python(source=..., provides=(...))` to declare names supplied by a Python
fragment. The compiler trusts those declarations. Python fragments also support
functions, classes, and pattern matching. Complete-input checks enforce scope
rules, including where `break`, `continue`, and `return` are allowed.

## Attach block comments

```python
from psi4_parser.builder import Memory, compose, options, render_job

memory = Memory(amount=1.0, units="GiB").with_comment("Memory for this job.")
basis = options(basis="cc-pvdz").with_comment(
    "Basis for the comparison.\n\nKeep across jobs."
)
source = render_job(compose(memory, basis))
```

Supply plain text without leading hashes. Each line becomes `# text`; empty lines
become `#`. Comments appear immediately before their component at its indentation.
Required separators go above the comment group. Attachments stay with components
through composition, immutable updates, and JSON round trips.

Attachments apply to whole components, including control-flow blocks.
Use input text for comments within atom rows, assignments, or statement lines.

## Import geometry and specify states

`Molecule.from_xyz(text, state=...)` and `Molecule.from_file(path, file_format=...)`
read one structure with coordinates. XYZ leaves charge and multiplicity
unspecified unless supplied; other formats use Open Babel's resolved state,
including format defaults. Generate coordinates before importing a structure
that contains only connectivity.

Atom IDs are `a1`, `a2`, and so on in file order. Imports retain isotope and ghost
labels and supplied bonds. Use `perceive_bonds=True` to infer bonds from positions.
Connectivity is available through `molecule.bonds`; define Psi4 fragments
explicitly. Manual `Nucleus` objects can also specify isotope masses.

```python
from psi4_parser.builder import (
    ElectronicState,
    Molecule,
    angstrom,
    assemble_fragments,
    translate,
)

singlet = ElectronicState(charge=0, multiplicity=1)
left = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n", state=singlet)
right = left | translate((angstrom(3), angstrom(0), angstrom(0)))
dimer = assemble_fragments(("left", left), ("right", right), state=singlet)
```

Assembly prefixes atom IDs, such as `left:a1`, and parameter names, such as
`left_R`. It preserves fragment states; choose the overall charge and multiplicity
separately when needed. Nested fragments with an additional subsystem-wide state
must be flattened because Psithon cannot express that hierarchy.

Manual molecules can contain Cartesian or Z-matrix coordinates, parameters,
geometry sources, effective fragment potential (EFP) placements, and symmetry
and frame settings.
`GeometrySource` retains a file path or PubChem query for Psi4 to resolve.
Numerical transformations require resolved atomic coordinates.

## Transform molecules

```python
from psi4_parser.builder import Molecule, angstrom, degrees, set_dihedral, set_distance

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
changed = (
    peroxide
    | set_distance(("a2", "a1"), angstrom(0.98), moving=("a1",))
    | set_dihedral(("a1", "a2", "a3", "a4"), degrees(60), moving=("a4",))
)
```

`set_distance`, `set_angle`, and `set_dihedral` require a `moving` selection.
Include the final coordinate endpoint and exclude the preceding reference atoms.
Selected atoms move together; other atoms retain their positions.
`connected_side(molecule, fixed, moving)` finds one side of a known bond.
A bond in a ring requires an explicit selection.

`translate`, `rotate`, and `reorder_atoms` preserve IDs and molecular metadata.
Reordering must retain fragment order and keep Z-matrix references valid.
`with_parameter(name, value)` replaces an existing geometry parameter while
retaining its references.

Numerical edits require resolved Cartesian coordinates. Use `to_cartesian()` to
resolve symbolic or Z-matrix geometry first. Keep the symbolic representation
when parameters should remain linked to coordinates.

Lengths use `angstrom()` or `bohr()`; angles use `degrees()` or `radians()`.
Values must be finite and have the coordinate's dimension.
`positions(molecule)` returns resolved `(x, y, z)` values in angstroms by atom ID.

## Molecular symmetry

Supply every atom. The builder retains coordinates and identities rather than
expanding symmetry-unique atoms or adjusting coordinates to force symmetry.
Set `Molecule.symmetry` or use a stage to choose the computational point group:

```python
from psi4_parser.builder import Molecule, angstrom, set_distance, with_symmetry

water = Molecule.from_xyz("3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n")
relaxed = (
    water
    | with_symmetry("c1")
    | set_distance(("a1", "a2"), angstrom(1.2), moving=("a2",))
)
```

`with_symmetry("c1")` fully relaxes symmetry. Choose a compatible lower group for
partial relaxation, or `None` for Psi4's automatic detection. Supported requests
are `c1`, `ci`, `cs`, `c2`, `d2`, `c2v`, `c2h`, and `d2h`; axis-qualified requests
require `fixed_orientation=True` for verification.

Edits and conversions check explicit requests at a positional tolerance of
`1e-9` angstrom. An incompatible request emits `SymmetryChangedWarning` and is
lowered to a verified subgroup. Stretching one O–H bond in C2v water can retain
Cs; a general distortion may require C1. Unresolved geometry that cannot verify
the request also warns and uses C1. An unset request stays automatic.

`detect_point_group(geometry)` uses MolSym to report the full molecular group,
such as `Td` for methane, with a `1e-6` angstrom tolerance. Linear groups are
`Cinfv` and `Dinfh`. Dummy atoms are excluded; isotope masses are retained.
Detection leaves coordinates unchanged. Psi4 calculations use one of its
supported computational subgroups.

MolSym distinguishes sites by mass. Equal-mass sites with different elements or
ghost roles raise `ValueError`; edit-time checks distinguish those roles.
Computational symmetry verification searches up to 10,000 candidate frames and
warns before relaxing a request it cannot verify.

After a symmetry change, adjust symmetry-dependent options such as `DOCC` for
the new group. To keep equal bonds or angles linked, reuse a `Parameter` in a Z-matrix
and update it with `with_parameter()`. Conversion retains atom identities but
creates independent parameters for requested coordinates.

## Convert coordinate representations

```python
from psi4_parser.builder import Molecule, NamedCoordinate, dihedral, to_zmatrix

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
internal = peroxide | to_zmatrix(
    frame="canonical",
    requested=(NamedCoordinate(name="D", coordinate=dihedral("a1", "a2", "a3", "a4")),),
)
```

Requested distances, bond angles, and dihedrals become adjustable parameters.
Names must be new and unique. For example, update the torsion above with
`with_parameter("D", degrees(90))`. `to_cartesian(molecule)` resolves coordinates
back to Cartesian positions.

Atom order is preserved by default. `reorder=True` allows reordering within
fragments to satisfy references; IDs and fragment order remain stable.
The result's `atoms` tuple gives its final ordering.
Use `layout=(AnchorLayout(...), ...)` to specify references and bypass search.

`frame="canonical"` allows translation and rotation into Psi4's standard Z-matrix
frame. `frame="preserve"` rejects multi-atom conversions; retain Cartesian
coordinates when laboratory positions and axes matter.

`allow_dummies=True` permits reference atoms labeled `X`, each with a unique ID.
They can provide a missing reference plane for linear geometry. A requested
dihedral must already be defined; inserting dummies cannot repair a collinear
requested torsion.

Automatic search considers up to `max_states=10_000` candidates.
`IncompatibleCoordinatesError` reports conflicting requests or frames,
`LayoutSearchExhaustedError` reports the search limit, and
`DegenerateGeometryError` reports undefined geometry or failed reconstruction.
Verification allows proper rotation and translation, excluding reflections.
Default tolerances are `1e-8` angstrom for positions and `1e-6` degrees for angles;
both must be finite and positive.

## Configure optimization constraints

```python
from psi4_parser.builder import (
    Molecule,
    compose,
    dihedral,
    freeze,
    molecule,
    optimize,
    options,
    render_job,
)

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
hooh = molecule("hooh", peroxide)
job = compose(
    hooh,
    options(basis="cc-pvdz"),
    optimize(
        "scf",
        molecule=hooh.ref,
        constraints=(freeze(dihedral("a1", "a2", "a3", "a4")),),
        local_options=(options(modules=("scf",), maxiter=100),),
        assign="e_opt",
    ),
)
source = render_job(job)
```

Attach typed constraints to `optimize()` with an explicit molecule reference.
They use OptKing. `freeze(coordinate)` retains the starting value;
`bound(coordinate, lower, upper)` restricts it to a range with lower below upper.
For an exact target, edit the geometry and then freeze the coordinate.

Coordinates can be distances, angles, dihedrals, out-of-plane angles, or Cartesian
axes. Atom IDs are resolved to optimizer indices after reordering; dummy atoms
are excluded. Cartesian constraints require Cartesian geometry. Cartesian bounds
also require `fixed_com=True` and `fixed_orientation=True` to keep the axes fixed.

`local_options` and generated constraints apply to one call and are restored in
`try/finally`, including after an exception. Composed `options(...)` remain in
effect. Defining the same constraint through both typed constraints and
`local_options` or `optimizer_keywords` raises an error.

Generated calls follow Psi4's ordinary molecule-update behavior. Choose loops,
separate jobs, or separate files to organize a scan.

## Use other Psi4 interfaces

`energy`, `gradient`, `hessian`, `optimize`, `frequency`, and `properties` accept
method names and extra keyword arguments from Psi4's interfaces.
Use `call(target, *args, **kwargs)` for other functions, `Reference` for earlier
named values, and `Expression` for Python expressions. `Python(source=...,
provides=...)` adds statements and declares the names they make available.

Native components cover `MoleculeDeclaration`, `Options`, `Basis`, `External`,
`PCM`, `CFour`, and `Memory`. Basis definitions contain assignments, labels,
and data records. PCM and CFOUR accept text in their respective solver languages.
Other optimizers are available through generic calls and their usual arguments.

## Apply external potentials

Pass `ExternalPotential` through a calculation's `external_potentials` argument.
Positions have explicit length units and are converted to bohr when rendered.

```python
from psi4_parser.builder import ExternalPointCharge, ExternalPotential, angstrom, energy

field = ExternalPotential(
    points=(
        ExternalPointCharge(
            charge=0.1,
            position=(angstrom(0), angstrom(0), angstrom(2.5)),
        ),
    ),
)
calculation = energy("scf", external_potentials=field)
```

Potentials combine point charges, Gaussian charges, and matrices through `points`,
`diffuse`, and `matrix`. Charges use elementary-charge units. `GaussianCharge`
requires a positive `exponent` in inverse square bohr. `PotentialMatrix` holds a
square matrix in hartree, ordered by the calculation's atomic basis functions.
For example: `PotentialMatrix(((1.0, 0.2), (0.2, -1.0)))`. Psi4 checks its size
against the basis at runtime.

For FI-SAPT, use `FragmentPotentials` containing `FragmentPotential` entries
labeled `A`, `B`, or `C`, each at most once. Point-only entries are emitted as
charge lists compatible with F-SAPT field-file export. The pinned Psi4 exporter
supports only point charges; set `fisapt_do_fsapt=False` for Gaussian or matrix
contributions when their F-SAPT analysis and export are unnecessary.

`External` represents the legacy `external { ... }` block, which the pinned
Psi4 build rejects. Use the argument models above for executable inputs.

## Locate construction errors

`lower_job()` and `render_job()` raise `CompilationError`, a `ValueError` subclass,
for invalid components, references, or complete input. Each diagnostic gives a
`path` of field names and zero-based indices, a readable `location`, and a
`message`. Parser errors also include the generated input's line and column.

For example, an undeclared method reference in the second component reports
`components[1].method: Reference must follow its declaration: missing`.
Nested arguments and atom selections identify their corresponding fields.
Serialize a diagnostic with `diagnostic.model_dump_json()`.

## Save specifications and emit input

```python
from psi4_parser.builder import JobSpec, Memory, compose, lower_job, render_job

job = compose(Memory(amount=1.0).with_comment("Memory budget."))
document = job.model_dump_json(indent=2)
restored = JobSpec.model_validate_json(document)
schema = JobSpec.model_json_schema()
source = render_job(restored)
native_tree = lower_job(restored)
```

JSON stores ordered components, resulting geometry, references, constraints,
and comments. Apply transformations before saving. Concrete Python constructors
supply their `kind` tags; JSON includes them to identify each variant.

Loading checks structure. `lower_job()` checks declarations, references,
constraint compatibility, and complete syntax, returning a `psi4_parser.job.Job`.
`render_job()` returns the formatted input. Generated inputs use Psi4 and their
requested solvers and are self-contained with respect to the builder package.

The MCP tool accepts this `JobSpec` JSON. The CLI's conversion and schema commands
use the separate [editable-input format](native-jobs.md) from `psi4_parser.job`.
