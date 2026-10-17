# Generated from grammar/PsithonParser.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


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


def serializedATN():
    return [
        4,1,151,3043,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,
        7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,
        13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,
        20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,
        26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,
        33,7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,
        39,2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,45,2,
        46,7,46,2,47,7,47,2,48,7,48,2,49,7,49,2,50,7,50,2,51,7,51,2,52,7,
        52,2,53,7,53,2,54,7,54,2,55,7,55,2,56,7,56,2,57,7,57,2,58,7,58,2,
        59,7,59,2,60,7,60,2,61,7,61,2,62,7,62,2,63,7,63,2,64,7,64,2,65,7,
        65,2,66,7,66,2,67,7,67,2,68,7,68,2,69,7,69,2,70,7,70,2,71,7,71,2,
        72,7,72,2,73,7,73,2,74,7,74,2,75,7,75,2,76,7,76,2,77,7,77,2,78,7,
        78,2,79,7,79,2,80,7,80,2,81,7,81,2,82,7,82,2,83,7,83,2,84,7,84,2,
        85,7,85,2,86,7,86,2,87,7,87,2,88,7,88,2,89,7,89,2,90,7,90,2,91,7,
        91,2,92,7,92,2,93,7,93,2,94,7,94,2,95,7,95,2,96,7,96,2,97,7,97,2,
        98,7,98,2,99,7,99,2,100,7,100,2,101,7,101,2,102,7,102,2,103,7,103,
        2,104,7,104,2,105,7,105,2,106,7,106,2,107,7,107,2,108,7,108,2,109,
        7,109,2,110,7,110,2,111,7,111,2,112,7,112,2,113,7,113,2,114,7,114,
        2,115,7,115,2,116,7,116,2,117,7,117,2,118,7,118,2,119,7,119,2,120,
        7,120,2,121,7,121,2,122,7,122,2,123,7,123,2,124,7,124,2,125,7,125,
        2,126,7,126,2,127,7,127,2,128,7,128,2,129,7,129,2,130,7,130,2,131,
        7,131,2,132,7,132,2,133,7,133,2,134,7,134,2,135,7,135,2,136,7,136,
        2,137,7,137,2,138,7,138,2,139,7,139,2,140,7,140,2,141,7,141,2,142,
        7,142,2,143,7,143,2,144,7,144,2,145,7,145,2,146,7,146,2,147,7,147,
        2,148,7,148,2,149,7,149,2,150,7,150,2,151,7,151,2,152,7,152,2,153,
        7,153,2,154,7,154,2,155,7,155,2,156,7,156,2,157,7,157,2,158,7,158,
        2,159,7,159,2,160,7,160,2,161,7,161,2,162,7,162,2,163,7,163,2,164,
        7,164,2,165,7,165,2,166,7,166,2,167,7,167,2,168,7,168,2,169,7,169,
        2,170,7,170,2,171,7,171,2,172,7,172,2,173,7,173,2,174,7,174,2,175,
        7,175,2,176,7,176,2,177,7,177,2,178,7,178,2,179,7,179,2,180,7,180,
        2,181,7,181,2,182,7,182,2,183,7,183,2,184,7,184,2,185,7,185,2,186,
        7,186,2,187,7,187,2,188,7,188,2,189,7,189,2,190,7,190,2,191,7,191,
        2,192,7,192,2,193,7,193,2,194,7,194,2,195,7,195,2,196,7,196,2,197,
        7,197,2,198,7,198,2,199,7,199,2,200,7,200,2,201,7,201,2,202,7,202,
        2,203,7,203,2,204,7,204,2,205,7,205,2,206,7,206,2,207,7,207,2,208,
        7,208,2,209,7,209,2,210,7,210,2,211,7,211,2,212,7,212,2,213,7,213,
        2,214,7,214,2,215,7,215,2,216,7,216,2,217,7,217,2,218,7,218,2,219,
        7,219,2,220,7,220,2,221,7,221,2,222,7,222,2,223,7,223,2,224,7,224,
        2,225,7,225,2,226,7,226,2,227,7,227,2,228,7,228,2,229,7,229,2,230,
        7,230,2,231,7,231,2,232,7,232,2,233,7,233,2,234,7,234,2,235,7,235,
        2,236,7,236,2,237,7,237,2,238,7,238,2,239,7,239,2,240,7,240,2,241,
        7,241,2,242,7,242,2,243,7,243,2,244,7,244,2,245,7,245,2,246,7,246,
        2,247,7,247,2,248,7,248,2,249,7,249,2,250,7,250,2,251,7,251,2,252,
        7,252,2,253,7,253,2,254,7,254,2,255,7,255,2,256,7,256,2,257,7,257,
        2,258,7,258,2,259,7,259,1,0,3,0,522,8,0,1,0,1,0,1,0,1,1,1,1,1,1,
        3,1,530,8,1,1,2,1,2,3,2,534,8,2,1,3,1,3,5,3,538,8,3,10,3,12,3,541,
        9,3,1,3,3,3,544,8,3,1,3,5,3,547,8,3,10,3,12,3,550,9,3,1,3,1,3,1,
        3,1,3,1,4,1,4,1,4,1,5,5,5,560,8,5,10,5,12,5,563,9,5,1,5,1,5,4,5,
        567,8,5,11,5,12,5,568,5,5,571,8,5,10,5,12,5,574,9,5,1,5,3,5,577,
        8,5,1,5,5,5,580,8,5,10,5,12,5,583,9,5,1,5,1,5,1,5,3,5,588,8,5,1,
        5,1,5,1,5,1,5,1,5,5,5,595,8,5,10,5,12,5,598,9,5,1,5,3,5,601,8,5,
        3,5,603,8,5,1,6,1,6,5,6,607,8,6,10,6,12,6,610,9,6,1,6,1,6,1,6,5,
        6,615,8,6,10,6,12,6,618,9,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,
        1,6,1,6,1,6,1,6,1,6,3,6,634,8,6,1,7,1,7,3,7,638,8,7,1,8,1,8,3,8,
        642,8,8,1,8,1,8,1,9,3,9,647,8,9,1,9,1,9,1,9,1,9,3,9,653,8,9,1,10,
        1,10,1,10,1,10,1,10,3,10,660,8,10,1,11,1,11,3,11,664,8,11,1,11,1,
        11,3,11,668,8,11,1,11,1,11,3,11,672,8,11,1,11,1,11,1,11,1,11,1,11,
        3,11,679,8,11,3,11,681,8,11,3,11,683,8,11,1,12,3,12,686,8,12,1,12,
        1,12,3,12,690,8,12,1,12,1,12,1,12,1,12,3,12,696,8,12,1,12,1,12,3,
        12,700,8,12,1,13,3,13,703,8,13,1,13,1,13,3,13,707,8,13,1,14,1,14,
        1,14,1,15,1,15,3,15,714,8,15,1,15,3,15,717,8,15,1,16,3,16,720,8,
        16,1,16,1,16,3,16,724,8,16,1,16,3,16,727,8,16,1,16,1,16,1,17,1,17,
        1,17,5,17,734,8,17,10,17,12,17,737,9,17,1,17,1,17,5,17,741,8,17,
        10,17,12,17,744,9,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,
        1,17,1,17,3,17,757,8,17,1,18,1,18,5,18,761,8,18,10,18,12,18,764,
        9,18,1,18,1,18,5,18,768,8,18,10,18,12,18,771,9,18,1,18,1,18,5,18,
        775,8,18,10,18,12,18,778,9,18,1,19,1,19,5,19,782,8,19,10,19,12,19,
        785,9,19,1,19,1,19,3,19,789,8,19,1,19,1,19,5,19,793,8,19,10,19,12,
        19,796,9,19,1,19,1,19,1,20,1,20,5,20,802,8,20,10,20,12,20,805,9,
        20,1,20,3,20,808,8,20,1,20,5,20,811,8,20,10,20,12,20,814,9,20,1,
        20,1,20,5,20,818,8,20,10,20,12,20,821,9,20,1,20,1,20,4,20,825,8,
        20,11,20,12,20,826,5,20,829,8,20,10,20,12,20,832,9,20,1,20,3,20,
        835,8,20,1,20,1,20,1,21,1,21,3,21,841,8,21,1,21,1,21,3,21,845,8,
        21,4,21,847,8,21,11,21,12,21,848,3,21,851,8,21,1,22,1,22,1,22,5,
        22,856,8,22,10,22,12,22,859,9,22,1,23,1,23,1,23,1,23,3,23,865,8,
        23,1,24,1,24,1,24,3,24,870,8,24,1,25,1,25,5,25,874,8,25,10,25,12,
        25,877,9,25,1,25,1,25,1,26,1,26,3,26,883,8,26,1,27,4,27,886,8,27,
        11,27,12,27,887,1,28,1,28,1,28,5,28,893,8,28,10,28,12,28,896,9,28,
        1,28,1,28,1,29,1,29,1,29,1,29,5,29,904,8,29,10,29,12,29,907,9,29,
        1,29,1,29,1,29,1,29,5,29,913,8,29,10,29,12,29,916,9,29,1,29,1,29,
        3,29,920,8,29,1,30,1,30,3,30,924,8,30,1,30,1,30,5,30,928,8,30,10,
        30,12,30,931,9,30,1,31,1,31,1,31,1,31,1,31,1,31,1,31,1,31,1,31,1,
        31,3,31,943,8,31,1,32,1,32,1,32,1,32,1,33,1,33,1,34,1,34,5,34,953,
        8,34,10,34,12,34,956,9,34,1,34,3,34,959,8,34,1,34,5,34,962,8,34,
        10,34,12,34,965,9,34,1,34,1,34,5,34,969,8,34,10,34,12,34,972,9,34,
        1,34,1,34,4,34,976,8,34,11,34,12,34,977,5,34,980,8,34,10,34,12,34,
        983,9,34,1,34,3,34,986,8,34,1,34,1,34,1,35,1,35,1,35,3,35,993,8,
        35,1,36,1,36,1,36,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,4,37,1006,
        8,37,11,37,12,37,1007,1,38,1,38,1,38,1,38,1,39,4,39,1015,8,39,11,
        39,12,39,1016,1,40,1,40,5,40,1021,8,40,10,40,12,40,1024,9,40,1,40,
        3,40,1027,8,40,1,40,5,40,1030,8,40,10,40,12,40,1033,9,40,1,40,1,
        40,5,40,1037,8,40,10,40,12,40,1040,9,40,1,40,1,40,4,40,1044,8,40,
        11,40,12,40,1045,5,40,1048,8,40,10,40,12,40,1051,9,40,1,40,3,40,
        1054,8,40,1,40,1,40,1,41,1,41,5,41,1060,8,41,10,41,12,41,1063,9,
        41,1,41,1,41,1,41,1,41,1,41,1,41,1,41,1,41,1,41,1,41,1,41,1,41,3,
        41,1077,8,41,1,42,1,42,5,42,1081,8,42,10,42,12,42,1084,9,42,1,42,
        4,42,1087,8,42,11,42,12,42,1088,1,43,1,43,1,43,1,44,1,44,5,44,1096,
        8,44,10,44,12,44,1099,9,44,1,44,3,44,1102,8,44,1,44,5,44,1105,8,
        44,10,44,12,44,1108,9,44,1,44,1,44,1,44,1,44,1,45,1,45,1,45,1,45,
        1,45,5,45,1119,8,45,10,45,12,45,1122,9,45,1,46,1,46,5,46,1126,8,
        46,10,46,12,46,1129,9,46,1,46,3,46,1132,8,46,1,46,5,46,1135,8,46,
        10,46,12,46,1138,9,46,1,46,1,46,3,46,1142,8,46,1,46,1,46,1,47,1,
        47,3,47,1148,8,47,1,48,1,48,1,49,1,49,3,49,1154,8,49,1,50,1,50,1,
        51,4,51,1159,8,51,11,51,12,51,1160,1,52,1,52,1,53,1,53,3,53,1167,
        8,53,1,53,3,53,1170,8,53,1,53,3,53,1173,8,53,1,54,1,54,3,54,1177,
        8,54,1,55,1,55,1,55,1,56,1,56,1,56,1,57,1,57,1,57,1,57,1,58,1,58,
        3,58,1191,8,58,1,58,1,58,1,59,4,59,1196,8,59,11,59,12,59,1197,1,
        59,1,59,1,59,1,60,5,60,1204,8,60,10,60,12,60,1207,9,60,1,60,4,60,
        1210,8,60,11,60,12,60,1211,1,60,1,60,1,60,1,61,1,61,3,61,1219,8,
        61,1,62,1,62,1,62,1,63,1,63,1,63,1,63,1,64,1,64,3,64,1230,8,64,1,
        64,1,64,1,65,4,65,1235,8,65,11,65,12,65,1236,1,65,1,65,1,65,1,66,
        5,66,1243,8,66,10,66,12,66,1246,9,66,1,66,4,66,1249,8,66,11,66,12,
        66,1250,1,66,1,66,1,66,1,67,3,67,1257,8,67,1,67,1,67,1,67,1,68,3,
        68,1263,8,68,1,68,1,68,5,68,1267,8,68,10,68,12,68,1270,9,68,1,68,
        1,68,1,68,1,68,1,68,3,68,1277,8,68,1,68,1,68,4,68,1281,8,68,11,68,
        12,68,1282,1,68,1,68,3,68,1287,8,68,1,69,1,69,1,70,1,70,1,70,1,71,
        1,71,1,71,1,71,3,71,1298,8,71,1,71,1,71,1,71,1,72,1,72,1,72,1,72,
        3,72,1307,8,72,1,72,1,72,1,72,1,73,1,73,1,73,1,73,1,73,1,74,1,74,
        1,74,1,74,1,74,1,75,1,75,1,75,3,75,1325,8,75,1,76,1,76,1,76,1,77,
        1,77,1,77,1,78,1,78,1,78,1,78,1,78,1,78,3,78,1339,8,78,3,78,1341,
        8,78,1,79,1,79,1,79,1,79,3,79,1347,8,79,1,80,1,80,3,80,1351,8,80,
        1,80,1,80,1,80,1,80,1,80,1,80,3,80,1359,8,80,1,80,1,80,3,80,1363,
        8,80,1,81,1,81,1,81,1,81,1,81,1,81,5,81,1371,8,81,10,81,12,81,1374,
        9,81,1,81,3,81,1377,8,81,1,81,1,81,1,81,3,81,1382,8,81,1,81,1,81,
        1,81,1,81,1,81,1,81,1,81,1,81,5,81,1392,8,81,10,81,12,81,1395,9,
        81,1,81,3,81,1398,8,81,1,81,1,81,1,81,1,81,1,81,3,81,1405,8,81,1,
        81,1,81,1,81,1,81,5,81,1411,8,81,10,81,12,81,1414,9,81,1,81,1,81,
        3,81,1418,8,81,1,81,1,81,3,81,1422,8,81,1,82,1,82,1,82,1,82,1,82,
        1,82,1,82,3,82,1431,8,82,1,83,1,83,1,83,1,83,1,83,1,83,1,83,1,83,
        1,83,1,83,1,83,3,83,1444,8,83,1,83,1,83,3,83,1448,8,83,1,83,1,83,
        1,83,1,83,3,83,1454,8,83,1,83,3,83,1457,8,83,1,84,1,84,1,85,1,85,
        5,85,1463,8,85,10,85,12,85,1466,9,85,1,85,1,85,1,86,1,86,3,86,1472,
        8,86,1,86,1,86,1,86,1,86,5,86,1478,8,86,10,86,12,86,1481,9,86,1,
        86,1,86,1,87,4,87,1486,8,87,11,87,12,87,1487,1,88,1,88,1,89,1,89,
        1,89,1,89,1,89,1,89,3,89,1498,8,89,1,90,1,90,1,90,5,90,1503,8,90,
        10,90,12,90,1506,9,90,1,90,3,90,1509,8,90,1,90,1,90,1,91,1,91,1,
        91,1,91,1,91,1,91,1,91,1,91,1,91,1,91,1,91,1,91,1,91,1,91,3,91,1527,
        8,91,1,92,1,92,1,92,1,92,1,92,1,92,1,92,1,92,3,92,1537,8,92,1,93,
        1,93,1,93,1,93,1,93,3,93,1544,8,93,1,93,1,93,1,93,1,93,1,93,3,93,
        1551,8,93,1,93,1,93,1,93,1,93,3,93,1557,8,93,1,93,1,93,1,93,4,93,
        1562,8,93,11,93,12,93,1563,1,93,1,93,3,93,1568,8,93,1,93,1,93,1,
        93,1,93,3,93,1574,8,93,1,94,1,94,3,94,1578,8,94,1,95,1,95,1,96,1,
        96,1,96,1,96,3,96,1586,8,96,3,96,1588,8,96,1,97,1,97,1,98,1,98,1,
        98,1,98,5,98,1596,8,98,10,98,12,98,1599,9,98,1,99,1,99,1,99,1,99,
        5,99,1605,8,99,10,99,12,99,1608,9,99,1,100,1,100,1,100,1,101,1,101,
        1,102,1,102,1,102,1,102,3,102,1619,8,102,1,103,1,103,3,103,1623,
        8,103,1,104,1,104,1,104,3,104,1628,8,104,1,104,1,104,1,104,1,104,
        3,104,1634,8,104,1,105,1,105,1,105,5,105,1639,8,105,10,105,12,105,
        1642,9,105,1,106,1,106,1,106,3,106,1647,8,106,1,107,1,107,1,107,
        5,107,1652,8,107,10,107,12,107,1655,9,107,1,108,1,108,1,108,3,108,
        1660,8,108,1,109,1,109,1,109,1,109,1,109,1,109,5,109,1668,8,109,
        10,109,12,109,1671,9,109,1,110,1,110,1,110,1,110,1,110,1,110,3,110,
        1679,8,110,1,111,1,111,1,111,1,111,4,111,1685,8,111,11,111,12,111,
        1686,1,112,1,112,1,112,1,112,3,112,1693,8,112,1,113,1,113,1,113,
        3,113,1698,8,113,1,113,1,113,3,113,1702,8,113,1,113,3,113,1705,8,
        113,1,113,1,113,1,113,1,114,1,114,1,114,1,114,3,114,1714,8,114,1,
        115,1,115,1,115,3,115,1719,8,115,1,115,1,115,3,115,1723,8,115,1,
        115,1,115,1,115,3,115,1728,8,115,1,115,1,115,3,115,1732,8,115,1,
        115,1,115,1,115,1,115,1,115,1,115,3,115,1740,8,115,1,115,1,115,3,
        115,1744,8,115,1,115,1,115,1,115,3,115,1749,8,115,1,115,1,115,3,
        115,1753,8,115,1,115,1,115,3,115,1757,8,115,1,116,1,116,1,117,1,
        117,5,117,1763,8,117,10,117,12,117,1766,9,117,1,117,5,117,1769,8,
        117,10,117,12,117,1772,9,117,1,117,3,117,1775,8,117,1,117,1,117,
        5,117,1779,8,117,10,117,12,117,1782,9,117,1,117,3,117,1785,8,117,
        1,117,4,117,1788,8,117,11,117,12,117,1789,1,117,5,117,1793,8,117,
        10,117,12,117,1796,9,117,1,117,3,117,1799,8,117,1,117,4,117,1802,
        8,117,11,117,12,117,1803,1,117,3,117,1807,8,117,1,117,3,117,1810,
        8,117,1,118,1,118,1,118,5,118,1815,8,118,10,118,12,118,1818,9,118,
        1,118,3,118,1821,8,118,1,118,1,118,1,118,5,118,1826,8,118,10,118,
        12,118,1829,9,118,1,118,3,118,1832,8,118,1,118,1,118,1,118,4,118,
        1837,8,118,11,118,12,118,1838,1,118,3,118,1842,8,118,1,118,3,118,
        1845,8,118,1,119,1,119,1,119,1,120,1,120,3,120,1852,8,120,1,121,
        1,121,1,121,1,122,1,122,1,122,1,123,1,123,1,123,1,124,1,124,1,124,
        1,125,1,125,1,125,1,125,1,125,1,125,3,125,1872,8,125,3,125,1874,
        8,125,1,126,1,126,1,126,1,126,1,126,1,126,3,126,1882,8,126,3,126,
        1884,8,126,1,127,1,127,1,127,1,127,1,128,1,128,1,128,1,128,1,128,
        3,128,1895,8,128,1,129,1,129,1,129,3,129,1900,8,129,1,130,1,130,
        1,130,1,130,1,130,1,130,1,130,1,130,1,130,4,130,1911,8,130,11,130,
        12,130,1912,1,130,3,130,1916,8,130,1,130,3,130,1919,8,130,1,130,
        1,130,1,130,1,130,4,130,1925,8,130,11,130,12,130,1926,1,130,3,130,
        1930,8,130,1,130,3,130,1933,8,130,3,130,1935,8,130,1,131,1,131,1,
        131,1,131,3,131,1941,8,131,1,131,3,131,1944,8,131,1,131,1,131,1,
        131,1,132,1,132,1,132,1,132,1,132,3,132,1954,8,132,1,132,3,132,1957,
        8,132,1,132,1,132,1,132,1,133,1,133,1,133,1,133,1,134,1,134,1,134,
        1,134,1,134,1,134,4,134,1972,8,134,11,134,12,134,1973,1,134,1,134,
        1,135,1,135,1,135,3,135,1981,8,135,1,135,3,135,1984,8,135,1,136,
        1,136,1,136,3,136,1989,8,136,1,136,1,136,1,136,1,137,1,137,1,137,
        1,138,1,138,3,138,1999,8,138,1,139,1,139,3,139,2003,8,139,1,140,
        1,140,1,140,1,140,1,141,1,141,1,141,5,141,2012,8,141,10,141,12,141,
        2015,9,141,1,142,1,142,1,142,1,142,1,142,1,142,1,142,1,142,3,142,
        2025,8,142,1,143,1,143,1,143,1,143,1,143,1,143,3,143,2033,8,143,
        1,144,1,144,1,144,1,144,1,144,1,144,3,144,2041,8,144,1,145,1,145,
        1,145,1,145,1,146,3,146,2048,8,146,1,146,1,146,1,147,3,147,2053,
        8,147,1,147,1,147,1,148,1,148,1,149,1,149,1,150,1,150,1,151,1,151,
        1,152,1,152,1,153,1,153,1,154,1,154,1,154,4,154,2072,8,154,11,154,
        12,154,2073,1,155,1,155,1,155,5,155,2079,8,155,10,155,12,155,2082,
        9,155,1,156,1,156,1,156,1,156,1,157,1,157,3,157,2090,8,157,1,157,
        1,157,1,157,3,157,2095,8,157,1,157,3,157,2098,8,157,1,158,1,158,
        1,158,3,158,2103,8,158,1,159,1,159,1,159,5,159,2108,8,159,10,159,
        12,159,2111,9,159,1,159,3,159,2114,8,159,1,160,1,160,3,160,2118,
        8,160,1,161,1,161,1,161,1,162,1,162,1,162,1,162,1,162,3,162,2128,
        8,162,1,162,1,162,1,162,1,162,1,162,1,162,3,162,2136,8,162,1,162,
        3,162,2139,8,162,1,162,1,162,3,162,2143,8,162,1,163,1,163,1,163,
        5,163,2148,8,163,10,163,12,163,2151,9,163,1,164,1,164,3,164,2155,
        8,164,1,164,1,164,1,164,1,165,1,165,1,165,1,166,1,166,1,166,1,166,
        1,166,3,166,2168,8,166,1,166,3,166,2171,8,166,1,166,3,166,2174,8,
        166,3,166,2176,8,166,1,166,1,166,1,167,1,167,1,167,5,167,2183,8,
        167,10,167,12,167,2186,9,167,1,168,1,168,1,168,5,168,2191,8,168,
        10,168,12,168,2194,9,168,1,169,1,169,1,169,1,169,1,170,1,170,1,170,
        3,170,2203,8,170,1,170,1,170,1,170,1,171,1,171,1,171,1,171,1,172,
        1,172,1,172,5,172,2215,8,172,10,172,12,172,2218,9,172,1,172,3,172,
        2221,8,172,1,173,1,173,3,173,2225,8,173,1,173,3,173,2228,8,173,1,
        173,1,173,1,173,3,173,2233,8,173,1,173,1,173,1,173,3,173,2238,8,
        173,3,173,2240,8,173,1,174,1,174,1,174,1,175,1,175,1,175,1,176,1,
        176,1,176,1,177,1,177,1,177,5,177,2254,8,177,10,177,12,177,2257,
        9,177,1,177,3,177,2260,8,177,1,178,1,178,1,178,1,178,1,178,1,178,
        3,178,2268,8,178,1,178,3,178,2271,8,178,1,179,1,179,1,179,5,179,
        2276,8,179,10,179,12,179,2279,9,179,1,179,3,179,2282,8,179,1,180,
        1,180,1,180,3,180,2287,8,180,1,181,1,181,1,181,5,181,2292,8,181,
        10,181,12,181,2295,9,181,1,181,3,181,2298,8,181,1,182,1,182,1,182,
        3,182,2303,8,182,1,183,1,183,1,183,1,183,1,184,1,184,3,184,2311,
        8,184,1,185,1,185,1,185,5,185,2316,8,185,10,185,12,185,2319,9,185,
        1,186,1,186,1,186,5,186,2324,8,186,10,186,12,186,2327,9,186,1,187,
        1,187,1,187,3,187,2332,8,187,1,188,1,188,5,188,2336,8,188,10,188,
        12,188,2339,9,188,1,189,1,189,1,189,1,189,1,189,1,189,1,189,1,189,
        1,189,1,189,3,189,2351,8,189,1,190,1,190,1,190,1,191,1,191,1,191,
        1,192,1,192,1,192,1,193,1,193,1,193,1,194,1,194,1,194,1,195,1,195,
        1,195,1,195,1,196,1,196,1,196,1,197,1,197,1,197,1,197,1,198,1,198,
        1,198,1,199,1,199,1,199,1,199,1,199,1,199,5,199,2388,8,199,10,199,
        12,199,2391,9,199,1,200,1,200,1,200,1,200,1,200,1,200,5,200,2399,
        8,200,10,200,12,200,2402,9,200,1,201,1,201,1,201,1,201,1,201,1,201,
        5,201,2410,8,201,10,201,12,201,2413,9,201,1,202,1,202,1,202,1,202,
        1,202,1,202,5,202,2421,8,202,10,202,12,202,2424,9,202,1,203,1,203,
        1,203,1,203,1,203,1,203,5,203,2432,8,203,10,203,12,203,2435,9,203,
        1,204,1,204,1,204,1,204,1,204,1,204,5,204,2443,8,204,10,204,12,204,
        2446,9,204,1,205,1,205,1,205,1,205,1,205,1,205,1,205,3,205,2455,
        8,205,1,206,1,206,1,206,3,206,2460,8,206,1,207,1,207,1,207,1,207,
        1,207,1,207,1,207,1,207,1,207,3,207,2471,8,207,1,207,1,207,1,207,
        1,207,1,207,3,207,2478,8,207,5,207,2480,8,207,10,207,12,207,2483,
        9,207,1,208,1,208,1,208,3,208,2488,8,208,1,208,1,208,1,208,3,208,
        2493,8,208,5,208,2495,8,208,10,208,12,208,2498,9,208,1,208,3,208,
        2501,8,208,3,208,2503,8,208,1,209,3,209,2506,8,209,1,209,1,209,3,
        209,2510,8,209,1,209,1,209,3,209,2514,8,209,3,209,2516,8,209,1,209,
        3,209,2519,8,209,1,210,1,210,1,210,3,210,2524,8,210,1,210,1,210,
        1,211,1,211,3,211,2530,8,211,1,211,1,211,1,211,1,212,1,212,1,213,
        1,213,5,213,2539,8,213,10,213,12,213,2542,9,213,1,213,5,213,2545,
        8,213,10,213,12,213,2548,9,213,1,213,3,213,2551,8,213,1,213,1,213,
        5,213,2555,8,213,10,213,12,213,2558,9,213,1,213,3,213,2561,8,213,
        1,213,4,213,2564,8,213,11,213,12,213,2565,1,213,5,213,2569,8,213,
        10,213,12,213,2572,9,213,1,213,3,213,2575,8,213,1,213,4,213,2578,
        8,213,11,213,12,213,2579,1,213,3,213,2583,8,213,1,213,3,213,2586,
        8,213,1,214,1,214,1,214,5,214,2591,8,214,10,214,12,214,2594,9,214,
        1,214,3,214,2597,8,214,1,214,1,214,1,214,4,214,2602,8,214,11,214,
        12,214,2603,1,214,3,214,2607,8,214,1,214,3,214,2610,8,214,1,215,
        1,215,1,215,1,216,1,216,1,217,1,217,3,217,2619,8,217,1,218,1,218,
        1,218,3,218,2624,8,218,1,218,3,218,2627,8,218,1,218,3,218,2630,8,
        218,1,218,1,218,1,219,1,219,1,219,1,220,1,220,5,220,2639,8,220,10,
        220,12,220,2642,9,220,1,221,1,221,3,221,2646,8,221,1,222,1,222,5,
        222,2650,8,222,10,222,12,222,2653,9,222,1,222,1,222,1,223,1,223,
        3,223,2659,8,223,1,224,1,224,5,224,2663,8,224,10,224,12,224,2666,
        9,224,1,225,1,225,1,225,3,225,2671,8,225,1,225,3,225,2674,8,225,
        1,225,3,225,2677,8,225,1,225,1,225,1,226,1,226,3,226,2683,8,226,
        1,227,1,227,5,227,2687,8,227,10,227,12,227,2690,9,227,1,227,1,227,
        1,228,1,228,1,229,1,229,4,229,2698,8,229,11,229,12,229,2699,1,229,
        4,229,2703,8,229,11,229,12,229,2704,3,229,2707,8,229,1,230,1,230,
        3,230,2711,8,230,1,230,1,230,1,231,1,231,1,231,1,231,3,231,2719,
        8,231,3,231,2721,8,231,1,231,1,231,1,232,1,232,1,232,1,232,1,233,
        1,233,3,233,2731,8,233,1,233,1,233,1,234,1,234,1,234,5,234,2738,
        8,234,10,234,12,234,2741,9,234,1,234,3,234,2744,8,234,1,235,1,235,
        1,235,3,235,2749,8,235,1,236,1,236,1,236,1,236,1,237,4,237,2756,
        8,237,11,237,12,237,2757,1,238,3,238,2761,8,238,1,238,1,238,1,238,
        1,238,1,238,1,238,5,238,2769,8,238,10,238,12,238,2772,9,238,1,239,
        1,239,3,239,2776,8,239,1,240,1,240,1,240,3,240,2781,8,240,3,240,
        2783,8,240,1,240,1,240,1,240,1,240,3,240,2789,8,240,3,240,2791,8,
        240,5,240,2793,8,240,10,240,12,240,2796,9,240,1,240,1,240,3,240,
        2800,8,240,1,240,3,240,2803,8,240,1,241,1,241,1,241,5,241,2808,8,
        241,10,241,12,241,2811,9,241,1,241,1,241,1,241,1,241,5,241,2817,
        8,241,10,241,12,241,2820,9,241,3,241,2822,8,241,1,241,1,241,1,241,
        5,241,2827,8,241,10,241,12,241,2830,9,241,3,241,2832,8,241,1,242,
        1,242,1,242,1,243,1,243,1,243,1,243,1,243,3,243,2842,8,243,1,244,
        1,244,1,244,1,244,1,244,1,244,3,244,2850,8,244,1,245,1,245,1,245,
        5,245,2855,8,245,10,245,12,245,2858,9,245,1,245,3,245,2861,8,245,
        1,246,1,246,1,246,5,246,2866,8,246,10,246,12,246,2869,9,246,1,246,
        3,246,2872,8,246,1,247,1,247,1,247,1,247,4,247,2878,8,247,11,247,
        12,247,2879,1,247,3,247,2883,8,247,3,247,2885,8,247,1,248,1,248,
        1,248,3,248,2890,8,248,1,249,1,249,1,249,1,249,1,249,1,249,1,249,
        3,249,2899,8,249,1,249,3,249,2902,8,249,1,250,1,250,1,250,1,250,
        1,250,1,250,1,250,3,250,2911,8,250,1,250,1,250,1,250,3,250,2916,
        8,250,1,250,3,250,2919,8,250,1,251,1,251,1,251,1,251,1,251,1,251,
        3,251,2927,8,251,1,252,1,252,1,252,1,252,1,252,1,252,1,252,3,252,
        2936,8,252,1,253,1,253,1,253,1,253,1,253,1,253,1,253,1,253,1,253,
        1,253,1,253,1,253,1,253,3,253,2951,8,253,1,253,3,253,2954,8,253,
        5,253,2956,8,253,10,253,12,253,2959,9,253,1,254,1,254,1,254,5,254,
        2964,8,254,10,254,12,254,2967,9,254,1,254,3,254,2970,8,254,1,255,
        1,255,1,255,1,255,1,255,1,255,1,255,3,255,2979,8,255,1,255,3,255,
        2982,8,255,1,256,1,256,1,256,1,256,1,256,1,256,1,256,3,256,2991,
        8,256,1,256,1,256,1,256,3,256,2996,8,256,1,256,3,256,2999,8,256,
        1,257,1,257,1,257,5,257,3004,8,257,10,257,12,257,3007,9,257,1,257,
        1,257,1,257,1,257,1,257,1,257,3,257,3015,8,257,1,257,1,257,3,257,
        3019,8,257,3,257,3021,8,257,1,257,1,257,1,257,1,257,1,257,3,257,
        3028,8,257,1,257,1,257,3,257,3032,8,257,1,258,1,258,1,258,3,258,
        3037,8,258,1,259,1,259,3,259,3041,8,259,1,259,0,9,218,398,400,402,
        404,406,408,414,506,260,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,
        30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,
        74,76,78,80,82,84,86,88,90,92,94,96,98,100,102,104,106,108,110,112,
        114,116,118,120,122,124,126,128,130,132,134,136,138,140,142,144,
        146,148,150,152,154,156,158,160,162,164,166,168,170,172,174,176,
        178,180,182,184,186,188,190,192,194,196,198,200,202,204,206,208,
        210,212,214,216,218,220,222,224,226,228,230,232,234,236,238,240,
        242,244,246,248,250,252,254,256,258,260,262,264,266,268,270,272,
        274,276,278,280,282,284,286,288,290,292,294,296,298,300,302,304,
        306,308,310,312,314,316,318,320,322,324,326,328,330,332,334,336,
        338,340,342,344,346,348,350,352,354,356,358,360,362,364,366,368,
        370,372,374,376,378,380,382,384,386,388,390,392,394,396,398,400,
        402,404,406,408,410,412,414,416,418,420,422,424,426,428,430,432,
        434,436,438,440,442,444,446,448,450,452,454,456,458,460,462,464,
        466,468,470,472,474,476,478,480,482,484,486,488,490,492,494,496,
        498,500,502,504,506,508,510,512,514,516,518,0,12,2,0,110,110,117,
        123,1,0,118,119,2,0,117,117,124,124,2,0,135,143,145,145,3,0,110,
        110,117,117,119,119,2,0,26,26,65,65,3,0,19,19,103,105,107,107,2,
        0,18,18,41,41,3,0,49,59,61,61,63,63,1,0,30,31,1,0,46,47,4,0,32,33,
        39,39,60,60,62,62,3311,0,521,1,0,0,0,2,529,1,0,0,0,4,531,1,0,0,0,
        6,535,1,0,0,0,8,555,1,0,0,0,10,602,1,0,0,0,12,633,1,0,0,0,14,635,
        1,0,0,0,16,639,1,0,0,0,18,646,1,0,0,0,20,654,1,0,0,0,22,661,1,0,
        0,0,24,699,1,0,0,0,26,706,1,0,0,0,28,708,1,0,0,0,30,716,1,0,0,0,
        32,719,1,0,0,0,34,756,1,0,0,0,36,758,1,0,0,0,38,779,1,0,0,0,40,799,
        1,0,0,0,42,850,1,0,0,0,44,852,1,0,0,0,46,864,1,0,0,0,48,866,1,0,
        0,0,50,871,1,0,0,0,52,882,1,0,0,0,54,885,1,0,0,0,56,889,1,0,0,0,
        58,919,1,0,0,0,60,923,1,0,0,0,62,942,1,0,0,0,64,944,1,0,0,0,66,948,
        1,0,0,0,68,950,1,0,0,0,70,992,1,0,0,0,72,994,1,0,0,0,74,1005,1,0,
        0,0,76,1009,1,0,0,0,78,1014,1,0,0,0,80,1018,1,0,0,0,82,1076,1,0,
        0,0,84,1078,1,0,0,0,86,1090,1,0,0,0,88,1093,1,0,0,0,90,1120,1,0,
        0,0,92,1123,1,0,0,0,94,1147,1,0,0,0,96,1149,1,0,0,0,98,1153,1,0,
        0,0,100,1155,1,0,0,0,102,1158,1,0,0,0,104,1162,1,0,0,0,106,1172,
        1,0,0,0,108,1176,1,0,0,0,110,1178,1,0,0,0,112,1181,1,0,0,0,114,1184,
        1,0,0,0,116,1188,1,0,0,0,118,1195,1,0,0,0,120,1205,1,0,0,0,122,1218,
        1,0,0,0,124,1220,1,0,0,0,126,1223,1,0,0,0,128,1227,1,0,0,0,130,1234,
        1,0,0,0,132,1244,1,0,0,0,134,1256,1,0,0,0,136,1286,1,0,0,0,138,1288,
        1,0,0,0,140,1290,1,0,0,0,142,1293,1,0,0,0,144,1302,1,0,0,0,146,1311,
        1,0,0,0,148,1316,1,0,0,0,150,1321,1,0,0,0,152,1326,1,0,0,0,154,1329,
        1,0,0,0,156,1332,1,0,0,0,158,1346,1,0,0,0,160,1348,1,0,0,0,162,1364,
        1,0,0,0,164,1430,1,0,0,0,166,1456,1,0,0,0,168,1458,1,0,0,0,170,1460,
        1,0,0,0,172,1469,1,0,0,0,174,1485,1,0,0,0,176,1489,1,0,0,0,178,1497,
        1,0,0,0,180,1499,1,0,0,0,182,1526,1,0,0,0,184,1536,1,0,0,0,186,1573,
        1,0,0,0,188,1577,1,0,0,0,190,1579,1,0,0,0,192,1581,1,0,0,0,194,1589,
        1,0,0,0,196,1591,1,0,0,0,198,1600,1,0,0,0,200,1609,1,0,0,0,202,1612,
        1,0,0,0,204,1614,1,0,0,0,206,1622,1,0,0,0,208,1633,1,0,0,0,210,1635,
        1,0,0,0,212,1643,1,0,0,0,214,1648,1,0,0,0,216,1656,1,0,0,0,218,1661,
        1,0,0,0,220,1678,1,0,0,0,222,1684,1,0,0,0,224,1692,1,0,0,0,226,1694,
        1,0,0,0,228,1713,1,0,0,0,230,1756,1,0,0,0,232,1758,1,0,0,0,234,1809,
        1,0,0,0,236,1844,1,0,0,0,238,1846,1,0,0,0,240,1849,1,0,0,0,242,1853,
        1,0,0,0,244,1856,1,0,0,0,246,1859,1,0,0,0,248,1862,1,0,0,0,250,1865,
        1,0,0,0,252,1875,1,0,0,0,254,1885,1,0,0,0,256,1889,1,0,0,0,258,1896,
        1,0,0,0,260,1934,1,0,0,0,262,1936,1,0,0,0,264,1948,1,0,0,0,266,1961,
        1,0,0,0,268,1965,1,0,0,0,270,1983,1,0,0,0,272,1985,1,0,0,0,274,1993,
        1,0,0,0,276,1998,1,0,0,0,278,2002,1,0,0,0,280,2004,1,0,0,0,282,2008,
        1,0,0,0,284,2024,1,0,0,0,286,2032,1,0,0,0,288,2040,1,0,0,0,290,2042,
        1,0,0,0,292,2047,1,0,0,0,294,2052,1,0,0,0,296,2056,1,0,0,0,298,2058,
        1,0,0,0,300,2060,1,0,0,0,302,2062,1,0,0,0,304,2064,1,0,0,0,306,2066,
        1,0,0,0,308,2068,1,0,0,0,310,2075,1,0,0,0,312,2083,1,0,0,0,314,2097,
        1,0,0,0,316,2099,1,0,0,0,318,2104,1,0,0,0,320,2117,1,0,0,0,322,2119,
        1,0,0,0,324,2142,1,0,0,0,326,2144,1,0,0,0,328,2154,1,0,0,0,330,2159,
        1,0,0,0,332,2162,1,0,0,0,334,2179,1,0,0,0,336,2187,1,0,0,0,338,2195,
        1,0,0,0,340,2199,1,0,0,0,342,2207,1,0,0,0,344,2211,1,0,0,0,346,2239,
        1,0,0,0,348,2241,1,0,0,0,350,2244,1,0,0,0,352,2247,1,0,0,0,354,2250,
        1,0,0,0,356,2270,1,0,0,0,358,2272,1,0,0,0,360,2286,1,0,0,0,362,2288,
        1,0,0,0,364,2302,1,0,0,0,366,2304,1,0,0,0,368,2310,1,0,0,0,370,2312,
        1,0,0,0,372,2320,1,0,0,0,374,2331,1,0,0,0,376,2333,1,0,0,0,378,2350,
        1,0,0,0,380,2352,1,0,0,0,382,2355,1,0,0,0,384,2358,1,0,0,0,386,2361,
        1,0,0,0,388,2364,1,0,0,0,390,2367,1,0,0,0,392,2371,1,0,0,0,394,2374,
        1,0,0,0,396,2378,1,0,0,0,398,2381,1,0,0,0,400,2392,1,0,0,0,402,2403,
        1,0,0,0,404,2414,1,0,0,0,406,2425,1,0,0,0,408,2436,1,0,0,0,410,2454,
        1,0,0,0,412,2456,1,0,0,0,414,2461,1,0,0,0,416,2502,1,0,0,0,418,2518,
        1,0,0,0,420,2520,1,0,0,0,422,2527,1,0,0,0,424,2534,1,0,0,0,426,2585,
        1,0,0,0,428,2609,1,0,0,0,430,2611,1,0,0,0,432,2614,1,0,0,0,434,2618,
        1,0,0,0,436,2620,1,0,0,0,438,2633,1,0,0,0,440,2636,1,0,0,0,442,2645,
        1,0,0,0,444,2647,1,0,0,0,446,2658,1,0,0,0,448,2660,1,0,0,0,450,2667,
        1,0,0,0,452,2682,1,0,0,0,454,2684,1,0,0,0,456,2693,1,0,0,0,458,2706,
        1,0,0,0,460,2708,1,0,0,0,462,2714,1,0,0,0,464,2724,1,0,0,0,466,2728,
        1,0,0,0,468,2734,1,0,0,0,470,2748,1,0,0,0,472,2750,1,0,0,0,474,2755,
        1,0,0,0,476,2760,1,0,0,0,478,2773,1,0,0,0,480,2802,1,0,0,0,482,2831,
        1,0,0,0,484,2833,1,0,0,0,486,2841,1,0,0,0,488,2849,1,0,0,0,490,2851,
        1,0,0,0,492,2862,1,0,0,0,494,2873,1,0,0,0,496,2889,1,0,0,0,498,2901,
        1,0,0,0,500,2918,1,0,0,0,502,2926,1,0,0,0,504,2928,1,0,0,0,506,2937,
        1,0,0,0,508,2960,1,0,0,0,510,2981,1,0,0,0,512,2998,1,0,0,0,514,3031,
        1,0,0,0,516,3036,1,0,0,0,518,3040,1,0,0,0,520,522,3,174,87,0,521,
        520,1,0,0,0,521,522,1,0,0,0,522,523,1,0,0,0,523,524,5,0,0,1,524,
        525,6,0,-1,0,525,1,1,0,0,0,526,530,3,4,2,0,527,530,3,184,92,0,528,
        530,3,180,90,0,529,526,1,0,0,0,529,527,1,0,0,0,529,528,1,0,0,0,530,
        3,1,0,0,0,531,533,3,164,82,0,532,534,5,110,0,0,533,532,1,0,0,0,533,
        534,1,0,0,0,534,5,1,0,0,0,535,539,5,11,0,0,536,538,3,96,48,0,537,
        536,1,0,0,0,538,541,1,0,0,0,539,537,1,0,0,0,539,540,1,0,0,0,540,
        543,1,0,0,0,541,539,1,0,0,0,542,544,3,8,4,0,543,542,1,0,0,0,543,
        544,1,0,0,0,544,548,1,0,0,0,545,547,5,117,0,0,546,545,1,0,0,0,547,
        550,1,0,0,0,548,546,1,0,0,0,548,549,1,0,0,0,549,551,1,0,0,0,550,
        548,1,0,0,0,551,552,5,118,0,0,552,553,3,10,5,0,553,554,5,119,0,0,
        554,7,1,0,0,0,555,556,4,4,0,0,556,557,3,98,49,0,557,9,1,0,0,0,558,
        560,5,117,0,0,559,558,1,0,0,0,560,563,1,0,0,0,561,559,1,0,0,0,561,
        562,1,0,0,0,562,572,1,0,0,0,563,561,1,0,0,0,564,566,3,12,6,0,565,
        567,5,117,0,0,566,565,1,0,0,0,567,568,1,0,0,0,568,566,1,0,0,0,568,
        569,1,0,0,0,569,571,1,0,0,0,570,564,1,0,0,0,571,574,1,0,0,0,572,
        570,1,0,0,0,572,573,1,0,0,0,573,576,1,0,0,0,574,572,1,0,0,0,575,
        577,3,12,6,0,576,575,1,0,0,0,576,577,1,0,0,0,577,603,1,0,0,0,578,
        580,5,117,0,0,579,578,1,0,0,0,580,583,1,0,0,0,581,579,1,0,0,0,581,
        582,1,0,0,0,582,584,1,0,0,0,583,581,1,0,0,0,584,585,3,14,7,0,585,
        587,5,117,0,0,586,588,3,102,51,0,587,586,1,0,0,0,587,588,1,0,0,0,
        588,589,1,0,0,0,589,596,5,117,0,0,590,595,5,117,0,0,591,592,3,22,
        11,0,592,593,5,117,0,0,593,595,1,0,0,0,594,590,1,0,0,0,594,591,1,
        0,0,0,595,598,1,0,0,0,596,594,1,0,0,0,596,597,1,0,0,0,597,600,1,
        0,0,0,598,596,1,0,0,0,599,601,3,22,11,0,600,599,1,0,0,0,600,601,
        1,0,0,0,601,603,1,0,0,0,602,561,1,0,0,0,602,581,1,0,0,0,603,11,1,
        0,0,0,604,608,5,135,0,0,605,607,5,124,0,0,606,605,1,0,0,0,607,610,
        1,0,0,0,608,606,1,0,0,0,608,609,1,0,0,0,609,611,1,0,0,0,610,608,
        1,0,0,0,611,634,3,20,10,0,612,616,5,138,0,0,613,615,5,124,0,0,614,
        613,1,0,0,0,615,618,1,0,0,0,616,614,1,0,0,0,616,617,1,0,0,0,617,
        619,1,0,0,0,618,616,1,0,0,0,619,634,3,98,49,0,620,634,5,136,0,0,
        621,634,5,137,0,0,622,634,5,134,0,0,623,624,5,139,0,0,624,625,5,
        126,0,0,625,634,3,102,51,0,626,627,5,140,0,0,627,628,5,126,0,0,628,
        634,3,102,51,0,629,634,3,34,17,0,630,634,3,16,8,0,631,634,3,18,9,
        0,632,634,3,22,11,0,633,604,1,0,0,0,633,612,1,0,0,0,633,620,1,0,
        0,0,633,621,1,0,0,0,633,622,1,0,0,0,633,623,1,0,0,0,633,626,1,0,
        0,0,633,629,1,0,0,0,633,630,1,0,0,0,633,631,1,0,0,0,633,632,1,0,
        0,0,634,13,1,0,0,0,635,637,5,144,0,0,636,638,3,98,49,0,637,636,1,
        0,0,0,637,638,1,0,0,0,638,15,1,0,0,0,639,641,5,144,0,0,640,642,5,
        125,0,0,641,640,1,0,0,0,641,642,1,0,0,0,642,643,1,0,0,0,643,644,
        5,144,0,0,644,17,1,0,0,0,645,647,5,131,0,0,646,645,1,0,0,0,646,647,
        1,0,0,0,647,648,1,0,0,0,648,649,3,98,49,0,649,652,5,124,0,0,650,
        653,5,144,0,0,651,653,3,98,49,0,652,650,1,0,0,0,652,651,1,0,0,0,
        653,19,1,0,0,0,654,659,3,98,49,0,655,656,5,133,0,0,656,657,3,98,
        49,0,657,658,5,133,0,0,658,660,1,0,0,0,659,655,1,0,0,0,659,660,1,
        0,0,0,660,21,1,0,0,0,661,682,3,24,12,0,662,664,5,125,0,0,663,662,
        1,0,0,0,663,664,1,0,0,0,664,665,1,0,0,0,665,667,3,30,15,0,666,668,
        5,125,0,0,667,666,1,0,0,0,667,668,1,0,0,0,668,669,1,0,0,0,669,671,
        3,30,15,0,670,672,5,125,0,0,671,670,1,0,0,0,671,672,1,0,0,0,672,
        673,1,0,0,0,673,674,3,30,15,0,674,683,1,0,0,0,675,680,3,32,16,0,
        676,678,3,32,16,0,677,679,3,32,16,0,678,677,1,0,0,0,678,679,1,0,
        0,0,679,681,1,0,0,0,680,676,1,0,0,0,680,681,1,0,0,0,681,683,1,0,
        0,0,682,663,1,0,0,0,682,675,1,0,0,0,682,683,1,0,0,0,683,23,1,0,0,
        0,684,686,5,128,0,0,685,684,1,0,0,0,685,686,1,0,0,0,686,687,1,0,
        0,0,687,689,3,26,13,0,688,690,3,28,14,0,689,688,1,0,0,0,689,690,
        1,0,0,0,690,700,1,0,0,0,691,692,5,142,0,0,692,693,5,122,0,0,693,
        695,3,26,13,0,694,696,3,28,14,0,695,694,1,0,0,0,695,696,1,0,0,0,
        696,697,1,0,0,0,697,698,5,123,0,0,698,700,1,0,0,0,699,685,1,0,0,
        0,699,691,1,0,0,0,700,25,1,0,0,0,701,703,5,144,0,0,702,701,1,0,0,
        0,702,703,1,0,0,0,703,704,1,0,0,0,704,707,3,98,49,0,705,707,5,144,
        0,0,706,702,1,0,0,0,706,705,1,0,0,0,707,27,1,0,0,0,708,709,5,128,
        0,0,709,710,5,144,0,0,710,29,1,0,0,0,711,717,5,144,0,0,712,714,5,
        131,0,0,713,712,1,0,0,0,713,714,1,0,0,0,714,715,1,0,0,0,715,717,
        3,98,49,0,716,711,1,0,0,0,716,713,1,0,0,0,717,31,1,0,0,0,718,720,
        5,125,0,0,719,718,1,0,0,0,719,720,1,0,0,0,720,723,1,0,0,0,721,724,
        5,144,0,0,722,724,3,98,49,0,723,721,1,0,0,0,723,722,1,0,0,0,724,
        726,1,0,0,0,725,727,5,125,0,0,726,725,1,0,0,0,726,727,1,0,0,0,727,
        728,1,0,0,0,728,729,3,30,15,0,729,33,1,0,0,0,730,731,5,141,0,0,731,
        735,3,98,49,0,732,734,5,125,0,0,733,732,1,0,0,0,734,737,1,0,0,0,
        735,733,1,0,0,0,735,736,1,0,0,0,736,738,1,0,0,0,737,735,1,0,0,0,
        738,742,3,36,18,0,739,741,5,125,0,0,740,739,1,0,0,0,741,744,1,0,
        0,0,742,740,1,0,0,0,742,743,1,0,0,0,743,745,1,0,0,0,744,742,1,0,
        0,0,745,746,3,36,18,0,746,757,1,0,0,0,747,748,5,141,0,0,748,749,
        3,98,49,0,749,750,5,117,0,0,750,751,3,36,18,0,751,752,5,117,0,0,
        752,753,3,36,18,0,753,754,5,117,0,0,754,755,3,36,18,0,755,757,1,
        0,0,0,756,730,1,0,0,0,756,747,1,0,0,0,757,35,1,0,0,0,758,762,5,144,
        0,0,759,761,5,125,0,0,760,759,1,0,0,0,761,764,1,0,0,0,762,760,1,
        0,0,0,762,763,1,0,0,0,763,765,1,0,0,0,764,762,1,0,0,0,765,769,5,
        144,0,0,766,768,5,125,0,0,767,766,1,0,0,0,768,771,1,0,0,0,769,767,
        1,0,0,0,769,770,1,0,0,0,770,772,1,0,0,0,771,769,1,0,0,0,772,776,
        5,144,0,0,773,775,5,125,0,0,774,773,1,0,0,0,775,778,1,0,0,0,776,
        774,1,0,0,0,776,777,1,0,0,0,777,37,1,0,0,0,778,776,1,0,0,0,779,783,
        5,12,0,0,780,782,5,117,0,0,781,780,1,0,0,0,782,785,1,0,0,0,783,781,
        1,0,0,0,783,784,1,0,0,0,784,788,1,0,0,0,785,783,1,0,0,0,786,787,
        4,19,1,1,787,789,3,42,21,0,788,786,1,0,0,0,788,789,1,0,0,0,789,790,
        1,0,0,0,790,794,3,48,24,0,791,793,5,124,0,0,792,791,1,0,0,0,793,
        796,1,0,0,0,794,792,1,0,0,0,794,795,1,0,0,0,795,797,1,0,0,0,796,
        794,1,0,0,0,797,798,3,52,26,0,798,39,1,0,0,0,799,803,5,12,0,0,800,
        802,5,117,0,0,801,800,1,0,0,0,802,805,1,0,0,0,803,801,1,0,0,0,803,
        804,1,0,0,0,804,807,1,0,0,0,805,803,1,0,0,0,806,808,3,42,21,0,807,
        806,1,0,0,0,807,808,1,0,0,0,808,812,1,0,0,0,809,811,3,96,48,0,810,
        809,1,0,0,0,811,814,1,0,0,0,812,810,1,0,0,0,812,813,1,0,0,0,813,
        815,1,0,0,0,814,812,1,0,0,0,815,819,5,118,0,0,816,818,5,117,0,0,
        817,816,1,0,0,0,818,821,1,0,0,0,819,817,1,0,0,0,819,820,1,0,0,0,
        820,830,1,0,0,0,821,819,1,0,0,0,822,824,3,50,25,0,823,825,5,117,
        0,0,824,823,1,0,0,0,825,826,1,0,0,0,826,824,1,0,0,0,826,827,1,0,
        0,0,827,829,1,0,0,0,828,822,1,0,0,0,829,832,1,0,0,0,830,828,1,0,
        0,0,830,831,1,0,0,0,831,834,1,0,0,0,832,830,1,0,0,0,833,835,3,50,
        25,0,834,833,1,0,0,0,834,835,1,0,0,0,835,836,1,0,0,0,836,837,5,119,
        0,0,837,41,1,0,0,0,838,851,3,44,22,0,839,841,3,44,22,0,840,839,1,
        0,0,0,840,841,1,0,0,0,841,846,1,0,0,0,842,844,5,125,0,0,843,845,
        3,44,22,0,844,843,1,0,0,0,844,845,1,0,0,0,845,847,1,0,0,0,846,842,
        1,0,0,0,847,848,1,0,0,0,848,846,1,0,0,0,848,849,1,0,0,0,849,851,
        1,0,0,0,850,838,1,0,0,0,850,840,1,0,0,0,851,43,1,0,0,0,852,857,3,
        46,23,0,853,854,4,22,2,1,854,856,3,46,23,0,855,853,1,0,0,0,856,859,
        1,0,0,0,857,855,1,0,0,0,857,858,1,0,0,0,858,45,1,0,0,0,859,857,1,
        0,0,0,860,865,3,98,49,0,861,865,5,144,0,0,862,865,5,131,0,0,863,
        865,5,134,0,0,864,860,1,0,0,0,864,861,1,0,0,0,864,862,1,0,0,0,864,
        863,1,0,0,0,865,47,1,0,0,0,866,869,4,24,3,0,867,870,3,100,50,0,868,
        870,5,144,0,0,869,867,1,0,0,0,869,868,1,0,0,0,870,49,1,0,0,0,871,
        875,3,48,24,0,872,874,5,124,0,0,873,872,1,0,0,0,874,877,1,0,0,0,
        875,873,1,0,0,0,875,876,1,0,0,0,876,878,1,0,0,0,877,875,1,0,0,0,
        878,879,3,54,27,0,879,51,1,0,0,0,880,883,3,56,28,0,881,883,3,60,
        30,0,882,880,1,0,0,0,882,881,1,0,0,0,883,53,1,0,0,0,884,886,3,58,
        29,0,885,884,1,0,0,0,886,887,1,0,0,0,887,885,1,0,0,0,887,888,1,0,
        0,0,888,55,1,0,0,0,889,894,5,120,0,0,890,893,3,58,29,0,891,893,5,
        117,0,0,892,890,1,0,0,0,892,891,1,0,0,0,893,896,1,0,0,0,894,892,
        1,0,0,0,894,895,1,0,0,0,895,897,1,0,0,0,896,894,1,0,0,0,897,898,
        5,121,0,0,898,57,1,0,0,0,899,920,3,56,28,0,900,905,5,122,0,0,901,
        904,3,58,29,0,902,904,5,117,0,0,903,901,1,0,0,0,903,902,1,0,0,0,
        904,907,1,0,0,0,905,903,1,0,0,0,905,906,1,0,0,0,906,908,1,0,0,0,
        907,905,1,0,0,0,908,920,5,123,0,0,909,914,5,118,0,0,910,913,3,58,
        29,0,911,913,5,117,0,0,912,910,1,0,0,0,912,911,1,0,0,0,913,916,1,
        0,0,0,914,912,1,0,0,0,914,915,1,0,0,0,915,917,1,0,0,0,916,914,1,
        0,0,0,917,920,5,119,0,0,918,920,8,0,0,0,919,899,1,0,0,0,919,900,
        1,0,0,0,919,909,1,0,0,0,919,918,1,0,0,0,920,59,1,0,0,0,921,924,3,
        64,32,0,922,924,3,62,31,0,923,921,1,0,0,0,923,922,1,0,0,0,924,929,
        1,0,0,0,925,926,4,30,4,1,926,928,3,62,31,0,927,925,1,0,0,0,928,931,
        1,0,0,0,929,927,1,0,0,0,929,930,1,0,0,0,930,61,1,0,0,0,931,929,1,
        0,0,0,932,943,3,98,49,0,933,943,5,144,0,0,934,943,5,131,0,0,935,
        943,5,130,0,0,936,943,5,125,0,0,937,943,5,129,0,0,938,943,5,126,
        0,0,939,943,5,122,0,0,940,943,5,123,0,0,941,943,5,133,0,0,942,932,
        1,0,0,0,942,933,1,0,0,0,942,934,1,0,0,0,942,935,1,0,0,0,942,936,
        1,0,0,0,942,937,1,0,0,0,942,938,1,0,0,0,942,939,1,0,0,0,942,940,
        1,0,0,0,942,941,1,0,0,0,943,63,1,0,0,0,944,945,5,127,0,0,945,946,
        4,32,5,0,946,947,3,98,49,0,947,65,1,0,0,0,948,949,5,17,0,0,949,67,
        1,0,0,0,950,954,5,13,0,0,951,953,3,96,48,0,952,951,1,0,0,0,953,956,
        1,0,0,0,954,952,1,0,0,0,954,955,1,0,0,0,955,958,1,0,0,0,956,954,
        1,0,0,0,957,959,3,94,47,0,958,957,1,0,0,0,958,959,1,0,0,0,959,963,
        1,0,0,0,960,962,5,117,0,0,961,960,1,0,0,0,962,965,1,0,0,0,963,961,
        1,0,0,0,963,964,1,0,0,0,964,966,1,0,0,0,965,963,1,0,0,0,966,970,
        5,118,0,0,967,969,5,117,0,0,968,967,1,0,0,0,969,972,1,0,0,0,970,
        968,1,0,0,0,970,971,1,0,0,0,971,981,1,0,0,0,972,970,1,0,0,0,973,
        975,3,70,35,0,974,976,5,117,0,0,975,974,1,0,0,0,976,977,1,0,0,0,
        977,975,1,0,0,0,977,978,1,0,0,0,978,980,1,0,0,0,979,973,1,0,0,0,
        980,983,1,0,0,0,981,979,1,0,0,0,981,982,1,0,0,0,982,985,1,0,0,0,
        983,981,1,0,0,0,984,986,3,70,35,0,985,984,1,0,0,0,985,986,1,0,0,
        0,986,987,1,0,0,0,987,988,5,119,0,0,988,69,1,0,0,0,989,993,3,72,
        36,0,990,993,3,76,38,0,991,993,3,78,39,0,992,989,1,0,0,0,992,990,
        1,0,0,0,992,991,1,0,0,0,993,71,1,0,0,0,994,995,5,143,0,0,995,996,
        3,74,37,0,996,73,1,0,0,0,997,1006,3,98,49,0,998,1006,5,144,0,0,999,
        1006,5,131,0,0,1000,1006,5,130,0,0,1001,1006,5,129,0,0,1002,1006,
        5,122,0,0,1003,1006,5,123,0,0,1004,1006,5,126,0,0,1005,997,1,0,0,
        0,1005,998,1,0,0,0,1005,999,1,0,0,0,1005,1000,1,0,0,0,1005,1001,
        1,0,0,0,1005,1002,1,0,0,0,1005,1003,1,0,0,0,1005,1004,1,0,0,0,1006,
        1007,1,0,0,0,1007,1005,1,0,0,0,1007,1008,1,0,0,0,1008,75,1,0,0,0,
        1009,1010,5,120,0,0,1010,1011,3,74,37,0,1011,1012,5,121,0,0,1012,
        77,1,0,0,0,1013,1015,3,104,52,0,1014,1013,1,0,0,0,1015,1016,1,0,
        0,0,1016,1014,1,0,0,0,1016,1017,1,0,0,0,1017,79,1,0,0,0,1018,1022,
        5,14,0,0,1019,1021,3,96,48,0,1020,1019,1,0,0,0,1021,1024,1,0,0,0,
        1022,1020,1,0,0,0,1022,1023,1,0,0,0,1023,1026,1,0,0,0,1024,1022,
        1,0,0,0,1025,1027,3,94,47,0,1026,1025,1,0,0,0,1026,1027,1,0,0,0,
        1027,1031,1,0,0,0,1028,1030,5,117,0,0,1029,1028,1,0,0,0,1030,1033,
        1,0,0,0,1031,1029,1,0,0,0,1031,1032,1,0,0,0,1032,1034,1,0,0,0,1033,
        1031,1,0,0,0,1034,1038,5,118,0,0,1035,1037,5,117,0,0,1036,1035,1,
        0,0,0,1037,1040,1,0,0,0,1038,1036,1,0,0,0,1038,1039,1,0,0,0,1039,
        1049,1,0,0,0,1040,1038,1,0,0,0,1041,1043,3,82,41,0,1042,1044,5,117,
        0,0,1043,1042,1,0,0,0,1044,1045,1,0,0,0,1045,1043,1,0,0,0,1045,1046,
        1,0,0,0,1046,1048,1,0,0,0,1047,1041,1,0,0,0,1048,1051,1,0,0,0,1049,
        1047,1,0,0,0,1049,1050,1,0,0,0,1050,1053,1,0,0,0,1051,1049,1,0,0,
        0,1052,1054,3,82,41,0,1053,1052,1,0,0,0,1053,1054,1,0,0,0,1054,1055,
        1,0,0,0,1055,1056,5,119,0,0,1056,81,1,0,0,0,1057,1061,5,135,0,0,
        1058,1060,5,124,0,0,1059,1058,1,0,0,0,1060,1063,1,0,0,0,1061,1059,
        1,0,0,0,1061,1062,1,0,0,0,1062,1064,1,0,0,0,1063,1061,1,0,0,0,1064,
        1077,3,20,10,0,1065,1077,3,84,42,0,1066,1067,5,144,0,0,1067,1068,
        5,144,0,0,1068,1069,5,144,0,0,1069,1077,5,144,0,0,1070,1071,3,24,
        12,0,1071,1072,5,144,0,0,1072,1073,5,144,0,0,1073,1074,5,144,0,0,
        1074,1077,1,0,0,0,1075,1077,5,134,0,0,1076,1057,1,0,0,0,1076,1065,
        1,0,0,0,1076,1066,1,0,0,0,1076,1070,1,0,0,0,1076,1075,1,0,0,0,1077,
        83,1,0,0,0,1078,1082,3,86,43,0,1079,1081,5,124,0,0,1080,1079,1,0,
        0,0,1081,1084,1,0,0,0,1082,1080,1,0,0,0,1082,1083,1,0,0,0,1083,1086,
        1,0,0,0,1084,1082,1,0,0,0,1085,1087,3,104,52,0,1086,1085,1,0,0,0,
        1087,1088,1,0,0,0,1088,1086,1,0,0,0,1088,1089,1,0,0,0,1089,85,1,
        0,0,0,1090,1091,4,43,6,0,1091,1092,3,98,49,0,1092,87,1,0,0,0,1093,
        1097,5,15,0,0,1094,1096,3,96,48,0,1095,1094,1,0,0,0,1096,1099,1,
        0,0,0,1097,1095,1,0,0,0,1097,1098,1,0,0,0,1098,1101,1,0,0,0,1099,
        1097,1,0,0,0,1100,1102,3,94,47,0,1101,1100,1,0,0,0,1101,1102,1,0,
        0,0,1102,1106,1,0,0,0,1103,1105,5,117,0,0,1104,1103,1,0,0,0,1105,
        1108,1,0,0,0,1106,1104,1,0,0,0,1106,1107,1,0,0,0,1107,1109,1,0,0,
        0,1108,1106,1,0,0,0,1109,1110,5,118,0,0,1110,1111,3,90,45,0,1111,
        1112,5,119,0,0,1112,89,1,0,0,0,1113,1114,5,118,0,0,1114,1115,3,90,
        45,0,1115,1116,5,119,0,0,1116,1119,1,0,0,0,1117,1119,8,1,0,0,1118,
        1113,1,0,0,0,1118,1117,1,0,0,0,1119,1122,1,0,0,0,1120,1118,1,0,0,
        0,1120,1121,1,0,0,0,1121,91,1,0,0,0,1122,1120,1,0,0,0,1123,1127,
        5,16,0,0,1124,1126,3,96,48,0,1125,1124,1,0,0,0,1126,1129,1,0,0,0,
        1127,1125,1,0,0,0,1127,1128,1,0,0,0,1128,1131,1,0,0,0,1129,1127,
        1,0,0,0,1130,1132,3,94,47,0,1131,1130,1,0,0,0,1131,1132,1,0,0,0,
        1132,1136,1,0,0,0,1133,1135,5,117,0,0,1134,1133,1,0,0,0,1135,1138,
        1,0,0,0,1136,1134,1,0,0,0,1136,1137,1,0,0,0,1137,1139,1,0,0,0,1138,
        1136,1,0,0,0,1139,1141,5,118,0,0,1140,1142,5,150,0,0,1141,1140,1,
        0,0,0,1141,1142,1,0,0,0,1142,1143,1,0,0,0,1143,1144,5,119,0,0,1144,
        93,1,0,0,0,1145,1148,3,98,49,0,1146,1148,5,144,0,0,1147,1145,1,0,
        0,0,1147,1146,1,0,0,0,1148,95,1,0,0,0,1149,1150,7,2,0,0,1150,97,
        1,0,0,0,1151,1154,3,100,50,0,1152,1154,5,146,0,0,1153,1151,1,0,0,
        0,1153,1152,1,0,0,0,1154,99,1,0,0,0,1155,1156,7,3,0,0,1156,101,1,
        0,0,0,1157,1159,3,104,52,0,1158,1157,1,0,0,0,1159,1160,1,0,0,0,1160,
        1158,1,0,0,0,1160,1161,1,0,0,0,1161,103,1,0,0,0,1162,1163,8,4,0,
        0,1163,105,1,0,0,0,1164,1166,5,28,0,0,1165,1167,5,4,0,0,1166,1165,
        1,0,0,0,1166,1167,1,0,0,0,1167,1173,1,0,0,0,1168,1170,5,4,0,0,1169,
        1168,1,0,0,0,1169,1170,1,0,0,0,1170,1171,1,0,0,0,1171,1173,4,53,
        7,0,1172,1164,1,0,0,0,1172,1169,1,0,0,0,1173,107,1,0,0,0,1174,1177,
        5,28,0,0,1175,1177,4,54,8,0,1176,1174,1,0,0,0,1176,1175,1,0,0,0,
        1177,109,1,0,0,0,1178,1179,3,240,120,0,1179,1180,3,106,53,0,1180,
        111,1,0,0,0,1181,1182,3,242,121,0,1182,1183,3,106,53,0,1183,113,
        1,0,0,0,1184,1185,3,240,120,0,1185,1186,3,248,124,0,1186,1187,3,
        106,53,0,1187,115,1,0,0,0,1188,1190,3,240,120,0,1189,1191,3,248,
        124,0,1190,1189,1,0,0,0,1190,1191,1,0,0,0,1191,1192,1,0,0,0,1192,
        1193,3,106,53,0,1193,117,1,0,0,0,1194,1196,3,110,55,0,1195,1194,
        1,0,0,0,1196,1197,1,0,0,0,1197,1195,1,0,0,0,1197,1198,1,0,0,0,1198,
        1199,1,0,0,0,1199,1200,5,33,0,0,1200,1201,3,108,54,0,1201,119,1,
        0,0,0,1202,1204,3,110,55,0,1203,1202,1,0,0,0,1204,1207,1,0,0,0,1205,
        1203,1,0,0,0,1205,1206,1,0,0,0,1206,1209,1,0,0,0,1207,1205,1,0,0,
        0,1208,1210,3,114,57,0,1209,1208,1,0,0,0,1210,1211,1,0,0,0,1211,
        1209,1,0,0,0,1211,1212,1,0,0,0,1212,1213,1,0,0,0,1213,1214,5,33,
        0,0,1214,1215,3,108,54,0,1215,121,1,0,0,0,1216,1219,5,28,0,0,1217,
        1219,4,61,9,0,1218,1216,1,0,0,0,1218,1217,1,0,0,0,1219,123,1,0,0,
        0,1220,1221,3,432,216,0,1221,1222,3,122,61,0,1222,125,1,0,0,0,1223,
        1224,3,432,216,0,1224,1225,3,248,124,0,1225,1226,3,122,61,0,1226,
        127,1,0,0,0,1227,1229,3,432,216,0,1228,1230,3,248,124,0,1229,1228,
        1,0,0,0,1229,1230,1,0,0,0,1230,1231,1,0,0,0,1231,1232,3,122,61,0,
        1232,129,1,0,0,0,1233,1235,3,124,62,0,1234,1233,1,0,0,0,1235,1236,
        1,0,0,0,1236,1234,1,0,0,0,1236,1237,1,0,0,0,1237,1238,1,0,0,0,1238,
        1239,5,33,0,0,1239,1240,3,122,61,0,1240,131,1,0,0,0,1241,1243,3,
        124,62,0,1242,1241,1,0,0,0,1243,1246,1,0,0,0,1244,1242,1,0,0,0,1244,
        1245,1,0,0,0,1245,1248,1,0,0,0,1246,1244,1,0,0,0,1247,1249,3,126,
        63,0,1248,1247,1,0,0,0,1249,1250,1,0,0,0,1250,1248,1,0,0,0,1250,
        1251,1,0,0,0,1251,1252,1,0,0,0,1252,1253,5,33,0,0,1253,1254,3,122,
        61,0,1254,133,1,0,0,0,1255,1257,5,19,0,0,1256,1255,1,0,0,0,1256,
        1257,1,0,0,0,1257,1258,1,0,0,0,1258,1259,5,71,0,0,1259,1260,3,214,
        107,0,1260,135,1,0,0,0,1261,1263,5,19,0,0,1262,1261,1,0,0,0,1262,
        1263,1,0,0,0,1263,1264,1,0,0,0,1264,1268,5,90,0,0,1265,1267,7,5,
        0,0,1266,1265,1,0,0,0,1267,1270,1,0,0,0,1268,1266,1,0,0,0,1268,1269,
        1,0,0,0,1269,1271,1,0,0,0,1270,1268,1,0,0,0,1271,1272,3,218,109,
        0,1272,1273,5,71,0,0,1273,1274,3,208,104,0,1274,1287,1,0,0,0,1275,
        1277,5,19,0,0,1276,1275,1,0,0,0,1276,1277,1,0,0,0,1277,1278,1,0,
        0,0,1278,1280,5,90,0,0,1279,1281,7,5,0,0,1280,1279,1,0,0,0,1281,
        1282,1,0,0,0,1282,1280,1,0,0,0,1282,1283,1,0,0,0,1283,1284,1,0,0,
        0,1284,1285,5,71,0,0,1285,1287,3,208,104,0,1286,1262,1,0,0,0,1286,
        1276,1,0,0,0,1287,137,1,0,0,0,1288,1289,7,6,0,0,1289,139,1,0,0,0,
        1290,1291,7,7,0,0,1291,1292,3,398,199,0,1292,141,1,0,0,0,1293,1297,
        5,20,0,0,1294,1298,3,366,183,0,1295,1298,3,356,178,0,1296,1298,3,
        484,242,0,1297,1294,1,0,0,0,1297,1295,1,0,0,0,1297,1296,1,0,0,0,
        1298,1299,1,0,0,0,1299,1300,3,474,237,0,1300,1301,5,23,0,0,1301,
        143,1,0,0,0,1302,1306,5,22,0,0,1303,1307,3,472,236,0,1304,1305,5,
        48,0,0,1305,1307,3,356,178,0,1306,1303,1,0,0,0,1306,1304,1,0,0,0,
        1307,1308,1,0,0,0,1308,1309,3,474,237,0,1309,1310,5,25,0,0,1310,
        145,1,0,0,0,1311,1312,5,21,0,0,1312,1313,3,364,182,0,1313,1314,3,
        474,237,0,1314,1315,5,24,0,0,1315,147,1,0,0,0,1316,1317,5,22,0,0,
        1317,1318,3,364,182,0,1318,1319,3,474,237,0,1319,1320,5,25,0,0,1320,
        149,1,0,0,0,1321,1322,4,75,10,1,1322,1324,5,82,0,0,1323,1325,3,358,
        179,0,1324,1323,1,0,0,0,1324,1325,1,0,0,0,1325,151,1,0,0,0,1326,
        1327,4,76,11,1,1327,1328,5,74,0,0,1328,153,1,0,0,0,1329,1330,4,77,
        12,1,1330,1331,5,84,0,0,1331,155,1,0,0,0,1332,1333,4,78,13,1,1333,
        1340,5,102,0,0,1334,1335,4,78,14,1,1335,1336,5,90,0,0,1336,1341,
        3,356,178,0,1337,1339,3,358,179,0,1338,1337,1,0,0,0,1338,1339,1,
        0,0,0,1339,1341,1,0,0,0,1340,1334,1,0,0,0,1340,1338,1,0,0,0,1341,
        157,1,0,0,0,1342,1343,4,79,15,1,1343,1344,5,69,0,0,1344,1347,3,414,
        207,0,1345,1347,3,414,207,0,1346,1342,1,0,0,0,1346,1345,1,0,0,0,
        1347,159,1,0,0,0,1348,1350,4,80,16,1,1349,1351,5,98,0,0,1350,1349,
        1,0,0,0,1350,1351,1,0,0,0,1351,1352,1,0,0,0,1352,1353,5,85,0,0,1353,
        1354,3,490,245,0,1354,1355,5,76,0,0,1355,1356,3,358,179,0,1356,1358,
        5,27,0,0,1357,1359,5,4,0,0,1358,1357,1,0,0,0,1358,1359,1,0,0,0,1359,
        1360,1,0,0,0,1360,1362,3,220,110,0,1361,1363,3,254,127,0,1362,1361,
        1,0,0,0,1362,1363,1,0,0,0,1363,161,1,0,0,0,1364,1421,4,81,17,1,1365,
        1366,5,97,0,0,1366,1367,5,20,0,0,1367,1372,3,258,129,0,1368,1369,
        5,28,0,0,1369,1371,3,258,129,0,1370,1368,1,0,0,0,1371,1374,1,0,0,
        0,1372,1370,1,0,0,0,1372,1373,1,0,0,0,1373,1376,1,0,0,0,1374,1372,
        1,0,0,0,1375,1377,5,28,0,0,1376,1375,1,0,0,0,1376,1377,1,0,0,0,1377,
        1378,1,0,0,0,1378,1379,5,23,0,0,1379,1381,5,27,0,0,1380,1382,5,4,
        0,0,1381,1380,1,0,0,0,1381,1382,1,0,0,0,1382,1383,1,0,0,0,1383,1384,
        3,220,110,0,1384,1422,1,0,0,0,1385,1386,5,98,0,0,1386,1387,5,97,
        0,0,1387,1388,5,20,0,0,1388,1393,3,258,129,0,1389,1390,5,28,0,0,
        1390,1392,3,258,129,0,1391,1389,1,0,0,0,1392,1395,1,0,0,0,1393,1391,
        1,0,0,0,1393,1394,1,0,0,0,1394,1397,1,0,0,0,1395,1393,1,0,0,0,1396,
        1398,5,28,0,0,1397,1396,1,0,0,0,1397,1398,1,0,0,0,1398,1399,1,0,
        0,0,1399,1400,5,23,0,0,1400,1401,5,27,0,0,1401,1402,3,220,110,0,
        1402,1422,1,0,0,0,1403,1405,5,98,0,0,1404,1403,1,0,0,0,1404,1405,
        1,0,0,0,1405,1406,1,0,0,0,1406,1407,5,97,0,0,1407,1412,3,258,129,
        0,1408,1409,5,28,0,0,1409,1411,3,258,129,0,1410,1408,1,0,0,0,1411,
        1414,1,0,0,0,1412,1410,1,0,0,0,1412,1413,1,0,0,0,1413,1415,1,0,0,
        0,1414,1412,1,0,0,0,1415,1417,5,27,0,0,1416,1418,5,4,0,0,1417,1416,
        1,0,0,0,1417,1418,1,0,0,0,1418,1419,1,0,0,0,1419,1420,3,220,110,
        0,1420,1422,1,0,0,0,1421,1365,1,0,0,0,1421,1385,1,0,0,0,1421,1404,
        1,0,0,0,1422,163,1,0,0,0,1423,1431,3,38,19,0,1424,1431,3,40,20,0,
        1425,1431,3,6,3,0,1426,1431,3,68,34,0,1427,1431,3,80,40,0,1428,1431,
        3,88,44,0,1429,1431,3,92,46,0,1430,1423,1,0,0,0,1430,1424,1,0,0,
        0,1430,1425,1,0,0,0,1430,1426,1,0,0,0,1430,1427,1,0,0,0,1430,1428,
        1,0,0,0,1430,1429,1,0,0,0,1431,165,1,0,0,0,1432,1457,3,164,82,0,
        1433,1457,3,66,33,0,1434,1457,3,518,259,0,1435,1457,5,78,0,0,1436,
        1457,5,68,0,0,1437,1457,5,73,0,0,1438,1457,3,458,229,0,1439,1457,
        5,108,0,0,1440,1444,3,462,231,0,1441,1444,3,420,210,0,1442,1444,
        3,142,71,0,1443,1440,1,0,0,0,1443,1441,1,0,0,0,1443,1442,1,0,0,0,
        1444,1457,1,0,0,0,1445,1448,3,460,230,0,1446,1448,3,146,73,0,1447,
        1445,1,0,0,0,1447,1446,1,0,0,0,1448,1457,1,0,0,0,1449,1454,3,466,
        233,0,1450,1454,3,464,232,0,1451,1454,3,144,72,0,1452,1454,3,148,
        74,0,1453,1449,1,0,0,0,1453,1450,1,0,0,0,1453,1451,1,0,0,0,1453,
        1452,1,0,0,0,1454,1457,1,0,0,0,1455,1457,5,65,0,0,1456,1432,1,0,
        0,0,1456,1433,1,0,0,0,1456,1434,1,0,0,0,1456,1435,1,0,0,0,1456,1436,
        1,0,0,0,1456,1437,1,0,0,0,1456,1438,1,0,0,0,1456,1439,1,0,0,0,1456,
        1443,1,0,0,0,1456,1447,1,0,0,0,1456,1453,1,0,0,0,1456,1455,1,0,0,
        0,1457,167,1,0,0,0,1458,1459,3,178,89,0,1459,169,1,0,0,0,1460,1464,
        3,354,177,0,1461,1463,5,110,0,0,1462,1461,1,0,0,0,1463,1466,1,0,
        0,0,1464,1462,1,0,0,0,1464,1465,1,0,0,0,1465,1467,1,0,0,0,1466,1464,
        1,0,0,0,1467,1468,5,0,0,1,1468,171,1,0,0,0,1469,1471,5,20,0,0,1470,
        1472,3,514,257,0,1471,1470,1,0,0,0,1471,1472,1,0,0,0,1472,1473,1,
        0,0,0,1473,1474,5,23,0,0,1474,1475,5,64,0,0,1475,1479,3,356,178,
        0,1476,1478,5,110,0,0,1477,1476,1,0,0,0,1478,1481,1,0,0,0,1479,1477,
        1,0,0,0,1479,1480,1,0,0,0,1480,1482,1,0,0,0,1481,1479,1,0,0,0,1482,
        1483,5,0,0,1,1483,173,1,0,0,0,1484,1486,3,2,1,0,1485,1484,1,0,0,
        0,1486,1487,1,0,0,0,1487,1485,1,0,0,0,1487,1488,1,0,0,0,1488,175,
        1,0,0,0,1489,1490,3,184,92,0,1490,177,1,0,0,0,1491,1492,3,176,88,
        0,1492,1493,5,110,0,0,1493,1498,1,0,0,0,1494,1498,3,180,90,0,1495,
        1498,5,110,0,0,1496,1498,5,0,0,1,1497,1491,1,0,0,0,1497,1494,1,0,
        0,0,1497,1495,1,0,0,0,1497,1496,1,0,0,0,1498,179,1,0,0,0,1499,1504,
        3,182,91,0,1500,1501,5,29,0,0,1501,1503,3,182,91,0,1502,1500,1,0,
        0,0,1503,1506,1,0,0,0,1504,1502,1,0,0,0,1504,1505,1,0,0,0,1505,1508,
        1,0,0,0,1506,1504,1,0,0,0,1507,1509,5,29,0,0,1508,1507,1,0,0,0,1508,
        1509,1,0,0,0,1509,1510,1,0,0,0,1510,1511,5,110,0,0,1511,181,1,0,
        0,0,1512,1527,3,186,93,0,1513,1527,3,340,170,0,1514,1527,3,358,179,
        0,1515,1527,3,150,75,0,1516,1527,3,206,103,0,1517,1527,3,192,96,
        0,1518,1527,3,194,97,0,1519,1527,3,200,100,0,1520,1527,3,202,101,
        0,1521,1527,3,204,102,0,1522,1527,3,152,76,0,1523,1527,3,154,77,
        0,1524,1527,3,196,98,0,1525,1527,3,198,99,0,1526,1512,1,0,0,0,1526,
        1513,1,0,0,0,1526,1514,1,0,0,0,1526,1515,1,0,0,0,1526,1516,1,0,0,
        0,1526,1517,1,0,0,0,1526,1518,1,0,0,0,1526,1519,1,0,0,0,1526,1520,
        1,0,0,0,1526,1521,1,0,0,0,1526,1522,1,0,0,0,1526,1523,1,0,0,0,1526,
        1524,1,0,0,0,1526,1525,1,0,0,0,1527,183,1,0,0,0,1528,1537,3,228,
        114,0,1529,1537,3,250,125,0,1530,1537,3,224,112,0,1531,1537,3,162,
        81,0,1532,1537,3,160,80,0,1533,1537,3,260,130,0,1534,1537,3,256,
        128,0,1535,1537,3,268,134,0,1536,1528,1,0,0,0,1536,1529,1,0,0,0,
        1536,1530,1,0,0,0,1536,1531,1,0,0,0,1536,1532,1,0,0,0,1536,1533,
        1,0,0,0,1536,1534,1,0,0,0,1536,1535,1,0,0,0,1537,185,1,0,0,0,1538,
        1539,3,518,259,0,1539,1540,5,27,0,0,1540,1543,3,356,178,0,1541,1542,
        5,38,0,0,1542,1544,3,188,94,0,1543,1541,1,0,0,0,1543,1544,1,0,0,
        0,1544,1574,1,0,0,0,1545,1546,5,20,0,0,1546,1547,3,502,251,0,1547,
        1548,5,23,0,0,1548,1551,1,0,0,0,1549,1551,3,504,252,0,1550,1545,
        1,0,0,0,1550,1549,1,0,0,0,1551,1552,1,0,0,0,1552,1553,5,27,0,0,1553,
        1556,3,356,178,0,1554,1555,5,38,0,0,1555,1557,3,188,94,0,1556,1554,
        1,0,0,0,1556,1557,1,0,0,0,1557,1574,1,0,0,0,1558,1559,3,490,245,
        0,1559,1560,5,38,0,0,1560,1562,1,0,0,0,1561,1558,1,0,0,0,1562,1563,
        1,0,0,0,1563,1561,1,0,0,0,1563,1564,1,0,0,0,1564,1565,1,0,0,0,1565,
        1567,3,188,94,0,1566,1568,5,4,0,0,1567,1566,1,0,0,0,1567,1568,1,
        0,0,0,1568,1574,1,0,0,0,1569,1570,3,502,251,0,1570,1571,3,190,95,
        0,1571,1572,3,188,94,0,1572,1574,1,0,0,0,1573,1538,1,0,0,0,1573,
        1550,1,0,0,0,1573,1561,1,0,0,0,1573,1569,1,0,0,0,1574,187,1,0,0,
        0,1575,1578,3,156,78,0,1576,1578,3,358,179,0,1577,1575,1,0,0,0,1577,
        1576,1,0,0,0,1578,189,1,0,0,0,1579,1580,7,8,0,0,1580,191,1,0,0,0,
        1581,1587,5,77,0,0,1582,1585,3,356,178,0,1583,1584,5,90,0,0,1584,
        1586,3,356,178,0,1585,1583,1,0,0,0,1585,1586,1,0,0,0,1586,1588,1,
        0,0,0,1587,1582,1,0,0,0,1587,1588,1,0,0,0,1588,193,1,0,0,0,1589,
        1590,5,72,0,0,1590,195,1,0,0,0,1591,1592,5,95,0,0,1592,1597,3,518,
        259,0,1593,1594,5,28,0,0,1594,1596,3,518,259,0,1595,1593,1,0,0,0,
        1596,1599,1,0,0,0,1597,1595,1,0,0,0,1597,1598,1,0,0,0,1598,197,1,
        0,0,0,1599,1597,1,0,0,0,1600,1601,5,91,0,0,1601,1606,3,518,259,0,
        1602,1603,5,28,0,0,1603,1605,3,518,259,0,1604,1602,1,0,0,0,1605,
        1608,1,0,0,0,1606,1604,1,0,0,0,1606,1607,1,0,0,0,1607,199,1,0,0,
        0,1608,1606,1,0,0,0,1609,1610,5,94,0,0,1610,1611,3,508,254,0,1611,
        201,1,0,0,0,1612,1613,3,156,78,0,1613,203,1,0,0,0,1614,1615,5,93,
        0,0,1615,1618,3,356,178,0,1616,1617,5,28,0,0,1617,1619,3,356,178,
        0,1618,1616,1,0,0,0,1618,1619,1,0,0,0,1619,205,1,0,0,0,1620,1623,
        3,134,67,0,1621,1623,3,136,68,0,1622,1620,1,0,0,0,1622,1621,1,0,
        0,0,1623,207,1,0,0,0,1624,1625,5,20,0,0,1625,1627,3,210,105,0,1626,
        1628,5,28,0,0,1627,1626,1,0,0,0,1627,1628,1,0,0,0,1628,1629,1,0,
        0,0,1629,1630,5,23,0,0,1630,1634,1,0,0,0,1631,1634,3,210,105,0,1632,
        1634,5,32,0,0,1633,1624,1,0,0,0,1633,1631,1,0,0,0,1633,1632,1,0,
        0,0,1634,209,1,0,0,0,1635,1640,3,212,106,0,1636,1637,5,28,0,0,1637,
        1639,3,212,106,0,1638,1636,1,0,0,0,1639,1642,1,0,0,0,1640,1638,1,
        0,0,0,1640,1641,1,0,0,0,1641,211,1,0,0,0,1642,1640,1,0,0,0,1643,
        1646,3,518,259,0,1644,1645,5,88,0,0,1645,1647,3,518,259,0,1646,1644,
        1,0,0,0,1646,1647,1,0,0,0,1647,213,1,0,0,0,1648,1653,3,216,108,0,
        1649,1650,5,28,0,0,1650,1652,3,216,108,0,1651,1649,1,0,0,0,1652,
        1655,1,0,0,0,1653,1651,1,0,0,0,1653,1654,1,0,0,0,1654,215,1,0,0,
        0,1655,1653,1,0,0,0,1656,1659,3,218,109,0,1657,1658,5,88,0,0,1658,
        1660,3,518,259,0,1659,1657,1,0,0,0,1659,1660,1,0,0,0,1660,217,1,
        0,0,0,1661,1662,6,109,-1,0,1662,1663,3,518,259,0,1663,1669,1,0,0,
        0,1664,1665,10,2,0,0,1665,1666,5,26,0,0,1666,1668,3,518,259,0,1667,
        1664,1,0,0,0,1668,1671,1,0,0,0,1669,1667,1,0,0,0,1669,1670,1,0,0,
        0,1670,219,1,0,0,0,1671,1669,1,0,0,0,1672,1673,5,110,0,0,1673,1674,
        5,2,0,0,1674,1675,3,174,87,0,1675,1676,5,3,0,0,1676,1679,1,0,0,0,
        1677,1679,3,180,90,0,1678,1672,1,0,0,0,1678,1677,1,0,0,0,1679,221,
        1,0,0,0,1680,1681,5,62,0,0,1681,1682,3,368,184,0,1682,1683,5,110,
        0,0,1683,1685,1,0,0,0,1684,1680,1,0,0,0,1685,1686,1,0,0,0,1686,1684,
        1,0,0,0,1686,1687,1,0,0,0,1687,223,1,0,0,0,1688,1689,3,222,111,0,
        1689,1690,3,226,113,0,1690,1693,1,0,0,0,1691,1693,3,226,113,0,1692,
        1688,1,0,0,0,1692,1691,1,0,0,0,1693,225,1,0,0,0,1694,1695,5,79,0,
        0,1695,1697,3,518,259,0,1696,1698,3,342,171,0,1697,1696,1,0,0,0,
        1697,1698,1,0,0,0,1698,1704,1,0,0,0,1699,1701,5,20,0,0,1700,1702,
        3,478,239,0,1701,1700,1,0,0,0,1701,1702,1,0,0,0,1702,1703,1,0,0,
        0,1703,1705,5,23,0,0,1704,1699,1,0,0,0,1704,1705,1,0,0,0,1705,1706,
        1,0,0,0,1706,1707,5,27,0,0,1707,1708,3,220,110,0,1708,227,1,0,0,
        0,1709,1710,3,222,111,0,1710,1711,3,230,115,0,1711,1714,1,0,0,0,
        1712,1714,3,230,115,0,1713,1709,1,0,0,0,1713,1712,1,0,0,0,1714,229,
        1,0,0,0,1715,1716,5,89,0,0,1716,1718,3,518,259,0,1717,1719,3,342,
        171,0,1718,1717,1,0,0,0,1718,1719,1,0,0,0,1719,1720,1,0,0,0,1720,
        1722,5,20,0,0,1721,1723,3,232,116,0,1722,1721,1,0,0,0,1722,1723,
        1,0,0,0,1723,1724,1,0,0,0,1724,1727,5,23,0,0,1725,1726,5,64,0,0,
        1726,1728,3,356,178,0,1727,1725,1,0,0,0,1727,1728,1,0,0,0,1728,1729,
        1,0,0,0,1729,1731,5,27,0,0,1730,1732,3,516,258,0,1731,1730,1,0,0,
        0,1731,1732,1,0,0,0,1732,1733,1,0,0,0,1733,1734,3,220,110,0,1734,
        1757,1,0,0,0,1735,1736,5,98,0,0,1736,1737,5,89,0,0,1737,1739,3,518,
        259,0,1738,1740,3,342,171,0,1739,1738,1,0,0,0,1739,1740,1,0,0,0,
        1740,1741,1,0,0,0,1741,1743,5,20,0,0,1742,1744,3,232,116,0,1743,
        1742,1,0,0,0,1743,1744,1,0,0,0,1744,1745,1,0,0,0,1745,1748,5,23,
        0,0,1746,1747,5,64,0,0,1747,1749,3,356,178,0,1748,1746,1,0,0,0,1748,
        1749,1,0,0,0,1749,1750,1,0,0,0,1750,1752,5,27,0,0,1751,1753,3,516,
        258,0,1752,1751,1,0,0,0,1752,1753,1,0,0,0,1753,1754,1,0,0,0,1754,
        1755,3,220,110,0,1755,1757,1,0,0,0,1756,1715,1,0,0,0,1756,1735,1,
        0,0,0,1757,231,1,0,0,0,1758,1759,3,234,117,0,1759,233,1,0,0,0,1760,
        1764,3,118,59,0,1761,1763,3,110,55,0,1762,1761,1,0,0,0,1763,1766,
        1,0,0,0,1764,1762,1,0,0,0,1764,1765,1,0,0,0,1765,1770,1,0,0,0,1766,
        1764,1,0,0,0,1767,1769,3,114,57,0,1768,1767,1,0,0,0,1769,1772,1,
        0,0,0,1770,1768,1,0,0,0,1770,1771,1,0,0,0,1771,1774,1,0,0,0,1772,
        1770,1,0,0,0,1773,1775,3,236,118,0,1774,1773,1,0,0,0,1774,1775,1,
        0,0,0,1775,1810,1,0,0,0,1776,1780,3,120,60,0,1777,1779,3,114,57,
        0,1778,1777,1,0,0,0,1779,1782,1,0,0,0,1780,1778,1,0,0,0,1780,1781,
        1,0,0,0,1781,1784,1,0,0,0,1782,1780,1,0,0,0,1783,1785,3,236,118,
        0,1784,1783,1,0,0,0,1784,1785,1,0,0,0,1785,1810,1,0,0,0,1786,1788,
        3,110,55,0,1787,1786,1,0,0,0,1788,1789,1,0,0,0,1789,1787,1,0,0,0,
        1789,1790,1,0,0,0,1790,1794,1,0,0,0,1791,1793,3,114,57,0,1792,1791,
        1,0,0,0,1793,1796,1,0,0,0,1794,1792,1,0,0,0,1794,1795,1,0,0,0,1795,
        1798,1,0,0,0,1796,1794,1,0,0,0,1797,1799,3,236,118,0,1798,1797,1,
        0,0,0,1798,1799,1,0,0,0,1799,1810,1,0,0,0,1800,1802,3,114,57,0,1801,
        1800,1,0,0,0,1802,1803,1,0,0,0,1803,1801,1,0,0,0,1803,1804,1,0,0,
        0,1804,1806,1,0,0,0,1805,1807,3,236,118,0,1806,1805,1,0,0,0,1806,
        1807,1,0,0,0,1807,1810,1,0,0,0,1808,1810,3,236,118,0,1809,1760,1,
        0,0,0,1809,1776,1,0,0,0,1809,1787,1,0,0,0,1809,1801,1,0,0,0,1809,
        1808,1,0,0,0,1810,235,1,0,0,0,1811,1812,5,32,0,0,1812,1816,3,110,
        55,0,1813,1815,3,116,58,0,1814,1813,1,0,0,0,1815,1818,1,0,0,0,1816,
        1814,1,0,0,0,1816,1817,1,0,0,0,1817,1820,1,0,0,0,1818,1816,1,0,0,
        0,1819,1821,3,238,119,0,1820,1819,1,0,0,0,1820,1821,1,0,0,0,1821,
        1845,1,0,0,0,1822,1823,5,32,0,0,1823,1827,3,112,56,0,1824,1826,3,
        116,58,0,1825,1824,1,0,0,0,1826,1829,1,0,0,0,1827,1825,1,0,0,0,1827,
        1828,1,0,0,0,1828,1831,1,0,0,0,1829,1827,1,0,0,0,1830,1832,3,238,
        119,0,1831,1830,1,0,0,0,1831,1832,1,0,0,0,1832,1845,1,0,0,0,1833,
        1834,5,32,0,0,1834,1836,5,28,0,0,1835,1837,3,116,58,0,1836,1835,
        1,0,0,0,1837,1838,1,0,0,0,1838,1836,1,0,0,0,1838,1839,1,0,0,0,1839,
        1841,1,0,0,0,1840,1842,3,238,119,0,1841,1840,1,0,0,0,1841,1842,1,
        0,0,0,1842,1845,1,0,0,0,1843,1845,3,238,119,0,1844,1811,1,0,0,0,
        1844,1822,1,0,0,0,1844,1833,1,0,0,0,1844,1843,1,0,0,0,1845,237,1,
        0,0,0,1846,1847,5,48,0,0,1847,1848,3,110,55,0,1848,239,1,0,0,0,1849,
        1851,3,518,259,0,1850,1852,3,244,122,0,1851,1850,1,0,0,0,1851,1852,
        1,0,0,0,1852,241,1,0,0,0,1853,1854,3,518,259,0,1854,1855,3,246,123,
        0,1855,243,1,0,0,0,1856,1857,5,27,0,0,1857,1858,3,356,178,0,1858,
        245,1,0,0,0,1859,1860,5,27,0,0,1860,1861,3,360,180,0,1861,247,1,
        0,0,0,1862,1863,5,38,0,0,1863,1864,3,356,178,0,1864,249,1,0,0,0,
        1865,1866,5,100,0,0,1866,1867,3,368,184,0,1867,1868,5,27,0,0,1868,
        1873,3,220,110,0,1869,1874,3,252,126,0,1870,1872,3,254,127,0,1871,
        1870,1,0,0,0,1871,1872,1,0,0,0,1872,1874,1,0,0,0,1873,1869,1,0,0,
        0,1873,1871,1,0,0,0,1874,251,1,0,0,0,1875,1876,5,99,0,0,1876,1877,
        3,368,184,0,1877,1878,5,27,0,0,1878,1883,3,220,110,0,1879,1884,3,
        252,126,0,1880,1882,3,254,127,0,1881,1880,1,0,0,0,1881,1882,1,0,
        0,0,1882,1884,1,0,0,0,1883,1879,1,0,0,0,1883,1881,1,0,0,0,1884,253,
        1,0,0,0,1885,1886,5,70,0,0,1886,1887,5,27,0,0,1887,1888,3,220,110,
        0,1888,255,1,0,0,0,1889,1890,5,92,0,0,1890,1891,3,368,184,0,1891,
        1892,5,27,0,0,1892,1894,3,220,110,0,1893,1895,3,254,127,0,1894,1893,
        1,0,0,0,1894,1895,1,0,0,0,1895,257,1,0,0,0,1896,1899,3,356,178,0,
        1897,1898,5,88,0,0,1898,1900,3,496,248,0,1899,1897,1,0,0,0,1899,
        1900,1,0,0,0,1900,259,1,0,0,0,1901,1902,5,87,0,0,1902,1903,5,27,
        0,0,1903,1904,3,220,110,0,1904,1905,3,266,133,0,1905,1935,1,0,0,
        0,1906,1907,5,87,0,0,1907,1908,5,27,0,0,1908,1910,3,220,110,0,1909,
        1911,3,262,131,0,1910,1909,1,0,0,0,1911,1912,1,0,0,0,1912,1910,1,
        0,0,0,1912,1913,1,0,0,0,1913,1915,1,0,0,0,1914,1916,3,254,127,0,
        1915,1914,1,0,0,0,1915,1916,1,0,0,0,1916,1918,1,0,0,0,1917,1919,
        3,266,133,0,1918,1917,1,0,0,0,1918,1919,1,0,0,0,1919,1935,1,0,0,
        0,1920,1921,5,87,0,0,1921,1922,5,27,0,0,1922,1924,3,220,110,0,1923,
        1925,3,264,132,0,1924,1923,1,0,0,0,1925,1926,1,0,0,0,1926,1924,1,
        0,0,0,1926,1927,1,0,0,0,1927,1929,1,0,0,0,1928,1930,3,254,127,0,
        1929,1928,1,0,0,0,1929,1930,1,0,0,0,1930,1932,1,0,0,0,1931,1933,
        3,266,133,0,1932,1931,1,0,0,0,1932,1933,1,0,0,0,1933,1935,1,0,0,
        0,1934,1901,1,0,0,0,1934,1906,1,0,0,0,1934,1920,1,0,0,0,1935,261,
        1,0,0,0,1936,1943,5,75,0,0,1937,1940,3,356,178,0,1938,1939,5,88,
        0,0,1939,1941,3,518,259,0,1940,1938,1,0,0,0,1940,1941,1,0,0,0,1941,
        1944,1,0,0,0,1942,1944,3,354,177,0,1943,1937,1,0,0,0,1943,1942,1,
        0,0,0,1943,1944,1,0,0,0,1944,1945,1,0,0,0,1945,1946,5,27,0,0,1946,
        1947,3,220,110,0,1947,263,1,0,0,0,1948,1949,5,75,0,0,1949,1956,5,
        32,0,0,1950,1953,3,356,178,0,1951,1952,5,88,0,0,1952,1954,3,518,
        259,0,1953,1951,1,0,0,0,1953,1954,1,0,0,0,1954,1957,1,0,0,0,1955,
        1957,3,354,177,0,1956,1950,1,0,0,0,1956,1955,1,0,0,0,1957,1958,1,
        0,0,0,1958,1959,5,27,0,0,1959,1960,3,220,110,0,1960,265,1,0,0,0,
        1961,1962,5,80,0,0,1962,1963,5,27,0,0,1963,1964,3,220,110,0,1964,
        267,1,0,0,0,1965,1966,5,104,0,0,1966,1967,3,270,135,0,1967,1968,
        5,27,0,0,1968,1969,5,110,0,0,1969,1971,5,2,0,0,1970,1972,3,272,136,
        0,1971,1970,1,0,0,0,1972,1973,1,0,0,0,1973,1971,1,0,0,0,1973,1974,
        1,0,0,0,1974,1975,1,0,0,0,1975,1976,5,3,0,0,1976,269,1,0,0,0,1977,
        1978,3,364,182,0,1978,1980,5,28,0,0,1979,1981,3,362,181,0,1980,1979,
        1,0,0,0,1980,1981,1,0,0,0,1981,1984,1,0,0,0,1982,1984,3,368,184,
        0,1983,1977,1,0,0,0,1983,1982,1,0,0,0,1984,271,1,0,0,0,1985,1986,
        5,105,0,0,1986,1988,3,276,138,0,1987,1989,3,274,137,0,1988,1987,
        1,0,0,0,1988,1989,1,0,0,0,1989,1990,1,0,0,0,1990,1991,5,27,0,0,1991,
        1992,3,220,110,0,1992,273,1,0,0,0,1993,1994,5,100,0,0,1994,1995,
        3,368,184,0,1995,275,1,0,0,0,1996,1999,3,316,158,0,1997,1999,3,278,
        139,0,1998,1996,1,0,0,0,1998,1997,1,0,0,0,1999,277,1,0,0,0,2000,
        2003,3,280,140,0,2001,2003,3,282,141,0,2002,2000,1,0,0,0,2002,2001,
        1,0,0,0,2003,279,1,0,0,0,2004,2005,3,282,141,0,2005,2006,5,88,0,
        0,2006,2007,3,302,151,0,2007,281,1,0,0,0,2008,2013,3,284,142,0,2009,
        2010,5,34,0,0,2010,2012,3,284,142,0,2011,2009,1,0,0,0,2012,2015,
        1,0,0,0,2013,2011,1,0,0,0,2013,2014,1,0,0,0,2014,283,1,0,0,0,2015,
        2013,1,0,0,0,2016,2025,3,286,143,0,2017,2025,3,300,150,0,2018,2025,
        3,304,152,0,2019,2025,3,306,153,0,2020,2025,3,312,156,0,2021,2025,
        3,314,157,0,2022,2025,3,324,162,0,2023,2025,3,332,166,0,2024,2016,
        1,0,0,0,2024,2017,1,0,0,0,2024,2018,1,0,0,0,2024,2019,1,0,0,0,2024,
        2020,1,0,0,0,2024,2021,1,0,0,0,2024,2022,1,0,0,0,2024,2023,1,0,0,
        0,2025,285,1,0,0,0,2026,2033,3,292,146,0,2027,2033,3,290,145,0,2028,
        2033,3,458,229,0,2029,2033,5,73,0,0,2030,2033,5,78,0,0,2031,2033,
        5,68,0,0,2032,2026,1,0,0,0,2032,2027,1,0,0,0,2032,2028,1,0,0,0,2032,
        2029,1,0,0,0,2032,2030,1,0,0,0,2032,2031,1,0,0,0,2033,287,1,0,0,
        0,2034,2041,3,292,146,0,2035,2041,3,290,145,0,2036,2041,3,458,229,
        0,2037,2041,5,73,0,0,2038,2041,5,78,0,0,2039,2041,5,68,0,0,2040,
        2034,1,0,0,0,2040,2035,1,0,0,0,2040,2036,1,0,0,0,2040,2037,1,0,0,
        0,2040,2038,1,0,0,0,2040,2039,1,0,0,0,2041,289,1,0,0,0,2042,2043,
        3,294,147,0,2043,2044,7,9,0,0,2044,2045,3,298,149,0,2045,291,1,0,
        0,0,2046,2048,5,31,0,0,2047,2046,1,0,0,0,2047,2048,1,0,0,0,2048,
        2049,1,0,0,0,2049,2050,5,108,0,0,2050,293,1,0,0,0,2051,2053,5,31,
        0,0,2052,2051,1,0,0,0,2052,2053,1,0,0,0,2053,2054,1,0,0,0,2054,2055,
        3,296,148,0,2055,295,1,0,0,0,2056,2057,5,108,0,0,2057,297,1,0,0,
        0,2058,2059,5,108,0,0,2059,299,1,0,0,0,2060,2061,3,302,151,0,2061,
        301,1,0,0,0,2062,2063,3,138,69,0,2063,303,1,0,0,0,2064,2065,5,106,
        0,0,2065,305,1,0,0,0,2066,2067,3,308,154,0,2067,307,1,0,0,0,2068,
        2071,3,518,259,0,2069,2070,5,26,0,0,2070,2072,3,518,259,0,2071,2069,
        1,0,0,0,2072,2073,1,0,0,0,2073,2071,1,0,0,0,2073,2074,1,0,0,0,2074,
        309,1,0,0,0,2075,2080,3,518,259,0,2076,2077,5,26,0,0,2077,2079,3,
        518,259,0,2078,2076,1,0,0,0,2079,2082,1,0,0,0,2080,2078,1,0,0,0,
        2080,2081,1,0,0,0,2081,311,1,0,0,0,2082,2080,1,0,0,0,2083,2084,5,
        20,0,0,2084,2085,3,278,139,0,2085,2086,5,23,0,0,2086,313,1,0,0,0,
        2087,2089,5,21,0,0,2088,2090,3,318,159,0,2089,2088,1,0,0,0,2089,
        2090,1,0,0,0,2090,2091,1,0,0,0,2091,2098,5,24,0,0,2092,2094,5,20,
        0,0,2093,2095,3,316,158,0,2094,2093,1,0,0,0,2094,2095,1,0,0,0,2095,
        2096,1,0,0,0,2096,2098,5,23,0,0,2097,2087,1,0,0,0,2097,2092,1,0,
        0,0,2098,315,1,0,0,0,2099,2100,3,320,160,0,2100,2102,5,28,0,0,2101,
        2103,3,318,159,0,2102,2101,1,0,0,0,2102,2103,1,0,0,0,2103,317,1,
        0,0,0,2104,2109,3,320,160,0,2105,2106,5,28,0,0,2106,2108,3,320,160,
        0,2107,2105,1,0,0,0,2108,2111,1,0,0,0,2109,2107,1,0,0,0,2109,2110,
        1,0,0,0,2110,2113,1,0,0,0,2111,2109,1,0,0,0,2112,2114,5,28,0,0,2113,
        2112,1,0,0,0,2113,2114,1,0,0,0,2114,319,1,0,0,0,2115,2118,3,322,
        161,0,2116,2118,3,278,139,0,2117,2115,1,0,0,0,2117,2116,1,0,0,0,
        2118,321,1,0,0,0,2119,2120,5,32,0,0,2120,2121,3,518,259,0,2121,323,
        1,0,0,0,2122,2123,5,22,0,0,2123,2143,5,25,0,0,2124,2125,5,22,0,0,
        2125,2127,3,330,165,0,2126,2128,5,28,0,0,2127,2126,1,0,0,0,2127,
        2128,1,0,0,0,2128,2129,1,0,0,0,2129,2130,5,25,0,0,2130,2143,1,0,
        0,0,2131,2132,5,22,0,0,2132,2135,3,326,163,0,2133,2134,5,28,0,0,
        2134,2136,3,330,165,0,2135,2133,1,0,0,0,2135,2136,1,0,0,0,2136,2138,
        1,0,0,0,2137,2139,5,28,0,0,2138,2137,1,0,0,0,2138,2139,1,0,0,0,2139,
        2140,1,0,0,0,2140,2141,5,25,0,0,2141,2143,1,0,0,0,2142,2122,1,0,
        0,0,2142,2124,1,0,0,0,2142,2131,1,0,0,0,2143,325,1,0,0,0,2144,2149,
        3,328,164,0,2145,2146,5,28,0,0,2146,2148,3,328,164,0,2147,2145,1,
        0,0,0,2148,2151,1,0,0,0,2149,2147,1,0,0,0,2149,2150,1,0,0,0,2150,
        327,1,0,0,0,2151,2149,1,0,0,0,2152,2155,3,288,144,0,2153,2155,3,
        308,154,0,2154,2152,1,0,0,0,2154,2153,1,0,0,0,2155,2156,1,0,0,0,
        2156,2157,5,27,0,0,2157,2158,3,278,139,0,2158,329,1,0,0,0,2159,2160,
        5,48,0,0,2160,2161,3,302,151,0,2161,331,1,0,0,0,2162,2163,3,310,
        155,0,2163,2175,5,20,0,0,2164,2167,3,334,167,0,2165,2166,5,28,0,
        0,2166,2168,3,336,168,0,2167,2165,1,0,0,0,2167,2168,1,0,0,0,2168,
        2171,1,0,0,0,2169,2171,3,336,168,0,2170,2164,1,0,0,0,2170,2169,1,
        0,0,0,2171,2173,1,0,0,0,2172,2174,5,28,0,0,2173,2172,1,0,0,0,2173,
        2174,1,0,0,0,2174,2176,1,0,0,0,2175,2170,1,0,0,0,2175,2176,1,0,0,
        0,2176,2177,1,0,0,0,2177,2178,5,23,0,0,2178,333,1,0,0,0,2179,2184,
        3,278,139,0,2180,2181,5,28,0,0,2181,2183,3,278,139,0,2182,2180,1,
        0,0,0,2183,2186,1,0,0,0,2184,2182,1,0,0,0,2184,2185,1,0,0,0,2185,
        335,1,0,0,0,2186,2184,1,0,0,0,2187,2192,3,338,169,0,2188,2189,5,
        28,0,0,2189,2191,3,338,169,0,2190,2188,1,0,0,0,2191,2194,1,0,0,0,
        2192,2190,1,0,0,0,2192,2193,1,0,0,0,2193,337,1,0,0,0,2194,2192,1,
        0,0,0,2195,2196,3,518,259,0,2196,2197,5,38,0,0,2197,2198,3,278,139,
        0,2198,339,1,0,0,0,2199,2200,5,103,0,0,2200,2202,3,518,259,0,2201,
        2203,3,342,171,0,2202,2201,1,0,0,0,2202,2203,1,0,0,0,2203,2204,1,
        0,0,0,2204,2205,5,38,0,0,2205,2206,3,356,178,0,2206,341,1,0,0,0,
        2207,2208,5,21,0,0,2208,2209,3,344,172,0,2209,2210,5,24,0,0,2210,
        343,1,0,0,0,2211,2216,3,346,173,0,2212,2213,5,28,0,0,2213,2215,3,
        346,173,0,2214,2212,1,0,0,0,2215,2218,1,0,0,0,2216,2214,1,0,0,0,
        2216,2217,1,0,0,0,2217,2220,1,0,0,0,2218,2216,1,0,0,0,2219,2221,
        5,28,0,0,2220,2219,1,0,0,0,2220,2221,1,0,0,0,2221,345,1,0,0,0,2222,
        2224,3,518,259,0,2223,2225,3,348,174,0,2224,2223,1,0,0,0,2224,2225,
        1,0,0,0,2225,2227,1,0,0,0,2226,2228,3,350,175,0,2227,2226,1,0,0,
        0,2227,2228,1,0,0,0,2228,2240,1,0,0,0,2229,2230,5,32,0,0,2230,2232,
        3,518,259,0,2231,2233,3,352,176,0,2232,2231,1,0,0,0,2232,2233,1,
        0,0,0,2233,2240,1,0,0,0,2234,2235,5,48,0,0,2235,2237,3,518,259,0,
        2236,2238,3,350,175,0,2237,2236,1,0,0,0,2237,2238,1,0,0,0,2238,2240,
        1,0,0,0,2239,2222,1,0,0,0,2239,2229,1,0,0,0,2239,2234,1,0,0,0,2240,
        347,1,0,0,0,2241,2242,5,27,0,0,2242,2243,3,356,178,0,2243,349,1,
        0,0,0,2244,2245,5,38,0,0,2245,2246,3,356,178,0,2246,351,1,0,0,0,
        2247,2248,5,38,0,0,2248,2249,3,360,180,0,2249,353,1,0,0,0,2250,2255,
        3,356,178,0,2251,2252,5,28,0,0,2252,2254,3,356,178,0,2253,2251,1,
        0,0,0,2254,2257,1,0,0,0,2255,2253,1,0,0,0,2255,2256,1,0,0,0,2256,
        2259,1,0,0,0,2257,2255,1,0,0,0,2258,2260,5,28,0,0,2259,2258,1,0,
        0,0,2259,2260,1,0,0,0,2260,355,1,0,0,0,2261,2267,3,370,185,0,2262,
        2263,5,100,0,0,2263,2264,3,370,185,0,2264,2265,5,70,0,0,2265,2266,
        3,356,178,0,2266,2268,1,0,0,0,2267,2262,1,0,0,0,2267,2268,1,0,0,
        0,2268,2271,1,0,0,0,2269,2271,3,422,211,0,2270,2261,1,0,0,0,2270,
        2269,1,0,0,0,2271,357,1,0,0,0,2272,2277,3,360,180,0,2273,2274,5,
        28,0,0,2274,2276,3,360,180,0,2275,2273,1,0,0,0,2276,2279,1,0,0,0,
        2277,2275,1,0,0,0,2277,2278,1,0,0,0,2278,2281,1,0,0,0,2279,2277,
        1,0,0,0,2280,2282,5,28,0,0,2281,2280,1,0,0,0,2281,2282,1,0,0,0,2282,
        359,1,0,0,0,2283,2284,5,32,0,0,2284,2287,3,398,199,0,2285,2287,3,
        356,178,0,2286,2283,1,0,0,0,2286,2285,1,0,0,0,2287,361,1,0,0,0,2288,
        2293,3,364,182,0,2289,2290,5,28,0,0,2290,2292,3,364,182,0,2291,2289,
        1,0,0,0,2292,2295,1,0,0,0,2293,2291,1,0,0,0,2293,2294,1,0,0,0,2294,
        2297,1,0,0,0,2295,2293,1,0,0,0,2296,2298,5,28,0,0,2297,2296,1,0,
        0,0,2297,2298,1,0,0,0,2298,363,1,0,0,0,2299,2300,5,32,0,0,2300,2303,
        3,398,199,0,2301,2303,3,368,184,0,2302,2299,1,0,0,0,2302,2301,1,
        0,0,0,2303,365,1,0,0,0,2304,2305,3,518,259,0,2305,2306,5,66,0,0,
        2306,2307,3,356,178,0,2307,367,1,0,0,0,2308,2311,3,366,183,0,2309,
        2311,3,356,178,0,2310,2308,1,0,0,0,2310,2309,1,0,0,0,2311,369,1,
        0,0,0,2312,2317,3,372,186,0,2313,2314,5,101,0,0,2314,2316,3,372,
        186,0,2315,2313,1,0,0,0,2316,2319,1,0,0,0,2317,2315,1,0,0,0,2317,
        2318,1,0,0,0,2318,371,1,0,0,0,2319,2317,1,0,0,0,2320,2325,3,374,
        187,0,2321,2322,5,83,0,0,2322,2324,3,374,187,0,2323,2321,1,0,0,0,
        2324,2327,1,0,0,0,2325,2323,1,0,0,0,2325,2326,1,0,0,0,2326,373,1,
        0,0,0,2327,2325,1,0,0,0,2328,2329,5,96,0,0,2329,2332,3,374,187,0,
        2330,2332,3,376,188,0,2331,2328,1,0,0,0,2331,2330,1,0,0,0,2332,375,
        1,0,0,0,2333,2337,3,398,199,0,2334,2336,3,378,189,0,2335,2334,1,
        0,0,0,2336,2339,1,0,0,0,2337,2335,1,0,0,0,2337,2338,1,0,0,0,2338,
        377,1,0,0,0,2339,2337,1,0,0,0,2340,2351,3,380,190,0,2341,2351,3,
        140,70,0,2342,2351,3,382,191,0,2343,2351,3,384,192,0,2344,2351,3,
        386,193,0,2345,2351,3,388,194,0,2346,2351,3,390,195,0,2347,2351,
        3,392,196,0,2348,2351,3,394,197,0,2349,2351,3,396,198,0,2350,2340,
        1,0,0,0,2350,2341,1,0,0,0,2350,2342,1,0,0,0,2350,2343,1,0,0,0,2350,
        2344,1,0,0,0,2350,2345,1,0,0,0,2350,2346,1,0,0,0,2350,2347,1,0,0,
        0,2350,2348,1,0,0,0,2350,2349,1,0,0,0,2351,379,1,0,0,0,2352,2353,
        5,40,0,0,2353,2354,3,398,199,0,2354,381,1,0,0,0,2355,2356,5,42,0,
        0,2356,2357,3,398,199,0,2357,383,1,0,0,0,2358,2359,5,36,0,0,2359,
        2360,3,398,199,0,2360,385,1,0,0,0,2361,2362,5,43,0,0,2362,2363,3,
        398,199,0,2363,387,1,0,0,0,2364,2365,5,37,0,0,2365,2366,3,398,199,
        0,2366,389,1,0,0,0,2367,2368,5,96,0,0,2368,2369,5,76,0,0,2369,2370,
        3,398,199,0,2370,391,1,0,0,0,2371,2372,5,76,0,0,2372,2373,3,398,
        199,0,2373,393,1,0,0,0,2374,2375,5,81,0,0,2375,2376,5,96,0,0,2376,
        2377,3,398,199,0,2377,395,1,0,0,0,2378,2379,5,81,0,0,2379,2380,3,
        398,199,0,2380,397,1,0,0,0,2381,2382,6,199,-1,0,2382,2383,3,400,
        200,0,2383,2389,1,0,0,0,2384,2385,10,2,0,0,2385,2386,5,34,0,0,2386,
        2388,3,400,200,0,2387,2384,1,0,0,0,2388,2391,1,0,0,0,2389,2387,1,
        0,0,0,2389,2390,1,0,0,0,2390,399,1,0,0,0,2391,2389,1,0,0,0,2392,
        2393,6,200,-1,0,2393,2394,3,402,201,0,2394,2400,1,0,0,0,2395,2396,
        10,2,0,0,2396,2397,5,45,0,0,2397,2399,3,402,201,0,2398,2395,1,0,
        0,0,2399,2402,1,0,0,0,2400,2398,1,0,0,0,2400,2401,1,0,0,0,2401,401,
        1,0,0,0,2402,2400,1,0,0,0,2403,2404,6,201,-1,0,2404,2405,3,404,202,
        0,2405,2411,1,0,0,0,2406,2407,10,2,0,0,2407,2408,5,35,0,0,2408,2410,
        3,404,202,0,2409,2406,1,0,0,0,2410,2413,1,0,0,0,2411,2409,1,0,0,
        0,2411,2412,1,0,0,0,2412,403,1,0,0,0,2413,2411,1,0,0,0,2414,2415,
        6,202,-1,0,2415,2416,3,406,203,0,2416,2422,1,0,0,0,2417,2418,10,
        2,0,0,2418,2419,7,10,0,0,2419,2421,3,406,203,0,2420,2417,1,0,0,0,
        2421,2424,1,0,0,0,2422,2420,1,0,0,0,2422,2423,1,0,0,0,2423,405,1,
        0,0,0,2424,2422,1,0,0,0,2425,2426,6,203,-1,0,2426,2427,3,408,204,
        0,2427,2433,1,0,0,0,2428,2429,10,2,0,0,2429,2430,7,9,0,0,2430,2432,
        3,408,204,0,2431,2428,1,0,0,0,2432,2435,1,0,0,0,2433,2431,1,0,0,
        0,2433,2434,1,0,0,0,2434,407,1,0,0,0,2435,2433,1,0,0,0,2436,2437,
        6,204,-1,0,2437,2438,3,410,205,0,2438,2444,1,0,0,0,2439,2440,10,
        2,0,0,2440,2441,7,11,0,0,2441,2443,3,410,205,0,2442,2439,1,0,0,0,
        2443,2446,1,0,0,0,2444,2442,1,0,0,0,2444,2445,1,0,0,0,2445,409,1,
        0,0,0,2446,2444,1,0,0,0,2447,2448,5,30,0,0,2448,2455,3,410,205,0,
        2449,2450,5,31,0,0,2450,2455,3,410,205,0,2451,2452,5,44,0,0,2452,
        2455,3,410,205,0,2453,2455,3,412,206,0,2454,2447,1,0,0,0,2454,2449,
        1,0,0,0,2454,2451,1,0,0,0,2454,2453,1,0,0,0,2455,411,1,0,0,0,2456,
        2459,3,158,79,0,2457,2458,5,48,0,0,2458,2460,3,410,205,0,2459,2457,
        1,0,0,0,2459,2460,1,0,0,0,2460,413,1,0,0,0,2461,2462,6,207,-1,0,
        2462,2463,3,166,83,0,2463,2481,1,0,0,0,2464,2477,10,2,0,0,2465,2466,
        5,26,0,0,2466,2478,3,518,259,0,2467,2478,3,142,71,0,2468,2470,5,
        20,0,0,2469,2471,3,478,239,0,2470,2469,1,0,0,0,2470,2471,1,0,0,0,
        2471,2472,1,0,0,0,2472,2478,5,23,0,0,2473,2474,5,21,0,0,2474,2475,
        3,416,208,0,2475,2476,5,24,0,0,2476,2478,1,0,0,0,2477,2465,1,0,0,
        0,2477,2467,1,0,0,0,2477,2468,1,0,0,0,2477,2473,1,0,0,0,2478,2480,
        1,0,0,0,2479,2464,1,0,0,0,2480,2483,1,0,0,0,2481,2479,1,0,0,0,2481,
        2482,1,0,0,0,2482,415,1,0,0,0,2483,2481,1,0,0,0,2484,2503,3,418,
        209,0,2485,2488,3,418,209,0,2486,2488,3,484,242,0,2487,2485,1,0,
        0,0,2487,2486,1,0,0,0,2488,2496,1,0,0,0,2489,2492,5,28,0,0,2490,
        2493,3,418,209,0,2491,2493,3,484,242,0,2492,2490,1,0,0,0,2492,2491,
        1,0,0,0,2493,2495,1,0,0,0,2494,2489,1,0,0,0,2495,2498,1,0,0,0,2496,
        2494,1,0,0,0,2496,2497,1,0,0,0,2497,2500,1,0,0,0,2498,2496,1,0,0,
        0,2499,2501,5,28,0,0,2500,2499,1,0,0,0,2500,2501,1,0,0,0,2501,2503,
        1,0,0,0,2502,2484,1,0,0,0,2502,2487,1,0,0,0,2503,417,1,0,0,0,2504,
        2506,3,356,178,0,2505,2504,1,0,0,0,2505,2506,1,0,0,0,2506,2507,1,
        0,0,0,2507,2509,5,27,0,0,2508,2510,3,356,178,0,2509,2508,1,0,0,0,
        2509,2510,1,0,0,0,2510,2515,1,0,0,0,2511,2513,5,27,0,0,2512,2514,
        3,356,178,0,2513,2512,1,0,0,0,2513,2514,1,0,0,0,2514,2516,1,0,0,
        0,2515,2511,1,0,0,0,2515,2516,1,0,0,0,2516,2519,1,0,0,0,2517,2519,
        3,368,184,0,2518,2505,1,0,0,0,2518,2517,1,0,0,0,2519,419,1,0,0,0,
        2520,2523,5,20,0,0,2521,2524,3,156,78,0,2522,2524,3,368,184,0,2523,
        2521,1,0,0,0,2523,2522,1,0,0,0,2524,2525,1,0,0,0,2525,2526,5,23,
        0,0,2526,421,1,0,0,0,2527,2529,5,86,0,0,2528,2530,3,424,212,0,2529,
        2528,1,0,0,0,2529,2530,1,0,0,0,2530,2531,1,0,0,0,2531,2532,5,27,
        0,0,2532,2533,3,356,178,0,2533,423,1,0,0,0,2534,2535,3,426,213,0,
        2535,425,1,0,0,0,2536,2540,3,130,65,0,2537,2539,3,124,62,0,2538,
        2537,1,0,0,0,2539,2542,1,0,0,0,2540,2538,1,0,0,0,2540,2541,1,0,0,
        0,2541,2546,1,0,0,0,2542,2540,1,0,0,0,2543,2545,3,126,63,0,2544,
        2543,1,0,0,0,2545,2548,1,0,0,0,2546,2544,1,0,0,0,2546,2547,1,0,0,
        0,2547,2550,1,0,0,0,2548,2546,1,0,0,0,2549,2551,3,428,214,0,2550,
        2549,1,0,0,0,2550,2551,1,0,0,0,2551,2586,1,0,0,0,2552,2556,3,132,
        66,0,2553,2555,3,126,63,0,2554,2553,1,0,0,0,2555,2558,1,0,0,0,2556,
        2554,1,0,0,0,2556,2557,1,0,0,0,2557,2560,1,0,0,0,2558,2556,1,0,0,
        0,2559,2561,3,428,214,0,2560,2559,1,0,0,0,2560,2561,1,0,0,0,2561,
        2586,1,0,0,0,2562,2564,3,124,62,0,2563,2562,1,0,0,0,2564,2565,1,
        0,0,0,2565,2563,1,0,0,0,2565,2566,1,0,0,0,2566,2570,1,0,0,0,2567,
        2569,3,126,63,0,2568,2567,1,0,0,0,2569,2572,1,0,0,0,2570,2568,1,
        0,0,0,2570,2571,1,0,0,0,2571,2574,1,0,0,0,2572,2570,1,0,0,0,2573,
        2575,3,428,214,0,2574,2573,1,0,0,0,2574,2575,1,0,0,0,2575,2586,1,
        0,0,0,2576,2578,3,126,63,0,2577,2576,1,0,0,0,2578,2579,1,0,0,0,2579,
        2577,1,0,0,0,2579,2580,1,0,0,0,2580,2582,1,0,0,0,2581,2583,3,428,
        214,0,2582,2581,1,0,0,0,2582,2583,1,0,0,0,2583,2586,1,0,0,0,2584,
        2586,3,428,214,0,2585,2536,1,0,0,0,2585,2552,1,0,0,0,2585,2563,1,
        0,0,0,2585,2577,1,0,0,0,2585,2584,1,0,0,0,2586,427,1,0,0,0,2587,
        2588,5,32,0,0,2588,2592,3,124,62,0,2589,2591,3,128,64,0,2590,2589,
        1,0,0,0,2591,2594,1,0,0,0,2592,2590,1,0,0,0,2592,2593,1,0,0,0,2593,
        2596,1,0,0,0,2594,2592,1,0,0,0,2595,2597,3,430,215,0,2596,2595,1,
        0,0,0,2596,2597,1,0,0,0,2597,2610,1,0,0,0,2598,2599,5,32,0,0,2599,
        2601,5,28,0,0,2600,2602,3,128,64,0,2601,2600,1,0,0,0,2602,2603,1,
        0,0,0,2603,2601,1,0,0,0,2603,2604,1,0,0,0,2604,2606,1,0,0,0,2605,
        2607,3,430,215,0,2606,2605,1,0,0,0,2606,2607,1,0,0,0,2607,2610,1,
        0,0,0,2608,2610,3,430,215,0,2609,2587,1,0,0,0,2609,2598,1,0,0,0,
        2609,2608,1,0,0,0,2610,429,1,0,0,0,2611,2612,5,48,0,0,2612,2613,
        3,124,62,0,2613,431,1,0,0,0,2614,2615,3,518,259,0,2615,433,1,0,0,
        0,2616,2619,3,436,218,0,2617,2619,5,6,0,0,2618,2616,1,0,0,0,2618,
        2617,1,0,0,0,2619,435,1,0,0,0,2620,2621,5,22,0,0,2621,2623,3,188,
        94,0,2622,2624,5,38,0,0,2623,2622,1,0,0,0,2623,2624,1,0,0,0,2624,
        2626,1,0,0,0,2625,2627,3,438,219,0,2626,2625,1,0,0,0,2626,2627,1,
        0,0,0,2627,2629,1,0,0,0,2628,2630,3,440,220,0,2629,2628,1,0,0,0,
        2629,2630,1,0,0,0,2630,2631,1,0,0,0,2631,2632,5,25,0,0,2632,437,
        1,0,0,0,2633,2634,5,67,0,0,2634,2635,3,518,259,0,2635,439,1,0,0,
        0,2636,2640,5,27,0,0,2637,2639,3,442,221,0,2638,2637,1,0,0,0,2639,
        2642,1,0,0,0,2640,2638,1,0,0,0,2640,2641,1,0,0,0,2641,441,1,0,0,
        0,2642,2640,1,0,0,0,2643,2646,5,6,0,0,2644,2646,3,436,218,0,2645,
        2643,1,0,0,0,2645,2644,1,0,0,0,2646,443,1,0,0,0,2647,2651,5,5,0,
        0,2648,2650,3,434,217,0,2649,2648,1,0,0,0,2650,2653,1,0,0,0,2651,
        2649,1,0,0,0,2651,2652,1,0,0,0,2652,2654,1,0,0,0,2653,2651,1,0,0,
        0,2654,2655,5,7,0,0,2655,445,1,0,0,0,2656,2659,5,9,0,0,2657,2659,
        3,450,225,0,2658,2656,1,0,0,0,2658,2657,1,0,0,0,2659,447,1,0,0,0,
        2660,2664,5,27,0,0,2661,2663,3,446,223,0,2662,2661,1,0,0,0,2663,
        2666,1,0,0,0,2664,2662,1,0,0,0,2664,2665,1,0,0,0,2665,449,1,0,0,
        0,2666,2664,1,0,0,0,2667,2668,5,22,0,0,2668,2670,3,188,94,0,2669,
        2671,5,38,0,0,2670,2669,1,0,0,0,2670,2671,1,0,0,0,2671,2673,1,0,
        0,0,2672,2674,3,438,219,0,2673,2672,1,0,0,0,2673,2674,1,0,0,0,2674,
        2676,1,0,0,0,2675,2677,3,448,224,0,2676,2675,1,0,0,0,2676,2677,1,
        0,0,0,2677,2678,1,0,0,0,2678,2679,5,25,0,0,2679,451,1,0,0,0,2680,
        2683,3,450,225,0,2681,2683,5,9,0,0,2682,2680,1,0,0,0,2682,2681,1,
        0,0,0,2683,453,1,0,0,0,2684,2688,5,8,0,0,2685,2687,3,452,226,0,2686,
        2685,1,0,0,0,2687,2690,1,0,0,0,2688,2686,1,0,0,0,2688,2689,1,0,0,
        0,2689,2691,1,0,0,0,2690,2688,1,0,0,0,2691,2692,5,10,0,0,2692,455,
        1,0,0,0,2693,2694,5,109,0,0,2694,457,1,0,0,0,2695,2698,3,444,222,
        0,2696,2698,3,456,228,0,2697,2695,1,0,0,0,2697,2696,1,0,0,0,2698,
        2699,1,0,0,0,2699,2697,1,0,0,0,2699,2700,1,0,0,0,2700,2707,1,0,0,
        0,2701,2703,3,454,227,0,2702,2701,1,0,0,0,2703,2704,1,0,0,0,2704,
        2702,1,0,0,0,2704,2705,1,0,0,0,2705,2707,1,0,0,0,2706,2697,1,0,0,
        0,2706,2702,1,0,0,0,2707,459,1,0,0,0,2708,2710,5,21,0,0,2709,2711,
        3,362,181,0,2710,2709,1,0,0,0,2710,2711,1,0,0,0,2711,2712,1,0,0,
        0,2712,2713,5,24,0,0,2713,461,1,0,0,0,2714,2720,5,20,0,0,2715,2716,
        3,364,182,0,2716,2718,5,28,0,0,2717,2719,3,362,181,0,2718,2717,1,
        0,0,0,2718,2719,1,0,0,0,2719,2721,1,0,0,0,2720,2715,1,0,0,0,2720,
        2721,1,0,0,0,2721,2722,1,0,0,0,2722,2723,5,23,0,0,2723,463,1,0,0,
        0,2724,2725,5,22,0,0,2725,2726,3,362,181,0,2726,2727,5,25,0,0,2727,
        465,1,0,0,0,2728,2730,5,22,0,0,2729,2731,3,468,234,0,2730,2729,1,
        0,0,0,2730,2731,1,0,0,0,2731,2732,1,0,0,0,2732,2733,5,25,0,0,2733,
        467,1,0,0,0,2734,2739,3,470,235,0,2735,2736,5,28,0,0,2736,2738,3,
        470,235,0,2737,2735,1,0,0,0,2738,2741,1,0,0,0,2739,2737,1,0,0,0,
        2739,2740,1,0,0,0,2740,2743,1,0,0,0,2741,2739,1,0,0,0,2742,2744,
        5,28,0,0,2743,2742,1,0,0,0,2743,2744,1,0,0,0,2744,469,1,0,0,0,2745,
        2746,5,48,0,0,2746,2749,3,398,199,0,2747,2749,3,472,236,0,2748,2745,
        1,0,0,0,2748,2747,1,0,0,0,2749,471,1,0,0,0,2750,2751,3,356,178,0,
        2751,2752,5,27,0,0,2752,2753,3,356,178,0,2753,473,1,0,0,0,2754,2756,
        3,476,238,0,2755,2754,1,0,0,0,2756,2757,1,0,0,0,2757,2755,1,0,0,
        0,2757,2758,1,0,0,0,2758,475,1,0,0,0,2759,2761,5,98,0,0,2760,2759,
        1,0,0,0,2760,2761,1,0,0,0,2761,2762,1,0,0,0,2762,2763,5,85,0,0,2763,
        2764,3,490,245,0,2764,2765,5,76,0,0,2765,2770,3,370,185,0,2766,2767,
        5,100,0,0,2767,2769,3,370,185,0,2768,2766,1,0,0,0,2769,2772,1,0,
        0,0,2770,2768,1,0,0,0,2770,2771,1,0,0,0,2771,477,1,0,0,0,2772,2770,
        1,0,0,0,2773,2775,3,480,240,0,2774,2776,5,28,0,0,2775,2774,1,0,0,
        0,2775,2776,1,0,0,0,2776,479,1,0,0,0,2777,2783,3,484,242,0,2778,
        2781,3,366,183,0,2779,2781,3,356,178,0,2780,2778,1,0,0,0,2780,2779,
        1,0,0,0,2781,2783,1,0,0,0,2782,2777,1,0,0,0,2782,2780,1,0,0,0,2783,
        2794,1,0,0,0,2784,2790,5,28,0,0,2785,2791,3,484,242,0,2786,2789,
        3,366,183,0,2787,2789,3,356,178,0,2788,2786,1,0,0,0,2788,2787,1,
        0,0,0,2789,2791,1,0,0,0,2790,2785,1,0,0,0,2790,2788,1,0,0,0,2791,
        2793,1,0,0,0,2792,2784,1,0,0,0,2793,2796,1,0,0,0,2794,2792,1,0,0,
        0,2794,2795,1,0,0,0,2795,2799,1,0,0,0,2796,2794,1,0,0,0,2797,2798,
        5,28,0,0,2798,2800,3,482,241,0,2799,2797,1,0,0,0,2799,2800,1,0,0,
        0,2800,2803,1,0,0,0,2801,2803,3,482,241,0,2802,2782,1,0,0,0,2802,
        2801,1,0,0,0,2803,481,1,0,0,0,2804,2809,3,486,243,0,2805,2806,5,
        28,0,0,2806,2808,3,486,243,0,2807,2805,1,0,0,0,2808,2811,1,0,0,0,
        2809,2807,1,0,0,0,2809,2810,1,0,0,0,2810,2821,1,0,0,0,2811,2809,
        1,0,0,0,2812,2813,5,28,0,0,2813,2818,3,488,244,0,2814,2815,5,28,
        0,0,2815,2817,3,488,244,0,2816,2814,1,0,0,0,2817,2820,1,0,0,0,2818,
        2816,1,0,0,0,2818,2819,1,0,0,0,2819,2822,1,0,0,0,2820,2818,1,0,0,
        0,2821,2812,1,0,0,0,2821,2822,1,0,0,0,2822,2832,1,0,0,0,2823,2828,
        3,488,244,0,2824,2825,5,28,0,0,2825,2827,3,488,244,0,2826,2824,1,
        0,0,0,2827,2830,1,0,0,0,2828,2826,1,0,0,0,2828,2829,1,0,0,0,2829,
        2832,1,0,0,0,2830,2828,1,0,0,0,2831,2804,1,0,0,0,2831,2823,1,0,0,
        0,2832,483,1,0,0,0,2833,2834,5,32,0,0,2834,2835,3,356,178,0,2835,
        485,1,0,0,0,2836,2837,3,518,259,0,2837,2838,5,38,0,0,2838,2839,3,
        356,178,0,2839,2842,1,0,0,0,2840,2842,3,484,242,0,2841,2836,1,0,
        0,0,2841,2840,1,0,0,0,2842,487,1,0,0,0,2843,2844,3,518,259,0,2844,
        2845,5,38,0,0,2845,2846,3,356,178,0,2846,2850,1,0,0,0,2847,2848,
        5,48,0,0,2848,2850,3,356,178,0,2849,2843,1,0,0,0,2849,2847,1,0,0,
        0,2850,489,1,0,0,0,2851,2856,3,496,248,0,2852,2853,5,28,0,0,2853,
        2855,3,496,248,0,2854,2852,1,0,0,0,2855,2858,1,0,0,0,2856,2854,1,
        0,0,0,2856,2857,1,0,0,0,2857,2860,1,0,0,0,2858,2856,1,0,0,0,2859,
        2861,5,28,0,0,2860,2859,1,0,0,0,2860,2861,1,0,0,0,2861,491,1,0,0,
        0,2862,2867,3,496,248,0,2863,2864,5,28,0,0,2864,2866,3,496,248,0,
        2865,2863,1,0,0,0,2866,2869,1,0,0,0,2867,2865,1,0,0,0,2867,2868,
        1,0,0,0,2868,2871,1,0,0,0,2869,2867,1,0,0,0,2870,2872,5,28,0,0,2871,
        2870,1,0,0,0,2871,2872,1,0,0,0,2872,493,1,0,0,0,2873,2884,3,496,
        248,0,2874,2885,5,28,0,0,2875,2876,5,28,0,0,2876,2878,3,496,248,
        0,2877,2875,1,0,0,0,2878,2879,1,0,0,0,2879,2877,1,0,0,0,2879,2880,
        1,0,0,0,2880,2882,1,0,0,0,2881,2883,5,28,0,0,2882,2881,1,0,0,0,2882,
        2883,1,0,0,0,2883,2885,1,0,0,0,2884,2874,1,0,0,0,2884,2877,1,0,0,
        0,2885,495,1,0,0,0,2886,2887,5,32,0,0,2887,2890,3,496,248,0,2888,
        2890,3,498,249,0,2889,2886,1,0,0,0,2889,2888,1,0,0,0,2890,497,1,
        0,0,0,2891,2898,3,506,253,0,2892,2893,5,26,0,0,2893,2899,3,518,259,
        0,2894,2895,5,21,0,0,2895,2896,3,416,208,0,2896,2897,5,24,0,0,2897,
        2899,1,0,0,0,2898,2892,1,0,0,0,2898,2894,1,0,0,0,2899,2902,1,0,0,
        0,2900,2902,3,500,250,0,2901,2891,1,0,0,0,2901,2900,1,0,0,0,2902,
        499,1,0,0,0,2903,2919,3,518,259,0,2904,2905,5,20,0,0,2905,2906,3,
        498,249,0,2906,2907,5,23,0,0,2907,2919,1,0,0,0,2908,2910,5,20,0,
        0,2909,2911,3,494,247,0,2910,2909,1,0,0,0,2910,2911,1,0,0,0,2911,
        2912,1,0,0,0,2912,2919,5,23,0,0,2913,2915,5,21,0,0,2914,2916,3,492,
        246,0,2915,2914,1,0,0,0,2915,2916,1,0,0,0,2916,2917,1,0,0,0,2917,
        2919,5,24,0,0,2918,2903,1,0,0,0,2918,2904,1,0,0,0,2918,2908,1,0,
        0,0,2918,2913,1,0,0,0,2919,501,1,0,0,0,2920,2927,3,504,252,0,2921,
        2927,3,518,259,0,2922,2923,5,20,0,0,2923,2924,3,502,251,0,2924,2925,
        5,23,0,0,2925,2927,1,0,0,0,2926,2920,1,0,0,0,2926,2921,1,0,0,0,2926,
        2922,1,0,0,0,2927,503,1,0,0,0,2928,2935,3,506,253,0,2929,2930,5,
        26,0,0,2930,2936,3,518,259,0,2931,2932,5,21,0,0,2932,2933,3,416,
        208,0,2933,2934,5,24,0,0,2934,2936,1,0,0,0,2935,2929,1,0,0,0,2935,
        2931,1,0,0,0,2936,505,1,0,0,0,2937,2938,6,253,-1,0,2938,2939,3,166,
        83,0,2939,2957,1,0,0,0,2940,2953,10,2,0,0,2941,2942,5,26,0,0,2942,
        2954,3,518,259,0,2943,2944,5,21,0,0,2944,2945,3,416,208,0,2945,2946,
        5,24,0,0,2946,2954,1,0,0,0,2947,2954,3,142,71,0,2948,2950,5,20,0,
        0,2949,2951,3,478,239,0,2950,2949,1,0,0,0,2950,2951,1,0,0,0,2951,
        2952,1,0,0,0,2952,2954,5,23,0,0,2953,2941,1,0,0,0,2953,2943,1,0,
        0,0,2953,2947,1,0,0,0,2953,2948,1,0,0,0,2954,2956,1,0,0,0,2955,2940,
        1,0,0,0,2956,2959,1,0,0,0,2957,2955,1,0,0,0,2957,2958,1,0,0,0,2958,
        507,1,0,0,0,2959,2957,1,0,0,0,2960,2965,3,510,255,0,2961,2962,5,
        28,0,0,2962,2964,3,510,255,0,2963,2961,1,0,0,0,2964,2967,1,0,0,0,
        2965,2963,1,0,0,0,2965,2966,1,0,0,0,2966,2969,1,0,0,0,2967,2965,
        1,0,0,0,2968,2970,5,28,0,0,2969,2968,1,0,0,0,2969,2970,1,0,0,0,2970,
        509,1,0,0,0,2971,2978,3,506,253,0,2972,2973,5,26,0,0,2973,2979,3,
        518,259,0,2974,2975,5,21,0,0,2975,2976,3,416,208,0,2976,2977,5,24,
        0,0,2977,2979,1,0,0,0,2978,2972,1,0,0,0,2978,2974,1,0,0,0,2979,2982,
        1,0,0,0,2980,2982,3,512,256,0,2981,2971,1,0,0,0,2981,2980,1,0,0,
        0,2982,511,1,0,0,0,2983,2999,3,518,259,0,2984,2985,5,20,0,0,2985,
        2986,3,510,255,0,2986,2987,5,23,0,0,2987,2999,1,0,0,0,2988,2990,
        5,20,0,0,2989,2991,3,508,254,0,2990,2989,1,0,0,0,2990,2991,1,0,0,
        0,2991,2992,1,0,0,0,2992,2999,5,23,0,0,2993,2995,5,21,0,0,2994,2996,
        3,508,254,0,2995,2994,1,0,0,0,2995,2996,1,0,0,0,2996,2997,1,0,0,
        0,2997,2999,5,24,0,0,2998,2983,1,0,0,0,2998,2984,1,0,0,0,2998,2988,
        1,0,0,0,2998,2993,1,0,0,0,2999,513,1,0,0,0,3000,3005,3,356,178,0,
        3001,3002,5,28,0,0,3002,3004,3,356,178,0,3003,3001,1,0,0,0,3004,
        3007,1,0,0,0,3005,3003,1,0,0,0,3005,3006,1,0,0,0,3006,3020,1,0,0,
        0,3007,3005,1,0,0,0,3008,3018,5,28,0,0,3009,3010,5,32,0,0,3010,3014,
        3,356,178,0,3011,3012,5,28,0,0,3012,3013,5,48,0,0,3013,3015,3,356,
        178,0,3014,3011,1,0,0,0,3014,3015,1,0,0,0,3015,3019,1,0,0,0,3016,
        3017,5,48,0,0,3017,3019,3,356,178,0,3018,3009,1,0,0,0,3018,3016,
        1,0,0,0,3019,3021,1,0,0,0,3020,3008,1,0,0,0,3020,3021,1,0,0,0,3021,
        3032,1,0,0,0,3022,3023,5,32,0,0,3023,3027,3,356,178,0,3024,3025,
        5,28,0,0,3025,3026,5,48,0,0,3026,3028,3,356,178,0,3027,3024,1,0,
        0,0,3027,3028,1,0,0,0,3028,3032,1,0,0,0,3029,3030,5,48,0,0,3030,
        3032,3,356,178,0,3031,3000,1,0,0,0,3031,3022,1,0,0,0,3031,3029,1,
        0,0,0,3032,515,1,0,0,0,3033,3034,5,110,0,0,3034,3037,5,4,0,0,3035,
        3037,5,4,0,0,3036,3033,1,0,0,0,3036,3035,1,0,0,0,3037,517,1,0,0,
        0,3038,3041,5,106,0,0,3039,3041,3,138,69,0,3040,3038,1,0,0,0,3040,
        3039,1,0,0,0,3041,519,1,0,0,0,406,521,529,533,539,543,548,561,568,
        572,576,581,587,594,596,600,602,608,616,633,637,641,646,652,659,
        663,667,671,678,680,682,685,689,695,699,702,706,713,716,719,723,
        726,735,742,756,762,769,776,783,788,794,803,807,812,819,826,830,
        834,840,844,848,850,857,864,869,875,882,887,892,894,903,905,912,
        914,919,923,929,942,954,958,963,970,977,981,985,992,1005,1007,1016,
        1022,1026,1031,1038,1045,1049,1053,1061,1076,1082,1088,1097,1101,
        1106,1118,1120,1127,1131,1136,1141,1147,1153,1160,1166,1169,1172,
        1176,1190,1197,1205,1211,1218,1229,1236,1244,1250,1256,1262,1268,
        1276,1282,1286,1297,1306,1324,1338,1340,1346,1350,1358,1362,1372,
        1376,1381,1393,1397,1404,1412,1417,1421,1430,1443,1447,1453,1456,
        1464,1471,1479,1487,1497,1504,1508,1526,1536,1543,1550,1556,1563,
        1567,1573,1577,1585,1587,1597,1606,1618,1622,1627,1633,1640,1646,
        1653,1659,1669,1678,1686,1692,1697,1701,1704,1713,1718,1722,1727,
        1731,1739,1743,1748,1752,1756,1764,1770,1774,1780,1784,1789,1794,
        1798,1803,1806,1809,1816,1820,1827,1831,1838,1841,1844,1851,1871,
        1873,1881,1883,1894,1899,1912,1915,1918,1926,1929,1932,1934,1940,
        1943,1953,1956,1973,1980,1983,1988,1998,2002,2013,2024,2032,2040,
        2047,2052,2073,2080,2089,2094,2097,2102,2109,2113,2117,2127,2135,
        2138,2142,2149,2154,2167,2170,2173,2175,2184,2192,2202,2216,2220,
        2224,2227,2232,2237,2239,2255,2259,2267,2270,2277,2281,2286,2293,
        2297,2302,2310,2317,2325,2331,2337,2350,2389,2400,2411,2422,2433,
        2444,2454,2459,2470,2477,2481,2487,2492,2496,2500,2502,2505,2509,
        2513,2515,2518,2523,2529,2540,2546,2550,2556,2560,2565,2570,2574,
        2579,2582,2585,2592,2596,2603,2606,2609,2618,2623,2626,2629,2640,
        2645,2651,2658,2664,2670,2673,2676,2682,2688,2697,2699,2704,2706,
        2710,2718,2720,2730,2739,2743,2748,2757,2760,2770,2775,2780,2782,
        2788,2790,2794,2799,2802,2809,2818,2821,2828,2831,2841,2849,2856,
        2860,2867,2871,2879,2882,2884,2889,2898,2901,2910,2915,2918,2926,
        2935,2950,2953,2957,2965,2969,2978,2981,2990,2995,2998,3005,3014,
        3018,3020,3027,3031,3036,3040
    ]

class PsithonParser ( Parser ):

    grammarFileName = "PsithonParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'<>'", "'lazy'", "'('", 
                     "'['", "<INVALID>", "')'", "']'", "<INVALID>", "'.'", 
                     "':'", "','", "';'", "'+'", "'-'", "'*'", "'/'", "'|'", 
                     "'&'", "'<'", "'>'", "'='", "'%'", "'=='", "'!='", 
                     "'<='", "'>='", "'~'", "'^'", "'<<'", "'>>'", "'**'", 
                     "'+='", "'-='", "'*='", "'/='", "'%='", "'&='", "'|='", 
                     "'^='", "'<<='", "'>>='", "'**='", "'//'", "'//='", 
                     "'@'", "'@='", "'->'", "'...'", "':='", "'!'", "'False'", 
                     "'await'", "'else'", "'import'", "'pass'", "'None'", 
                     "'break'", "'except'", "'in'", "'raise'", "'True'", 
                     "'class'", "'finally'", "'is'", "'return'", "'and'", 
                     "'continue'", "'for'", "'lambda'", "'try'", "'as'", 
                     "'def'", "'from'", "'nonlocal'", "'while'", "'assert'", 
                     "'del'", "'global'", "'not'", "'with'", "'async'", 
                     "'elif'", "'if'", "'or'", "'yield'", "'type'", "'match'", 
                     "'case'", "'_'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'--'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'\\#'", "<INVALID>", "<INVALID>", "'\\uFEFF'" ]

    symbolicNames = [ "<INVALID>", "ENCODING", "INDENT", "DEDENT", "TYPE_COMMENT", 
                      "FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END", 
                      "TSTRING_START", "TSTRING_MIDDLE", "TSTRING_END", 
                      "PSI_MOLECULE", "PSI_SET", "PSI_BASIS", "PSI_EXTERNAL", 
                      "PSI_PCM", "PSI_CFOUR", "PSI_MEMORY", "PSI_BARRY_NOTEQUAL", 
                      "NAME_OR_LAZY", "LPAR", "LSQB", "LBRACE", "RPAR", 
                      "RSQB", "RBRACE", "DOT", "COLON", "COMMA", "SEMI", 
                      "PLUS", "MINUS", "STAR", "SLASH", "VBAR", "AMPER", 
                      "LESS", "GREATER", "EQUAL", "PERCENT", "EQEQUAL", 
                      "NOTEQUAL", "LESSEQUAL", "GREATEREQUAL", "TILDE", 
                      "CIRCUMFLEX", "LEFTSHIFT", "RIGHTSHIFT", "DOUBLESTAR", 
                      "PLUSEQUAL", "MINEQUAL", "STAREQUAL", "SLASHEQUAL", 
                      "PERCENTEQUAL", "AMPEREQUAL", "VBAREQUAL", "CIRCUMFLEXEQUAL", 
                      "LEFTSHIFTEQUAL", "RIGHTSHIFTEQUAL", "DOUBLESTAREQUAL", 
                      "DOUBLESLASH", "DOUBLESLASHEQUAL", "AT", "ATEQUAL", 
                      "RARROW", "ELLIPSIS", "COLONEQUAL", "EXCLAMATION", 
                      "FALSE", "AWAIT", "ELSE", "IMPORT", "PASS", "NONE", 
                      "BREAK", "EXCEPT", "IN", "RAISE", "TRUE", "CLASS", 
                      "FINALLY", "IS", "RETURN", "AND", "CONTINUE", "FOR", 
                      "LAMBDA", "TRY", "AS", "DEF", "FROM", "NONLOCAL", 
                      "WHILE", "ASSERT", "DEL", "GLOBAL", "NOT", "WITH", 
                      "ASYNC", "ELIF", "IF", "OR", "YIELD", "NAME_OR_TYPE", 
                      "NAME_OR_MATCH", "NAME_OR_CASE", "NAME_OR_WILDCARD", 
                      "NAME", "NUMBER", "STRING", "NEWLINE", "COMMENT", 
                      "WS", "EXPLICIT_LINE_JOINING", "ERRORTOKEN", "D_WS", 
                      "D_COMMENT", "D_NEWLINE", "D_LBRACE", "D_RBRACE", 
                      "D_LBRACKET", "D_RBRACKET", "D_LPAREN", "D_RPAREN", 
                      "D_EQUALS", "D_COMMA", "D_COLON", "D_DOLLAR", "D_AT", 
                      "D_STAR", "D_PLUS", "D_MINUS", "D_SLASH", "D_DOT", 
                      "D_SEPARATOR", "D_UNITS", "D_NO_COM", "D_NO_REORIENT", 
                      "D_SYMMETRY", "D_PUBCHEM", "D_FROM_FILE", "D_EFP", 
                      "D_GHOST", "D_ASSIGN", "D_NUMBER", "D_WORD", "D_HYPHEN_WORD", 
                      "D_STRING", "D_ESC_HASH", "D_OTHER", "CFOUR_TEXT", 
                      "BOM" ]

    RULE_file_input = 0
    RULE_statement = 1
    RULE_psithon_statement = 2
    RULE_molecule_block = 3
    RULE_molecule_name = 4
    RULE_molecule_body = 5
    RULE_molecule_line = 6
    RULE_xyz_header = 7
    RULE_charge_multiplicity = 8
    RULE_geometry_variable = 9
    RULE_unit_name = 10
    RULE_atom_line = 11
    RULE_nucleus = 12
    RULE_nucleus_label = 13
    RULE_isotope_mass = 14
    RULE_coordinate = 15
    RULE_anchor_pair = 16
    RULE_efp_fragment = 17
    RULE_numeric_xyz = 18
    RULE_set_command = 19
    RULE_set_block = 20
    RULE_module_list = 21
    RULE_module_name = 22
    RULE_module_piece = 23
    RULE_option_key = 24
    RULE_option_assignment = 25
    RULE_inline_option_value = 26
    RULE_set_option_value = 27
    RULE_set_option_array = 28
    RULE_set_option_piece = 29
    RULE_inline_option_scalar = 30
    RULE_inline_option_piece = 31
    RULE_option_reference = 32
    RULE_memory_line = 33
    RULE_basis_block = 34
    RULE_basis_line = 35
    RULE_basis_assignment = 36
    RULE_basis_name = 37
    RULE_basis_label = 38
    RULE_basis_record = 39
    RULE_external_block = 40
    RULE_external_line = 41
    RULE_external_basis_line = 42
    RULE_external_basis_key = 43
    RULE_pcm_block = 44
    RULE_pcm_body = 45
    RULE_cfour_block = 46
    RULE_header_label = 47
    RULE_header_space = 48
    RULE_native_word = 49
    RULE_native_identifier = 50
    RULE_literal_line = 51
    RULE_literal_piece = 52
    RULE_param_end = 53
    RULE_slash_end = 54
    RULE_param_no_default = 55
    RULE_param_no_default_star_annotation = 56
    RULE_param_with_default = 57
    RULE_param_maybe_default = 58
    RULE_slash_no_default = 59
    RULE_slash_with_default = 60
    RULE_lambda_param_end = 61
    RULE_lambda_param_no_default = 62
    RULE_lambda_param_with_default = 63
    RULE_lambda_param_maybe_default = 64
    RULE_lambda_slash_no_default = 65
    RULE_lambda_slash_with_default = 66
    RULE_import_name = 67
    RULE_import_from = 68
    RULE_name_except_underscore = 69
    RULE_noteq_bitwise_or = 70
    RULE_genexp = 71
    RULE_dictcomp = 72
    RULE_listcomp = 73
    RULE_setcomp = 74
    RULE_return_stmt = 75
    RULE_break_stmt = 76
    RULE_continue_stmt = 77
    RULE_yield_expr = 78
    RULE_await_primary = 79
    RULE_for_stmt = 80
    RULE_with_stmt = 81
    RULE_native_expression = 82
    RULE_atom = 83
    RULE_interactive = 84
    RULE_eval = 85
    RULE_func_type = 86
    RULE_statements = 87
    RULE_single_compound_stmt = 88
    RULE_statement_newline = 89
    RULE_simple_stmts = 90
    RULE_simple_stmt = 91
    RULE_compound_stmt = 92
    RULE_assignment = 93
    RULE_annotated_rhs = 94
    RULE_augassign = 95
    RULE_raise_stmt = 96
    RULE_pass_stmt = 97
    RULE_global_stmt = 98
    RULE_nonlocal_stmt = 99
    RULE_del_stmt = 100
    RULE_yield_stmt = 101
    RULE_assert_stmt = 102
    RULE_import_stmt = 103
    RULE_import_from_targets = 104
    RULE_import_from_as_names = 105
    RULE_import_from_as_name = 106
    RULE_dotted_as_names = 107
    RULE_dotted_as_name = 108
    RULE_dotted_name = 109
    RULE_block = 110
    RULE_decorators = 111
    RULE_class_def = 112
    RULE_class_def_raw = 113
    RULE_function_def = 114
    RULE_function_def_raw = 115
    RULE_params = 116
    RULE_parameters = 117
    RULE_star_etc = 118
    RULE_kwds = 119
    RULE_param = 120
    RULE_param_star_annotation = 121
    RULE_annotation = 122
    RULE_star_annotation = 123
    RULE_default_assignment = 124
    RULE_if_stmt = 125
    RULE_elif_stmt = 126
    RULE_else_block = 127
    RULE_while_stmt = 128
    RULE_with_item = 129
    RULE_try_stmt = 130
    RULE_except_block = 131
    RULE_except_star_block = 132
    RULE_finally_block = 133
    RULE_match_stmt = 134
    RULE_subject_expr = 135
    RULE_case_block = 136
    RULE_guard = 137
    RULE_patterns = 138
    RULE_pattern = 139
    RULE_as_pattern = 140
    RULE_or_pattern = 141
    RULE_closed_pattern = 142
    RULE_literal_pattern = 143
    RULE_literal_expr = 144
    RULE_complex_number = 145
    RULE_signed_number = 146
    RULE_signed_real_number = 147
    RULE_real_number = 148
    RULE_imaginary_number = 149
    RULE_capture_pattern = 150
    RULE_pattern_capture_target = 151
    RULE_wildcard_pattern = 152
    RULE_value_pattern = 153
    RULE_attr = 154
    RULE_name_or_attr = 155
    RULE_group_pattern = 156
    RULE_sequence_pattern = 157
    RULE_open_sequence_pattern = 158
    RULE_maybe_sequence_pattern = 159
    RULE_maybe_star_pattern = 160
    RULE_star_pattern = 161
    RULE_mapping_pattern = 162
    RULE_items_pattern = 163
    RULE_key_value_pattern = 164
    RULE_double_star_pattern = 165
    RULE_class_pattern = 166
    RULE_positional_patterns = 167
    RULE_keyword_patterns = 168
    RULE_keyword_pattern = 169
    RULE_type_alias = 170
    RULE_type_params = 171
    RULE_type_param_seq = 172
    RULE_type_param = 173
    RULE_type_param_bound = 174
    RULE_type_param_default = 175
    RULE_type_param_starred_default = 176
    RULE_expressions = 177
    RULE_expression = 178
    RULE_star_expressions = 179
    RULE_star_expression = 180
    RULE_star_named_expressions = 181
    RULE_star_named_expression = 182
    RULE_assignment_expression = 183
    RULE_named_expression = 184
    RULE_disjunction = 185
    RULE_conjunction = 186
    RULE_inversion = 187
    RULE_comparison = 188
    RULE_compare_op_bitwise_or_pair = 189
    RULE_eq_bitwise_or = 190
    RULE_lte_bitwise_or = 191
    RULE_lt_bitwise_or = 192
    RULE_gte_bitwise_or = 193
    RULE_gt_bitwise_or = 194
    RULE_notin_bitwise_or = 195
    RULE_in_bitwise_or = 196
    RULE_isnot_bitwise_or = 197
    RULE_is_bitwise_or = 198
    RULE_bitwise_or = 199
    RULE_bitwise_xor = 200
    RULE_bitwise_and = 201
    RULE_shift_expr = 202
    RULE_sum = 203
    RULE_term = 204
    RULE_factor = 205
    RULE_power = 206
    RULE_primary = 207
    RULE_slices = 208
    RULE_slice = 209
    RULE_group = 210
    RULE_lambdef = 211
    RULE_lambda_params = 212
    RULE_lambda_parameters = 213
    RULE_lambda_star_etc = 214
    RULE_lambda_kwds = 215
    RULE_lambda_param = 216
    RULE_fstring_middle = 217
    RULE_fstring_replacement_field = 218
    RULE_fstring_conversion = 219
    RULE_fstring_full_format_spec = 220
    RULE_fstring_format_spec = 221
    RULE_fstring = 222
    RULE_tstring_format_spec = 223
    RULE_tstring_full_format_spec = 224
    RULE_tstring_replacement_field = 225
    RULE_tstring_middle = 226
    RULE_tstring = 227
    RULE_string = 228
    RULE_strings = 229
    RULE_list = 230
    RULE_tuple = 231
    RULE_set = 232
    RULE_dict = 233
    RULE_double_starred_kvpairs = 234
    RULE_double_starred_kvpair = 235
    RULE_kvpair = 236
    RULE_for_if_clauses = 237
    RULE_for_if_clause = 238
    RULE_arguments = 239
    RULE_args = 240
    RULE_kwargs = 241
    RULE_starred_expression = 242
    RULE_kwarg_or_starred = 243
    RULE_kwarg_or_double_starred = 244
    RULE_star_targets = 245
    RULE_star_targets_list_seq = 246
    RULE_star_targets_tuple_seq = 247
    RULE_star_target = 248
    RULE_target_with_star_atom = 249
    RULE_star_atom = 250
    RULE_single_target = 251
    RULE_single_subscript_attribute_target = 252
    RULE_t_primary = 253
    RULE_del_targets = 254
    RULE_del_target = 255
    RULE_del_t_atom = 256
    RULE_type_expressions = 257
    RULE_func_type_comment = 258
    RULE_name = 259

    ruleNames =  [ "file_input", "statement", "psithon_statement", "molecule_block", 
                   "molecule_name", "molecule_body", "molecule_line", "xyz_header", 
                   "charge_multiplicity", "geometry_variable", "unit_name", 
                   "atom_line", "nucleus", "nucleus_label", "isotope_mass", 
                   "coordinate", "anchor_pair", "efp_fragment", "numeric_xyz", 
                   "set_command", "set_block", "module_list", "module_name", 
                   "module_piece", "option_key", "option_assignment", "inline_option_value", 
                   "set_option_value", "set_option_array", "set_option_piece", 
                   "inline_option_scalar", "inline_option_piece", "option_reference", 
                   "memory_line", "basis_block", "basis_line", "basis_assignment", 
                   "basis_name", "basis_label", "basis_record", "external_block", 
                   "external_line", "external_basis_line", "external_basis_key", 
                   "pcm_block", "pcm_body", "cfour_block", "header_label", 
                   "header_space", "native_word", "native_identifier", "literal_line", 
                   "literal_piece", "param_end", "slash_end", "param_no_default", 
                   "param_no_default_star_annotation", "param_with_default", 
                   "param_maybe_default", "slash_no_default", "slash_with_default", 
                   "lambda_param_end", "lambda_param_no_default", "lambda_param_with_default", 
                   "lambda_param_maybe_default", "lambda_slash_no_default", 
                   "lambda_slash_with_default", "import_name", "import_from", 
                   "name_except_underscore", "noteq_bitwise_or", "genexp", 
                   "dictcomp", "listcomp", "setcomp", "return_stmt", "break_stmt", 
                   "continue_stmt", "yield_expr", "await_primary", "for_stmt", 
                   "with_stmt", "native_expression", "atom", "interactive", 
                   "eval", "func_type", "statements", "single_compound_stmt", 
                   "statement_newline", "simple_stmts", "simple_stmt", "compound_stmt", 
                   "assignment", "annotated_rhs", "augassign", "raise_stmt", 
                   "pass_stmt", "global_stmt", "nonlocal_stmt", "del_stmt", 
                   "yield_stmt", "assert_stmt", "import_stmt", "import_from_targets", 
                   "import_from_as_names", "import_from_as_name", "dotted_as_names", 
                   "dotted_as_name", "dotted_name", "block", "decorators", 
                   "class_def", "class_def_raw", "function_def", "function_def_raw", 
                   "params", "parameters", "star_etc", "kwds", "param", 
                   "param_star_annotation", "annotation", "star_annotation", 
                   "default_assignment", "if_stmt", "elif_stmt", "else_block", 
                   "while_stmt", "with_item", "try_stmt", "except_block", 
                   "except_star_block", "finally_block", "match_stmt", "subject_expr", 
                   "case_block", "guard", "patterns", "pattern", "as_pattern", 
                   "or_pattern", "closed_pattern", "literal_pattern", "literal_expr", 
                   "complex_number", "signed_number", "signed_real_number", 
                   "real_number", "imaginary_number", "capture_pattern", 
                   "pattern_capture_target", "wildcard_pattern", "value_pattern", 
                   "attr", "name_or_attr", "group_pattern", "sequence_pattern", 
                   "open_sequence_pattern", "maybe_sequence_pattern", "maybe_star_pattern", 
                   "star_pattern", "mapping_pattern", "items_pattern", "key_value_pattern", 
                   "double_star_pattern", "class_pattern", "positional_patterns", 
                   "keyword_patterns", "keyword_pattern", "type_alias", 
                   "type_params", "type_param_seq", "type_param", "type_param_bound", 
                   "type_param_default", "type_param_starred_default", "expressions", 
                   "expression", "star_expressions", "star_expression", 
                   "star_named_expressions", "star_named_expression", "assignment_expression", 
                   "named_expression", "disjunction", "conjunction", "inversion", 
                   "comparison", "compare_op_bitwise_or_pair", "eq_bitwise_or", 
                   "lte_bitwise_or", "lt_bitwise_or", "gte_bitwise_or", 
                   "gt_bitwise_or", "notin_bitwise_or", "in_bitwise_or", 
                   "isnot_bitwise_or", "is_bitwise_or", "bitwise_or", "bitwise_xor", 
                   "bitwise_and", "shift_expr", "sum", "term", "factor", 
                   "power", "primary", "slices", "slice", "group", "lambdef", 
                   "lambda_params", "lambda_parameters", "lambda_star_etc", 
                   "lambda_kwds", "lambda_param", "fstring_middle", "fstring_replacement_field", 
                   "fstring_conversion", "fstring_full_format_spec", "fstring_format_spec", 
                   "fstring", "tstring_format_spec", "tstring_full_format_spec", 
                   "tstring_replacement_field", "tstring_middle", "tstring", 
                   "string", "strings", "list", "tuple", "set", "dict", 
                   "double_starred_kvpairs", "double_starred_kvpair", "kvpair", 
                   "for_if_clauses", "for_if_clause", "arguments", "args", 
                   "kwargs", "starred_expression", "kwarg_or_starred", "kwarg_or_double_starred", 
                   "star_targets", "star_targets_list_seq", "star_targets_tuple_seq", 
                   "star_target", "target_with_star_atom", "star_atom", 
                   "single_target", "single_subscript_attribute_target", 
                   "t_primary", "del_targets", "del_target", "del_t_atom", 
                   "type_expressions", "func_type_comment", "name" ]

    EOF = Token.EOF
    ENCODING=1
    INDENT=2
    DEDENT=3
    TYPE_COMMENT=4
    FSTRING_START=5
    FSTRING_MIDDLE=6
    FSTRING_END=7
    TSTRING_START=8
    TSTRING_MIDDLE=9
    TSTRING_END=10
    PSI_MOLECULE=11
    PSI_SET=12
    PSI_BASIS=13
    PSI_EXTERNAL=14
    PSI_PCM=15
    PSI_CFOUR=16
    PSI_MEMORY=17
    PSI_BARRY_NOTEQUAL=18
    NAME_OR_LAZY=19
    LPAR=20
    LSQB=21
    LBRACE=22
    RPAR=23
    RSQB=24
    RBRACE=25
    DOT=26
    COLON=27
    COMMA=28
    SEMI=29
    PLUS=30
    MINUS=31
    STAR=32
    SLASH=33
    VBAR=34
    AMPER=35
    LESS=36
    GREATER=37
    EQUAL=38
    PERCENT=39
    EQEQUAL=40
    NOTEQUAL=41
    LESSEQUAL=42
    GREATEREQUAL=43
    TILDE=44
    CIRCUMFLEX=45
    LEFTSHIFT=46
    RIGHTSHIFT=47
    DOUBLESTAR=48
    PLUSEQUAL=49
    MINEQUAL=50
    STAREQUAL=51
    SLASHEQUAL=52
    PERCENTEQUAL=53
    AMPEREQUAL=54
    VBAREQUAL=55
    CIRCUMFLEXEQUAL=56
    LEFTSHIFTEQUAL=57
    RIGHTSHIFTEQUAL=58
    DOUBLESTAREQUAL=59
    DOUBLESLASH=60
    DOUBLESLASHEQUAL=61
    AT=62
    ATEQUAL=63
    RARROW=64
    ELLIPSIS=65
    COLONEQUAL=66
    EXCLAMATION=67
    FALSE=68
    AWAIT=69
    ELSE=70
    IMPORT=71
    PASS=72
    NONE=73
    BREAK=74
    EXCEPT=75
    IN=76
    RAISE=77
    TRUE=78
    CLASS=79
    FINALLY=80
    IS=81
    RETURN=82
    AND=83
    CONTINUE=84
    FOR=85
    LAMBDA=86
    TRY=87
    AS=88
    DEF=89
    FROM=90
    NONLOCAL=91
    WHILE=92
    ASSERT=93
    DEL=94
    GLOBAL=95
    NOT=96
    WITH=97
    ASYNC=98
    ELIF=99
    IF=100
    OR=101
    YIELD=102
    NAME_OR_TYPE=103
    NAME_OR_MATCH=104
    NAME_OR_CASE=105
    NAME_OR_WILDCARD=106
    NAME=107
    NUMBER=108
    STRING=109
    NEWLINE=110
    COMMENT=111
    WS=112
    EXPLICIT_LINE_JOINING=113
    ERRORTOKEN=114
    D_WS=115
    D_COMMENT=116
    D_NEWLINE=117
    D_LBRACE=118
    D_RBRACE=119
    D_LBRACKET=120
    D_RBRACKET=121
    D_LPAREN=122
    D_RPAREN=123
    D_EQUALS=124
    D_COMMA=125
    D_COLON=126
    D_DOLLAR=127
    D_AT=128
    D_STAR=129
    D_PLUS=130
    D_MINUS=131
    D_SLASH=132
    D_DOT=133
    D_SEPARATOR=134
    D_UNITS=135
    D_NO_COM=136
    D_NO_REORIENT=137
    D_SYMMETRY=138
    D_PUBCHEM=139
    D_FROM_FILE=140
    D_EFP=141
    D_GHOST=142
    D_ASSIGN=143
    D_NUMBER=144
    D_WORD=145
    D_HYPHEN_WORD=146
    D_STRING=147
    D_ESC_HASH=148
    D_OTHER=149
    CFOUR_TEXT=150
    BOM=151

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



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




    class File_inputContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(PsithonParser.EOF, 0)

        def statements(self):
            return self.getTypedRuleContext(PsithonParser.StatementsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_file_input




    def file_input(self):

        localctx = PsithonParser.File_inputContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_file_input)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 521
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.state = 520
                self.statements()


            self.state = 523
            self.match(PsithonParser.EOF)
            (self.psithon_validate_input(localctx) if self.psithon_deferred() else self.psithon_constraints(localctx)) if self.getNumberOfSyntaxErrors() == 0 else None
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def psithon_statement(self):
            return self.getTypedRuleContext(PsithonParser.Psithon_statementContext,0)


        def compound_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Compound_stmtContext,0)


        def simple_stmts(self):
            return self.getTypedRuleContext(PsithonParser.Simple_stmtsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_statement




    def statement(self):

        localctx = PsithonParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 529
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 526
                self.psithon_statement()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 527
                self.compound_stmt()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 528
                self.simple_stmts()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Psithon_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_expression(self):
            return self.getTypedRuleContext(PsithonParser.Native_expressionContext,0)


        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_psithon_statement




    def psithon_statement(self):

        localctx = PsithonParser.Psithon_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_psithon_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 531
            self.native_expression()
            self.state = 533
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.state = 532
                self.match(PsithonParser.NEWLINE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Molecule_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_MOLECULE(self):
            return self.getToken(PsithonParser.PSI_MOLECULE, 0)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def molecule_body(self):
            return self.getTypedRuleContext(PsithonParser.Molecule_bodyContext,0)


        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def header_space(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Header_spaceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Header_spaceContext,i)


        def molecule_name(self):
            return self.getTypedRuleContext(PsithonParser.Molecule_nameContext,0)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_molecule_block




    def molecule_block(self):

        localctx = PsithonParser.Molecule_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_molecule_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 535
            self.match(PsithonParser.PSI_MOLECULE)
            self.state = 539
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 536
                    self.header_space() 
                self.state = 541
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

            self.state = 543
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.state = 542
                self.molecule_name()


            self.state = 548
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117:
                self.state = 545
                self.match(PsithonParser.D_NEWLINE)
                self.state = 550
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 551
            self.match(PsithonParser.D_LBRACE)
            self.state = 552
            self.molecule_body()
            self.state = 553
            self.match(PsithonParser.D_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Molecule_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_molecule_name




    def molecule_name(self):

        localctx = PsithonParser.Molecule_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_molecule_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 555
            if not self._input.LT(1).text.isidentifier():
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "self._input.LT(1).text.isidentifier()")
            self.state = 556
            self.native_word()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Molecule_bodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def molecule_line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Molecule_lineContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Molecule_lineContext,i)


        def xyz_header(self):
            return self.getTypedRuleContext(PsithonParser.Xyz_headerContext,0)


        def literal_line(self):
            return self.getTypedRuleContext(PsithonParser.Literal_lineContext,0)


        def atom_line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Atom_lineContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Atom_lineContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_molecule_body




    def molecule_body(self):

        localctx = PsithonParser.Molecule_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_molecule_body)
        self._la = 0 # Token type
        try:
            self.state = 602
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 561
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==117:
                    self.state = 558
                    self.match(PsithonParser.D_NEWLINE)
                    self.state = 563
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 572
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,8,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 564
                        self.molecule_line()
                        self.state = 566 
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        while True:
                            self.state = 565
                            self.match(PsithonParser.D_NEWLINE)
                            self.state = 568 
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)
                            if not (_la==117):
                                break
                 
                    self.state = 574
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

                self.state = 576
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 524233) != 0):
                    self.state = 575
                    self.molecule_line()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 581
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==117:
                    self.state = 578
                    self.match(PsithonParser.D_NEWLINE)
                    self.state = 583
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 584
                self.xyz_header()
                self.state = 585
                self.match(PsithonParser.D_NEWLINE)
                self.state = 587
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -45106365017882625) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0):
                    self.state = 586
                    self.literal_line()


                self.state = 589
                self.match(PsithonParser.D_NEWLINE)
                self.state = 596
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 594
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [117]:
                            self.state = 590
                            self.match(PsithonParser.D_NEWLINE)
                            pass
                        elif token in [128, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146]:
                            self.state = 591
                            self.atom_line()
                            self.state = 592
                            self.match(PsithonParser.D_NEWLINE)
                            pass
                        else:
                            raise NoViableAltException(self)
                 
                    self.state = 598
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                self.state = 600
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 524161) != 0):
                    self.state = 599
                    self.atom_line()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Molecule_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_UNITS(self):
            return self.getToken(PsithonParser.D_UNITS, 0)

        def unit_name(self):
            return self.getTypedRuleContext(PsithonParser.Unit_nameContext,0)


        def D_EQUALS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_EQUALS)
            else:
                return self.getToken(PsithonParser.D_EQUALS, i)

        def D_SYMMETRY(self):
            return self.getToken(PsithonParser.D_SYMMETRY, 0)

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_NO_COM(self):
            return self.getToken(PsithonParser.D_NO_COM, 0)

        def D_NO_REORIENT(self):
            return self.getToken(PsithonParser.D_NO_REORIENT, 0)

        def D_SEPARATOR(self):
            return self.getToken(PsithonParser.D_SEPARATOR, 0)

        def D_PUBCHEM(self):
            return self.getToken(PsithonParser.D_PUBCHEM, 0)

        def D_COLON(self):
            return self.getToken(PsithonParser.D_COLON, 0)

        def literal_line(self):
            return self.getTypedRuleContext(PsithonParser.Literal_lineContext,0)


        def D_FROM_FILE(self):
            return self.getToken(PsithonParser.D_FROM_FILE, 0)

        def efp_fragment(self):
            return self.getTypedRuleContext(PsithonParser.Efp_fragmentContext,0)


        def charge_multiplicity(self):
            return self.getTypedRuleContext(PsithonParser.Charge_multiplicityContext,0)


        def geometry_variable(self):
            return self.getTypedRuleContext(PsithonParser.Geometry_variableContext,0)


        def atom_line(self):
            return self.getTypedRuleContext(PsithonParser.Atom_lineContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_molecule_line




    def molecule_line(self):

        localctx = PsithonParser.Molecule_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_molecule_line)
        self._la = 0 # Token type
        try:
            self.state = 633
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 604
                self.match(PsithonParser.D_UNITS)
                self.state = 608
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==124:
                    self.state = 605
                    self.match(PsithonParser.D_EQUALS)
                    self.state = 610
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 611
                self.unit_name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 612
                self.match(PsithonParser.D_SYMMETRY)
                self.state = 616
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==124:
                    self.state = 613
                    self.match(PsithonParser.D_EQUALS)
                    self.state = 618
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 619
                self.native_word()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 620
                self.match(PsithonParser.D_NO_COM)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 621
                self.match(PsithonParser.D_NO_REORIENT)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 622
                self.match(PsithonParser.D_SEPARATOR)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 623
                self.match(PsithonParser.D_PUBCHEM)
                self.state = 624
                self.match(PsithonParser.D_COLON)
                self.state = 625
                self.literal_line()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 626
                self.match(PsithonParser.D_FROM_FILE)
                self.state = 627
                self.match(PsithonParser.D_COLON)
                self.state = 628
                self.literal_line()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 629
                self.efp_fragment()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 630
                self.charge_multiplicity()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 631
                self.geometry_variable()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 632
                self.atom_line()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Xyz_headerContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_xyz_header




    def xyz_header(self):

        localctx = PsithonParser.Xyz_headerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_xyz_header)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 635
            self.match(PsithonParser.D_NUMBER)
            self.state = 637
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & 3583) != 0):
                self.state = 636
                self.native_word()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Charge_multiplicityContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NUMBER)
            else:
                return self.getToken(PsithonParser.D_NUMBER, i)

        def D_COMMA(self):
            return self.getToken(PsithonParser.D_COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_charge_multiplicity




    def charge_multiplicity(self):

        localctx = PsithonParser.Charge_multiplicityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_charge_multiplicity)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 639
            self.match(PsithonParser.D_NUMBER)
            self.state = 641
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==125:
                self.state = 640
                self.match(PsithonParser.D_COMMA)


            self.state = 643
            self.match(PsithonParser.D_NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Geometry_variableContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Native_wordContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Native_wordContext,i)


        def D_EQUALS(self):
            return self.getToken(PsithonParser.D_EQUALS, 0)

        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def D_MINUS(self):
            return self.getToken(PsithonParser.D_MINUS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_geometry_variable




    def geometry_variable(self):

        localctx = PsithonParser.Geometry_variableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_geometry_variable)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 646
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==131:
                self.state = 645
                self.match(PsithonParser.D_MINUS)


            self.state = 648
            self.native_word()
            self.state = 649
            self.match(PsithonParser.D_EQUALS)
            self.state = 652
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [144]:
                self.state = 650
                self.match(PsithonParser.D_NUMBER)
                pass
            elif token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                self.state = 651
                self.native_word()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Unit_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Native_wordContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Native_wordContext,i)


        def D_DOT(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_DOT)
            else:
                return self.getToken(PsithonParser.D_DOT, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_unit_name




    def unit_name(self):

        localctx = PsithonParser.Unit_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_unit_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 654
            self.native_word()
            self.state = 659
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==133:
                self.state = 655
                self.match(PsithonParser.D_DOT)
                self.state = 656
                self.native_word()
                self.state = 657
                self.match(PsithonParser.D_DOT)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Atom_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nucleus(self):
            return self.getTypedRuleContext(PsithonParser.NucleusContext,0)


        def coordinate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.CoordinateContext)
            else:
                return self.getTypedRuleContext(PsithonParser.CoordinateContext,i)


        def anchor_pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Anchor_pairContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Anchor_pairContext,i)


        def D_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_COMMA)
            else:
                return self.getToken(PsithonParser.D_COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_atom_line




    def atom_line(self):

        localctx = PsithonParser.Atom_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_atom_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 661
            self.nucleus()
            self.state = 682
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.state = 663
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==125:
                    self.state = 662
                    self.match(PsithonParser.D_COMMA)


                self.state = 665
                self.coordinate()
                self.state = 667
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==125:
                    self.state = 666
                    self.match(PsithonParser.D_COMMA)


                self.state = 669
                self.coordinate()
                self.state = 671
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==125:
                    self.state = 670
                    self.match(PsithonParser.D_COMMA)


                self.state = 673
                self.coordinate()

            elif la_ == 2:
                self.state = 675
                self.anchor_pair()
                self.state = 680
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 125)) & ~0x3f) == 0 and ((1 << (_la - 125)) & 4193281) != 0):
                    self.state = 676
                    self.anchor_pair()
                    self.state = 678
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if ((((_la - 125)) & ~0x3f) == 0 and ((1 << (_la - 125)) & 4193281) != 0):
                        self.state = 677
                        self.anchor_pair()






        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NucleusContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nucleus_label(self):
            return self.getTypedRuleContext(PsithonParser.Nucleus_labelContext,0)


        def D_AT(self):
            return self.getToken(PsithonParser.D_AT, 0)

        def isotope_mass(self):
            return self.getTypedRuleContext(PsithonParser.Isotope_massContext,0)


        def D_GHOST(self):
            return self.getToken(PsithonParser.D_GHOST, 0)

        def D_LPAREN(self):
            return self.getToken(PsithonParser.D_LPAREN, 0)

        def D_RPAREN(self):
            return self.getToken(PsithonParser.D_RPAREN, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_nucleus




    def nucleus(self):

        localctx = PsithonParser.NucleusContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_nucleus)
        self._la = 0 # Token type
        try:
            self.state = 699
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 685
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==128:
                    self.state = 684
                    self.match(PsithonParser.D_AT)


                self.state = 687
                self.nucleus_label()
                self.state = 689
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==128:
                    self.state = 688
                    self.isotope_mass()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 691
                self.match(PsithonParser.D_GHOST)
                self.state = 692
                self.match(PsithonParser.D_LPAREN)
                self.state = 693
                self.nucleus_label()
                self.state = 695
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==128:
                    self.state = 694
                    self.isotope_mass()


                self.state = 697
                self.match(PsithonParser.D_RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Nucleus_labelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_nucleus_label




    def nucleus_label(self):

        localctx = PsithonParser.Nucleus_labelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_nucleus_label)
        self._la = 0 # Token type
        try:
            self.state = 706
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,35,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 702
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==144:
                    self.state = 701
                    self.match(PsithonParser.D_NUMBER)


                self.state = 704
                self.native_word()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 705
                self.match(PsithonParser.D_NUMBER)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Isotope_massContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_AT(self):
            return self.getToken(PsithonParser.D_AT, 0)

        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_isotope_mass




    def isotope_mass(self):

        localctx = PsithonParser.Isotope_massContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_isotope_mass)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 708
            self.match(PsithonParser.D_AT)
            self.state = 709
            self.match(PsithonParser.D_NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CoordinateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_MINUS(self):
            return self.getToken(PsithonParser.D_MINUS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_coordinate




    def coordinate(self):

        localctx = PsithonParser.CoordinateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_coordinate)
        self._la = 0 # Token type
        try:
            self.state = 716
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [144]:
                self.enterOuterAlt(localctx, 1)
                self.state = 711
                self.match(PsithonParser.D_NUMBER)
                pass
            elif token in [131, 135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                self.enterOuterAlt(localctx, 2)
                self.state = 713
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==131:
                    self.state = 712
                    self.match(PsithonParser.D_MINUS)


                self.state = 715
                self.native_word()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Anchor_pairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def coordinate(self):
            return self.getTypedRuleContext(PsithonParser.CoordinateContext,0)


        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_COMMA)
            else:
                return self.getToken(PsithonParser.D_COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_anchor_pair




    def anchor_pair(self):

        localctx = PsithonParser.Anchor_pairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_anchor_pair)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 719
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==125:
                self.state = 718
                self.match(PsithonParser.D_COMMA)


            self.state = 723
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [144]:
                self.state = 721
                self.match(PsithonParser.D_NUMBER)
                pass
            elif token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                self.state = 722
                self.native_word()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 726
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==125:
                self.state = 725
                self.match(PsithonParser.D_COMMA)


            self.state = 728
            self.coordinate()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Efp_fragmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_EFP(self):
            return self.getToken(PsithonParser.D_EFP, 0)

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def numeric_xyz(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Numeric_xyzContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Numeric_xyzContext,i)


        def D_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_COMMA)
            else:
                return self.getToken(PsithonParser.D_COMMA, i)

        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_efp_fragment




    def efp_fragment(self):

        localctx = PsithonParser.Efp_fragmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_efp_fragment)
        self._la = 0 # Token type
        try:
            self.state = 756
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,43,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 730
                self.match(PsithonParser.D_EFP)
                self.state = 731
                self.native_word()
                self.state = 735
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==125:
                    self.state = 732
                    self.match(PsithonParser.D_COMMA)
                    self.state = 737
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 738
                self.numeric_xyz()
                self.state = 742
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==125:
                    self.state = 739
                    self.match(PsithonParser.D_COMMA)
                    self.state = 744
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 745
                self.numeric_xyz()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 747
                self.match(PsithonParser.D_EFP)
                self.state = 748
                self.native_word()
                self.state = 749
                self.match(PsithonParser.D_NEWLINE)
                self.state = 750
                self.numeric_xyz()
                self.state = 751
                self.match(PsithonParser.D_NEWLINE)
                self.state = 752
                self.numeric_xyz()
                self.state = 753
                self.match(PsithonParser.D_NEWLINE)
                self.state = 754
                self.numeric_xyz()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Numeric_xyzContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NUMBER)
            else:
                return self.getToken(PsithonParser.D_NUMBER, i)

        def D_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_COMMA)
            else:
                return self.getToken(PsithonParser.D_COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_numeric_xyz




    def numeric_xyz(self):

        localctx = PsithonParser.Numeric_xyzContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_numeric_xyz)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 758
            self.match(PsithonParser.D_NUMBER)
            self.state = 762
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==125:
                self.state = 759
                self.match(PsithonParser.D_COMMA)
                self.state = 764
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 765
            self.match(PsithonParser.D_NUMBER)
            self.state = 769
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==125:
                self.state = 766
                self.match(PsithonParser.D_COMMA)
                self.state = 771
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 772
            self.match(PsithonParser.D_NUMBER)
            self.state = 776
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,46,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 773
                    self.match(PsithonParser.D_COMMA) 
                self.state = 778
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,46,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Set_commandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_SET(self):
            return self.getToken(PsithonParser.PSI_SET, 0)

        def option_key(self):
            return self.getTypedRuleContext(PsithonParser.Option_keyContext,0)


        def inline_option_value(self):
            return self.getTypedRuleContext(PsithonParser.Inline_option_valueContext,0)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def module_list(self):
            return self.getTypedRuleContext(PsithonParser.Module_listContext,0)


        def D_EQUALS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_EQUALS)
            else:
                return self.getToken(PsithonParser.D_EQUALS, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_set_command




    def set_command(self):

        localctx = PsithonParser.Set_commandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_set_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 779
            self.match(PsithonParser.PSI_SET)
            self.state = 783
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,47,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 780
                    self.match(PsithonParser.D_NEWLINE) 
                self.state = 785
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,47,self._ctx)

            self.state = 788
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,48,self._ctx)
            if la_ == 1:
                self.state = 786
                if not self.psithon_inline_module(localctx):
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, "self.psithon_inline_module($ctx)")
                self.state = 787
                self.module_list()


            self.state = 790
            self.option_key()
            self.state = 794
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==124:
                self.state = 791
                self.match(PsithonParser.D_EQUALS)
                self.state = 796
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 797
            self.inline_option_value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Set_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_SET(self):
            return self.getToken(PsithonParser.PSI_SET, 0)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def module_list(self):
            return self.getTypedRuleContext(PsithonParser.Module_listContext,0)


        def header_space(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Header_spaceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Header_spaceContext,i)


        def option_assignment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Option_assignmentContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Option_assignmentContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_set_block




    def set_block(self):

        localctx = PsithonParser.Set_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_set_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 799
            self.match(PsithonParser.PSI_SET)
            self.state = 803
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,50,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 800
                    self.match(PsithonParser.D_NEWLINE) 
                self.state = 805
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,50,self._ctx)

            self.state = 807
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 125)) & ~0x3f) == 0 and ((1 << (_la - 125)) & 4193857) != 0):
                self.state = 806
                self.module_list()


            self.state = 812
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117 or _la==124:
                self.state = 809
                self.header_space()
                self.state = 814
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 815
            self.match(PsithonParser.D_LBRACE)
            self.state = 819
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,53,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 816
                    self.match(PsithonParser.D_NEWLINE) 
                self.state = 821
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,53,self._ctx)

            self.state = 830
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,55,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 822
                    self.option_assignment()
                    self.state = 824 
                    self._errHandler.sync(self)
                    _alt = 1
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt == 1:
                            self.state = 823
                            self.match(PsithonParser.D_NEWLINE)

                        else:
                            raise NoViableAltException(self)
                        self.state = 826 
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,54,self._ctx)
             
                self.state = 832
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,55,self._ctx)

            self.state = 834
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,56,self._ctx)
            if la_ == 1:
                self.state = 833
                self.option_assignment()


            self.state = 836
            self.match(PsithonParser.D_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Module_listContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def module_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Module_nameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Module_nameContext,i)


        def D_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_COMMA)
            else:
                return self.getToken(PsithonParser.D_COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_module_list




    def module_list(self):

        localctx = PsithonParser.Module_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_module_list)
        self._la = 0 # Token type
        try:
            self.state = 850
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,60,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 838
                self.module_name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 840
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((((_la - 131)) & ~0x3f) == 0 and ((1 << (_la - 131)) & 65529) != 0):
                    self.state = 839
                    self.module_name()


                self.state = 846 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 842
                        self.match(PsithonParser.D_COMMA)
                        self.state = 844
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,58,self._ctx)
                        if la_ == 1:
                            self.state = 843
                            self.module_name()



                    else:
                        raise NoViableAltException(self)
                    self.state = 848 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,59,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Module_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def module_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Module_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Module_pieceContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_module_name




    def module_name(self):

        localctx = PsithonParser.Module_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_module_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 852
            self.module_piece()
            self.state = 857
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,61,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 853
                    if not self.psithon_contiguous(localctx):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.psithon_contiguous($ctx)")
                    self.state = 854
                    self.module_piece() 
                self.state = 859
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,61,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Module_pieceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def D_MINUS(self):
            return self.getToken(PsithonParser.D_MINUS, 0)

        def D_SEPARATOR(self):
            return self.getToken(PsithonParser.D_SEPARATOR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_module_piece




    def module_piece(self):

        localctx = PsithonParser.Module_pieceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_module_piece)
        try:
            self.state = 864
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                self.enterOuterAlt(localctx, 1)
                self.state = 860
                self.native_word()
                pass
            elif token in [144]:
                self.enterOuterAlt(localctx, 2)
                self.state = 861
                self.match(PsithonParser.D_NUMBER)
                pass
            elif token in [131]:
                self.enterOuterAlt(localctx, 3)
                self.state = 862
                self.match(PsithonParser.D_MINUS)
                pass
            elif token in [134]:
                self.enterOuterAlt(localctx, 4)
                self.state = 863
                self.match(PsithonParser.D_SEPARATOR)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Option_keyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_identifier(self):
            return self.getTypedRuleContext(PsithonParser.Native_identifierContext,0)


        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_option_key




    def option_key(self):

        localctx = PsithonParser.Option_keyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_option_key)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 866
            if not all(c.isalnum() or c == "_" for c in self._input.LT(1).text):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "all(c.isalnum() or c == \"_\" for c in self._input.LT(1).text)")
            self.state = 869
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145]:
                self.state = 867
                self.native_identifier()
                pass
            elif token in [144]:
                self.state = 868
                self.match(PsithonParser.D_NUMBER)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Option_assignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def option_key(self):
            return self.getTypedRuleContext(PsithonParser.Option_keyContext,0)


        def set_option_value(self):
            return self.getTypedRuleContext(PsithonParser.Set_option_valueContext,0)


        def D_EQUALS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_EQUALS)
            else:
                return self.getToken(PsithonParser.D_EQUALS, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_option_assignment




    def option_assignment(self):

        localctx = PsithonParser.Option_assignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_option_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 871
            self.option_key()
            self.state = 875
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,64,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 872
                    self.match(PsithonParser.D_EQUALS) 
                self.state = 877
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,64,self._ctx)

            self.state = 878
            self.set_option_value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Inline_option_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def set_option_array(self):
            return self.getTypedRuleContext(PsithonParser.Set_option_arrayContext,0)


        def inline_option_scalar(self):
            return self.getTypedRuleContext(PsithonParser.Inline_option_scalarContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_inline_option_value




    def inline_option_value(self):

        localctx = PsithonParser.Inline_option_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_inline_option_value)
        try:
            self.state = 882
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [120]:
                self.enterOuterAlt(localctx, 1)
                self.state = 880
                self.set_option_array()
                pass
            elif token in [122, 123, 125, 126, 127, 129, 130, 131, 133, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146]:
                self.enterOuterAlt(localctx, 2)
                self.state = 881
                self.inline_option_scalar()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Set_option_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def set_option_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Set_option_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Set_option_pieceContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_set_option_value




    def set_option_value(self):

        localctx = PsithonParser.Set_option_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_set_option_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 885 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 884
                self.set_option_piece()
                self.state = 887 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -765682305397161985) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Set_option_arrayContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_LBRACKET(self):
            return self.getToken(PsithonParser.D_LBRACKET, 0)

        def D_RBRACKET(self):
            return self.getToken(PsithonParser.D_RBRACKET, 0)

        def set_option_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Set_option_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Set_option_pieceContext,i)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_set_option_array




    def set_option_array(self):

        localctx = PsithonParser.Set_option_arrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_set_option_array)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 889
            self.match(PsithonParser.D_LBRACKET)
            self.state = 894
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -756675106142420993) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0):
                self.state = 892
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 118, 120, 122, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]:
                    self.state = 890
                    self.set_option_piece()
                    pass
                elif token in [117]:
                    self.state = 891
                    self.match(PsithonParser.D_NEWLINE)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 896
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 897
            self.match(PsithonParser.D_RBRACKET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Set_option_pieceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def set_option_array(self):
            return self.getTypedRuleContext(PsithonParser.Set_option_arrayContext,0)


        def D_LPAREN(self):
            return self.getToken(PsithonParser.D_LPAREN, 0)

        def D_RPAREN(self):
            return self.getToken(PsithonParser.D_RPAREN, 0)

        def set_option_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Set_option_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Set_option_pieceContext,i)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def D_LBRACKET(self):
            return self.getToken(PsithonParser.D_LBRACKET, 0)

        def D_RBRACKET(self):
            return self.getToken(PsithonParser.D_RBRACKET, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_set_option_piece




    def set_option_piece(self):

        localctx = PsithonParser.Set_option_pieceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_set_option_piece)
        self._la = 0 # Token type
        try:
            self.state = 919
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [120]:
                self.enterOuterAlt(localctx, 1)
                self.state = 899
                self.set_option_array()
                pass
            elif token in [122]:
                self.enterOuterAlt(localctx, 2)
                self.state = 900
                self.match(PsithonParser.D_LPAREN)
                self.state = 905
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -756675106142420993) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0):
                    self.state = 903
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 118, 120, 122, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]:
                        self.state = 901
                        self.set_option_piece()
                        pass
                    elif token in [117]:
                        self.state = 902
                        self.match(PsithonParser.D_NEWLINE)
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 907
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 908
                self.match(PsithonParser.D_RPAREN)
                pass
            elif token in [118]:
                self.enterOuterAlt(localctx, 3)
                self.state = 909
                self.match(PsithonParser.D_LBRACE)
                self.state = 914
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -756675106142420993) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0):
                    self.state = 912
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 118, 120, 122, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]:
                        self.state = 910
                        self.set_option_piece()
                        pass
                    elif token in [117]:
                        self.state = 911
                        self.match(PsithonParser.D_NEWLINE)
                        pass
                    else:
                        raise NoViableAltException(self)

                    self.state = 916
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 917
                self.match(PsithonParser.D_RBRACE)
                pass
            elif token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]:
                self.enterOuterAlt(localctx, 4)
                self.state = 918
                _la = self._input.LA(1)
                if _la <= 0 or ((((_la - 110)) & ~0x3f) == 0 and ((1 << (_la - 110)) & 16257) != 0):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Inline_option_scalarContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def option_reference(self):
            return self.getTypedRuleContext(PsithonParser.Option_referenceContext,0)


        def inline_option_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Inline_option_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Inline_option_pieceContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_inline_option_scalar




    def inline_option_scalar(self):

        localctx = PsithonParser.Inline_option_scalarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_inline_option_scalar)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 923
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [127]:
                self.state = 921
                self.option_reference()
                pass
            elif token in [122, 123, 125, 126, 129, 130, 131, 133, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146]:
                self.state = 922
                self.inline_option_piece()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 929
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,75,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 925
                    if not self.psithon_contiguous(localctx):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.psithon_contiguous($ctx)")
                    self.state = 926
                    self.inline_option_piece() 
                self.state = 931
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,75,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Inline_option_pieceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def D_MINUS(self):
            return self.getToken(PsithonParser.D_MINUS, 0)

        def D_PLUS(self):
            return self.getToken(PsithonParser.D_PLUS, 0)

        def D_COMMA(self):
            return self.getToken(PsithonParser.D_COMMA, 0)

        def D_STAR(self):
            return self.getToken(PsithonParser.D_STAR, 0)

        def D_COLON(self):
            return self.getToken(PsithonParser.D_COLON, 0)

        def D_LPAREN(self):
            return self.getToken(PsithonParser.D_LPAREN, 0)

        def D_RPAREN(self):
            return self.getToken(PsithonParser.D_RPAREN, 0)

        def D_DOT(self):
            return self.getToken(PsithonParser.D_DOT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_inline_option_piece




    def inline_option_piece(self):

        localctx = PsithonParser.Inline_option_pieceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_inline_option_piece)
        try:
            self.state = 942
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                self.enterOuterAlt(localctx, 1)
                self.state = 932
                self.native_word()
                pass
            elif token in [144]:
                self.enterOuterAlt(localctx, 2)
                self.state = 933
                self.match(PsithonParser.D_NUMBER)
                pass
            elif token in [131]:
                self.enterOuterAlt(localctx, 3)
                self.state = 934
                self.match(PsithonParser.D_MINUS)
                pass
            elif token in [130]:
                self.enterOuterAlt(localctx, 4)
                self.state = 935
                self.match(PsithonParser.D_PLUS)
                pass
            elif token in [125]:
                self.enterOuterAlt(localctx, 5)
                self.state = 936
                self.match(PsithonParser.D_COMMA)
                pass
            elif token in [129]:
                self.enterOuterAlt(localctx, 6)
                self.state = 937
                self.match(PsithonParser.D_STAR)
                pass
            elif token in [126]:
                self.enterOuterAlt(localctx, 7)
                self.state = 938
                self.match(PsithonParser.D_COLON)
                pass
            elif token in [122]:
                self.enterOuterAlt(localctx, 8)
                self.state = 939
                self.match(PsithonParser.D_LPAREN)
                pass
            elif token in [123]:
                self.enterOuterAlt(localctx, 9)
                self.state = 940
                self.match(PsithonParser.D_RPAREN)
                pass
            elif token in [133]:
                self.enterOuterAlt(localctx, 10)
                self.state = 941
                self.match(PsithonParser.D_DOT)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Option_referenceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_DOLLAR(self):
            return self.getToken(PsithonParser.D_DOLLAR, 0)

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_option_reference




    def option_reference(self):

        localctx = PsithonParser.Option_referenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_option_reference)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 944
            self.match(PsithonParser.D_DOLLAR)
            self.state = 945
            if not (self._input.LT(-1).stop + 1 == self._input.LT(1).start
                    and self._input.LT(1).text[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self._input.LT(-1).stop + 1 == self._input.LT(1).start\n        and self._input.LT(1).text[0] in \"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\")")
            self.state = 946
            self.native_word()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Memory_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_MEMORY(self):
            return self.getToken(PsithonParser.PSI_MEMORY, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_memory_line




    def memory_line(self):

        localctx = PsithonParser.Memory_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_memory_line)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 948
            self.match(PsithonParser.PSI_MEMORY)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basis_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_BASIS(self):
            return self.getToken(PsithonParser.PSI_BASIS, 0)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def header_space(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Header_spaceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Header_spaceContext,i)


        def header_label(self):
            return self.getTypedRuleContext(PsithonParser.Header_labelContext,0)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def basis_line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Basis_lineContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Basis_lineContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_basis_block




    def basis_block(self):

        localctx = PsithonParser.Basis_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_basis_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 950
            self.match(PsithonParser.PSI_BASIS)
            self.state = 954
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,77,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 951
                    self.header_space() 
                self.state = 956
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,77,self._ctx)

            self.state = 958
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & 4095) != 0):
                self.state = 957
                self.header_label()


            self.state = 963
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117:
                self.state = 960
                self.match(PsithonParser.D_NEWLINE)
                self.state = 965
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 966
            self.match(PsithonParser.D_LBRACE)
            self.state = 970
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117:
                self.state = 967
                self.match(PsithonParser.D_NEWLINE)
                self.state = 972
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 981
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,82,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 973
                    self.basis_line()
                    self.state = 975 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while True:
                        self.state = 974
                        self.match(PsithonParser.D_NEWLINE)
                        self.state = 977 
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if not (_la==117):
                            break
             
                self.state = 983
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,82,self._ctx)

            self.state = 985
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -45106365017882625) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0):
                self.state = 984
                self.basis_line()


            self.state = 987
            self.match(PsithonParser.D_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basis_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def basis_assignment(self):
            return self.getTypedRuleContext(PsithonParser.Basis_assignmentContext,0)


        def basis_label(self):
            return self.getTypedRuleContext(PsithonParser.Basis_labelContext,0)


        def basis_record(self):
            return self.getTypedRuleContext(PsithonParser.Basis_recordContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_basis_line




    def basis_line(self):

        localctx = PsithonParser.Basis_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_basis_line)
        try:
            self.state = 992
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,84,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 989
                self.basis_assignment()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 990
                self.basis_label()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 991
                self.basis_record()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basis_assignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_ASSIGN(self):
            return self.getToken(PsithonParser.D_ASSIGN, 0)

        def basis_name(self):
            return self.getTypedRuleContext(PsithonParser.Basis_nameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_basis_assignment




    def basis_assignment(self):

        localctx = PsithonParser.Basis_assignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_basis_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 994
            self.match(PsithonParser.D_ASSIGN)
            self.state = 995
            self.basis_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basis_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Native_wordContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Native_wordContext,i)


        def D_NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NUMBER)
            else:
                return self.getToken(PsithonParser.D_NUMBER, i)

        def D_MINUS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_MINUS)
            else:
                return self.getToken(PsithonParser.D_MINUS, i)

        def D_PLUS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_PLUS)
            else:
                return self.getToken(PsithonParser.D_PLUS, i)

        def D_STAR(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_STAR)
            else:
                return self.getToken(PsithonParser.D_STAR, i)

        def D_LPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_LPAREN)
            else:
                return self.getToken(PsithonParser.D_LPAREN, i)

        def D_RPAREN(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_RPAREN)
            else:
                return self.getToken(PsithonParser.D_RPAREN, i)

        def D_COLON(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_COLON)
            else:
                return self.getToken(PsithonParser.D_COLON, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_basis_name




    def basis_name(self):

        localctx = PsithonParser.Basis_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_basis_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1005 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1005
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                    self.state = 997
                    self.native_word()
                    pass
                elif token in [144]:
                    self.state = 998
                    self.match(PsithonParser.D_NUMBER)
                    pass
                elif token in [131]:
                    self.state = 999
                    self.match(PsithonParser.D_MINUS)
                    pass
                elif token in [130]:
                    self.state = 1000
                    self.match(PsithonParser.D_PLUS)
                    pass
                elif token in [129]:
                    self.state = 1001
                    self.match(PsithonParser.D_STAR)
                    pass
                elif token in [122]:
                    self.state = 1002
                    self.match(PsithonParser.D_LPAREN)
                    pass
                elif token in [123]:
                    self.state = 1003
                    self.match(PsithonParser.D_RPAREN)
                    pass
                elif token in [126]:
                    self.state = 1004
                    self.match(PsithonParser.D_COLON)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 1007 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (((((_la - 122)) & ~0x3f) == 0 and ((1 << (_la - 122)) & 33547155) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basis_labelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_LBRACKET(self):
            return self.getToken(PsithonParser.D_LBRACKET, 0)

        def basis_name(self):
            return self.getTypedRuleContext(PsithonParser.Basis_nameContext,0)


        def D_RBRACKET(self):
            return self.getToken(PsithonParser.D_RBRACKET, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_basis_label




    def basis_label(self):

        localctx = PsithonParser.Basis_labelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_basis_label)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1009
            self.match(PsithonParser.D_LBRACKET)
            self.state = 1010
            self.basis_name()
            self.state = 1011
            self.match(PsithonParser.D_RBRACKET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basis_recordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Literal_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Literal_pieceContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_basis_record




    def basis_record(self):

        localctx = PsithonParser.Basis_recordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_basis_record)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1014 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1013
                self.literal_piece()
                self.state = 1016 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -45106365017882625) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class External_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_EXTERNAL(self):
            return self.getToken(PsithonParser.PSI_EXTERNAL, 0)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def header_space(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Header_spaceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Header_spaceContext,i)


        def header_label(self):
            return self.getTypedRuleContext(PsithonParser.Header_labelContext,0)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def external_line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.External_lineContext)
            else:
                return self.getTypedRuleContext(PsithonParser.External_lineContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_external_block




    def external_block(self):

        localctx = PsithonParser.External_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_external_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1018
            self.match(PsithonParser.PSI_EXTERNAL)
            self.state = 1022
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,88,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1019
                    self.header_space() 
                self.state = 1024
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,88,self._ctx)

            self.state = 1026
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & 4095) != 0):
                self.state = 1025
                self.header_label()


            self.state = 1031
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117:
                self.state = 1028
                self.match(PsithonParser.D_NEWLINE)
                self.state = 1033
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 1034
            self.match(PsithonParser.D_LBRACE)
            self.state = 1038
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,91,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1035
                    self.match(PsithonParser.D_NEWLINE) 
                self.state = 1040
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,91,self._ctx)

            self.state = 1049
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,93,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1041
                    self.external_line()
                    self.state = 1043 
                    self._errHandler.sync(self)
                    _alt = 1
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt == 1:
                            self.state = 1042
                            self.match(PsithonParser.D_NEWLINE)

                        else:
                            raise NoViableAltException(self)
                        self.state = 1045 
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,92,self._ctx)
             
                self.state = 1051
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,93,self._ctx)

            self.state = 1053
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,94,self._ctx)
            if la_ == 1:
                self.state = 1052
                self.external_line()


            self.state = 1055
            self.match(PsithonParser.D_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class External_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_UNITS(self):
            return self.getToken(PsithonParser.D_UNITS, 0)

        def unit_name(self):
            return self.getTypedRuleContext(PsithonParser.Unit_nameContext,0)


        def D_EQUALS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_EQUALS)
            else:
                return self.getToken(PsithonParser.D_EQUALS, i)

        def external_basis_line(self):
            return self.getTypedRuleContext(PsithonParser.External_basis_lineContext,0)


        def D_NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NUMBER)
            else:
                return self.getToken(PsithonParser.D_NUMBER, i)

        def nucleus(self):
            return self.getTypedRuleContext(PsithonParser.NucleusContext,0)


        def D_SEPARATOR(self):
            return self.getToken(PsithonParser.D_SEPARATOR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_external_line




    def external_line(self):

        localctx = PsithonParser.External_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_external_line)
        self._la = 0 # Token type
        try:
            self.state = 1076
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,96,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1057
                self.match(PsithonParser.D_UNITS)
                self.state = 1061
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==124:
                    self.state = 1058
                    self.match(PsithonParser.D_EQUALS)
                    self.state = 1063
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1064
                self.unit_name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1065
                self.external_basis_line()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1066
                self.match(PsithonParser.D_NUMBER)
                self.state = 1067
                self.match(PsithonParser.D_NUMBER)
                self.state = 1068
                self.match(PsithonParser.D_NUMBER)
                self.state = 1069
                self.match(PsithonParser.D_NUMBER)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1070
                self.nucleus()
                self.state = 1071
                self.match(PsithonParser.D_NUMBER)
                self.state = 1072
                self.match(PsithonParser.D_NUMBER)
                self.state = 1073
                self.match(PsithonParser.D_NUMBER)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 1075
                self.match(PsithonParser.D_SEPARATOR)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class External_basis_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def external_basis_key(self):
            return self.getTypedRuleContext(PsithonParser.External_basis_keyContext,0)


        def D_EQUALS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_EQUALS)
            else:
                return self.getToken(PsithonParser.D_EQUALS, i)

        def literal_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Literal_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Literal_pieceContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_external_basis_line




    def external_basis_line(self):

        localctx = PsithonParser.External_basis_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_external_basis_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1078
            self.external_basis_key()
            self.state = 1082
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,97,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1079
                    self.match(PsithonParser.D_EQUALS) 
                self.state = 1084
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,97,self._ctx)

            self.state = 1086 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1085
                self.literal_piece()
                self.state = 1088 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -45106365017882625) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class External_basis_keyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_external_basis_key




    def external_basis_key(self):

        localctx = PsithonParser.External_basis_keyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_external_basis_key)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1090
            if not self._input.LT(1).text.casefold() in {"basis", "df_basis_scf"}:
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "self._input.LT(1).text.casefold() in {\"basis\", \"df_basis_scf\"}")
            self.state = 1091
            self.native_word()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pcm_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_PCM(self):
            return self.getToken(PsithonParser.PSI_PCM, 0)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def pcm_body(self):
            return self.getTypedRuleContext(PsithonParser.Pcm_bodyContext,0)


        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def header_space(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Header_spaceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Header_spaceContext,i)


        def header_label(self):
            return self.getTypedRuleContext(PsithonParser.Header_labelContext,0)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_pcm_block




    def pcm_block(self):

        localctx = PsithonParser.Pcm_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_pcm_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1093
            self.match(PsithonParser.PSI_PCM)
            self.state = 1097
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,99,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1094
                    self.header_space() 
                self.state = 1099
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,99,self._ctx)

            self.state = 1101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & 4095) != 0):
                self.state = 1100
                self.header_label()


            self.state = 1106
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117:
                self.state = 1103
                self.match(PsithonParser.D_NEWLINE)
                self.state = 1108
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 1109
            self.match(PsithonParser.D_LBRACE)
            self.state = 1110
            self.pcm_body()
            self.state = 1111
            self.match(PsithonParser.D_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pcm_bodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_LBRACE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_LBRACE)
            else:
                return self.getToken(PsithonParser.D_LBRACE, i)

        def pcm_body(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Pcm_bodyContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Pcm_bodyContext,i)


        def D_RBRACE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_RBRACE)
            else:
                return self.getToken(PsithonParser.D_RBRACE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_pcm_body




    def pcm_body(self):

        localctx = PsithonParser.Pcm_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_pcm_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1120
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -36028797018963969) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0):
                self.state = 1118
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [118]:
                    self.state = 1113
                    self.match(PsithonParser.D_LBRACE)
                    self.state = 1114
                    self.pcm_body()
                    self.state = 1115
                    self.match(PsithonParser.D_RBRACE)
                    pass
                elif token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151]:
                    self.state = 1117
                    _la = self._input.LA(1)
                    if _la <= 0 or _la==118 or _la==119:
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 1122
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cfour_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PSI_CFOUR(self):
            return self.getToken(PsithonParser.PSI_CFOUR, 0)

        def D_LBRACE(self):
            return self.getToken(PsithonParser.D_LBRACE, 0)

        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def header_space(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Header_spaceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Header_spaceContext,i)


        def header_label(self):
            return self.getTypedRuleContext(PsithonParser.Header_labelContext,0)


        def D_NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.D_NEWLINE)
            else:
                return self.getToken(PsithonParser.D_NEWLINE, i)

        def CFOUR_TEXT(self):
            return self.getToken(PsithonParser.CFOUR_TEXT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_cfour_block




    def cfour_block(self):

        localctx = PsithonParser.Cfour_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_cfour_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1123
            self.match(PsithonParser.PSI_CFOUR)
            self.state = 1127
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,104,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1124
                    self.header_space() 
                self.state = 1129
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,104,self._ctx)

            self.state = 1131
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & 4095) != 0):
                self.state = 1130
                self.header_label()


            self.state = 1136
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==117:
                self.state = 1133
                self.match(PsithonParser.D_NEWLINE)
                self.state = 1138
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 1139
            self.match(PsithonParser.D_LBRACE)
            self.state = 1141
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==150:
                self.state = 1140
                self.match(PsithonParser.CFOUR_TEXT)


            self.state = 1143
            self.match(PsithonParser.D_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Header_labelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_word(self):
            return self.getTypedRuleContext(PsithonParser.Native_wordContext,0)


        def D_NUMBER(self):
            return self.getToken(PsithonParser.D_NUMBER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_header_label




    def header_label(self):

        localctx = PsithonParser.Header_labelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_header_label)
        try:
            self.state = 1147
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1145
                self.native_word()
                pass
            elif token in [144]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1146
                self.match(PsithonParser.D_NUMBER)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Header_spaceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_EQUALS(self):
            return self.getToken(PsithonParser.D_EQUALS, 0)

        def D_NEWLINE(self):
            return self.getToken(PsithonParser.D_NEWLINE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_header_space




    def header_space(self):

        localctx = PsithonParser.Header_spaceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_header_space)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1149
            _la = self._input.LA(1)
            if not(_la==117 or _la==124):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Native_wordContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_identifier(self):
            return self.getTypedRuleContext(PsithonParser.Native_identifierContext,0)


        def D_HYPHEN_WORD(self):
            return self.getToken(PsithonParser.D_HYPHEN_WORD, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_native_word




    def native_word(self):

        localctx = PsithonParser.Native_wordContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_native_word)
        try:
            self.state = 1153
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [135, 136, 137, 138, 139, 140, 141, 142, 143, 145]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1151
                self.native_identifier()
                pass
            elif token in [146]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1152
                self.match(PsithonParser.D_HYPHEN_WORD)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Native_identifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_WORD(self):
            return self.getToken(PsithonParser.D_WORD, 0)

        def D_UNITS(self):
            return self.getToken(PsithonParser.D_UNITS, 0)

        def D_NO_COM(self):
            return self.getToken(PsithonParser.D_NO_COM, 0)

        def D_NO_REORIENT(self):
            return self.getToken(PsithonParser.D_NO_REORIENT, 0)

        def D_SYMMETRY(self):
            return self.getToken(PsithonParser.D_SYMMETRY, 0)

        def D_PUBCHEM(self):
            return self.getToken(PsithonParser.D_PUBCHEM, 0)

        def D_FROM_FILE(self):
            return self.getToken(PsithonParser.D_FROM_FILE, 0)

        def D_EFP(self):
            return self.getToken(PsithonParser.D_EFP, 0)

        def D_GHOST(self):
            return self.getToken(PsithonParser.D_GHOST, 0)

        def D_ASSIGN(self):
            return self.getToken(PsithonParser.D_ASSIGN, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_native_identifier




    def native_identifier(self):

        localctx = PsithonParser.Native_identifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 100, self.RULE_native_identifier)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1155
            _la = self._input.LA(1)
            if not(((((_la - 135)) & ~0x3f) == 0 and ((1 << (_la - 135)) & 1535) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Literal_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal_piece(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Literal_pieceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Literal_pieceContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_literal_line




    def literal_line(self):

        localctx = PsithonParser.Literal_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 102, self.RULE_literal_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1158 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1157
                self.literal_piece()
                self.state = 1160 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & -2) != 0) or ((((_la - 64)) & ~0x3f) == 0 and ((1 << (_la - 64)) & -45106365017882625) != 0) or ((((_la - 128)) & ~0x3f) == 0 and ((1 << (_la - 128)) & 16777215) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Literal_pieceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def D_NEWLINE(self):
            return self.getToken(PsithonParser.D_NEWLINE, 0)

        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def D_RBRACE(self):
            return self.getToken(PsithonParser.D_RBRACE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_literal_piece




    def literal_piece(self):

        localctx = PsithonParser.Literal_pieceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 104, self.RULE_literal_piece)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1162
            _la = self._input.LA(1)
            if _la <= 0 or ((((_la - 110)) & ~0x3f) == 0 and ((1 << (_la - 110)) & 641) != 0):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Param_endContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def TYPE_COMMENT(self):
            return self.getToken(PsithonParser.TYPE_COMMENT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_param_end




    def param_end(self):

        localctx = PsithonParser.Param_endContext(self, self._ctx, self.state)
        self.enterRule(localctx, 106, self.RULE_param_end)
        self._la = 0 # Token type
        try:
            self.state = 1172
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,113,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1164
                self.match(PsithonParser.COMMA)
                self.state = 1166
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 1165
                    self.match(PsithonParser.TYPE_COMMENT)


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1169
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,112,self._ctx)
                if la_ == 1:
                    self.state = 1168
                    self.match(PsithonParser.TYPE_COMMENT)


                self.state = 1171
                if not self._input.LA(1) == self.RPAR:
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, "self._input.LA(1) == self.RPAR")
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Slash_endContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_slash_end




    def slash_end(self):

        localctx = PsithonParser.Slash_endContext(self, self._ctx, self.state)
        self.enterRule(localctx, 108, self.RULE_slash_end)
        try:
            self.state = 1176
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,114,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1174
                self.match(PsithonParser.COMMA)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1175
                if not self._input.LA(1) == self.RPAR:
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, "self._input.LA(1) == self.RPAR")
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Param_no_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def param(self):
            return self.getTypedRuleContext(PsithonParser.ParamContext,0)


        def param_end(self):
            return self.getTypedRuleContext(PsithonParser.Param_endContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_param_no_default




    def param_no_default(self):

        localctx = PsithonParser.Param_no_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 110, self.RULE_param_no_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1178
            self.param()
            self.state = 1179
            self.param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Param_no_default_star_annotationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def param_star_annotation(self):
            return self.getTypedRuleContext(PsithonParser.Param_star_annotationContext,0)


        def param_end(self):
            return self.getTypedRuleContext(PsithonParser.Param_endContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_param_no_default_star_annotation




    def param_no_default_star_annotation(self):

        localctx = PsithonParser.Param_no_default_star_annotationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 112, self.RULE_param_no_default_star_annotation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1181
            self.param_star_annotation()
            self.state = 1182
            self.param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Param_with_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def param(self):
            return self.getTypedRuleContext(PsithonParser.ParamContext,0)


        def default_assignment(self):
            return self.getTypedRuleContext(PsithonParser.Default_assignmentContext,0)


        def param_end(self):
            return self.getTypedRuleContext(PsithonParser.Param_endContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_param_with_default




    def param_with_default(self):

        localctx = PsithonParser.Param_with_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 114, self.RULE_param_with_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1184
            self.param()
            self.state = 1185
            self.default_assignment()
            self.state = 1186
            self.param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Param_maybe_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def param(self):
            return self.getTypedRuleContext(PsithonParser.ParamContext,0)


        def param_end(self):
            return self.getTypedRuleContext(PsithonParser.Param_endContext,0)


        def default_assignment(self):
            return self.getTypedRuleContext(PsithonParser.Default_assignmentContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_param_maybe_default




    def param_maybe_default(self):

        localctx = PsithonParser.Param_maybe_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 116, self.RULE_param_maybe_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1188
            self.param()
            self.state = 1190
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,115,self._ctx)
            if la_ == 1:
                self.state = 1189
                self.default_assignment()


            self.state = 1192
            self.param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Slash_no_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLASH(self):
            return self.getToken(PsithonParser.SLASH, 0)

        def slash_end(self):
            return self.getTypedRuleContext(PsithonParser.Slash_endContext,0)


        def param_no_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Param_no_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Param_no_defaultContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_slash_no_default




    def slash_no_default(self):

        localctx = PsithonParser.Slash_no_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 118, self.RULE_slash_no_default)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1195 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1194
                self.param_no_default()
                self.state = 1197 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                    break

            self.state = 1199
            self.match(PsithonParser.SLASH)
            self.state = 1200
            self.slash_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Slash_with_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLASH(self):
            return self.getToken(PsithonParser.SLASH, 0)

        def slash_end(self):
            return self.getTypedRuleContext(PsithonParser.Slash_endContext,0)


        def param_no_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Param_no_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Param_no_defaultContext,i)


        def param_with_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Param_with_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Param_with_defaultContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_slash_with_default




    def slash_with_default(self):

        localctx = PsithonParser.Slash_with_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 120, self.RULE_slash_with_default)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1205
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,117,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1202
                    self.param_no_default() 
                self.state = 1207
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,117,self._ctx)

            self.state = 1209 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1208
                self.param_with_default()
                self.state = 1211 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                    break

            self.state = 1213
            self.match(PsithonParser.SLASH)
            self.state = 1214
            self.slash_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_param_endContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_param_end




    def lambda_param_end(self):

        localctx = PsithonParser.Lambda_param_endContext(self, self._ctx, self.state)
        self.enterRule(localctx, 122, self.RULE_lambda_param_end)
        try:
            self.state = 1218
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,119,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1216
                self.match(PsithonParser.COMMA)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1217
                if not self._input.LA(1) == self.COLON:
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, "self._input.LA(1) == self.COLON")
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_param_no_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lambda_param(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_paramContext,0)


        def lambda_param_end(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_endContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_param_no_default




    def lambda_param_no_default(self):

        localctx = PsithonParser.Lambda_param_no_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 124, self.RULE_lambda_param_no_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1220
            self.lambda_param()
            self.state = 1221
            self.lambda_param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_param_with_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lambda_param(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_paramContext,0)


        def default_assignment(self):
            return self.getTypedRuleContext(PsithonParser.Default_assignmentContext,0)


        def lambda_param_end(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_endContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_param_with_default




    def lambda_param_with_default(self):

        localctx = PsithonParser.Lambda_param_with_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 126, self.RULE_lambda_param_with_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1223
            self.lambda_param()
            self.state = 1224
            self.default_assignment()
            self.state = 1225
            self.lambda_param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_param_maybe_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lambda_param(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_paramContext,0)


        def lambda_param_end(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_endContext,0)


        def default_assignment(self):
            return self.getTypedRuleContext(PsithonParser.Default_assignmentContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_param_maybe_default




    def lambda_param_maybe_default(self):

        localctx = PsithonParser.Lambda_param_maybe_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 128, self.RULE_lambda_param_maybe_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1227
            self.lambda_param()
            self.state = 1229
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,120,self._ctx)
            if la_ == 1:
                self.state = 1228
                self.default_assignment()


            self.state = 1231
            self.lambda_param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_slash_no_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLASH(self):
            return self.getToken(PsithonParser.SLASH, 0)

        def lambda_param_end(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_endContext,0)


        def lambda_param_no_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Lambda_param_no_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Lambda_param_no_defaultContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_slash_no_default




    def lambda_slash_no_default(self):

        localctx = PsithonParser.Lambda_slash_no_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 130, self.RULE_lambda_slash_no_default)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1234 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1233
                self.lambda_param_no_default()
                self.state = 1236 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                    break

            self.state = 1238
            self.match(PsithonParser.SLASH)
            self.state = 1239
            self.lambda_param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_slash_with_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLASH(self):
            return self.getToken(PsithonParser.SLASH, 0)

        def lambda_param_end(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_endContext,0)


        def lambda_param_no_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Lambda_param_no_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Lambda_param_no_defaultContext,i)


        def lambda_param_with_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Lambda_param_with_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Lambda_param_with_defaultContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_slash_with_default




    def lambda_slash_with_default(self):

        localctx = PsithonParser.Lambda_slash_with_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 132, self.RULE_lambda_slash_with_default)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1244
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,122,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1241
                    self.lambda_param_no_default() 
                self.state = 1246
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,122,self._ctx)

            self.state = 1248 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1247
                self.lambda_param_with_default()
                self.state = 1250 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                    break

            self.state = 1252
            self.match(PsithonParser.SLASH)
            self.state = 1253
            self.lambda_param_end()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Import_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IMPORT(self):
            return self.getToken(PsithonParser.IMPORT, 0)

        def dotted_as_names(self):
            return self.getTypedRuleContext(PsithonParser.Dotted_as_namesContext,0)


        def NAME_OR_LAZY(self):
            return self.getToken(PsithonParser.NAME_OR_LAZY, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_import_name




    def import_name(self):

        localctx = PsithonParser.Import_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 134, self.RULE_import_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1256
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 1255
                self.match(PsithonParser.NAME_OR_LAZY)


            self.state = 1258
            self.match(PsithonParser.IMPORT)
            self.state = 1259
            self.dotted_as_names()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Import_fromContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FROM(self):
            return self.getToken(PsithonParser.FROM, 0)

        def dotted_name(self):
            return self.getTypedRuleContext(PsithonParser.Dotted_nameContext,0)


        def IMPORT(self):
            return self.getToken(PsithonParser.IMPORT, 0)

        def import_from_targets(self):
            return self.getTypedRuleContext(PsithonParser.Import_from_targetsContext,0)


        def NAME_OR_LAZY(self):
            return self.getToken(PsithonParser.NAME_OR_LAZY, 0)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.DOT)
            else:
                return self.getToken(PsithonParser.DOT, i)

        def ELLIPSIS(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.ELLIPSIS)
            else:
                return self.getToken(PsithonParser.ELLIPSIS, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_import_from




    def import_from(self):

        localctx = PsithonParser.Import_fromContext(self, self._ctx, self.state)
        self.enterRule(localctx, 136, self.RULE_import_from)
        self._la = 0 # Token type
        try:
            self.state = 1286
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,129,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1262
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==19:
                    self.state = 1261
                    self.match(PsithonParser.NAME_OR_LAZY)


                self.state = 1264
                self.match(PsithonParser.FROM)
                self.state = 1268
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==26 or _la==65:
                    self.state = 1265
                    _la = self._input.LA(1)
                    if not(_la==26 or _la==65):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 1270
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1271
                self.dotted_name(0)
                self.state = 1272
                self.match(PsithonParser.IMPORT)
                self.state = 1273
                self.import_from_targets()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1276
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==19:
                    self.state = 1275
                    self.match(PsithonParser.NAME_OR_LAZY)


                self.state = 1278
                self.match(PsithonParser.FROM)
                self.state = 1280 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 1279
                    _la = self._input.LA(1)
                    if not(_la==26 or _la==65):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 1282 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==26 or _la==65):
                        break

                self.state = 1284
                self.match(PsithonParser.IMPORT)
                self.state = 1285
                self.import_from_targets()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Name_except_underscoreContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(PsithonParser.NAME, 0)

        def NAME_OR_TYPE(self):
            return self.getToken(PsithonParser.NAME_OR_TYPE, 0)

        def NAME_OR_MATCH(self):
            return self.getToken(PsithonParser.NAME_OR_MATCH, 0)

        def NAME_OR_CASE(self):
            return self.getToken(PsithonParser.NAME_OR_CASE, 0)

        def NAME_OR_LAZY(self):
            return self.getToken(PsithonParser.NAME_OR_LAZY, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_name_except_underscore




    def name_except_underscore(self):

        localctx = PsithonParser.Name_except_underscoreContext(self, self._ctx, self.state)
        self.enterRule(localctx, 138, self.RULE_name_except_underscore)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1288
            _la = self._input.LA(1)
            if not(_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 23) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Noteq_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def NOTEQUAL(self):
            return self.getToken(PsithonParser.NOTEQUAL, 0)

        def PSI_BARRY_NOTEQUAL(self):
            return self.getToken(PsithonParser.PSI_BARRY_NOTEQUAL, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_noteq_bitwise_or




    def noteq_bitwise_or(self):

        localctx = PsithonParser.Noteq_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 140, self.RULE_noteq_bitwise_or)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1290
            _la = self._input.LA(1)
            if not(_la==18 or _la==41):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 1291
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenexpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def for_if_clauses(self):
            return self.getTypedRuleContext(PsithonParser.For_if_clausesContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def assignment_expression(self):
            return self.getTypedRuleContext(PsithonParser.Assignment_expressionContext,0)


        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def starred_expression(self):
            return self.getTypedRuleContext(PsithonParser.Starred_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_genexp




    def genexp(self):

        localctx = PsithonParser.GenexpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 142, self.RULE_genexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1293
            self.match(PsithonParser.LPAR)
            self.state = 1297
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,130,self._ctx)
            if la_ == 1:
                self.state = 1294
                self.assignment_expression()
                pass

            elif la_ == 2:
                self.state = 1295
                self.expression()
                pass

            elif la_ == 3:
                self.state = 1296
                self.starred_expression()
                pass


            self.state = 1299
            self.for_if_clauses()
            self.state = 1300
            self.match(PsithonParser.RPAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DictcompContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def for_if_clauses(self):
            return self.getTypedRuleContext(PsithonParser.For_if_clausesContext,0)


        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def kvpair(self):
            return self.getTypedRuleContext(PsithonParser.KvpairContext,0)


        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_dictcomp




    def dictcomp(self):

        localctx = PsithonParser.DictcompContext(self, self._ctx, self.state)
        self.enterRule(localctx, 144, self.RULE_dictcomp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1302
            self.match(PsithonParser.LBRACE)
            self.state = 1306
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,131,self._ctx)
            if la_ == 1:
                self.state = 1303
                self.kvpair()
                pass

            elif la_ == 2:
                self.state = 1304
                self.match(PsithonParser.DOUBLESTAR)
                self.state = 1305
                self.expression()
                pass


            self.state = 1308
            self.for_if_clauses()
            self.state = 1309
            self.match(PsithonParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ListcompContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def star_named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionContext,0)


        def for_if_clauses(self):
            return self.getTypedRuleContext(PsithonParser.For_if_clausesContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_listcomp




    def listcomp(self):

        localctx = PsithonParser.ListcompContext(self, self._ctx, self.state)
        self.enterRule(localctx, 146, self.RULE_listcomp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1311
            self.match(PsithonParser.LSQB)
            self.state = 1312
            self.star_named_expression()
            self.state = 1313
            self.for_if_clauses()
            self.state = 1314
            self.match(PsithonParser.RSQB)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SetcompContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def star_named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionContext,0)


        def for_if_clauses(self):
            return self.getTypedRuleContext(PsithonParser.For_if_clausesContext,0)


        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_setcomp




    def setcomp(self):

        localctx = PsithonParser.SetcompContext(self, self._ctx, self.state)
        self.enterRule(localctx, 148, self.RULE_setcomp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1316
            self.match(PsithonParser.LBRACE)
            self.state = 1317
            self.star_named_expression()
            self.state = 1318
            self.for_if_clauses()
            self.state = 1319
            self.match(PsithonParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Return_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(PsithonParser.RETURN, 0)

        def star_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_return_stmt




    def return_stmt(self):

        localctx = PsithonParser.Return_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 150, self.RULE_return_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1321
            if not (self.psithon_deferred() or self.psithon_scope(localctx) in {"function", "async"}):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self.psithon_deferred() or self.psithon_scope($ctx) in {\"function\", \"async\"})")
            self.state = 1322
            self.match(PsithonParser.RETURN)
            self.state = 1324
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,132,self._ctx)
            if la_ == 1:
                self.state = 1323
                self.star_expressions()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Break_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BREAK(self):
            return self.getToken(PsithonParser.BREAK, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_break_stmt




    def break_stmt(self):

        localctx = PsithonParser.Break_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 152, self.RULE_break_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1326
            if not (self.psithon_deferred() or self.psithon_loop(localctx)):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self.psithon_deferred() or self.psithon_loop($ctx))")
            self.state = 1327
            self.match(PsithonParser.BREAK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Continue_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONTINUE(self):
            return self.getToken(PsithonParser.CONTINUE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_continue_stmt




    def continue_stmt(self):

        localctx = PsithonParser.Continue_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 154, self.RULE_continue_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1329
            if not (self.psithon_deferred() or self.psithon_loop(localctx)):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self.psithon_deferred() or self.psithon_loop($ctx))")
            self.state = 1330
            self.match(PsithonParser.CONTINUE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Yield_exprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def YIELD(self):
            return self.getToken(PsithonParser.YIELD, 0)

        def FROM(self):
            return self.getToken(PsithonParser.FROM, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def star_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_yield_expr




    def yield_expr(self):

        localctx = PsithonParser.Yield_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 156, self.RULE_yield_expr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1332
            if not (self.psithon_deferred() or self.psithon_scope(localctx) in {"function", "async", "lambda"}):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self.psithon_deferred() or self.psithon_scope($ctx) in {\"function\", \"async\", \"lambda\"})")
            self.state = 1333
            self.match(PsithonParser.YIELD)
            self.state = 1340
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,134,self._ctx)
            if la_ == 1:
                self.state = 1334
                if not (self.psithon_deferred() or self.psithon_scope(localctx) != "async"):
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, "(self.psithon_deferred() or self.psithon_scope($ctx) != \"async\")")
                self.state = 1335
                self.match(PsithonParser.FROM)
                self.state = 1336
                self.expression()
                pass

            elif la_ == 2:
                self.state = 1338
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,133,self._ctx)
                if la_ == 1:
                    self.state = 1337
                    self.star_expressions()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Await_primaryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AWAIT(self):
            return self.getToken(PsithonParser.AWAIT, 0)

        def primary(self):
            return self.getTypedRuleContext(PsithonParser.PrimaryContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_await_primary




    def await_primary(self):

        localctx = PsithonParser.Await_primaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 158, self.RULE_await_primary)
        try:
            self.state = 1346
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,135,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1342
                if not (self.psithon_deferred() or self.psithon_scope(localctx) in {"async", "generator", "async_comprehension"}):
                    from antlr4.error.Errors import FailedPredicateException
                    raise FailedPredicateException(self, "(self.psithon_deferred() or self.psithon_scope($ctx) in {\"async\", \"generator\", \"async_comprehension\"})")
                self.state = 1343
                self.match(PsithonParser.AWAIT)
                self.state = 1344
                self.primary(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1345
                self.primary(0)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class For_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FOR(self):
            return self.getToken(PsithonParser.FOR, 0)

        def star_targets(self):
            return self.getTypedRuleContext(PsithonParser.Star_targetsContext,0)


        def IN(self):
            return self.getToken(PsithonParser.IN, 0)

        def star_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionsContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def ASYNC(self):
            return self.getToken(PsithonParser.ASYNC, 0)

        def TYPE_COMMENT(self):
            return self.getToken(PsithonParser.TYPE_COMMENT, 0)

        def else_block(self):
            return self.getTypedRuleContext(PsithonParser.Else_blockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_for_stmt




    def for_stmt(self):

        localctx = PsithonParser.For_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 160, self.RULE_for_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1348
            if not (self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope(localctx) == "async"):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope($ctx) == \"async\")")
            self.state = 1350
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==98:
                self.state = 1349
                self.match(PsithonParser.ASYNC)


            self.state = 1352
            self.match(PsithonParser.FOR)
            self.state = 1353
            self.star_targets()
            self.state = 1354
            self.match(PsithonParser.IN)
            self.state = 1355
            self.star_expressions()
            self.state = 1356
            self.match(PsithonParser.COLON)
            self.state = 1358
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,137,self._ctx)
            if la_ == 1:
                self.state = 1357
                self.match(PsithonParser.TYPE_COMMENT)


            self.state = 1360
            self.block()
            self.state = 1362
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,138,self._ctx)
            if la_ == 1:
                self.state = 1361
                self.else_block()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class With_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WITH(self):
            return self.getToken(PsithonParser.WITH, 0)

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def with_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.With_itemContext)
            else:
                return self.getTypedRuleContext(PsithonParser.With_itemContext,i)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def ASYNC(self):
            return self.getToken(PsithonParser.ASYNC, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def TYPE_COMMENT(self):
            return self.getToken(PsithonParser.TYPE_COMMENT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_with_stmt




    def with_stmt(self):

        localctx = PsithonParser.With_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 162, self.RULE_with_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1364
            if not (self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope(localctx) == "async"):
                from antlr4.error.Errors import FailedPredicateException
                raise FailedPredicateException(self, "(self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope($ctx) == \"async\")")
            self.state = 1421
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,147,self._ctx)
            if la_ == 1:
                self.state = 1365
                self.match(PsithonParser.WITH)
                self.state = 1366
                self.match(PsithonParser.LPAR)
                self.state = 1367
                self.with_item()
                self.state = 1372
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,139,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 1368
                        self.match(PsithonParser.COMMA)
                        self.state = 1369
                        self.with_item() 
                    self.state = 1374
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,139,self._ctx)

                self.state = 1376
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 1375
                    self.match(PsithonParser.COMMA)


                self.state = 1378
                self.match(PsithonParser.RPAR)
                self.state = 1379
                self.match(PsithonParser.COLON)
                self.state = 1381
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,141,self._ctx)
                if la_ == 1:
                    self.state = 1380
                    self.match(PsithonParser.TYPE_COMMENT)


                self.state = 1383
                self.block()
                pass

            elif la_ == 2:
                self.state = 1385
                self.match(PsithonParser.ASYNC)
                self.state = 1386
                self.match(PsithonParser.WITH)
                self.state = 1387
                self.match(PsithonParser.LPAR)
                self.state = 1388
                self.with_item()
                self.state = 1393
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,142,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 1389
                        self.match(PsithonParser.COMMA)
                        self.state = 1390
                        self.with_item() 
                    self.state = 1395
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,142,self._ctx)

                self.state = 1397
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 1396
                    self.match(PsithonParser.COMMA)


                self.state = 1399
                self.match(PsithonParser.RPAR)
                self.state = 1400
                self.match(PsithonParser.COLON)
                self.state = 1401
                self.block()
                pass

            elif la_ == 3:
                self.state = 1404
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==98:
                    self.state = 1403
                    self.match(PsithonParser.ASYNC)


                self.state = 1406
                self.match(PsithonParser.WITH)
                self.state = 1407
                self.with_item()
                self.state = 1412
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==28:
                    self.state = 1408
                    self.match(PsithonParser.COMMA)
                    self.state = 1409
                    self.with_item()
                    self.state = 1414
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1415
                self.match(PsithonParser.COLON)
                self.state = 1417
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,146,self._ctx)
                if la_ == 1:
                    self.state = 1416
                    self.match(PsithonParser.TYPE_COMMENT)


                self.state = 1419
                self.block()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Native_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def set_command(self):
            return self.getTypedRuleContext(PsithonParser.Set_commandContext,0)


        def set_block(self):
            return self.getTypedRuleContext(PsithonParser.Set_blockContext,0)


        def molecule_block(self):
            return self.getTypedRuleContext(PsithonParser.Molecule_blockContext,0)


        def basis_block(self):
            return self.getTypedRuleContext(PsithonParser.Basis_blockContext,0)


        def external_block(self):
            return self.getTypedRuleContext(PsithonParser.External_blockContext,0)


        def pcm_block(self):
            return self.getTypedRuleContext(PsithonParser.Pcm_blockContext,0)


        def cfour_block(self):
            return self.getTypedRuleContext(PsithonParser.Cfour_blockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_native_expression




    def native_expression(self):

        localctx = PsithonParser.Native_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 164, self.RULE_native_expression)
        try:
            self.state = 1430
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,148,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1423
                self.set_command()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1424
                self.set_block()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1425
                self.molecule_block()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1426
                self.basis_block()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 1427
                self.external_block()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 1428
                self.pcm_block()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 1429
                self.cfour_block()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def native_expression(self):
            return self.getTypedRuleContext(PsithonParser.Native_expressionContext,0)


        def memory_line(self):
            return self.getTypedRuleContext(PsithonParser.Memory_lineContext,0)


        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def TRUE(self):
            return self.getToken(PsithonParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(PsithonParser.FALSE, 0)

        def NONE(self):
            return self.getToken(PsithonParser.NONE, 0)

        def strings(self):
            return self.getTypedRuleContext(PsithonParser.StringsContext,0)


        def NUMBER(self):
            return self.getToken(PsithonParser.NUMBER, 0)

        def tuple_(self):
            return self.getTypedRuleContext(PsithonParser.TupleContext,0)


        def group(self):
            return self.getTypedRuleContext(PsithonParser.GroupContext,0)


        def genexp(self):
            return self.getTypedRuleContext(PsithonParser.GenexpContext,0)


        def list_(self):
            return self.getTypedRuleContext(PsithonParser.ListContext,0)


        def listcomp(self):
            return self.getTypedRuleContext(PsithonParser.ListcompContext,0)


        def dict_(self):
            return self.getTypedRuleContext(PsithonParser.DictContext,0)


        def set_(self):
            return self.getTypedRuleContext(PsithonParser.SetContext,0)


        def dictcomp(self):
            return self.getTypedRuleContext(PsithonParser.DictcompContext,0)


        def setcomp(self):
            return self.getTypedRuleContext(PsithonParser.SetcompContext,0)


        def ELLIPSIS(self):
            return self.getToken(PsithonParser.ELLIPSIS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_atom




    def atom(self):

        localctx = PsithonParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 166, self.RULE_atom)
        try:
            self.state = 1456
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [11, 12, 13, 14, 15, 16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1432
                self.native_expression()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1433
                self.memory_line()
                pass
            elif token in [19, 103, 104, 105, 106, 107]:
                self.enterOuterAlt(localctx, 3)
                self.state = 1434
                self.name()
                pass
            elif token in [78]:
                self.enterOuterAlt(localctx, 4)
                self.state = 1435
                self.match(PsithonParser.TRUE)
                pass
            elif token in [68]:
                self.enterOuterAlt(localctx, 5)
                self.state = 1436
                self.match(PsithonParser.FALSE)
                pass
            elif token in [73]:
                self.enterOuterAlt(localctx, 6)
                self.state = 1437
                self.match(PsithonParser.NONE)
                pass
            elif token in [5, 8, 109]:
                self.enterOuterAlt(localctx, 7)
                self.state = 1438
                self.strings()
                pass
            elif token in [108]:
                self.enterOuterAlt(localctx, 8)
                self.state = 1439
                self.match(PsithonParser.NUMBER)
                pass
            elif token in [20]:
                self.enterOuterAlt(localctx, 9)
                self.state = 1443
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,149,self._ctx)
                if la_ == 1:
                    self.state = 1440
                    self.tuple_()
                    pass

                elif la_ == 2:
                    self.state = 1441
                    self.group()
                    pass

                elif la_ == 3:
                    self.state = 1442
                    self.genexp()
                    pass


                pass
            elif token in [21]:
                self.enterOuterAlt(localctx, 10)
                self.state = 1447
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,150,self._ctx)
                if la_ == 1:
                    self.state = 1445
                    self.list_()
                    pass

                elif la_ == 2:
                    self.state = 1446
                    self.listcomp()
                    pass


                pass
            elif token in [22]:
                self.enterOuterAlt(localctx, 11)
                self.state = 1453
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,151,self._ctx)
                if la_ == 1:
                    self.state = 1449
                    self.dict_()
                    pass

                elif la_ == 2:
                    self.state = 1450
                    self.set_()
                    pass

                elif la_ == 3:
                    self.state = 1451
                    self.dictcomp()
                    pass

                elif la_ == 4:
                    self.state = 1452
                    self.setcomp()
                    pass


                pass
            elif token in [65]:
                self.enterOuterAlt(localctx, 12)
                self.state = 1455
                self.match(PsithonParser.ELLIPSIS)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InteractiveContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement_newline(self):
            return self.getTypedRuleContext(PsithonParser.Statement_newlineContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_interactive




    def interactive(self):

        localctx = PsithonParser.InteractiveContext(self, self._ctx, self.state)
        self.enterRule(localctx, 168, self.RULE_interactive)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1458
            self.statement_newline()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EvalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expressions(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionsContext,0)


        def EOF(self):
            return self.getToken(PsithonParser.EOF, 0)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.NEWLINE)
            else:
                return self.getToken(PsithonParser.NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_eval




    def eval_(self):

        localctx = PsithonParser.EvalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 170, self.RULE_eval)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1460
            self.expressions()
            self.state = 1464
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==110:
                self.state = 1461
                self.match(PsithonParser.NEWLINE)
                self.state = 1466
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 1467
            self.match(PsithonParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Func_typeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def RARROW(self):
            return self.getToken(PsithonParser.RARROW, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(PsithonParser.EOF, 0)

        def type_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Type_expressionsContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.NEWLINE)
            else:
                return self.getToken(PsithonParser.NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_func_type




    def func_type(self):

        localctx = PsithonParser.Func_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 172, self.RULE_func_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1469
            self.match(PsithonParser.LPAR)
            self.state = 1471
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,154,self._ctx)
            if la_ == 1:
                self.state = 1470
                self.type_expressions()


            self.state = 1473
            self.match(PsithonParser.RPAR)
            self.state = 1474
            self.match(PsithonParser.RARROW)
            self.state = 1475
            self.expression()
            self.state = 1479
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==110:
                self.state = 1476
                self.match(PsithonParser.NEWLINE)
                self.state = 1481
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 1482
            self.match(PsithonParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.StatementContext)
            else:
                return self.getTypedRuleContext(PsithonParser.StatementContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_statements




    def statements(self):

        localctx = PsithonParser.StatementsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 174, self.RULE_statements)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1485 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 1484
                    self.statement()

                else:
                    raise NoViableAltException(self)
                self.state = 1487 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,156,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Single_compound_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def compound_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Compound_stmtContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_single_compound_stmt




    def single_compound_stmt(self):

        localctx = PsithonParser.Single_compound_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 176, self.RULE_single_compound_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1489
            self.compound_stmt()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Statement_newlineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def single_compound_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Single_compound_stmtContext,0)


        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def simple_stmts(self):
            return self.getTypedRuleContext(PsithonParser.Simple_stmtsContext,0)


        def EOF(self):
            return self.getToken(PsithonParser.EOF, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_statement_newline




    def statement_newline(self):

        localctx = PsithonParser.Statement_newlineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 178, self.RULE_statement_newline)
        try:
            self.state = 1497
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,157,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1491
                self.single_compound_stmt()
                self.state = 1492
                self.match(PsithonParser.NEWLINE)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1494
                self.simple_stmts()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1495
                self.match(PsithonParser.NEWLINE)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1496
                self.match(PsithonParser.EOF)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Simple_stmtsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def simple_stmt(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Simple_stmtContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Simple_stmtContext,i)


        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def SEMI(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.SEMI)
            else:
                return self.getToken(PsithonParser.SEMI, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_simple_stmts




    def simple_stmts(self):

        localctx = PsithonParser.Simple_stmtsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 180, self.RULE_simple_stmts)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1499
            self.simple_stmt()
            self.state = 1504
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,158,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1500
                    self.match(PsithonParser.SEMI)
                    self.state = 1501
                    self.simple_stmt() 
                self.state = 1506
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,158,self._ctx)

            self.state = 1508
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==29:
                self.state = 1507
                self.match(PsithonParser.SEMI)


            self.state = 1510
            self.match(PsithonParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Simple_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignment(self):
            return self.getTypedRuleContext(PsithonParser.AssignmentContext,0)


        def type_alias(self):
            return self.getTypedRuleContext(PsithonParser.Type_aliasContext,0)


        def star_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionsContext,0)


        def return_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Return_stmtContext,0)


        def import_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Import_stmtContext,0)


        def raise_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Raise_stmtContext,0)


        def pass_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Pass_stmtContext,0)


        def del_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Del_stmtContext,0)


        def yield_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Yield_stmtContext,0)


        def assert_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Assert_stmtContext,0)


        def break_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Break_stmtContext,0)


        def continue_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Continue_stmtContext,0)


        def global_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Global_stmtContext,0)


        def nonlocal_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Nonlocal_stmtContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_simple_stmt




    def simple_stmt(self):

        localctx = PsithonParser.Simple_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 182, self.RULE_simple_stmt)
        try:
            self.state = 1526
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,160,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1512
                self.assignment()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1513
                self.type_alias()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1514
                self.star_expressions()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1515
                self.return_stmt()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 1516
                self.import_stmt()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 1517
                self.raise_stmt()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 1518
                self.pass_stmt()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 1519
                self.del_stmt()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 1520
                self.yield_stmt()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 1521
                self.assert_stmt()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 1522
                self.break_stmt()
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 1523
                self.continue_stmt()
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 1524
                self.global_stmt()
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 1525
                self.nonlocal_stmt()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compound_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def function_def(self):
            return self.getTypedRuleContext(PsithonParser.Function_defContext,0)


        def if_stmt(self):
            return self.getTypedRuleContext(PsithonParser.If_stmtContext,0)


        def class_def(self):
            return self.getTypedRuleContext(PsithonParser.Class_defContext,0)


        def with_stmt(self):
            return self.getTypedRuleContext(PsithonParser.With_stmtContext,0)


        def for_stmt(self):
            return self.getTypedRuleContext(PsithonParser.For_stmtContext,0)


        def try_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Try_stmtContext,0)


        def while_stmt(self):
            return self.getTypedRuleContext(PsithonParser.While_stmtContext,0)


        def match_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Match_stmtContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_compound_stmt




    def compound_stmt(self):

        localctx = PsithonParser.Compound_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 184, self.RULE_compound_stmt)
        try:
            self.state = 1536
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,161,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1528
                self.function_def()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1529
                self.if_stmt()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1530
                self.class_def()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1531
                self.with_stmt()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 1532
                self.for_stmt()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 1533
                self.try_stmt()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 1534
                self.while_stmt()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 1535
                self.match_stmt()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def EQUAL(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.EQUAL)
            else:
                return self.getToken(PsithonParser.EQUAL, i)

        def annotated_rhs(self):
            return self.getTypedRuleContext(PsithonParser.Annotated_rhsContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def single_target(self):
            return self.getTypedRuleContext(PsithonParser.Single_targetContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def single_subscript_attribute_target(self):
            return self.getTypedRuleContext(PsithonParser.Single_subscript_attribute_targetContext,0)


        def star_targets(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Star_targetsContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Star_targetsContext,i)


        def TYPE_COMMENT(self):
            return self.getToken(PsithonParser.TYPE_COMMENT, 0)

        def augassign(self):
            return self.getTypedRuleContext(PsithonParser.AugassignContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_assignment




    def assignment(self):

        localctx = PsithonParser.AssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 186, self.RULE_assignment)
        self._la = 0 # Token type
        try:
            self.state = 1573
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,167,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1538
                self.name()
                self.state = 1539
                self.match(PsithonParser.COLON)
                self.state = 1540
                self.expression()
                self.state = 1543
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==38:
                    self.state = 1541
                    self.match(PsithonParser.EQUAL)
                    self.state = 1542
                    self.annotated_rhs()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1550
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,163,self._ctx)
                if la_ == 1:
                    self.state = 1545
                    self.match(PsithonParser.LPAR)
                    self.state = 1546
                    self.single_target()
                    self.state = 1547
                    self.match(PsithonParser.RPAR)
                    pass

                elif la_ == 2:
                    self.state = 1549
                    self.single_subscript_attribute_target()
                    pass


                self.state = 1552
                self.match(PsithonParser.COLON)
                self.state = 1553
                self.expression()
                self.state = 1556
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==38:
                    self.state = 1554
                    self.match(PsithonParser.EQUAL)
                    self.state = 1555
                    self.annotated_rhs()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1561 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 1558
                        self.star_targets()
                        self.state = 1559
                        self.match(PsithonParser.EQUAL)

                    else:
                        raise NoViableAltException(self)
                    self.state = 1563 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,165,self._ctx)

                self.state = 1565
                self.annotated_rhs()
                self.state = 1567
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 1566
                    self.match(PsithonParser.TYPE_COMMENT)


                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1569
                self.single_target()
                self.state = 1570
                self.augassign()
                self.state = 1571
                self.annotated_rhs()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Annotated_rhsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def yield_expr(self):
            return self.getTypedRuleContext(PsithonParser.Yield_exprContext,0)


        def star_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_annotated_rhs




    def annotated_rhs(self):

        localctx = PsithonParser.Annotated_rhsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 188, self.RULE_annotated_rhs)
        try:
            self.state = 1577
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,168,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1575
                self.yield_expr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1576
                self.star_expressions()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AugassignContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PLUSEQUAL(self):
            return self.getToken(PsithonParser.PLUSEQUAL, 0)

        def MINEQUAL(self):
            return self.getToken(PsithonParser.MINEQUAL, 0)

        def STAREQUAL(self):
            return self.getToken(PsithonParser.STAREQUAL, 0)

        def ATEQUAL(self):
            return self.getToken(PsithonParser.ATEQUAL, 0)

        def SLASHEQUAL(self):
            return self.getToken(PsithonParser.SLASHEQUAL, 0)

        def PERCENTEQUAL(self):
            return self.getToken(PsithonParser.PERCENTEQUAL, 0)

        def AMPEREQUAL(self):
            return self.getToken(PsithonParser.AMPEREQUAL, 0)

        def VBAREQUAL(self):
            return self.getToken(PsithonParser.VBAREQUAL, 0)

        def CIRCUMFLEXEQUAL(self):
            return self.getToken(PsithonParser.CIRCUMFLEXEQUAL, 0)

        def LEFTSHIFTEQUAL(self):
            return self.getToken(PsithonParser.LEFTSHIFTEQUAL, 0)

        def RIGHTSHIFTEQUAL(self):
            return self.getToken(PsithonParser.RIGHTSHIFTEQUAL, 0)

        def DOUBLESTAREQUAL(self):
            return self.getToken(PsithonParser.DOUBLESTAREQUAL, 0)

        def DOUBLESLASHEQUAL(self):
            return self.getToken(PsithonParser.DOUBLESLASHEQUAL, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_augassign




    def augassign(self):

        localctx = PsithonParser.AugassignContext(self, self._ctx, self.state)
        self.enterRule(localctx, 190, self.RULE_augassign)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1579
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & -5765170472987656192) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Raise_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RAISE(self):
            return self.getToken(PsithonParser.RAISE, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def FROM(self):
            return self.getToken(PsithonParser.FROM, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_raise_stmt




    def raise_stmt(self):

        localctx = PsithonParser.Raise_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 192, self.RULE_raise_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1581
            self.match(PsithonParser.RAISE)
            self.state = 1587
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,170,self._ctx)
            if la_ == 1:
                self.state = 1582
                self.expression()
                self.state = 1585
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==90:
                    self.state = 1583
                    self.match(PsithonParser.FROM)
                    self.state = 1584
                    self.expression()




        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pass_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PASS(self):
            return self.getToken(PsithonParser.PASS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_pass_stmt




    def pass_stmt(self):

        localctx = PsithonParser.Pass_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 194, self.RULE_pass_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1589
            self.match(PsithonParser.PASS)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Global_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def GLOBAL(self):
            return self.getToken(PsithonParser.GLOBAL, 0)

        def name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.NameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.NameContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_global_stmt




    def global_stmt(self):

        localctx = PsithonParser.Global_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 196, self.RULE_global_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1591
            self.match(PsithonParser.GLOBAL)
            self.state = 1592
            self.name()
            self.state = 1597
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==28:
                self.state = 1593
                self.match(PsithonParser.COMMA)
                self.state = 1594
                self.name()
                self.state = 1599
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Nonlocal_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NONLOCAL(self):
            return self.getToken(PsithonParser.NONLOCAL, 0)

        def name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.NameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.NameContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_nonlocal_stmt




    def nonlocal_stmt(self):

        localctx = PsithonParser.Nonlocal_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 198, self.RULE_nonlocal_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1600
            self.match(PsithonParser.NONLOCAL)
            self.state = 1601
            self.name()
            self.state = 1606
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==28:
                self.state = 1602
                self.match(PsithonParser.COMMA)
                self.state = 1603
                self.name()
                self.state = 1608
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Del_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEL(self):
            return self.getToken(PsithonParser.DEL, 0)

        def del_targets(self):
            return self.getTypedRuleContext(PsithonParser.Del_targetsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_del_stmt




    def del_stmt(self):

        localctx = PsithonParser.Del_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 200, self.RULE_del_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1609
            self.match(PsithonParser.DEL)
            self.state = 1610
            self.del_targets()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Yield_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def yield_expr(self):
            return self.getTypedRuleContext(PsithonParser.Yield_exprContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_yield_stmt




    def yield_stmt(self):

        localctx = PsithonParser.Yield_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 202, self.RULE_yield_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1612
            self.yield_expr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Assert_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSERT(self):
            return self.getToken(PsithonParser.ASSERT, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_assert_stmt




    def assert_stmt(self):

        localctx = PsithonParser.Assert_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 204, self.RULE_assert_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1614
            self.match(PsithonParser.ASSERT)
            self.state = 1615
            self.expression()
            self.state = 1618
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 1616
                self.match(PsithonParser.COMMA)
                self.state = 1617
                self.expression()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Import_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def import_name(self):
            return self.getTypedRuleContext(PsithonParser.Import_nameContext,0)


        def import_from(self):
            return self.getTypedRuleContext(PsithonParser.Import_fromContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_import_stmt




    def import_stmt(self):

        localctx = PsithonParser.Import_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 206, self.RULE_import_stmt)
        try:
            self.state = 1622
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,174,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1620
                self.import_name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1621
                self.import_from()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Import_from_targetsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def import_from_as_names(self):
            return self.getTypedRuleContext(PsithonParser.Import_from_as_namesContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_import_from_targets




    def import_from_targets(self):

        localctx = PsithonParser.Import_from_targetsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 208, self.RULE_import_from_targets)
        self._la = 0 # Token type
        try:
            self.state = 1633
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [20]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1624
                self.match(PsithonParser.LPAR)
                self.state = 1625
                self.import_from_as_names()
                self.state = 1627
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 1626
                    self.match(PsithonParser.COMMA)


                self.state = 1629
                self.match(PsithonParser.RPAR)
                pass
            elif token in [19, 103, 104, 105, 106, 107]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1631
                self.import_from_as_names()
                pass
            elif token in [32]:
                self.enterOuterAlt(localctx, 3)
                self.state = 1632
                self.match(PsithonParser.STAR)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Import_from_as_namesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def import_from_as_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Import_from_as_nameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Import_from_as_nameContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_import_from_as_names




    def import_from_as_names(self):

        localctx = PsithonParser.Import_from_as_namesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 210, self.RULE_import_from_as_names)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1635
            self.import_from_as_name()
            self.state = 1640
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,177,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 1636
                    self.match(PsithonParser.COMMA)
                    self.state = 1637
                    self.import_from_as_name() 
                self.state = 1642
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,177,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Import_from_as_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.NameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.NameContext,i)


        def AS(self):
            return self.getToken(PsithonParser.AS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_import_from_as_name




    def import_from_as_name(self):

        localctx = PsithonParser.Import_from_as_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 212, self.RULE_import_from_as_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1643
            self.name()
            self.state = 1646
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 1644
                self.match(PsithonParser.AS)
                self.state = 1645
                self.name()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dotted_as_namesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def dotted_as_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Dotted_as_nameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Dotted_as_nameContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_dotted_as_names




    def dotted_as_names(self):

        localctx = PsithonParser.Dotted_as_namesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 214, self.RULE_dotted_as_names)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1648
            self.dotted_as_name()
            self.state = 1653
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==28:
                self.state = 1649
                self.match(PsithonParser.COMMA)
                self.state = 1650
                self.dotted_as_name()
                self.state = 1655
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dotted_as_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def dotted_name(self):
            return self.getTypedRuleContext(PsithonParser.Dotted_nameContext,0)


        def AS(self):
            return self.getToken(PsithonParser.AS, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_dotted_as_name




    def dotted_as_name(self):

        localctx = PsithonParser.Dotted_as_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 216, self.RULE_dotted_as_name)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1656
            self.dotted_name(0)
            self.state = 1659
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 1657
                self.match(PsithonParser.AS)
                self.state = 1658
                self.name()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Dotted_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def dotted_name(self):
            return self.getTypedRuleContext(PsithonParser.Dotted_nameContext,0)


        def DOT(self):
            return self.getToken(PsithonParser.DOT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_dotted_name



    def dotted_name(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.Dotted_nameContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 218
        self.enterRecursionRule(localctx, 218, self.RULE_dotted_name, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1662
            self.name()
            self._ctx.stop = self._input.LT(-1)
            self.state = 1669
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,181,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.Dotted_nameContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_dotted_name)
                    self.state = 1664
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 1665
                    self.match(PsithonParser.DOT)
                    self.state = 1666
                    self.name() 
                self.state = 1671
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,181,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def INDENT(self):
            return self.getToken(PsithonParser.INDENT, 0)

        def statements(self):
            return self.getTypedRuleContext(PsithonParser.StatementsContext,0)


        def DEDENT(self):
            return self.getToken(PsithonParser.DEDENT, 0)

        def simple_stmts(self):
            return self.getTypedRuleContext(PsithonParser.Simple_stmtsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_block




    def block(self):

        localctx = PsithonParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 220, self.RULE_block)
        try:
            self.state = 1678
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,182,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1672
                self.match(PsithonParser.NEWLINE)
                self.state = 1673
                self.match(PsithonParser.INDENT)
                self.state = 1674
                self.statements()
                self.state = 1675
                self.match(PsithonParser.DEDENT)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1677
                self.simple_stmts()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DecoratorsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AT(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.AT)
            else:
                return self.getToken(PsithonParser.AT, i)

        def named_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Named_expressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Named_expressionContext,i)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.NEWLINE)
            else:
                return self.getToken(PsithonParser.NEWLINE, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_decorators




    def decorators(self):

        localctx = PsithonParser.DecoratorsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 222, self.RULE_decorators)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1684 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1680
                self.match(PsithonParser.AT)
                self.state = 1681
                self.named_expression()
                self.state = 1682
                self.match(PsithonParser.NEWLINE)
                self.state = 1686 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==62):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Class_defContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def decorators(self):
            return self.getTypedRuleContext(PsithonParser.DecoratorsContext,0)


        def class_def_raw(self):
            return self.getTypedRuleContext(PsithonParser.Class_def_rawContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_class_def




    def class_def(self):

        localctx = PsithonParser.Class_defContext(self, self._ctx, self.state)
        self.enterRule(localctx, 224, self.RULE_class_def)
        try:
            self.state = 1692
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [62]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1688
                self.decorators()
                self.state = 1689
                self.class_def_raw()
                pass
            elif token in [79]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1691
                self.class_def_raw()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Class_def_rawContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CLASS(self):
            return self.getToken(PsithonParser.CLASS, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def type_params(self):
            return self.getTypedRuleContext(PsithonParser.Type_paramsContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def arguments(self):
            return self.getTypedRuleContext(PsithonParser.ArgumentsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_class_def_raw




    def class_def_raw(self):

        localctx = PsithonParser.Class_def_rawContext(self, self._ctx, self.state)
        self.enterRule(localctx, 226, self.RULE_class_def_raw)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1694
            self.match(PsithonParser.CLASS)
            self.state = 1695
            self.name()
            self.state = 1697
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==21:
                self.state = 1696
                self.type_params()


            self.state = 1704
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==20:
                self.state = 1699
                self.match(PsithonParser.LPAR)
                self.state = 1701
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,186,self._ctx)
                if la_ == 1:
                    self.state = 1700
                    self.arguments()


                self.state = 1703
                self.match(PsithonParser.RPAR)


            self.state = 1706
            self.match(PsithonParser.COLON)
            self.state = 1707
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_defContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def decorators(self):
            return self.getTypedRuleContext(PsithonParser.DecoratorsContext,0)


        def function_def_raw(self):
            return self.getTypedRuleContext(PsithonParser.Function_def_rawContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_function_def




    def function_def(self):

        localctx = PsithonParser.Function_defContext(self, self._ctx, self.state)
        self.enterRule(localctx, 228, self.RULE_function_def)
        try:
            self.state = 1713
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [62]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1709
                self.decorators()
                self.state = 1710
                self.function_def_raw()
                pass
            elif token in [89, 98]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1712
                self.function_def_raw()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_def_rawContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DEF(self):
            return self.getToken(PsithonParser.DEF, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def type_params(self):
            return self.getTypedRuleContext(PsithonParser.Type_paramsContext,0)


        def params(self):
            return self.getTypedRuleContext(PsithonParser.ParamsContext,0)


        def RARROW(self):
            return self.getToken(PsithonParser.RARROW, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def func_type_comment(self):
            return self.getTypedRuleContext(PsithonParser.Func_type_commentContext,0)


        def ASYNC(self):
            return self.getToken(PsithonParser.ASYNC, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_function_def_raw




    def function_def_raw(self):

        localctx = PsithonParser.Function_def_rawContext(self, self._ctx, self.state)
        self.enterRule(localctx, 230, self.RULE_function_def_raw)
        self._la = 0 # Token type
        try:
            self.state = 1756
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [89]:
                self.enterOuterAlt(localctx, 1)
                self.state = 1715
                self.match(PsithonParser.DEF)
                self.state = 1716
                self.name()
                self.state = 1718
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==21:
                    self.state = 1717
                    self.type_params()


                self.state = 1720
                self.match(PsithonParser.LPAR)
                self.state = 1722
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 281479272202240) != 0) or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1721
                    self.params()


                self.state = 1724
                self.match(PsithonParser.RPAR)
                self.state = 1727
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==64:
                    self.state = 1725
                    self.match(PsithonParser.RARROW)
                    self.state = 1726
                    self.expression()


                self.state = 1729
                self.match(PsithonParser.COLON)
                self.state = 1731
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,192,self._ctx)
                if la_ == 1:
                    self.state = 1730
                    self.func_type_comment()


                self.state = 1733
                self.block()
                pass
            elif token in [98]:
                self.enterOuterAlt(localctx, 2)
                self.state = 1735
                self.match(PsithonParser.ASYNC)
                self.state = 1736
                self.match(PsithonParser.DEF)
                self.state = 1737
                self.name()
                self.state = 1739
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==21:
                    self.state = 1738
                    self.type_params()


                self.state = 1741
                self.match(PsithonParser.LPAR)
                self.state = 1743
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 281479272202240) != 0) or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1742
                    self.params()


                self.state = 1745
                self.match(PsithonParser.RPAR)
                self.state = 1748
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==64:
                    self.state = 1746
                    self.match(PsithonParser.RARROW)
                    self.state = 1747
                    self.expression()


                self.state = 1750
                self.match(PsithonParser.COLON)
                self.state = 1752
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,196,self._ctx)
                if la_ == 1:
                    self.state = 1751
                    self.func_type_comment()


                self.state = 1754
                self.block()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParamsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameters(self):
            return self.getTypedRuleContext(PsithonParser.ParametersContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_params




    def params(self):

        localctx = PsithonParser.ParamsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 232, self.RULE_params)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1758
            self.parameters()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParametersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def slash_no_default(self):
            return self.getTypedRuleContext(PsithonParser.Slash_no_defaultContext,0)


        def param_no_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Param_no_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Param_no_defaultContext,i)


        def param_with_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Param_with_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Param_with_defaultContext,i)


        def star_etc(self):
            return self.getTypedRuleContext(PsithonParser.Star_etcContext,0)


        def slash_with_default(self):
            return self.getTypedRuleContext(PsithonParser.Slash_with_defaultContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_parameters




    def parameters(self):

        localctx = PsithonParser.ParametersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 234, self.RULE_parameters)
        self._la = 0 # Token type
        try:
            self.state = 1809
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,208,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1760
                self.slash_no_default()
                self.state = 1764
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,198,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 1761
                        self.param_no_default() 
                    self.state = 1766
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,198,self._ctx)

                self.state = 1770
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1767
                    self.param_with_default()
                    self.state = 1772
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1774
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 1773
                    self.star_etc()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1776
                self.slash_with_default()
                self.state = 1780
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1777
                    self.param_with_default()
                    self.state = 1782
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1784
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 1783
                    self.star_etc()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1787 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 1786
                        self.param_no_default()

                    else:
                        raise NoViableAltException(self)
                    self.state = 1789 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,203,self._ctx)

                self.state = 1794
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1791
                    self.param_with_default()
                    self.state = 1796
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1798
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 1797
                    self.star_etc()


                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1801 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 1800
                    self.param_with_default()
                    self.state = 1803 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                        break

                self.state = 1806
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 1805
                    self.star_etc()


                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 1808
                self.star_etc()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_etcContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def param_no_default(self):
            return self.getTypedRuleContext(PsithonParser.Param_no_defaultContext,0)


        def param_maybe_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Param_maybe_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Param_maybe_defaultContext,i)


        def kwds(self):
            return self.getTypedRuleContext(PsithonParser.KwdsContext,0)


        def param_no_default_star_annotation(self):
            return self.getTypedRuleContext(PsithonParser.Param_no_default_star_annotationContext,0)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_star_etc




    def star_etc(self):

        localctx = PsithonParser.Star_etcContext(self, self._ctx, self.state)
        self.enterRule(localctx, 236, self.RULE_star_etc)
        self._la = 0 # Token type
        try:
            self.state = 1844
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,215,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1811
                self.match(PsithonParser.STAR)
                self.state = 1812
                self.param_no_default()
                self.state = 1816
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1813
                    self.param_maybe_default()
                    self.state = 1818
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1820
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==48:
                    self.state = 1819
                    self.kwds()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1822
                self.match(PsithonParser.STAR)
                self.state = 1823
                self.param_no_default_star_annotation()
                self.state = 1827
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 1824
                    self.param_maybe_default()
                    self.state = 1829
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 1831
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==48:
                    self.state = 1830
                    self.kwds()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1833
                self.match(PsithonParser.STAR)
                self.state = 1834
                self.match(PsithonParser.COMMA)
                self.state = 1836 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 1835
                    self.param_maybe_default()
                    self.state = 1838 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                        break

                self.state = 1841
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==48:
                    self.state = 1840
                    self.kwds()


                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 1843
                self.kwds()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class KwdsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def param_no_default(self):
            return self.getTypedRuleContext(PsithonParser.Param_no_defaultContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_kwds




    def kwds(self):

        localctx = PsithonParser.KwdsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 238, self.RULE_kwds)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1846
            self.match(PsithonParser.DOUBLESTAR)
            self.state = 1847
            self.param_no_default()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParamContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def annotation(self):
            return self.getTypedRuleContext(PsithonParser.AnnotationContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_param




    def param(self):

        localctx = PsithonParser.ParamContext(self, self._ctx, self.state)
        self.enterRule(localctx, 240, self.RULE_param)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1849
            self.name()
            self.state = 1851
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,216,self._ctx)
            if la_ == 1:
                self.state = 1850
                self.annotation()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Param_star_annotationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def star_annotation(self):
            return self.getTypedRuleContext(PsithonParser.Star_annotationContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_param_star_annotation




    def param_star_annotation(self):

        localctx = PsithonParser.Param_star_annotationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 242, self.RULE_param_star_annotation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1853
            self.name()
            self.state = 1854
            self.star_annotation()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AnnotationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_annotation




    def annotation(self):

        localctx = PsithonParser.AnnotationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 244, self.RULE_annotation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1856
            self.match(PsithonParser.COLON)
            self.state = 1857
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_annotationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def star_expression(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_star_annotation




    def star_annotation(self):

        localctx = PsithonParser.Star_annotationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 246, self.RULE_star_annotation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1859
            self.match(PsithonParser.COLON)
            self.state = 1860
            self.star_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Default_assignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_default_assignment




    def default_assignment(self):

        localctx = PsithonParser.Default_assignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 248, self.RULE_default_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1862
            self.match(PsithonParser.EQUAL)
            self.state = 1863
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class If_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(PsithonParser.IF, 0)

        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def elif_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Elif_stmtContext,0)


        def else_block(self):
            return self.getTypedRuleContext(PsithonParser.Else_blockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_if_stmt




    def if_stmt(self):

        localctx = PsithonParser.If_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 250, self.RULE_if_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1865
            self.match(PsithonParser.IF)
            self.state = 1866
            self.named_expression()
            self.state = 1867
            self.match(PsithonParser.COLON)
            self.state = 1868
            self.block()
            self.state = 1873
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,218,self._ctx)
            if la_ == 1:
                self.state = 1869
                self.elif_stmt()
                pass

            elif la_ == 2:
                self.state = 1871
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,217,self._ctx)
                if la_ == 1:
                    self.state = 1870
                    self.else_block()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Elif_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ELIF(self):
            return self.getToken(PsithonParser.ELIF, 0)

        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def elif_stmt(self):
            return self.getTypedRuleContext(PsithonParser.Elif_stmtContext,0)


        def else_block(self):
            return self.getTypedRuleContext(PsithonParser.Else_blockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_elif_stmt




    def elif_stmt(self):

        localctx = PsithonParser.Elif_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 252, self.RULE_elif_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1875
            self.match(PsithonParser.ELIF)
            self.state = 1876
            self.named_expression()
            self.state = 1877
            self.match(PsithonParser.COLON)
            self.state = 1878
            self.block()
            self.state = 1883
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,220,self._ctx)
            if la_ == 1:
                self.state = 1879
                self.elif_stmt()
                pass

            elif la_ == 2:
                self.state = 1881
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,219,self._ctx)
                if la_ == 1:
                    self.state = 1880
                    self.else_block()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Else_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ELSE(self):
            return self.getToken(PsithonParser.ELSE, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_else_block




    def else_block(self):

        localctx = PsithonParser.Else_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 254, self.RULE_else_block)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1885
            self.match(PsithonParser.ELSE)
            self.state = 1886
            self.match(PsithonParser.COLON)
            self.state = 1887
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class While_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHILE(self):
            return self.getToken(PsithonParser.WHILE, 0)

        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def else_block(self):
            return self.getTypedRuleContext(PsithonParser.Else_blockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_while_stmt




    def while_stmt(self):

        localctx = PsithonParser.While_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 256, self.RULE_while_stmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1889
            self.match(PsithonParser.WHILE)
            self.state = 1890
            self.named_expression()
            self.state = 1891
            self.match(PsithonParser.COLON)
            self.state = 1892
            self.block()
            self.state = 1894
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,221,self._ctx)
            if la_ == 1:
                self.state = 1893
                self.else_block()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class With_itemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def AS(self):
            return self.getToken(PsithonParser.AS, 0)

        def star_target(self):
            return self.getTypedRuleContext(PsithonParser.Star_targetContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_with_item




    def with_item(self):

        localctx = PsithonParser.With_itemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 258, self.RULE_with_item)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1896
            self.expression()
            self.state = 1899
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==88:
                self.state = 1897
                self.match(PsithonParser.AS)
                self.state = 1898
                self.star_target()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Try_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TRY(self):
            return self.getToken(PsithonParser.TRY, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def finally_block(self):
            return self.getTypedRuleContext(PsithonParser.Finally_blockContext,0)


        def except_block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Except_blockContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Except_blockContext,i)


        def else_block(self):
            return self.getTypedRuleContext(PsithonParser.Else_blockContext,0)


        def except_star_block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Except_star_blockContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Except_star_blockContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_try_stmt




    def try_stmt(self):

        localctx = PsithonParser.Try_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 260, self.RULE_try_stmt)
        try:
            self.state = 1934
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,229,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1901
                self.match(PsithonParser.TRY)
                self.state = 1902
                self.match(PsithonParser.COLON)
                self.state = 1903
                self.block()
                self.state = 1904
                self.finally_block()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1906
                self.match(PsithonParser.TRY)
                self.state = 1907
                self.match(PsithonParser.COLON)
                self.state = 1908
                self.block()
                self.state = 1910 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 1909
                        self.except_block()

                    else:
                        raise NoViableAltException(self)
                    self.state = 1912 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,223,self._ctx)

                self.state = 1915
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,224,self._ctx)
                if la_ == 1:
                    self.state = 1914
                    self.else_block()


                self.state = 1918
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,225,self._ctx)
                if la_ == 1:
                    self.state = 1917
                    self.finally_block()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 1920
                self.match(PsithonParser.TRY)
                self.state = 1921
                self.match(PsithonParser.COLON)
                self.state = 1922
                self.block()
                self.state = 1924 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 1923
                        self.except_star_block()

                    else:
                        raise NoViableAltException(self)
                    self.state = 1926 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,226,self._ctx)

                self.state = 1929
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,227,self._ctx)
                if la_ == 1:
                    self.state = 1928
                    self.else_block()


                self.state = 1932
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,228,self._ctx)
                if la_ == 1:
                    self.state = 1931
                    self.finally_block()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Except_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXCEPT(self):
            return self.getToken(PsithonParser.EXCEPT, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def expressions(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionsContext,0)


        def AS(self):
            return self.getToken(PsithonParser.AS, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_except_block




    def except_block(self):

        localctx = PsithonParser.Except_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 262, self.RULE_except_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1936
            self.match(PsithonParser.EXCEPT)
            self.state = 1943
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,231,self._ctx)
            if la_ == 1:
                self.state = 1937
                self.expression()
                self.state = 1940
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==88:
                    self.state = 1938
                    self.match(PsithonParser.AS)
                    self.state = 1939
                    self.name()



            elif la_ == 2:
                self.state = 1942
                self.expressions()


            self.state = 1945
            self.match(PsithonParser.COLON)
            self.state = 1946
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Except_star_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXCEPT(self):
            return self.getToken(PsithonParser.EXCEPT, 0)

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def expressions(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionsContext,0)


        def AS(self):
            return self.getToken(PsithonParser.AS, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_except_star_block




    def except_star_block(self):

        localctx = PsithonParser.Except_star_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 264, self.RULE_except_star_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1948
            self.match(PsithonParser.EXCEPT)
            self.state = 1949
            self.match(PsithonParser.STAR)
            self.state = 1956
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,233,self._ctx)
            if la_ == 1:
                self.state = 1950
                self.expression()
                self.state = 1953
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==88:
                    self.state = 1951
                    self.match(PsithonParser.AS)
                    self.state = 1952
                    self.name()


                pass

            elif la_ == 2:
                self.state = 1955
                self.expressions()
                pass


            self.state = 1958
            self.match(PsithonParser.COLON)
            self.state = 1959
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Finally_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FINALLY(self):
            return self.getToken(PsithonParser.FINALLY, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_finally_block




    def finally_block(self):

        localctx = PsithonParser.Finally_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 266, self.RULE_finally_block)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1961
            self.match(PsithonParser.FINALLY)
            self.state = 1962
            self.match(PsithonParser.COLON)
            self.state = 1963
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Match_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME_OR_MATCH(self):
            return self.getToken(PsithonParser.NAME_OR_MATCH, 0)

        def subject_expr(self):
            return self.getTypedRuleContext(PsithonParser.Subject_exprContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def INDENT(self):
            return self.getToken(PsithonParser.INDENT, 0)

        def DEDENT(self):
            return self.getToken(PsithonParser.DEDENT, 0)

        def case_block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Case_blockContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Case_blockContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_match_stmt




    def match_stmt(self):

        localctx = PsithonParser.Match_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 268, self.RULE_match_stmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1965
            self.match(PsithonParser.NAME_OR_MATCH)
            self.state = 1966
            self.subject_expr()
            self.state = 1967
            self.match(PsithonParser.COLON)
            self.state = 1968
            self.match(PsithonParser.NEWLINE)
            self.state = 1969
            self.match(PsithonParser.INDENT)
            self.state = 1971 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 1970
                self.case_block()
                self.state = 1973 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==105):
                    break

            self.state = 1975
            self.match(PsithonParser.DEDENT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Subject_exprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionContext,0)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def star_named_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionsContext,0)


        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_subject_expr




    def subject_expr(self):

        localctx = PsithonParser.Subject_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 270, self.RULE_subject_expr)
        try:
            self.state = 1983
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,236,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1977
                self.star_named_expression()
                self.state = 1978
                self.match(PsithonParser.COMMA)
                self.state = 1980
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,235,self._ctx)
                if la_ == 1:
                    self.state = 1979
                    self.star_named_expressions()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1982
                self.named_expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Case_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME_OR_CASE(self):
            return self.getToken(PsithonParser.NAME_OR_CASE, 0)

        def patterns(self):
            return self.getTypedRuleContext(PsithonParser.PatternsContext,0)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def block(self):
            return self.getTypedRuleContext(PsithonParser.BlockContext,0)


        def guard(self):
            return self.getTypedRuleContext(PsithonParser.GuardContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_case_block




    def case_block(self):

        localctx = PsithonParser.Case_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 272, self.RULE_case_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1985
            self.match(PsithonParser.NAME_OR_CASE)
            self.state = 1986
            self.patterns()
            self.state = 1988
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==100:
                self.state = 1987
                self.guard()


            self.state = 1990
            self.match(PsithonParser.COLON)
            self.state = 1991
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GuardContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(PsithonParser.IF, 0)

        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_guard




    def guard(self):

        localctx = PsithonParser.GuardContext(self, self._ctx, self.state)
        self.enterRule(localctx, 274, self.RULE_guard)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 1993
            self.match(PsithonParser.IF)
            self.state = 1994
            self.named_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PatternsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def open_sequence_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Open_sequence_patternContext,0)


        def pattern(self):
            return self.getTypedRuleContext(PsithonParser.PatternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_patterns




    def patterns(self):

        localctx = PsithonParser.PatternsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 276, self.RULE_patterns)
        try:
            self.state = 1998
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,238,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 1996
                self.open_sequence_pattern()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 1997
                self.pattern()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PatternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def as_pattern(self):
            return self.getTypedRuleContext(PsithonParser.As_patternContext,0)


        def or_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Or_patternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_pattern




    def pattern(self):

        localctx = PsithonParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 278, self.RULE_pattern)
        try:
            self.state = 2002
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,239,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2000
                self.as_pattern()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2001
                self.or_pattern()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class As_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def or_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Or_patternContext,0)


        def AS(self):
            return self.getToken(PsithonParser.AS, 0)

        def pattern_capture_target(self):
            return self.getTypedRuleContext(PsithonParser.Pattern_capture_targetContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_as_pattern




    def as_pattern(self):

        localctx = PsithonParser.As_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 280, self.RULE_as_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2004
            self.or_pattern()
            self.state = 2005
            self.match(PsithonParser.AS)
            self.state = 2006
            self.pattern_capture_target()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Or_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def closed_pattern(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Closed_patternContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Closed_patternContext,i)


        def VBAR(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.VBAR)
            else:
                return self.getToken(PsithonParser.VBAR, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_or_pattern




    def or_pattern(self):

        localctx = PsithonParser.Or_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 282, self.RULE_or_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2008
            self.closed_pattern()
            self.state = 2013
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==34:
                self.state = 2009
                self.match(PsithonParser.VBAR)
                self.state = 2010
                self.closed_pattern()
                self.state = 2015
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Closed_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Literal_patternContext,0)


        def capture_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Capture_patternContext,0)


        def wildcard_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Wildcard_patternContext,0)


        def value_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Value_patternContext,0)


        def group_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Group_patternContext,0)


        def sequence_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Sequence_patternContext,0)


        def mapping_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Mapping_patternContext,0)


        def class_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Class_patternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_closed_pattern




    def closed_pattern(self):

        localctx = PsithonParser.Closed_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 284, self.RULE_closed_pattern)
        try:
            self.state = 2024
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,241,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2016
                self.literal_pattern()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2017
                self.capture_pattern()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2018
                self.wildcard_pattern()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2019
                self.value_pattern()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 2020
                self.group_pattern()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 2021
                self.sequence_pattern()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 2022
                self.mapping_pattern()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 2023
                self.class_pattern()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Literal_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def signed_number(self):
            return self.getTypedRuleContext(PsithonParser.Signed_numberContext,0)


        def complex_number(self):
            return self.getTypedRuleContext(PsithonParser.Complex_numberContext,0)


        def strings(self):
            return self.getTypedRuleContext(PsithonParser.StringsContext,0)


        def NONE(self):
            return self.getToken(PsithonParser.NONE, 0)

        def TRUE(self):
            return self.getToken(PsithonParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(PsithonParser.FALSE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_literal_pattern




    def literal_pattern(self):

        localctx = PsithonParser.Literal_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 286, self.RULE_literal_pattern)
        try:
            self.state = 2032
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,242,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2026
                self.signed_number()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2027
                self.complex_number()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2028
                self.strings()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2029
                self.match(PsithonParser.NONE)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 2030
                self.match(PsithonParser.TRUE)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 2031
                self.match(PsithonParser.FALSE)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Literal_exprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def signed_number(self):
            return self.getTypedRuleContext(PsithonParser.Signed_numberContext,0)


        def complex_number(self):
            return self.getTypedRuleContext(PsithonParser.Complex_numberContext,0)


        def strings(self):
            return self.getTypedRuleContext(PsithonParser.StringsContext,0)


        def NONE(self):
            return self.getToken(PsithonParser.NONE, 0)

        def TRUE(self):
            return self.getToken(PsithonParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(PsithonParser.FALSE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_literal_expr




    def literal_expr(self):

        localctx = PsithonParser.Literal_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 288, self.RULE_literal_expr)
        try:
            self.state = 2040
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,243,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2034
                self.signed_number()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2035
                self.complex_number()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2036
                self.strings()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2037
                self.match(PsithonParser.NONE)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 2038
                self.match(PsithonParser.TRUE)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 2039
                self.match(PsithonParser.FALSE)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Complex_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def signed_real_number(self):
            return self.getTypedRuleContext(PsithonParser.Signed_real_numberContext,0)


        def imaginary_number(self):
            return self.getTypedRuleContext(PsithonParser.Imaginary_numberContext,0)


        def PLUS(self):
            return self.getToken(PsithonParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(PsithonParser.MINUS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_complex_number




    def complex_number(self):

        localctx = PsithonParser.Complex_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 290, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2042
            self.signed_real_number()
            self.state = 2043
            _la = self._input.LA(1)
            if not(_la==30 or _la==31):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 2044
            self.imaginary_number()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Signed_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(PsithonParser.NUMBER, 0)

        def MINUS(self):
            return self.getToken(PsithonParser.MINUS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_signed_number




    def signed_number(self):

        localctx = PsithonParser.Signed_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 292, self.RULE_signed_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2047
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==31:
                self.state = 2046
                self.match(PsithonParser.MINUS)


            self.state = 2049
            self.match(PsithonParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Signed_real_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def real_number(self):
            return self.getTypedRuleContext(PsithonParser.Real_numberContext,0)


        def MINUS(self):
            return self.getToken(PsithonParser.MINUS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_signed_real_number




    def signed_real_number(self):

        localctx = PsithonParser.Signed_real_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 294, self.RULE_signed_real_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2052
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==31:
                self.state = 2051
                self.match(PsithonParser.MINUS)


            self.state = 2054
            self.real_number()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Real_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(PsithonParser.NUMBER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_real_number




    def real_number(self):

        localctx = PsithonParser.Real_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 296, self.RULE_real_number)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2056
            self.match(PsithonParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Imaginary_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(PsithonParser.NUMBER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_imaginary_number




    def imaginary_number(self):

        localctx = PsithonParser.Imaginary_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 298, self.RULE_imaginary_number)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2058
            self.match(PsithonParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Capture_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pattern_capture_target(self):
            return self.getTypedRuleContext(PsithonParser.Pattern_capture_targetContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_capture_pattern




    def capture_pattern(self):

        localctx = PsithonParser.Capture_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 300, self.RULE_capture_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2060
            self.pattern_capture_target()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pattern_capture_targetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name_except_underscore(self):
            return self.getTypedRuleContext(PsithonParser.Name_except_underscoreContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_pattern_capture_target




    def pattern_capture_target(self):

        localctx = PsithonParser.Pattern_capture_targetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 302, self.RULE_pattern_capture_target)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2062
            self.name_except_underscore()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Wildcard_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME_OR_WILDCARD(self):
            return self.getToken(PsithonParser.NAME_OR_WILDCARD, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_wildcard_pattern




    def wildcard_pattern(self):

        localctx = PsithonParser.Wildcard_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 304, self.RULE_wildcard_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2064
            self.match(PsithonParser.NAME_OR_WILDCARD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Value_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attr(self):
            return self.getTypedRuleContext(PsithonParser.AttrContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_value_pattern




    def value_pattern(self):

        localctx = PsithonParser.Value_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 306, self.RULE_value_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2066
            self.attr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.NameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.NameContext,i)


        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.DOT)
            else:
                return self.getToken(PsithonParser.DOT, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_attr




    def attr(self):

        localctx = PsithonParser.AttrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 308, self.RULE_attr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2068
            self.name()
            self.state = 2071 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 2069
                self.match(PsithonParser.DOT)
                self.state = 2070
                self.name()
                self.state = 2073 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==26):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Name_or_attrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.NameContext)
            else:
                return self.getTypedRuleContext(PsithonParser.NameContext,i)


        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.DOT)
            else:
                return self.getToken(PsithonParser.DOT, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_name_or_attr




    def name_or_attr(self):

        localctx = PsithonParser.Name_or_attrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 310, self.RULE_name_or_attr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2075
            self.name()
            self.state = 2080
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==26:
                self.state = 2076
                self.match(PsithonParser.DOT)
                self.state = 2077
                self.name()
                self.state = 2082
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Group_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def pattern(self):
            return self.getTypedRuleContext(PsithonParser.PatternContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_group_pattern




    def group_pattern(self):

        localctx = PsithonParser.Group_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 312, self.RULE_group_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2083
            self.match(PsithonParser.LPAR)
            self.state = 2084
            self.pattern()
            self.state = 2085
            self.match(PsithonParser.RPAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Sequence_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def maybe_sequence_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Maybe_sequence_patternContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def open_sequence_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Open_sequence_patternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_sequence_pattern




    def sequence_pattern(self):

        localctx = PsithonParser.Sequence_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 314, self.RULE_sequence_pattern)
        self._la = 0 # Token type
        try:
            self.state = 2097
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [21]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2087
                self.match(PsithonParser.LSQB)
                self.state = 2089
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 6450315552) != 0) or ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 4363686773793) != 0):
                    self.state = 2088
                    self.maybe_sequence_pattern()


                self.state = 2091
                self.match(PsithonParser.RSQB)
                pass
            elif token in [20]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2092
                self.match(PsithonParser.LPAR)
                self.state = 2094
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 6450315552) != 0) or ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 4363686773793) != 0):
                    self.state = 2093
                    self.open_sequence_pattern()


                self.state = 2096
                self.match(PsithonParser.RPAR)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Open_sequence_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def maybe_star_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Maybe_star_patternContext,0)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def maybe_sequence_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Maybe_sequence_patternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_open_sequence_pattern




    def open_sequence_pattern(self):

        localctx = PsithonParser.Open_sequence_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 316, self.RULE_open_sequence_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2099
            self.maybe_star_pattern()
            self.state = 2100
            self.match(PsithonParser.COMMA)
            self.state = 2102
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 6450315552) != 0) or ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 4363686773793) != 0):
                self.state = 2101
                self.maybe_sequence_pattern()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Maybe_sequence_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def maybe_star_pattern(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Maybe_star_patternContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Maybe_star_patternContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_maybe_sequence_pattern




    def maybe_sequence_pattern(self):

        localctx = PsithonParser.Maybe_sequence_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 318, self.RULE_maybe_sequence_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2104
            self.maybe_star_pattern()
            self.state = 2109
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,252,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2105
                    self.match(PsithonParser.COMMA)
                    self.state = 2106
                    self.maybe_star_pattern() 
                self.state = 2111
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,252,self._ctx)

            self.state = 2113
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2112
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Maybe_star_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Star_patternContext,0)


        def pattern(self):
            return self.getTypedRuleContext(PsithonParser.PatternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_maybe_star_pattern




    def maybe_star_pattern(self):

        localctx = PsithonParser.Maybe_star_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 320, self.RULE_maybe_star_pattern)
        try:
            self.state = 2117
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [32]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2115
                self.star_pattern()
                pass
            elif token in [5, 8, 19, 20, 21, 22, 31, 68, 73, 78, 103, 104, 105, 106, 107, 108, 109]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2116
                self.pattern()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_star_pattern




    def star_pattern(self):

        localctx = PsithonParser.Star_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 322, self.RULE_star_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2119
            self.match(PsithonParser.STAR)
            self.state = 2120
            self.name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Mapping_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def double_star_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Double_star_patternContext,0)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def items_pattern(self):
            return self.getTypedRuleContext(PsithonParser.Items_patternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_mapping_pattern




    def mapping_pattern(self):

        localctx = PsithonParser.Mapping_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 324, self.RULE_mapping_pattern)
        self._la = 0 # Token type
        try:
            self.state = 2142
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,258,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2122
                self.match(PsithonParser.LBRACE)
                self.state = 2123
                self.match(PsithonParser.RBRACE)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2124
                self.match(PsithonParser.LBRACE)
                self.state = 2125
                self.double_star_pattern()
                self.state = 2127
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 2126
                    self.match(PsithonParser.COMMA)


                self.state = 2129
                self.match(PsithonParser.RBRACE)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2131
                self.match(PsithonParser.LBRACE)
                self.state = 2132
                self.items_pattern()
                self.state = 2135
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,256,self._ctx)
                if la_ == 1:
                    self.state = 2133
                    self.match(PsithonParser.COMMA)
                    self.state = 2134
                    self.double_star_pattern()


                self.state = 2138
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 2137
                    self.match(PsithonParser.COMMA)


                self.state = 2140
                self.match(PsithonParser.RBRACE)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Items_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def key_value_pattern(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Key_value_patternContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Key_value_patternContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_items_pattern




    def items_pattern(self):

        localctx = PsithonParser.Items_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 326, self.RULE_items_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2144
            self.key_value_pattern()
            self.state = 2149
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,259,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2145
                    self.match(PsithonParser.COMMA)
                    self.state = 2146
                    self.key_value_pattern() 
                self.state = 2151
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,259,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Key_value_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def pattern(self):
            return self.getTypedRuleContext(PsithonParser.PatternContext,0)


        def literal_expr(self):
            return self.getTypedRuleContext(PsithonParser.Literal_exprContext,0)


        def attr(self):
            return self.getTypedRuleContext(PsithonParser.AttrContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_key_value_pattern




    def key_value_pattern(self):

        localctx = PsithonParser.Key_value_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 328, self.RULE_key_value_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2154
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5, 8, 31, 68, 73, 78, 108, 109]:
                self.state = 2152
                self.literal_expr()
                pass
            elif token in [19, 103, 104, 105, 106, 107]:
                self.state = 2153
                self.attr()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 2156
            self.match(PsithonParser.COLON)
            self.state = 2157
            self.pattern()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Double_star_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def pattern_capture_target(self):
            return self.getTypedRuleContext(PsithonParser.Pattern_capture_targetContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_double_star_pattern




    def double_star_pattern(self):

        localctx = PsithonParser.Double_star_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 330, self.RULE_double_star_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2159
            self.match(PsithonParser.DOUBLESTAR)
            self.state = 2160
            self.pattern_capture_target()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Class_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name_or_attr(self):
            return self.getTypedRuleContext(PsithonParser.Name_or_attrContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def positional_patterns(self):
            return self.getTypedRuleContext(PsithonParser.Positional_patternsContext,0)


        def keyword_patterns(self):
            return self.getTypedRuleContext(PsithonParser.Keyword_patternsContext,0)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_class_pattern




    def class_pattern(self):

        localctx = PsithonParser.Class_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 332, self.RULE_class_pattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2162
            self.name_or_attr()
            self.state = 2163
            self.match(PsithonParser.LPAR)
            self.state = 2175
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 2155348256) != 0) or ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 4363686773793) != 0):
                self.state = 2170
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,262,self._ctx)
                if la_ == 1:
                    self.state = 2164
                    self.positional_patterns()
                    self.state = 2167
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,261,self._ctx)
                    if la_ == 1:
                        self.state = 2165
                        self.match(PsithonParser.COMMA)
                        self.state = 2166
                        self.keyword_patterns()


                    pass

                elif la_ == 2:
                    self.state = 2169
                    self.keyword_patterns()
                    pass


                self.state = 2173
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 2172
                    self.match(PsithonParser.COMMA)




            self.state = 2177
            self.match(PsithonParser.RPAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Positional_patternsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pattern(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.PatternContext)
            else:
                return self.getTypedRuleContext(PsithonParser.PatternContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_positional_patterns




    def positional_patterns(self):

        localctx = PsithonParser.Positional_patternsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 334, self.RULE_positional_patterns)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2179
            self.pattern()
            self.state = 2184
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,265,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2180
                    self.match(PsithonParser.COMMA)
                    self.state = 2181
                    self.pattern() 
                self.state = 2186
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,265,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Keyword_patternsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def keyword_pattern(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Keyword_patternContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Keyword_patternContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_keyword_patterns




    def keyword_patterns(self):

        localctx = PsithonParser.Keyword_patternsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 336, self.RULE_keyword_patterns)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2187
            self.keyword_pattern()
            self.state = 2192
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,266,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2188
                    self.match(PsithonParser.COMMA)
                    self.state = 2189
                    self.keyword_pattern() 
                self.state = 2194
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,266,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Keyword_patternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def pattern(self):
            return self.getTypedRuleContext(PsithonParser.PatternContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_keyword_pattern




    def keyword_pattern(self):

        localctx = PsithonParser.Keyword_patternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 338, self.RULE_keyword_pattern)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2195
            self.name()
            self.state = 2196
            self.match(PsithonParser.EQUAL)
            self.state = 2197
            self.pattern()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_aliasContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME_OR_TYPE(self):
            return self.getToken(PsithonParser.NAME_OR_TYPE, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def type_params(self):
            return self.getTypedRuleContext(PsithonParser.Type_paramsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_type_alias




    def type_alias(self):

        localctx = PsithonParser.Type_aliasContext(self, self._ctx, self.state)
        self.enterRule(localctx, 340, self.RULE_type_alias)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2199
            self.match(PsithonParser.NAME_OR_TYPE)
            self.state = 2200
            self.name()
            self.state = 2202
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==21:
                self.state = 2201
                self.type_params()


            self.state = 2204
            self.match(PsithonParser.EQUAL)
            self.state = 2205
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_paramsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def type_param_seq(self):
            return self.getTypedRuleContext(PsithonParser.Type_param_seqContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_type_params




    def type_params(self):

        localctx = PsithonParser.Type_paramsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 342, self.RULE_type_params)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2207
            self.match(PsithonParser.LSQB)
            self.state = 2208
            self.type_param_seq()
            self.state = 2209
            self.match(PsithonParser.RSQB)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_param_seqContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def type_param(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Type_paramContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Type_paramContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_type_param_seq




    def type_param_seq(self):

        localctx = PsithonParser.Type_param_seqContext(self, self._ctx, self.state)
        self.enterRule(localctx, 344, self.RULE_type_param_seq)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2211
            self.type_param()
            self.state = 2216
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,268,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2212
                    self.match(PsithonParser.COMMA)
                    self.state = 2213
                    self.type_param() 
                self.state = 2218
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,268,self._ctx)

            self.state = 2220
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2219
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_paramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def type_param_bound(self):
            return self.getTypedRuleContext(PsithonParser.Type_param_boundContext,0)


        def type_param_default(self):
            return self.getTypedRuleContext(PsithonParser.Type_param_defaultContext,0)


        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def type_param_starred_default(self):
            return self.getTypedRuleContext(PsithonParser.Type_param_starred_defaultContext,0)


        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_type_param




    def type_param(self):

        localctx = PsithonParser.Type_paramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 346, self.RULE_type_param)
        self._la = 0 # Token type
        try:
            self.state = 2239
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [19, 103, 104, 105, 106, 107]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2222
                self.name()
                self.state = 2224
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==27:
                    self.state = 2223
                    self.type_param_bound()


                self.state = 2227
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==38:
                    self.state = 2226
                    self.type_param_default()


                pass
            elif token in [32]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2229
                self.match(PsithonParser.STAR)
                self.state = 2230
                self.name()
                self.state = 2232
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==38:
                    self.state = 2231
                    self.type_param_starred_default()


                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 3)
                self.state = 2234
                self.match(PsithonParser.DOUBLESTAR)
                self.state = 2235
                self.name()
                self.state = 2237
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==38:
                    self.state = 2236
                    self.type_param_default()


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_param_boundContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_type_param_bound




    def type_param_bound(self):

        localctx = PsithonParser.Type_param_boundContext(self, self._ctx, self.state)
        self.enterRule(localctx, 348, self.RULE_type_param_bound)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2241
            self.match(PsithonParser.COLON)
            self.state = 2242
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_param_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_type_param_default




    def type_param_default(self):

        localctx = PsithonParser.Type_param_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 350, self.RULE_type_param_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2244
            self.match(PsithonParser.EQUAL)
            self.state = 2245
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_param_starred_defaultContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def star_expression(self):
            return self.getTypedRuleContext(PsithonParser.Star_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_type_param_starred_default




    def type_param_starred_default(self):

        localctx = PsithonParser.Type_param_starred_defaultContext(self, self._ctx, self.state)
        self.enterRule(localctx, 352, self.RULE_type_param_starred_default)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2247
            self.match(PsithonParser.EQUAL)
            self.state = 2248
            self.star_expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_expressions




    def expressions(self):

        localctx = PsithonParser.ExpressionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 354, self.RULE_expressions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2250
            self.expression()
            self.state = 2255
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,275,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2251
                    self.match(PsithonParser.COMMA)
                    self.state = 2252
                    self.expression() 
                self.state = 2257
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,275,self._ctx)

            self.state = 2259
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2258
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def disjunction(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.DisjunctionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.DisjunctionContext,i)


        def IF(self):
            return self.getToken(PsithonParser.IF, 0)

        def ELSE(self):
            return self.getToken(PsithonParser.ELSE, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def lambdef(self):
            return self.getTypedRuleContext(PsithonParser.LambdefContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_expression




    def expression(self):

        localctx = PsithonParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 356, self.RULE_expression)
        try:
            self.state = 2270
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,278,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2261
                self.disjunction()
                self.state = 2267
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,277,self._ctx)
                if la_ == 1:
                    self.state = 2262
                    self.match(PsithonParser.IF)
                    self.state = 2263
                    self.disjunction()
                    self.state = 2264
                    self.match(PsithonParser.ELSE)
                    self.state = 2265
                    self.expression()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2269
                self.lambdef()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_expressionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Star_expressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Star_expressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_star_expressions




    def star_expressions(self):

        localctx = PsithonParser.Star_expressionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 358, self.RULE_star_expressions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2272
            self.star_expression()
            self.state = 2277
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,279,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2273
                    self.match(PsithonParser.COMMA)
                    self.state = 2274
                    self.star_expression() 
                self.state = 2279
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,279,self._ctx)

            self.state = 2281
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2280
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_star_expression




    def star_expression(self):

        localctx = PsithonParser.Star_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 360, self.RULE_star_expression)
        try:
            self.state = 2286
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,281,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2283
                self.match(PsithonParser.STAR)
                self.state = 2284
                self.bitwise_or(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2285
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_named_expressionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_named_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Star_named_expressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Star_named_expressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_star_named_expressions




    def star_named_expressions(self):

        localctx = PsithonParser.Star_named_expressionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 362, self.RULE_star_named_expressions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2288
            self.star_named_expression()
            self.state = 2293
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,282,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2289
                    self.match(PsithonParser.COMMA)
                    self.state = 2290
                    self.star_named_expression() 
                self.state = 2295
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,282,self._ctx)

            self.state = 2297
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2296
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_named_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_star_named_expression




    def star_named_expression(self):

        localctx = PsithonParser.Star_named_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 364, self.RULE_star_named_expression)
        try:
            self.state = 2302
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,284,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2299
                self.match(PsithonParser.STAR)
                self.state = 2300
                self.bitwise_or(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2301
                self.named_expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Assignment_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def COLONEQUAL(self):
            return self.getToken(PsithonParser.COLONEQUAL, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_assignment_expression




    def assignment_expression(self):

        localctx = PsithonParser.Assignment_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 366, self.RULE_assignment_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2304
            self.name()
            self.state = 2305
            self.match(PsithonParser.COLONEQUAL)
            self.state = 2306
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Named_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignment_expression(self):
            return self.getTypedRuleContext(PsithonParser.Assignment_expressionContext,0)


        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_named_expression




    def named_expression(self):

        localctx = PsithonParser.Named_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 368, self.RULE_named_expression)
        try:
            self.state = 2310
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,285,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2308
                self.assignment_expression()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2309
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DisjunctionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conjunction(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ConjunctionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ConjunctionContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.OR)
            else:
                return self.getToken(PsithonParser.OR, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_disjunction




    def disjunction(self):

        localctx = PsithonParser.DisjunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 370, self.RULE_disjunction)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2312
            self.conjunction()
            self.state = 2317
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,286,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2313
                    self.match(PsithonParser.OR)
                    self.state = 2314
                    self.conjunction() 
                self.state = 2319
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,286,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConjunctionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def inversion(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.InversionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.InversionContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.AND)
            else:
                return self.getToken(PsithonParser.AND, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_conjunction




    def conjunction(self):

        localctx = PsithonParser.ConjunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 372, self.RULE_conjunction)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2320
            self.inversion()
            self.state = 2325
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,287,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2321
                    self.match(PsithonParser.AND)
                    self.state = 2322
                    self.inversion() 
                self.state = 2327
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,287,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InversionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(PsithonParser.NOT, 0)

        def inversion(self):
            return self.getTypedRuleContext(PsithonParser.InversionContext,0)


        def comparison(self):
            return self.getTypedRuleContext(PsithonParser.ComparisonContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_inversion




    def inversion(self):

        localctx = PsithonParser.InversionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 374, self.RULE_inversion)
        try:
            self.state = 2331
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,288,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2328
                self.match(PsithonParser.NOT)
                self.state = 2329
                self.inversion()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2330
                self.comparison()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparisonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def compare_op_bitwise_or_pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Compare_op_bitwise_or_pairContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Compare_op_bitwise_or_pairContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_comparison




    def comparison(self):

        localctx = PsithonParser.ComparisonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 376, self.RULE_comparison)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2333
            self.bitwise_or(0)
            self.state = 2337
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,289,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2334
                    self.compare_op_bitwise_or_pair() 
                self.state = 2339
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,289,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compare_op_bitwise_or_pairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def eq_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Eq_bitwise_orContext,0)


        def noteq_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Noteq_bitwise_orContext,0)


        def lte_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Lte_bitwise_orContext,0)


        def lt_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Lt_bitwise_orContext,0)


        def gte_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Gte_bitwise_orContext,0)


        def gt_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Gt_bitwise_orContext,0)


        def notin_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Notin_bitwise_orContext,0)


        def in_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.In_bitwise_orContext,0)


        def isnot_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Isnot_bitwise_orContext,0)


        def is_bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Is_bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_compare_op_bitwise_or_pair




    def compare_op_bitwise_or_pair(self):

        localctx = PsithonParser.Compare_op_bitwise_or_pairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 378, self.RULE_compare_op_bitwise_or_pair)
        try:
            self.state = 2350
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,290,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2340
                self.eq_bitwise_or()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2341
                self.noteq_bitwise_or()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2342
                self.lte_bitwise_or()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2343
                self.lt_bitwise_or()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 2344
                self.gte_bitwise_or()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 2345
                self.gt_bitwise_or()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 2346
                self.notin_bitwise_or()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 2347
                self.in_bitwise_or()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 2348
                self.isnot_bitwise_or()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 2349
                self.is_bitwise_or()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Eq_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EQEQUAL(self):
            return self.getToken(PsithonParser.EQEQUAL, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_eq_bitwise_or




    def eq_bitwise_or(self):

        localctx = PsithonParser.Eq_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 380, self.RULE_eq_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2352
            self.match(PsithonParser.EQEQUAL)
            self.state = 2353
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lte_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LESSEQUAL(self):
            return self.getToken(PsithonParser.LESSEQUAL, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lte_bitwise_or




    def lte_bitwise_or(self):

        localctx = PsithonParser.Lte_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 382, self.RULE_lte_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2355
            self.match(PsithonParser.LESSEQUAL)
            self.state = 2356
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lt_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LESS(self):
            return self.getToken(PsithonParser.LESS, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lt_bitwise_or




    def lt_bitwise_or(self):

        localctx = PsithonParser.Lt_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 384, self.RULE_lt_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2358
            self.match(PsithonParser.LESS)
            self.state = 2359
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Gte_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def GREATEREQUAL(self):
            return self.getToken(PsithonParser.GREATEREQUAL, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_gte_bitwise_or




    def gte_bitwise_or(self):

        localctx = PsithonParser.Gte_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 386, self.RULE_gte_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2361
            self.match(PsithonParser.GREATEREQUAL)
            self.state = 2362
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Gt_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def GREATER(self):
            return self.getToken(PsithonParser.GREATER, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_gt_bitwise_or




    def gt_bitwise_or(self):

        localctx = PsithonParser.Gt_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 388, self.RULE_gt_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2364
            self.match(PsithonParser.GREATER)
            self.state = 2365
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Notin_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(PsithonParser.NOT, 0)

        def IN(self):
            return self.getToken(PsithonParser.IN, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_notin_bitwise_or




    def notin_bitwise_or(self):

        localctx = PsithonParser.Notin_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 390, self.RULE_notin_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2367
            self.match(PsithonParser.NOT)
            self.state = 2368
            self.match(PsithonParser.IN)
            self.state = 2369
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class In_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IN(self):
            return self.getToken(PsithonParser.IN, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_in_bitwise_or




    def in_bitwise_or(self):

        localctx = PsithonParser.In_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 392, self.RULE_in_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2371
            self.match(PsithonParser.IN)
            self.state = 2372
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Isnot_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IS(self):
            return self.getToken(PsithonParser.IS, 0)

        def NOT(self):
            return self.getToken(PsithonParser.NOT, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_isnot_bitwise_or




    def isnot_bitwise_or(self):

        localctx = PsithonParser.Isnot_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 394, self.RULE_isnot_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2374
            self.match(PsithonParser.IS)
            self.state = 2375
            self.match(PsithonParser.NOT)
            self.state = 2376
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Is_bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IS(self):
            return self.getToken(PsithonParser.IS, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_is_bitwise_or




    def is_bitwise_or(self):

        localctx = PsithonParser.Is_bitwise_orContext(self, self._ctx, self.state)
        self.enterRule(localctx, 396, self.RULE_is_bitwise_or)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2378
            self.match(PsithonParser.IS)
            self.state = 2379
            self.bitwise_or(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Bitwise_orContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def bitwise_xor(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_xorContext,0)


        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def VBAR(self):
            return self.getToken(PsithonParser.VBAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_bitwise_or



    def bitwise_or(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.Bitwise_orContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 398
        self.enterRecursionRule(localctx, 398, self.RULE_bitwise_or, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2382
            self.bitwise_xor(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 2389
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,291,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.Bitwise_orContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_bitwise_or)
                    self.state = 2384
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2385
                    self.match(PsithonParser.VBAR)
                    self.state = 2386
                    self.bitwise_xor(0) 
                self.state = 2391
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,291,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class Bitwise_xorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def bitwise_and(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_andContext,0)


        def bitwise_xor(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_xorContext,0)


        def CIRCUMFLEX(self):
            return self.getToken(PsithonParser.CIRCUMFLEX, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_bitwise_xor



    def bitwise_xor(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.Bitwise_xorContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 400
        self.enterRecursionRule(localctx, 400, self.RULE_bitwise_xor, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2393
            self.bitwise_and(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 2400
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,292,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.Bitwise_xorContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_bitwise_xor)
                    self.state = 2395
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2396
                    self.match(PsithonParser.CIRCUMFLEX)
                    self.state = 2397
                    self.bitwise_and(0) 
                self.state = 2402
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,292,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class Bitwise_andContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def shift_expr(self):
            return self.getTypedRuleContext(PsithonParser.Shift_exprContext,0)


        def bitwise_and(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_andContext,0)


        def AMPER(self):
            return self.getToken(PsithonParser.AMPER, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_bitwise_and



    def bitwise_and(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.Bitwise_andContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 402
        self.enterRecursionRule(localctx, 402, self.RULE_bitwise_and, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2404
            self.shift_expr(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 2411
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,293,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.Bitwise_andContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_bitwise_and)
                    self.state = 2406
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2407
                    self.match(PsithonParser.AMPER)
                    self.state = 2408
                    self.shift_expr(0) 
                self.state = 2413
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,293,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class Shift_exprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def sum_(self):
            return self.getTypedRuleContext(PsithonParser.SumContext,0)


        def shift_expr(self):
            return self.getTypedRuleContext(PsithonParser.Shift_exprContext,0)


        def LEFTSHIFT(self):
            return self.getToken(PsithonParser.LEFTSHIFT, 0)

        def RIGHTSHIFT(self):
            return self.getToken(PsithonParser.RIGHTSHIFT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_shift_expr



    def shift_expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.Shift_exprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 404
        self.enterRecursionRule(localctx, 404, self.RULE_shift_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2415
            self.sum_(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 2422
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,294,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.Shift_exprContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_shift_expr)
                    self.state = 2417
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2418
                    _la = self._input.LA(1)
                    if not(_la==46 or _la==47):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 2419
                    self.sum_(0) 
                self.state = 2424
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,294,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class SumContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def term(self):
            return self.getTypedRuleContext(PsithonParser.TermContext,0)


        def sum_(self):
            return self.getTypedRuleContext(PsithonParser.SumContext,0)


        def PLUS(self):
            return self.getToken(PsithonParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(PsithonParser.MINUS, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_sum



    def sum_(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.SumContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 406
        self.enterRecursionRule(localctx, 406, self.RULE_sum, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2426
            self.term(0)
            self._ctx.stop = self._input.LT(-1)
            self.state = 2433
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,295,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.SumContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_sum)
                    self.state = 2428
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2429
                    _la = self._input.LA(1)
                    if not(_la==30 or _la==31):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 2430
                    self.term(0) 
                self.state = 2435
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,295,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class TermContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def factor(self):
            return self.getTypedRuleContext(PsithonParser.FactorContext,0)


        def term(self):
            return self.getTypedRuleContext(PsithonParser.TermContext,0)


        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def SLASH(self):
            return self.getToken(PsithonParser.SLASH, 0)

        def DOUBLESLASH(self):
            return self.getToken(PsithonParser.DOUBLESLASH, 0)

        def PERCENT(self):
            return self.getToken(PsithonParser.PERCENT, 0)

        def AT(self):
            return self.getToken(PsithonParser.AT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_term



    def term(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.TermContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 408
        self.enterRecursionRule(localctx, 408, self.RULE_term, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2437
            self.factor()
            self._ctx.stop = self._input.LT(-1)
            self.state = 2444
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,296,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.TermContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_term)
                    self.state = 2439
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2440
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 5764608085674950656) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 2441
                    self.factor() 
                self.state = 2446
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,296,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class FactorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PLUS(self):
            return self.getToken(PsithonParser.PLUS, 0)

        def factor(self):
            return self.getTypedRuleContext(PsithonParser.FactorContext,0)


        def MINUS(self):
            return self.getToken(PsithonParser.MINUS, 0)

        def TILDE(self):
            return self.getToken(PsithonParser.TILDE, 0)

        def power(self):
            return self.getTypedRuleContext(PsithonParser.PowerContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_factor




    def factor(self):

        localctx = PsithonParser.FactorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 410, self.RULE_factor)
        try:
            self.state = 2454
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,297,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2447
                self.match(PsithonParser.PLUS)
                self.state = 2448
                self.factor()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2449
                self.match(PsithonParser.MINUS)
                self.state = 2450
                self.factor()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2451
                self.match(PsithonParser.TILDE)
                self.state = 2452
                self.factor()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2453
                self.power()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PowerContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def await_primary(self):
            return self.getTypedRuleContext(PsithonParser.Await_primaryContext,0)


        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def factor(self):
            return self.getTypedRuleContext(PsithonParser.FactorContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_power




    def power(self):

        localctx = PsithonParser.PowerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 412, self.RULE_power)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2456
            self.await_primary()
            self.state = 2459
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,298,self._ctx)
            if la_ == 1:
                self.state = 2457
                self.match(PsithonParser.DOUBLESTAR)
                self.state = 2458
                self.factor()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrimaryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom(self):
            return self.getTypedRuleContext(PsithonParser.AtomContext,0)


        def primary(self):
            return self.getTypedRuleContext(PsithonParser.PrimaryContext,0)


        def DOT(self):
            return self.getToken(PsithonParser.DOT, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def genexp(self):
            return self.getTypedRuleContext(PsithonParser.GenexpContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def slices(self):
            return self.getTypedRuleContext(PsithonParser.SlicesContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def arguments(self):
            return self.getTypedRuleContext(PsithonParser.ArgumentsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_primary



    def primary(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.PrimaryContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 414
        self.enterRecursionRule(localctx, 414, self.RULE_primary, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2462
            self.atom()
            self._ctx.stop = self._input.LT(-1)
            self.state = 2481
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,301,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.PrimaryContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_primary)
                    self.state = 2464
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2477
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,300,self._ctx)
                    if la_ == 1:
                        self.state = 2465
                        self.match(PsithonParser.DOT)
                        self.state = 2466
                        self.name()
                        pass

                    elif la_ == 2:
                        self.state = 2467
                        self.genexp()
                        pass

                    elif la_ == 3:
                        self.state = 2468
                        self.match(PsithonParser.LPAR)
                        self.state = 2470
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,299,self._ctx)
                        if la_ == 1:
                            self.state = 2469
                            self.arguments()


                        self.state = 2472
                        self.match(PsithonParser.RPAR)
                        pass

                    elif la_ == 4:
                        self.state = 2473
                        self.match(PsithonParser.LSQB)
                        self.state = 2474
                        self.slices()
                        self.state = 2475
                        self.match(PsithonParser.RSQB)
                        pass

             
                self.state = 2483
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,301,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class SlicesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def slice_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.SliceContext)
            else:
                return self.getTypedRuleContext(PsithonParser.SliceContext,i)


        def starred_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Starred_expressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Starred_expressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_slices




    def slices(self):

        localctx = PsithonParser.SlicesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 416, self.RULE_slices)
        self._la = 0 # Token type
        try:
            self.state = 2502
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,306,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2484
                self.slice_()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2487
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,302,self._ctx)
                if la_ == 1:
                    self.state = 2485
                    self.slice_()
                    pass

                elif la_ == 2:
                    self.state = 2486
                    self.starred_expression()
                    pass


                self.state = 2496
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,304,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 2489
                        self.match(PsithonParser.COMMA)
                        self.state = 2492
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,303,self._ctx)
                        if la_ == 1:
                            self.state = 2490
                            self.slice_()
                            pass

                        elif la_ == 2:
                            self.state = 2491
                            self.starred_expression()
                            pass

                 
                    self.state = 2498
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,304,self._ctx)

                self.state = 2500
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 2499
                    self.match(PsithonParser.COMMA)


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SliceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COLON)
            else:
                return self.getToken(PsithonParser.COLON, i)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_slice




    def slice_(self):

        localctx = PsithonParser.SliceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 418, self.RULE_slice)
        self._la = 0 # Token type
        try:
            self.state = 2518
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,311,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2505
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,307,self._ctx)
                if la_ == 1:
                    self.state = 2504
                    self.expression()


                self.state = 2507
                self.match(PsithonParser.COLON)
                self.state = 2509
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,308,self._ctx)
                if la_ == 1:
                    self.state = 2508
                    self.expression()


                self.state = 2515
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==27:
                    self.state = 2511
                    self.match(PsithonParser.COLON)
                    self.state = 2513
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,309,self._ctx)
                    if la_ == 1:
                        self.state = 2512
                        self.expression()




                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2517
                self.named_expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GroupContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def yield_expr(self):
            return self.getTypedRuleContext(PsithonParser.Yield_exprContext,0)


        def named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Named_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_group




    def group(self):

        localctx = PsithonParser.GroupContext(self, self._ctx, self.state)
        self.enterRule(localctx, 420, self.RULE_group)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2520
            self.match(PsithonParser.LPAR)
            self.state = 2523
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,312,self._ctx)
            if la_ == 1:
                self.state = 2521
                self.yield_expr()
                pass

            elif la_ == 2:
                self.state = 2522
                self.named_expression()
                pass


            self.state = 2525
            self.match(PsithonParser.RPAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LambdefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LAMBDA(self):
            return self.getToken(PsithonParser.LAMBDA, 0)

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def lambda_params(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_paramsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambdef




    def lambdef(self):

        localctx = PsithonParser.LambdefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 422, self.RULE_lambdef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2527
            self.match(PsithonParser.LAMBDA)
            self.state = 2529
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 281479272202240) != 0) or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                self.state = 2528
                self.lambda_params()


            self.state = 2531
            self.match(PsithonParser.COLON)
            self.state = 2532
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_paramsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lambda_parameters(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_parametersContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_params




    def lambda_params(self):

        localctx = PsithonParser.Lambda_paramsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 424, self.RULE_lambda_params)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2534
            self.lambda_parameters()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_parametersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lambda_slash_no_default(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_slash_no_defaultContext,0)


        def lambda_param_no_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Lambda_param_no_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Lambda_param_no_defaultContext,i)


        def lambda_param_with_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Lambda_param_with_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Lambda_param_with_defaultContext,i)


        def lambda_star_etc(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_star_etcContext,0)


        def lambda_slash_with_default(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_slash_with_defaultContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_parameters




    def lambda_parameters(self):

        localctx = PsithonParser.Lambda_parametersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 426, self.RULE_lambda_parameters)
        self._la = 0 # Token type
        try:
            self.state = 2585
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,324,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2536
                self.lambda_slash_no_default()
                self.state = 2540
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,314,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 2537
                        self.lambda_param_no_default() 
                    self.state = 2542
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,314,self._ctx)

                self.state = 2546
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 2543
                    self.lambda_param_with_default()
                    self.state = 2548
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 2550
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 2549
                    self.lambda_star_etc()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2552
                self.lambda_slash_with_default()
                self.state = 2556
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 2553
                    self.lambda_param_with_default()
                    self.state = 2558
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 2560
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 2559
                    self.lambda_star_etc()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2563 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 2562
                        self.lambda_param_no_default()

                    else:
                        raise NoViableAltException(self)
                    self.state = 2565 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,319,self._ctx)

                self.state = 2570
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 2567
                    self.lambda_param_with_default()
                    self.state = 2572
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 2574
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 2573
                    self.lambda_star_etc()


                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2577 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 2576
                    self.lambda_param_with_default()
                    self.state = 2579 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                        break

                self.state = 2582
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==32 or _la==48:
                    self.state = 2581
                    self.lambda_star_etc()


                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 2584
                self.lambda_star_etc()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_star_etcContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def lambda_param_no_default(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_no_defaultContext,0)


        def lambda_param_maybe_default(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Lambda_param_maybe_defaultContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Lambda_param_maybe_defaultContext,i)


        def lambda_kwds(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_kwdsContext,0)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_star_etc




    def lambda_star_etc(self):

        localctx = PsithonParser.Lambda_star_etcContext(self, self._ctx, self.state)
        self.enterRule(localctx, 428, self.RULE_lambda_star_etc)
        self._la = 0 # Token type
        try:
            self.state = 2609
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,329,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2587
                self.match(PsithonParser.STAR)
                self.state = 2588
                self.lambda_param_no_default()
                self.state = 2592
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0):
                    self.state = 2589
                    self.lambda_param_maybe_default()
                    self.state = 2594
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 2596
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==48:
                    self.state = 2595
                    self.lambda_kwds()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2598
                self.match(PsithonParser.STAR)
                self.state = 2599
                self.match(PsithonParser.COMMA)
                self.state = 2601 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 2600
                    self.lambda_param_maybe_default()
                    self.state = 2603 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==19 or ((((_la - 103)) & ~0x3f) == 0 and ((1 << (_la - 103)) & 31) != 0)):
                        break

                self.state = 2606
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==48:
                    self.state = 2605
                    self.lambda_kwds()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2608
                self.lambda_kwds()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_kwdsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def lambda_param_no_default(self):
            return self.getTypedRuleContext(PsithonParser.Lambda_param_no_defaultContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_kwds




    def lambda_kwds(self):

        localctx = PsithonParser.Lambda_kwdsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 430, self.RULE_lambda_kwds)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2611
            self.match(PsithonParser.DOUBLESTAR)
            self.state = 2612
            self.lambda_param_no_default()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Lambda_paramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_lambda_param




    def lambda_param(self):

        localctx = PsithonParser.Lambda_paramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 432, self.RULE_lambda_param)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2614
            self.name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Fstring_middleContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def fstring_replacement_field(self):
            return self.getTypedRuleContext(PsithonParser.Fstring_replacement_fieldContext,0)


        def FSTRING_MIDDLE(self):
            return self.getToken(PsithonParser.FSTRING_MIDDLE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_fstring_middle




    def fstring_middle(self):

        localctx = PsithonParser.Fstring_middleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 434, self.RULE_fstring_middle)
        try:
            self.state = 2618
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [22]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2616
                self.fstring_replacement_field()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2617
                self.match(PsithonParser.FSTRING_MIDDLE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Fstring_replacement_fieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def annotated_rhs(self):
            return self.getTypedRuleContext(PsithonParser.Annotated_rhsContext,0)


        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def fstring_conversion(self):
            return self.getTypedRuleContext(PsithonParser.Fstring_conversionContext,0)


        def fstring_full_format_spec(self):
            return self.getTypedRuleContext(PsithonParser.Fstring_full_format_specContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_fstring_replacement_field




    def fstring_replacement_field(self):

        localctx = PsithonParser.Fstring_replacement_fieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 436, self.RULE_fstring_replacement_field)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2620
            self.match(PsithonParser.LBRACE)
            self.state = 2621
            self.annotated_rhs()
            self.state = 2623
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==38:
                self.state = 2622
                self.match(PsithonParser.EQUAL)


            self.state = 2626
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==67:
                self.state = 2625
                self.fstring_conversion()


            self.state = 2629
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 2628
                self.fstring_full_format_spec()


            self.state = 2631
            self.match(PsithonParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Fstring_conversionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXCLAMATION(self):
            return self.getToken(PsithonParser.EXCLAMATION, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_fstring_conversion




    def fstring_conversion(self):

        localctx = PsithonParser.Fstring_conversionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 438, self.RULE_fstring_conversion)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2633
            self.match(PsithonParser.EXCLAMATION)
            self.state = 2634
            self.name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Fstring_full_format_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def fstring_format_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Fstring_format_specContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Fstring_format_specContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_fstring_full_format_spec




    def fstring_full_format_spec(self):

        localctx = PsithonParser.Fstring_full_format_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 440, self.RULE_fstring_full_format_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2636
            self.match(PsithonParser.COLON)
            self.state = 2640
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6 or _la==22:
                self.state = 2637
                self.fstring_format_spec()
                self.state = 2642
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Fstring_format_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FSTRING_MIDDLE(self):
            return self.getToken(PsithonParser.FSTRING_MIDDLE, 0)

        def fstring_replacement_field(self):
            return self.getTypedRuleContext(PsithonParser.Fstring_replacement_fieldContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_fstring_format_spec




    def fstring_format_spec(self):

        localctx = PsithonParser.Fstring_format_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 442, self.RULE_fstring_format_spec)
        try:
            self.state = 2645
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [6]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2643
                self.match(PsithonParser.FSTRING_MIDDLE)
                pass
            elif token in [22]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2644
                self.fstring_replacement_field()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FstringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FSTRING_START(self):
            return self.getToken(PsithonParser.FSTRING_START, 0)

        def FSTRING_END(self):
            return self.getToken(PsithonParser.FSTRING_END, 0)

        def fstring_middle(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Fstring_middleContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Fstring_middleContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_fstring




    def fstring(self):

        localctx = PsithonParser.FstringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 444, self.RULE_fstring)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2647
            self.match(PsithonParser.FSTRING_START)
            self.state = 2651
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6 or _la==22:
                self.state = 2648
                self.fstring_middle()
                self.state = 2653
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 2654
            self.match(PsithonParser.FSTRING_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tstring_format_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TSTRING_MIDDLE(self):
            return self.getToken(PsithonParser.TSTRING_MIDDLE, 0)

        def tstring_replacement_field(self):
            return self.getTypedRuleContext(PsithonParser.Tstring_replacement_fieldContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_tstring_format_spec




    def tstring_format_spec(self):

        localctx = PsithonParser.Tstring_format_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 446, self.RULE_tstring_format_spec)
        try:
            self.state = 2658
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2656
                self.match(PsithonParser.TSTRING_MIDDLE)
                pass
            elif token in [22]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2657
                self.tstring_replacement_field()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tstring_full_format_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def tstring_format_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Tstring_format_specContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Tstring_format_specContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_tstring_full_format_spec




    def tstring_full_format_spec(self):

        localctx = PsithonParser.Tstring_full_format_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 448, self.RULE_tstring_full_format_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2660
            self.match(PsithonParser.COLON)
            self.state = 2664
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==9 or _la==22:
                self.state = 2661
                self.tstring_format_spec()
                self.state = 2666
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tstring_replacement_fieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def annotated_rhs(self):
            return self.getTypedRuleContext(PsithonParser.Annotated_rhsContext,0)


        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def fstring_conversion(self):
            return self.getTypedRuleContext(PsithonParser.Fstring_conversionContext,0)


        def tstring_full_format_spec(self):
            return self.getTypedRuleContext(PsithonParser.Tstring_full_format_specContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_tstring_replacement_field




    def tstring_replacement_field(self):

        localctx = PsithonParser.Tstring_replacement_fieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 450, self.RULE_tstring_replacement_field)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2667
            self.match(PsithonParser.LBRACE)
            self.state = 2668
            self.annotated_rhs()
            self.state = 2670
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==38:
                self.state = 2669
                self.match(PsithonParser.EQUAL)


            self.state = 2673
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==67:
                self.state = 2672
                self.fstring_conversion()


            self.state = 2676
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 2675
                self.tstring_full_format_spec()


            self.state = 2678
            self.match(PsithonParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tstring_middleContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tstring_replacement_field(self):
            return self.getTypedRuleContext(PsithonParser.Tstring_replacement_fieldContext,0)


        def TSTRING_MIDDLE(self):
            return self.getToken(PsithonParser.TSTRING_MIDDLE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_tstring_middle




    def tstring_middle(self):

        localctx = PsithonParser.Tstring_middleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 452, self.RULE_tstring_middle)
        try:
            self.state = 2682
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [22]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2680
                self.tstring_replacement_field()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2681
                self.match(PsithonParser.TSTRING_MIDDLE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TstringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TSTRING_START(self):
            return self.getToken(PsithonParser.TSTRING_START, 0)

        def TSTRING_END(self):
            return self.getToken(PsithonParser.TSTRING_END, 0)

        def tstring_middle(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Tstring_middleContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Tstring_middleContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_tstring




    def tstring(self):

        localctx = PsithonParser.TstringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 454, self.RULE_tstring)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2684
            self.match(PsithonParser.TSTRING_START)
            self.state = 2688
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==9 or _la==22:
                self.state = 2685
                self.tstring_middle()
                self.state = 2690
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 2691
            self.match(PsithonParser.TSTRING_END)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(PsithonParser.STRING, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_string




    def string(self):

        localctx = PsithonParser.StringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 456, self.RULE_string)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2693
            self.match(PsithonParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def fstring(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.FstringContext)
            else:
                return self.getTypedRuleContext(PsithonParser.FstringContext,i)


        def string(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.StringContext)
            else:
                return self.getTypedRuleContext(PsithonParser.StringContext,i)


        def tstring(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.TstringContext)
            else:
                return self.getTypedRuleContext(PsithonParser.TstringContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_strings




    def strings(self):

        localctx = PsithonParser.StringsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 458, self.RULE_strings)
        try:
            self.state = 2706
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5, 109]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2697 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 2697
                        self._errHandler.sync(self)
                        token = self._input.LA(1)
                        if token in [5]:
                            self.state = 2695
                            self.fstring()
                            pass
                        elif token in [109]:
                            self.state = 2696
                            self.string()
                            pass
                        else:
                            raise NoViableAltException(self)


                    else:
                        raise NoViableAltException(self)
                    self.state = 2699 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,345,self._ctx)

                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2702 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 2701
                        self.tstring()

                    else:
                        raise NoViableAltException(self)
                    self.state = 2704 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,346,self._ctx)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def star_named_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_list




    def list_(self):

        localctx = PsithonParser.ListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 460, self.RULE_list)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2708
            self.match(PsithonParser.LSQB)
            self.state = 2710
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,348,self._ctx)
            if la_ == 1:
                self.state = 2709
                self.star_named_expressions()


            self.state = 2712
            self.match(PsithonParser.RSQB)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TupleContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def star_named_expression(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionContext,0)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def star_named_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_tuple




    def tuple_(self):

        localctx = PsithonParser.TupleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 462, self.RULE_tuple)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2714
            self.match(PsithonParser.LPAR)
            self.state = 2720
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,350,self._ctx)
            if la_ == 1:
                self.state = 2715
                self.star_named_expression()
                self.state = 2716
                self.match(PsithonParser.COMMA)
                self.state = 2718
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,349,self._ctx)
                if la_ == 1:
                    self.state = 2717
                    self.star_named_expressions()




            self.state = 2722
            self.match(PsithonParser.RPAR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def star_named_expressions(self):
            return self.getTypedRuleContext(PsithonParser.Star_named_expressionsContext,0)


        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_set




    def set_(self):

        localctx = PsithonParser.SetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 464, self.RULE_set)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2724
            self.match(PsithonParser.LBRACE)
            self.state = 2725
            self.star_named_expressions()
            self.state = 2726
            self.match(PsithonParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DictContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(PsithonParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(PsithonParser.RBRACE, 0)

        def double_starred_kvpairs(self):
            return self.getTypedRuleContext(PsithonParser.Double_starred_kvpairsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_dict




    def dict_(self):

        localctx = PsithonParser.DictContext(self, self._ctx, self.state)
        self.enterRule(localctx, 466, self.RULE_dict)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2728
            self.match(PsithonParser.LBRACE)
            self.state = 2730
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,351,self._ctx)
            if la_ == 1:
                self.state = 2729
                self.double_starred_kvpairs()


            self.state = 2732
            self.match(PsithonParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Double_starred_kvpairsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def double_starred_kvpair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Double_starred_kvpairContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Double_starred_kvpairContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_double_starred_kvpairs




    def double_starred_kvpairs(self):

        localctx = PsithonParser.Double_starred_kvpairsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 468, self.RULE_double_starred_kvpairs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2734
            self.double_starred_kvpair()
            self.state = 2739
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,352,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2735
                    self.match(PsithonParser.COMMA)
                    self.state = 2736
                    self.double_starred_kvpair() 
                self.state = 2741
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,352,self._ctx)

            self.state = 2743
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2742
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Double_starred_kvpairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def bitwise_or(self):
            return self.getTypedRuleContext(PsithonParser.Bitwise_orContext,0)


        def kvpair(self):
            return self.getTypedRuleContext(PsithonParser.KvpairContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_double_starred_kvpair




    def double_starred_kvpair(self):

        localctx = PsithonParser.Double_starred_kvpairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 470, self.RULE_double_starred_kvpair)
        try:
            self.state = 2748
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,354,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2745
                self.match(PsithonParser.DOUBLESTAR)
                self.state = 2746
                self.bitwise_or(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2747
                self.kvpair()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class KvpairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def COLON(self):
            return self.getToken(PsithonParser.COLON, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_kvpair




    def kvpair(self):

        localctx = PsithonParser.KvpairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 472, self.RULE_kvpair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2750
            self.expression()
            self.state = 2751
            self.match(PsithonParser.COLON)
            self.state = 2752
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class For_if_clausesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def for_if_clause(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.For_if_clauseContext)
            else:
                return self.getTypedRuleContext(PsithonParser.For_if_clauseContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_for_if_clauses




    def for_if_clauses(self):

        localctx = PsithonParser.For_if_clausesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 474, self.RULE_for_if_clauses)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2755 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 2754
                self.for_if_clause()
                self.state = 2757 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==85 or _la==98):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class For_if_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FOR(self):
            return self.getToken(PsithonParser.FOR, 0)

        def star_targets(self):
            return self.getTypedRuleContext(PsithonParser.Star_targetsContext,0)


        def IN(self):
            return self.getToken(PsithonParser.IN, 0)

        def disjunction(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.DisjunctionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.DisjunctionContext,i)


        def ASYNC(self):
            return self.getToken(PsithonParser.ASYNC, 0)

        def IF(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.IF)
            else:
                return self.getToken(PsithonParser.IF, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_for_if_clause




    def for_if_clause(self):

        localctx = PsithonParser.For_if_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 476, self.RULE_for_if_clause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2760
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==98:
                self.state = 2759
                self.match(PsithonParser.ASYNC)


            self.state = 2762
            self.match(PsithonParser.FOR)
            self.state = 2763
            self.star_targets()
            self.state = 2764
            self.match(PsithonParser.IN)
            self.state = 2765
            self.disjunction()
            self.state = 2770
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==100:
                self.state = 2766
                self.match(PsithonParser.IF)
                self.state = 2767
                self.disjunction()
                self.state = 2772
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def args(self):
            return self.getTypedRuleContext(PsithonParser.ArgsContext,0)


        def COMMA(self):
            return self.getToken(PsithonParser.COMMA, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_arguments




    def arguments(self):

        localctx = PsithonParser.ArgumentsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 478, self.RULE_arguments)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2773
            self.args()
            self.state = 2775
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2774
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def starred_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Starred_expressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Starred_expressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def kwargs(self):
            return self.getTypedRuleContext(PsithonParser.KwargsContext,0)


        def assignment_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Assignment_expressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Assignment_expressionContext,i)


        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_args




    def args(self):

        localctx = PsithonParser.ArgsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 480, self.RULE_args)
        try:
            self.state = 2802
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,365,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2782
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,360,self._ctx)
                if la_ == 1:
                    self.state = 2777
                    self.starred_expression()
                    pass

                elif la_ == 2:
                    self.state = 2780
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,359,self._ctx)
                    if la_ == 1:
                        self.state = 2778
                        self.assignment_expression()
                        pass

                    elif la_ == 2:
                        self.state = 2779
                        self.expression()
                        pass


                    pass


                self.state = 2794
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,363,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 2784
                        self.match(PsithonParser.COMMA)
                        self.state = 2790
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,362,self._ctx)
                        if la_ == 1:
                            self.state = 2785
                            self.starred_expression()
                            pass

                        elif la_ == 2:
                            self.state = 2788
                            self._errHandler.sync(self)
                            la_ = self._interp.adaptivePredict(self._input,361,self._ctx)
                            if la_ == 1:
                                self.state = 2786
                                self.assignment_expression()
                                pass

                            elif la_ == 2:
                                self.state = 2787
                                self.expression()
                                pass


                            pass

                 
                    self.state = 2796
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,363,self._ctx)

                self.state = 2799
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,364,self._ctx)
                if la_ == 1:
                    self.state = 2797
                    self.match(PsithonParser.COMMA)
                    self.state = 2798
                    self.kwargs()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2801
                self.kwargs()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class KwargsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def kwarg_or_starred(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Kwarg_or_starredContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Kwarg_or_starredContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def kwarg_or_double_starred(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Kwarg_or_double_starredContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Kwarg_or_double_starredContext,i)


        def getRuleIndex(self):
            return PsithonParser.RULE_kwargs




    def kwargs(self):

        localctx = PsithonParser.KwargsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 482, self.RULE_kwargs)
        try:
            self.state = 2831
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,370,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2804
                self.kwarg_or_starred()
                self.state = 2809
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,366,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 2805
                        self.match(PsithonParser.COMMA)
                        self.state = 2806
                        self.kwarg_or_starred() 
                    self.state = 2811
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,366,self._ctx)

                self.state = 2821
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,368,self._ctx)
                if la_ == 1:
                    self.state = 2812
                    self.match(PsithonParser.COMMA)
                    self.state = 2813
                    self.kwarg_or_double_starred()
                    self.state = 2818
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,367,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 2814
                            self.match(PsithonParser.COMMA)
                            self.state = 2815
                            self.kwarg_or_double_starred() 
                        self.state = 2820
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,367,self._ctx)



                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2823
                self.kwarg_or_double_starred()
                self.state = 2828
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,369,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 2824
                        self.match(PsithonParser.COMMA)
                        self.state = 2825
                        self.kwarg_or_double_starred() 
                    self.state = 2830
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,369,self._ctx)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Starred_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_starred_expression




    def starred_expression(self):

        localctx = PsithonParser.Starred_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 484, self.RULE_starred_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2833
            self.match(PsithonParser.STAR)
            self.state = 2834
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Kwarg_or_starredContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def starred_expression(self):
            return self.getTypedRuleContext(PsithonParser.Starred_expressionContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_kwarg_or_starred




    def kwarg_or_starred(self):

        localctx = PsithonParser.Kwarg_or_starredContext(self, self._ctx, self.state)
        self.enterRule(localctx, 486, self.RULE_kwarg_or_starred)
        try:
            self.state = 2841
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [19, 103, 104, 105, 106, 107]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2836
                self.name()
                self.state = 2837
                self.match(PsithonParser.EQUAL)
                self.state = 2838
                self.expression()
                pass
            elif token in [32]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2840
                self.starred_expression()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Kwarg_or_double_starredContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def EQUAL(self):
            return self.getToken(PsithonParser.EQUAL, 0)

        def expression(self):
            return self.getTypedRuleContext(PsithonParser.ExpressionContext,0)


        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_kwarg_or_double_starred




    def kwarg_or_double_starred(self):

        localctx = PsithonParser.Kwarg_or_double_starredContext(self, self._ctx, self.state)
        self.enterRule(localctx, 488, self.RULE_kwarg_or_double_starred)
        try:
            self.state = 2849
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [19, 103, 104, 105, 106, 107]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2843
                self.name()
                self.state = 2844
                self.match(PsithonParser.EQUAL)
                self.state = 2845
                self.expression()
                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2847
                self.match(PsithonParser.DOUBLESTAR)
                self.state = 2848
                self.expression()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_targetsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_target(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Star_targetContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Star_targetContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_star_targets




    def star_targets(self):

        localctx = PsithonParser.Star_targetsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 490, self.RULE_star_targets)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2851
            self.star_target()
            self.state = 2856
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,373,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2852
                    self.match(PsithonParser.COMMA)
                    self.state = 2853
                    self.star_target() 
                self.state = 2858
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,373,self._ctx)

            self.state = 2860
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2859
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_targets_list_seqContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_target(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Star_targetContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Star_targetContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_star_targets_list_seq




    def star_targets_list_seq(self):

        localctx = PsithonParser.Star_targets_list_seqContext(self, self._ctx, self.state)
        self.enterRule(localctx, 492, self.RULE_star_targets_list_seq)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2862
            self.star_target()
            self.state = 2867
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,375,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2863
                    self.match(PsithonParser.COMMA)
                    self.state = 2864
                    self.star_target() 
                self.state = 2869
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,375,self._ctx)

            self.state = 2871
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2870
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_targets_tuple_seqContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def star_target(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Star_targetContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Star_targetContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_star_targets_tuple_seq




    def star_targets_tuple_seq(self):

        localctx = PsithonParser.Star_targets_tuple_seqContext(self, self._ctx, self.state)
        self.enterRule(localctx, 494, self.RULE_star_targets_tuple_seq)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2873
            self.star_target()
            self.state = 2884
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,379,self._ctx)
            if la_ == 1:
                self.state = 2874
                self.match(PsithonParser.COMMA)
                pass

            elif la_ == 2:
                self.state = 2877 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 2875
                        self.match(PsithonParser.COMMA)
                        self.state = 2876
                        self.star_target()

                    else:
                        raise NoViableAltException(self)
                    self.state = 2879 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,377,self._ctx)

                self.state = 2882
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 2881
                    self.match(PsithonParser.COMMA)


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_targetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def star_target(self):
            return self.getTypedRuleContext(PsithonParser.Star_targetContext,0)


        def target_with_star_atom(self):
            return self.getTypedRuleContext(PsithonParser.Target_with_star_atomContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_star_target




    def star_target(self):

        localctx = PsithonParser.Star_targetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 496, self.RULE_star_target)
        try:
            self.state = 2889
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [32]:
                self.enterOuterAlt(localctx, 1)
                self.state = 2886
                self.match(PsithonParser.STAR)

                self.state = 2887
                self.star_target()
                pass
            elif token in [5, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 65, 68, 73, 78, 103, 104, 105, 106, 107, 108, 109]:
                self.enterOuterAlt(localctx, 2)
                self.state = 2888
                self.target_with_star_atom()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Target_with_star_atomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def t_primary(self):
            return self.getTypedRuleContext(PsithonParser.T_primaryContext,0)


        def DOT(self):
            return self.getToken(PsithonParser.DOT, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def slices(self):
            return self.getTypedRuleContext(PsithonParser.SlicesContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def star_atom(self):
            return self.getTypedRuleContext(PsithonParser.Star_atomContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_target_with_star_atom




    def target_with_star_atom(self):

        localctx = PsithonParser.Target_with_star_atomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 498, self.RULE_target_with_star_atom)
        try:
            self.state = 2901
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,382,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2891
                self.t_primary(0)
                self.state = 2898
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [26]:
                    self.state = 2892
                    self.match(PsithonParser.DOT)
                    self.state = 2893
                    self.name()
                    pass
                elif token in [21]:
                    self.state = 2894
                    self.match(PsithonParser.LSQB)
                    self.state = 2895
                    self.slices()
                    self.state = 2896
                    self.match(PsithonParser.RSQB)
                    pass
                else:
                    raise NoViableAltException(self)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2900
                self.star_atom()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Star_atomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def target_with_star_atom(self):
            return self.getTypedRuleContext(PsithonParser.Target_with_star_atomContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def star_targets_tuple_seq(self):
            return self.getTypedRuleContext(PsithonParser.Star_targets_tuple_seqContext,0)


        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def star_targets_list_seq(self):
            return self.getTypedRuleContext(PsithonParser.Star_targets_list_seqContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_star_atom




    def star_atom(self):

        localctx = PsithonParser.Star_atomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 500, self.RULE_star_atom)
        self._la = 0 # Token type
        try:
            self.state = 2918
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,385,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2903
                self.name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2904
                self.match(PsithonParser.LPAR)
                self.state = 2905
                self.target_with_star_atom()
                self.state = 2906
                self.match(PsithonParser.RPAR)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2908
                self.match(PsithonParser.LPAR)
                self.state = 2910
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4303092000) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 34909494190345) != 0):
                    self.state = 2909
                    self.star_targets_tuple_seq()


                self.state = 2912
                self.match(PsithonParser.RPAR)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2913
                self.match(PsithonParser.LSQB)
                self.state = 2915
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 4303092000) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 34909494190345) != 0):
                    self.state = 2914
                    self.star_targets_list_seq()


                self.state = 2917
                self.match(PsithonParser.RSQB)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Single_targetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def single_subscript_attribute_target(self):
            return self.getTypedRuleContext(PsithonParser.Single_subscript_attribute_targetContext,0)


        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def single_target(self):
            return self.getTypedRuleContext(PsithonParser.Single_targetContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_single_target




    def single_target(self):

        localctx = PsithonParser.Single_targetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 502, self.RULE_single_target)
        try:
            self.state = 2926
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,386,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2920
                self.single_subscript_attribute_target()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2921
                self.name()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2922
                self.match(PsithonParser.LPAR)
                self.state = 2923
                self.single_target()
                self.state = 2924
                self.match(PsithonParser.RPAR)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Single_subscript_attribute_targetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def t_primary(self):
            return self.getTypedRuleContext(PsithonParser.T_primaryContext,0)


        def DOT(self):
            return self.getToken(PsithonParser.DOT, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def slices(self):
            return self.getTypedRuleContext(PsithonParser.SlicesContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_single_subscript_attribute_target




    def single_subscript_attribute_target(self):

        localctx = PsithonParser.Single_subscript_attribute_targetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 504, self.RULE_single_subscript_attribute_target)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2928
            self.t_primary(0)
            self.state = 2935
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [26]:
                self.state = 2929
                self.match(PsithonParser.DOT)
                self.state = 2930
                self.name()
                pass
            elif token in [21]:
                self.state = 2931
                self.match(PsithonParser.LSQB)
                self.state = 2932
                self.slices()
                self.state = 2933
                self.match(PsithonParser.RSQB)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class T_primaryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom(self):
            return self.getTypedRuleContext(PsithonParser.AtomContext,0)


        def t_primary(self):
            return self.getTypedRuleContext(PsithonParser.T_primaryContext,0)


        def DOT(self):
            return self.getToken(PsithonParser.DOT, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def slices(self):
            return self.getTypedRuleContext(PsithonParser.SlicesContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def genexp(self):
            return self.getTypedRuleContext(PsithonParser.GenexpContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def arguments(self):
            return self.getTypedRuleContext(PsithonParser.ArgumentsContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_t_primary



    def t_primary(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = PsithonParser.T_primaryContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 506
        self.enterRecursionRule(localctx, 506, self.RULE_t_primary, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2938
            self.atom()
            self._ctx.stop = self._input.LT(-1)
            self.state = 2957
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,390,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = PsithonParser.T_primaryContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_t_primary)
                    self.state = 2940
                    if not self.precpred(self._ctx, 2):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                    self.state = 2953
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,389,self._ctx)
                    if la_ == 1:
                        self.state = 2941
                        self.match(PsithonParser.DOT)
                        self.state = 2942
                        self.name()
                        pass

                    elif la_ == 2:
                        self.state = 2943
                        self.match(PsithonParser.LSQB)
                        self.state = 2944
                        self.slices()
                        self.state = 2945
                        self.match(PsithonParser.RSQB)
                        pass

                    elif la_ == 3:
                        self.state = 2947
                        self.genexp()
                        pass

                    elif la_ == 4:
                        self.state = 2948
                        self.match(PsithonParser.LPAR)
                        self.state = 2950
                        self._errHandler.sync(self)
                        la_ = self._interp.adaptivePredict(self._input,388,self._ctx)
                        if la_ == 1:
                            self.state = 2949
                            self.arguments()


                        self.state = 2952
                        self.match(PsithonParser.RPAR)
                        pass

             
                self.state = 2959
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,390,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class Del_targetsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def del_target(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.Del_targetContext)
            else:
                return self.getTypedRuleContext(PsithonParser.Del_targetContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def getRuleIndex(self):
            return PsithonParser.RULE_del_targets




    def del_targets(self):

        localctx = PsithonParser.Del_targetsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 508, self.RULE_del_targets)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 2960
            self.del_target()
            self.state = 2965
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,391,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 2961
                    self.match(PsithonParser.COMMA)
                    self.state = 2962
                    self.del_target() 
                self.state = 2967
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,391,self._ctx)

            self.state = 2969
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 2968
                self.match(PsithonParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Del_targetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def t_primary(self):
            return self.getTypedRuleContext(PsithonParser.T_primaryContext,0)


        def DOT(self):
            return self.getToken(PsithonParser.DOT, 0)

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def slices(self):
            return self.getTypedRuleContext(PsithonParser.SlicesContext,0)


        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def del_t_atom(self):
            return self.getTypedRuleContext(PsithonParser.Del_t_atomContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_del_target




    def del_target(self):

        localctx = PsithonParser.Del_targetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 510, self.RULE_del_target)
        try:
            self.state = 2981
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,394,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2971
                self.t_primary(0)
                self.state = 2978
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [26]:
                    self.state = 2972
                    self.match(PsithonParser.DOT)
                    self.state = 2973
                    self.name()
                    pass
                elif token in [21]:
                    self.state = 2974
                    self.match(PsithonParser.LSQB)
                    self.state = 2975
                    self.slices()
                    self.state = 2976
                    self.match(PsithonParser.RSQB)
                    pass
                else:
                    raise NoViableAltException(self)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2980
                self.del_t_atom()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Del_t_atomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def name(self):
            return self.getTypedRuleContext(PsithonParser.NameContext,0)


        def LPAR(self):
            return self.getToken(PsithonParser.LPAR, 0)

        def del_target(self):
            return self.getTypedRuleContext(PsithonParser.Del_targetContext,0)


        def RPAR(self):
            return self.getToken(PsithonParser.RPAR, 0)

        def del_targets(self):
            return self.getTypedRuleContext(PsithonParser.Del_targetsContext,0)


        def LSQB(self):
            return self.getToken(PsithonParser.LSQB, 0)

        def RSQB(self):
            return self.getToken(PsithonParser.RSQB, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_del_t_atom




    def del_t_atom(self):

        localctx = PsithonParser.Del_t_atomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 512, self.RULE_del_t_atom)
        self._la = 0 # Token type
        try:
            self.state = 2998
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,397,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 2983
                self.name()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 2984
                self.match(PsithonParser.LPAR)
                self.state = 2985
                self.del_target()
                self.state = 2986
                self.match(PsithonParser.RPAR)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 2988
                self.match(PsithonParser.LPAR)
                self.state = 2990
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 8124704) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 34909494190345) != 0):
                    self.state = 2989
                    self.del_targets()


                self.state = 2992
                self.match(PsithonParser.RPAR)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 2993
                self.match(PsithonParser.LSQB)
                self.state = 2995
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 8124704) != 0) or ((((_la - 65)) & ~0x3f) == 0 and ((1 << (_la - 65)) & 34909494190345) != 0):
                    self.state = 2994
                    self.del_targets()


                self.state = 2997
                self.match(PsithonParser.RSQB)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_expressionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PsithonParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(PsithonParser.ExpressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(PsithonParser.COMMA)
            else:
                return self.getToken(PsithonParser.COMMA, i)

        def STAR(self):
            return self.getToken(PsithonParser.STAR, 0)

        def DOUBLESTAR(self):
            return self.getToken(PsithonParser.DOUBLESTAR, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_type_expressions




    def type_expressions(self):

        localctx = PsithonParser.Type_expressionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 514, self.RULE_type_expressions)
        self._la = 0 # Token type
        try:
            self.state = 3031
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,403,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 3000
                self.expression()
                self.state = 3005
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,398,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 3001
                        self.match(PsithonParser.COMMA)
                        self.state = 3002
                        self.expression() 
                    self.state = 3007
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,398,self._ctx)

                self.state = 3020
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 3008
                    self.match(PsithonParser.COMMA)
                    self.state = 3018
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [32]:
                        self.state = 3009
                        self.match(PsithonParser.STAR)
                        self.state = 3010
                        self.expression()
                        self.state = 3014
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if _la==28:
                            self.state = 3011
                            self.match(PsithonParser.COMMA)
                            self.state = 3012
                            self.match(PsithonParser.DOUBLESTAR)
                            self.state = 3013
                            self.expression()


                        pass
                    elif token in [48]:
                        self.state = 3016
                        self.match(PsithonParser.DOUBLESTAR)
                        self.state = 3017
                        self.expression()
                        pass
                    else:
                        raise NoViableAltException(self)



                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 3022
                self.match(PsithonParser.STAR)
                self.state = 3023
                self.expression()
                self.state = 3027
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==28:
                    self.state = 3024
                    self.match(PsithonParser.COMMA)
                    self.state = 3025
                    self.match(PsithonParser.DOUBLESTAR)
                    self.state = 3026
                    self.expression()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 3029
                self.match(PsithonParser.DOUBLESTAR)
                self.state = 3030
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Func_type_commentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(PsithonParser.NEWLINE, 0)

        def TYPE_COMMENT(self):
            return self.getToken(PsithonParser.TYPE_COMMENT, 0)

        def getRuleIndex(self):
            return PsithonParser.RULE_func_type_comment




    def func_type_comment(self):

        localctx = PsithonParser.Func_type_commentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 516, self.RULE_func_type_comment)
        try:
            self.state = 3036
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [110]:
                self.enterOuterAlt(localctx, 1)
                self.state = 3033
                self.match(PsithonParser.NEWLINE)
                self.state = 3034
                self.match(PsithonParser.TYPE_COMMENT)
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)
                self.state = 3035
                self.match(PsithonParser.TYPE_COMMENT)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME_OR_WILDCARD(self):
            return self.getToken(PsithonParser.NAME_OR_WILDCARD, 0)

        def name_except_underscore(self):
            return self.getTypedRuleContext(PsithonParser.Name_except_underscoreContext,0)


        def getRuleIndex(self):
            return PsithonParser.RULE_name




    def name(self):

        localctx = PsithonParser.NameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 518, self.RULE_name)
        try:
            self.state = 3040
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [106]:
                self.enterOuterAlt(localctx, 1)
                self.state = 3038
                self.match(PsithonParser.NAME_OR_WILDCARD)
                pass
            elif token in [19, 103, 104, 105, 107]:
                self.enterOuterAlt(localctx, 2)
                self.state = 3039
                self.name_except_underscore()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[4] = self.molecule_name_sempred
        self._predicates[19] = self.set_command_sempred
        self._predicates[22] = self.module_name_sempred
        self._predicates[24] = self.option_key_sempred
        self._predicates[30] = self.inline_option_scalar_sempred
        self._predicates[32] = self.option_reference_sempred
        self._predicates[43] = self.external_basis_key_sempred
        self._predicates[53] = self.param_end_sempred
        self._predicates[54] = self.slash_end_sempred
        self._predicates[61] = self.lambda_param_end_sempred
        self._predicates[75] = self.return_stmt_sempred
        self._predicates[76] = self.break_stmt_sempred
        self._predicates[77] = self.continue_stmt_sempred
        self._predicates[78] = self.yield_expr_sempred
        self._predicates[79] = self.await_primary_sempred
        self._predicates[80] = self.for_stmt_sempred
        self._predicates[81] = self.with_stmt_sempred
        self._predicates[109] = self.dotted_name_sempred
        self._predicates[199] = self.bitwise_or_sempred
        self._predicates[200] = self.bitwise_xor_sempred
        self._predicates[201] = self.bitwise_and_sempred
        self._predicates[202] = self.shift_expr_sempred
        self._predicates[203] = self.sum_sempred
        self._predicates[204] = self.term_sempred
        self._predicates[207] = self.primary_sempred
        self._predicates[253] = self.t_primary_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def molecule_name_sempred(self, localctx:Molecule_nameContext, predIndex:int):
            if predIndex == 0:
                return self._input.LT(1).text.isidentifier()
         

    def set_command_sempred(self, localctx:Set_commandContext, predIndex:int):
            if predIndex == 1:
                return self.psithon_inline_module(localctx)
         

    def module_name_sempred(self, localctx:Module_nameContext, predIndex:int):
            if predIndex == 2:
                return self.psithon_contiguous(localctx)
         

    def option_key_sempred(self, localctx:Option_keyContext, predIndex:int):
            if predIndex == 3:
                return all(c.isalnum() or c == "_" for c in self._input.LT(1).text)
         

    def inline_option_scalar_sempred(self, localctx:Inline_option_scalarContext, predIndex:int):
            if predIndex == 4:
                return self.psithon_contiguous(localctx)
         

    def option_reference_sempred(self, localctx:Option_referenceContext, predIndex:int):
            if predIndex == 5:
                return (self._input.LT(-1).stop + 1 == self._input.LT(1).start
                and self._input.LT(1).text[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
         

    def external_basis_key_sempred(self, localctx:External_basis_keyContext, predIndex:int):
            if predIndex == 6:
                return self._input.LT(1).text.casefold() in {"basis", "df_basis_scf"}
         

    def param_end_sempred(self, localctx:Param_endContext, predIndex:int):
            if predIndex == 7:
                return self._input.LA(1) == self.RPAR
         

    def slash_end_sempred(self, localctx:Slash_endContext, predIndex:int):
            if predIndex == 8:
                return self._input.LA(1) == self.RPAR
         

    def lambda_param_end_sempred(self, localctx:Lambda_param_endContext, predIndex:int):
            if predIndex == 9:
                return self._input.LA(1) == self.COLON
         

    def return_stmt_sempred(self, localctx:Return_stmtContext, predIndex:int):
            if predIndex == 10:
                return (self.psithon_deferred() or self.psithon_scope(localctx) in {"function", "async"})
         

    def break_stmt_sempred(self, localctx:Break_stmtContext, predIndex:int):
            if predIndex == 11:
                return (self.psithon_deferred() or self.psithon_loop(localctx))
         

    def continue_stmt_sempred(self, localctx:Continue_stmtContext, predIndex:int):
            if predIndex == 12:
                return (self.psithon_deferred() or self.psithon_loop(localctx))
         

    def yield_expr_sempred(self, localctx:Yield_exprContext, predIndex:int):
            if predIndex == 13:
                return (self.psithon_deferred() or self.psithon_scope(localctx) in {"function", "async", "lambda"})
         

            if predIndex == 14:
                return (self.psithon_deferred() or self.psithon_scope(localctx) != "async")
         

    def await_primary_sempred(self, localctx:Await_primaryContext, predIndex:int):
            if predIndex == 15:
                return (self.psithon_deferred() or self.psithon_scope(localctx) in {"async", "generator", "async_comprehension"})
         

    def for_stmt_sempred(self, localctx:For_stmtContext, predIndex:int):
            if predIndex == 16:
                return (self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope(localctx) == "async")
         

    def with_stmt_sempred(self, localctx:With_stmtContext, predIndex:int):
            if predIndex == 17:
                return (self.psithon_deferred() or self._input.LA(1) != self.ASYNC or self.psithon_scope(localctx) == "async")
         

    def dotted_name_sempred(self, localctx:Dotted_nameContext, predIndex:int):
            if predIndex == 18:
                return self.precpred(self._ctx, 2)
         

    def bitwise_or_sempred(self, localctx:Bitwise_orContext, predIndex:int):
            if predIndex == 19:
                return self.precpred(self._ctx, 2)
         

    def bitwise_xor_sempred(self, localctx:Bitwise_xorContext, predIndex:int):
            if predIndex == 20:
                return self.precpred(self._ctx, 2)
         

    def bitwise_and_sempred(self, localctx:Bitwise_andContext, predIndex:int):
            if predIndex == 21:
                return self.precpred(self._ctx, 2)
         

    def shift_expr_sempred(self, localctx:Shift_exprContext, predIndex:int):
            if predIndex == 22:
                return self.precpred(self._ctx, 2)
         

    def sum_sempred(self, localctx:SumContext, predIndex:int):
            if predIndex == 23:
                return self.precpred(self._ctx, 2)
         

    def term_sempred(self, localctx:TermContext, predIndex:int):
            if predIndex == 24:
                return self.precpred(self._ctx, 2)
         

    def primary_sempred(self, localctx:PrimaryContext, predIndex:int):
            if predIndex == 25:
                return self.precpred(self._ctx, 2)
         

    def t_primary_sempred(self, localctx:T_primaryContext, predIndex:int):
            if predIndex == 26:
                return self.precpred(self._ctx, 2)
         




