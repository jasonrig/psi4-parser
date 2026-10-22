# Require calculation products and thermal conditions

Use `ProductGoal` to require a named quantity from an earlier calculation goal.
The corresponding plan `Product` records its source and canonical type. It
contains no result value and performs no retrieval or parsing.

```python
from psi4_parser.formal import ProductGoal

spectrum = ProductGoal(
    id="spectrum",
    calculation="frequency",
    name="harmonic_frequencies",
)
```

Append this goal after a frequency `CalculationGoal` named `frequency`. Ordinary
frequency calls still return electronic energy as their primary quantity. The
named spectrum is a separate expected product. Missing products, a changed
source calculation, incompatible types, or absent product evidence prevent
accepted construction. `finite_study()` namespaces product goals and their
sources together with the rest of each case.

## Preserve the product's meaning and provenance

`product_quantity()` documents the built-in product types. Gradients and Hessians
are real tensors. Harmonic frequencies include all 3N modes, including the
translation/rotation classification; their `number_kind` is `complex` to allow
imaginary modes. `normal_modes` means normalized un-mass-weighted Cartesian
columns, with shape `(3*atoms, 3*atoms)` and unit bohr. This is distinct from a
filtered vibrational-only list or mass-weighted modes.

Named oriented products use the producing calculation ID as their native frame
identity. `ExpectedQuantity.geometry` separately retains the geometry source.
The framework does not transform arrays between frames. Scalar expressions
cannot consume these tensors.

Property products require the appropriate explicit property in a `properties`
calculation. Dipoles use three Cartesian components in `e*bohr`. Quadrupoles
use six unique components, XX, XY, XZ, YY, YZ, ZZ, in `e*bohr^2`. Mulliken/Lowdin
charges use `e`; Mayer/Wiberg indices are dimensionless atom matrices. These are
canonical quantity layouts, separate from a result reader's storage layout.

## Declare thermal conditions explicitly

Thermal products require `analysis` on their full frequency calculation:

```python
from psi4_parser.formal import ThermalConditions, VibrationalAnalysis

analysis = VibrationalAnalysis(
    conditions=ThermalConditions(
        temperature_kelvin=298.15,
        pressure_pascal=101325.0,
    ),
    rotational_symmetry_number=2,
)
```

Attach this to the independent `CalculationGoal`. Construction scopes THERMO
temperature, pressure, and symmetry settings to the call, and explicitly passes
the translation/rotation projection choices. Do not override those conditions
in `Model.settings`. A proposed calculation with different analysis settings
fails independent request coverage.

The rotational symmetry number is a scientific input, including isotope
effects. Choose it for the intended species. The framework does not infer it
from an uncomputed optimized geometry. The treatment is native ideal-gas RRHO;
stationarity, imaginary-mode handling, and the suitability of that approximation
remain explicit assumptions. These are expected product contracts, not numerical
checks of a completed calculation.

## Compose corrected energies without relabelling

Named products include zero-point, thermal-energy, enthalpy, and Gibbs corrections
and their corresponding native totals. The solver encodes each total as its
electronic energy plus the corresponding correction. Repeated declarations of
the same source product share that identity.

An expression labelled `gibbs_free_energy`, for example, needs one net electronic
energy and one net Gibbs correction. Its sources must share geometry, system,
electronic state, and one full analysis context. Exact rational coefficients and
nested expressions remain supported. A wrong correction, doubled correction,
mixed temperature, or stale geometry is rejected.

A hybrid expression can use an explicitly selected electronic-energy model
with a correction from another model at the same geometry. Its operand
provenance retains both models; acceptance does not establish the scientific
accuracy of that approximation. [Example 31](../examples/31-formal-products-and-thermochemistry/README.md)
demonstrates MP2 electronic energy plus a specified HF RRHO Gibbs correction.

`reaction_energy` requires closed electronic-energy sources. Use
`reaction_gibbs_free_energy`, `reaction_enthalpy`, `reaction_thermal_energy`, or
`reaction_zero_k_enthalpy` for closed thermal reactions. These additionally check
a shared thermal state and balance electronic and correction treatments
independently. See [reaction contracts](formal-reactions.md). A generic
`energy_difference` does not assert these reaction contracts.

## Export products for a separate consumer

Bundles retain the product declarations, expected quantities, dependencies,
analysis conditions, and symbolic expressions. Export leaves expressions as
recipes. Native input contains no result retrieval or numerical acceptance
guards. Legacy `build()`/`render()` can evaluate expressions using direct return
values; expressions requiring secondary products remain external recipes.
Use bundle export to preserve that handoff.

For named frequency products, construction requests Psi4's native `.vibrec`
output and assigns a distinct writer label for every producing call. This
preserves full vibrational and thermal information when a later calculation
clears global variables. The manifest's `native_outputs` declares each expected
filename template in the engine output directory; `{pid}` is filled by the
engine process. Use a separate output directory for each execution.
The native record includes full vibrational arrays, so its storage cost grows
with the system size.

Each native output binding identifies the expected quantity, top-level record
key, and encoding. Hessians are raw arrays. Other vibrational/thermal entries
are JSON-encoded QCElemental Datum strings in the reviewed build. A separate
consumer must decode those native records. The framework neither reads the
files nor claims they already exist. The native writer may also produce Hessian
side files. Property products remain available through the native calculation
output for the separate result consumer.

For [SAPT products](formal-sapt.md), `native_variables` declares each producer,
quantity, native QCVariable key, unit, and transient lifetime. These declarations
add no retrieval or file-writing code. A separate consumer must collect values
after that producer and before a later calculation can overwrite them.

## Discover only relevant evidence

Method support does not establish every secondary product. Product capabilities
are explicit, versioned facts within the same method/driver/reference/route and
option conditions. Inspect them with `discover_products()` or:

```sh
psi4-parser formal capabilities capabilities.json --section products \
  --name hf --driver frequency --product gibbs_correction --limit 3
psi4-parser formal schema request --definition ProductGoal --field name
```

MCP uses the same `formal_capabilities` query and `formal_schema` selection.
Method pages normally return `product_count`; use the products section or
`--include-products` for full product evidence. The bundled snapshot records
QCElemental `0.51.3` as provenance for the reviewed Datum serialization contract.
This is not a runtime pin or compatibility check; deployment is operator-managed.
