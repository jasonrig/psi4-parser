# Psi4 Inputs plugin

Write reusable Python scripts that plan calculations, create Psi4 input, or
validate, format, and convert existing input files. The plugin contains three skills:

- **plan-calculations**: preserve independent scientific intent, use capability
  evidence, propose or verify plans, and export checked construction bundles.
- **build-jobs**: discover the Python builder API and write a script for a job.
- **edit-inputs**: validate, format, and convert input using the CLI or reader API.

The skills defer to installed docstrings, source, command help, and matching
Psi4 documentation. API inventories and scientific option lists stay in their
original sources.

## Install

Requires an agent with local command execution, [uv](https://docs.astral.sh/uv/),
and Git. The runtime commands request Python 3.15; uv can download it when needed.
The host must support the package's dependencies, including Open Babel.

### Codex

```sh
codex plugin marketplace add jasonrig/psi4-parser
codex plugin add psi4-parser@psi4-parser
```

In the desktop plugin directory, add `https://github.com/jasonrig/psi4-parser`
as a repository marketplace, then install **Psi4 Inputs**. Start a new conversation
to load the skills.

For local testing, replace `jasonrig/psi4-parser` in the first command with the
absolute path to this checkout.

### Claude Code

```sh
claude plugin marketplace add jasonrig/psi4-parser
claude plugin install psi4-parser@psi4-parser
```

Start a new session. For local testing, use the absolute checkout path as the
marketplace source.

### Other clients

The package at `plugins/psi4-parser` uses the
[Agent Plugins format](https://agent-plugins.org/) and includes a Claude Code
manifest for compatibility. Clients that implement those formats can load the
same skills; their installation commands vary.

## Run the library

Installing this plugin copies its skills and references. It does not install a
Python environment or bundle the library source. The agent uses `uvx` to fetch
and cache the package and its dependencies directly from this repository:

```sh
uvx --python 3.15 --from 'git+https://github.com/jasonrig/psi4-parser.git@main' python build.py
uvx --python 3.15 --from 'git+https://github.com/jasonrig/psi4-parser.git@main' psi4-parser validate input.dat
```

This needs no checkout, `uv sync`, or dependency edits in the user's project.
The first invocation needs network access. The installed Python source is
available through `inspect.getfile()` and `inspect.getsource()` in that same
runtime. Repository guides and examples remain available on GitHub.

`main` follows the repository's development branch. Replace it with a commit or
tag for a repeatable workflow, using the same source for discovery and execution.
See [runtime and discovery](references/runtime.md) for details.

## Package layout

The repository's `.agents/plugins/marketplace.json` and
`.claude-plugin/marketplace.json` point to this directory. `plugin.json` describes
the portable package; `.claude-plugin/plugin.json` supplies Claude Code metadata.
Both hosts use the same skill and reference files.

## Plan checked inputs

Give the planning skill a scientific objective and molecular inputs. It uses
Python to describe the intended work, proposes a calculation plan, checks that
plan against the saved requirements and scientific/input contracts, then
exports Psi4 input with a proof report and manifest. For example, it can check
that a requested spectrum comes from a frequency calculation at the optimized
geometry with the specified electronic model.

Start with the packaged [request-to-export and repair example](references/formal-start.md).
It constructs every input from scratch and demonstrates a supported calculation
rejected for using the wrong geometry. The [planning skill](skills/plan-calculations/SKILL.md)
routes to task-specific guidance only when needed. Supported operations compose
into new workflows; a named protocol catalogue is not required.

Checks cover the requirements actually expressed: goal completeness, geometry
provenance, permitted model choices, quantity meaning, and exact formulas.
The agent must still choose scientifically appropriate models and express the
right requirements. Proofs depend on capability evidence and listed assumptions;
they do not establish convergence, numerical accuracy, or research suitability.
Execution, result parsing, and numerical acceptance are separate tasks. Target
binaries, optional dependencies, and versions remain operator-managed.

The shared catalogue is the default. Missing scientific coverage stays unknown;
caller declarations retain their assumption status. Use
[targeted discovery and recovery](references/formal.md) for method conditions,
named products, bounded searches, and unsupported work. For saved requests,
compact CLI/MCP operations return short summaries with handles and paged
explanations. CLI workspaces persist; copy MCP artifacts before server shutdown.

Retain the complete exported bundle, including goal coverage, native output
bindings, symbolic recipes, option policies, and payload paths for the separate result
consumer. Revise the source request or plan and re-export when changing a checked
job; editing emitted input alone does not update its proof. Use the matching
library source for discovery and construction, as described in
[runtime and discovery](references/runtime.md).
