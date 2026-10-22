# Construct basis-limit energy and correction estimates

Use `extrapolation_expansion()` to require two target/reference energy pairs and
an explicitly chosen inverse-power correction model. Its returned goals compose
with optimizations, scalar expressions, reactions, and finite studies. Every
point uses one geometry provenance and a uniform orbital basis.

[Example 35](../examples/35-formal-basis-extrapolation/README.md) constructs MP2
minus HF corrections at D, T, and Q cardinal numbers. It retains DT and TQ
estimates, a finite-QZ HF plus TQ correction estimate, and a symbolic comparison.
No calculation or result evaluation occurs during construction.
[Example 41](../examples/41-formal-exponential-extrapolation/README.md) adds
exponential HF reference limits and combines them with an inverse-power correction.
Both workflows use `extrapolation_expansion()`.

## Declare the model independently

`ExtrapolationStudy` requires `geometry`, a common basis `family`, an explicit
positive integer `power`, and `low`/`high` `BasisCorrectionPoint` records. Each
point fixes its basis name and cardinal number and supplies permitted target
`models` and subtracted `reference_models` in preference order. The helper
creates four energy goals, two energy differences, and a final expression.
It never changes a supplied model's basis to make it fit a point.

The correction model is:

```text
C(X) = C(infinity) + A / X**p
C(infinity) = [H**p * C(H) - L**p * C(L)] / [H**p - L**p]
```

For D/T and `p=3`, the exact coefficients are `-8/19` and `27/19`.
`InversePowerExtrapolation` records the family, point references, bases, cardinals,
and exponent separately from the expression's coefficients. Verification derives
the expected algebra from that model. Matching a caller-supplied `EnergyFormula`
alone cannot establish correct extrapolation weights.

Every point must expand to exactly one target electronic energy minus one
reference electronic energy. HF subtraction defines a correlation estimate;
another explicitly chosen reference method defines a method correction. The
four calls must retain the same geometry. Each point preserves reference,
declared core treatment, angular representation, ECPs, and environment across
its target/reference pair. Across points, target and reference treatments each
remain fixed while their basis names vary. Arbitrary method changes, numerical
setting changes, and per-center orbital overrides do not satisfy this contract.

## Supply basis membership evidence

`BasisCapability.sequence` supplies a `BasisSequence(family=..., cardinal=...)`.
The basis entry's evidence supports this membership as well as its element and
dimension information. Family names distinguish augmentation, core/valence,
relativistic, and other variants; the verifier does not infer membership from
a familiar-looking basis name. Missing membership remains unknown. Contrary
family or cardinal evidence is a violation.

Explicit fitting bases may vary with the orbital cardinal. Each target/reference
fitting role must retain one evidenced family across the points, with the
corresponding cardinal at each point. All other model choices remain fixed.
Method/driver/reference, options, element coverage, and dimensions still need
their ordinary scientific/input contracts. Component availability is not checked.

The bundled source catalog records `cc-pvXZ` memberships for cc-pVDZ,
cc-pVTZ, and cc-pVQZ, with H–Ar dimensions. Its source review binds the native
D/T/Q convention and basis files. Reference compilation limits and version/build
labels do not constrain construction for another machine. Loading a catalog
does not inspect an installation. Even relationship-only verification of these recipes
requires a catalog for their basis claims.

## Compose and hand off

The output has meaning `basis_limit_correction`, in hartree. Add it to an
explicit electronic reference through an `ExpressionGoal` with meaning
`electronic_energy`. The finite reference basis remains explicit in that
estimate. Corrected molecular expressions must retain common geometry provenance.
Their underlying electronic-energy coefficients must sum to one, so a correction
alone cannot be relabelled as a total electronic energy.
Existing thermal and reaction contracts still check their own conditions and
bookkeeping when composed with these expressions.

`ExtrapolationStudy.reuse_group` optionally grants the ordinary permission to
share matching point calculations. It defaults to null. Using the same explicit
group across DT and TQ studies can share their common T calculations while
preserving both point differences and recipes. `finite_study()` translates all
recipe references and confines sharing to each case. See [reuse contracts](formal-reuse.md).

Export retains recipes in manifest `expressions`, alongside exact coefficients,
dependencies, goal mappings, and expected quantities. Native inputs contain the
point calculations; the expressions remain symbolic for a separate consumer.
No output files are parsed and no extrapolated values are accepted or rejected.

For compact discovery, select `ExpressionGoal.extrapolation` in the request
schema and query the relevant basis entries. The recipe also appears on
`Combination` in the plan schema. New fields default to null for old records;
reverify and export to obtain current rule and catalog identities.

The chosen inverse-power law, exponent, consistent SCF state, and asymptotic
regime remain scientific assumptions. A construction proof does not establish
convergence to a physical basis limit or numerical accuracy. This contract covers
positive integer powers from 1 through 16 and increasing cardinals from 1 through
32. Noninteger inverse powers, fitted nonlinear schemes, and per-center series
need additional contracts. The underlying
[reviewed Psi4 formula](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/driver_cbs_helper.py)
and [source review](../src/psi4_parser/formal/catalogs/psi4/README.md)
document the present scope.

## Construct exponential HF reference estimates

Pass `ReferenceExtrapolationStudy` to `extrapolation_expansion()`. Its two
`BasisEnergyPoint` records supply basis names, cardinals, and permitted HF/SCF
models. Choose `alpha` explicitly as a `Rational`; no empirical default is
inferred. `shape="cardinal"` uses `f(X)=X`; `shape="sqrt_cardinal"` uses
`f(X)=sqrt(X)`:

```text
E(X) = E(infinity) + A exp(-alpha f(X))
r = exp(alpha * (f(H) - f(L)))
E(infinity) = -E(L)/(r-1) + r*E(H)/(r-1)
```

`ExponentialExtrapolation` records the family, points, decay choices, and
`coefficient_digits` separately from the expression. Its result has meaning
`basis_limit_reference_energy` in hartree. Each point must expand to one HF/SCF
electronic energy with weight one and a uniform orbital basis. Both points
retain one geometry provenance and treatment, varying evidenced basis names.
Ordinary method/input evidence and fitting-family checks also apply. A correlated
total, excitation, interaction, or arbitrary difference is not an HF reference
point. Missing basis-family/cardinal evidence remains unknown.

The exact exponential weights are generally irrational. Construction rounds the
low weight using a private decimal context and defines the high weight as its
exact rational complement. Verification independently uses positive rational
Taylor terms with a geometric remainder, range reduction, outward rounding, and
integer square-root bounds. It requires the complete exact-weight enclosure to
fit within `10**(-coefficient_digits)` of the supplied rational weight. Weights
must sum exactly to one and use only the declared points. An incorrect formula
can fail even when it matches the request's ordinary algebra. An inconclusive
coefficient enclosure remains unknown.

The default bound is `1e-15`, with 6 through 30 decimal digits supported. Alpha is
positive and at most 32; its reduced numerator and denominator each use at most
256 bits. These limits bound certificate arithmetic. The checker uses 64 Taylor
terms, a 320-place outward grid, and 160-place square-root bounds. The resulting
two-point energy-expression error is bounded by that coefficient error times
`abs(E(H)-E(L))`; construction does not evaluate those energies or establish a
physical accuracy target.

Combine one reference estimate with a `basis_limit_correction` through an
`ExpressionGoal` with meaning `electronic_energy`. It must retain one net energy
and one geometry provenance. Explicit reuse groups may share matching HF calls
between reference and correction studies; different basis members remain
different calls. Native calls and formula recipes remain in checked exports.

The forms follow the reviewed
[Psi4 CBS source](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/driver_cbs_helper.py)
(`scf_xtpl_helgaker_2` and `scf_xtpl_karton_2`). This framework constructs ordinary
energy calls and its own symbolic recipes. The linear-cardinal formula uses the
explicit cardinal difference, including nonadjacent pairs; it does not invoke
the native adjacent-pair helper. The decay law, exponent suitability, asymptotic
regime, reference-state consistency, and floating-point evaluation remain
scientific assumptions or responsibilities of a separate consumer. Fitted
three-point models and nonlinear energy-dependent formulas remain open.
