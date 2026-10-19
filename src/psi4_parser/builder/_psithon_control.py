"""Compile composed job bodies and track definite Python bindings."""

import io
import tokenize
from typing import Protocol

from pydantic import Field

from psi4_parser import job as native
from psi4_parser.api import parse
from psi4_parser.builder import _encoding
from psi4_parser.builder import components as c
from psi4_parser.builder._model import Model
from psi4_parser.builder.diagnostics import (
    CompilationDiagnostic,
    CompilationError,
    ComponentPath,
    compilation_context,
)
from psi4_parser.builder.molecular import Molecule, ZMatrix
from psi4_parser.builder.values import Assignment, assignment_names


class LeafLowerer(Protocol):
    """Translate a non-control component in its preceding binding environment."""

    def __call__(
        self,
        component: c.LeafComponent,
        bindings: set[str],
        molecules: dict[str, MoleculeLayout],
        serial: int,
    ) -> native.Node:
        """Return the component's native or Python node."""
        ...


class CommentLowerer(Protocol):
    """Attach leading comments to a translated component."""

    def __call__(self, component: c.JobComponent, node: native.Node) -> native.Node:
        """Return the annotated node."""
        ...


class CompiledJob(Model):
    """Retain a native tree and its completely validated source."""

    job: native.Job = Field(description="Compiled native job.")
    source: str = Field(description="Validated Psithon emitted from the job.")


class MoleculeLayout(Model):
    """Retain the atom indexing and frame information needed by constraints."""

    atom_ids: tuple[str, ...] = Field(
        description="Atom IDs in input order, including dummies."
    )
    dummy_ids: frozenset[str] = Field(
        description="IDs excluded from optimizer atom indexing."
    )
    cartesian: bool = Field(description="Whether every atom uses Cartesian records.")
    resolved_atoms: bool = Field(
        description="Whether atom counts are known without file or EFP expansion."
    )
    fixed_com: bool = Field(
        description="Whether center-of-mass translation is disabled."
    )
    fixed_orientation: bool = Field(
        description="Whether orientation changes are disabled."
    )

    @classmethod
    def from_molecule(cls, geometry: Molecule) -> MoleculeLayout:
        """Return the layout properties shared by equivalent constraint mappings."""
        return cls(
            atom_ids=tuple(atom.id for atom in geometry.atoms),
            dummy_ids=frozenset(
                atom.id for atom in geometry.atoms if atom.nucleus.dummy
            ),
            cartesian=all(
                not isinstance(atom.coordinates, ZMatrix) for atom in geometry.atoms
            ),
            resolved_atoms=not geometry.sources and not geometry.efp,
            fixed_com=geometry.fixed_com,
            fixed_orientation=geometry.fixed_orientation,
        )

    def optimizer_indices(self) -> dict[str, int]:
        """Return one-based optimizer indices with reference dummies excluded."""
        return {
            name: index
            for index, name in enumerate(
                (name for name in self.atom_ids if name not in self.dummy_ids),
                1,
            )
        }


class _MoleculeBinding(Model):
    name: str = Field(description="Explicit molecule binding.")
    layout: MoleculeLayout = Field(
        description="Known atom identities and frame metadata."
    )


class _Scope(Model):
    definite: frozenset[str] = Field(
        default=frozenset(), description="Names bound on every incoming path."
    )
    possible: frozenset[str] = Field(
        default=frozenset(), description="Names bound on any incoming path."
    )
    molecules: tuple[_MoleculeBinding, ...] = Field(
        default=(), description="Molecule metadata shared by every incoming path."
    )

    def layout_map(self) -> dict[str, MoleculeLayout]:
        return {entry.name: entry.layout for entry in self.molecules}

    def bind(
        self, names: tuple[str, ...], molecule: c.MoleculeDeclaration | None = None
    ) -> _Scope:
        known = tuple(entry for entry in self.molecules if entry.name not in names)
        if molecule is not None:
            known += (
                _MoleculeBinding(
                    name=molecule.name,
                    layout=MoleculeLayout.from_molecule(molecule.geometry),
                ),
            )
        return _Scope(
            definite=self.definite.union(names),
            possible=self.possible.union(names),
            molecules=known,
        )

    def discard(self, name: str) -> _Scope:
        return _Scope(
            definite=self.definite.difference((name,)),
            possible=self.possible,
            molecules=tuple(entry for entry in self.molecules if entry.name != name),
        )


def _merge(scopes: tuple[_Scope, ...]) -> _Scope:
    first, *remaining = scopes
    definite = first.definite.intersection(*(scope.definite for scope in remaining))
    return _Scope(
        definite=definite,
        possible=frozenset().union(*(scope.possible for scope in scopes)),
        molecules=tuple(
            entry
            for entry in first.molecules
            if entry.name in definite
            and all(entry in scope.molecules for scope in remaining)
        ),
    )


class _SourceLocation(Model):
    first: int = Field(ge=1, description="First emitted line, one-based.")
    last: int = Field(ge=0, description="Last emitted line, or zero for empty text.")
    path: ComponentPath = Field(description="Owning builder field.")

    def shifted(self, offset: int) -> _SourceLocation:
        return _SourceLocation(
            first=self.first + offset, last=self.last + offset, path=self.path
        )


class _Emission(Model):
    node: native.Node = Field(description="Native node or mixed Python template.")
    text: str = Field(description="Emitted text without trailing line endings.")
    locations: tuple[_SourceLocation, ...] = Field(
        default=(), description="Relative source owners for diagnostics."
    )

    @property
    def lines(self) -> int:
        return self.text.count("\n") + 1 if self.text else 0


class _ComponentResult(Model):
    emission: _Emission = Field(
        description="Translated component and its source owners."
    )
    scope: _Scope = Field(description="Bindings after normal completion.")
    writes: frozenset[str] = Field(
        default=frozenset(),
        description="Names written on any path through the component.",
    )

    deletions: frozenset[str] = Field(
        default=frozenset(),
        description="Names that may be deleted before they are rebound.",
    )


class _SuiteResult(Model):
    emissions: tuple[_Emission, ...] = Field(
        description="Translated components in execution order."
    )
    scope: _Scope = Field(description="Bindings after normal completion of the suite.")
    writes: frozenset[str] = Field(
        default=frozenset(), description="Names written on any path through the suite."
    )

    deletions: frozenset[str] = Field(
        default=frozenset(),
        description="Names that may be deleted before they are rebound.",
    )


def _emission(
    node: native.Node, locations: tuple[_SourceLocation, ...] = ()
) -> _Emission:
    text = native.emit_job(native.Job(body=(node,)), validate=False).rstrip("\r\n")
    return _Emission(node=node, text=text, locations=locations)


def _parts(node: native.Node) -> tuple[native.TemplatePart, ...]:
    parts = list(node.parts) if isinstance(node, native.PythonTemplate) else [node]
    while parts and isinstance(parts[-1], native.Python):
        tail = parts.pop()
        if isinstance(tail, native.Python) and tail.source.rstrip("\r\n"):
            parts.append(native.Python(source=tail.source.rstrip("\r\n")))
            break
    return tuple(parts)


def _join(emissions: tuple[_Emission, ...], separator: str = "\n\n") -> _Emission:
    parts: list[native.TemplatePart] = []
    locations: list[_SourceLocation] = []
    offset = 0
    for index, item in enumerate(emissions):
        if index:
            parts.append(native.Python(source=separator))
        parts.extend(_parts(item.node))
        locations.extend(location.shifted(offset) for location in item.locations)
        offset += item.lines - 1 + separator.count("\n")
    return _emission(native.PythonTemplate(parts=tuple(parts)), tuple(locations))


def _literal_rows(source: str) -> frozenset[int]:
    protected: set[int] = set()
    interpolated: list[int] = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.STRING:
                protected.update(range(token.start[0] + 1, token.end[0] + 1))
            elif token.type in {tokenize.FSTRING_START, tokenize.TSTRING_START}:
                interpolated.append(token.start[0])
            elif token.type in {tokenize.FSTRING_END, tokenize.TSTRING_END}:
                start = interpolated.pop()
                protected.update(range(start + 1, token.end[0] + 1))
    except (tokenize.TokenError, IndentationError) as error:
        raise ValueError("Invalid Python source: " + str(error)) from error
    return frozenset(protected)


def _python_projection(node: native.Node) -> str:
    """Return a Python projection retaining the native payload line counts."""
    chunks: list[str] = []
    for part in _parts(node):
        if isinstance(part, native.Python):
            chunks.append(part.source)
        else:
            text = _emission(part).text
            chunks.append("pass" + "\n" * text.count("\n"))
    return "".join(chunks)


def _indented(node: native.Node) -> native.PythonTemplate:
    """Return an indented suite with unchanged multiline literal contents."""
    protected = _literal_rows(_python_projection(node))
    parts: list[native.TemplatePart] = []
    line_start = True
    number = 1
    for part in _parts(node):
        if isinstance(part, native.Python):
            rows: list[str] = []
            for row in part.source.splitlines(keepends=True):
                newline = row.endswith(("\n", "\r"))
                needs_indent = bool(row.strip()) or not newline
                prefix = (
                    "    "
                    if line_start and number not in protected and needs_indent
                    else ""
                )
                rows.append(prefix + row)
                line_start = newline
                number += int(newline)
            parts.append(native.Python(source="".join(rows)))
        else:
            if line_start:
                parts.append(native.Python(source="    "))
            parts.append(part)
            number += _emission(part).text.count("\n")
            line_start = False
    return native.PythonTemplate(parts=tuple(parts))


def _suite_emission(suite: _SuiteResult) -> _Emission:
    result = _join(suite.emissions)
    if not any(
        line.strip() and not line.lstrip().startswith("#")
        for line in result.text.splitlines()
    ):
        result = _join(
            (*suite.emissions, _emission(native.Python(source="pass"))), "\n"
        )
    return _emission(_indented(result.node), result.locations)


def _clause(header: str, suite: _SuiteResult, path: ComponentPath) -> _Emission:
    with compilation_context(*path):
        body = _suite_emission(suite)
    return _emission(
        native.PythonTemplate(
            parts=(native.Python(source=header + "\n"), *_parts(body.node))
        ),
        tuple(location.shifted(1) for location in body.locations),
    )


def _target(target: Assignment) -> str:
    text = _encoding.assignment(target).removesuffix(" = ")
    return "(" + text + ")" if isinstance(target, tuple) else text


class _Compiler:
    def __init__(self, lower: LeafLowerer, comments: CommentLowerer) -> None:
        self._lower = lower
        self._comments = comments
        self._serial = 0

    def sequence(
        self,
        spec: c.JobSpec,
        scope: _Scope,
        path: ComponentPath = (),
        *,
        nested: bool = False,
    ) -> _SuiteResult:
        emissions: list[_Emission] = []
        writes: frozenset[str] = frozenset()
        deletions: frozenset[str] = frozenset()
        for index, component in enumerate(spec.components):
            component_path = (*path, "components", index)
            with compilation_context("components", index):
                result = self._component(
                    component, scope, component_path, nested=nested
                )
                annotated = self._comments(component, result.emission.node)
                emission = _emission(annotated)
                comment_lines = emission.lines - result.emission.lines
                locations = (
                    _SourceLocation(first=1, last=emission.lines, path=component_path),
                    *(
                        location.shifted(comment_lines)
                        for location in result.emission.locations
                    ),
                )
                emissions.append(_emission(annotated, locations))
                scope = result.scope
                writes = writes.union(result.writes)
                deletions = deletions.union(result.deletions) - result.scope.definite
        return _SuiteResult(
            emissions=tuple(emissions), scope=scope, writes=writes, deletions=deletions
        )

    def _body(
        self, spec: c.JobSpec, scope: _Scope, path: ComponentPath, field: ComponentPath
    ) -> _SuiteResult:
        with compilation_context(*field):
            return self.sequence(spec, scope, (*path, *field), nested=True)

    def _component(
        self,
        component: c.JobComponent,
        scope: _Scope,
        path: ComponentPath,
        *,
        nested: bool,
    ) -> _ComponentResult:
        match component:
            case c.ForLoop() | c.WhileLoop():
                return self._loop(component, scope, path)
            case c.Conditional():
                return self._conditional(component, scope, path)
            case c.WithBlock():
                return self._with(component, scope, path)
            case c.TryBlock():
                return self._try(component, scope, path)
            case _:
                return self._leaf(component, scope, path, nested=nested)

    def _leaf(
        self,
        component: c.LeafComponent,
        scope: _Scope,
        path: ComponentPath,
        *,
        nested: bool,
    ) -> _ComponentResult:
        names = _provided(component)
        _check_declarations(component, scope, names, nested=nested)
        node = self._lower(
            component, set(scope.definite), scope.layout_map(), self._serial
        )
        self._serial += 1
        result = _emission(node)
        location = (*path, "source") if isinstance(component, c.Python) else path
        return _ComponentResult(
            emission=_emission(
                node, (_SourceLocation(first=1, last=result.lines, path=location),)
            ),
            scope=scope.bind(
                names,
                component if isinstance(component, c.MoleculeDeclaration) else None,
            ),
            writes=frozenset(names),
        )

    def _conditional(
        self, component: c.Conditional, scope: _Scope, path: ComponentPath
    ) -> _ComponentResult:
        with compilation_context("condition"):
            condition = _encoding.encode_value(component.condition, set(scope.definite))
        body = self._body(component.body, scope, path, ("body",))
        clauses = [_clause("if " + condition + ":", body, ("body",))]
        alternate = self._body(
            component.otherwise or c.JobSpec(), scope, path, ("otherwise",)
        )
        if component.otherwise is not None:
            clauses.append(_clause("else:", alternate, ("otherwise",)))
        return _ComponentResult(
            emission=_join(tuple(clauses), "\n"),
            scope=_merge((body.scope, alternate.scope)),
            writes=body.writes.union(alternate.writes),
            deletions=body.deletions.union(alternate.deletions),
        )

    def _loop(
        self, component: c.ForLoop | c.WhileLoop, scope: _Scope, path: ComponentPath
    ) -> _ComponentResult:
        body_scope = scope
        targets: tuple[str, ...] = ()
        if isinstance(component, c.ForLoop):
            with compilation_context("iterable"):
                iterable = _encoding.encode_value(
                    component.iterable, set(scope.definite)
                )
            with compilation_context("target"):
                target = _target(component.target)
            targets = assignment_names(component.target)
            body_scope = scope.bind(targets)
            header = "for " + target + " in " + iterable + ":"
        else:
            with compilation_context("condition"):
                condition = _encoding.encode_value(
                    component.condition, set(scope.definite)
                )
            header = "while " + condition + ":"
        body = self._body(component.body, body_scope, path, ("body",))
        # Loop targets are not available in an else body if the iterable is empty.
        alternate_scope = _merge((scope, body.scope))
        alternate = self._body(
            component.otherwise or c.JobSpec(), alternate_scope, path, ("otherwise",)
        )
        clauses = [_clause(header, body, ("body",))]
        if component.otherwise is not None:
            clauses.append(_clause("else:", alternate, ("otherwise",)))
        return _ComponentResult(
            emission=_join(tuple(clauses), "\n"),
            scope=_merge((scope, body.scope, alternate.scope)),
            writes=body.writes.union(alternate.writes, targets),
            deletions=body.deletions.union(alternate.deletions),
        )

    def _with(
        self, component: c.WithBlock, scope: _Scope, path: ComponentPath
    ) -> _ComponentResult:
        managers: list[str] = []
        entered: list[_Scope] = []
        targets: set[str] = set()
        current = scope
        for index, item in enumerate(component.items):
            with compilation_context("items", index):
                with compilation_context("context"):
                    context = _encoding.encode_value(
                        item.context, set(current.definite)
                    )
                with compilation_context("target"):
                    target = _target(item.target)
                managers.append(context + (" as " + target if target else ""))
                names = assignment_names(item.target)
                targets.update(names)
                current = current.bind(names)
                entered.append(current)
        body = self._body(component.body, current, path, ("body",))
        # A manager can suppress target-unpacking or later __enter__ failures.
        guaranteed = entered[0] if isinstance(component.items[0].target, str) else scope
        return _ComponentResult(
            emission=_clause("with " + ", ".join(managers) + ":", body, ("body",)),
            scope=_merge(
                (
                    guaranteed,
                    *entered,
                    body.scope,
                )
            ),
            writes=body.writes.union(targets),
            deletions=body.deletions,
        )

    def _try(
        self, component: c.TryBlock, scope: _Scope, path: ComponentPath
    ) -> _ComponentResult:
        body = self._body(component.body, scope, path, ("body",))
        clauses = [_clause("try:", body, ("body",))]
        success = self._body(
            component.otherwise or c.JobSpec(), body.scope, path, ("otherwise",)
        )
        handlers = [
            self._handler(handler, scope, path, index)
            for index, handler in enumerate(component.handlers)
        ]
        clauses.extend(result.emission for result in handlers)
        if component.otherwise is not None:
            clauses.append(_clause("else:", success, ("otherwise",)))
        exits = (success.scope, *(result.scope for result in handlers))
        outgoing = _merge(exits)
        writes = body.writes.union(
            success.writes, *(result.writes for result in handlers)
        )
        deletions = body.deletions.union(
            success.deletions, *(result.deletions for result in handlers)
        )
        if component.finally_body is not None:
            # Cleanup can run before the try body has created any new names.
            final_input = _merge((scope, *exits))
            final = self._body(
                component.finally_body, final_input, path, ("finally_body",)
            )
            clauses.append(_clause("finally:", final, ("finally_body",)))
            outgoing = _after_finally(outgoing, final_input, final)
            writes = writes.union(final.writes)
            deletions = deletions.union(final.deletions)
        return _ComponentResult(
            emission=_join(tuple(clauses), "\n"),
            scope=outgoing,
            writes=writes,
            deletions=deletions,
        )

    def _handler(
        self,
        handler: c.ExceptionHandler,
        scope: _Scope,
        path: ComponentPath,
        index: int,
    ) -> _ComponentResult:
        field: ComponentPath = ("handlers", index)
        with compilation_context(*field):
            with compilation_context("exception"):
                exception = (
                    _encoding.encode_value(handler.exception, set(scope.definite))
                    if handler.exception is not None
                    else ""
                )
            with compilation_context("name"):
                name = (
                    _encoding.name(handler.name) if handler.name is not None else None
                )
        incoming = scope.bind((name,)) if name is not None else scope
        body = self._body(handler.body, incoming, path, (*field, "body"))
        header = "except" + (" " + exception if exception else "")
        if name is not None:
            header += " as " + name
        outgoing = body.scope.discard(name) if name is not None else body.scope
        return _ComponentResult(
            emission=_clause(header + ":", body, (*field, "body")),
            scope=outgoing,
            writes=body.writes.union((name,) if name else ()),
            deletions=body.deletions.union((name,) if name else ()),
        )


def _after_finally(outgoing: _Scope, incoming: _Scope, final: _SuiteResult) -> _Scope:
    introduced = final.scope.definite - incoming.definite
    molecules = tuple(
        entry for entry in outgoing.molecules if entry.name not in final.writes
    )
    molecules += tuple(
        entry for entry in final.scope.molecules if entry.name in final.writes
    )
    return _Scope(
        definite=(outgoing.definite - final.deletions).union(introduced),
        possible=outgoing.possible.union(final.scope.possible),
        molecules=molecules,
    )


def _provided(component: c.LeafComponent) -> tuple[str, ...]:
    if isinstance(component, (c.Calculation, c.Call)):
        return assignment_names(component.assign)
    if isinstance(component, c.Python):
        return component.provides
    return (component.name,) if isinstance(component, c.MoleculeDeclaration) else ()


def _check_declarations(
    component: c.LeafComponent, scope: _Scope, names: tuple[str, ...], *, nested: bool
) -> None:
    for index, name in enumerate(names):
        if isinstance(component, c.MoleculeDeclaration):
            field: ComponentPath = ("name",)
        elif isinstance(component, c.Python):
            field = ("provides", index)
        elif isinstance(component, (c.Calculation, c.Call)) and isinstance(
            component.assign, tuple
        ):
            field = ("assign", index)
        else:
            field = ("assign",)
        with compilation_context(*field):
            _encoding.name(name)
            if names.count(name) > 1 or (
                name in scope.possible
                and (not nested or isinstance(component, c.MoleculeDeclaration))
            ):
                raise ValueError("Duplicate declaration: " + name)


def compile_spec(
    spec: c.JobSpec, lower: LeafLowerer, comments: CommentLowerer
) -> CompiledJob:
    """Return a native job and its complete, validated Psithon source.

    Raises:
        CompilationError: A component, reference, or complete input is invalid.
    """
    suite = _Compiler(lower, comments).sequence(spec, _Scope())
    combined = _join(suite.emissions)
    job = native.Job(body=tuple(item.node for item in suite.emissions))
    source = native.emit_job(job, validate=False)
    diagnostics: list[CompilationDiagnostic] = []
    for diagnostic in parse(source).diagnostics:
        owner: _SourceLocation | None = None
        for location in combined.locations:
            if location.first <= diagnostic.line <= location.last and (
                owner is None or len(location.path) > len(owner.path)
            ):
                owner = location
        diagnostics.append(
            CompilationDiagnostic(
                path=owner.path if owner is not None else (),
                message=diagnostic.message,
                line=diagnostic.line,
                column=diagnostic.column,
            )
        )
    if diagnostics:
        raise CompilationError(tuple(diagnostics))
    return CompiledJob(job=job, source=source)
