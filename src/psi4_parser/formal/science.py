"""Describe scientific choices and expected artifacts without storing results."""

import json
from fractions import Fraction
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from psi4_parser.builder import BasisAssignment, ElectronicState, ExternalPotential
from psi4_parser.builder._model import BOHR_ANGSTROM
from psi4_parser.formal._record import Record
from psi4_parser.formal.excited_models import TDSCFAnalysis
from psi4_parser.formal.solvation import PCMSolverSolvation

type Driver = Literal[
    "energy", "optimize", "frequency", "gradient", "hessian", "properties"
]
type Scalar = str | bool | int | float
type SettingValue = Scalar | tuple[Scalar, ...]
type ProductName = Literal[
    "excitation_energy",
    "excited_state_energy",
    "oscillator_strength_length",
    "oscillator_strength_velocity",
    "electric_transition_dipole_length",
    "electronic_energy",
    "gradient",
    "hessian",
    "harmonic_frequencies",
    "normal_modes",
    "zero_point_energy",
    "thermal_energy_correction",
    "enthalpy_correction",
    "gibbs_correction",
    "zero_k_enthalpy",
    "thermal_energy",
    "enthalpy",
    "gibbs_free_energy",
    "dipole",
    "quadrupole",
    "mulliken_charges",
    "lowdin_charges",
    "mayer_indices",
    "wiberg_lowdin_indices",
    "sapt_total_energy",
    "sapt_electrostatics",
    "sapt_exchange",
    "sapt_induction",
    "sapt_dispersion",
]


def _normalize_option_module(module: str | None) -> str | None:
    """Return null for Psi4's global option scope aliases."""
    return None if not module or module.casefold() in {"global", "globals"} else module


class ThermalConditions(Record):
    """Specify the thermodynamic state for an ideal-gas RRHO analysis."""

    temperature_kelvin: float = Field(
        gt=0, description="Positive absolute temperature in kelvin."
    )
    pressure_pascal: float = Field(
        gt=0, description="Positive ideal-gas pressure in pascal."
    )
    treatment: Literal["ideal_gas_rrho"] = Field(
        default="ideal_gas_rrho",
        description="Native rigid-rotor harmonic-oscillator ideal-gas treatment.",
    )


class VibrationalAnalysis(Record):
    """Request explicit projection and thermal conditions for a full frequency job.

    The rotational symmetry number is a scientific input, including isotope
    effects; it is not inferred from an uncomputed optimized geometry.
    """

    conditions: ThermalConditions = Field(
        description="Temperature, pressure, and thermal treatment."
    )
    rotational_symmetry_number: int = Field(
        ge=1, description="Explicit external rotational symmetry number."
    )
    project_translations: bool = Field(
        default=True,
        description="Project translational degrees of freedom in harmonic analysis.",
    )
    project_rotations: bool = Field(
        default=True,
        description="Project rotational degrees of freedom in harmonic analysis.",
    )


class SAPTAnalysis(Record):
    """Require a specific fragment partition and SAPT basis/induction treatment.

    Fragment names follow the native monomer A/B order. A midbond fragment,
    when present, must be third and contain only ghost basis centers. Open-shell
    SAPT requires the high-spin complex; method evidence gates each reference.
    """

    fragments: tuple[str, str] = Field(
        description="Two distinct real-fragment names, in native monomer A/B order."
    )
    basis: Literal["dimer", "monomer"] = Field(
        default="dimer",
        description="Dimer-centered or monomer-centered orbital basis treatment.",
    )
    coupled_induction: bool = Field(
        default=True,
        description="Request coupled induction; ROHF requires false explicitly.",
    )
    midbond_fragment: str | None = Field(
        default=None,
        min_length=1,
        pattern=r"\S",
        description="Optional third all-ghost fragment; requires dimer-centered bases.",
    )

    @model_validator(mode="after")
    def check_partition(self) -> Self:
        """Return an unambiguous ordered partition and compatible basis choice.

        Raises:
            ValueError: Names repeat or are empty, or midbond uses monomer bases.
        """
        if len(set(self.fragments)) != len(self.fragments) or any(
            not name.strip() for name in self.fragments
        ):
            raise ValueError("Supply distinct nonempty SAPT fragment names")
        if self.midbond_fragment in self.fragments:
            raise ValueError("The SAPT midbond fragment must be distinct")
        if self.midbond_fragment is not None and self.basis != "dimer":
            raise ValueError("SAPT midbond functions require dimer-centered bases")
        return self


class Rational(Record):
    """Retain an exact coefficient without floating-point approximation."""

    numerator: int = Field(description="Signed numerator of the exact coefficient.")
    denominator: int = Field(
        default=1, ge=1, description="Positive denominator of the exact coefficient."
    )

    @property
    def fraction(self) -> Fraction:
        """Return the coefficient in reduced form using exact integer arithmetic."""
        return Fraction(self.numerator, self.denominator)

    @property
    def smt(self) -> str:
        """Return a reduced numerator/denominator literal accepted by Z3."""
        value = self.fraction
        return f"{value.numerator}/{value.denominator}"


class Setting(Record):
    """Apply a named application option within one calculation's scope."""

    name: str = Field(
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
        description="Option name, such as scf_type or e_convergence.",
    )
    value: SettingValue = Field(
        description="Literal option value; a tuple represents an ordered option list."
    )
    module: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z][A-Za-z0-9_]*$",
        description=(
            "Application module, such as SCF; null, GLOBAL, and GLOBALS select "
            "a global option and serialize as null."
        ),
    )

    @field_validator("module")
    @classmethod
    def _normalize_module(cls, value: str | None) -> str | None:
        return _normalize_option_module(value)

    @property
    def key(self) -> tuple[str, str]:
        """Return the case-insensitive module and option identity."""
        return ((self.module or "").casefold(), self.name.casefold())


class AuxiliaryBasis(Record):
    """Select a named fitting basis for a particular computational role."""

    role: str = Field(
        pattern=r"^df_basis_[A-Za-z0-9_]+$",
        description="Psi4 fitting-basis option, such as df_basis_scf or df_basis_mp2.",
    )
    basis: str = Field(
        min_length=1, pattern=r"\S", description="Fitting-basis name for this role."
    )


class ECP(Record):
    """Declare an ECP association that a capability catalog must corroborate."""

    element: str = Field(
        pattern=r"^[A-Z][a-z]?$", description="Element symbol to which the ECP applies."
    )
    name: str = Field(min_length=1, description="ECP identity recorded by the catalog.")
    core_electrons: int = Field(
        ge=0, description="Electrons replaced by the ECP on each real atom."
    )


class DDXSolvation(Record):
    """Choose an equilibrium DDX model, dielectric, and atom-centered cavity.

    An omitted dielectric requests the named solvent's value from the
    native solvent table. Cavity radii use the selected table and explicit scaling.
    LPB additionally requires an inverse screening length in inverse bohr.
    """

    model: Literal["pcm", "cosmo", "lpb"] = Field(
        default="pcm", description="Equilibrium continuum equation to solve."
    )
    dielectric_constant: float | None = Field(
        default=None,
        ge=1,
        description="Static relative permittivity; null uses the named solvent table.",
    )
    radii_set: Literal["uff", "bondi"] = Field(
        default="uff", description="Native atom-centered cavity radius table."
    )
    radii_scaling: float = Field(
        default=1.1, gt=0, description="Positive multiplier for the tabulated radii."
    )
    screening_inverse_bohr: float | None = Field(
        default=None,
        gt=0,
        description="Positive Debye screening parameter in inverse bohr, only for LPB.",
    )

    @model_validator(mode="after")
    def check_screening(self) -> Self:
        """Return a model with an explicit, applicable screening parameter.

        Raises:
            ValueError: LPB lacks screening, or another model would ignore it.
        """
        if (self.model == "lpb") != (self.screening_inverse_bohr is not None):
            raise ValueError("Supply screening_inverse_bohr exactly when model is lpb")
        return self


class Environment(Record):
    """Describe an implicit solvent and the settings needed to construct it."""

    kind: Literal["pcm", "ddx"] = Field(
        description="Implicit-solvent implementation requested from the application."
    )
    solvent: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Solvent name; an explicit dielectric overrides its table value.",
    )
    ddx: DDXSolvation = Field(
        default_factory=DDXSolvation,
        description="Equilibrium DDX equation and cavity choices, "
        "used when kind is ddx.",
    )
    pcm: PCMSolverSolvation = Field(
        default_factory=PCMSolverSolvation,
        description="Equilibrium PCMSolver medium and cavity, used when kind is pcm.",
    )
    settings: tuple[Setting, ...] = Field(
        default=(), description="Additional model-specific solvent settings."
    )

    @model_validator(mode="after")
    def check_settings(self) -> Self:
        """Return settings consistent with the selected solvent implementation.

        Raises:
            ValueError: Settings override dedicated choices or name another solver.
        """
        if self.kind != "ddx":
            if self.settings or self.ddx != DDXSolvation():
                raise ValueError("Use dedicated PCM fields without DDX settings")
            self.pcm.input_text(self.solvent)
            return self
        if self.pcm != PCMSolverSolvation():
            raise ValueError("PCM choices require kind pcm")
        names = [item.name.casefold() for item in self.settings]
        reserved = {
            "ddx",
            "pcm",
            "ddx_model",
            "ddx_solvent",
            "ddx_solvent_epsilon",
            "ddx_solvent_epsilon_optical",
            "ddx_radii",
            "ddx_radii_set",
            "ddx_radii_scaling",
            "ddx_solvent_kappa",
        }
        if len(names) != len(set(names)) or any(
            item.name.casefold() in reserved
            or not item.name.casefold().startswith("ddx_")
            or (item.module or "ddx").casefold() != "ddx"
            for item in self.settings
        ):
            raise ValueError(
                "Use unique DDX numerical settings and dedicated solvent fields"
            )
        return self

    def engine_settings_for(
        self, units: Literal["angstrom", "bohr"]
    ) -> tuple[Setting, ...]:
        """Return solvent options with screening in the geometry's units.

        Args:
            units: Native molecule length units, used for inverse screening length.

        Returns:
            Explicit controls; PCMSolver text is supplied separately inside the call.
        """
        if self.kind != "ddx":
            return (
                Setting(name="pcm_scf_type", module="PCM", value=self.pcm.scf_type),
            )
        settings: tuple[Setting, ...] = (
            Setting(name="ddx_model", module="DDX", value=self.ddx.model),
            Setting(name="ddx_solvent", module="DDX", value=self.solvent),
            Setting(name="ddx_radii_set", module="DDX", value=self.ddx.radii_set),
            Setting(
                name="ddx_radii_scaling", module="DDX", value=self.ddx.radii_scaling
            ),
        )
        if self.ddx.dielectric_constant is not None:
            settings += (
                Setting(
                    name="ddx_solvent_epsilon",
                    module="DDX",
                    value=self.ddx.dielectric_constant,
                ),
            )
        if self.ddx.screening_inverse_bohr is not None:
            settings += (
                Setting(
                    name="ddx_solvent_kappa",
                    module="DDX",
                    value=self.ddx.screening_inverse_bohr
                    / (BOHR_ANGSTROM if units == "angstrom" else 1),
                ),
            )
        return settings + tuple(
            Setting(name=item.name, module="DDX", value=item.value)
            for item in self.settings
        )


class ElectronicTarget(Record):
    """Name an excited-state root without claiming physical state tracking."""

    root: int = Field(
        ge=1,
        description="One-based root in the producing response's energy-ordered "
        "requested set; a symmetry label selects a symmetry-resolved convention.",
    )
    symmetry: str | None = Field(
        default=None, description="Requested irreducible representation, if specified."
    )
    multiplicity: int | None = Field(
        default=None, ge=1, description="Requested excited-state spin multiplicity."
    )


class ComponentRequirement(Record):
    """Identify an optional component needed by the constructed calculation plan."""

    name: str = Field(min_length=1, description="Required component name.")
    version: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Informational version if supplied; constructed plans leave it null."
        ),
    )


class Model(Record):
    """Specify the method and all declared choices that distinguish calculations.

    Scientific/input support for combinations requires a capability catalog. Fields
    describe the requested model; they do not supply a scientific recommendation.
    """

    method: str = Field(
        min_length=1, pattern=r"\S", description="Psi4 method name, such as scf or mp2."
    )
    basis: str = Field(
        min_length=1,
        pattern=r"\S",
        description="Default orbital basis for all centers.",
    )
    reference: Literal["rhf", "uhf", "rohf"] = Field(
        description="SCF reference to request explicitly."
    )
    frozen_core: bool = Field(
        default=False, description="Whether to request Psi4's frozen-core treatment."
    )
    puream: bool = Field(
        default=True,
        description="Use spherical harmonics; false selects Cartesian shells.",
    )
    basis_assignments: tuple[BasisAssignment, ...] = Field(
        default=(),
        description="Ordered orbital-basis overrides for elements or atom labels.",
    )
    auxiliary_bases: tuple[AuxiliaryBasis, ...] = Field(
        default=(), description="Explicit fitting bases, with one entry per role."
    )
    ecps: tuple[ECP, ...] = Field(
        default=(),
        description="ECP identities and replaced-electron counts by element.",
    )
    environment: Environment | None = Field(
        default=None, description="Implicit solvent; null requests no implicit solvent."
    )
    external_potential: ExternalPotential | None = Field(
        default=None,
        description="Explicit point, Gaussian, or matrix potential for this model.",
    )
    electric_field: tuple[float, float, float] | None = Field(
        default=None, description="Uniform electric-field vector in atomic units."
    )
    electronic_target: ElectronicTarget | None = Field(
        default=None,
        description="Excited-state root; null selects the method's ordinary state.",
    )
    tdscf: TDSCFAnalysis | None = Field(
        default=None,
        description="Explicit TD-SCF root set, spin sector, and response equations; "
        "null makes no response-operation claim.",
    )
    settings: tuple[Setting, ...] = Field(
        default=(),
        description="Additional explicit numerical and method options, scoped locally.",
    )

    @model_validator(mode="after")
    def check_unique_settings(self) -> Self:
        """Return the model after rejecting ambiguous settings and duplicate roles.

        Raises:
            ValueError: A choice is duplicated or overrides a dedicated model field.
        """
        keys = [item.key for item in self.settings]
        reserved = {
            "basis",
            "reference",
            "freeze_core",
            "perturb_h",
            "perturb_with",
            "perturb_dipole",
            "puream",
            "pcm",
            "ddx",
            "tdscf_states",
            "tdscf_triplets",
            "tdscf_tda",
            "tdscf_r_convergence",
            "tdscf_maxiter",
            "tdscf_tdm_print",
        }
        if len(keys) != len(set(keys)):
            raise ValueError("Model settings must have unique module/name pairs")
        if any(
            item.name.casefold() in reserved
            or item.name.casefold().startswith("df_basis_")
            or item.name.casefold().startswith("ddx_")
            or item.name.casefold().startswith("pcm_")
            or item.name.casefold() == "pcmsolver_parsed_fname"
            for item in self.settings
        ):
            raise ValueError(
                "Use dedicated fields for basis, reference, core, field, and solvent"
            )
        for values in (
            [item.role.casefold() for item in self.auxiliary_bases],
            [item.element for item in self.ecps],
        ):
            if len(values) != len(set(values)):
                raise ValueError("Fitting-basis roles and ECP elements must be unique")
        return self

    @property
    def identity(self) -> str:
        """Return an identity with normalized method, basis, and option names.

        Literal option values and ordered basis assignments remain distinct.
        Method aliases are not resolved.
        """
        return self._identity(self.reference)

    @property
    def reaction_treatment_identity(self) -> str:
        """Return normalized model choices excluding the species' SCF reference.

        Reaction bookkeeping groups these identities to require balanced
        computational treatments across all species. All other model choices
        remain distinct; reference selection stays explicit for each species.
        """
        return self._identity(None)

    @property
    def basis_treatment_identity(self) -> str:
        """Return normalized model choices excluding orbital and fitting basis names.

        Basis-limit contracts check those names against separate family/cardinal
        evidence. Fitting roles and all other model choices remain distinct.
        """
        return self._identity(self.reference, basis_independent=True)

    @property
    def solvent_free_identity(self) -> str:
        """Return the electronic treatment identity with implicit solvent removed."""
        return self._identity(self.reference, solvent_independent=True)

    def _identity(
        self,
        reference: str | None,
        *,
        basis_independent: bool = False,
        solvent_independent: bool = False,
    ) -> str:
        settings = sorted(
            (item.key, item.model_dump_json(include={"value"}))
            for item in self.settings
        )
        return json.dumps(
            (
                self.method.strip().casefold(),
                None if basis_independent else self.basis.strip().casefold(),
                reference,
                self.frozen_core,
                self.puream,
                tuple(
                    (item.target, item.basis.strip().casefold())
                    for item in self.basis_assignments
                ),
                sorted(
                    (
                        item.role.casefold(),
                        None if basis_independent else item.basis.strip().casefold(),
                    )
                    for item in self.auxiliary_bases
                ),
                sorted(
                    (item.element, item.name, item.core_electrons) for item in self.ecps
                ),
                self.environment.model_dump_json()
                if self.environment and not solvent_independent
                else None,
                self.external_potential.model_dump_json()
                if self.external_potential
                else None,
                self.electric_field,
                self.electronic_target.model_dump_json()
                if self.electronic_target
                else None,
                self.tdscf.model_dump_json() if self.tdscf else None,
                settings,
            ),
            separators=(",", ":"),
        )

    @property
    def engine_settings(self) -> tuple[Setting, ...]:
        """Return the explicit engine options lowered for this model, in order.

        Dedicated basis, reference, core, and angular-representation choices
        precede fitting bases, additional settings, and an explicit electric
        field. Unrepresented ambient options are not inferred from defaults.
        Screening uses bohr here; use engine_settings_for() for other molecule units.
        """
        return self.engine_settings_for("bohr")

    def engine_settings_for(
        self, units: Literal["angstrom", "bohr"]
    ) -> tuple[Setting, ...]:
        """Return native settings for a geometry's length units.

        Args:
            units: Native molecule units, also used for LPB screening conversion.

        Returns:
            Fully declared model options, including explicit solvent activation.
        """
        settings = (
            Setting(name="basis", value=self.basis.strip()),
            Setting(name="reference", value=self.reference),
            Setting(name="freeze_core", value=self.frozen_core),
            Setting(name="puream", value=self.puream),
            Setting(
                name="ddx",
                value=self.environment is not None and self.environment.kind == "ddx",
            ),
            Setting(
                name="pcm",
                value=self.environment is not None and self.environment.kind == "pcm",
            ),
            *(
                Setting(name=item.role, value=item.basis)
                for item in self.auxiliary_bases
            ),
            *self.settings,
            *(self.environment.engine_settings_for(units) if self.environment else ()),
        )
        if self.electric_field is not None:
            settings += (
                Setting(name="perturb_h", value=True),
                Setting(name="perturb_with", value="dipole"),
                Setting(name="perturb_dipole", value=self.electric_field),
            )
        if self.tdscf is not None:
            settings += (
                Setting(
                    name="tdscf_states", module="SCF", value=self.tdscf.native_states
                ),
                Setting(
                    name="tdscf_triplets",
                    module="SCF",
                    value=self.tdscf.native_triplets,
                ),
                Setting(
                    name="tdscf_tda",
                    module="SCF",
                    value=self.tdscf.approximation == "tda",
                ),
                Setting(
                    name="tdscf_r_convergence",
                    module="SCF",
                    value=self.tdscf.residual_threshold,
                ),
                Setting(
                    name="tdscf_maxiter", module="SCF", value=self.tdscf.max_iterations
                ),
            )
        return settings


class QuantityType(Record):
    """Describe the meaning, unit, and tensor layout of an expected product."""

    meaning: str = Field(
        min_length=1,
        description="Physical meaning, such as electronic_energy.",
    )
    unit: str = Field(
        min_length=1,
        description="Explicit unit, such as hartree, hartree/bohr, or cm^-1.",
    )
    shape: tuple[int | Literal["atoms", "3*atoms", "modes"], ...] = Field(
        default=(), description="Tensor dimensions; an empty tuple denotes a scalar."
    )
    frame: str | None = Field(
        default=None,
        description="Frame identity for oriented quantities; null for scalars.",
    )
    number_kind: Literal["real", "complex"] = Field(
        default="real",
        description="Element domain; complex frequencies can include imaginary modes.",
    )

    @model_validator(mode="after")
    def check_dimensions(self) -> Self:
        """Return the quantity type after rejecting non-positive dimensions.

        Raises:
            ValueError: A concrete dimension is zero or negative.
        """
        if any(isinstance(size, int) and size <= 0 for size in self.shape):
            raise ValueError("Tensor dimensions must be positive")
        return self


class NativeProductBinding(Record):
    """Locate a quantity in a native record without decoding any value."""

    quantity: str = Field(min_length=1, description="Expected quantity identity.")
    key: str = Field(min_length=1, description="Top-level native record member.")
    encoding: Literal["raw_array", "qcelemental_datum_json"] = Field(
        description="Raw array or JSON-encoded QCElemental Datum string."
    )


class NativeProductOutput(Record):
    """Declare a native engine output file needed by a separate result consumer."""

    producer: str = Field(min_length=1, description="Producing calculation identity.")
    format: Literal["psi4_vibrec"] = Field(
        default="psi4_vibrec",
        description="Native vibrational/thermal JSON record format.",
    )
    label: str = Field(
        description="Explicit unique writer label used for this calculation."
    )
    filename_template: str = Field(
        description="File basename with {pid} filled by the engine process ID."
    )
    directory: Literal["engine_output_directory"] = Field(
        default="engine_output_directory",
        description="Output directory selected by the separate execution consumer.",
    )
    bindings: tuple[NativeProductBinding, ...] = Field(
        description="Quantity locations and native encodings; no values are read."
    )

    @property
    def products(self) -> tuple[str, ...]:
        """Return the declared expected quantity IDs in record-path order."""
        return tuple(item.quantity for item in self.bindings)


class NativeVariableBinding(Record):
    """Describe a transient native quantity for a separate execution/result consumer.

    This is a declaration only. Export does not retrieve values, add snapshots,
    or preserve them after a later calculation changes the application's state.
    """

    producer: str = Field(min_length=1, description="Producing calculation step ID.")
    quantity: str = Field(min_length=1, description="Expected named-product identity.")
    key: str = Field(min_length=1, description="Native Psi4 QCVariable name.")
    unit: str = Field(
        min_length=1, description="Native quantity unit, such as hartree."
    )
    storage: Literal["scalar", "array"] = Field(
        default="scalar", description="Native scalar or array variable storage."
    )
    lifetime: Literal["after_producer_before_next_calculation"] = Field(
        default="after_producer_before_next_calculation",
        description="The separate consumer must collect before native state changes.",
    )


class ExpectedQuantity(Record):
    """Trace an expected product to its geometry, system, state, and model."""

    id: str = Field(min_length=1, description="Stable expected-artifact identity.")
    producer: str = Field(
        min_length=1, description="Calculation or expression step ID."
    )
    quantity: QuantityType = Field(description="Expected physical meaning and layout.")
    system: str | None = Field(
        default=None, description="Original molecular input; null for an expression."
    )
    geometry: str | None = Field(
        default=None,
        description="Geometry where the quantity is defined; null for an expression.",
    )
    model: Model | None = Field(
        default=None, description="Producing model; null for an algebraic expression."
    )
    operands: tuple[str, ...] = Field(
        default=(), description="Preceding quantity IDs used by a symbolic expression."
    )
    state: ElectronicState | None = Field(
        default=None,
        description="Electronic state of the input reference; excited products "
        "carry their selected root separately. Null for expressions.",
    )
    product: ProductName | None = Field(
        default=None,
        description="Named secondary product; null for a primary return or expression.",
    )
    electronic_target: ElectronicTarget | None = Field(
        default=None,
        description="Requested root selector for an excited-state product.",
    )
    analysis: VibrationalAnalysis | None = Field(
        default=None,
        description="Explicit vibrational/thermal context, when applicable.",
    )
    sapt: SAPTAnalysis | None = Field(
        default=None,
        description="Producing SAPT fragment/basis/induction context; null otherwise.",
    )


class GeometryArtifact(Record):
    """Track known or future coordinates while retaining their molecular identity."""

    id: str = Field(
        min_length=1, description="Geometry identity referenced by later steps."
    )
    system: str = Field(min_length=1, description="Original molecular-input identity.")
    source: str | None = Field(
        default=None, description="Parent geometry identity; null for an initial input."
    )
    producer: str | None = Field(
        default=None,
        description="Producing step; null for coordinates supplied as input.",
    )
    coordinates_known: bool = Field(
        description="Whether coordinates are available during input construction."
    )
    atom_ids: tuple[str, ...] = Field(
        description="Stable center IDs in coordinate order."
    )
    frame: str = Field(
        description="Coordinate-frame provenance retained by this artifact."
    )


class GoalCoverage(Record):
    """Locate the proposed steps that address one mandatory scientific goal."""

    goal: str = Field(description="Scientific-request goal ID.")
    steps: tuple[str, ...] = Field(description="Proposed steps that declare this goal.")
    status: Literal["covered", "missing", "incompatible"] = Field(
        description="Whether one compatible step addresses the complete goal."
    )
