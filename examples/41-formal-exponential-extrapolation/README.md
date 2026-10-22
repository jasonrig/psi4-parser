# Combine exponential reference and correlation limits

This example constructs two HF reference-limit estimates: an exponential in the
D/T cardinal number and an exponential in the square root of the T/Q cardinal
number. Both combine with one inverse-cube MP2-minus-HF correction estimate.
The decay constants illustrate the two models and are not protocol recommendations.

```sh
uv run python examples/41-formal-exponential-extrapolation/build.py --destination /tmp/psi4-example-41
```

`ReferenceExtrapolationStudy` independently declares the basis family, point
models, decay constant, coordinate, and coefficient-error bound. The common
`extrapolation_expansion()` helper constructs rounded rational weights that sum
exactly to one. Verification independently encloses the exponential using
rational Taylor bounds, square-root intervals, and outward rounding. A successful
check certifies an absolute weight error of at most `1e-18` in this example.
The physical decay law, reference-state consistency, asymptotic regime, and
floating-point result evaluation remain assumptions or separate responsibilities.

The [request](saved/request.json) has 16 mandatory goals. Explicit sharing groups
permit the matching HF evaluations to serve multiple purposes, leaving five
native driver calls. Each composite must contain one net electronic energy at
the same geometry. Repeating the reference or mixing geometry provenance fails
that contract. All energies and comparisons remain symbolic during construction.

The [damaged request](saved/wrong-weight-request.json) changes an exponential
expression to `-E(low) + 2*E(high)` while retaining the independently chosen decay
model. Its weights sum to one and its requested algebra is self-consistent;
the exponential coefficient contract rejects it.

The [bundle manifest](saved/bundle/manifest.json) retains both exponential recipes,
the inverse-power recipe, rational weights, goal coverage, and payload hashes.
The native input uses ordinary HF/MP2 calls and explicit conventional MP2 routing.
No CBS helper evaluates energies, no calculation is executed, and no output is
collected or validated by this example. See the
[basis-limit guide](../../docs/formal-extrapolation.md) for the certificate and scope.
