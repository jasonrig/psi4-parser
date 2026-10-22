# Share calculation calls with explicit scientific permission

Set the same nonempty `CalculationGoal.reuse_group` on goals that may use one
matching calculation. The default is `None`: each such goal requires a separate
top-level driver call. A matching group permits sharing; it does not require it.
Keep separate calls when the scientific request needs separate implementations.

[Example 34](../examples/34-formal-calculation-reuse/README.md) constructs a
spectrum and Gibbs correction with a shared optimization and frequency analysis.
Two energy goals retain separate calls. All eight goals remain mandatory.

```python
from psi4_parser.formal import CalculationGoal

# `model` is an independently selected Model; `water` names a request input.
spectrum_geometry = CalculationGoal(
    id="spectrum_geometry",
    driver="optimize",
    geometry="water",
    models=(model,),
    reuse_group="one-water-optimization",
)
thermal_geometry = CalculationGoal(
    id="thermal_geometry",
    driver="optimize",
    geometry="water",
    models=(model,),
    reuse_group="one-water-optimization",
)
```

Sharing requires matching drivers, selected models and routes, settings,
constraints, requested properties, analysis conditions, and quantity types.
Geometry provenance must resolve to the same source. Copying the same
coordinates into another molecular input does not grant this equivalence.
References to a shared optimization are translated to its implementing step;
product frames, derivative frames, and symbolic expressions follow that mapping.
Matching full-basis subsystem constructions may also share pure geometry
metadata on these dependency paths. This alone never merges driver calls.

Every proposed graph is independently verified against the original request.
The verifier checks sharing permission even for manually supplied plans. Other
scientific contracts can require separate calls despite matching group labels;
the search can reject a shared graph and try a separate implementation.

## Rank permitted implementations

By default, `propose(request, catalog)` follows the request's model and route order,
then prefers fewer top-level calls within the selected scientific alternatives.
Use `PlanningPreferences(calculation_reuse="avoid")` to try separate calls first.
This is a soft preference. To require separate calls, leave `reuse_group=None`.
Neither preference adds a fallback model, grants sharing permission, or changes
scientific requirements.

The CLI option is `formal propose ... --call-reuse prefer` or `avoid`. MCP's
`formal_propose` accepts `preferences={"calculation_reuse": "avoid"}`. The Python
workspace accepts the same typed `PlanningPreferences` as `propose()`.

Search limits bound reuse alternatives and solver checks as well as model/route
choices. A failed shared candidate may leave another graph to check. Exhaustion
is not proof that no plan exists. Counts describe top-level calls, not internal
finite differences, SCF iterations, runtime, statistical independence, or accuracy.
One permitted implementation does not prove that separately executed jobs agree.

`finite_study()` namespaces groups per case. Sharing within a case cannot erase
another case's geometry history. Compose goals directly for cross-purpose reuse;
protocol names and a fixed protocol catalogue are unnecessary.

## Retain the mapping

Accepted `Proposal.reuses` lists each shared calculation and its logical goals.
Compact summaries return `calculation_count` and `shared_call_count`;
`explain(..., section="reuse")` pages through mappings with complete-record paths.
`choices` still records the model and route for every calculation goal.

The bundle manifest's `goal_coverage` maps every goal to implementing steps.
Native `formal_results` keys and product output bindings use actual step IDs;
they do not create duplicate values under logical alias names. A separate
execution/result consumer can use the manifest mapping. No results are read or
validated during construction.

An unsuccessful proposal can retain `last_candidate`, the checked graph matching
its last report's diagnostic paths. It is never an accepted `plan`. Workspace
summaries return its saved handle. `capability_status` describes application
evidence for represented calls separately from coverage and scientific findings.
Exact report replay requires its saved `limits`, request, catalog, and plan;
limits are part of verification identity.

These fields have backward-compatible defaults. An empty older manifest mapping
makes no coverage declaration. Reverify and export to obtain current evidence.
See [compact interfaces](formal-interfaces.md) and [the roadmap](formal-development.md).
