"""Compose ordered, serializable native declarations and Python calculations."""

from collections.abc import Callable
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from psi4_parser._solver_blocks import CFourFields, PCMFields
from psi4_parser.builder._model import Model, evolve
from psi4_parser.builder.constraints import Constraint
from psi4_parser.builder.molecular import Molecule, Nucleus
from psi4_parser.builder.values import (
    Assignment,
    AssignmentTarget,
    InputValue,
    Reference,
    Value,
    assignment_reference,
    value,
)


class CommentBlock(Model):
    """Comment lines to place before a job step or block."""

    text: str = Field(
        description="Plain comment text; each line becomes a separate comment line."
    )


class Component(Model):
    """A job step or block with optional leading comments."""

    comments: tuple[CommentBlock, ...] = Field(
        default=(), description="Comments placed immediately before this step or block."
    )

    def with_comment(self, text: str) -> Self:
        """Attach comment lines immediately before this component.

        Args:
            text: Plain text with optional line breaks; supply it without leading #
                characters. Empty lines become empty comment lines.

        Returns:
            A new component of the same type, with these comments appended to any
            existing comments. The original component can still be reused.
        """
        return evolve(self, comments=(*self.comments, CommentBlock(text=text)))

    def __add__(self, other: Component | JobSpec) -> JobSpec:
        """Return the concatenated components in execution order."""
        return compose(self, other)

    def __call__(self, job: JobSpec) -> JobSpec:
        """Return a job with this component appended."""
        return compose(job, self)


class MoleculeDeclaration(Component):
    """Declare a named molecule for subsequent calculations."""

    kind: Literal["molecule"] = Field(
        default="molecule", description="Selects a molecule declaration."
    )
    name: str = Field(
        min_length=1,
        description="Python name for this molecule, used by later calculations.",
    )
    geometry: Molecule = Field(
        description="Atoms, coordinates, fragments, and charge and spin settings."
    )

    @property
    def ref(self) -> Reference:
        """Return a reference to this molecule for subsequent job steps.

        Declare this component before using the reference, for example
        ``compose(h2, energy("scf", molecule=h2.ref))``.
        """
        return Reference(name=self.name)


class MoleculeClone(Component):
    """Copy an earlier structured molecule while retaining its stable atom layout.

    The generated input creates a separate Psi4 molecule at this point. Later
    constraints can use the source's atom IDs on the clone. The source must have
    a consistent structured layout on every path that reaches this component.
    """

    kind: Literal["molecule_clone"] = Field(
        default="molecule_clone", description="Selects a private copy of a molecule."
    )
    name: str = Field(
        min_length=1, description="New Python name for the cloned molecule."
    )
    source: Reference = Field(
        description="Reference to an earlier structured molecule."
    )

    @property
    def ref(self) -> Reference:
        """Return a reference to the new molecule for subsequent calculations."""
        return Reference(name=self.name)


class OptionExpression(Model):
    """A Psi4 option value supplied as input text."""

    kind: Literal["option_expression"] = Field(
        default="option_expression",
        description="Selects a Psi4 option value written as input text.",
    )
    source: str = Field(description="Psi4 option value as input text, such as cc-pvdz.")


class OptionAssignment(Model):
    """One Psi4 setting and its value."""

    key: str = Field(
        min_length=1, description="Psi4 setting name, such as basis or maxiter."
    )
    value: Value | OptionExpression = Field(
        description=(
            "Setting value: text, number, boolean, list, reference, or expression."
        )
    )


class Options(Component):
    """Psi4 settings that stay in effect for subsequent steps."""

    kind: Literal["options"] = Field(
        default="options", description="Selects a group of Psi4 settings."
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


class BasisAssignment(Model):
    """Apply a basis set to all atoms, an element, or an atom label."""

    kind: Literal["assignment"] = Field(
        default="assignment", description="Selects a basis-set assignment."
    )
    basis: str = Field(
        min_length=1,
        description=(
            "Basis-set name, such as cc-pvdz, or a label defined in this block."
        ),
    )
    target: str | None = Field(
        default=None,
        description="Element or atom label; null applies the basis to all atoms.",
    )


class BasisLabel(Model):
    """Name a section of basis-set data for use by assignments."""

    kind: Literal["label"] = Field(
        default="label", description="Selects a named section of basis-set data."
    )
    name: str = Field(
        min_length=1,
        description="Section name used by basis assignments in this block.",
    )


class BasisData(Model):
    """One line of Gaussian basis-set or effective core potential data."""

    kind: Literal["data"] = Field(
        default="data", description="Selects one line of basis-set data."
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


class Basis(Component):
    """Define orbital or auxiliary basis sets using assignments and data lines."""

    kind: Literal["basis"] = Field(
        default="basis", description="Selects a basis-set definition."
    )
    role: str = Field(
        default="basis",
        description="Psi4 basis setting to define, such as basis or df_basis_scf.",
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
    """A point charge in a legacy external-potential block."""

    kind: Literal["point_charge"] = Field(
        default="point_charge",
        description="Selects a point charge in a legacy external-potential block.",
    )
    charge: float = Field(description="Signed charge in elementary-charge units.")
    position: tuple[float, float, float] = Field(
        description="Charge x, y, and z coordinates in the block's length unit."
    )


class ExternalAtom(Model):
    """An atom in a legacy external diffuse-charge fragment."""

    kind: Literal["atom"] = Field(
        default="atom",
        description="Selects an atom in a legacy diffuse-charge fragment.",
    )
    nucleus: Nucleus = Field(
        description="Element label and any isotope or ghost-center settings."
    )
    position: tuple[float, float, float] = Field(
        description="Atom x, y, and z coordinates in the block's length unit."
    )


class ExternalBasis(Model):
    """An orbital or fitting basis for an external fragment."""

    kind: Literal["basis"] = Field(
        default="basis", description="Selects a basis setting for an external fragment."
    )
    role: Literal["basis", "df_basis_scf"] = Field(
        description="Basis setting for the external fragment."
    )
    value: str = Field(description="Basis-set name or Psi4 basis expression.")


class ExternalUnits(Model):
    """Length units for an external-potential block."""

    kind: Literal["units"] = Field(
        default="units",
        description="Selects the length unit for an external-potential block.",
    )
    name: str = Field(description="Length-unit name, such as angstrom or bohr.")


class ExternalSeparator(Model):
    """A boundary between external diffuse-charge fragments."""

    kind: Literal["separator"] = Field(
        default="separator",
        description="Starts a new external diffuse-charge fragment.",
    )


type ExternalRecord = Annotated[
    PointCharge | ExternalAtom | ExternalBasis | ExternalUnits | ExternalSeparator,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "A charge, atom, basis setting, unit declaration, or fragment separator."
        ),
    ),
]


class External(Component):
    """Point and diffuse charges in Psi4's legacy external-block syntax."""

    kind: Literal["external"] = Field(
        default="external", description="Selects a legacy external-potential block."
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


class PCM(PCMFields, Component):
    """Add PCMSolver solvent settings to a composed job.

    Attributes:
        name: Optional name for the solvent configuration block.
        body: PCMSolver configuration text, including nested sections.
        comments: Comment blocks placed before the solvent settings.
    """


class CFour(CFourFields, Component):
    """Add CFOUR configuration to a composed job.

    Attributes:
        name: Optional name for the CFOUR block.
        body: CFOUR configuration text.
        comments: Comment blocks placed before the CFOUR configuration.
    """


class Memory(Component):
    """The maximum memory allocated to Psi4."""

    kind: Literal["memory"] = Field(
        default="memory", description="Selects the memory limit for Psi4."
    )
    amount: float = Field(
        gt=0, description="Positive memory limit in the chosen units."
    )
    units: str = Field(
        default="GB", description="Memory unit, such as MB, GB, MiB, or GiB."
    )


class Keyword(Model):
    """One named argument and its value."""

    name: str = Field(
        min_length=1, description="Named argument to pass to the function."
    )
    value: Value = Field(description="Value to pass for this named argument.")


class Calculation(Component):
    """A Psi4 calculation with a method, molecule, and optional settings."""

    kind: Literal["calculation"] = Field(
        default="calculation", description="Selects a Psi4 calculation step."
    )
    driver: Literal[
        "energy", "gradient", "hessian", "optimize", "frequency", "properties"
    ] = Field(
        description="Calculation to request, such as energy, optimize, or frequency."
    )
    method: Value = Field(
        description=(
            "Method name, such as scf or mp2, or an expression that supplies it."
        )
    )
    molecule: Reference | None = Field(
        default=None,
        description=(
            "Reference to an earlier molecule; null uses Psi4's active molecule."
        ),
    )
    kwargs: tuple[Keyword, ...] = Field(
        default=(),
        description="Additional named arguments passed to the Psi4 calculation.",
    )
    assign: Assignment = Field(
        default=None,
        description="Result name, or a list of names for multiple returned values.",
    )
    constraints: tuple[Constraint, ...] = Field(
        default=(),
        description=(
            "Coordinates to hold fixed or keep within bounds during optimization."
        ),
    )
    local_options: tuple[Options, ...] = Field(
        default=(),
        description=(
            "Settings for this calculation, restored afterward even if it fails."
        ),
    )
    isolate_options: bool = Field(
        default=False,
        description="Reset native options before applying local_options, then "
        "restore captured values and changed flags even on failure. Covers native "
        "modules, explicitly named option modules, and the selected module.",
    )
    pcm_input: str | None = Field(
        default=None,
        min_length=1,
        description="PCMSolver configuration text applied through PCM__INPUT within "
        "this call's option scope; null supplies no solver block. The parsed filename "
        "is restored afterward; Psi4 manages the helper's scratch files.",
    )

    @property
    def ref(self) -> Reference:
        """Return a reference to the name assigned to this calculation's result.

        For tuple assignments such as ``assign=("e", "wfn")``, select each name
        explicitly with ``Reference(name="wfn")``.

        Raises:
            ValueError: The calculation has no assignment or assigns multiple names.
        """  # noqa: DOC502 - Shared assignment validation raises ValueError.
        return assignment_reference(self.assign)


class Call(Component):
    """Call a Python function within the generated input."""

    kind: Literal["call"] = Field(
        default="call", description="Selects a Python function call."
    )
    target: str = Field(
        min_length=1,
        description="Python function to call, such as psi4.oeprop or wfn.energy.",
    )
    args: tuple[Value, ...] = Field(
        default=(), description="Arguments passed by position, in order."
    )
    kwargs: tuple[Keyword, ...] = Field(
        default=(), description="Arguments passed by name."
    )
    assign: Assignment = Field(
        default=None,
        description="Result name, or a list of names for multiple returned values.",
    )

    @property
    def ref(self) -> Reference:
        """Return a reference to the name assigned to this call's result.

        For tuple assignments, select each name with ``Reference(name="name")``.

        Raises:
            ValueError: The call has no assignment or assigns multiple names.
        """  # noqa: DOC502 - Shared assignment validation raises ValueError.
        return assignment_reference(self.assign)


class Python(Component):
    """Python statements to include in the generated input."""

    kind: Literal["python"] = Field(
        default="python",
        description="Selects Python statements to include in the input.",
    )
    source: str = Field(
        description="Python statements to include at this point in the input."
    )
    provides: tuple[str, ...] = Field(
        default=(),
        description="Names assigned by this code for later steps to reference.",
    )


class ForLoop(Component):
    """Run a group of steps for each value in a sequence."""

    kind: Literal["for"] = Field(
        default="for", description="Selects a loop over a sequence of values."
    )
    target: AssignmentTarget = Field(
        min_length=1,
        description="Name, or list of names, receiving each item in the loop.",
    )
    iterable: Value = Field(
        description="Values to loop over, or an expression that supplies them."
    )
    body: JobSpec = Field(description="Steps to run for each item.")
    otherwise: JobSpec | None = Field(
        default=None,
        description="Steps run after normal loop completion; break skips them.",
    )


class Conditional(Component):
    """Choose between two groups of steps using a condition."""

    kind: Literal["if"] = Field(default="if", description="Selects an if/else branch.")
    condition: Value = Field(description="Condition that selects which branch to run.")
    body: JobSpec = Field(description="Steps to run when the condition is true.")
    otherwise: JobSpec | None = Field(
        default=None, description="Steps to run when the condition is false."
    )


class WhileLoop(Component):
    """Repeat a group of steps while a condition is true."""

    kind: Literal["while"] = Field(
        default="while",
        description="Selects a loop that repeats while a condition is true.",
    )
    condition: Value = Field(description="Condition checked before each repetition.")
    body: JobSpec = Field(description="Steps to repeat while the condition is true.")
    otherwise: JobSpec | None = Field(
        default=None,
        description="Steps run after normal loop completion; break skips them.",
    )


class WithItem(Model):
    """A context manager and an optional name for its returned value."""

    context: Value = Field(
        description="Context manager expression, such as open('results.txt', 'w')."
    )
    target: Assignment = Field(
        default=None,
        description=(
            "Name, or list of names, receiving the context manager's returned value."
        ),
    )


class WithBlock(Component):
    """Run steps within Python context managers, such as an open file."""

    kind: Literal["with"] = Field(
        default="with", description="Selects a block that uses context managers."
    )
    items: tuple[WithItem, ...] = Field(
        min_length=1, description="Context managers to enter, in order."
    )
    body: JobSpec = Field(
        description="Steps to run inside the entered context managers."
    )


class ExceptionHandler(Model):
    """Steps to run when a matching Python exception occurs."""

    exception: Value | None = Field(
        default=None,
        description="Python exception type to catch; null catches any exception.",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Name for the caught exception, available only inside this handler."
        ),
    )
    body: JobSpec = Field(
        description="Steps to run when this handler catches an exception."
    )

    @model_validator(mode="after")
    def _named_exception(self) -> Self:
        if self.exception is None and self.name is not None:
            raise ValueError("A named exception handler requires an exception type")
        return self


class TryBlock(Component):
    """Attempt steps with exception handlers and optional cleanup."""

    kind: Literal["try"] = Field(
        default="try",
        description="Selects exception handling and cleanup for a group of steps.",
    )
    body: JobSpec = Field(
        description="Steps to attempt before applying the exception handlers."
    )
    handlers: tuple[ExceptionHandler, ...] = Field(
        default=(),
        description=(
            "Exception handlers tried in order; a catch-all handler must be last."
        ),
    )
    otherwise: JobSpec | None = Field(
        default=None, description="Steps run when the try body completes normally."
    )
    finally_body: JobSpec | None = Field(
        default=None, description="Cleanup steps run on both success and failure."
    )

    @model_validator(mode="after")
    def _valid_clauses(self) -> Self:
        if not self.handlers and self.finally_body is None:
            raise ValueError("A try block requires handlers or a finally body")
        if self.otherwise is not None and not self.handlers:
            raise ValueError("A try-else body requires exception handlers")
        if any(handler.exception is None for handler in self.handlers[:-1]):
            raise ValueError("A bare exception handler must be last")
        return self


type NativeComponent = (
    MoleculeDeclaration | Options | Basis | External | PCM | CFour | Memory
)

type LeafComponent = NativeComponent | MoleculeClone | Calculation | Call | Python
type ControlComponent = ForLoop | Conditional | WhileLoop | WithBlock | TryBlock
type JobComponent = Annotated[
    LeafComponent | ControlComponent,
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "A molecule, setting, calculation, Python statement, or control-flow block."
        ),
    ),
]


class JobSpec(Model):
    """Molecules, settings, calculations, and Python steps that form a Psi4 input."""

    components: tuple[JobComponent, ...] = Field(
        default=(),
        description=(
            "Molecules, settings, and calculation steps in the order they will run."
        ),
    )

    def __add__(self, other: Component | JobSpec) -> JobSpec:
        """Return the concatenated components in execution order."""
        return compose(self, other)

    def __or__(self, stage: Callable[[JobSpec], JobSpec]) -> JobSpec:
        """Return the updated job, as in job | options(basis="sto-3g")."""
        return stage(self)


def compose(*items: Component | JobSpec) -> JobSpec:
    """Combine job components in the supplied order.

    Nested specifications are flattened. Settings and calculations keep their
    positions, so repeated components have repeated effects when the input runs.
    The result is also available through ``a + b`` or ``JobSpec() | a | b``.

    Args:
        *items: Components or previously composed jobs to concatenate.

    Returns:
        A new job containing all components; no arguments gives an empty job.

    Example:
        Build a named molecule, then settings, then a calculation::

            job = compose(h2, options(basis="sto-3g"), energy("scf", molecule=h2.ref))
            source = render_job(job)
    """
    flattened: list[Component] = []
    for item in items:
        flattened.extend(item.components if isinstance(item, JobSpec) else (item,))
    payload: dict[str, tuple[Component, ...]] = {"components": tuple(flattened)}
    return JobSpec.model_validate(payload)


def pipe[T](item: T, *stages: Callable[[T], T]) -> T:
    """Apply transformations to a value from left to right.

    Args:
        item: Starting molecule or job.
        *stages: Functions that accept and return the same kind of value.

    Returns:
        The final transformed value, or the starting value when no stages are given.

    Example:
        Apply a geometry edit and then declare the resulting molecule::

            edited = pipe(
                geometry, set_distance(("a1", "a2"), angstrom(1.0), moving=("a2",))
            )
            h2 = molecule("h2", edited)
    """
    for stage in stages:
        item = stage(item)
    return item


def declare_molecule(name: str, geometry: Molecule) -> MoleculeDeclaration:
    """Declare a molecule under a name used by later job steps.

    Import this helper as ``molecule`` from ``psi4_parser.builder``.

    Args:
        name: Python identifier, such as h2; each declaration needs a unique name.
        geometry: Atoms, coordinates, fragments, charge, spin, and frame settings.

    Returns:
        A component to place before calculations. Pass its ``.ref`` property to
        their ``molecule`` argument.
    """
    return MoleculeDeclaration(name=name, geometry=geometry)


def options(
    *, modules: tuple[str, ...] = (), **settings: InputValue | OptionExpression
) -> Options:
    """Create a block of Psi4 settings for subsequent calculations.

    Args:
        modules: Module names, such as ("scf",); an empty tuple sets global options.
        **settings: Option names and values in insertion order. Strings are text
            values, lists and tuples are arrays, and Reference or Expression uses
            a value supplied by the generated input. OptionExpression accepts
            Psi4 option text directly.

    Returns:
        A settings component. Compose it into a job for persistent settings, or
        pass it in a calculation's ``local_options`` for temporary settings.

    Example:
        ``options(modules=("scf",), maxiter=100, reference="rhf")``
    """
    return Options(
        modules=modules,
        assignments=tuple(
            OptionAssignment(
                key=k, value=v if isinstance(v, OptionExpression) else value(v)
            )
            for k, v in settings.items()
        ),
    )


def call(
    target: str,
    *args: InputValue,
    assign: Assignment = None,
    **kwargs: InputValue,
) -> Call:
    """Include a Python function call as a job step.

    Args:
        target: Function expression, such as psi4.oeprop or wfn.energy.
        *args: Positional values. Strings are literal text; use Reference for an
            earlier named value or Expression for Python code evaluated later.
        assign: Result name, tuple of names for unpacking, or None to discard it.
        **kwargs: Additional named values, encoded in the same way as args.

    Returns:
        A call component to compose into the job. An assigned result can be used
        by subsequent steps through ``.ref`` or ``Reference(name=...)``.

    Example:
        ``call("psi4.oeprop", Reference(name="wfn"), "DIPOLE")``
    """
    return Call(
        target=target,
        args=tuple(value(a) for a in args),
        kwargs=tuple(Keyword(name=k, value=value(v)) for k, v in kwargs.items()),
        assign=assign,
    )


def _calculation(  # noqa: PLR0913 - Mirror the public driver construction fields plus the selected driver.
    driver: Literal[
        "energy", "gradient", "hessian", "optimize", "frequency", "properties"
    ],
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    return Calculation(
        driver=driver,
        method=value(method),
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        kwargs=tuple(Keyword(name=k, value=value(v)) for k, v in kwargs.items()),
    )


def energy(  # noqa: PLR0913 - Mirror the typed calculation fields.
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    """Add a step to compute an electronic energy when the Psi4 input runs.

    Args:
        method: Psi4 method name, such as scf or mp2. Strings are literal names;
            use Reference for an earlier named value or Expression for Python code.
        molecule: Earlier molecule declaration's .ref; None uses Psi4's active molecule.
        assign: Result name, tuple of names for unpacking, or None to discard it.
            Names can be referenced by subsequent steps after this calculation.
        constraints: Use an empty tuple; typed constraints belong to optimize().
        local_options: Settings applied for this call and restored afterward,
            including if it raises. Compose options separately for persistent settings.
        pcm_input: PCMSolver text applied inside the call through PCM__INPUT;
            None supplies no solvent configuration. Psi4 manages its scratch files.
        isolate_options: Start from native option defaults, then apply local_options
            and restore captured values/changed flags afterward. The default keeps
            ambient options available. Resource settings and unlisted plugin
            state remain separate.
        **kwargs: Additional Psi4 arguments. Strings are literal text; Reference
            and Expression use values from the generated input.

    Returns:
        A calculation component to compose into the job. Its arguments follow
        Psi4's energy() interface, including any requested return_wfn behavior.

    Example:
        ``energy("scf", molecule=h2.ref, return_wfn=True, assign=("e", "wfn"))``
    """
    return _calculation(
        "energy",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        **kwargs,
    )


def gradient(  # noqa: PLR0913 - Mirror the typed calculation fields.
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    """Add a step to compute an energy gradient when the Psi4 input runs.

    Args:
        method: Psi4 method name, such as scf or mp2. Strings are literal names;
            use Reference for an earlier named value or Expression for Python code.
        molecule: Earlier molecule declaration's .ref; None uses Psi4's active molecule.
        assign: Result name, tuple of names for unpacking, or None to discard it.
            Names can be referenced by subsequent steps after this calculation.
        constraints: Use an empty tuple; typed constraints belong to optimize().
        local_options: Settings applied for this call and restored afterward,
            including if it raises. Compose options separately for persistent settings.
        pcm_input: PCMSolver text applied inside the call through PCM__INPUT;
            None supplies no solvent configuration. Psi4 manages its scratch files.
        isolate_options: Start from native option defaults, then apply local_options
            and restore captured values/changed flags afterward. The default keeps
            ambient options available. Resource settings and unlisted plugin
            state remain separate.
        **kwargs: Additional Psi4 arguments. Strings are literal text; Reference
            and Expression use values from the generated input.

    Returns:
        A calculation component to compose into the job. Its arguments follow
        Psi4's gradient() interface, including any requested return_wfn behavior.

    Example:
        ``gradient("mp2", molecule=h2.ref, assign="g")``
    """
    return _calculation(
        "gradient",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        **kwargs,
    )


def hessian(  # noqa: PLR0913 - Mirror the typed calculation fields.
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    """Add a step to compute an energy Hessian when the Psi4 input runs.

    Args:
        method: Psi4 method name, such as scf or mp2. Strings are literal names;
            use Reference for an earlier named value or Expression for Python code.
        molecule: Earlier molecule declaration's .ref; None uses Psi4's active molecule.
        assign: Result name, tuple of names for unpacking, or None to discard it.
            Names can be referenced by subsequent steps after this calculation.
        constraints: Use an empty tuple; typed constraints belong to optimize().
        local_options: Settings applied for this call and restored afterward,
            including if it raises. Compose options separately for persistent settings.
        pcm_input: PCMSolver text applied inside the call through PCM__INPUT;
            None supplies no solvent configuration. Psi4 manages its scratch files.
        isolate_options: Start from native option defaults, then apply local_options
            and restore captured values/changed flags afterward. The default keeps
            ambient options available. Resource settings and unlisted plugin
            state remain separate.
        **kwargs: Additional Psi4 arguments. Strings are literal text; Reference
            and Expression use values from the generated input.

    Returns:
        A calculation component to compose into the job. Its arguments follow
        Psi4's hessian() interface, including any requested return_wfn behavior.

    Example:
        ``hessian("scf", molecule=h2.ref, assign="h")``
    """
    return _calculation(
        "hessian",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        **kwargs,
    )


def optimize(  # noqa: PLR0913 - Mirror the typed calculation fields.
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    """Add a step to optimize a molecular geometry when the Psi4 input runs.

    Args:
        method: Psi4 method name, such as scf or mp2. Strings are literal names;
            use Reference for an earlier named value or Expression for Python code.
        molecule: Earlier molecule declaration's .ref; None uses Psi4's active molecule.
        assign: Result name, tuple of names for unpacking, or None to discard it.
            Names can be referenced by subsequent steps after this calculation.
        constraints: OptKing constraints addressed by atom ID; provide an explicit
            molecule reference whose geometry contains these atoms.
        local_options: Settings applied for this call and restored afterward,
            including if it raises. Compose options separately for persistent settings.
        pcm_input: PCMSolver text applied inside the call through PCM__INPUT;
            None supplies no solvent configuration. Psi4 manages its scratch files.
        isolate_options: Start from native option defaults, then apply local_options
            and restore captured values/changed flags afterward. The default keeps
            ambient options available. Resource settings and unlisted plugin
            state remain separate.
        **kwargs: Additional Psi4 arguments. Strings are literal text; Reference
            and Expression use values from the generated input.

    Returns:
        A calculation component to compose into the job. Its arguments follow
        Psi4's optimize() interface, including any requested return_wfn behavior.

    Example:
        Freeze a bond at its starting length::

            constraint = freeze(distance("a1", "a2"))
            step = optimize("scf", molecule=h2.ref, constraints=(constraint,))
    """
    return _calculation(
        "optimize",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        **kwargs,
    )


def frequency(  # noqa: PLR0913 - Mirror the typed calculation fields.
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    """Add a step to compute vibrational frequencies when the Psi4 input runs.

    Args:
        method: Psi4 method name, such as scf or mp2. Strings are literal names;
            use Reference for an earlier named value or Expression for Python code.
        molecule: Earlier molecule declaration's .ref; None uses Psi4's active molecule.
        assign: Result name, tuple of names for unpacking, or None to discard it.
            Names can be referenced by subsequent steps after this calculation.
        constraints: Use an empty tuple; typed constraints belong to optimize().
        local_options: Settings applied for this call and restored afterward,
            including if it raises. Compose options separately for persistent settings.
        pcm_input: PCMSolver text applied inside the call through PCM__INPUT;
            None supplies no solvent configuration. Psi4 manages its scratch files.
        isolate_options: Start from native option defaults, then apply local_options
            and restore captured values/changed flags afterward. The default keeps
            ambient options available. Resource settings and unlisted plugin
            state remain separate.
        **kwargs: Additional Psi4 arguments. Strings are literal text; Reference
            and Expression use values from the generated input.

    Returns:
        A calculation component to compose into the job. Its arguments follow
        Psi4's frequency() interface, including any requested return_wfn behavior.

    Example:
        ``frequency("scf", molecule=h2.ref, assign="e_freq")``
    """
    return _calculation(
        "frequency",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        **kwargs,
    )


def properties(  # noqa: PLR0913 - Mirror the typed calculation fields.
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    isolate_options: bool = False,
    pcm_input: str | None = None,
    **kwargs: InputValue,
) -> Calculation:
    """Add a step to compute molecular properties when the Psi4 input runs.

    Args:
        method: Psi4 method name, such as scf or mp2. Strings are literal names;
            use Reference for an earlier named value or Expression for Python code.
        molecule: Earlier molecule declaration's .ref; None uses Psi4's active molecule.
        assign: Result name, tuple of names for unpacking, or None to discard it.
            Names can be referenced by subsequent steps after this calculation.
        constraints: Use an empty tuple; typed constraints belong to optimize().
        local_options: Settings applied for this call and restored afterward,
            including if it raises. Compose options separately for persistent settings.
        pcm_input: PCMSolver text applied inside the call through PCM__INPUT;
            None supplies no solvent configuration. Psi4 manages its scratch files.
        isolate_options: Start from native option defaults, then apply local_options
            and restore captured values/changed flags afterward. The default keeps
            ambient options available. Resource settings and unlisted plugin
            state remain separate.
        **kwargs: Additional Psi4 arguments. Strings are literal text; Reference
            and Expression use values from the generated input.

    Returns:
        A calculation component to compose into the job. Its arguments follow
        Psi4's properties() interface, including any requested return_wfn behavior.

    Example:
        ``properties("scf", molecule=h2.ref, properties=["dipole"], assign="e_prop")``
    """
    return _calculation(
        "properties",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        isolate_options=isolate_options,
        pcm_input=pcm_input,
        **kwargs,
    )


def for_each(
    target: AssignmentTarget,
    iterable: InputValue,
    body: JobSpec,
    *,
    otherwise: JobSpec | None = None,
) -> ForLoop:
    """Repeat a composed job body for each value in an iterable.

    Args:
        target: Loop variable name, or tuple of names to unpack each item.
        iterable: Python list or tuple, an earlier Reference, or an Expression
            such as ``Expression(source="range(3)")``. A string is literal text.
        body: Steps repeated in order; they may refer to the loop variables.
        otherwise: Steps run after normal loop completion, including an empty
            iterable. A Python break skips these steps.

    Returns:
        A for-loop component. References after it must be assigned on every
        execution path; values assigned only in the loop body may be absent.

    Example:
        Reuse one calculation body for two methods::

            body = compose(energy(Reference(name="method")))
            loop = for_each("method", ["scf", "mp2"], body)
    """
    return ForLoop(
        target=target, iterable=value(iterable), body=body, otherwise=otherwise
    )


def if_else(
    condition: InputValue,
    body: JobSpec,
    *,
    otherwise: JobSpec | None = None,
) -> Conditional:
    """Choose between two composed job bodies when the input runs.

    Args:
        condition: A value to test. Use Expression for a Python test such as
            ``Expression(source="e_scf < -1.0")``; strings are literal text.
        body: Steps run when the condition is true.
        otherwise: Steps run when the condition is false; None leaves that case empty.

    Returns:
        A conditional component. Names used afterward must be assigned on every
        branch or already exist before the conditional.
    """
    return Conditional(condition=value(condition), body=body, otherwise=otherwise)


def while_loop(
    condition: InputValue,
    body: JobSpec,
    *,
    otherwise: JobSpec | None = None,
) -> WhileLoop:
    """Repeat a composed job body while a condition is true.

    Args:
        condition: Value tested before each iteration. Use Expression for a
            Python test evaluated anew each time; strings are literal text.
        body: Repeated steps, including any updates needed to end the loop.
        otherwise: Steps run when the condition becomes false, including when
            the body never runs. A Python break skips these steps.

    Returns:
        A while-loop component. Names assigned only in its body may be absent
        after the loop.
    """
    return WhileLoop(condition=value(condition), body=body, otherwise=otherwise)


def with_context(
    context: InputValue,
    body: JobSpec,
    *,
    target: Assignment = None,
) -> WithBlock:
    """Run a composed job body within a Python context manager.

    Args:
        context: Context-manager Reference or Expression, such as
            ``Expression(source="open('values.txt', 'w')")``.
        body: Steps to run inside the context.
        target: Optional name, or tuple of names, for the value returned on entry.

    Returns:
        A with-block component. Its target names are available inside the body;
        names used afterward must be assigned on every execution path.
    """
    return WithBlock(
        items=(WithItem(context=value(context), target=target),), body=body
    )


# Resolve the recursive relationship between block bodies and job components.
JobSpec.model_rebuild()
