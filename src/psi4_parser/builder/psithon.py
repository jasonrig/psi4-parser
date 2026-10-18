"""Compile independent job specifications into validated, formatted Psithon."""

import ast
import keyword
import re
from typing import assert_never

from pydantic import Field

from psi4_parser import job as native
from psi4_parser.builder import components as c
from psi4_parser.builder import molecular as m
from psi4_parser.builder._model import BOHR_ANGSTROM, Angle, Length, Model
from psi4_parser.builder.constraints import Bounded, Constraint, Frozen
from psi4_parser.builder.values import (
    Expression,
    LiteralValue,
    MappingValue,
    Reference,
    SequenceValue,
    Value,
)
from psi4_parser.formatting import format_source


class OptionScope(Model):
    """Identify a global or module-local option whose state must be restored."""

    option: str = Field(description="Uppercase option name.")
    module: str | None = Field(
        default=None, description="Uppercase module name, or None for a global option."
    )

    def arguments(self) -> list[str]:
        """Return the option-name sequence expected by Psi4 OptionsState."""
        return [self.option] if self.module is None else [self.module, self.option]


_PREFIX = "_psi4_builder_"
_CONSTRAINT_NAMES = {
    "distance": "DISTANCE",
    "angle": "BEND",
    "dihedral": "DIHEDRAL",
    "out_of_plane": "OOFP",
    "cartesian": "CARTESIAN",
}


def _name(name: str) -> str:
    if not name.isidentifier() or keyword.iskeyword(name) or name.startswith(_PREFIX):
        raise ValueError("Invalid or reserved Python binding: " + name)
    return name


def _expression(source: str) -> str:
    ast.parse(source, mode="eval")
    return source


def _literal(item: str | bool | int | float | None) -> str:
    return repr(item).replace("#", r"\x23").replace("psi", r"\x70si")


def _value(item: Value, bindings: set[str]) -> str:
    match item:
        case LiteralValue():
            return _literal(item.value)
        case Reference():
            _name(item.name)
            if item.name not in bindings:
                raise ValueError("Reference must follow its declaration: " + item.name)
            return item.name
        case Expression():
            return "(" + _expression(item.source) + ")"
        case SequenceValue():
            content = ", ".join(_value(v, bindings) for v in item.items)
            if item.style == "list":
                return "[" + content + "]"
            return "(" + content + ("," if len(item.items) == 1 else "") + ")"
        case MappingValue():
            return (
                "{"
                + ", ".join(
                    _value(e.key, bindings) + ": " + _value(e.value, bindings)
                    for e in item.entries
                )
                + "}"
            )
        case _:
            assert_never(item)


def _option_string(text: str) -> str:
    # Psi4 quotifies words before parsing Python literals. Encode punctuation
    # outside its word alphabet so literal strings survive that substitution.
    encoded = (
        '"'
        + "".join(
            char if re.fullmatch(r"[\w+*/().-]", char) else f"\\U{ord(char):08x}"
            for char in text
        )
        + '"'
    )
    return encoded.replace("psi", r"\x70si")


def _option(item: Value | c.OptionExpression, bindings: set[str]) -> native.OptionValue:
    match item:
        case c.OptionExpression():
            return native.OptionExpression(source=item.source)
        case Reference():
            _value(item, bindings)
            return native.OptionReference(name=item.name)
        case SequenceValue():
            parts: list[native.OptionValue] = []
            for index, element in enumerate(item.items):
                if index:
                    parts.append(native.OptionExpression(source=","))
                parts.append(_option(element, bindings))
            return native.OptionArray(parts=tuple(parts))
        case LiteralValue():
            return _option_literal(item)
        case Expression() | MappingValue():
            raise ValueError(
                "Native options require literals, arrays, references, "
                "or OptionExpression"
            )
        case _:
            assert_never(item)


def _option_literal(item: LiteralValue) -> native.OptionExpression:
    if isinstance(item.value, str):
        source = _option_string(item.value)
    elif isinstance(item.value, bool):
        source = "true" if item.value else "false"
    elif item.value is None:
        raise ValueError(
            "Native options cannot represent None; use Python for this value"
        )
    else:
        source = repr(item.value)
    return native.OptionExpression(source=source)


def _options(component: c.Options, bindings: set[str]) -> native.SetOptions:
    return native.SetOptions(
        modules=component.modules,
        assignments=tuple(
            native.OptionAssignment(key=a.key, value=_option(a.value, bindings))
            for a in component.assignments
        ),
    )


def _number(value: float | int) -> native.Number:
    return native.Number(value=repr(value))


def _triple(
    value: tuple[float, float, float],
) -> tuple[native.Number, native.Number, native.Number]:
    return _number(value[0]), _number(value[1]), _number(value[2])


def _nucleus(value: m.Nucleus) -> native.Nucleus:
    return native.Nucleus(
        label=value.label,
        ghost=value.ghost,
        mass=None if value.mass is None else _number(value.mass),
    )


def _scalar(
    value: m.InternalValue | float, units: str, *, cartesian_unit: str | None = None
) -> native.Scalar:
    if isinstance(value, m.Parameter):
        return native.Variable(name=value.name, negative=value.negative)
    if isinstance(value, m.GeometryExpression):
        return native.Variable(name=value.source)
    if isinstance(value, Length):
        return _number(value.angstroms / (BOHR_ANGSTROM if units == "bohr" else 1.0))
    if isinstance(value, Angle):
        return _number(value.degrees)
    scale = BOHR_ANGSTROM if cartesian_unit == "bohr" else 1.0
    return _number(value * scale / (BOHR_ANGSTROM if units == "bohr" else 1.0))


def _atom(atom: m.Atom, units: str) -> native.Atom:
    position = atom.coordinates
    if isinstance(position, m.Cartesian):
        coordinates: native.Coordinates = native.Cartesian(
            x=_scalar(position.x, units, cartesian_unit=position.unit),
            y=_scalar(position.y, units, cartesian_unit=position.unit),
            z=_scalar(position.z, units, cartesian_unit=position.unit),
        )
    else:
        coordinates = native.ZMatrix(
            anchors=tuple(
                native.Anchor(
                    atom=native.AtomReference(atom_id=a.atom),
                    value=_scalar(a.value, units),
                )
                for a in position.anchors
            )
        )
    return native.Atom(
        id=atom.id, nucleus=_nucleus(atom.nucleus), coordinates=coordinates
    )


def _state(state: m.ElectronicState) -> native.ElectronicState:
    return native.ElectronicState(
        charge=_number(state.charge), multiplicity=_number(state.multiplicity)
    )


def _molecule(component: c.MoleculeDeclaration) -> native.Molecule:
    geometry = component.geometry
    records: list[native.MoleculeRecord] = []
    if geometry.state is not None:
        records.append(_state(geometry.state))
        if geometry.fragments:
            records.append(native.FragmentSeparator())
    if geometry.xyz_header is not None:
        records.append(
            native.XYZHeader(
                count=str(len(geometry.atoms)),
                units=geometry.xyz_header.units
                or ("bohr" if geometry.units == "bohr" else None),
                title=geometry.xyz_header.title,
            )
        )
    atoms = {a.id: a for a in geometry.atoms}
    effective = {f.id: f for f in geometry.efp}
    fragments = geometry.fragments or (
        m.Fragment(name="implicit", atom_ids=tuple(atoms), efp_ids=tuple(effective)),
    )
    for index, fragment in enumerate(fragments):
        if index:
            records.append(native.FragmentSeparator())
        if fragment.state is not None:
            records.append(_state(fragment.state))
        records.extend(_atom(atoms[key], geometry.units) for key in fragment.atom_ids)
        for key in fragment.efp_ids:
            item = effective[key]
            records.append(
                native.EFPFragment(
                    name=item.name,
                    points=tuple(_triple(p) for p in item.points),
                )
            )
    records.extend(_molecule_directives(geometry))
    return native.Molecule(name=component.name, records=tuple(records))


def _molecule_directives(geometry: m.Molecule) -> list[native.MoleculeRecord]:
    records: list[native.MoleculeRecord] = []
    records.extend(
        native.GeometrySource(provider=s.provider, value=s.value)
        for s in geometry.sources
    )
    records.extend(
        native.GeometryVariable(name=p.name, value=_scalar(p.value, geometry.units))
        for p in geometry.parameters
    )
    if geometry.xyz_header is None:
        records.append(native.Units(name=geometry.units))
    if geometry.symmetry is not None:
        records.append(native.Symmetry(group=geometry.symmetry))
    if geometry.fixed_com:
        records.append(native.FrameDirective(name="no_com"))
    if geometry.fixed_orientation:
        records.append(native.FrameDirective(name="no_reorient"))
    return records


def _basis(component: c.Basis) -> native.Basis:
    records: list[native.BasisRecord] = []
    for record in component.records:
        match record:
            case c.BasisAssignment():
                records.append(
                    native.BasisAssignment(basis=record.basis, target=record.target)
                )
            case c.BasisLabel():
                records.append(native.BasisLabel(name=record.name))
            case c.BasisData():
                records.append(native.BasisData(text=record.text))
            case _:
                assert_never(record)
    return native.Basis(
        role=component.role, name=component.name, records=tuple(records)
    )


def _external(component: c.External) -> native.External:
    records: list[native.ExternalRecord] = []
    for record in component.records:
        match record:
            case c.PointCharge():
                records.append(
                    native.PointCharge(
                        charge=_number(record.charge),
                        position=_triple(record.position),
                    )
                )
            case c.ExternalAtom():
                records.append(
                    native.ExternalAtom(
                        nucleus=_nucleus(record.nucleus),
                        position=_triple(record.position),
                    )
                )
            case c.ExternalBasis():
                records.append(
                    native.ExternalBasis(role=record.role, value=record.value)
                )
            case c.ExternalUnits():
                records.append(native.Units(name=record.name))
            case c.ExternalSeparator():
                records.append(native.FragmentSeparator())
            case _:
                assert_never(record)
    return native.External(name=component.name, records=tuple(records))


def _keywords(keywords: tuple[c.Keyword, ...], bindings: set[str]) -> list[str]:
    if len({k.name for k in keywords}) != len(keywords):
        raise ValueError("Duplicate call keyword arguments")
    return [_name(k.name) + "=" + _value(k.value, bindings) for k in keywords]


def _assignment(assign: str | tuple[str, ...] | None) -> str:
    if assign is None:
        return ""
    names = (assign,) if isinstance(assign, str) else assign
    if not names or len(set(names)) != len(names):
        raise ValueError("Assignment requires distinct binding names")
    return (
        ", ".join(_name(n) for n in names)
        + ("," if len(names) == 1 and isinstance(assign, tuple) else "")
        + " = "
    )


def _constraint_values(
    constraints: tuple[Constraint, ...], geometry: m.Molecule
) -> dict[str, str]:
    indices = {
        a.id: i
        for i, a in enumerate((a for a in geometry.atoms if not a.nucleus.dummy), 1)
    }
    grouped: dict[str, list[str]] = {}
    for constraint in constraints:
        coord = constraint.coordinate
        if not set(coord.atoms) <= indices.keys():
            raise ValueError("Constraints require known non-dummy atom IDs")
        if (
            isinstance(constraint, Bounded)
            and coord.kind == "cartesian"
            and not (geometry.fixed_com and geometry.fixed_orientation)
        ):
            raise ValueError(
                "Ranged Cartesian constraints require fixed_com=True "
                "and fixed_orientation=True"
            )
        if coord.kind == "cartesian" and any(
            isinstance(a.coordinates, m.ZMatrix) for a in geometry.atoms
        ):
            raise ValueError("Cartesian constraints require Cartesian geometry")
        fields = [str(indices[a]) for a in coord.atoms]
        if coord.kind == "cartesian":
            fields.append(coord.axes.upper())
        if isinstance(constraint, Bounded):
            fields.extend(
                repr(limit.angstroms if isinstance(limit, Length) else limit.degrees)
                for limit in (constraint.lower, constraint.upper)
            )
        name = (
            "FROZEN_" if isinstance(constraint, Frozen) else "RANGED_"
        ) + _CONSTRAINT_NAMES[coord.kind]
        grouped.setdefault(name, []).append(" ".join(fields))
    return {key: " ".join(rows) for key, rows in grouped.items()}


def _check_constraint_conflicts(component: c.Calculation, names: set[str]) -> None:
    for block in component.local_options:
        if any(a.key.upper() in names for a in block.assignments) and (
            not block.modules
            or any(
                module.upper() in {"OPTKING", "GLOBAL", "GLOBALS"}
                for module in block.modules
            )
        ):
            raise ValueError(
                "Typed and raw definitions conflict for a constraint setting"
            )
    for argument in component.kwargs:
        if argument.name == "optimizer_keywords":
            if not isinstance(argument.value, MappingValue):
                raise ValueError(
                    "Typed constraints require inspectable optimizer_keywords"
                )
            for entry in argument.value.entries:
                if not isinstance(entry.key, LiteralValue) or not isinstance(
                    entry.key.value, str
                ):
                    raise ValueError(
                        "Typed constraints require literal optimizer keyword names"
                    )
                if entry.key.value.upper() in names:
                    raise ValueError(
                        "Typed and raw definitions conflict for a constraint setting"
                    )
        if argument.name == "engine" and argument.value != LiteralValue(
            value="optking"
        ):
            raise ValueError("Typed constraints support only the OptKing engine")


def _calculation_statement(component: c.Calculation, bindings: set[str]) -> str:
    arguments = [_value(component.method, bindings)]
    keywords = _keywords(component.kwargs, bindings)
    if component.molecule is not None:
        if any(k.name == "molecule" for k in component.kwargs):
            raise ValueError("Molecule is specified more than once")
        arguments.append("molecule=" + _value(component.molecule, bindings))
    arguments.extend(keywords)
    return (
        _assignment(component.assign)
        + component.driver
        + "("
        + ", ".join(arguments)
        + ")"
    )


def _typed_constraints(
    component: c.Calculation, molecules: dict[str, m.Molecule]
) -> dict[str, str]:
    if not component.constraints:
        return {}
    if (
        component.driver != "optimize"
        or component.molecule is None
        or component.molecule.name not in molecules
    ):
        raise ValueError(
            "Typed constraints require optimize and a structured molecule reference"
        )
    geometry = molecules[component.molecule.name]
    if geometry.sources or geometry.efp:
        raise ValueError("Typed constraints require a resolved atom list")
    constraints = _constraint_values(component.constraints, geometry)
    _check_constraint_conflicts(component, set(constraints))
    return constraints


def _calculation(
    component: c.Calculation,
    bindings: set[str],
    molecules: dict[str, m.Molecule],
    serial: int,
) -> native.Node:
    statement = _calculation_statement(component, bindings)
    if not component.constraints and not component.local_options:
        return native.Python(source=statement)
    constraints = _typed_constraints(component, molecules)
    snapshots: list[OptionScope] = []
    for block in component.local_options:
        for module in block.modules or ("",):
            normalized = module.upper()
            scope = None if normalized in {"", "GLOBAL", "GLOBALS"} else normalized
            snapshots.extend(
                OptionScope(module=scope, option=a.key.upper())
                for a in block.assignments
            )
    snapshots.extend(OptionScope(module="OPTKING", option=key) for key in constraints)
    unique: list[OptionScope] = []
    for snapshot in snapshots:
        if snapshot not in unique:
            unique.append(snapshot)
    snapshots = unique
    temporary = _PREFIX + f"options_{serial}"
    setup = (
        "import psi4 as "
        + _PREFIX
        + "psi4\n"
        + temporary
        + " = "
        + _PREFIX
        + "psi4.driver.p4util.OptionsState("
        + ", ".join(repr(scope.arguments()) for scope in snapshots)
        + ")\ntry:\n"
    )
    parts: list[native.TemplatePart] = [native.Python(source=setup)]
    for block in component.local_options:
        if block.comments:
            parts.append(
                native.Python(source=_comment_source(block, indentation="    "))
            )
        parts.extend(
            (
                native.Python(source="    "),
                _options(block, bindings),
                native.Python(source="\n"),
            )
        )
    body = "".join(
        "    "
        + _PREFIX
        + "psi4.core.set_local_option('OPTKING', "
        + repr(key)
        + ", "
        + repr(text)
        + ")\n"
        for key, text in constraints.items()
    )
    body += "    " + statement + "\nfinally:\n    " + temporary + ".restore()\n"
    parts.append(native.Python(source=body))
    return native.PythonTemplate(parts=tuple(parts))


def _native_component(
    component: c.NativeComponent, bindings: set[str]
) -> native.NativeNode:
    match component:
        case c.MoleculeDeclaration():
            result: native.NativeNode = _molecule(component)
        case c.Options():
            result = _options(component, bindings)
        case c.Basis():
            result = _basis(component)
        case c.External():
            result = _external(component)
        case c.PCM():
            result = native.PCM(name=component.name, body=component.body)
        case c.CFour():
            result = native.CFour(name=component.name, body=component.body)
        case c.Memory():
            result = native.Memory(
                amount=_number(component.amount), units=component.units
            )
        case _:
            assert_never(component)
    return result


def _lower(
    component: c.JobComponent,
    bindings: set[str],
    molecules: dict[str, m.Molecule],
    serial: int,
) -> native.Node:
    if isinstance(component, c.Calculation):
        return _calculation(component, bindings, molecules, serial)
    if isinstance(component, c.Call):
        arguments = [_value(a, bindings) for a in component.args] + _keywords(
            component.kwargs, bindings
        )
        return native.Python(
            source=_assignment(component.assign)
            + "("
            + _expression(component.target)
            + ")("
            + ", ".join(arguments)
            + ")"
        )
    if isinstance(component, c.Python):
        if _PREFIX in component.source:
            raise ValueError("Python source uses the reserved builder name prefix")
        return native.Python(source=component.source)
    return _native_component(component, bindings)


def _provided(component: c.JobComponent) -> tuple[str, ...]:
    if isinstance(component, (c.Calculation, c.Call)):
        return (
            ()
            if component.assign is None
            else (component.assign,)
            if isinstance(component.assign, str)
            else component.assign
        )
    if isinstance(component, c.Python):
        return component.provides
    if isinstance(component, c.MoleculeDeclaration):
        return (component.name,)
    return ()


def _comment_source(component: c.Component, *, indentation: str = "") -> str:
    return "".join(
        indentation + "#" + (" " + line if line else "") + "\n"
        for block in component.comments
        for line in block.text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    )


def _commented(component: c.JobComponent, node: native.Node) -> native.Node:
    if not component.comments:
        return node
    comments = _comment_source(component)
    prefix = native.Python(source=comments)
    if isinstance(node, native.Python):
        return native.Python(source=comments + node.source)
    if isinstance(node, native.PythonTemplate):
        return native.PythonTemplate(parts=(prefix, *node.parts))
    return native.PythonTemplate(parts=(prefix, node))


def lower_job(spec: c.JobSpec) -> native.Job:
    """Return a compiled AST after validating bindings and complete input.

    Raises:
        ValueError: Names, references, or backend combinations are invalid.
    """
    bindings: set[str] = set()
    molecules: dict[str, m.Molecule] = {}
    nodes: list[native.Node] = []
    for serial, component in enumerate(spec.components):
        names = _provided(component)
        for name in names:
            _name(name)
            if name in bindings or names.count(name) > 1:
                raise ValueError("Duplicate declaration: " + name)
        node = _lower(component, bindings, molecules, serial)
        nodes.append(_commented(component, node))
        bindings.update(names)
        if isinstance(component, c.MoleculeDeclaration):
            molecules[component.name] = component.geometry
    result = native.Job(body=tuple(nodes))
    native.emit_job(result)
    return result


def render_job(spec: c.JobSpec) -> str:
    """Return validated Psithon with the agreed formatting style."""
    return format_source(native.emit_job(lower_job(spec)))
