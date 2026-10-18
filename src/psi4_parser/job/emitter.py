"""Render structured jobs as Psithon input."""

from typing import assert_never

from psi4_parser.api import parse
from psi4_parser.job.model import (
    FragmentSeparator,
    Nucleus,
    Number,
    Scalar,
    Units,
    Variable,
)
from psi4_parser.job.molecule import (
    Atom,
    AtomReference,
    Cartesian,
    EFPFragment,
    ElectronicState,
    FrameDirective,
    GeometrySource,
    GeometryVariable,
    Molecule,
    MoleculeRecord,
    Symmetry,
    XYZHeader,
)
from psi4_parser.job.nodes import (
    PCM,
    Basis,
    BasisAssignment,
    BasisData,
    BasisLabel,
    CFour,
    External,
    ExternalAtom,
    ExternalBasis,
    Job,
    Memory,
    NativeNode,
    Node,
    OptionArray,
    OptionExpression,
    OptionReference,
    OptionValue,
    PointCharge,
    Python,
    PythonTemplate,
    SetOptions,
)
from psi4_parser.job.reader import JobSyntaxError


def _scalar(value: Scalar) -> str:
    match value:
        case Number():
            return value.value
        case Variable():
            return ("-" if value.negative else "") + value.name
    assert_never(value)


def _nucleus(nucleus: Nucleus) -> str:
    label = nucleus.label
    if nucleus.mass is not None:
        label += "@" + nucleus.mass.value
    match nucleus.ghost:
        case "at":
            return "@" + label
        case "gh":
            return "Gh(" + label + ")"
        case "none":
            return label
    assert_never(nucleus.ghost)


def _atom(record: Atom, indices: dict[str, int]) -> str:
    fields = [_nucleus(record.nucleus)]
    position = record.coordinates
    if isinstance(position, Cartesian):
        fields.extend(map(_scalar, (position.x, position.y, position.z)))
    else:
        for anchor in position.anchors:
            reference = anchor.atom
            if isinstance(reference, AtomReference):
                if reference.atom_id not in indices:
                    raise ValueError("Unknown atom reference: " + reference.atom_id)
                target = str(indices[reference.atom_id])
            else:
                target = reference.label
            fields.extend((target, _scalar(anchor.value)))
    return " ".join(fields)


def _metadata(
    record: ElectronicState
    | FragmentSeparator
    | GeometryVariable
    | Units
    | Symmetry
    | FrameDirective
    | GeometrySource,
) -> str:
    match record:
        case ElectronicState():
            text = record.charge.value + " " + record.multiplicity.value
        case FragmentSeparator():
            text = "--"
        case GeometryVariable():
            text = record.name + " = " + _scalar(record.value)
        case Units():
            text = "units " + record.name
        case Symmetry():
            text = "symmetry " + record.group
        case FrameDirective():
            text = record.name
        case GeometrySource():
            text = record.provider + ": " + record.value
        case _:
            assert_never(record)
    return text


def _record(record: MoleculeRecord, indices: dict[str, int]) -> str:
    match record:
        case Atom():
            return _atom(record, indices)
        case (
            ElectronicState()
            | FragmentSeparator()
            | GeometryVariable()
            | Units()
            | Symmetry()
            | FrameDirective()
            | GeometrySource()
        ):
            return _metadata(record)
        case XYZHeader():
            units = " " + record.units if record.units else ""
            return record.count + units + "\n" + record.title
        case EFPFragment():
            points = [
                " ".join(number.value for number in triple) for triple in record.points
            ]
            match points:
                case [position, orientation]:
                    return "efp " + record.name + " " + position + " " + orientation
                case _:
                    return "efp " + record.name + "\n" + "\n".join(points)
    assert_never(record)


def _block(header: str, rows: list[str], indentation: str) -> str:
    body = "".join(indentation + "    " + row + "\n" for row in rows)
    return header + " {\n" + body + indentation + "}"


def _option(value: OptionValue) -> str:
    match value:
        case OptionExpression():
            return value.source
        case OptionReference():
            return "$" + value.name
        case OptionArray():
            return "[" + "".join(map(_option, value.parts)) + "]"
    assert_never(value)


def _basis(node: Basis, indentation: str) -> str:
    rows = []
    for record in node.records:
        match record:
            case BasisAssignment():
                target = record.target + " " if record.target is not None else ""
                rows.append("assign " + target + record.basis)
            case BasisLabel():
                rows.append("[" + record.name + "]")
            case BasisData():
                rows.append(record.text)
            case _:
                assert_never(record)
    header = node.role + (" " + node.name if node.name is not None else "")
    return _block(header, rows, indentation)


def _external(node: External, indentation: str) -> str:
    rows = []
    for record in node.records:
        match record:
            case PointCharge():
                fields = [
                    record.charge.value,
                    *(value.value for value in record.position),
                ]
                rows.append(" ".join(fields))
            case ExternalAtom():
                rows.append(
                    _nucleus(record.nucleus)
                    + " "
                    + " ".join(value.value for value in record.position)
                )
            case ExternalBasis():
                rows.append(record.role + " " + record.value)
            case Units():
                rows.append("units " + record.name)
            case FragmentSeparator():
                rows.append("--")
            case _:
                assert_never(record)
    header = "external" + (" " + node.name if node.name is not None else "")
    return _block(header, rows, indentation)


def _native(node: NativeNode, indentation: str) -> str:
    match node:
        case Molecule():
            indices = {atom.id: index for index, atom in enumerate(node.atoms, start=1)}
            if len(indices) != len(node.atoms):
                raise ValueError("Molecule contains duplicate atom identities")
            rows = [_record(record, indices) for record in node.records]
            header = "molecule" + (" " + node.name if node.name is not None else "")
            text = _block(header, rows, indentation)
        case SetOptions():
            header = "set" + (" " + ",".join(node.modules) if node.modules else "")
            rows = [
                assignment.key + " " + _option(assignment.value)
                for assignment in node.assignments
            ]
            if node.style == "inline":
                if len(rows) != 1:
                    raise ValueError("An inline set command requires one assignment")
                text = header + " " + rows[0]
            else:
                text = _block(header, rows, indentation)
        case Basis():
            text = _basis(node, indentation)
        case External():
            text = _external(node, indentation)
        case PCM() | CFour():
            header = node.kind + (" " + node.name if node.name is not None else "")
            text = header + " {" + node.body + "}"
        case Memory():
            text = node.prefix + "memory " + node.amount.value + " " + node.units
        case _:
            assert_never(node)
    return text


def _node(node: Node) -> str:
    match node:
        case Python():
            return node.source
        case PythonTemplate():
            chunks: list[str] = []
            for part in node.parts:
                if isinstance(part, Python):
                    chunks.append(part.source)
                else:
                    prefix = "".join(chunks).rsplit("\n", 1)[-1]
                    indentation = prefix if not prefix.strip() else ""
                    chunks.append(_native(part, indentation))
            return "".join(chunks)
        case _:
            return _native(node, "")


def emit_job(job: Job, *, validate: bool = True) -> str:
    """Emit a job and check native and contextual Python syntax by default.

    Args:
        job: Structured native job; its Python text is never executed.
        validate: Run the established parser on the complete emitted source.

    Returns:
        Psithon source with one empty line between top-level components.

    Raises:
        JobSyntaxError: Emitted Python or native syntax is invalid.
        ValueError: An atom reference or inline option specification is invalid.
    """  # noqa: DOC502 - Native emission helpers also raise ValueError.
    source = "\n\n".join(_node(node).rstrip("\r\n") for node in job.body)
    if source:
        source += "\n"
    if validate:
        result = parse(source)
        if result.diagnostics:
            raise JobSyntaxError(result.diagnostics)
    return source
