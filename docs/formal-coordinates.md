# Require the intended geometry coordinates

Use `CoordinateValue` or `CoordinateRange` in `ScientificRequest.relations` to
state a bond length, angle, signed torsion, out-of-plane angle, or Cartesian
component independently from its prepared geometry. This catches a wrong scan
point even when a plan faithfully copies a wrongly prepared request geometry.

```python
from psi4_parser.builder import angstrom, distance
from psi4_parser.formal import CoordinateValue

required_distance = CoordinateValue(
    geometry="water",
    coordinate=distance("a1", "a2"),
    value=angstrom(1.1),
    tolerance=angstrom(1e-7),
)
```

Add this requirement to a request's `relations`. For a finite study, put
case-specific requirements in `StudyCase.relations` using the template's input
and goal IDs. `finite_study()` namespaces them together with the rest of each
case. Template relationships still apply to every case. A plan cannot bypass
these requirements by omitting its own assertions: independent coverage derives
them again during verification and export.

Discover only the needed fields with the matching runtime:

```sh
psi4-parser formal schema request --definition CoordinateValue \
  --field value --field tolerance
```

MCP exposes the same selection through `formal_schema`. These requirements use
the existing propose, verify, explain, and export operations.

`geometry` can name an input, optimization goal, or subsystem goal. A scalar
coordinate uses stable atom IDs, with the same order and conventions as builder
constraints. Distances and angles also accept reversed atom order; reversing
all four torsion atoms preserves the signed torsion. Out-of-plane plane order
retains its sign. Cartesian requirements select exactly one axis.

## Check inputs and future geometry differently

Resolved input coordinates are measured in angstroms or degrees. Length targets
and tolerances accept angstrom or bohr; angles accept degrees or radians.
Tolerances are explicit, nonnegative absolute differences. Invalid dimensions,
nonfinite converted quantities, and multi-axis scalar requirements are rejected
when the record is constructed.

An optimization's future coordinates are not measured from its placeholder
input. A matching frozen constraint propagates an established starting value or
interval. A matching bounded constraint supplies its declared interval, under
the assumption that successful optimization enforces it. A later freeze of an
unknown value stays unknown. Subsystems preserve their parent's coordinate
domains while changing real and ghost centers.

The entire established interval must fit the requested tolerance or range.
The solver searches for a permitted violating value, rather than checking an
interval midpoint. A counterexample means the declared construction does not
establish the requirement. An unconstrained future coordinate stays `unknown`.
Missing or dummy atoms, undefined coordinates, and inconsistent coordinate
premises also prevent a proof; the obligation explains the reason.

Absolute Cartesian requirements need `fixed_com=True` and
`fixed_orientation=True` to anchor the application frame. Internal coordinates
are independent of rigid translation and rotation.

## Preserve angular conventions

Torsion targets compare modulo 360 degrees. `CoordinateRange` uses an increasing
interval expanded by the explicit tolerance. For torsions it describes a
continuous angular arc: 170 to 190 degrees includes either representation of
180 degrees. A complete turn covers all torsions. Signed out-of-plane angles
use the bond from the second atom to the first and the oriented plane formed
by the second, third, and fourth atoms.

Future optimizer dihedral bounds outside the canonical -180 to 180 degree
interval currently remain unknown: the framework needs an additional contract
for the optimizer's branch tracking. This limit does not prevent checking a
known input or a frozen known torsion across the signed-angle branch cut.

## Interpret the proof scope

The retained solver query encodes measured input values or declared constraint
intervals, explicit units, and the required tolerance. Proofs and counterexamples
are replayable. Geometry measurement and unit conversion use floating-point
arithmetic; this is not a certified error bound for trigonometric computation.
The report and manifest retain that assumption. Choose a tolerance appropriate
to input preparation and units.

Successful construction establishes the encoded coordinate contract conditional
on the stated engine behavior. It does not promise optimizer convergence,
scientific accuracy, or numerical agreement of a completed calculation. No
runtime output guards, calculation execution, or result parsing are added.
See [example 30](../examples/30-formal-coordinate-scan/README.md) and the composed
[counterpoise study](../examples/25-formal-counterpoise-study/README.md).
