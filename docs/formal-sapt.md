# Construct explicit SAPT interaction plans

Attach `SAPTAnalysis` to an energy goal to require the native SAPT interaction
return and its fragment, basis, and induction choices. It composes with finite
studies and scalar comparisons. [Example 36](../examples/36-formal-sapt/README.md)
combines dimer- and monomer-centered SAPT0 with a counterpoise HF comparison.

```python
from psi4_parser.formal import CalculationGoal, SAPTAnalysis

# `model` is an independently selected, explicitly configured SAPT Model.
interaction = CalculationGoal(
    id="interaction",
    driver="energy",
    geometry="complex",
    models=(model,),
    sapt=SAPTAnalysis(
        fragments=("a", "b"),
        basis="dimer",
        coupled_induction=True,
    ),
)
```

Prepare the molecular assembly with explicit overall and fragment states.
`fragments` names the first two real fragments in native A/B order. RHF requires
closed-shell monomers. Open-shell SAPT requires the high-spin complex; a spin
coupling that is otherwise possible does not establish the native SAPT state.
ROHF requires an explicit `coupled_induction=False`, so native substitution of
uncoupled induction cannot silently change the request.

An optional `midbond_fragment` must identify the third fragment and contain only
ghost centers, with charge zero and multiplicity one. Midbond functions require
dimer-centered bases. Real monomers cannot contain ghost centers under this
contract. The source's internal C1/fixed-frame preparation occurs on a private
clone; absolute coordinate requirements still use the ordinary frame contracts.

The primary return has meaning `interaction_energy`, in hartree. It cannot be
labelled as a molecular electronic total or used as one in a closed reaction.
Use `energy_difference` for an explicitly requested comparison with another
interaction treatment. Method, basis, and reference choices remain independent
scientific inputs.

## Discover fitting and method evidence

Supply explicit `AuxiliaryBasis` entries for `df_basis_sapt` and `df_basis_elst`.
DF SCF also requires `df_basis_scf`. The bundled snapshot supports reviewed
cc-pVDZ/TZ/QZ pairings with the corresponding RI and JKFIT definitions. Its
method conditions specify the exact orbital/fitting names and SCF algorithm.
Missing or mismatched pairings remain unknown; the planner does not invent
fitting defaults or infer their quality from their names.

The source-pinned snapshot covers fifteen legacy HF-SAPT method spellings,
including scaled, higher-order, CCD-dispersion, and delta-MP2 variants. Only
SAPT0 has positive open-shell reference cases. Reviewed monomer-centered support
is restricted to RHF SAPT0. Induction and midbond coverage are explicit features.
Delta-MP2 cases require the reviewed PK/CONV/OCC route. Other combinations need
separate evidence. These are application capabilities, not a protocol catalogue.

The audit records five orbital bases and nine fitting-role entries. RI coverage
extends through Ar; these JKFIT files omit He, Li, Be, Na, and Mg within that
range. Fitting sets are not advertised as orbital bases. Compilation limits and
native component availability are left to the execution operator.

For compact discovery, select `CalculationGoal.sapt` in the request schema and
query matching methods/products. Product pages retain producing features as
well as conditions and component requirements. A SAPT proof requires a catalog
even in relationship-only mode. Ordinary `verify(plan)` continues to provide its
legacy scope for plans without these specialized requirements.

## Require components without collecting results

Named products are `sapt_total_energy`, `sapt_electrostatics`, `sapt_exchange`,
`sapt_induction`, and `sapt_dispersion`. Request them with `ProductGoal`; each
needs producing-case evidence. A complete component sum requires all four
components with coefficient one from a single producing call. The solver links
this partition to the native interaction return. Self-consistent wrong sums
cannot pass solely because the request and proposed algebra agree.

`Report.native_variables` and manifest `native_variables` declare native scalar
QCVariable keys, units, quantity IDs, producers, and lifetime. These declarations
are transient: a later calculation can replace native state. Export adds no
snapshot, result retrieval, numerical validation, or collection code. A separate
consumer must handle application output or collect runtime values before state
changes. The input-only planning workflow cannot promise durable component data.

Basis and induction choices remain attached to expected quantities. Finite
studies retain each case's context. Explicit calculation reuse requires matching
SAPT choices as well as models and geometry; monomer- and dimer-centered calls
cannot be merged just because their `Model` records match.

## Native input state and scope

Backend `psi4-builder/8` restores the default scratch namespace captured at each
call's entry, as well as native option values and flags. The manifest records
`namespace_policy="restore_after_calculation"`. Native molecule declarations may
select a namespace before that scope starts. Scratch paths, file preservation,
process resources, and concurrent mutation remain separate concerns.

The contracts establish requested construction under the supplied application
evidence. Perturbative suitability, convergence, basis adequacy, and numerical
accuracy remain assumptions. SAPT(DFT), spin-flip SAPT, F-SAPT partitions,
charge-transfer special drivers, and empirical-dispersion variants need their
own reviewed contracts and lowering. See [the source review](../src/psi4_parser/formal/catalogs/psi4/README.md)
and [development roadmap](formal-development.md).
