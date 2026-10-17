// Full native statement families plus the imported Python grammar.
// Entry point: file_input. Payload schemas and execution checks are documented
// in README.md; a syntactic parse is not a successful calculation.
parser grammar PsithonParser;

options { tokenVocab = PsithonLexer; }
import PythonParser;

@header {
import __future__
import codecs
import keyword
import re
import unicodedata
import uuid
import warnings

from antlr4 import CommonTokenStream, InputStream, ParserRuleContext, Token
from antlr4.Token import CommonToken
from antlr4.error.ErrorListener import ErrorListener

# Pinned inventories: see compatibility/psi4.json; refreshed by psi4-sync.
_PSITHON_CORE_NAMES = (
    "AOShellCombinationsIterator",
    "Absent",
    "Angstrom",
    "AngularMomentumInt",
    "Ascending",
    "BSVec",
    "BasisExtents",
    "BasisFunctions",
    "BasisSet",
    "BlockOPoints",
    "Bohr",
    "BoysLocalizer",
    "CCWavefunction",
    "CIVector",
    "CIWavefunction",
    "CUHF",
    "Cartesian",
    "CdSalc",
    "CdSalcList",
    "CharacterTable",
    "CompositeJK",
    "CorrelationFactor",
    "CorrelationTable",
    "CubeProperties",
    "DASUM",
    "DAXPY",
    "DCOPY",
    "DDOT",
    "DFEP2Wavefunction",
    "DFHelper",
    "DFSOMCSCF",
    "DFTGrid",
    "DFTensor",
    "DGBMV",
    "DGEEV",
    "DGEMM",
    "DGEMV",
    "DGER",
    "DGETRF",
    "DGETRI",
    "DGETRS",
    "DNRM2",
    "DPOTRF",
    "DPOTRI",
    "DPOTRS",
    "DROT",
    "DSBMV",
    "DSCAL",
    "DSWAP",
    "DSYEV",
    "DSYMM",
    "DSYMV",
    "DSYR",
    "DSYR2",
    "DSYR2K",
    "DSYRK",
    "DSYSV",
    "DTBMV",
    "DTBSV",
    "DTRMM",
    "DTRMV",
    "DTRSM",
    "DTRSV",
    "Deriv",
    "DerivCalcType",
    "Descending",
    "DiagonalizeOrder",
    "Dimension",
    "DipoleInt",
    "DirectJK",
    "DiskSOMCSCF",
    "Dispersion",
    "ERI",
    "ESPPropCalc",
    "ElectricFieldInt",
    "ElectrostaticInt",
    "ExternalPotential",
    "FCHKWriter",
    "FDDS_Dispersion",
    "FISAPT",
    "Failure",
    "FittedSlaterCorrelationFactor",
    "FittingMetric",
    "FragmentType",
    "Functional",
    "GaussianShell",
    "GaussianType",
    "GeometryUnits",
    "Ghost",
    "HF",
    "IDAMAX",
    "IO",
    "IOManager",
    "IntVector",
    "IntegralFactory",
    "IntegralTransform",
    "IrreducibleRepresentation",
    "JK",
    "KineticInt",
    "LS_THC_Computer",
    "LaplaceDenominator",
    "LibXCFunctional",
    "Localizer",
    "LowerTriangle",
    "MOSpace",
    "MOWriter",
    "Matrix",
    "MatrixFactory",
    "MemDFJK",
    "MintsHelper",
    "MolecularGrid",
    "Molecule",
    "MultipoleInt",
    "MultipoleSymmetry",
    "NablaInt",
    "Normalized",
    "NumIntHelper",
    "OEProp",
    "OneBodyAOInt",
    "OneBodySOInt",
    "Options",
    "OrbitalSpace",
    "OverlapInt",
    "PMLocalizer",
    "PetiteList",
    "PointFunctions",
    "PointGroup",
    "PotentialInt",
    "PrimitiveType",
    "Prop",
    "ProtoIntVector",
    "ProtoVector",
    "PsiReturnType",
    "Pure",
    "QuadrupoleInt",
    "RHF",
    "RKSFunctions",
    "ROHF",
    "Real",
    "SADGuess",
    "SOBasisSet",
    "SOMCSCF",
    "SalcComponent",
    "SaveType",
    "ShellInfo",
    "Slice",
    "SubBlocks",
    "Success",
    "SuperFunctional",
    "SymmetryOperation",
    "TLaplaceDenominator",
    "ThreeCenterOverlapInt",
    "TracelessQuadrupoleInt",
    "TwoBodyAOInt",
    "TwoElectronInt",
    "UHF",
    "UKSFunctions",
    "Unnormalized",
    "VBase",
    "Vector",
    "Vector3",
    "Wavefunction",
    "__doc__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__spec__",
    "_libint2_configuration",
    "array_variable",
    "array_variables",
    "be_quiet",
    "benchmark_blas1",
    "benchmark_blas2",
    "benchmark_blas3",
    "benchmark_disk",
    "benchmark_integrals",
    "benchmark_math",
    "ccdensity",
    "ccenergy",
    "cceom",
    "cchbar",
    "cclambda",
    "ccresponse",
    "cctransort",
    "cctriples",
    "clean",
    "clean_options",
    "clean_timers",
    "clean_variables",
    "close_outfile",
    "dct",
    "del_array_variable",
    "del_scalar_variable",
    "del_variable",
    "detci",
    "dfmp2",
    "dfocc",
    "dlpno",
    "dmrg",
    "doublet",
    "dpdbuf4",
    "dpdfile2",
    "dummy_einsums",
    "dummy_integratorxx",
    "f12",
    "fcidump_tei_helper",
    "finalize",
    "flush_outfile",
    "fnocc",
    "get_active_molecule",
    "get_datadir",
    "get_global_option",
    "get_global_option_list",
    "get_local_option",
    "get_memory",
    "get_num_threads",
    "get_option",
    "get_options",
    "get_output_file",
    "get_timer_records",
    "get_writer_file_prefix",
    "git_version",
    "has_array_variable",
    "has_global_option_changed",
    "has_local_option_changed",
    "has_option_changed",
    "has_scalar_variable",
    "has_variable",
    "initialize",
    "libint2_solid_harmonics_ordering",
    "libint2_supports",
    "mcscf",
    "mrcc_generate_input",
    "mrcc_load_densities",
    "occ",
    "option_exists_in_module",
    "options_to_python",
    "outfile_name",
    "plugin",
    "plugin_close",
    "plugin_close_all",
    "plugin_load",
    "prepare_options_for_module",
    "print_global_options",
    "print_options",
    "print_out",
    "print_variables",
    "psi_top_srcdir",
    "psimrcc",
    "psio_entry",
    "reopen_outfile",
    "revoke_global_option_changed",
    "revoke_local_option_changed",
    "sapt",
    "scalar_variable",
    "scalar_variables",
    "scatter",
    "scfgrad",
    "scfhess",
    "set_active_molecule",
    "set_array_variable",
    "set_datadir",
    "set_global_option",
    "set_global_option_python",
    "set_local_option",
    "set_local_option_python",
    "set_memory_bytes",
    "set_num_threads",
    "set_output_file",
    "set_psi_file_prefix",
    "set_scalar_variable",
    "set_variable",
    "test_matrix_dpd_interface",
    "timer_off",
    "timer_on",
    "triplet",
    "tstart",
    "tstop",
    "variable",
    "variables",
    "version",
)
_PSITHON_CONSTANT_NAMES = (
    "Angstrom_star",
    "Avogadro_constant",
    "Bohr_magneton",
    "Bohr_magneton_in_HzpT",
    "Bohr_magneton_in_KpT",
    "Bohr_magneton_in_eVpT",
    "Bohr_magneton_in_inverse_meters_per_tesla",
    "Bohr_radius",
    "Boltzmann_constant",
    "Boltzmann_constant_in_HzpK",
    "Boltzmann_constant_in_eVpK",
    "Boltzmann_constant_in_inverse_meters_per_kelvin",
    "Compton_wavelength",
    "Compton_wavelength_over_2_pi",
    "Cu_x_unit",
    "Faraday_constant",
    "Faraday_constant_for_conventional_electric_current",
    "Fermi_coupling_constant",
    "Hartree_energy",
    "Hartree_energy_in_eV",
    "Josephson_constant",
    "Loschmidt_constant_27315_K_100_kPa",
    "Loschmidt_constant_27315_K_101325_kPa",
    "Mo_x_unit",
    "Newtonian_constant_of_gravitation",
    "Newtonian_constant_of_gravitation_over_h_bar_c",
    "Planck_constant",
    "Planck_constant_in_eV_s",
    "Planck_constant_over_2_pi",
    "Planck_constant_over_2_pi_in_eV_s",
    "Planck_constant_over_2_pi_times_c_in_MeV_fm",
    "Planck_length",
    "Planck_mass",
    "Planck_mass_energy_equivalent_in_GeV",
    "Planck_temperature",
    "Planck_time",
    "Quantity",
    "R",
    "Rydberg_constant",
    "Rydberg_constant_times_c_in_Hz",
    "Rydberg_constant_times_hc_in_J",
    "Rydberg_constant_times_hc_in_eV",
    "Sackur_Tetrode_constant_1_K_100_kPa",
    "Sackur_Tetrode_constant_1_K_101325_kPa",
    "Stefan_Boltzmann_constant",
    "Thomson_cross_section",
    "Wien_frequency_displacement_law_constant",
    "Wien_wavelength_displacement_law_constant",
    "_220_lattice_spacing_of_silicon",
    "_transtable",
    "_ureg",
    "alpha_particle_electron_mass_ratio",
    "alpha_particle_mass",
    "alpha_particle_mass_energy_equivalent",
    "alpha_particle_mass_energy_equivalent_in_MeV",
    "alpha_particle_mass_in_u",
    "alpha_particle_molar_mass",
    "alpha_particle_proton_mass_ratio",
    "amu2g",
    "amu2kg",
    "atomic_mass_constant",
    "atomic_mass_constant_energy_equivalent",
    "atomic_mass_constant_energy_equivalent_in_MeV",
    "atomic_mass_unit_electron_volt_relationship",
    "atomic_mass_unit_hartree_relationship",
    "atomic_mass_unit_hertz_relationship",
    "atomic_mass_unit_inverse_meter_relationship",
    "atomic_mass_unit_joule_relationship",
    "atomic_mass_unit_kelvin_relationship",
    "atomic_mass_unit_kilogram_relationship",
    "atomic_unit_of_1st_hyperpolarizability",
    "atomic_unit_of_2nd_hyperpolarizability",
    "atomic_unit_of_action",
    "atomic_unit_of_charge",
    "atomic_unit_of_charge_density",
    "atomic_unit_of_current",
    "atomic_unit_of_electric_dipole_mom",
    "atomic_unit_of_electric_field",
    "atomic_unit_of_electric_field_gradient",
    "atomic_unit_of_electric_polarizability",
    "atomic_unit_of_electric_potential",
    "atomic_unit_of_electric_quadrupole_mom",
    "atomic_unit_of_energy",
    "atomic_unit_of_force",
    "atomic_unit_of_length",
    "atomic_unit_of_mag_dipole_mom",
    "atomic_unit_of_mag_flux_density",
    "atomic_unit_of_magnetizability",
    "atomic_unit_of_mass",
    "atomic_unit_of_momum",
    "atomic_unit_of_permittivity",
    "atomic_unit_of_time",
    "atomic_unit_of_velocity",
    "au2amu",
    "bohr2angstroms",
    "bohr2cm",
    "bohr2m",
    "c",
    "c_au",
    "cal2J",
    "calorie_joule_relationship",
    "characteristic_impedance_of_vacuum",
    "classical_electron_radius",
    "conductance_quantum",
    "conventional_value_of_Josephson_constant",
    "conventional_value_of_von_Klitzing_constant",
    "conversion_factor",
    "deuteron_electron_mag_mom_ratio",
    "deuteron_electron_mass_ratio",
    "deuteron_g_factor",
    "deuteron_mag_mom",
    "deuteron_mag_mom_to_Bohr_magneton_ratio",
    "deuteron_mag_mom_to_nuclear_magneton_ratio",
    "deuteron_mass",
    "deuteron_mass_energy_equivalent",
    "deuteron_mass_energy_equivalent_in_MeV",
    "deuteron_mass_in_u",
    "deuteron_molar_mass",
    "deuteron_neutron_mag_mom_ratio",
    "deuteron_proton_mag_mom_ratio",
    "deuteron_proton_mass_ratio",
    "deuteron_rms_charge_radius",
    "dipmom_au2debye",
    "dipmom_au2si",
    "dipmom_debye2si",
    "doi",
    "e0",
    "electric_constant",
    "electron_charge_to_mass_quotient",
    "electron_deuteron_mag_mom_ratio",
    "electron_deuteron_mass_ratio",
    "electron_g_factor",
    "electron_gyromag_ratio",
    "electron_gyromag_ratio_over_2_pi",
    "electron_helion_mass_ratio",
    "electron_mag_mom",
    "electron_mag_mom_anomaly",
    "electron_mag_mom_to_Bohr_magneton_ratio",
    "electron_mag_mom_to_nuclear_magneton_ratio",
    "electron_mass",
    "electron_mass_energy_equivalent",
    "electron_mass_energy_equivalent_in_MeV",
    "electron_mass_in_u",
    "electron_molar_mass",
    "electron_muon_mag_mom_ratio",
    "electron_muon_mass_ratio",
    "electron_neutron_mag_mom_ratio",
    "electron_neutron_mass_ratio",
    "electron_proton_mag_mom_ratio",
    "electron_proton_mass_ratio",
    "electron_tau_mass_ratio",
    "electron_to_alpha_particle_mass_ratio",
    "electron_to_shielded_helion_mag_mom_ratio",
    "electron_to_shielded_proton_mag_mom_ratio",
    "electron_triton_mass_ratio",
    "electron_volt",
    "electron_volt_atomic_mass_unit_relationship",
    "electron_volt_hartree_relationship",
    "electron_volt_hertz_relationship",
    "electron_volt_inverse_meter_relationship",
    "electron_volt_joule_relationship",
    "electron_volt_kelvin_relationship",
    "electron_volt_kilogram_relationship",
    "elementary_charge",
    "elementary_charge_over_h",
    "fine_structure_constant",
    "first_radiation_constant",
    "first_radiation_constant_for_spectral_radiance",
    "get",
    "h",
    "hartree2J",
    "hartree2MHz",
    "hartree2aJ",
    "hartree2ev",
    "hartree2kJmol",
    "hartree2kcalmol",
    "hartree2wavenumbers",
    "hartree_atomic_mass_unit_relationship",
    "hartree_electron_volt_relationship",
    "hartree_hertz_relationship",
    "hartree_inverse_meter_relationship",
    "hartree_joule_relationship",
    "hartree_kelvin_relationship",
    "hartree_kilogram_relationship",
    "hbar",
    "helion_electron_mass_ratio",
    "helion_g_factor",
    "helion_mag_mom",
    "helion_mag_mom_to_Bohr_magneton_ratio",
    "helion_mag_mom_to_nuclear_magneton_ratio",
    "helion_mass",
    "helion_mass_energy_equivalent",
    "helion_mass_energy_equivalent_in_MeV",
    "helion_mass_in_u",
    "helion_molar_mass",
    "helion_proton_mass_ratio",
    "hertz_atomic_mass_unit_relationship",
    "hertz_electron_volt_relationship",
    "hertz_hartree_relationship",
    "hertz_inverse_meter_relationship",
    "hertz_joule_relationship",
    "hertz_kelvin_relationship",
    "hertz_kilogram_relationship",
    "inverse_fine_structure_constant",
    "inverse_meter_atomic_mass_unit_relationship",
    "inverse_meter_electron_volt_relationship",
    "inverse_meter_hartree_relationship",
    "inverse_meter_hertz_relationship",
    "inverse_meter_joule_relationship",
    "inverse_meter_kelvin_relationship",
    "inverse_meter_kilogram_relationship",
    "inverse_of_conductance_quantum",
    "joule_atomic_mass_unit_relationship",
    "joule_electron_volt_relationship",
    "joule_hartree_relationship",
    "joule_hertz_relationship",
    "joule_inverse_meter_relationship",
    "joule_kelvin_relationship",
    "joule_kilogram_relationship",
    "kb",
    "kcalmol2wavenumbers",
    "kelvin_atomic_mass_unit_relationship",
    "kelvin_electron_volt_relationship",
    "kelvin_hartree_relationship",
    "kelvin_hertz_relationship",
    "kelvin_inverse_meter_relationship",
    "kelvin_joule_relationship",
    "kelvin_kilogram_relationship",
    "kilogram_atomic_mass_unit_relationship",
    "kilogram_electron_volt_relationship",
    "kilogram_hartree_relationship",
    "kilogram_hertz_relationship",
    "kilogram_inverse_meter_relationship",
    "kilogram_joule_relationship",
    "kilogram_kelvin_relationship",
    "lattice_parameter_of_silicon",
    "mag_constant",
    "mag_flux_quantum",
    "me",
    "molar_Planck_constant",
    "molar_Planck_constant_times_c",
    "molar_gas_constant",
    "molar_mass_constant",
    "molar_mass_of_carbon_12",
    "molar_volume_of_ideal_gas_27315_K_100_kPa",
    "molar_volume_of_ideal_gas_27315_K_101325_kPa",
    "molar_volume_of_silicon",
    "muon_Compton_wavelength",
    "muon_Compton_wavelength_over_2_pi",
    "muon_electron_mass_ratio",
    "muon_g_factor",
    "muon_mag_mom",
    "muon_mag_mom_anomaly",
    "muon_mag_mom_to_Bohr_magneton_ratio",
    "muon_mag_mom_to_nuclear_magneton_ratio",
    "muon_mass",
    "muon_mass_energy_equivalent",
    "muon_mass_energy_equivalent_in_MeV",
    "muon_mass_in_u",
    "muon_molar_mass",
    "muon_neutron_mass_ratio",
    "muon_proton_mag_mom_ratio",
    "muon_proton_mass_ratio",
    "muon_tau_mass_ratio",
    "na",
    "name",
    "natural_unit_of_action",
    "natural_unit_of_action_in_eV_s",
    "natural_unit_of_energy",
    "natural_unit_of_energy_in_MeV",
    "natural_unit_of_length",
    "natural_unit_of_mass",
    "natural_unit_of_momum",
    "natural_unit_of_momum_in_MeVpc",
    "natural_unit_of_time",
    "natural_unit_of_velocity",
    "neutron_Compton_wavelength",
    "neutron_Compton_wavelength_over_2_pi",
    "neutron_electron_mag_mom_ratio",
    "neutron_electron_mass_ratio",
    "neutron_g_factor",
    "neutron_gyromag_ratio",
    "neutron_gyromag_ratio_over_2_pi",
    "neutron_mag_mom",
    "neutron_mag_mom_to_Bohr_magneton_ratio",
    "neutron_mag_mom_to_nuclear_magneton_ratio",
    "neutron_mass",
    "neutron_mass_energy_equivalent",
    "neutron_mass_energy_equivalent_in_MeV",
    "neutron_mass_in_u",
    "neutron_molar_mass",
    "neutron_muon_mass_ratio",
    "neutron_proton_mag_mom_ratio",
    "neutron_proton_mass_difference",
    "neutron_proton_mass_difference_energy_equivalent",
    "neutron_proton_mass_difference_energy_equivalent_in_MeV",
    "neutron_proton_mass_difference_in_u",
    "neutron_proton_mass_ratio",
    "neutron_tau_mass_ratio",
    "neutron_to_shielded_proton_mag_mom_ratio",
    "nuclear_magneton",
    "nuclear_magneton_in_KpT",
    "nuclear_magneton_in_MHzpT",
    "nuclear_magneton_in_eVpT",
    "nuclear_magneton_in_inverse_meters_per_tesla",
    "pc",
    "proton_Compton_wavelength",
    "proton_Compton_wavelength_over_2_pi",
    "proton_charge_to_mass_quotient",
    "proton_electron_mass_ratio",
    "proton_g_factor",
    "proton_gyromag_ratio",
    "proton_gyromag_ratio_over_2_pi",
    "proton_mag_mom",
    "proton_mag_mom_to_Bohr_magneton_ratio",
    "proton_mag_mom_to_nuclear_magneton_ratio",
    "proton_mag_shielding_correction",
    "proton_mass",
    "proton_mass_energy_equivalent",
    "proton_mass_energy_equivalent_in_MeV",
    "proton_mass_in_u",
    "proton_molar_mass",
    "proton_muon_mass_ratio",
    "proton_neutron_mag_mom_ratio",
    "proton_neutron_mass_ratio",
    "proton_rms_charge_radius",
    "proton_tau_mass_ratio",
    "quantum_of_circulation",
    "quantum_of_circulation_times_2",
    "raw_codata",
    "second_radiation_constant",
    "shielded_helion_gyromag_ratio",
    "shielded_helion_gyromag_ratio_over_2_pi",
    "shielded_helion_mag_mom",
    "shielded_helion_mag_mom_to_Bohr_magneton_ratio",
    "shielded_helion_mag_mom_to_nuclear_magneton_ratio",
    "shielded_helion_to_proton_mag_mom_ratio",
    "shielded_helion_to_shielded_proton_mag_mom_ratio",
    "shielded_proton_gyromag_ratio",
    "shielded_proton_gyromag_ratio_over_2_pi",
    "shielded_proton_mag_mom",
    "shielded_proton_mag_mom_to_Bohr_magneton_ratio",
    "shielded_proton_mag_mom_to_nuclear_magneton_ratio",
    "speed_of_light_in_vacuum",
    "standard_acceleration_of_gravity",
    "standard_atmosphere",
    "standard_state_pressure",
    "string_representation",
    "tau_Compton_wavelength",
    "tau_Compton_wavelength_over_2_pi",
    "tau_electron_mass_ratio",
    "tau_mass",
    "tau_mass_energy_equivalent",
    "tau_mass_energy_equivalent_in_MeV",
    "tau_mass_in_u",
    "tau_molar_mass",
    "tau_muon_mass_ratio",
    "tau_neutron_mass_ratio",
    "tau_proton_mass_ratio",
    "triton_electron_mass_ratio",
    "triton_g_factor",
    "triton_mag_mom",
    "triton_mag_mom_to_Bohr_magneton_ratio",
    "triton_mag_mom_to_nuclear_magneton_ratio",
    "triton_mass",
    "triton_mass_energy_equivalent",
    "triton_mass_energy_equivalent_in_MeV",
    "triton_mass_in_u",
    "triton_molar_mass",
    "triton_proton_mass_ratio",
    "unified_atomic_mass_unit",
    "ureg",
    "von_Klitzing_constant",
    "weak_mixing_angle",
    "year",
)

}

@members {
def psithon_scope(self, context):
    """Find the nearest executing body, excluding function/class headers."""
    child = None
    outer_iterable = False
    comprehension = False
    while context is not None:
        rule = self.ruleNames[context.getRuleIndex()]
        child_rule = (
            self.ruleNames[child.getRuleIndex()] if child is not None else ""
        )
        if rule == "for_if_clause" and child_rule == "disjunction":
            # The first iterable of a comprehension executes in the enclosing scope.
            clauses = context.parentCtx.getTypedRuleContexts(
                self.For_if_clauseContext
            )
            expressions = context.getTypedRuleContexts(self.DisjunctionContext)
            outer_iterable = clauses[0] is context and expressions[0] is child
        if rule in {"genexp", "listcomp", "setcomp", "dictcomp"}:
            if not outer_iterable:
                if rule == "genexp":
                    return "generator"
                comprehension = True
            outer_iterable = False
        if rule == "lambdef" and child_rule == "expression":
            return "comprehension" if comprehension else "lambda"
        is_body = child_rule == "block"
        if is_body and rule == "class_def_raw":
            return "class"
        if is_body and rule == "function_def_raw":
            scope = (
                "async"
                if context.getToken(self.ASYNC, 0) is not None
                else "function"
            )
            return scope + "_comprehension" if comprehension else scope
        child = context
        context = context.parentCtx
    return "comprehension" if comprehension else "module"

def psithon_loop(self, context):
    """A break/continue needs a loop in the same function/class body."""
    child = None
    while context is not None:
        rule = self.ruleNames[context.getRuleIndex()]
        is_body = (
            child is not None and self.ruleNames[child.getRuleIndex()] == "block"
        )
        if is_body and rule in {"for_stmt", "while_stmt"}:
            return True
        if is_body and rule in {"function_def_raw", "class_def_raw"}:
            return False
        child = context
        context = context.parentCtx
    return False

def psithon_contiguous(self, context):
    """Keep a scalar contiguous, with a predicate local to this rule."""
    return (
        context is not None
        and context.start.start < self._input.LT(1).start
        and self._input.LT(-1).stop + 1 == self._input.LT(1).start
    )

def psithon_rule(self, node):
    return self.ruleNames[node.getRuleIndex()]

def psithon_children(self, node):
    return [
        child
        for child in node.getChildren()
        if isinstance(child, ParserRuleContext)
    ]

def psithon_nodes(self, root, stop=()):
    """Walk rule contexts without depending on generated visitor classes."""
    pending = [root]
    while pending:
        node = pending.pop()
        yield node
        if node is root or self.psithon_rule(node) not in stop:
            pending.extend(reversed(self.psithon_children(node)))

def psithon_error(self, node, message):
    anchor = getattr(self, "_psithon_projection_anchor", None)
    if anchor is not None:
        self.psithon_source_error(anchor, message)
    else:
        self.notifyErrorListeners(message, node.start, None)

def psithon_name(self, node):
    return unicodedata.normalize("NFKC", node.getText())

def psithon_binding_name(self, node):
    """Normalize bound identifiers and apply lexical class-private mangling."""
    name = self.psithon_name(node)
    if not name.startswith("__") or name.endswith("__"):
        return name
    child, parent = node, node.parentCtx
    while parent is not None:
        if (
            self.psithon_rule(parent) == "class_def_raw"
            and self.psithon_rule(child) == "block"
        ):
            prefix = self.psithon_name(parent.name()).lstrip("_")
            return "_" + prefix + name if prefix else name
        child, parent = parent, parent.parentCtx
    return name

def psithon_owner(self, node):
    """Find the code scope; definition headers execute in the outer scope."""
    child = None
    while node is not None:
        rule = self.psithon_rule(node)
        child_rule = self.psithon_rule(child) if child is not None else ""
        if rule == "file_input":
            return node
        if rule in {"function_def_raw", "class_def_raw"} and child_rule == "block":
            return node
        if rule == "lambdef" and child_rule == "expression":
            return node
        child, node = node, node.parentCtx

def psithon_targets(self, node):
    """Collect stored names, excluding attribute and subscript expressions."""
    rule = self.psithon_rule(node)
    if rule == "name":
        return [node]
    if rule in {"t_primary", "single_subscript_attribute_target"}:
        return []
    if rule in {"target_with_star_atom", "del_target"} and node.t_primary():
        return []
    return [
        name
        for child in self.psithon_children(node)
        for name in self.psithon_targets(child)
    ]

def psithon_parameters(self, scope):
    rule = self.psithon_rule(scope)
    root = (
        scope.params()
        if rule == "function_def_raw"
        else scope.lambda_params()
        if rule == "lambdef"
        else None
    )
    if root is None:
        return []
    return [
        node.name()
        for node in self.psithon_nodes(root, {"lambdef"})
        if self.psithon_rule(node)
        in {"param", "param_star_annotation", "lambda_param"}
    ]

def psithon_annotation(self, node):
    """Annotations have deferred scopes and do not count as earlier outer reads."""
    child = node
    parent = node.parentCtx
    while parent is not None:
        rule = self.psithon_rule(parent)
        if rule in {
            "annotation",
            "star_annotation",
            "type_param_bound",
            "type_param_default",
            "type_param_starred_default",
        }:
            return True
        if (
            rule in {"assignment", "function_def_raw"}
            and self.psithon_rule(child) == "expression"
        ):
            return True
        child, parent = parent, parent.parentCtx
    return False

def psithon_bindings(self, root, nodes):
    """Resolve declarations after all local bindings are known, including forward ones."""
    scopes = [root] + [
        node
        for node in nodes
        if self.psithon_rule(node)
        in {"function_def_raw", "class_def_raw", "lambdef"}
    ]
    environments = {
        scope: {
            "bound": set(),
            "parameters": set(),
            "reads": [],
            "stores": [],
            "annotations": [],
            "declarations": [],
            "global": {},
            "nonlocal": {},
            "type_parameters": set(),
        }
        for scope in scopes
    }
    for scope in scopes:
        environment = environments[scope]
        if (
            self.psithon_rule(scope) in {"function_def_raw", "class_def_raw"}
            and scope.type_params() is not None
        ):
            environment["type_parameters"] = {
                self.psithon_binding_name(parameter.name())
                for parameter in scope.type_params().type_param_seq().type_param()
            }
        for parameter in self.psithon_parameters(scope):
            name = self.psithon_binding_name(parameter)
            if name in environment["parameters"]:
                self.psithon_error(parameter, "duplicate parameter: " + name)
            environment["parameters"].add(name)
            environment["bound"].add(name)
            if name == "__debug__":
                self.psithon_error(parameter, "cannot bind __debug__")
    for node in nodes:
        rule = self.psithon_rule(node)
        owner = self.psithon_owner(node)
        environment = environments[owner]
        stored = []
        if rule in {"global_stmt", "nonlocal_stmt"}:
            kind = "global" if rule == "global_stmt" else "nonlocal"
            for name_node in node.name():
                name = self.psithon_binding_name(name_node)
                environment[kind].setdefault(name, node)
                environment["declarations"].append((kind, name, node))
        elif rule == "assignment":
            for child in self.psithon_children(node):
                if self.psithon_rule(child) in {
                    "name",
                    "star_targets",
                    "single_target",
                }:
                    stored.extend(self.psithon_targets(child))
            if node.name() is not None:
                environment["annotations"].append(node.name())
        elif rule in {
            "function_def_raw",
            "class_def_raw",
            "type_alias",
            "assignment_expression",
        }:
            stored = [node.name()]
        elif rule == "for_stmt":
            stored = self.psithon_targets(node.star_targets())
        elif rule == "with_item" and node.star_target() is not None:
            stored = self.psithon_targets(node.star_target())
        elif (
            rule in {"except_block", "except_star_block"}
            and node.name() is not None
        ):
            stored = [node.name()]
        elif rule == "del_stmt":
            stored = self.psithon_targets(node.del_targets())
        elif rule in {"dotted_as_name", "import_from_as_name"}:
            names = node.name()
            if rule == "dotted_as_name":
                stored = (
                    [names]
                    if names is not None
                    else [
                        next(
                            part
                            for part in self.psithon_nodes(node.dotted_name())
                            if self.psithon_rule(part) == "name"
                        )
                    ]
                )
            else:
                stored = [names[-1]]
        elif rule == "pattern_capture_target":
            stored = [node]
        elif rule == "star_pattern" and node.name().getText() != "_":
            stored = [node.name()]
        elif (
            rule == "atom"
            and node.name() is not None
            and not self.psithon_annotation(node)
        ):
            environment["reads"].append(node.name())
        elif rule in {"name_or_attr", "attr"}:
            environment["reads"].append(node.name(0))
        elif (
            rule == "import_from_targets"
            and node.getText() == "*"
            and owner is not root
        ):
            self.psithon_error(node, "import * is only allowed at module level")
        for name_node in stored:
            name = self.psithon_binding_name(name_node)
            environment["bound"].add(name)
            # CPython marks imports DEF_IMPORT, not DEF_LOCAL. They provide
            # nonlocal bindings but do not forbid a later declaration.
            if rule not in {"dotted_as_name", "import_from_as_name"}:
                environment["stores"].append(name_node)
            if name == "__debug__":
                self.psithon_error(name_node, "cannot bind or delete __debug__")
    for scope, environment in environments.items():
        for kind, name, declaration in environment["declarations"]:
            other = "nonlocal" if kind == "global" else "global"
            if name in environment[other] or name in environment["parameters"]:
                self.psithon_error(declaration, "conflicting declaration: " + name)
            if scope is not root and any(
                self.psithon_binding_name(node) == name
                for node in environment["annotations"]
            ):
                self.psithon_error(
                    declaration, "annotated name cannot be " + kind + ": " + name
                )
            for node in environment["reads"] + environment["stores"]:
                if (
                    self.psithon_binding_name(node) == name
                    and node.start.tokenIndex < declaration.start.tokenIndex
                ):
                    self.psithon_error(
                        declaration,
                        "name used or assigned before " + kind + ": " + name,
                    )
                    break
            if kind == "nonlocal":
                parent = (
                    None
                    if name in environment["type_parameters"]
                    else self.psithon_owner(scope)
                )
                found = False
                while parent is not None and parent is not scope:
                    outer = environments[parent]
                    if (
                        self.psithon_rule(parent) == "class_def_raw"
                        and name == "__class__"
                    ):
                        found = True
                        break
                    if self.psithon_rule(parent) in {"function_def_raw", "lambdef"}:
                        if name in outer["global"]:
                            break
                        if (
                            name in outer["bound"]
                            and name not in outer["global"]
                            and name not in outer["nonlocal"]
                        ):
                            found = True
                            break
                    if name in outer["type_parameters"]:
                        break
                    if parent is root:
                        break
                    parent = self.psithon_owner(parent)
                if not found:
                    self.psithon_error(
                        declaration, "no binding for nonlocal: " + name
                    )

def psithon_comprehension(self, node):
    """Enforce iteration-variable, iterable, class and asynchronous restrictions."""
    clauses = node.for_if_clauses().for_if_clause()
    targets = {
        self.psithon_binding_name(name)
        for clause in clauses
        for name in self.psithon_targets(clause.star_targets())
    }
    for clause in clauses:
        iterable = clause.disjunction(0)
        if any(
            self.psithon_rule(part) == "assignment_expression"
            for part in self.psithon_nodes(iterable)
        ):
            self.psithon_error(
                iterable, "assignment expression in comprehension iterable"
            )
    for part in self.psithon_nodes(node):
        if self.psithon_rule(
            part
        ) == "assignment_expression" and self.psithon_owner(
            part
        ) is self.psithon_owner(node):
            if self.psithon_binding_name(part.name()) in targets:
                self.psithon_error(
                    part,
                    "assignment expression rebinds comprehension iteration variable",
                )
            if self.psithon_rule(self.psithon_owner(node)) == "class_def_raw":
                self.psithon_error(
                    part, "assignment expression in class comprehension"
                )
    if self.psithon_rule(node) != "genexp" and any(
        clause.getToken(self.ASYNC, 0) for clause in clauses
    ):
        if self.psithon_scope(node) not in {
            "async",
            "generator",
            "async_comprehension",
        }:
            self.psithon_error(
                node, "asynchronous comprehension outside async scope"
            )

def psithon_literal(self, node):
    """Evaluate only ANTLR-recognized literal tokens; never parse or compile Python."""
    parts = list(self.psithon_nodes(node, {"fstring", "tstring"}))
    strings = [part for part in parts if self.psithon_rule(part) == "string"]
    interpolated = any(
        self.psithon_rule(part) in {"fstring", "tstring"} for part in parts
    )
    if strings:
        values = []
        for part in strings:
            text = part.getText()
            quote = min(
                index for index, char in enumerate(text) if char in '"\u0027'
            )
            prefix = text[:quote].lower()
            width = (
                3 if text[quote : quote + 3] in {'"""', "\u0027\u0027\u0027"} else 1
            )
            payload = text[quote + width : -width]
            try:
                with warnings.catch_warnings(
                    action="ignore", category=DeprecationWarning
                ):
                    if "b" in prefix:
                        value = payload.encode("ascii")
                        if "r" not in prefix:
                            value = codecs.escape_decode(value)[0]
                    else:
                        value = (
                            payload
                            if "r" in prefix
                            else codecs.decode(
                                payload.encode("raw_unicode_escape"),
                                "unicode_escape",
                            )
                        )
            except (ValueError, UnicodeError) as error:
                self.psithon_error(part, "invalid literal: " + str(error))
                return False, None
            values.append(value)
        if len({type(value) for value in values}) != 1:
            self.psithon_error(node, "cannot mix bytes and text literals")
            return False, None
        if interpolated and isinstance(values[0], bytes):
            self.psithon_error(node, "cannot mix bytes and interpolated text")
            return False, None
        return True, values[0][:0].join(values)
    text = node.getText().replace("_", "")
    if text in {"True", "False", "None"}:
        return True, {"True": True, "False": False, "None": None}[text]
    try:
        try:
            return True, int(text, 0)
        except ValueError:
            return True, complex(text) if "j" in text.lower() else float(text)
    except ValueError:
        return False, None

def psithon_pattern(self, node):
    """Return captures and irrefutability while checking recursive pattern constraints."""
    rule = self.psithon_rule(node)
    if rule in {"pattern_capture_target", "capture_pattern"}:
        return {self.psithon_name(node)}, True
    if rule == "wildcard_pattern":
        return set(), True
    if rule == "star_pattern":
        name = self.psithon_name(node.name())
        return ({name} if name != "_" else set()), False
    if rule in {
        "literal_pattern",
        "value_pattern",
        "literal_expr",
        "attr",
        "name_or_attr",
        "name",
    }:
        if rule in {"literal_pattern", "literal_expr"} and any(
            self.psithon_rule(part) in {"fstring", "tstring"}
            for part in self.psithon_nodes(node)
        ):
            self.psithon_error(
                node, "interpolated strings are not literal patterns"
            )
        return set(), False
    children = self.psithon_children(node)
    if rule == "key_value_pattern":
        if node.literal_expr() is not None:
            self.psithon_pattern(node.literal_expr())
        children = [node.pattern()]
    if rule == "keyword_pattern":
        children = [node.pattern()]
    results = [self.psithon_pattern(child) for child in children]
    if rule == "or_pattern":
        if any(captures != results[0][0] for captures, _ in results[1:]):
            self.psithon_error(node, "alternative patterns bind different names")
        if any(irrefutable for _, irrefutable in results[:-1]):
            self.psithon_error(
                node, "irrefutable alternative makes remaining patterns unreachable"
            )
        return results[0][0], any(irrefutable for _, irrefutable in results)
    captured = set()
    for names, _ in results:
        if captured & names:
            self.psithon_error(node, "multiple assignments to a name in pattern")
        captured.update(names)
    if rule in {"maybe_sequence_pattern", "open_sequence_pattern"}:
        sequence = node.maybe_star_pattern()
        if rule == "open_sequence_pattern":
            rest = node.maybe_sequence_pattern()
            sequence = [sequence] + (rest.maybe_star_pattern() if rest else [])
        stars = [part for part in sequence if part.star_pattern() is not None]
        if len(stars) > 1:
            self.psithon_error(node, "multiple starred names in sequence pattern")
        elif (
            stars and sequence.index(stars[0]) >= 256 and stars[0].getText() != "*_"
        ):
            self.psithon_error(
                node, "too many expressions before starred sequence pattern"
            )
    if rule == "keyword_patterns":
        names = [self.psithon_name(part.name()) for part in node.keyword_pattern()]
        if len(names) != len(set(names)):
            self.psithon_error(node, "duplicate class pattern keyword")
        if "__debug__" in names:
            self.psithon_error(node, "cannot assign to __debug__")
    if rule == "items_pattern":
        keys = []
        for part in node.key_value_pattern():
            if part.literal_expr() is not None:
                known, value = self.psithon_literal(part.literal_expr())
                if known:
                    if value in keys:
                        self.psithon_error(part, "duplicate mapping pattern key")
                    keys.append(value)
    wrappers = {
        "patterns",
        "pattern",
        "closed_pattern",
        "group_pattern",
        "maybe_star_pattern",
    }
    irrefutable = rule == "as_pattern" or (rule in wrappers and len(results) == 1)
    return captured, irrefutable and any(value for _, value in results)

def psithon_interpolated_literal(self, node):
    """Check literal f/t-string chunks separately from their Python expressions."""
    opening = node.start.text.lower()
    quote = next(index for index, char in enumerate(opening) if char in '"\u0027')
    triple = len(opening) - quote == 3
    raw = "r" in opening[:quote]
    for part in self.psithon_nodes(node, {"fstring", "tstring"}):
        token = part.getToken(self.FSTRING_MIDDLE, 0) or part.getToken(
            self.TSTRING_MIDDLE, 0
        )
        if token is None:
            continue
        text = token.getText()
        if not triple and "\n" in text:
            self.psithon_error(
                part, "physical newline in a short interpolated string"
            )
        if not raw:
            try:
                # A chunk can end in a backslash before a replacement field.
                # A sentinel keeps this valid unknown escape from becoming a
                # truncated escape when decoding the chunk in isolation.
                with warnings.catch_warnings(
                    action="ignore", category=DeprecationWarning
                ):
                    codecs.decode(
                        (text + " ").encode("raw_unicode_escape"), "unicode_escape"
                    )
            except (ValueError, UnicodeError) as error:
                self.psithon_error(
                    part, "invalid interpolated literal: " + str(error)
                )

def psithon_restricted_expression(self, root):
    """Deferred annotations and generic definitions prohibit suspension and rebinding."""
    owner = self.psithon_owner(root)
    for node in self.psithon_nodes(root):
        if self.psithon_owner(node) is not owner:
            continue
        rule = self.psithon_rule(node)
        if rule in {"assignment_expression", "yield_expr"} or (
            rule == "await_primary" and node.getToken(self.AWAIT, 0)
        ):
            self.psithon_error(
                node,
                "yield, await and named expressions are prohibited in this annotation scope",
            )

def psithon_source(self, node):
    """Read a physical source span, including hidden whitespace."""
    return node.start.getInputStream().getText(node.start.start, node.stop.stop)

def psithon_inline_module(self, context):
    """Choose the optional module only when a following key has its own separator."""
    if context is None:
        return False
    token = self._input.LT(1)
    stream = token.getInputStream()
    tail = stream.getText(token.start, stream.size - 1)
    return re.match(r"[-,\w]+[^\S\n]+\w+(?:[^\S\n]|=)+[^\s=]", tail) is not None

def psithon_namespace_replacements(self):
    """Yield the reference namespace substitutions in their exact order."""
    for name in _PSITHON_CORE_NAMES:
        yield "psi4." + name, "psi4.core." + name
    for name in _PSITHON_CONSTANT_NAMES:
        yield "psi_" + name, "psi4.constants." + name

def psithon_namespace_text(self, text):
    """Project geometry fields that reach their reader after namespace expansion."""
    if "psi_" not in text and "psi4." not in text:
        return text
    for needle, replacement in self.psithon_namespace_replacements():
        text = text.replace(needle, replacement)
    return text

def psithon_native_constraint(self, node, rule):
    """Match the lexical fields consumed by the Psi4 and QCEElemental readers."""
    text = self.psithon_source(node)
    if rule in {"nucleus_label", "coordinate", "geometry_variable"}:
        text = self.psithon_namespace_text(text)
    geometry_fields = rule in {
        "atom_line",
        "charge_multiplicity",
        "numeric_xyz",
    } or (rule == "external_line" and node.nucleus() is not None)
    if geometry_fields and any(
        char.isspace() and char not in " \t" for char in text.strip()
    ):
        self.psithon_error(node, "geometry fields require spaces, tabs or commas")
    number = r"[+-]?(?:\d*\.\d+|\d+\.?\d*)(?:[dDeE][+-]?\d+)?"
    patterns = {
        "nucleus_label": r"(?:\d*[a-z]{1,3}(?:_\w+|\d+)?|\d{1,3}(?:_\w+)?)",
        "isotope_mass": r"@\d+\.\d+",
        "coordinate": r"(?:" + number + r"|-?[a-z][a-z0-9_]*)",
        "geometry_variable": r"-?[a-z][a-z0-9_]*\s*=\s*(?:tda|" + number + r")",
        "unit_name": r"(?:ang|angstrom|bohr|au|a\.u\.)",
        "module_name": r"[-\w]+",
        "header_label": r"\w+",
        "external_basis_line": r"(?:basis|df_basis_scf)[\s=]+\S+",
    }
    if (
        rule in patterns
        and re.fullmatch(patterns[rule], text, re.IGNORECASE) is None
    ):
        self.psithon_error(node, "invalid native " + rule.replace("_", " "))
    if rule == "molecule_name" and keyword.iskeyword(text):
        self.psithon_error(node, "molecule name cannot be a Python keyword")
    elif (
        rule == "charge_multiplicity" and not node.D_NUMBER(1).getText().isdecimal()
    ):
        self.psithon_error(node, "multiplicity must be an unsigned integer")
    elif rule == "anchor_pair":
        anchor = node.D_NUMBER() or node.native_word()
        if (
            re.fullmatch(
                r"(?:\d+|[a-z]{1,3}(?:_\w+|\d+)?)",
                self.psithon_namespace_text(anchor.getText()),
                re.IGNORECASE,
            )
            is None
        ):
            self.psithon_error(node, "invalid Z-matrix anchor")
    elif rule == "external_line":
        if any("." not in number.getText() for number in node.D_NUMBER()):
            self.psithon_error(
                node, "external coordinates and charges require decimal notation"
            )
    elif rule in {"set_command", "option_assignment"}:
        value = (
            node.inline_option_value()
            if rule == "set_command"
            else node.set_option_value()
        )
        key = node.option_key()
        separator = key.stop.getInputStream().getText(
            key.stop.stop + 1, value.start.start - 1
        )
        if re.fullmatch(r"[\s=]+", separator) is None:
            self.psithon_error(
                node, "option key and value require whitespace or equals"
            )
        if rule == "set_command" and value.inline_option_scalar() is not None:
            if (
                re.fullmatch(r"[$]?[-+,*:().\w]+", self.psithon_source(value))
                is None
            ):
                self.psithon_error(value, "invalid inline option scalar")

def psithon_option_python(self, node, spaces, modules, key, value):
    """Render the reference quoting rules and complete option calls."""
    words = (
        r'(([$]?)([-+:()*.,\w"\u0027/\\]+))'
        if "BASIS" in key.upper()
        else r'(([$]?)([-+()*.\w"\u0027/\\]+))'
    )

    def quote(match):
        dollar, word = match.group(2), match.group(3)
        if dollar:
            if re.match(r"^[A-Za-z][\w]*", word) is None:
                self.psithon_error(
                    node, "invalid Python variable in option expression"
                )
            return word
        if re.match(r"^-?\d+\.?\d*(?:[Ee]-?\d+)?$", word) or re.match(
            r'^\u0027.*\u0027$|^".*"$', word
        ):
            return word
        return '"' + word + '"'

    expression = re.sub(words, quote, value.strip())
    result = ""
    for module in modules.upper().split(","):
        if module in {"", "GLOBAL", "GLOBALS"}:
            result += (
                spaces
                + 'core.set_global_option("'
                + key.upper()
                + '", '
                + expression
                + ")\n"
            )
        else:
            result += (
                spaces
                + 'core.set_local_option("'
                + module
                + '", "'
                + key.upper()
                + '", '
                + expression
                + ")\n"
            )
    return result

def psithon_molecule_python(self, spaces, name, body):
    """Render geometry wrappers without opening referenced molecule files."""
    def from_file(match):
        self.native_payloads += (("from_file", match.group(2)),)
        return "\n"

    body = re.sub(
        r"^(\s*from_file\s*:\s*(.*)\n)$",
        from_file,
        body,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    result = spaces + (name + " = " if name else "") + 'geometry("""' + body + '"""'
    if name:
        result += ',"' + name + '"'
    return result + ")\n" + spaces + 'core.IO.set_default_namespace("' + name + '")'

def psithon_basis_python(self, node, spaces, role, name, body, *, anonymous_name=None):
    """Render basis definitions with the reference assignment and label layout."""
    name = name or anonymous_name or "anonymous" + str(uuid.uuid4())[:8]

    def basname(value):
        return (
            value.lower()
            .replace("+", "p")
            .replace("*", "s")
            .replace("(", "_")
            .replace(")", "_")
            .replace(",", "_")
        )

    clean = basname(name).replace("-", "")
    code = [
        "def basisspec_psi4_yo__" + clean + "(mol, role):",
        "    basstrings = {}",
    ]
    remaining, assigned = [], False
    for line in body.split("\n"):
        match = re.fullmatch(
            r"\s*assign\s+(?:([a-z]{1,3}(?:_\w+|\d+)?)\s+)?([-+:*()\w]+)\s*",
            line,
            re.IGNORECASE,
        )
        if match is None:
            if line.strip():
                remaining.append(line.strip())
            continue
        assigned = True
        label, basis = match.groups()
        if label is None:
            code.append('    mol.set_basis_all_atoms("' + basis + '", role=role)')
        else:
            method = (
                "set_basis_by_symbol"
                if re.fullmatch(r"[a-z]{1,3}", label, re.IGNORECASE)
                else "set_basis_by_label"
            )
            code.append(
                "    mol."
                + method
                + '("'
                + label
                + '", "'
                + basis
                + '", role=role)'
            )
    blocks = list(
        filter(None, re.split(r"\s*\[\s*([-*()\w]+)\s*\]\s*", "\n".join(remaining)))
    )
    if len(blocks) == 1 and (assigned or "\n" in spaces):
        self.psithon_error(
            node, "assign lines and unlabelled basis shells conflict"
        )
        return ""
    if len(blocks) > 1 and len(blocks) % 2:
        self.psithon_error(node, "basis label requires a following payload")
        return ""
    if len(blocks) == 1:
        code.append('    mol.set_basis_all_atoms("' + name + '", role=role)')
        blocks = [name, blocks[0]]
    for index in range(0, len(blocks), 2):
        code.append(
            "    basstrings['"
            + basname(blocks[index])
            + '\'] = """\n'
            + blocks[index + 1]
            + '\n"""'
        )
    code.extend(
        [
            "    return basstrings",
            "qcdb.libmintsbasisset.basishorde['"
            + name.upper()
            + "'] = basisspec_psi4_yo__"
            + clean,
            'core.set_global_option("' + role.upper() + '", "' + name + '")',
        ]
    )
    return spaces + ("\n" + spaces).join(code)

def psithon_external_python(self, node, spaces, name, body, *, geometry_indent=None):
    """Render external potentials, preserving Python numeric and string syntax."""
    number = r"[+-]?(?:\d*\.\d+|\d+\.\d*)(?:[dDeE][+-]?\d+)?"
    lines = [line for line in body.split("\n") if line.strip()]
    units, basis, fitting, remaining = "ang", "cc-pvdz", "cc-pvdz-jkfit", []
    for line in lines:
        match = re.fullmatch(
            r"^\s*units?[\s=]+(ang|angstrom|bohr|au|a\.u\.)$\s*",
            line,
            re.IGNORECASE,
        )
        if match:
            units = "bohr" if match.group(1) in {"bohr", "au", "a.u."} else "ang"
        else:
            remaining.append(line)
    lines, remaining = remaining, []
    for line in lines:
        match = re.fullmatch(
            r"\s*(basis|df_basis_scf)[\s=]+(\S+)\s*", line, re.IGNORECASE
        )
        if match:
            if match.group(1).lower() == "basis":
                basis = match.group(2)
            else:
                fitting = match.group(2)
        else:
            remaining.append(line)
    # Native geometry semantics do not include indentation inserted by this
    # wrapper. AST mode retains the original body separately and canonicalizes
    # only that generated padding; the ordinary reference projection is exact.
    geometry_spaces = spaces if geometry_indent is None else geometry_indent
    result = spaces + "qmmm = QMMM()\n"
    lines, remaining = remaining, []
    charge = re.compile(
        r"\s*("
        + number
        + r")\s+("
        + number
        + r")\s+("
        + number
        + r")\s+("
        + number
        + r")\s*"
    )
    for line in lines:
        match = charge.fullmatch(line)
        if match:
            method = "addChargeAngstrom" if units == "ang" else "addChargeBohr"
            result += (
                spaces + "qmmm." + method + "(" + ",".join(match.groups()) + ")\n"
            )
        else:
            remaining.append(line)
    fragments = [[]]
    for line in remaining:
        if re.fullmatch(r"\s*--\s*", line):
            if fragments[-1]:
                fragments.append([])
        else:
            fragments[-1].append(line)
    result += spaces + "extern_mol_temp = core.get_active_molecule()\n"
    molecule_line = re.compile(
        r"\s*\S+\s+" + number + r"\s+" + number + r"\s+" + number + r"\s*"
    )
    for fragment in fragments:
        if not fragment:
            continue
        result += spaces + 'external_diffuse = geometry("""\n' + geometry_spaces + "0 1\n"
        for line in fragment:
            if molecule_line.fullmatch(line) is None:
                self.psithon_error(node, "unrecognized external-potential line")
            else:
                result += geometry_spaces + line + "\n"
        for line in [
            "units " + units,
            "symmetry c1",
            "no_reorient",
            "no_com",
            '""")',
        ]:
            result += geometry_spaces + line + "\n"
        result += (
            spaces
            + "diffuse = Diffuse(external_diffuse,'"
            + basis
            + "','"
            + fitting
            + "')\n"
        )
        result += (
            spaces + "diffuse.fitScf()\n" + spaces + "qmmm.addDiffuse(diffuse)\n\n"
        )
    for line in [
        "core.set_active_molecule(extern_mol_temp)",
        "qmmm.populateExtern()",
        (name or "extern") + " = qmmm.extern",
        'core.set_global_option_python("EXTERN", extern)',
    ]:
        result += spaces + line + "\n"
    return result

def psithon_project_replace(self, projection, pattern, replacement):
    """Carry original character positions through one ordered regex rewrite."""
    source, positions = projection
    chunks, origins, cursor = [], [], 0
    for match in pattern.finditer(source):
        chunks.append(source[cursor : match.start()])
        origins.extend(positions[cursor : match.start()])
        anchor = match.start()
        if (
            match.lastindex
            and match.group(1) is not None
            and match.group(1).isspace()
        ):
            anchor += len(match.group(1))
        anchor = positions[min(anchor, len(positions) - 1)] if positions else 0
        self._psithon_projection_anchor = anchor
        try:
            value = replacement(match)
        finally:
            self._psithon_projection_anchor = None
        chunks.append(value)
        origins.extend([anchor] * len(value))
        cursor = match.end()
    chunks.append(source[cursor:])
    origins.extend(positions[cursor:])
    return "".join(chunks), origins

def psithon_balanced(self, text):
    """Match the reference raw-character bracket counter, including curly braces."""
    stack, pairs = [], {"(": ")", "[": "]", "{": "}"}
    for char in text:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack or pairs[stack.pop()] != char:
                return False
    return not stack

def psithon_project(self, root, source, *, for_ast=False):
    """Apply ordered syntactic rewrites from the pinned Psi4 preprocessor."""
    self.native_payloads = ()
    projection = source, list(range(len(source)))
    flags = re.MULTILINE | re.DOTALL | re.IGNORECASE
    literals = {}

    def cfour(match):
        key = str(uuid.uuid4())[:8]
        literals[key] = match.group(3)
        return (
            match.group(1)
            + 'core.set_global_option("LITERAL_CFOUR", """literals_psi4_yo-'
            + key
            + '\n""")\n'
        )

    projection = self.psithon_project_replace(
        projection,
        re.compile(r"^(\s*?)cfour[=\s]*(\w*?)\s*\{(.*?)\}", flags),
        cfour,
    )
    projection = self.psithon_project_replace(
        projection, re.compile(r"(^|[^\\])#.*"), lambda match: ""
    )
    projection = self.psithon_project_replace(
        projection, re.compile(r"\\#"), lambda match: "#"
    )
    # The reference passes re.MULTILINE as re.sub count, not as regex flags.
    # Consequently this step only removes an entirely whitespace-only input.
    projection = self.psithon_project_replace(
        projection, re.compile(r"^\s*$"), lambda match: ""
    )
    text, positions = projection
    lines = text.split("\n")
    cursor, chunks, origins, index = 0, [], [], 0
    array_start = re.compile(
        r"^(\s*?)set\s+(?:([-,\w]+)\s+)?(\w+)[\s=]+\[.*", re.IGNORECASE
    )
    while index < len(lines):
        value, offset = lines[index], cursor
        cursor += len(value) + 1
        index += 1
        if array_start.match(value):
            while not self.psithon_balanced(value):
                if index >= len(lines):
                    self.psithon_error(root, "unbalanced native multiline array")
                    break
                value += lines[index].strip()
                cursor += len(lines[index]) + 1
                index += 1
            anchor = positions[min(offset, len(positions) - 1)] if positions else 0
            origins.extend([anchor] * (len(value) + 1))
        else:
            origins.extend(positions[offset : min(cursor, len(positions))])
            if cursor > len(positions):
                origins.append(positions[-1] if positions else 0)
        chunks.append(value + "\n")
    projection = "".join(chunks), origins

    def set_block(match):
        spaces, modules, body = match.groups()
        command, result = "", ""
        for line in body.split("\n"):
            command += line
            if not self.psithon_balanced(command) or not line.strip():
                continue
            option = re.fullmatch(r"\s*(\w+)[\s=]+(.*?)", command)
            if option is None:
                self.psithon_error(root, "unsupported option syntax")
                return ""
            result += self.psithon_option_python(
                root, spaces, modules, option.group(1), option.group(2)
            )
            command = ""
        return result

    projection = self.psithon_project_replace(
        projection,
        re.compile(r"^(\s*?)set\s*([-,\w]*?)[\s=]*\{(.*?)\}", flags),
        set_block,
    )
    projection = self.psithon_project_replace(
        projection,
        re.compile(
            r"^(\s*?)set\s+(?:([-,\w]+)[^\S\n]+)?(\w+)(?:[^\S\n]|=)+((\[.*\])|([$]?[-+,*:()\.\w]+))\s*$",
            re.MULTILINE | re.IGNORECASE,
        ),
        lambda match: self.psithon_option_python(
            root,
            match.group(1),
            match.group(2) or "",
            match.group(3),
            match.group(4),
        ),
    )
    projection = self.psithon_project_replace(
        projection,
        re.compile(r"^(\s*?)molecule[=\s]*(\S*?)\s*\{(.*?)\}", flags),
        lambda match: self.psithon_molecule_python(*match.groups()),
    )
    def external(match):
        self.native_payloads += (("external", match.group(3)),)
        return self.psithon_external_python(
            root, *match.groups(), geometry_indent="" if for_ast else None
        )

    projection = self.psithon_project_replace(
        projection,
        re.compile(r"^(\s*?)external[=\s]*(\w*?)\s*\{(.*?)\}", flags),
        external,
    )
    # Solver values are repr(list[str]); their contents cannot change the wrapper.
    pcm_python = "parsedFile = os.path.join(os.getcwd(), '@pcmsolver.syntax')\nwith open(parsedFile, 'w') as tmp:\n    tmp.write('\\n'.join([]))\n\ncore.set_local_option('PCM', 'PCMSOLVER_PARSED_FNAME', '@pcmsolver.syntax')\n\n"
    def pcm(match):
        self.native_payloads += (("pcm", match.group(3)),)
        return pcm_python

    projection = self.psithon_project_replace(
        projection,
        re.compile(r"^(\s*?)pcm[=\s]*(\w*?)\s*\{(.*?)^\}", flags),
        pcm,
    )
    projection = self.psithon_project_replace(
        projection, re.compile(r"\n+"), lambda match: "\n"
    )

    def extract(match):
        spaces, name = match.group(1), match.group(2)
        return (
            match.group(0)
            + spaces
            + name
            + '.set_name("'
            + name
            + '")\n'
            + spaces
            + "core.set_active_molecule("
            + name
            + ")\n"
            + spaces
            + 'core.IO.set_default_namespace("'
            + name
            + '")'
        )

    projection = self.psithon_project_replace(
        projection,
        re.compile(r"(\s*?)(\w+)\s*=\s*\w+\.extract_subsets.*", re.IGNORECASE),
        extract,
    )

    def memory(match):
        spaces, amount, units = match.groups()
        units = units.upper()
        try:
            size = int(
                float(amount)
                * (1024 if "I" in units else 1000) ** "BKMGTPE".index(units[0])
            )
        except ValueError, OverflowError:
            self.psithon_error(root, "invalid memory amount")
            return ""
        return spaces + "core.set_memory_bytes(" + str(size) + ")\n"

    projection = self.psithon_project_replace(
        projection,
        re.compile(r"(\s*?)memory\s+(\d*\.?\d+)\s*([KMGTPBE]i?B)", re.IGNORECASE),
        memory,
    )
    basis_index = 0
    reserved_names = unicodedata.normalize("NFKC", source).casefold() if for_ast else ""

    def basis(match):
        nonlocal basis_index
        anonymous = None
        if not match.group(3):
            self.native_payloads += (("anonymous_basis", ""),)
        if for_ast and not match.group(3):
            # Use fresh deterministic symbols so normalization cannot capture
            # an explicit user binding or the function generated for a named basis.
            while True:
                anonymous = "anonymous" + format(basis_index, "08x")
                basis_index += 1
                if anonymous not in reserved_names:
                    break
        return self.psithon_basis_python(
            root, *match.groups(), anonymous_name=anonymous
        )

    projection = self.psithon_project_replace(
        projection,
        re.compile(
            r"^(\s*?)(basis_relativistic|df_basis_scf|df_basis_mp2|df_basis_cc|df_basis_sapt|df_basis_sad|df_basis_dct|basis)[=\s]*(\w*?)\s*\{(.*?)\}",
            flags,
        ),
        basis,
    )

    def restore(match):
        key = match.group(1)
        if key not in literals:
            self.psithon_error(root, "unknown CFOUR literal marker")
            return ""
        return literals[key]

    projection = self.psithon_project_replace(
        projection, re.compile(r"literals_psi4_yo-(\w{8})"), restore
    )
    futures = []

    def hoist(match):
        futures.append((match.group(0) + "\n", self._psithon_projection_anchor))
        return ""

    projection = self.psithon_project_replace(
        projection, re.compile(r"^from __future__ import .*$", re.MULTILINE), hoist
    )
    prelude = (
        "import psi4\nfrom psi4 import *\nfrom psi4.core import *\n"
        "from psi4.driver.diatomic import anharmonicity\nfrom psi4.driver.gaussian_n import *\n"
        "from psi4.driver.frac import ip_fitting, frac_traverse\nfrom psi4.driver.aliases import *\n"
        "from psi4.driver.driver_cbs import *\n"
        "from psi4.driver.wrapper_database import database, db, DB_RGT, DB_RXN\n"
        "from psi4.driver.wrapper_autofrag import auto_fragments\npsi4_io = core.IOManager.shared_object()\n"
    )
    text, positions = projection
    prefix = (
        "".join(value for value, _ in futures) + ("" if futures else "\n") + prelude
    )
    prefix_origins = []
    for value, anchor in futures:
        prefix_origins.extend([anchor] * len(value))
    prefix_origins.extend([0] * (len(prelude) + (0 if futures else 1)))
    projection = prefix + text, prefix_origins + positions
    for needle, replacement in self.psithon_namespace_replacements():
        if needle in projection[0]:
            projection = self.psithon_project_replace(
                projection,
                re.compile(re.escape(needle)),
                lambda match, replacement=replacement: replacement,
            )
    return projection

def psithon_deferred(self):
    """Defer Python context rules until the complete native rewrite is recognized."""
    return self._input.tokenSource.native_input

python_source = None
native_payloads = ()

def psithon_validate_input(self, root):
    """Validate native fields, then recognize the complete projected Python job."""
    from psi4_parser._generated.PsithonLexer import PsithonLexer

    fields = {
        "nucleus_label",
        "isotope_mass",
        "coordinate",
        "geometry_variable",
        "unit_name",
        "module_name",
        "header_label",
        "external_basis_line",
        "molecule_name",
        "charge_multiplicity",
        "anchor_pair",
        "atom_line",
        "numeric_xyz",
        "external_line",
        "set_command",
        "option_assignment",
    }
    for node in self.psithon_nodes(root):
        if self.psithon_rule(node) in fields:
            self.psithon_native_constraint(node, self.psithon_rule(node))
    if self.getNumberOfSyntaxErrors():
        return
    source = self._input.tokenSource._psithon_source
    self._psithon_original_source = source
    projection, positions = self.psithon_project(root, source, for_ast=True)
    self.python_source = projection
    if self.getNumberOfSyntaxErrors():
        return

    class PythonLexer(PsithonLexer):
        native_input = False

    starts = [0] + [
        index + 1 for index, char in enumerate(projection) if char == "\n"
    ]

    class Errors(ErrorListener):
        def syntaxError(listener, recognizer, symbol, line, column, message, error):
            projected = starts[min(line - 1, len(starts) - 1)] + column
            original = (
                positions[max(0, projected)]
                if projected < len(positions)
                else len(source)
            )
            self.psithon_source_error(original, message)

    lexer = PythonLexer(InputStream(projection))
    errors = Errors()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errors)
    parser = type(self)(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(errors)
    parser.file_input()

def psithon_source_error(self, position, message):
    """Report a projected diagnostic at the corresponding original position."""
    source = self._psithon_original_source
    token = CommonToken(type=Token.INVALID_TYPE)
    token.line = source.count("\n", 0, position) + 1
    token.column = position - source.rfind("\n", 0, position) - 1
    self.notifyErrorListeners(message, token, None)

def psithon_future(self, nodes):
    """Validate future imports and flags in the final Python program."""
    root = nodes[0]
    permitted = set()
    beginning = True
    first = True
    statements = (
        root.statements().statement() if root.statements() is not None else []
    )
    for statement in statements:
        if statement.simple_stmts() is None:
            beginning = False
            first = False
            continue
        for simple in statement.simple_stmts().simple_stmt():
            imported = simple.import_stmt()
            future = imported.import_from() if imported is not None else None
            is_future = (
                future is not None
                and future.dotted_name() is not None
                and self.psithon_name(future.dotted_name()) == "__future__"
                and not (
                    future.getToken(self.DOT, 0)
                    or future.getToken(self.ELLIPSIS, 0)
                )
            )
            if is_future and beginning:
                permitted.add(future)
            elif not is_future:
                expression = simple.star_expressions()
                literals = [
                    part
                    for part in self.psithon_nodes(simple)
                    if self.psithon_rule(part) == "strings"
                ]
                docstring = False
                if first and expression is not None and len(literals) == 1:
                    text = expression.getText()
                    while text.startswith("(") and text.endswith(")"):
                        text = text[1:-1]
                    known, value = self.psithon_literal(literals[0])
                    docstring = (
                        known
                        and isinstance(value, str)
                        and text == literals[0].getText()
                    )
                if not docstring:
                    beginning = False
            first = False
    features = set()
    for node in nodes:
        if self.psithon_rule(node) != "import_from" or node.dotted_name() is None:
            continue
        if (
            self.psithon_name(node.dotted_name()) != "__future__"
            or node.getToken(self.DOT, 0)
            or node.getToken(self.ELLIPSIS, 0)
        ):
            continue
        if node not in permitted:
            self.psithon_error(node, "future import must precede other statements")
        targets = node.import_from_targets().import_from_as_names()
        if targets is None:
            self.psithon_error(node, "future import cannot use wildcard")
            continue
        for target in targets.import_from_as_name():
            feature = self.psithon_name(target.name(0))
            if feature not in __future__.all_feature_names:
                self.psithon_error(
                    target, "future feature is not defined: " + feature
                )
            features.add(feature)
    barry = "barry_as_FLUFL" in features
    for node in nodes:
        if self.psithon_rule(node) == "noteq_bitwise_or" and (
            (node.getChild(0).getText() == "<>") != barry
        ):
            self.psithon_error(
                node, "comparison operator does not match the active future flags"
            )

def psithon_lazy_import(self, node):
    """Lazy imports require module scope outside protected try blocks."""
    if node.getToken(self.NAME_OR_LAZY, 0) is None:
        return
    if self.psithon_rule(self.psithon_owner(node)) != "file_input":
        self.psithon_error(node, "lazy import is only allowed at module scope")
    parent = node.parentCtx
    while parent is not None:
        if self.psithon_rule(parent) == "try_stmt":
            self.psithon_error(node, "lazy import is not allowed inside try blocks")
            break
        parent = parent.parentCtx
    if self.psithon_rule(node) == "import_from":
        if node.import_from_targets().getText() == "*":
            self.psithon_error(node, "lazy wildcard import is not allowed")
        if (
            node.dotted_name() is not None
            and self.psithon_name(node.dotted_name()) == "__future__"
            and not (node.getToken(self.DOT, 0) or node.getToken(self.ELLIPSIS, 0))
        ):
            self.psithon_error(node, "lazy future import is not allowed")

def psithon_constraints(self, root):
    """Apply static constraints over the complete ANTLR tree, including forward references."""
    nodes = list(self.psithon_nodes(root))
    stream = root.start.getInputStream()
    if "\x00" in stream.getText(0, stream.size - 1):
        self.psithon_error(root, "source code cannot contain null bytes")
    self.psithon_future(nodes)
    self.psithon_bindings(root, nodes)
    generators = {
        self.psithon_owner(node)
        for node in nodes
        if self.psithon_rule(node) == "yield_expr"
    }
    for node in nodes:
        rule = self.psithon_rule(node)
        if rule == "name_except_underscore" and self.psithon_name(node) in {
            "None",
            "True",
            "False",
        }:
            self.psithon_error(node, "identifier normalizes to a reserved constant")
        if rule in {"import_name", "import_from"}:
            self.psithon_lazy_import(node)
        if rule in {"return_stmt", "break_stmt", "continue_stmt"}:
            child = node
            parent = node.parentCtx
            while parent is not None:
                parent_rule = self.psithon_rule(parent)
                if parent_rule in {"function_def_raw", "class_def_raw", "lambdef"}:
                    break
                if (
                    rule != "return_stmt"
                    and parent_rule in {"for_stmt", "while_stmt"}
                    and self.psithon_rule(child) == "block"
                ):
                    break
                if parent_rule == "except_star_block":
                    self.psithon_error(
                        node, "control flow cannot leave an except* block"
                    )
                    break
                child, parent = parent, parent.parentCtx
            owner = self.psithon_owner(node)
            if (
                rule == "return_stmt"
                and node.star_expressions() is not None
                and owner in generators
            ):
                if self.psithon_rule(
                    owner
                ) == "function_def_raw" and owner.getToken(self.ASYNC, 0):
                    self.psithon_error(node, "return with value in async generator")
        elif rule == "try_stmt":
            handlers = node.except_block()
            if any(
                handler.expression() is None and handler.expressions() is None
                for handler in handlers[:-1]
            ):
                self.psithon_error(node, "bare except must be last")
        elif rule in {"genexp", "listcomp", "setcomp", "dictcomp"}:
            self.psithon_comprehension(node)
        elif rule == "match_stmt":
            cases = node.case_block()
            for index, case in enumerate(cases):
                _, irrefutable = self.psithon_pattern(case.patterns())
                if irrefutable and case.guard() is None and index + 1 < len(cases):
                    self.psithon_error(
                        case,
                        "irrefutable pattern makes remaining cases unreachable",
                    )
        elif rule == "complex_number":
            if (
                "j" in node.signed_real_number().getText().lower()
                or "j" not in node.imaginary_number().getText().lower()
            ):
                self.psithon_error(
                    node, "complex pattern requires real and imaginary parts"
                )
        elif rule == "kwargs":
            keywords = [
                part
                for part in self.psithon_children(node)
                if part.name() is not None
            ]
            names = [self.psithon_name(part.name()) for part in keywords]
            if len(names) != len(set(names)):
                self.psithon_error(node, "keyword argument repeated")
            if "__debug__" in names:
                self.psithon_error(node, "cannot assign to __debug__")
        elif rule in {
            "star_targets",
            "star_targets_list_seq",
            "star_targets_tuple_seq",
        }:
            stars = [
                part
                for part in node.star_target()
                if part.getText().startswith("*")
            ]
            if len(stars) > 1 or (
                stars
                and rule == "star_targets"
                and len(node.star_target()) == 1
                and node.getToken(self.COMMA, 0) is None
            ):
                self.psithon_error(node, "invalid starred assignment target")
            elif stars and node.star_target().index(stars[0]) >= 256:
                self.psithon_error(
                    node, "too many expressions before starred assignment target"
                )
        elif rule == "star_expressions":
            if (
                len(node.star_expression()) == 1
                and node.star_expression(0).getText().startswith("*")
                and node.getToken(self.COMMA, 0) is None
            ):
                self.psithon_error(
                    node, "starred expression requires a tuple or container"
                )
        elif rule == "type_param_seq":
            seen = set()
            defaulted = False
            for parameter in node.type_param():
                name = self.psithon_binding_name(parameter.name())
                if name in seen:
                    self.psithon_error(
                        parameter, "duplicate type parameter: " + name
                    )
                if name == "__debug__":
                    self.psithon_error(parameter, "cannot bind __debug__")
                seen.add(name)
                has_default = (
                    parameter.type_param_default() is not None
                    or parameter.type_param_starred_default() is not None
                )
                if defaulted and not has_default:
                    self.psithon_error(
                        parameter, "non-default type parameter follows default"
                    )
                defaulted |= has_default
        elif rule == "strings":
            self.psithon_literal(node)
        elif rule in {"fstring", "tstring"}:
            self.psithon_interpolated_literal(node)
        elif rule == "fstring_conversion" and node.name().getText() not in {
            "s",
            "r",
            "a",
        }:
            self.psithon_error(
                node, "invalid interpolation conversion; expected s, r or a"
            )
        if rule in {
            "annotation",
            "star_annotation",
            "type_param_bound",
            "type_param_default",
            "type_param_starred_default",
        }:
            self.psithon_restricted_expression(node)
        elif (
            rule in {"assignment", "function_def_raw", "type_alias"}
            and node.expression() is not None
        ):
            self.psithon_restricted_expression(node.expression())
        elif (
            rule == "class_def_raw"
            and node.type_params() is not None
            and node.arguments() is not None
        ):
            self.psithon_restricted_expression(node.arguments())
        if rule in {
            "single_subscript_attribute_target",
            "target_with_star_atom",
            "del_target",
        }:
            name = node.getTypedRuleContext(self.NameContext, 0)
            if name is not None and self.psithon_name(name) == "__debug__":
                self.psithon_error(name, "cannot assign to or delete __debug__")

}

// Tree-dependent constraints run inside the generated parser, after successful
// syntax recognition. This permits forward binding checks without CPython.
file_input
    : statements? EOF
      {(self.psithon_validate_input($ctx) if self.psithon_deferred() else self.psithon_constraints($ctx)) if self.getNumberOfSyntaxErrors() == 0 else None}
    ;

statement
    : psithon_statement
    | compound_stmt
    | simple_stmts
    ;

psithon_statement
    : native_expression NEWLINE?
    ;

// '=' and optional names follow the permissive headers in inputparser.py.
molecule_block
    : PSI_MOLECULE header_space* molecule_name? D_NEWLINE* D_LBRACE molecule_body D_RBRACE
    ;
molecule_name
    : {self._input.LT(1).text.isidentifier()}? native_word
    ;
molecule_body
    : D_NEWLINE* (molecule_line D_NEWLINE+)* molecule_line?
    | D_NEWLINE* xyz_header D_NEWLINE literal_line? D_NEWLINE
      (D_NEWLINE | atom_line D_NEWLINE)* atom_line?
    ;
molecule_line
    : D_UNITS D_EQUALS* unit_name
    | D_SYMMETRY D_EQUALS* native_word
    | D_NO_COM
    | D_NO_REORIENT
    | D_SEPARATOR
    | D_PUBCHEM D_COLON literal_line
    | D_FROM_FILE D_COLON literal_line
    | efp_fragment
    | charge_multiplicity
    | geometry_variable
    | atom_line
    ;
xyz_header
    : D_NUMBER native_word?
    ;
charge_multiplicity
    : D_NUMBER D_COMMA? D_NUMBER
    ;
geometry_variable
    : D_MINUS? native_word D_EQUALS (D_NUMBER | native_word)
    ;
unit_name
    : native_word (D_DOT native_word D_DOT)?
    ;
atom_line
    : nucleus
      (D_COMMA? coordinate D_COMMA? coordinate D_COMMA? coordinate
      | anchor_pair (anchor_pair anchor_pair?)?)?
    ;
nucleus
    : D_AT? nucleus_label isotope_mass?
    | D_GHOST D_LPAREN nucleus_label isotope_mass? D_RPAREN
    ;
nucleus_label
    : D_NUMBER? native_word | D_NUMBER
    ;
isotope_mass
    : D_AT D_NUMBER
    ;
coordinate
    : D_NUMBER | D_MINUS? native_word
    ;
anchor_pair
    : D_COMMA? (D_NUMBER | native_word) D_COMMA? coordinate
    ;
efp_fragment
    : D_EFP native_word D_COMMA* numeric_xyz D_COMMA* numeric_xyz
    | D_EFP native_word D_NEWLINE numeric_xyz D_NEWLINE numeric_xyz D_NEWLINE numeric_xyz
    ;
numeric_xyz
    : D_NUMBER D_COMMA* D_NUMBER D_COMMA* D_NUMBER D_COMMA*
    ;

set_command
    : PSI_SET D_NEWLINE* ({self.psithon_inline_module($ctx)}? module_list)?
      option_key D_EQUALS* inline_option_value
    ;
set_block
    : PSI_SET D_NEWLINE* module_list? header_space* D_LBRACE
      D_NEWLINE* (option_assignment D_NEWLINE+)* option_assignment? D_RBRACE
    ;
module_list
    : module_name | module_name? (D_COMMA module_name?)+
    ;
module_name
    : module_piece ({self.psithon_contiguous($ctx)}? module_piece)*
    ;
module_piece
    : native_word | D_NUMBER | D_MINUS | D_SEPARATOR
    ;
option_key
    : {all(c.isalnum() or c == "_" for c in self._input.LT(1).text)}?
      (native_identifier | D_NUMBER)
    ;
option_assignment
    : option_key D_EQUALS* set_option_value
    ;
inline_option_value
    : set_option_array | inline_option_scalar
    ;
// Values retain their physical spelling until the ordered quotify rewrite.
// The projected Python program checks their operators and expression syntax.
set_option_value
    : set_option_piece+
    ;
set_option_array
    : D_LBRACKET (set_option_piece | D_NEWLINE)* D_RBRACKET
    ;
set_option_piece
    : set_option_array
    | D_LPAREN (set_option_piece | D_NEWLINE)* D_RPAREN
    | D_LBRACE (set_option_piece | D_NEWLINE)* D_RBRACE
    | ~(D_NEWLINE | NEWLINE | D_LBRACKET | D_RBRACKET | D_LPAREN | D_RPAREN | D_LBRACE | D_RBRACE)
    ;
inline_option_scalar
    : (option_reference | inline_option_piece)
      ({self.psithon_contiguous($ctx)}? inline_option_piece)*
    ;
inline_option_piece
    : native_word | D_NUMBER | D_MINUS | D_PLUS | D_COMMA | D_STAR | D_COLON
    | D_LPAREN | D_RPAREN | D_DOT
    ;
option_reference
    : D_DOLLAR
      {(self._input.LT(-1).stop + 1 == self._input.LT(1).start
        and self._input.LT(1).text[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")}?
      native_word
    ;
memory_line
    : PSI_MEMORY
    ;

// Every supported basis role uses the same assignment/GBS body. Raw Gaussian
// basis and ECP records are data consumed by Psi4's basis reader, not Python.
basis_block
    : PSI_BASIS header_space* header_label? D_NEWLINE* D_LBRACE
      D_NEWLINE* (basis_line D_NEWLINE+)* basis_line? D_RBRACE
    ;
basis_line
    : basis_assignment | basis_label | basis_record
    ;
basis_assignment
    : D_ASSIGN basis_name
    ;
basis_name
    : (native_word | D_NUMBER | D_MINUS | D_PLUS | D_STAR | D_LPAREN | D_RPAREN | D_COLON)+
    ;
basis_label
    : D_LBRACKET basis_name D_RBRACKET
    ;
basis_record
    : literal_piece+
    ;

external_block
    : PSI_EXTERNAL header_space* header_label? D_NEWLINE* D_LBRACE
      D_NEWLINE* (external_line D_NEWLINE+)* external_line? D_RBRACE
    ;
external_line
    : D_UNITS D_EQUALS* unit_name
    | external_basis_line
    | D_NUMBER D_NUMBER D_NUMBER D_NUMBER
    | nucleus D_NUMBER D_NUMBER D_NUMBER
    | D_SEPARATOR
    ;
external_basis_line
    : external_basis_key D_EQUALS* literal_piece+
    ;
external_basis_key
    : {self._input.LT(1).text.casefold() in {"basis", "df_basis_scf"}}? native_word
    ;

// PCM's outer closing brace must start in column zero, as in inputparser.py.
// The lexer enforces that boundary; nested solver sections remain structured.
pcm_block
    : PSI_PCM header_space* header_label? D_NEWLINE* D_LBRACE pcm_body D_RBRACE
    ;
pcm_body
    : (D_LBRACE pcm_body D_RBRACE | ~(D_LBRACE | D_RBRACE))*
    ;
cfour_block
    : PSI_CFOUR header_space* header_label? D_NEWLINE* D_LBRACE CFOUR_TEXT? D_RBRACE
    ;
header_label
    : native_word | D_NUMBER
    ;
header_space
    : D_EQUALS | D_NEWLINE
    ;

native_word
    : native_identifier | D_HYPHEN_WORD
    ;
native_identifier
    : D_WORD | D_UNITS | D_NO_COM | D_NO_REORIENT | D_SYMMETRY
    | D_PUBCHEM | D_FROM_FILE | D_EFP | D_GHOST | D_ASSIGN
    ;
literal_line
    : literal_piece+
    ;
literal_piece
    : ~(D_NEWLINE | NEWLINE | D_RBRACE)
    ;

// Parameter productions must distinguish a comma from an omitted separator at
// the final delimiter. Unconditional optional commas accept `def f(a b): ...`.
param_end
    : ',' TYPE_COMMENT? | TYPE_COMMENT? {self._input.LA(1) == self.RPAR}?
    ;
slash_end
    : ',' | {self._input.LA(1) == self.RPAR}?
    ;
param_no_default
    : param param_end
    ;
param_no_default_star_annotation
    : param_star_annotation param_end
    ;
param_with_default
    : param default_assignment param_end
    ;
param_maybe_default
    : param default_assignment? param_end
    ;
slash_no_default
    : param_no_default+ '/' slash_end
    ;
slash_with_default
    : param_no_default* param_with_default+ '/' slash_end
    ;
lambda_param_end
    : ',' | {self._input.LA(1) == self.COLON}?
    ;
lambda_param_no_default
    : lambda_param lambda_param_end
    ;
lambda_param_with_default
    : lambda_param default_assignment lambda_param_end
    ;
lambda_param_maybe_default
    : lambda_param default_assignment? lambda_param_end
    ;
lambda_slash_no_default
    : lambda_param_no_default+ '/' lambda_param_end
    ;
lambda_slash_with_default
    : lambda_param_no_default* lambda_param_with_default+ '/' lambda_param_end
    ;

// Python 3.15 additions to the complete imported Python 3.14 grammar.
import_name
    : NAME_OR_LAZY? 'import' dotted_as_names
    ;
import_from
    : NAME_OR_LAZY? 'from' ('.' | '...')* dotted_name 'import' import_from_targets
    | NAME_OR_LAZY? 'from' ('.' | '...')+ 'import' import_from_targets
    ;
name_except_underscore
    : NAME | NAME_OR_TYPE | NAME_OR_MATCH | NAME_OR_CASE | NAME_OR_LAZY
    ;
noteq_bitwise_or
    : ('!=' | PSI_BARRY_NOTEQUAL) bitwise_or
    ;
genexp
    : '(' (assignment_expression | expression | starred_expression) for_if_clauses ')'
    ;
dictcomp
    : LBRACE (kvpair | '**' expression) for_if_clauses RBRACE
    ;
listcomp
    : '[' star_named_expression for_if_clauses ']'
    ;
setcomp
    : LBRACE star_named_expression for_if_clauses RBRACE
    ;

// Context restrictions belong to the combined grammar. No separate Python
// compiler is used by the thin parser entry point to enforce these rules.
return_stmt
    : {(self.psithon_deferred() or self.psithon_scope($ctx) in {"function", "async"})}? 'return' star_expressions?
    ;
break_stmt
    : {(self.psithon_deferred() or self.psithon_loop($ctx))}? 'break'
    ;
continue_stmt
    : {(self.psithon_deferred() or self.psithon_loop($ctx))}? 'continue'
    ;
yield_expr
    : {(self.psithon_deferred() or self.psithon_scope($ctx) in {"function", "async", "lambda"})}? 'yield'
      ({(self.psithon_deferred() or self.psithon_scope($ctx) != "async")}? 'from' expression | star_expressions?)
    ;
await_primary
    : {(self.psithon_deferred() or self.psithon_scope($ctx) in {"async", "generator", "async_comprehension"})}? 'await' primary
    | primary
    ;
for_stmt
    : {(self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope($ctx) == "async")}?
      'async'? 'for' star_targets 'in' star_expressions ':' TYPE_COMMENT? block else_block?
    ;
with_stmt
    : {(self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope($ctx) == "async")}?
      ('with' '(' with_item (',' with_item)* ','? ')' ':' TYPE_COMMENT? block
      | 'async' 'with' '(' with_item (',' with_item)* ','? ')' ':' block
      | 'async'? 'with' with_item (',' with_item)* ':' TYPE_COMMENT? block)
    ;

// Native rewrites can produce a single Python call inside an expression.
// Recognition of the projected job rejects placements that produce multiple
// statements, invalid argument order or malformed interpolation fields.
native_expression
    : set_command
    | set_block
    | molecule_block
    | basis_block
    | external_block
    | pcm_block
    | cfour_block
    ;
atom
    : native_expression
    | memory_line
    | name
    | 'True'
    | 'False'
    | 'None'
    | strings
    | NUMBER
    | (tuple | group | genexp)
    | (list | listcomp)
    | (dict | set | dictcomp | setcomp)
    | '...'
    ;
