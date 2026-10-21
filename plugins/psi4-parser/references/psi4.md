# Psi4 methods and options

The parser API explains how to construct input. Psi4's own documentation
explains the methods, options, molecular syntax, and their scientific meaning.
An available Psi4 environment can also reveal runtime behavior through its Python
interface. Its absence should generally not prevent the builder from running.

1. Use the target version specified by the user or established by the task's
   context. Otherwise, check an available Psi4 executable (`psi4 --version`) or
   configured Psi4 Python environment. A development build may report its revision.
2. If those sources do not establish a version, check the
   [official release notes](https://github.com/psi4/psi4/releases) and assume the
   latest available Psi4 release. State the assumption briefly and proceed with
   input generation using official documentation.
3. Prefer the `.rst` documentation under `doc/sphinxman/source/` at the
   matching release tag or development commit. The
   [upstream source directory](https://github.com/psi4/psi4/tree/master/doc/sphinxman/source)
   is the entry point; replace `master` with the identified ref.
4. Read local RST files when a matching checkout is available. Otherwise, fetch
   their raw contents from GitHub. Follow references to included RST files,
   option definitions, or driver source at that same ref as needed.
5. Use the rendered manual only when the needed information is unavailable or
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
and version-matched Psi4 sources. The audited target and intended Psi4 version
serve different purposes.

Do not copy method or keyword inventories into these skills. Resolve the exact
interface through the current API and the matching upstream documentation.
