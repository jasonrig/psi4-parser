# Construct PCMSolver energies and solvation shifts

This example builds a vacuum energy, a named-water IEFPCM energy, and explicit
dielectric IEFPCM/CPCM energies at one geometry with one electronic treatment.
It checks three electronic solvation shifts and retains an equation comparison
as a symbolic expression. The chosen models illustrate construction; they are
not a recommended research protocol.

```sh
uv run python examples/38-formal-pcmsolver/build.py --destination /tmp/psi4-example-38
```

The eight goals produce four native driver calls. Shared scientific contracts
apply through `propose(request)` and default export, with no version profile or
catalogue selection. The source rules cover RHF/UHF HF/SCF energy construction.
No Psi4 or PCMSolver installation
is needed to build this bundle, and component versions are unpinned. Installation,
native solvent lookup, compilation, and execution failures belong to the target
operator. Construction emits no deployment checks or warnings.

`PCMSolverSolvation` declares equilibrium IEFPCM/CPCM, cavity table and scaling,
surface element area, and explicit dielectric/probe choices. The block always
uses atomic units, independently of molecular coordinate units. A named solvent
uses its native dielectric/probe table; an explicit medium needs both fields.
The example fixes the same cavity and discretization for its equation comparison.

Generated input applies `PCM__INPUT` inside each calculation's option scope.
Psi4 invokes its PCMSolver parser when the input executes, manages the helper's
scratch files, and restores the parsed filename and other captured options after
the call. Preprocessing does not need PCMSolver for this form of input.

The saved [summary](saved/summary.json) and [bundle](saved/bundle/manifest.json)
retain the request, checked plan, proof report, native input, and symbolic recipes.
The [damaged request](saved/wrong-weight-request.json) is internally consistent
but incorrectly doubles one solvated energy; independent solvation algebra
rejects it. No calculations run and no numerical outputs are parsed or validated.

Current contracts cover ordinary equilibrium energies with real cavity nuclei.
Derivatives, nonequilibrium response, custom cavities, and full Gibbs solvation
cycles require further scientific contracts. Read the
[solvent guide](../../docs/formal-solvation.md) and
[PCMSolver input documentation](https://pcmsolver.readthedocs.io/en/stable/users/input.html).
