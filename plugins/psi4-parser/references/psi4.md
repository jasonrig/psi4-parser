# Psi4 methods and options

The parser API explains how to construct input. Psi4's own documentation
explains the methods, options, molecular syntax, and their scientific meaning.
Choose documentation from the user's requested reference or available source.
Input construction requires no target binary, installed library, dependency
inspection, or version discovery.

1. When the user specifies a Psi4 release or source revision, consult that
   reference. Otherwise, use the available checkout or maintained upstream source
   for the method or option being constructed. Record the source reference when
   it matters to a scientific choice; it does not constrain the execution host.
2. Prefer the `.rst` documentation under `doc/sphinxman/source/` and the relevant
   implementation at the same source reference. The
   [upstream source directory](https://github.com/psi4/psi4/tree/master/doc/sphinxman/source)
   is the entry point; replace `master` with a user-specified ref when supplied.
3. Read local RST files when the relevant checkout is available. Otherwise, fetch
   their raw contents from GitHub. Follow references to included RST files,
   option definitions, or driver source at that same ref as needed.
4. Use the rendered manual only when the needed information is unavailable or
   unclear in the sources, choosing the matching documentation version. The
   [development manual](https://psicode.org/psi4manual/master/index.html) tracks
   `master`.

Search a local checkout's documentation with `rg` and read the relevant sections.
Keep links or paths to the sources used for consequential method and option
choices. The optional parser
[compatibility record](https://github.com/jasonrig/psi4-parser/blob/main/compatibility/psi4.json)
is repository metadata describing its audited syntax target. Consult it at the
recorded parser commit when available; installed packages may omit repository
files. If it is absent or the commit is unknown, continue with the installed API
and the relevant Psi4 sources. Syntax-audit provenance is not an engine-version
requirement and must not trigger a runtime check or deployment warning.

Do not copy method or keyword inventories into these skills. Resolve the exact
interface through the current API and the matching upstream documentation.
