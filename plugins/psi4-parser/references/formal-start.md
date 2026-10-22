# From a scientific request to checked Psi4 input

Use this example for the shape of the workflow, then adapt its scientific
choices to the task. RHF/STO-3G here is a small API teaching example, not a
research recommendation. It uses the shared catalogue and requires no input
files or custom capability declarations.

Select the parser environment using [runtime and discovery](runtime.md). Save
the first Python block as `build_plan.py` and run it with that environment's
Python in a writable working directory. It creates a new `planning-demo`
directory; use a different name for another run.

## Translate the scientific task

For this example, the specified task is: “Starting with singlet neutral H2 at
0.85 angstrom, optimize at RHF/STO-3G with PK integrals, then request its harmonic
vibrational spectrum at that optimized geometry with the same model. Use
analytic derivative routes.”

| Scientific requirement | Request representation |
| --- | --- |
| Initial coordinates and electronic state | An exact molecule named `h2` |
| Fixed electronic model and route | One `Model`; `derivative_routes=("analytic",)` |
| Optimize before calculating frequencies | `opt` consumes `h2`; `freq` consumes `opt` |
| Keep optimization and frequencies at the same model | `SameModel` relation |
| Require the spectrum separately from the returned energy | `ProductGoal(name="harmonic_frequencies")` |

The request describes intended work, independently of any candidate plan. In a
real task, choose a defensible method, basis, state, and approximations using the
scientific context and appropriate sources. Record consequential assumptions;
resolve missing information that changes the scientific meaning. A proof of the
request's implementation cannot supply scientific requirements left out of it.

## Construct, check, and export

```python
from pathlib import Path

from psi4_parser.builder import ElectronicState, Molecule, molecule
from psi4_parser.formal import (
    CalculationGoal,
    Model,
    ProductGoal,
    SameModel,
    ScientificRequest,
    Setting,
    export_bundle,
    propose,
)

output = Path("planning-demo")
output.mkdir()
geometry = Molecule.from_xyz(
    "2\nH2; XYZ coordinates in angstrom\nH 0 0 0\nH 0 0 0.85\n",
    state=ElectronicState(charge=0, multiplicity=1),
)
model = Model(
    method="scf",
    basis="sto-3g",
    reference="rhf",
    settings=(Setting(name="scf_type", value="pk"),),
)
request = ScientificRequest(
    molecules=(molecule("h2", geometry),),
    goals=(
        CalculationGoal(
            id="opt",
            driver="optimize",
            geometry="h2",
            models=(model,),
            derivative_routes=("analytic",),
            reason="Supply the optimized geometry",
        ),
        CalculationGoal(
            id="freq",
            driver="frequency",
            geometry="opt",
            models=(model,),
            derivative_routes=("analytic",),
            reason="Calculate vibrations at the optimized geometry",
        ),
        ProductGoal(
            id="spectrum",
            calculation="freq",
            name="harmonic_frequencies",
        ),
    ),
    relations=(SameModel(calculations=("opt", "freq")),),
)
(output / "request.json").write_text(
    request.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
proposal = propose(request)
(output / "proposal.json").write_text(
    proposal.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
report = proposal.report
print("Proposal:", proposal.status)
if (
    proposal.plan is None
    or report is None
    or report.status != "proved"
    or report.scope != "scientific_request"
    or not report.request_complete
):
    raise SystemExit("Inspect planning-demo/proposal.json before continuing")

print("Verification:", report.status, report.request_complete)
print("Coverage:", [(item.goal, item.status) for item in report.coverage])
exported = export_bundle(proposal.plan, request, destination=output / "bundle")
print("Bundle:", exported.directory)
print("Input:", Path(exported.directory) / "inputs" / "workflow.dat")
```

With the matching implementation, the proposal is `constructed`, verification
is `proved` with `request_complete=True`, and all three goals are `covered`.
The bundle contains `scientific-request.json`, `calculation-plan.json`,
`capabilities.json`, `verification.json`, `manifest.json`, and
`inputs/workflow.dat`. The input carries the future optimized geometry to the
frequency call; no optimized coordinates are needed while planning.

Keep the bundle together. The manifest links goals to implementing steps,
expected products, native output bindings, symbolic recipes, and payload paths.
A covered spectrum goal establishes that the required frequency product is
requested in the right context. It does not establish that the optimization
will converge, that its stationary point is a minimum, or that the resulting
spectrum is accurate. Execution and interpretation of results are separate.

## Diagnose and repair an incorrect geometry dependency

This second script deliberately introduces a common implementation error into
the exported plan: frequencies consume the starting geometry. In an actual
repair, load the failing plan directly and retain the independently saved
request. Save this block as `repair_plan.py` and run it from the same directory
after `build_plan.py`. It needs no variables from the first script.

```python
import json
from pathlib import Path

from psi4_parser.formal import Plan, ScientificRequest, export_bundle, verify

output = Path("planning-demo")
request = ScientificRequest.model_validate_json((output / "request.json").read_bytes())
payload = json.loads(
    (output / "bundle" / "calculation-plan.json").read_text(encoding="utf-8")
)
frequency = next(step for step in payload["steps"] if step["id"] == "freq")
frequency["geometry"] = "h2"
broken = Plan.model_validate_json(json.dumps(payload))
(output / "broken-plan.json").write_text(
    broken.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
rejected = verify(broken, request=request)
(output / "rejected-verification.json").write_text(
    rejected.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
print("Rejected:", rejected.status, rejected.request_complete)
print("Capability coverage:", rejected.capability_status)
for diagnostic in rejected.diagnostics:
    print(diagnostic.path, diagnostic.code, diagnostic.message)
for obligation in rejected.obligations:
    if obligation.status != "proved":
        print(obligation.path, obligation.status, obligation.message)
        print([(value.name, value.value) for value in obligation.counterexample])

# Repair the implementation to match the unchanged scientific requirement.
frequency["geometry"] = "opt"
repaired = Plan.model_validate_json(json.dumps(payload))
checked = verify(repaired, request=request)
(output / "repaired-verification.json").write_text(
    checked.model_dump_json(indent=2) + "\n", encoding="utf-8"
)
if (
    checked.status != "proved"
    or checked.scope != "scientific_request"
    or not checked.request_complete
):
    raise SystemExit("Repair still rejected; inspect repaired-verification.json")
exported = export_bundle(repaired, request, destination=output / "repaired-bundle")
print("Repaired:", checked.status, checked.request_complete)
print("Bundle:", exported.directory)
```

The broken plan reports `violated` and `request_complete=False`, while
`capability_status` remains `supported`. Both calls are supported; the dependency
is wrong. Failed obligations report that `freq` must consume `opt`, with actual
geometry `"h2"` and expected geometry `"opt"`. This violation appears in the
plan's requirement and the requirement derived independently from the request.
It need not appear in `diagnostics`, so inspecting only that field misses it.
The repaired plan reports `proved` and exports to a new directory.

Never “repair” this by changing the request to permit frequencies on `h2` or by
removing the spectrum goal. For other failures, use the
[status and recovery guide](formal.md#propose-diagnose-and-export). A repeated
unknown with no new evidence is a reason to report the missing contract, not to
keep retrying or manufacture a supporting declaration.

## Adapt the example without loading every reference

Use selected fields and method/product conditions from
[targeted discovery](formal.md#discover-the-selected-runtime). For a saved
request, the [compact CLI/MCP workflow](formal.md#use-compact-planning-interfaces)
keeps large proof records in files and returns short summaries. For a new
scientific combination, choose the relevant task section from the
[planning skill](../skills/plan-calculations/SKILL.md#read-only-what-the-task-needs).
