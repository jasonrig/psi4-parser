# Construct equilibrium solvent calculations

Use `Environment(kind="ddx", ...)` on a model to request an equilibrium continuum
energy. `DDXSolvation` declares the PCM, COSMO, or screened LPB equation,
dielectric, and cavity choices. [Example 37](../examples/37-formal-solvation/README.md)
compares all three equations against one vacuum energy at a shared geometry.

```python
from psi4_parser.formal import DDXSolvation, Environment, Model, Setting

solvated = Model(
    method="hf",
    basis="cc-pvdz",
    reference="rhf",
    settings=(Setting(name="scf_type", value="PK"),),
    environment=Environment(
        kind="ddx",
        solvent="water",
        ddx=DDXSolvation(model="pcm", radii_set="uff", radii_scaling=1.1),
    ),
)
```

An omitted dielectric requests the named solvent's static value from the target
application. Supply `dielectric_constant` for an independently chosen
relative permittivity; the solvent string then serves as its label. The
permittivity must be at least one. Cavity radii use the declared UFF or Bondi
table and positive scale. The default scale is explicitly 1.1; changing tables
does not select a different scale automatically.

LPB additionally requires positive `screening_inverse_bohr`. Other equations
reject that field rather than silently ignoring it. Lowering converts screening
to inverse molecular length, as required by the reviewed native interface.
Capability conditions use the same converted settings. `Model.engine_settings`
uses bohr; `engine_settings_for("angstrom")` exposes the other native convention.

Numerical settings such as `ddx_lmax` belong in `Environment.settings`. They use
the DDX option module and require method-specific option evidence. Dedicated
solvent fields cannot be overridden by these settings or by `Model.settings`.
Formal calls explicitly select one solvent implementation or disable both for
vacuum calculations, within their independent native option scopes.

## Construct PCMSolver input

Use `Environment(kind="pcm", ...)` with `PCMSolverSolvation` for equilibrium
IEFPCM or CPCM energies. This is separate from the PCM equation implemented by
DDX. [Example 38](../examples/38-formal-pcmsolver/README.md) constructs named and
explicit media and checks their electronic solvation shifts.

```python
from psi4_parser.formal import Environment, PCMSolverSolvation

environment = Environment(
    kind="pcm",
    solvent="example-medium",
    pcm=PCMSolverSolvation(
        solver="cpcm",
        dielectric_constant=12,
        probe_radius_bohr=2.5,
        cpcm_correction=0.5,
        radii_set="uff",
        scale_radii=False,
        surface_area_bohr2=0.3,
    ),
)
```

Omitting both dielectric and probe radius selects native values by solvent name.
An explicit medium needs both fields because `Solvent = Explicit` disables that
lookup. Solvent names remain data, with no installed-table checks. Configuration
always declares atomic units: probe radius is in bohr and surface area in square
bohr, independently of the molecule's units. `scale_radii=True` applies the native
factor 1.2. `cpcm_correction` is the CPCM denominator correction and must be zero
for IEFPCM. These choices follow the
[PCMSolver input contract](https://pcmsolver.readthedocs.io/en/stable/users/input.html).

Lowering uses Psi4's `set_options({"PCM__INPUT": ...})` inside the calculation
scope. Building or preprocessing the input does not invoke the optional parser.
On execution, the native helper parses the block, selects its parsed filename,
and manages scratch files. The scope restores the filename, values, and changed
flags after success or failure. Each call receives its own block; an ambient or
earlier block cannot supply its cavity. The ordinary builder exposes the same
scoped text through `energy(..., pcm_input=...)` and the other driver helpers.

The current source catalog covers RHF/UHF HF/SCF energy inputs. ROHF, solvent
derivatives, and response need separate reviewed scientific contracts. Inspect
`PCMSolverSolvation` through the existing request schema discovery interface.

## Leave runtime deployment to the operator

Scientific/input evidence covers the requested equation and option choices.
`EnvironmentCapability` provides optional reference catalogues for radius tables
and solvent names. Missing installed tables or libraries never block planning.
The target operator resolves lookup, installation, compilation, and execution
failures. No dependency or version checks or warnings are emitted. Ghost and
dummy cavity centers currently require separate scientific construction contracts.

```sh
psi4-parser formal capabilities capabilities.json --section environments --name ddx
psi4-parser formal schema request --definition DDXSolvation --field screening_inverse_bohr
```

The bundled source catalog retains HF/SCF energy input contracts. Its reference
installation lacks pyddx, which does not prevent constructing DDX jobs for a
different target. The optional maintenance audit records reference component
metadata separately; planning never needs access to that or any target binary.
`runtime_policy="operator_managed"` records this boundary in reports and manifests.

## Check an electronic solvation shift

Use an `ExpressionGoal` with quantity meaning `electronic_solvation_shift` for
one solvated energy minus one vacuum energy. Both must have the same system,
geometry provenance, electronic state, and solvent-free computational treatment.
The verifier checks exact coefficients independently of the proposed algebra.
Nested scalar expressions and named primary-energy aliases preserve these rules.
Separately declared but numerically identical geometries do not establish common
provenance. Different dielectric choices remain distinct when call reuse is allowed.

This quantity is an equilibrium electronic energy shift. Thermal, non-electrostatic,
and standard-state terms need separately declared contracts before a Gibbs
solvation quantity can be claimed. Continuum and cavity suitability, numerical
convergence, and scientific accuracy remain assumptions.

Current formal lowering covers ordinary energy calls. Derivatives, optimizations,
response calculations, and custom per-atom cavity radii require further reviewed
contracts. Bundles retain the selected
environment and symbolic recipes; execution and result parsing remain separate.
