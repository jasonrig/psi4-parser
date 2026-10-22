# Isolate native options for every calculation

[build.py](build.py) requires an MP2 energy followed by an HF energy on one H2
geometry, then exports their symbolic difference. The first call explicitly
uses conventional MP2 with `QC_MODULE=OCC`; the second starts from native defaults
and applies its own HF model. The exported calls cannot inherit that routing
choice or unrelated native options from the caller.

From the repository root, choose a new directory:

```sh
uv run python examples/33-formal-option-isolation/build.py \
  --destination /tmp/psi4-option-isolation
```

The script constructs inputs without executing Psi4. It uses shared source-audited
contracts from [example 29](../29-formal-audited-capabilities/README.md), or separately
reviewed evidence supplied with `--capabilities PATH`. The electronic models and
STO-3G basis illustrate the API, rather than a research recommendation.

Inspect the [summary](saved/summary.json), [request](saved/bundle/scientific-request.json),
and [manifest](saved/bundle/manifest.json). The manifest records
`option_policy="native_defaults_per_calculation"`. The [input](saved/bundle/inputs/workflow.dat) contains a standalone
native option helper, with no parser-library runtime dependency.
The summary and manifest also record
`namespace_policy="restore_after_calculation"`: cleanup restores the IO
namespace captured at call entry, including after failure. Native molecule
declarations may change the namespace before that scope begins.

Each call captures raw option values and changed flags, resets options, applies
the declared model, and restores the captured state on success or failure.
Resetting to native defaults also avoids trying to assign an empty native
`QC_MODULE` default through a setter that rejects it.

Separate [development tests](../../tests/test_formal_isolation.py) seed hostile
global and module-local settings and observe mocked drivers through the real
native option library. They cover arrays, unflagged nondefault values, additional
native module scopes, failure cleanup, and a skipped nested branch. Actual small
calculations are covered by the separate native reference/product tests.

See [option isolation](../../docs/formal-isolation.md) for the ordinary builder's
opt-in API, module coverage, resource settings, and remaining assumptions.
