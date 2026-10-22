# Apply each calculation's declared options independently

Formal construction starts each calculation from native Psi4 option defaults,
applies its model, analysis settings, and constraints, then restores the captured
option state. An ambient module-local `SCF.REFERENCE` or a preceding call's
`QC_MODULE` cannot silently change the declared model.

The emitted helper uses Psi4 and the Python standard library. The generated input
requires no `psi4_parser` installation. Export records
`option_policy="native_defaults_per_calculation"` with backend version
`psi4-builder/8`. An absent policy parses as null and makes no isolation claim
for older bundles.

## Preserve values and changed flags

Psi4 combines global and module-local settings using both their values and
changed flags. Isolation captures the raw state of both scopes, resets options,
and restores the captured state in cleanup even if setup or a driver raises.
Restoring only values or only changed options would be insufficient: a caller can
have a nondefault raw value whose changed flag has been revoked.

Restoration resets native defaults before reapplying saved differences and changed
flags. This avoids assigning clean defaults that native setters reject, such as
the empty `QC_MODULE` value. The selected option module is restored at each call's
boundary; molecule construction and subsequent option queries can independently
change that selection.

The helper also restores the native IO namespace captured at calculation entry,
including after failure. The manifest records
`namespace_policy="restore_after_calculation"`. Psi4's molecule declarations may
set a namespace before the helper begins; this policy preserves the call-entry
namespace rather than the namespace before the whole input. This matters for
SAPT, whose driver switches namespaces while preparing its monomers.

PCMSolver input is applied through `PCM__INPUT` inside the scope. Its native
helper selects a parsed-input filename, which is captured/restored with the PCM
module's options. The helper's scratch-file lifecycle remains Psi4-managed.
The ordinary builder's `pcm_input` argument enables this scope even without
additional `local_options`; it is never forwarded to the chemistry driver.

The supported scopes include all native globals, modules in Psi4's public option
catalogue, ADC/DDX/F12 from the reviewed native source, modules explicitly named
in local option blocks, and the module selected at call entry. This coverage is
tested in a reviewed reference build. Target API availability and deployment
remain operator-managed, without construction-time checks or warnings.

Opaque option values that the native getter cannot preserve are rejected before
the calculation starts. Unlisted third-party plugin scopes or plugin-owned state
require additional integration. Memory, thread counts, paths, engine objects, and
other process resources retain their separately supplied configuration. Use one
coordinator for a Psi4 process; concurrent mutations of its options are outside
this contract.

## Opt in through the ordinary builder

Formal lowering always enables isolation. Ordinary builder helpers keep ambient
options available by default. Enable isolation when `local_options` completely
declares the options needed by the call:

```python
from psi4_parser.builder import (
    ElectronicState,
    Molecule,
    compose,
    energy,
    molecule,
    options,
    render_job,
)

geometry = Molecule.from_xyz(
    "2\nHydrogen\nH 0 0 0\nH 0 0 .8\n",
    state=ElectronicState(charge=0, multiplicity=1),
)
h2 = molecule("h2", geometry)
job = compose(
    h2,
    energy(
        "scf",
        molecule=h2.ref,
        isolate_options=True,
        local_options=(options(basis="sto-3g", reference="rhf", scf_type="PK"),),
    ),
)
source = render_job(job)
```

The same keyword is available on `gradient()`, `hessian()`, `optimize()`,
`frequency()`, `properties()`, and the typed `Calculation` record. Move required
persistent option components into `local_options` for an isolated call, because
the call establishes its own native baseline. This setting remains builder
configuration and is never forwarded as a Psi4 driver argument.

## Retain evidence and assumptions

Resetting options does not establish application support. For example, omitting
`SCF_TYPE` still leaves support unknown under a catalog whose only positive case
requires an explicit `SCF_TYPE=PK`. Keep the independent request, exact catalog,
and all [capability conditions](formal-capabilities.md).

[Example 33](../examples/33-formal-option-isolation/README.md) exports an MP2/HF
comparison with independent scopes and a structured manifest policy.
[Development tests](../tests/test_formal_isolation.py) use the actual native option
library to check hostile globals/locals, arrays, unflagged nondefault values,
additional modules, skipped branches, and deliberate failure. Separate reference
and product tests run small calculations. The public framework constructs inputs;
it has no execution or numerical result-acceptance API.

This is a tested lowering contract. Artifact hashes bind the selected inputs,
rules, and evidence; they do not formally prove the compiler or promise that an
application call will converge or achieve scientific accuracy.
