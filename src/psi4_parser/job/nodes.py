"""Define first-class native statements and explicit mixed Python templates."""

from typing import Annotated, Literal

from pydantic import Field

from psi4_parser.job.model import FragmentSeparator, Model, Nucleus, Number, Units
from psi4_parser.job.molecule import Molecule

_OPTION_REFERENCE_NAME_EXAMPLES: list[str] = ["basis_name"]
_OPTION_ASSIGNMENT_KEY_EXAMPLES: list[str] = ["basis", "e_convergence"]
_BASIS_ASSIGNMENT_BASIS_EXAMPLES: list[str] = ["cc-pvdz", "custom"]
_BASIS_ASSIGNMENT_TARGET_EXAMPLES: list[str] = ["H", "C1"]
_MEMORY_UNITS_EXAMPLES: list[str] = ["GB", "GiB", "MB"]


class Python(Model):
    """Retain Python text for contextual validation after JSON validation.

    Attributes:
        source: Python source, or a text segment in a mixed Python template.
    """

    kind: Literal["python"] = Field(
        default="python", description="Discriminator identifying the Python variant."
    )
    source: str = Field(
        description="Python source, or a text segment in a mixed Python template."
    )


class OptionExpression(Model):
    """Retain a native option expression with Psi4's quoting rules.

    Attributes:
        source: Expression spelling before native quoting and substitution.
    """

    kind: Literal["option_expression"] = Field(
        default="option_expression",
        description="Discriminator identifying the OptionExpression variant.",
    )
    source: str = Field(
        description="Expression spelling before native quoting and substitution."
    )


class OptionReference(Model):
    """Reference a Python binding from an option assignment.

    Attributes:
        name: Python name following the native dollar marker.
    """

    kind: Literal["option_reference"] = Field(
        default="option_reference",
        description="Discriminator identifying the OptionReference variant.",
    )
    name: str = Field(
        description="Python name following the native dollar marker.",
        min_length=1,
        examples=_OPTION_REFERENCE_NAME_EXAMPLES,
    )


class OptionArray(Model):
    """Represent nested option arrays without evaluating their expressions.

    Attributes:
        parts: Ordered expression segments and nested arrays, including commas.
    """

    kind: Literal["option_array"] = Field(
        default="option_array",
        description="Discriminator identifying the OptionArray variant.",
    )
    parts: tuple[OptionValue, ...] = Field(
        default=(),
        description="Ordered expression segments and nested arrays, including commas.",
    )


type OptionValue = Annotated[
    OptionExpression | OptionReference | OptionArray,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class OptionAssignment(Model):
    """Assign one option while preserving order and Python references.

    Attributes:
        key: Native option name.
        value: Native expression, Python reference, or nested array.
    """

    key: str = Field(
        description="Native option name.",
        min_length=1,
        examples=_OPTION_ASSIGNMENT_KEY_EXAMPLES,
    )
    value: OptionValue = Field(
        description="Native expression, Python reference, or nested array."
    )


class SetOptions(Model):
    """Specify global or module-scoped native options.

    Attributes:
        modules: Ordered native module list; empty means global options.
        assignments: Option assignments in their original execution order.
        style: Inline command or braced block.
    """

    kind: Literal["set"] = Field(
        default="set", description="Discriminator identifying the SetOptions variant."
    )
    modules: tuple[str, ...] = Field(
        default=(),
        description="Ordered native module list; empty means global options.",
    )
    assignments: tuple[OptionAssignment, ...] = Field(
        default=(), description="Option assignments in their original execution order."
    )
    style: Literal["inline", "block"] = Field(
        default="block", description="Inline command or braced block."
    )


class BasisAssignment(Model):
    """Assign a basis globally or to an element or atom label.

    Attributes:
        basis: Named basis or local basis payload label.
        target: Optional element or atom label; omitted means all atoms.
    """

    kind: Literal["basis_assignment"] = Field(
        default="basis_assignment",
        description="Discriminator identifying the BasisAssignment variant.",
    )
    basis: str = Field(
        description="Named basis or local basis payload label.",
        min_length=1,
        examples=_BASIS_ASSIGNMENT_BASIS_EXAMPLES,
    )
    target: str | None = Field(
        default=None,
        description="Optional element or atom label; omitted means all atoms.",
        min_length=1,
        examples=_BASIS_ASSIGNMENT_TARGET_EXAMPLES,
    )


class BasisLabel(Model):
    """Introduce a named basis-data section.

    Attributes:
        name: Native label inside square brackets.
    """

    kind: Literal["basis_label"] = Field(
        default="basis_label",
        description="Discriminator identifying the BasisLabel variant.",
    )
    name: str = Field(description="Native label inside square brackets.", min_length=1)


class BasisData(Model):
    """Retain a record in the embedded Gaussian basis/ECP language.

    Attributes:
        text: Basis-reader record, preserved without Python interpretation.
    """

    kind: Literal["basis_data"] = Field(
        default="basis_data",
        description="Discriminator identifying the BasisData variant.",
    )
    text: str = Field(
        description="Basis-reader record, preserved without Python interpretation."
    )


type BasisRecord = Annotated[
    BasisAssignment | BasisLabel | BasisData,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Basis(Model):
    """Define a basis for any supported native basis role.

    Attributes:
        role: Native role, such as basis or df_basis_scf.
        name: Optional user-supplied binding for this definition.
        records: Ordered assignments, labels, and embedded GBS/ECP records.
    """

    kind: Literal["basis"] = Field(
        default="basis", description="Discriminator identifying the Basis variant."
    )
    role: str = Field(
        default="basis",
        description="Native role, such as basis or df_basis_scf.",
        pattern=r"^(?:basis(?:_relativistic)?|df_basis_(?:scf|mp2|cc|sapt|sad|dct))$",
    )
    name: str | None = Field(
        default=None, description="Optional user-supplied binding for this definition."
    )
    records: tuple[BasisRecord, ...] = Field(
        default=(),
        description="Ordered assignments, labels, and embedded GBS/ECP records.",
    )


class PointCharge(Model):
    """Place one external point charge in the declared external units.

    Attributes:
        charge: External charge magnitude.
        position: Three numeric Cartesian coordinates.
    """

    kind: Literal["point_charge"] = Field(
        default="point_charge",
        description="Discriminator identifying the PointCharge variant.",
    )
    charge: Number = Field(description="External charge magnitude.")
    position: tuple[Number, Number, Number] = Field(
        description="Three numeric Cartesian coordinates."
    )


class ExternalAtom(Model):
    """Place a nucleus in an external diffuse-charge fragment.

    Attributes:
        nucleus: Element, label, ghost notation, and optional isotope mass.
        position: Three numeric Cartesian coordinates.
    """

    kind: Literal["external_atom"] = Field(
        default="external_atom",
        description="Discriminator identifying the ExternalAtom variant.",
    )
    nucleus: Nucleus = Field(
        description="Element, label, ghost notation, and optional isotope mass."
    )
    position: tuple[Number, Number, Number] = Field(
        description="Three numeric Cartesian coordinates."
    )


class ExternalBasis(Model):
    """Specify an external fragment's orbital or density-fitting basis.

    Attributes:
        role: Native external basis option.
        value: Basis-reader value, retained as native text.
    """

    kind: Literal["external_basis"] = Field(
        default="external_basis",
        description="Discriminator identifying the ExternalBasis variant.",
    )
    role: Literal["basis", "df_basis_scf"] = Field(
        description="Native external basis option."
    )
    value: str = Field(description="Basis-reader value, retained as native text.")


type ExternalRecord = Annotated[
    PointCharge | ExternalAtom | ExternalBasis | Units | FragmentSeparator,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class External(Model):
    """Specify an external potential with ordered point and diffuse charges.

    Attributes:
        name: Optional native external-potential label.
        records: Complete ordered external specification.
    """

    kind: Literal["external"] = Field(
        default="external",
        description="Discriminator identifying the External variant.",
    )
    name: str | None = Field(
        default=None, description="Optional native external-potential label."
    )
    records: tuple[ExternalRecord, ...] = Field(
        default=(), description="Complete ordered external specification."
    )


class PCM(Model):
    """Contain complete PCMSolver input at an explicit foreign-language boundary.

    Attributes:
        name: Optional native block label.
        body: Embedded PCMSolver configuration, including its nested sections.
    """

    kind: Literal["pcm"] = Field(
        default="pcm", description="Discriminator identifying the PCM variant."
    )
    name: str | None = Field(default=None, description="Optional native block label.")
    body: str = Field(
        description="Embedded PCMSolver configuration, including its nested sections."
    )


class CFour(Model):
    """Contain literal CFOUR configuration without interpreting its language.

    Attributes:
        name: Optional native block label.
        body: Literal embedded CFOUR input, including hashes and whitespace.
    """

    kind: Literal["cfour"] = Field(
        default="cfour", description="Discriminator identifying the CFour variant."
    )
    name: str | None = Field(default=None, description="Optional native block label.")
    body: str = Field(
        description="Literal embedded CFOUR input, including hashes and whitespace."
    )


class Memory(Model):
    """Specify the native memory directive, including legacy name prefixes.

    Attributes:
        amount: Numeric memory amount.
        units: Native decimal or binary memory unit.
        prefix: Prefix recognized by the reference memory substitution.
    """

    kind: Literal["memory"] = Field(
        default="memory", description="Discriminator identifying the Memory variant."
    )
    amount: Number = Field(description="Numeric memory amount.")
    units: str = Field(
        description="Native decimal or binary memory unit.",
        pattern=r"^[kKmMgGtTpPbBeE][iI]?[bB]$",
        examples=_MEMORY_UNITS_EXAMPLES,
    )
    prefix: str = Field(
        default="",
        description="Prefix recognized by the reference memory substitution.",
    )


type NativeNode = Annotated[
    Molecule | SetOptions | Basis | External | PCM | CFour | Memory,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class PythonTemplate(Model):
    """Expose native children embedded anywhere in surrounding Python syntax.

    Text segments are concatenated with emitted native children. Native children
    remain directly accessible for inspection and editing. Validation checks the
    complete assembled program so Python scope and indentation retain context.

    Attributes:
        parts: Ordered Python text segments and first-class native nodes.
    """

    kind: Literal["python_template"] = Field(
        default="python_template",
        description="Discriminator identifying the PythonTemplate variant.",
    )
    parts: tuple[TemplatePart, ...] = Field(
        description="Ordered Python text segments and first-class native nodes."
    )


type TemplatePart = Annotated[
    Python | Molecule | SetOptions | Basis | External | PCM | CFour | Memory,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
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
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Job(Model):
    """Describe an ordered, serializable Psi4 job.

    Attributes:
        body: Ordered Python and native statements, including mixed templates.
    """

    body: tuple[Node, ...] = Field(
        default=(),
        description="Ordered Python and native statements, including mixed templates.",
    )


OptionArray.model_rebuild()
PythonTemplate.model_rebuild()
Job.model_rebuild()
