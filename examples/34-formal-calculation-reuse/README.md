# Share a calculation across scientific purposes

[build.py](build.py) requests a water spectrum and a Gibbs correction. Each
purpose names its optimization and frequency analysis independently, then
explicitly permits matching calls to be shared. Two additional energy goals
require separate calls by leaving `reuse_group=None`.

From the repository root, choose a new destination:

```sh
uv run python examples/34-formal-calculation-reuse/build.py \
  --destination /tmp/psi4-calculation-reuse
```

The script constructs inputs without executing Psi4. It uses the shared
source-audited contracts from [example 29](../29-formal-audited-capabilities/README.md),
or independently reviewed evidence passed with `--capabilities PATH`. HF/STO-3G
illustrates construction; it is not a recommended research treatment.

Inspect the [summary](saved/summary.json),
[shared proposal](saved/shared-proposal.json), and
[manifest](saved/bundle/manifest.json). Eight goals remain covered. Six logical
calculation goals use four actual calls: one optimization, one frequency
analysis, and two energy calls. Both named products retain the shared analysis's
provenance and native output binding. The manifest maps logical goal IDs to
implementing step IDs for a separate consumer.

The [separate proposal](saved/separate-proposal.json) uses
`PlanningPreferences(calculation_reuse="avoid")` and retains six calls. Scientific
model and route choices rank before sharing preferences. A preference cannot
authorize sharing or change a requested model. Counts do not estimate internal
SCF evaluations or execution time.

The [changed request](saved/changed-request.json) withdraws sharing permission
from one frequency goal. The same proposed graph is
[rejected](saved/changed-request-report.json) with `unauthorized_reuse`, even
though its method, geometry, analysis, and formulas are otherwise unchanged.

See [reuse contracts](../../docs/formal-reuse.md) for dependency and frame
translation, case boundaries, bounded search, compact explanations, and scope.
Sharing is an explicit choice to use one implementation; it does not establish
agreement between separately executed numerical calculations.
