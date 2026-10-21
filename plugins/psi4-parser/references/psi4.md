# Psi4 methods and options

The parser API explains how to construct input. Psi4's own documentation
explains the methods, options, molecular syntax, and their scientific meaning.

1. Identify the Psi4 version intended to run the input, using the user's supplied
   executable (`psi4 --version`) or environment information. A development build
   may also report its Git revision.
2. For a released version, follow its documentation link in the
   [Psi4 release notes](https://github.com/psi4/psi4/releases). The
   [development manual](https://psicode.org/psi4manual/master/index.html) tracks
   `master`; use it when it matches the intended build.
3. For a source checkout or development build, read the relevant `.rst` files
   under `doc/sphinxman/source/` at the corresponding branch, tag, or commit.
   The [upstream source directory](https://github.com/psi4/psi4/tree/master/doc/sphinxman/source)
   is the entry point; replace `master` with the identified ref.
4. Follow references to option definitions or driver source at that same ref when
   the manual leaves a question unresolved.

For a local checkout, search its documentation with `rg` and read the relevant
sections. Keep links or paths to the sources used for consequential method and
option choices. The parser's
[compatibility record](https://github.com/jasonrig/psi4-parser/blob/main/compatibility/psi4.json)
identifies its audited syntax target; read it at the runtime's ref and distinguish
that target from the user's installed Psi4 version.

Do not copy method or keyword inventories into these skills. Resolve the exact
interface through the current API and the matching upstream documentation.
