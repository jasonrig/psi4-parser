# Construct explicit response roots and products

Attach `TDSCFAnalysis` to a response model and require each secondary quantity
through a root-resolved `ProductGoal`. Shared scientific contracts apply across
Psi4 releases. No binary, dependency, or version inspection is performed.
[Example 39](../examples/39-formal-excited-states/README.md) builds three response
calculations and proves their reference/excitation/total relationships.

```python
from psi4_parser.formal import (
    CalculationGoal,
    ElectronicTarget,
    Model,
    ProductGoal,
    Setting,
    TDSCFAnalysis,
)

response = CalculationGoal(
    id="response",
    driver="energy",
    geometry="molecule",
    models=(
        Model(
            method="td-hf",
            basis="cc-pvdz",
            reference="rhf",
            settings=(Setting(name="scf_type", value="PK"),),
            tdscf=TDSCFAnalysis(states=3, spin="singlet", approximation="tda"),
        ),
    ),
)
excitation = ProductGoal(
    id="excitation",
    calculation="response",
    name="excitation_energy",
    electronic_target=ElectronicTarget(root=1, multiplicity=1),
)
```

The calculation's primary return is the ground-reference electronic energy.
Labelling that return as an excitation or excited-state total fails verification.
The selected root belongs on the product. `Model.electronic_target` still needs
separate state-specific lowering.

## Preserve the root set

`states` is a positive total count or a tuple containing one nonnegative count
per native computational irrep. A total uses Psi4's native allocation among
irreps; it does not establish the globally lowest roots across every possible
irrep. A tuple requires an explicit molecular point group with matching size.
A one-entry tuple is rejected because Psi4 unwraps it into the total-count
convention; use an integer for C1.

`spin` selects RHF singlets, triplets, or the native `both` split, which favors
singlets for odd counts. Per-irrep tuples split each entry independently. UHF
uses `unrestricted` response and carries no guaranteed multiplicity. A product's
explicit multiplicity must follow a single restricted spin sector.

Root selectors use one-based energy order within the requested set and must fit
that set. This supplies no physical state tracking across changed geometries,
kernels, or RPA/TDA choices. Symmetry-resolved selection needs a further contract;
leave the selector's `symmetry` null.
Scalar simplification and solver encoding retain different roots as distinct
quantities. Repeated aliases of the same validated native root may cancel,
including aliases with an explicit compatible spin qualifier.

Root counts are bounded by the complete occupied–virtual response space:
`O * (N - O)` per restricted sector, or the sum of alpha and beta spaces for UHF.
Electron/basis evidence establishes these dimensions. Per-irrep populations and
a suitable reference remain assumptions. RPA additionally assumes the required
stability. Convergence and physical accuracy remain separate from construction.

`approximation` selects `rpa` or `tda`. Residual threshold and iteration limit
are typed independent controls. Raw settings cannot override these choices.
Native input applies them inside the per-call option scope and restores values
and changed flags afterward. Permitted reuse preserves the entire response model.

## Require each product independently

| Product | Native unit | Native layout |
| --- | --- | --- |
| `excitation_energy` | hartree | Scalar, ground to selected root |
| `excited_state_energy` | hartree | Scalar, reference plus selected excitation |
| `oscillator_strength_length` | 1 | Scalar, length gauge |
| `oscillator_strength_velocity` | 1 | Scalar, velocity gauge |
| `electric_transition_dipole_length` | e·bohr | `(1, 3)` row, producing calculation frame |

An `excited_state_energy` expression must be a native total alias, or exactly one
reference plus one excitation from that same producer. Altered weights and
unrelated producers fail. The symbolic encoding connects each native total to
its own excitation; another root's identity produces a counterexample.

Reports and manifests declare transient `native_variables`, including scalar
or array storage. HF products use `TD-HF` keys; reviewed density-functional
products use Psi4's generic `TD-DFT` aliases. These declarations neither retrieve
nor preserve values. A separate consumer must collect after the producer and
before a later call changes native state. Dependent expressions remain symbolic
recipes. No collection writer or output validator is added.
Length-gauge transition-moment requests also enable native `E_TDM_LEN` printing,
so a separate parser can find these observables in normal Psi4 output. This uses
native text formatting and adds no durable full-precision snapshot.

## Inspect and extend coverage

The shared catalogue covers PK `td-hf`/`td-scf` with RHF singlet/triplet/both
sectors and UHF spin-conserving response, plus RHF singlet `td-pbe`/`td-b3lyp`.
ROHF, restricted density-functional triplets, other kernels, solvent response,
derivatives, and further observables need additional contracts.

Inspect `TDSCFAnalysis` and `ProductGoal.electronic_target` through targeted schema
discovery, and query method/product cases through existing CLI/MCP interfaces.
`combine_catalogs()` merges independent contributions, deduplicates identical
entries, and rejects conflicting identities or overlapping cases. Each rule keeps
its own evidence. These response rules required source review without a new
binary audit or release profile.

The reviewed relationships follow Psi4's
[response implementation](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/procrouting/response/scf_response.py),
[driver route](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/procrouting/proc.py),
and [TD-SCF manual](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/doc/sphinxman/source/tdscf.rst).
