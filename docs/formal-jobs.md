# Construct jobs with proved relationships

Use `psi4_parser.formal` when a job must satisfy explicit relationships between
its calculations. Describe molecular inputs, steps, and requirements with
`Plan`. Call `verify()` for a report, `build()` for a checked builder `JobSpec`,
or `render()` for complete Psi4 input. These calls run without Psi4 installed.

The module is separate from `psi4_parser.builder` and `psi4_parser.job`.
It composes calculations and energy expressions; complete workflow presets are
not required. The ordinary builder remains available for other interfaces.

For independent scientific requests, capability evidence, bounded construction,
and export bundles, start with [scientific planning](scientific-planning.md).
Calling `verify(plan)` alone retains relationship-only scope.

## Discover and describe a plan

Use `inspect.signature()` and selected `model_fields` to inspect constructors
and field descriptions. `help(verify)`, `help(build)`, and `help(render)` explain
their results. `Plan.model_json_schema()` describes the JSON format; the
`kind` field selects each step and requirement variant.

```python
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    Calculation,
    Model,
    Plan,
    SameModel,
    UsesGeometry,
    render,
    verify,
)

geometry = Molecule.from_xyz(
    "2\nHydrogen\nH 0 0 0\nH 0 0 0.85\n",
    state=ElectronicState(charge=0, multiplicity=1),
)
model = Model(method="scf", basis="sto-3g", reference="rhf")
plan = Plan(
    molecules=(molecule("h2", geometry),),
    steps=(
        Calculation(id="opt", driver="optimize", geometry="h2", model=model),
        Calculation(id="freq", driver="frequency", geometry="opt", model=model),
    ),
    requirements=(
        UsesGeometry(calculation="freq", geometry="opt"),
        SameModel(calculations=("opt", "freq")),
    ),
)
report = verify(plan)
Path("proof.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
Path("input.dat").write_text(render(plan), encoding="utf-8")
```

The example demonstrates construction and verification with a small basis; it
is not a recommended research protocol. See the runnable
[geometry example](../examples/22-formal-geometry/build.py) and
[composite-energy example](../examples/23-formal-composite/build.py). Each saves
its plan, proof report, generated input, and a rejected variant's counterexample.

## Compose steps and requirements

Declare resolved Cartesian molecules with explicit overall charge and
multiplicity. Convert Z-matrices with the builder before planning. External
geometry sources, geometry parameters, and EFP placements produce a located
`invalid` report. Plan names must be unique across molecules and steps.

Drivers include `energy`, `optimize`, `frequency`, `gradient`, `hessian`, and
`properties`. Gradients and Hessians are tensors and cannot enter scalar energy
expressions. The properties driver requires explicit property names; its primary
return value remains an energy.
A calculation's `geometry` names a preceding molecular input or optimization.
Optimization supplies a future geometry under its id. Full-basis `Subsystem`
steps also supply geometry after selecting real and ghost fragments. Each calculation has
an explicit method, basis, and reference. Method and basis names are trimmed
before execution; model comparisons ignore case but do not resolve aliases.

Use `Combination` and `EnergyTerm` to add exact rational multiples of preceding
results. Combinations may use earlier combinations. Scalar primary values represent the
selected driver's returned energy in hartree. In particular, `frequency()`
returns the electronic energy, not a thermal correction. Some energy methods
return interaction energies; the caller must choose compatible physical
quantities for their scientific question.

State the intended relationships independently of the proposed steps:

| Requirement | Claim |
| --- | --- |
| `UsesGeometry` | A calculation consumes the specified input or optimized geometry. |
| `SameGeometry` | Two calculations consume the same geometry source and electronic state. |
| `SameModel` | Two calculations have matching declared models, including core treatment and settings. |
| `EnergyFormula` | A result equals the supplied linear energy formula for every possible input energy. |

Geometry equality means shared provenance. Two independent declarations with
identical coordinates remain distinct sources. Different methods and bases are
allowed unless a requirement demands equality. Requirements and combinations
can be added to express new workflows within these operations.

## Inspect verification results

`verify(plan)` first checks names, reference order, and supported geometries.
It then confirms that the encoded premises are satisfiable. For each requirement,
it asks whether those premises and a violation can hold together:

- `proved`: no violating assignment exists.
- `violated`: a counterexample shows actual and expected symbolic values.
- `unknown`: a solver limit or undecided check prevents a conclusion.
- `invalid`: structural diagnostics prevent a faithful encoding of the plan.
- `unsupported`: a feature lacks implemented lowering or explicit support.

Only `proved` permits `build()` or `render()`. Other outcomes raise
`VerificationError`; its `.report` retains the structured result. These functions
verify the supplied plan themselves, so a stale report cannot authorize a
changed plan. At least one requirement is required.

Reports bind plan, request, capability and verification identities, rule and
Z3 versions, resource limits, expected quantities, assumptions,
and every obligation's SMT-LIB counterexample query. Proved obligations also
include Z3 proof expressions. Replay a query with a fresh `z3.Solver` and
`from_string()`: proved queries must return `unsat`, and violated queries `sat`.
This is evidence checked by Z3, not a separate proof of Z3 or the Python renderer.

Use `Limits` to bound each solver check. Unknown results remain undecided.
Inspect status and individual messages during agent work; save the complete
report to a file instead of repeatedly sending proof text through the model.

## Export and use the constructed job

The generated input uses private molecule clones, native option defaults plus
declared per-call settings, state restoration, and integral cleanup between
calculations. See [option isolation](formal-isolation.md) for scope and native
API assumptions. An optimization cannot change its source or an earlier geometry
snapshot. Execution, result parsing, and numerical acceptance belong to a
separate consumer. After successful execution, `formal_results` maps step ids to energies and
`formal_geometries` maps molecular input and optimization ids to molecules.
Generated variable names are independent of caller-supplied ids.

Proofs cover the requested relationships under the report's execution
assumptions. Psi4 remains responsible for resolving methods, bases, molecular
consistency, native defaults, convergence, and numerical results. The algebra
uses exact real numbers; its proof does not bound floating-point roundoff.
Scientific suitability and diagnostics require separate evidence. Run the saved
input with the intended Psi4 build and preserve its output before reporting a
completed calculation. Editing the returned builder job or generated input
creates a new artifact outside the original plan's checked construction.
