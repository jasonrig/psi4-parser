# Evidence record for psi4

`reference-audit.json` retains collected basis dimensions, integral limits,
selector outcomes, property names, and optional component observations.
`psi4_parser.maintenance.capabilities.curate_catalog()` can reproduce this
historical contribution. The shared catalogue has no target version or build;
new releases require no new catalogue or complete audit. Additional entries can
cite their own evidence from other revisions.

Source review targets commit
`60c9b2a773c05abc26991c5ed48cf9862cdb4978`:

- [proc.py](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/procrouting/proc.py):
  SCF/MP2 routing, analytic derivative and ROHF Hessian restrictions, PK
  execution, conventional MP2, property implementation, and legacy SAPT routing.
- [driver.py](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/driver.py)
  and the reviewed `driver_util.py`/`proc_table.py`: registration, derivative
  selection, finite differences, frequency/Hessian, and optimization dispatch.
- [read_options.cc](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/src/read_options.cc):
  option domains. The observed empty `QC_MODULE` default cannot be explicitly
  set, so it is excluded from the settable domain.
- [proc_util.py](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/procrouting/proc_util.py)
  and [psivardefs.py](https://github.com/psi4/psi4/blob/60c9b2a773c05abc26991c5ed48cf9862cdb4978/psi4/driver/qcdb/psivardefs.py):
  SAPT monomer preparation, dimer/monomer basis handling, and grouped component
  definitions. Both files are reviewed alongside the routing sources.

The standalone `maintenance/capability_reference.py` collects
222 atomic dimension rows without an SCF calculation: 90 orbital rows for five
bases through Ar and 132 fitting rows across explicit SAPT, ELST, and SCF roles.
The fitting definitions cover cc-pVDZ/TZ/QZ-RI and -JKFIT; the reviewed JKFIT
files lack He, Li, Be, Na, and Mg. Role-specific membership is retained.
It calls
only four reviewed selectors with `probe=True`, for three references and two
core treatments: 24 routing rows. Every row records explicit PK/CONV/OCC and
the native `FREEZE_CORE` value after Psithon-compatible string setting.

The broader 382 curated cases are source deductions combined with those
measurements. In particular:

- HF/SCF derivative and property dispatch use reviewed source and registered
  properties, independently of reference compilation limits.
- MP2 energy and analytic gradient restrictions use selector outcomes.
  Conventional MP2 properties and analytic Hessians are unsupported in this
  scope. Automatic and explicit finite-difference derivative routes use reviewed
  fallback dispatch and evidenced energy/gradient routes.
- ROHF analytic/automatic SCF Hessian and frequency cases retain the explicit
  source restriction; the finite-difference route is separate.
- Analytic MP2 gradient/optimization cases split by frozen core. Unmatched
  algorithm conditions remain unknown.
- SCF Hessian/frequency contracts retain documented driver/reference rules.
  Recorded compilation limits do not constrain the eventual execution machine.
- Legacy SAPT cases cover 15 method spellings with RHF and explicit matching
  D/T/Q fitting roles. Only SAPT0 has positive UHF/ROHF cases; ROHF requires
  uncoupled induction. Monomer-basis support is reviewed for RHF SAPT0.
  PK/DF SCF and conventional dMP2/OCC routing distinguish input cases. Native
  component availability and compilation are operator-managed. These are source deductions,
  not 216 additional chemistry executions.

The catalog additionally retains 1657 named product cases. The reviewed
`driver/qcdb/vib.py` and reviewed `driver.py` establish full harmonic arrays,
RRHO corrections/totals, and native vibrational record writing. Reviewed
`oeprop.cc` establishes the property quantities and native atomic units.
`get_writer_file_prefix.cc` establishes writer-label and process-ID naming.
The reviewed QCElemental `0.51.3` serializer establishes the frequency encoding: native
Datum entries in `.vibrec` are JSON strings, while the Hessian is a raw array.
These source deductions are separate from the metadata-only routing probes.
SAPT total and four grouped components use declarative native variable bindings.
The construction bundle adds no runtime collection; their transient lifetimes
require a separate consumer to collect before another call overwrites them.

Source review also covers `solvent/ddx.py`, the solvent package's import guard,
and `scf_proc/scf_iterator.py`. Eighteen conditional HF/SCF energy cases cover
DDX PCM, COSMO, and LPB equations. The audit records that this reference
environment lacks pyddx; those observations do not block construction. When available,
the inspector records named solvent
and UFF/Bondi table keys. These optional catalogues are reference metadata,
without installed-table checks in verification. No DDX chemistry run is
claimed by this metadata audit.

Four RHF/UHF HF/SCF energy cases cover equilibrium PCMSolver IEFPCM/CPCM input.
The reviewed `p4util/python_helpers.py` establishes `PCM__INPUT` dispatch
and the helper's parsed filename; native option scoping is tested separately.
The [PCMSolver input documentation](https://pcmsolver.readthedocs.io/en/stable/users/input.html)
establishes the explicit dielectric/probe and GePol parameters. No PCMSolver
installation or chemistry execution is required by this source evidence.

Component observations provide reference context. They never constrain an
execution host or emit deployment warnings. Runtime is operator-managed.

Source review also covers `driver_cbs.py`, `driver_cbs_helper.py`, and the
cc-pVTZ/cc-pVQZ basis files. The native D/T/Q cardinal convention and reviewed
cc-pVXZ basis definitions support explicit sequence memberships for D=2, T=3,
and Q=4. The inverse-power correction equation is reviewed independently from
the constructed scalar coefficients; its physical suitability remains an assumption.

Only reviewed features are claimed. Ghost centers are covered for energies;
optimization constraints use the separately tested lowerer. Basis element and
orbital-dimension evidence stops at Ar. No quantum chemistry calculation was
executed to produce this audit. See [maintenance instructions](../../../../../docs/formal-capabilities.md)
for collection and scope.

The TD-SCF contribution is reviewed independently in
`maintenance/tdscf_contracts.py`. Its nine source records establish HF/PBE/B3LYP
input routes, spin/kernel limits, primary reference returns, and five ordered
root products. These facts require no new binary audit and carry no target-version
constraint. `combine_catalogs()` retains both contributions and rejects conflicts.
Read the [response guide](../../../../../docs/formal-excited-states.md) for exact
root semantics, native scalar/array bindings, and remaining boundaries.
