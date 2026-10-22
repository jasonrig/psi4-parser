"""Construct checked Psi4 calculation plans from independent scientific intent.

Save molecular inputs and mandatory goals in ScientificRequest, then call
propose(). Shared scientific/input contracts apply by default across Psi4 releases;
an explicit CapabilityCatalog can extend coverage. Compose supported goals
with finite_study(), fragment_expansion(), reaction_expansion(), and
extrapolation_expansion(). export_bundle()
saves accepted intent, plan, evidence, verification, native input, and symbolic recipes
for a separate consumer. No calculation execution or result parsing is performed.
ProductGoal requires named quantities independently from primary returns.
VibrationalAnalysis records explicit thermal conditions and projection choices;
native frequency records preserve products for a separate result consumer.
ReactionThermochemistry composes native or explicitly hybrid thermal reactions
with common conditions and species-specific symmetry and electronic states.
InversePowerExtrapolation retains a chosen correction convergence model;
basis-family/cardinal evidence and exact formula checks remain separate.
ExponentialExtrapolation retains explicit HF decay choices and a certified bound
on rational coefficient error. Both models compose through extrapolation_expansion().

Plan also supports explicit relationships through UsesGeometry, SameGeometry,
SameModel, and EnergyFormula. CoordinateValue and CoordinateRange require input
or constrained future geometry to meet explicit targets. verify(plan) alone checks
those relationships and operation prerequisites without independent intent coverage.
build() returns a
builder JobSpec for an accepted plan; render() produces input.

Use constructor signatures and selected model_fields for discovery. Each record
has its own JSON schema and dump/validate methods. Proofs cover encoded
obligations under capability evidence and listed assumptions; they do not promise
scientific accuracy or convergence. An installed Psi4 executable is not required.
"""

from psi4_parser.formal.capabilities import (
    BasisCapability,
    BasisFunctions,
    CapabilityCatalog,
    ComponentCapability,
    EnvironmentCapability,
    Evidence,
    MethodCapability,
    OptionCapability,
    OptionCondition,
    ProductCapability,
    ProductCase,
    discover_capabilities,
    discover_products,
)
from psi4_parser.formal.catalog_composition import combine_catalogs
from psi4_parser.formal.catalogs import CatalogInfo, available_catalogs, load_catalog
from psi4_parser.formal.construction import VerificationError, build, render
from psi4_parser.formal.contracts import OperationContract, operation_contracts
from psi4_parser.formal.coordinate_models import CoordinateRange, CoordinateValue
from psi4_parser.formal.discovery import describe_contracts, describe_schema
from psi4_parser.formal.excited_models import TDSCFAnalysis
from psi4_parser.formal.exporting import BundleManifest, ExportedBundle, export_bundle
from psi4_parser.formal.extrapolation_models import (
    BasisSequence,
    ExponentialExtrapolation,
    ExtrapolationPoint,
    InversePowerExtrapolation,
)
from psi4_parser.formal.extrapolation_plans import (
    BasisCorrectionPoint,
    BasisEnergyPoint,
    ExtrapolationExpansion,
    ExtrapolationStudy,
    ReferenceExtrapolationStudy,
    extrapolation_expansion,
)
from psi4_parser.formal.fragment_plans import (
    FragmentExpansion,
    FragmentStudy,
    SubsystemState,
    fragment_expansion,
)
from psi4_parser.formal.intent import (
    CalculationGoal,
    ExpressionGoal,
    GoalTerm,
    ProductGoal,
    ScientificRequest,
    SubsystemGoal,
)
from psi4_parser.formal.interface_models import CapabilityQuery
from psi4_parser.formal.models import (
    Calculation,
    Combination,
    Diagnostic,
    EnergyFormula,
    EnergyTerm,
    Limits,
    Obligation,
    Plan,
    Product,
    Report,
    SameGeometry,
    SameModel,
    Subsystem,
    UsesGeometry,
    Witness,
)
from psi4_parser.formal.planning import ChosenModel, Proposal, SearchLimits, propose
from psi4_parser.formal.products import product_quantity
from psi4_parser.formal.reaction_plans import (
    ReactionExpansion,
    ReactionParticipant,
    ReactionQuantity,
    ReactionStudy,
    ReactionThermochemistry,
    reaction_expansion,
)
from psi4_parser.formal.reuse import CalculationReuse, PlanningPreferences
from psi4_parser.formal.science import (
    ECP,
    AuxiliaryBasis,
    ComponentRequirement,
    DDXSolvation,
    ElectronicTarget,
    Environment,
    ExpectedQuantity,
    GeometryArtifact,
    Model,
    NativeProductBinding,
    NativeProductOutput,
    NativeVariableBinding,
    QuantityType,
    Rational,
    SAPTAnalysis,
    Setting,
    ThermalConditions,
    VibrationalAnalysis,
)
from psi4_parser.formal.solvation import PCMSolverSolvation
from psi4_parser.formal.stored_inputs import (
    MoleculeBinding,
    RequestTemplate,
    StoredMolecule,
)
from psi4_parser.formal.studies import CaseModels, StudyCase, finite_study
from psi4_parser.formal.verification import verify
from psi4_parser.formal.workspace import PlanningWorkspace

__all__ = [
    "ECP",
    "AuxiliaryBasis",
    "BasisCapability",
    "BasisCorrectionPoint",
    "BasisEnergyPoint",
    "BasisFunctions",
    "BasisSequence",
    "BundleManifest",
    "Calculation",
    "CalculationGoal",
    "CalculationReuse",
    "CapabilityCatalog",
    "CapabilityQuery",
    "CaseModels",
    "CatalogInfo",
    "ChosenModel",
    "Combination",
    "ComponentCapability",
    "ComponentRequirement",
    "CoordinateRange",
    "CoordinateValue",
    "DDXSolvation",
    "Diagnostic",
    "ElectronicTarget",
    "EnergyFormula",
    "EnergyTerm",
    "Environment",
    "EnvironmentCapability",
    "Evidence",
    "ExpectedQuantity",
    "ExponentialExtrapolation",
    "ExportedBundle",
    "ExpressionGoal",
    "ExtrapolationExpansion",
    "ExtrapolationPoint",
    "ExtrapolationStudy",
    "FragmentExpansion",
    "FragmentStudy",
    "GeometryArtifact",
    "GoalTerm",
    "InversePowerExtrapolation",
    "Limits",
    "MethodCapability",
    "Model",
    "MoleculeBinding",
    "NativeProductBinding",
    "NativeProductOutput",
    "NativeVariableBinding",
    "Obligation",
    "OperationContract",
    "OptionCapability",
    "OptionCondition",
    "PCMSolverSolvation",
    "Plan",
    "PlanningPreferences",
    "PlanningWorkspace",
    "Product",
    "ProductCapability",
    "ProductCase",
    "ProductGoal",
    "Proposal",
    "QuantityType",
    "Rational",
    "ReactionExpansion",
    "ReactionParticipant",
    "ReactionQuantity",
    "ReactionStudy",
    "ReactionThermochemistry",
    "ReferenceExtrapolationStudy",
    "Report",
    "RequestTemplate",
    "SAPTAnalysis",
    "SameGeometry",
    "SameModel",
    "ScientificRequest",
    "SearchLimits",
    "Setting",
    "StoredMolecule",
    "StudyCase",
    "Subsystem",
    "SubsystemGoal",
    "SubsystemState",
    "TDSCFAnalysis",
    "ThermalConditions",
    "UsesGeometry",
    "VerificationError",
    "VibrationalAnalysis",
    "Witness",
    "available_catalogs",
    "build",
    "combine_catalogs",
    "describe_contracts",
    "describe_schema",
    "discover_capabilities",
    "discover_products",
    "export_bundle",
    "extrapolation_expansion",
    "finite_study",
    "fragment_expansion",
    "load_catalog",
    "operation_contracts",
    "product_quantity",
    "propose",
    "reaction_expansion",
    "render",
    "verify",
]
