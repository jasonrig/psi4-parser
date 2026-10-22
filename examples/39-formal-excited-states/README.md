# Construct root-resolved response calculations

This example constructs HF/RPA, HF/TDA, and PBE/RPA singlet responses for one
formaldehyde geometry. It requests excitation energies, an excited-state total,
oscillator strength, and a length-gauge electric transition dipole for explicit
roots. These choices illustrate construction and are not a recommended protocol.

```sh
uv run python examples/39-formal-excited-states/build.py --destination /tmp/psi4-example-39
```

The 22 mandatory goals produce three native driver calls through the default
shared scientific contracts. No Psi4 binary, per-version profile, or dependency
inspection is needed. Installation and execution remain operator-managed.

Psi4's `energy('td-hf')` return is the ground-reference energy. The excitation and
excited-state total are separate `ProductGoal` declarations. A native total equals
the producing reference plus the excitation for the same ordered root. Independent
relations prove that identity, while the deliberately
[damaged request](saved/wrong-weight-request.json) doubles a reference and fails
even though its requested algebra is internally consistent.

Root numbers refer to energy order within the requested spin/irrep allocation.
Comparing root one across RPA/TDA is an explicit numerical comparison, not a
claim that it tracks the same physical state. Stability, convergence, physical
accuracy, and irrep-specific orbital-space suitability remain assumptions.

The [manifest](saved/bundle/manifest.json) records 15 transient native variable
bindings. Transition dipoles retain Psi4's native `(1, 3)` row layout and producer
frame. The separate execution consumer must collect these values after their
producer and before a later call overwrites them. The generated input contains
no QCVariable retrieval, collection writer, or output validation. Expressions
depending on secondary products remain symbolic recipes.
Transition-moment requests enable native `E_TDM_LEN` printing for a separate text
parser. Full-precision variable collection remains the separate consumer's
responsibility at the producer boundary.

Read the [excited-state contracts](../../docs/formal-excited-states.md) for
root allocation, spin sectors, supported kernels, response equations, and limits.
