"""Compose ordered, serializable native declarations and Python calculations."""

from collections.abc import Callable
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

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
    """Attach plain multiline text as leading standalone hash comments."""

    text: str = Field(
        description="Comment text without generated hash prefixes; explicit "
        "line breaks are preserved."
    )


class Component(Model):
    """Retain leading comments and participate in ordered job composition."""

    comments: tuple[CommentBlock, ...] = Field(
        default=(), description="Leading block comments attached to this component."
    )

    def with_comment(self, text: str) -> Self:
        """Return a copy with an additional leading block comment."""
        return evolve(self, comments=(*self.comments, CommentBlock(text=text)))

    def __add__(self, other: Component | JobSpec) -> JobSpec:
        """Return the concatenated components in execution order."""
        return compose(self, other)

    def __call__(self, job: JobSpec) -> JobSpec:
        """Return a job with this component appended."""
        return compose(job, self)


class MoleculeDeclaration(Component):
    """Bind a molecular specification to an explicit Python name."""

    kind: Literal["molecule"] = Field(
        default="molecule", description="Molecule declaration."
    )
    name: str = Field(
        min_length=1, description="Python name assigned to this molecule."
    )
    geometry: Molecule = Field(description="Independent molecular specification.")

    @property
    def ref(self) -> Reference:
        """Return a reference for later calculations."""
        return Reference(name=self.name)


class OptionExpression(Model):
    """Retain native option syntax that cannot be expressed as a literal."""

    kind: Literal["option_expression"] = Field(
        default="option_expression", description="Native option expression."
    )
    source: str = Field(description="Exact native option value syntax.")


class OptionAssignment(Model):
    """Assign an option literal, reference, or explicit native expression."""

    key: str = Field(min_length=1, description="Native option name.")
    value: Value | OptionExpression = Field(
        description="Literal, reference, array, or native expression."
    )


class Options(Component):
    """Set persistent global or module-specific Psi4 options."""

    kind: Literal["options"] = Field(
        default="options", description="Native options block."
    )
    modules: tuple[str, ...] = Field(
        default=(), description="Native module names; empty selects global options."
    )
    assignments: tuple[OptionAssignment, ...] = Field(
        default=(), description="Ordered option assignments."
    )


class BasisAssignment(Model):
    """Assign a named basis globally or to an element or atom label."""

    kind: Literal["assignment"] = Field(
        default="assignment", description="Basis assignment."
    )
    basis: str = Field(min_length=1, description="Named basis or embedded basis label.")
    target: str | None = Field(
        default=None, description="Optional element or atom label."
    )


class BasisLabel(Model):
    """Introduce a named section in an embedded Gaussian basis definition."""

    kind: Literal["label"] = Field(default="label", description="Basis data label.")
    name: str = Field(min_length=1, description="Section name inside square brackets.")


class BasisData(Model):
    """Retain a line of Gaussian basis or ECP data."""

    kind: Literal["data"] = Field(default="data", description="Embedded basis record.")
    text: str = Field(description="Literal basis-reader line.")


type BasisRecord = Annotated[
    BasisAssignment | BasisLabel | BasisData,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class Basis(Component):
    """Define an orbital or auxiliary basis using native assignments and data."""

    kind: Literal["basis"] = Field(
        default="basis", description="Native basis definition."
    )
    role: str = Field(
        default="basis", description="Native orbital or auxiliary basis role."
    )
    name: str | None = Field(
        default=None, description="Optional Python binding for the definition."
    )
    records: tuple[BasisRecord, ...] = Field(
        default=(), description="Ordered assignments and literal basis records."
    )


class PointCharge(Model):
    """Place an external point charge in the external block's length unit."""

    kind: Literal["point_charge"] = Field(
        default="point_charge", description="External point charge."
    )
    charge: float = Field(description="Charge in elementary-charge units.")
    position: tuple[float, float, float] = Field(
        description="Cartesian charge position."
    )


class ExternalAtom(Model):
    """Place an atom in an external diffuse-charge fragment."""

    kind: Literal["atom"] = Field(
        default="atom", description="External diffuse-charge atom."
    )
    nucleus: Nucleus = Field(description="Element and isotope metadata.")
    position: tuple[float, float, float] = Field(description="Cartesian atom position.")


class ExternalBasis(Model):
    """Set an external fragment's orbital or fitting basis."""

    kind: Literal["basis"] = Field(
        default="basis", description="External basis setting."
    )
    role: Literal["basis", "df_basis_scf"] = Field(description="External basis role.")
    value: str = Field(description="Native basis value.")


class ExternalUnits(Model):
    """Select the external potential's length unit."""

    kind: Literal["units"] = Field(
        default="units", description="External length units."
    )
    name: str = Field(description="Native length-unit spelling.")


class ExternalSeparator(Model):
    """Separate diffuse external fragments."""

    kind: Literal["separator"] = Field(
        default="separator", description="External fragment boundary."
    )


type ExternalRecord = Annotated[
    PointCharge | ExternalAtom | ExternalBasis | ExternalUnits | ExternalSeparator,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class External(Component):
    """Represent the legacy native external-potential block.

    Current Psi4 calculations use ExternalPotential argument values instead.
    This model retains the historical input syntax for reading and generation.
    """

    kind: Literal["external"] = Field(
        default="external", description="External potential."
    )
    name: str | None = Field(
        default=None, description="Optional external-potential name."
    )
    records: tuple[ExternalRecord, ...] = Field(
        default=(), description="Ordered external records."
    )


class PCM(Component):
    """Contain an explicit PCMSolver configuration payload."""

    kind: Literal["pcm"] = Field(default="pcm", description="PCM configuration.")
    name: str | None = Field(default=None, description="Optional native block name.")
    body: str = Field(description="Complete embedded PCMSolver configuration.")


class CFour(Component):
    """Contain a literal CFOUR configuration payload."""

    kind: Literal["cfour"] = Field(default="cfour", description="CFOUR configuration.")
    name: str | None = Field(default=None, description="Optional native block name.")
    body: str = Field(description="Complete literal CFOUR payload.")


class Memory(Component):
    """Set the native Psi4 memory allocation."""

    kind: Literal["memory"] = Field(
        default="memory", description="Native memory directive."
    )
    amount: float = Field(gt=0, description="Positive memory amount.")
    units: str = Field(
        default="GB", description="Native decimal or binary memory unit."
    )


class Keyword(Model):
    """Associate an unrestricted Python keyword with a structured value."""

    name: str = Field(min_length=1, description="Python keyword argument name.")
    value: Value = Field(description="Structured argument value.")


class Calculation(Component):
    """Describe a Psi4 driver call with optional local settings and constraints."""

    kind: Literal["calculation"] = Field(
        default="calculation", description="Psi4 calculation call."
    )
    driver: Literal[
        "energy", "gradient", "hessian", "optimize", "frequency", "properties"
    ] = Field(description="Psi4 driver function.")
    method: Value = Field(description="Open method name or explicit Python expression.")
    molecule: Reference | None = Field(
        default=None, description="Previously declared molecule binding."
    )
    kwargs: tuple[Keyword, ...] = Field(
        default=(), description="Additional unrestricted driver arguments."
    )
    assign: Assignment = Field(
        default=None, description="Result binding or tuple-unpacking names."
    )
    constraints: tuple[Constraint, ...] = Field(
        default=(), description="Step-local typed OptKing constraints."
    )
    local_options: tuple[Options, ...] = Field(
        default=(),
        description="Settings restored after this calculation, even on failure.",
    )

    @property
    def ref(self) -> Reference:
        """Reference a single named assignment; reject absent or unpacked targets.

        Raises:
            ValueError: There is no single named assignment to reference.
        """  # noqa: DOC502 - Shared assignment validation raises ValueError.
        return assignment_reference(self.assign)


class Call(Component):
    """Call an arbitrary Python target without a method or keyword catalogue."""

    kind: Literal["call"] = Field(default="call", description="Generic Python call.")
    target: str = Field(min_length=1, description="Python callable expression.")
    args: tuple[Value, ...] = Field(default=(), description="Positional arguments.")
    kwargs: tuple[Keyword, ...] = Field(default=(), description="Keyword arguments.")
    assign: Assignment = Field(
        default=None, description="Optional assignment or tuple unpacking."
    )

    @property
    def ref(self) -> Reference:
        """Reference a single explicit assignment.

        Raises:
            ValueError: There is no single named assignment to reference.
        """  # noqa: DOC502 - Shared assignment validation raises ValueError.
        return assignment_reference(self.assign)


class Python(Component):
    """Include Python source and explicitly declare bindings it provides."""

    kind: Literal["python"] = Field(
        default="python", description="Opaque Python source."
    )
    source: str = Field(
        description="Python statements validated in complete input context."
    )
    provides: tuple[str, ...] = Field(
        default=(), description="Names made available to later structured references."
    )


class ForLoop(Component):
    """Repeat a job body for each value in an iterable."""

    kind: Literal["for"] = Field(default="for", description="Python for loop.")
    target: AssignmentTarget = Field(
        min_length=1, description="Loop binding or tuple-unpacking names."
    )
    iterable: Value = Field(description="Iterable value, reference, or expression.")
    body: JobSpec = Field(description="Components executed for each item.")
    otherwise: JobSpec | None = Field(
        default=None, description="Optional Python loop-else body."
    )


class Conditional(Component):
    """Select one of two job bodies using an ordinary Python condition."""

    kind: Literal["if"] = Field(default="if", description="Python conditional.")
    condition: Value = Field(description="Condition value, reference, or expression.")
    body: JobSpec = Field(description="Components executed when the condition is true.")
    otherwise: JobSpec | None = Field(
        default=None, description="Optional body for a false condition."
    )


class WhileLoop(Component):
    """Repeat a job body while a Python condition remains true."""

    kind: Literal["while"] = Field(default="while", description="Python while loop.")
    condition: Value = Field(description="Condition value, reference, or expression.")
    body: JobSpec = Field(description="Repeated job components.")
    otherwise: JobSpec | None = Field(
        default=None, description="Optional Python loop-else body."
    )


class WithItem(Model):
    """Enter a context manager and optionally bind its returned value."""

    context: Value = Field(description="Context-manager reference or expression.")
    target: Assignment = Field(
        default=None, description="Optional name or tuple-unpacking target."
    )


class WithBlock(Component):
    """Execute a job body within one or more Python context managers."""

    kind: Literal["with"] = Field(
        default="with", description="Python context-manager block."
    )
    items: tuple[WithItem, ...] = Field(
        min_length=1, description="Context managers entered from left to right."
    )
    body: JobSpec = Field(
        description="Components executed inside the entered contexts."
    )


class ExceptionHandler(Model):
    """Handle matching Python exceptions with a composed job body."""

    exception: Value | None = Field(
        default=None,
        description="Exception type expression; None catches all exceptions.",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        description="Optional exception binding, deleted after this handler.",
    )
    body: JobSpec = Field(description="Components executed by this handler.")

    @model_validator(mode="after")
    def _named_exception(self) -> Self:
        if self.exception is None and self.name is not None:
            raise ValueError("A named exception handler requires an exception type")
        return self


class TryBlock(Component):
    """Compose exception handling, success-only work, and guaranteed cleanup."""

    kind: Literal["try"] = Field(
        default="try", description="Python exception-handling block."
    )
    body: JobSpec = Field(description="Components whose exceptions are handled.")
    handlers: tuple[ExceptionHandler, ...] = Field(
        default=(),
        description="Ordered exception handlers; a bare handler must be last.",
    )
    otherwise: JobSpec | None = Field(
        default=None, description="Optional body executed after a successful try body."
    )
    finally_body: JobSpec | None = Field(
        default=None, description="Optional cleanup body executed on every exit."
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

type LeafComponent = NativeComponent | Calculation | Call | Python
type ControlComponent = ForLoop | Conditional | WhileLoop | WithBlock | TryBlock
type JobComponent = Annotated[
    LeafComponent | ControlComponent,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


class JobSpec(Model):
    """Retain ordered domain components for input generation and JSON exchange."""

    components: tuple[JobComponent, ...] = Field(
        default=(), description="Components in execution order."
    )

    def __add__(self, other: Component | JobSpec) -> JobSpec:
        """Return the concatenated components in execution order."""
        return compose(self, other)

    def __or__(self, stage: Callable[[JobSpec], JobSpec]) -> JobSpec:
        """Return the result of applying a pure pipeline stage."""
        return stage(self)


def compose(*items: Component | JobSpec) -> JobSpec:
    """Return an ordered job by flattening components and specifications."""
    flattened: list[Component] = []
    for item in items:
        flattened.extend(item.components if isinstance(item, JobSpec) else (item,))
    payload: dict[str, tuple[Component, ...]] = {"components": tuple(flattened)}
    return JobSpec.model_validate(payload)


def pipe[T](item: T, *stages: Callable[[T], T]) -> T:
    """Return the result of applying transformations from left to right."""
    for stage in stages:
        item = stage(item)
    return item


def declare_molecule(name: str, geometry: Molecule) -> MoleculeDeclaration:
    """Return a molecule declaration with an explicit Python binding."""
    return MoleculeDeclaration(name=name, geometry=geometry)


def options(
    *, modules: tuple[str, ...] = (), **settings: InputValue | OptionExpression
) -> Options:
    """Return a native option block from ordered keyword settings."""
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
    """Return a generic Python call with literal-safe argument values."""
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
    **kwargs: InputValue,
) -> Calculation:
    return Calculation(
        driver=driver,
        method=value(method),
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        kwargs=tuple(Keyword(name=k, value=value(v)) for k, v in kwargs.items()),
    )


def energy(
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    **kwargs: InputValue,
) -> Calculation:
    """Return a Psi4 energy call with unrestricted additional arguments."""
    return _calculation(
        "energy",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        **kwargs,
    )


def gradient(
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    **kwargs: InputValue,
) -> Calculation:
    """Return a Psi4 gradient call with unrestricted additional arguments."""
    return _calculation(
        "gradient",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        **kwargs,
    )


def hessian(
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    **kwargs: InputValue,
) -> Calculation:
    """Return a Psi4 hessian call with unrestricted additional arguments."""
    return _calculation(
        "hessian",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        **kwargs,
    )


def optimize(
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    **kwargs: InputValue,
) -> Calculation:
    """Return a Psi4 optimize call with unrestricted additional arguments."""
    return _calculation(
        "optimize",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        **kwargs,
    )


def frequency(
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    **kwargs: InputValue,
) -> Calculation:
    """Return a Psi4 frequency call with unrestricted additional arguments."""
    return _calculation(
        "frequency",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        **kwargs,
    )


def properties(
    method: InputValue,
    *,
    molecule: Reference | None = None,
    assign: Assignment = None,
    constraints: tuple[Constraint, ...] = (),
    local_options: tuple[Options, ...] = (),
    **kwargs: InputValue,
) -> Calculation:
    """Return a Psi4 properties call with unrestricted additional arguments."""
    return _calculation(
        "properties",
        method,
        molecule=molecule,
        assign=assign,
        constraints=constraints,
        local_options=local_options,
        **kwargs,
    )


def for_each(
    target: AssignmentTarget,
    iterable: InputValue,
    body: JobSpec,
    *,
    otherwise: JobSpec | None = None,
) -> ForLoop:
    """Return a loop that binds each iterable item before executing its body."""
    return ForLoop(
        target=target, iterable=value(iterable), body=body, otherwise=otherwise
    )


def if_else(
    condition: InputValue,
    body: JobSpec,
    *,
    otherwise: JobSpec | None = None,
) -> Conditional:
    """Return a conditional with an optional alternative body."""
    return Conditional(condition=value(condition), body=body, otherwise=otherwise)


def while_loop(
    condition: InputValue,
    body: JobSpec,
    *,
    otherwise: JobSpec | None = None,
) -> WhileLoop:
    """Return a condition-controlled loop with an optional loop-else body."""
    return WhileLoop(condition=value(condition), body=body, otherwise=otherwise)


def with_context(
    context: InputValue,
    body: JobSpec,
    *,
    target: Assignment = None,
) -> WithBlock:
    """Return a body executed within a context manager."""
    return WithBlock(
        items=(WithItem(context=value(context), target=target),), body=body
    )


# Resolve the recursive relationship between block bodies and job components.
JobSpec.model_rebuild()
