"""Define first-class native statements and explicit mixed Python templates."""

from typing import Annotated, Literal

from pydantic import Field

from psi4_parser._solver_blocks import CFourFields, PCMFields
from psi4_parser.job.model import FragmentSeparator, Model, Nucleus, Number, Units
from psi4_parser.job.molecule import Molecule

_OPTION_REFERENCE_NAME_EXAMPLES: list[str] = ["basis_name"]
_OPTION_ASSIGNMENT_KEY_EXAMPLES: list[str] = ["basis", "e_convergence"]
_BASIS_ASSIGNMENT_BASIS_EXAMPLES: list[str] = ["cc-pvdz", "custom"]
_BASIS_ASSIGNMENT_TARGET_EXAMPLES: list[str] = ["H", "C1"]
_MEMORY_UNITS_EXAMPLES: list[str] = ["GB", "GiB", "MB"]


class Python(Model):
    """Python text to include in a Psi4 input."""

    kind: Literal["python"] = Field(
        default="python", description="Selects Python text to include in the input."
    )
    source: str = Field(
        description=(
            "Python statements, or text surrounding a Psi4 block in a mixed statement."
        )
    )


class OptionExpression(Model):
    """An option value written in Psi4 input notation."""

    kind: Literal["option_expression"] = Field(
        default="option_expression",
        description="Selects a Psi4 option value written as input text.",
    )
    source: str = Field(description="Psi4 option value as input text, such as cc-pvdz.")


class OptionReference(Model):
    """Use an earlier Python value as a Psi4 option."""

    kind: Literal["option_reference"] = Field(
        default="option_reference",
        description="Selects an earlier Python value for an option.",
    )
    name: str = Field(
        description=(
            "Earlier Python name; Psi4 writes this reference with a dollar sign."
        ),
        min_length=1,
        examples=_OPTION_REFERENCE_NAME_EXAMPLES,
    )


class OptionArray(Model):
    """An array of Psi4 option values, including nested arrays."""

    kind: Literal["option_array"] = Field(
        default="option_array",
        description="Selects an array of Psi4 option values.",
    )
    parts: tuple[OptionValue, ...] = Field(
        default=(),
        description=(
            "Array contents in order; text entries include any separating commas."
        ),
    )


type OptionValue = Annotated[
    OptionExpression | OptionReference | OptionArray,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="A Psi4 option expression, named Python value, or array.",
    ),
]


class OptionAssignment(Model):
    """One Psi4 setting and its value."""

    key: str = Field(
        description="Psi4 setting name, such as basis or e_convergence.",
        min_length=1,
        examples=_OPTION_ASSIGNMENT_KEY_EXAMPLES,
    )
    value: OptionValue = Field(
        description="Setting value as input text, a named Python value, or an array."
    )


class SetOptions(Model):
    """Settings applied globally or to selected Psi4 modules."""

    kind: Literal["set"] = Field(
        default="set", description="Selects a group of Psi4 settings."
    )
    modules: tuple[str, ...] = Field(
        default=(),
        description=(
            "Psi4 module names, such as scf; an empty list selects global settings."
        ),
    )
    assignments: tuple[OptionAssignment, ...] = Field(
        default=(), description="Settings to apply in the supplied order."
    )
    style: Literal["inline", "block"] = Field(
        default="block",
        description="Write settings on one line or inside a braced block.",
    )


class BasisAssignment(Model):
    """Apply a basis set to all atoms, an element, or an atom label."""

    kind: Literal["basis_assignment"] = Field(
        default="basis_assignment",
        description="Selects a basis-set assignment.",
    )
    basis: str = Field(
        description=(
            "Basis-set name, such as cc-pvdz, or a label defined in this block."
        ),
        min_length=1,
        examples=_BASIS_ASSIGNMENT_BASIS_EXAMPLES,
    )
    target: str | None = Field(
        default=None,
        description="Element or atom label; null applies the basis to all atoms.",
        min_length=1,
        examples=_BASIS_ASSIGNMENT_TARGET_EXAMPLES,
    )


class BasisLabel(Model):
    """Name a section of basis-set data for use by assignments."""

    kind: Literal["basis_label"] = Field(
        default="basis_label",
        description="Selects a named section of basis-set data.",
    )
    name: str = Field(
        description="Section name used by basis assignments in this block.",
        min_length=1,
    )


class BasisData(Model):
    """One line of Gaussian basis-set or effective core potential data."""

    kind: Literal["basis_data"] = Field(
        default="basis_data",
        description="Selects one line of basis-set data.",
    )
    text: str = Field(
        description="One line of Gaussian basis-set or effective core potential data."
    )


type BasisRecord = Annotated[
    BasisAssignment | BasisLabel | BasisData,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="A basis assignment, section label, or line of basis-set data.",
    ),
]


class Basis(Model):
    """Define an orbital or auxiliary basis set using assignments and data lines."""

    kind: Literal["basis"] = Field(
        default="basis", description="Selects a basis-set definition."
    )
    role: str = Field(
        default="basis",
        description="Psi4 basis setting to define, such as basis or df_basis_scf.",
        pattern=r"^(?:basis(?:_relativistic)?|df_basis_(?:scf|mp2|cc|sapt|sad|dct))$",
    )
    name: str | None = Field(
        default=None, description="Optional Python name for this basis definition."
    )
    records: tuple[BasisRecord, ...] = Field(
        default=(),
        description=(
            "Basis assignments, section labels, and data lines in input order."
        ),
    )


class PointCharge(Model):
    """A point charge at a specified position."""

    kind: Literal["point_charge"] = Field(
        default="point_charge",
        description="Selects a point charge in an external-potential block.",
    )
    charge: Number = Field(
        description="Signed point charge in elementary-charge units."
    )
    position: tuple[Number, Number, Number] = Field(
        description="Charge x, y, and z coordinates in the block's length unit."
    )


class ExternalAtom(Model):
    """An atom in an external diffuse-charge fragment."""

    kind: Literal["external_atom"] = Field(
        default="external_atom",
        description="Selects an atom in an external diffuse-charge fragment.",
    )
    nucleus: Nucleus = Field(
        description="Element label and any isotope or ghost-center settings."
    )
    position: tuple[Number, Number, Number] = Field(
        description="Atom x, y, and z coordinates in the block's length unit."
    )


class ExternalBasis(Model):
    """An orbital or fitting basis for an external fragment."""

    kind: Literal["external_basis"] = Field(
        default="external_basis",
        description="Selects a basis setting for an external fragment.",
    )
    role: Literal["basis", "df_basis_scf"] = Field(
        description="Basis setting for the external fragment."
    )
    value: str = Field(description="Basis-set name or Psi4 basis expression.")


type ExternalRecord = Annotated[
    PointCharge | ExternalAtom | ExternalBasis | Units | FragmentSeparator,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "A charge, atom, basis setting, unit declaration, or fragment separator."
        ),
    ),
]


class External(Model):
    """Point and diffuse charges in Psi4's legacy external-block syntax."""

    kind: Literal["external"] = Field(
        default="external",
        description="Selects a legacy external-potential block.",
    )
    name: str | None = Field(
        default=None, description="Optional name for this external potential."
    )
    records: tuple[ExternalRecord, ...] = Field(
        default=(),
        description=(
            "Charges, atoms, basis settings, units, and separators in input order."
        ),
    )


class PCM(PCMFields, Model):
    """A pcm block containing PCMSolver solvent settings.

    Attributes:
        name: Optional block name as written in Psi4 input.
        body: PCMSolver sections retained as text, including their line breaks.
    """


class CFour(CFourFields, Model):
    """A cfour block containing CFOUR configuration text.

    Attributes:
        name: Optional block name as written in Psi4 input.
        body: CFOUR text retained with its original line breaks.
    """


class Memory(Model):
    """The maximum memory allocated to Psi4."""

    kind: Literal["memory"] = Field(
        default="memory", description="Selects the memory limit for Psi4."
    )
    amount: Number = Field(description="Memory limit in the chosen units.")
    units: str = Field(
        description="Memory unit, such as MB, GB, MiB, or GiB.",
        pattern=r"^[kKmMgGtTpPbBeE][iI]?[bB]$",
        examples=_MEMORY_UNITS_EXAMPLES,
    )
    prefix: str = Field(
        default="",
        description=(
            "Text preceding the memory keyword in legacy input; usually empty."
        ),
    )


type NativeNode = Annotated[
    Molecule | SetOptions | Basis | External | PCM | CFour | Memory,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "A Psi4 molecule, settings, basis, external potential, solvent, "
            "CFOUR, or memory block."
        ),
    ),
]


class PythonTemplate(Model):
    """Python statements containing Psi4 blocks between text sections."""

    kind: Literal["python_template"] = Field(
        default="python_template",
        description="Selects Python text with Psi4 blocks inserted between its parts.",
    )
    parts: tuple[TemplatePart, ...] = Field(
        description=(
            "Python text and Psi4 blocks in the order they appear in the input."
        )
    )


type TemplatePart = Annotated[
    Python | Molecule | SetOptions | Basis | External | PCM | CFour | Memory,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="Python text or a Psi4 block within a larger Python statement.",
    ),
]

type Node = Annotated[
    Python
    | PythonTemplate
    | Molecule
    | SetOptions
    | Basis
    | External
    | PCM
    | CFour
    | Memory,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description="A Python statement, Psi4 block, or combination of the two.",
    ),
]


class Job(Model):
    """Python statements and Psi4 blocks that form a complete input."""

    body: tuple[Node, ...] = Field(
        default=(),
        description="Python statements and Psi4 blocks in input order.",
    )


OptionArray.model_rebuild()
PythonTemplate.model_rebuild()
Job.model_rebuild()
