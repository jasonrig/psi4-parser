# Construct closed electronic and thermal reactions

Use `reaction_expansion()` to compose species calculations and an exact
product-minus-reactant expression. Supply explicit molecular inputs, electronic
states, allowed models, and nonzero integer or `Rational` coefficients. Negative
coefficients consume species; positive coefficients produce them. A species can
use an input geometry or a preceding optimization goal.

`ReactionStudy.quantity` selects the molecular quantity to combine:

| Molecular quantity | Final expression meaning |
| --- | --- |
| `electronic_energy` (default) | `reaction_energy` |
| `zero_k_enthalpy` | `reaction_zero_k_enthalpy` |
| `thermal_energy` | `reaction_thermal_energy` |
| `enthalpy` | `reaction_enthalpy` |
| `gibbs_free_energy` | `reaction_gibbs_free_energy` |

Compose the returned goals with molecular declarations and optional preceding
optimizations in a `ScientificRequest`. The expansion uses ordinary calculation,
product, and expression goals; it composes with `finite_study()` and does not
require a fixed protocol catalogue. `max_species` bounds expansion.

## Specify each species' thermal analysis

Thermal participants require `ReactionThermochemistry`. For example, this creates
explicit ideal-gas RRHO analysis settings for a species with rotational symmetry
number 2:

```python
from psi4_parser.formal import (
    ReactionThermochemistry,
    ThermalConditions,
    VibrationalAnalysis,
)

thermal = ReactionThermochemistry(
    analysis=VibrationalAnalysis(
        conditions=ThermalConditions(
            temperature_kelvin=298.15,
            pressure_pascal=101325.0,
        ),
        rotational_symmetry_number=2,
    ),
    derivative_routes=("analytic",),
)
```

Attach it through `ReactionParticipant.thermochemistry`, then select a thermal
quantity in `ReactionStudy`. Electronic-only reactions omit thermochemistry;
thermal reactions require it for every species. Missing configuration raises
`ValueError` during expansion. Inconsistent declared thermal states are diagnosed
by verification.

All species must share temperature, pressure, treatment, and projection choices.
Rotational symmetry numbers remain species-specific: CO can use 1 while O2 and
CO2 use 2. Each number is an explicit scientific input, including isotope effects.
The framework does not infer it from an uncomputed optimized geometry.
These contracts use the full explicit analysis context even for zero-point totals.

## Choose native totals or explicit hybrid models

With `ReactionThermochemistry.models=()` (the default), a single frequency call
uses the participant's permitted models and supplies its native thermal total.
No redundant electronic single point is added.

Supplying correction models requests a hybrid construction. The participant's
models supply a separate electronic energy. The thermochemistry models supply
a full frequency analysis and the corresponding named correction at the same
species geometry. An explicit molecular expression combines those two quantities
before the reaction expression uses it. This retains both model choices rather
than relabelling electronic energy as a thermal total.

Every permitted model or derivative alternative is a scientific authorization.
Selection remains bounded and every candidate needs exact capability evidence,
including the named thermal products. An unsupported or uncovered route does not
authorize a new fallback.

## Check conservation and computational treatments

The verifier expands nested scalar formulas with exact rational arithmetic.
Real nuclei, isotope labels, explicit masses, and charge must balance.
Ghost and dummy centers do not count as real nuclei. Unspecified isotope/mass
defaults remain distinct from explicit choices.

Every electronic-energy treatment must separately balance nuclei and charge.
Thermal reactions also balance every correction treatment independently. A
correction basis changed on only one side is rejected even when the electronic
models agree. Species-specific RHF/UHF/ROHF references remain explicit and may
differ; other normalized model choices distinguish computational treatments.

Thermal reaction terms must be molecular totals of the required meaning or
nested reactions of the same meaning. A raw electronic energy cannot replace one
species' Gibbs total. Each corrected molecular expression separately needs one
net electronic energy, one net matching correction, and common geometry, system,
electronic state, and full analysis provenance. See
[product contracts](formal-products.md) for those checks.

## Export for a separate consumer

The manifest retains products, exact symbolic recipes, dependencies, thermal
conditions, assumptions, and native frequency output bindings. Each frequency
call receives a distinct writer label so later calls cannot erase its transient
thermal data. Input construction performs no result retrieval or parsing.

[Example 32](../examples/32-formal-thermal-reaction/README.md) constructs native
and hybrid Gibbs reactions after species optimizations. Its separate rejected
request has correct stoichiometry and exact algebra but mixes temperatures.
[Example 27](../examples/27-formal-reaction/README.md) covers electronic reactions.

The current thermal treatment is native ideal-gas RRHO. Suitability of the model,
stationarity, imaginary-mode handling, successful execution, and numerical
accuracy remain assumptions. External particle reservoirs, concentration/solution
standard-state conversions, other thermal models, reaction pathways, and kinetic
feasibility need additional contracts. An ordinary `energy_difference` can retain
a requested comparison without claiming closed-reaction conservation or a shared
thermal state.
