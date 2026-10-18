# Build Psi4 jobs with Python

Use `psi4_parser.builder` to construct inputs from reusable components, transform
molecules, and save complete specifications as JSON. Rendering checks the whole
input and applies the standard formatting style. It does not execute Python or
run calculations.

## Compose components

```python
from psi4_parser.builder import JobSpec, Molecule, energy, molecule, options, render_job

geometry = Molecule.from_xyz("2\nHydrogen\nH 0 0 0\nH 0 0 0.74\n")
h2 = molecule("h2", geometry)
job = JobSpec() | h2 | options(basis="cc-pvdz") | energy("scf", molecule=h2.ref)
source = render_job(job)
```

A molecule declaration's `.ref` refers to its explicit Python name. Declare it
before using it. Calculations can use `assign="e_scf"` or
`assign=("e_scf", "wfn")` for tuple unpacking. A calculation with one assigned
name exposes `.ref` for subsequent calls; use `Reference(name="wfn")` to select
an unpacked binding.

`compose(*components)` concatenates components and existing specifications.
`+` is an equivalent shorthand. Composition preserves every component in order:
it does not merge options, insert dependencies, or deduplicate declarations.
Duplicate declarations and unresolved structured references fail at compilation.

`pipe(value, *stages)` is the named counterpart to `|`. Job components act as
append stages. Molecules use `|` for transformations; fragment assembly has its
own named operation.

## Attach block comments

```python
from psi4_parser.builder import Memory, compose, options, render_job

memory = Memory(amount=1.0, units="GiB").with_comment("Memory for this job.")
basis = options(basis="cc-pvdz").with_comment(
    "Basis for the comparison.\n\nKeep this setting across all jobs."
)
source = render_job(compose(memory, basis))
```

Pass plain text without generated hash prefixes. Each line becomes a standalone
`#` comment, and empty lines become `#`. Comments precede their component; blank
lines between components go above its comment group. They are retained in JSON
and when reusing components. Inline attachments and comments on individual
atoms or assignments are not supported.

## Import geometry and specify states

`Molecule.from_xyz(text, state=...)` and `Molecule.from_file(path,
file_format=...)` import one structure. XYZ imports leave charge and multiplicity
unspecified unless supplied. Other formats retain Open Babel's resolved state,
which may include format defaults. No import infers Psi4 fragments from bonds.

Coordinate-only formats use explicit `perceive_bonds=True` to request bond
perception. Supplied connectivity remains available through `molecule.bonds`.
Imports retain stable atom IDs (`a1`, `a2`, ...), isotope labels, and ghost labels.
Manual `Nucleus` values can also specify an explicit isotope mass.

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

Assembly namespaces IDs, for example `left:a1`, and preserves fragment states.
The overall state must be specified when needed; combined multiplicity is never
inferred. Nested fragment structures with an additional subsystem-wide state
must be flattened explicitly because Psithon cannot express that hierarchy.

Manual molecules support Cartesian and Z-matrix records, geometry parameters,
external geometry sources, effective fragments, symmetry, and frame directives.
`GeometrySource` keeps a filename or PubChem query unresolved. Numerical
transformations require resolved atomic coordinates.

## Molecular symmetry

Set `symmetry="c2v"` when constructing a `Molecule` to request that computational
subgroup. The setting is retained in JSON and through coordinate conversions,
and emits `symmetry c2v` in the molecule block. Leave it as `None` for Psi4's
automatic detection, or use `"c1"` to request a calculation without exploiting
point-group symmetry. Psi4 uses a supported Abelian subgroup even when the full
molecular point group is non-Abelian, such as tetrahedral methane.

Conversions preserve the geometry within their stated tolerances and retain
atom identities; they do not permute equivalent atoms to obtain a match. Supply
the complete geometry: the builder never expands a symmetry-unique subset of
atoms or symmetrizes coordinates automatically.

Geometry edits check an explicit computational symmetry request with a
`1e-9` angstrom positional tolerance, stricter than Psi4's `1e-8` bohr symmetry
check. If it no longer fits, they emit
`SymmetryChangedWarning` and adopt a verified lower subgroup. Stretching only
one O–H bond in `c2v` water, for example, retains `cs`; a distortion with no
remaining supported symmetry adopts `c1`. Every atom, isotope mass, ghost role,
fragment, and state is retained. The check does not adjust other coordinates.
Unresolved geometry cannot establish symmetry, so an edit that leaves it
unresolved warns and uses `c1`. An unset request remains automatic.

Use `with_symmetry("c1")` to relax symmetry intentionally before an edit. This
changes the request without changing any coordinates or parameter references,
and subsequent edits do not warn about symmetry loss. `with_symmetry(None)`
restores automatic Psi4 detection. Selecting another supported subgroup checks
that it fits the resolved geometry first. Axis-qualified requests require
`fixed_orientation=True` for independent verification.

```python
from psi4_parser.builder import Molecule, angstrom, set_distance, with_symmetry

water = Molecule.from_xyz("3\nWater\nO 0 0 0\nH 0 .757 .586\nH 0 -.757 .586\n")
relaxed = (
    water
    | with_symmetry("c1")
    | set_distance(("a1", "a2"), angstrom(1.2), moving=("a2",))
)
```

`detect_point_group(geometry)` reports the full Schoenflies group using MolSym,
with a `1e-6` angstrom detection tolerance. For example, tetrahedral methane is
`"Td"`, although a Psi4 calculation uses a supported Abelian subgroup. Linear
groups are returned as `"Cinfv"` or `"Dinfh"`. Detection uses disposable arrays;
it never adopts recentered or symmetrized backend coordinates. Dummy reference
atoms are excluded, and custom isotope masses are retained.

MolSym distinguishes sites by mass. If equal-mass sites have different elements
or ghost roles, full-group detection raises `ValueError` rather than conflate
them. The independent edit checks still distinguish those roles.

Irrep-indexed options, such as `DOCC`, retain their supplied values after a
symmetry change; choose their entries for the new computational group.

To keep equal bonds or angles linked, reuse one `Parameter` in a hand-authored
Z-matrix, then change the shared value with `with_parameter`. Conversion does
not infer shared parameters from coincidentally equal values. Keep Cartesian
coordinates and the appropriate frame directives when laboratory axes matter.
Verification searches up to 10,000 candidate frames; a request that cannot be
verified within that limit is relaxed conservatively, with a warning.

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

`set_distance`, `set_angle`, and `set_dihedral` require the moving side explicitly.
It must contain the final coordinate endpoint and exclude its fixed reference
atoms. Other selected atoms move rigidly with that endpoint.

`connected_side(molecule, fixed, moving)` can select the connected side of an
explicit bond. Ring cuts are ambiguous and require a manual selection.

`translate`, `rotate`, and `reorder_atoms` retain atom identities and metadata.
Reordering stays within fragments and must keep Z-matrix anchors valid. Use
`with_parameter(name, value)` to replace a declared symbolic coordinate.
Numerical edits require Cartesian, resolved coordinates: apply `to_cartesian`
explicitly before discarding symbolic relationships.

Lengths use `angstrom()` or `bohr()`; angles use `degrees()` or `radians()`.
`positions(molecule)` returns resolved positions in angstroms. Numerical values
must be finite, and dimensioned parameters must match their coordinate.

## Convert coordinate representations

```python
from psi4_parser.builder import Molecule, NamedCoordinate, dihedral, to_zmatrix

peroxide = Molecule.from_xyz("4\nPeroxide\nH 1 0 0\nO 0 0 0\nO 0 0 1.4\nH 0 1 1.4\n")
internal = peroxide | to_zmatrix(
    frame="canonical",
    requested=(NamedCoordinate(name="D", coordinate=dihedral("a1", "a2", "a3", "a4")),),
)
```

Requested distances, angles, and dihedrals become named geometry variables.
Use `with_parameter("D", degrees(90))` to change the selected torsion later.
`to_cartesian(molecule)` resolves a symbolic or internal representation.

Conversion preserves atom order by default. `reorder=True` permits a different
order within fragments to satisfy requested coordinates or find a usable
reference plane. Stable IDs are retained; the result's `atoms` exposes the order.
Use `layout=(AnchorLayout(...), ...)` to supply explicit reference choices and
bypass automatic search.

`frame="canonical"` acknowledges that the laboratory frame can change. Psi4
normalizes Z-matrix orientation, so `frame="preserve"` rejects multi-atom
conversions; keep Cartesian coordinates when the absolute frame matters.

Dummy insertion requires `allow_dummies=True`. Inserted dummies have stable IDs
and nucleus label `X`. They can supply a missing reference plane, but cannot
make a collinear requested dihedral meaningful.

Automatic layout search defaults to 10,000 candidate states, controlled by
`max_states`. Incompatible requests, exhausted search, and numerical degeneracy
produce distinct errors. Reconstruction is verified after a proper rigid
alignment, excluding reflections. Default tolerances are `1e-8` angstrom for
positions and `1e-6` degrees for angles; both must be finite and positive.

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

Typed constraints currently target OptKing. Use `freeze(coordinate)` or
`bound(coordinate, lower, upper)` with distance, angle, dihedral, out-of-plane,
or Cartesian coordinates. Frozen coordinates retain their initial value. For
an exact target, first manipulate the geometry and then freeze the coordinate.
A range must have distinct lower and upper bounds.

Constraints use stable atom IDs. Compilation resolves optimizer indices after
reordering and excludes reference-frame dummies. Cartesian constraints require
Cartesian geometry. Ranged Cartesian constraints also require the molecule's
`fixed_com=True` and `fixed_orientation=True` so the axes retain their meaning.

Local options and generated constraints are restored with `try/finally`,
including when the calculation raises. Persistent `options(...)` components
remain in effect. Conflicting typed and raw definitions of the same constraint
setting are rejected.

The generated calls retain Psi4's ordinary molecule mutation semantics. Jobs,
loops, and separate input files for a scan remain the caller's choice.

## Use other Psi4 interfaces

`energy`, `gradient`, `hessian`, `optimize`, `frequency`, and `properties` accept
open method names and extra keyword arguments. Use `call(target, *args, **kwargs)`
for other interfaces. Strings are literal values; `Reference` names an explicit
binding and `Expression` supplies Python syntax. `Python(source=..., provides=...)`
can declare bindings used by later structured components.

The native components are `MoleculeDeclaration`, `Options`, `Basis`, `External`,
`PCM`, `CFour`, and `Memory`. Basis definitions expose assignment, section-label,
and data records; external potentials expose their ordered records. PCM and
CFour take explicit embedded-language bodies. Other optimizers remain accessible
through generic calls and their ordinary argument interfaces.

## Save specifications and emit input

```python
from psi4_parser.builder import JobSpec, Memory, compose, lower_job, render_job

job = compose(Memory(amount=1.0).with_comment("Memory budget."))
document = job.model_dump_json(indent=2)
schema = JobSpec.model_json_schema()
restored = JobSpec.model_validate_json(document)
source = render_job(restored)
native_tree = lower_job(restored)
```

The JSON document retains construction intent, molecular geometry, references,
constraints, and comments. It does not store transformation callables or replay
recipes. Each tagged variant's `kind` defaults when constructing its concrete
Python class and is included in JSON. The schema has no version field.

Loading JSON validates structure. `lower_job` additionally checks declarations,
references, backend combinations, and complete input syntax. `render_job` also
formats the result. The emitted input depends on Psi4 and its requested solvers;
it does not import this builder package.

The CLI's existing JSON conversion uses the parsed native job representation
from `psi4_parser.job`. Builder specifications use the Python API described here.
