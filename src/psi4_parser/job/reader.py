"""Build native job models directly from the original ANTLR concrete tree."""

import re
from collections.abc import Callable, Iterator
from typing import Literal

from antlr4 import ParserRuleContext, Token
from antlr4.tree.Tree import TerminalNodeImpl

from psi4_parser._tree import contexts, rule_name, terminals
from psi4_parser.api import Diagnostic, ParseResult, parse
from psi4_parser.job.model import (
    FragmentSeparator,
    Nucleus,
    Number,
    Scalar,
    Units,
    Variable,
)
from psi4_parser.job.molecule import (
    Anchor,
    Atom,
    AtomReference,
    Cartesian,
    EFPFragment,
    ElectronicState,
    FrameDirective,
    GeometrySource,
    GeometryVariable,
    LabelReference,
    Molecule,
    MoleculeRecord,
    NumericTriple,
    Symmetry,
    XYZHeader,
    ZMatrix,
)
from psi4_parser.job.nodes import (
    PCM,
    Basis,
    BasisAssignment,
    BasisData,
    BasisLabel,
    BasisRecord,
    CFour,
    External,
    ExternalAtom,
    ExternalBasis,
    ExternalRecord,
    Job,
    Memory,
    NativeNode,
    Node,
    OptionArray,
    OptionAssignment,
    OptionExpression,
    OptionReference,
    OptionValue,
    PointCharge,
    Python,
    PythonTemplate,
    SetOptions,
    TemplatePart,
)

_NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[dDeE][+-]?\d+)?\Z")


class JobSyntaxError(ValueError):
    """Retain diagnostics from contextual validation of a serialized job.

    Attributes:
        diagnostics: Original grammar diagnostics without executing input.
    """

    def __init__(self, diagnostics: tuple[Diagnostic, ...]) -> None:
        """Retain the rejected job's diagnostics.

        Args:
            diagnostics: Nonempty diagnostics returned by the native parser.
        """
        self.diagnostics = diagnostics
        first = diagnostics[0]
        super().__init__(f"{first.line}:{first.column}: {first.message}")


def _children(
    node: ParserRuleContext, name: str | None = None
) -> list[ParserRuleContext]:
    children = node.getTypedRuleContexts(ParserRuleContext)
    return [child for child in children if name is None or rule_name(child) == name]


def _child(node: ParserRuleContext, name: str) -> ParserRuleContext:
    matches = _children(node, name)
    if len(matches) != 1:
        raise ValueError(f"Expected one {name} in {rule_name(node)}")
    return matches[0]


def _tokens(node: ParserRuleContext) -> Iterator[Token]:
    for child in node.getChildren():
        if isinstance(child, TerminalNodeImpl):
            yield child.getSymbol()
        elif isinstance(child, ParserRuleContext):
            yield from _tokens(child)


def _numbers(node: ParserRuleContext) -> list[Number]:
    return [
        Number(value=token.text)
        for token in _tokens(node)
        if _NUMBER.fullmatch(token.text)
    ]


def _scalar(node: ParserRuleContext) -> Scalar:
    text = node.getText()
    if _NUMBER.fullmatch(text):
        return Number(value=text)
    return Variable(name=text.removeprefix("-"), negative=text.startswith("-"))


def _name(node: ParserRuleContext, field: str = "header_label") -> str | None:
    names = _children(node, field)
    return names[0].getText() if names else None


def _body(result: ParseResult, node: ParserRuleContext) -> str:
    braces = [token for token in _tokens(node) if token.text in {"{", "}"}]
    first = result.source_span(braces[0])[1]
    last = result.source_span(braces[-1])[0]
    return result.source[first:last]


def _nucleus(node: ParserRuleContext) -> Nucleus:
    label = _child(node, "nucleus_label").getText()
    masses = _children(node, "isotope_mass")
    mass = _numbers(masses[0])[0] if masses else None
    text = node.getText()
    ghost: Literal["none", "at", "gh"] = "none"
    if text.startswith("@"):
        ghost = "at"
    elif text.lower().startswith("gh("):
        ghost = "gh"
    return Nucleus(label=label, mass=mass, ghost=ghost)


def _atom(node: ParserRuleContext, atoms: list[Atom]) -> Atom:
    coordinates = _children(node, "coordinate")
    if coordinates:
        x, y, z = map(_scalar, coordinates)
        position: Cartesian | ZMatrix = Cartesian(x=x, y=y, z=z)
    else:
        anchors: list[Anchor] = []
        for pair in _children(node, "anchor_pair"):
            coordinate = _child(pair, "coordinate")
            target = next(token.text for token in _tokens(pair) if token.text != ",")
            if target.isdecimal() and 1 <= int(target) <= len(atoms):
                reference: AtomReference | LabelReference = AtomReference(
                    atom_id=atoms[int(target) - 1].id
                )
            else:
                reference = LabelReference(label=target)
            anchors.append(Anchor(atom=reference, value=_scalar(coordinate)))
        position = ZMatrix(anchors=tuple(anchors))
    return Atom(
        id=f"a{len(atoms) + 1}",
        nucleus=_nucleus(_child(node, "nucleus")),
        coordinates=position,
    )


def _efp(node: ParserRuleContext) -> EFPFragment:
    points: list[NumericTriple] = []
    for triple in _children(node, "numeric_xyz"):
        x, y, z = _numbers(triple)
        points.append((x, y, z))
    return EFPFragment(
        name=_child(node, "native_word").getText(),
        points=tuple(points),
    )


def _molecule_record(
    result: ParseResult, node: ParserRuleContext, atoms: list[Atom]
) -> MoleculeRecord:
    name = rule_name(node)
    if name == "atom_line":
        return _atom(node, atoms)
    if name == "charge_multiplicity":
        charge, multiplicity = _numbers(node)
        return ElectronicState(charge=charge, multiplicity=multiplicity)
    if name == "geometry_variable":
        text = node.getText()
        lhs, rhs = text.split("=", 1)
        value: Scalar = (
            Number(value=rhs) if _NUMBER.fullmatch(rhs) else Variable(name=rhs)
        )
        return GeometryVariable(name=lhs, value=value)
    if name == "efp_fragment":
        return _efp(node)
    if name == "molecule_line":
        return _molecule_directive(result, node, atoms)
    raise ValueError("Unmapped molecule production: " + name)


def _molecule_directive(
    result: ParseResult, node: ParserRuleContext, atoms: list[Atom]
) -> MoleculeRecord:
    children = _children(node)
    first = next(_tokens(node)).text.casefold()
    if first in {"units", "unit"}:
        return Units(name=_child(node, "unit_name").getText())
    if first == "symmetry":
        return Symmetry(group=_child(node, "native_word").getText())
    if first.replace("_", "") in {"nocom", "noreorient"}:
        return FrameDirective(
            name="no_com" if "com" in first else "no_reorient",
        )
    if first == "--":
        return FragmentSeparator()
    if first in {"pubchem", "from_file"}:
        provider: Literal["from_file", "pubchem"] = (
            "pubchem" if first == "pubchem" else "from_file"
        )
        return GeometrySource(
            provider=provider,
            value=result.source_text(_child(node, "literal_line")),
        )
    if len(children) == 1:
        return _molecule_record(result, children[0], atoms)
    raise ValueError("Unmapped molecule directive: " + first)


def _molecule(result: ParseResult, node: ParserRuleContext) -> Molecule:
    body = _child(node, "molecule_body")
    text = _body(result, node)
    xyz = re.match(
        r"\s*(\d+)(?:[^\S\r\n]+([A-Za-z][\w.]*))?[^\S\r\n]*(?:\r\n|\r|\n)([^\r\n]*)",
        text,
    )
    records: list[MoleculeRecord] = []
    atoms: list[Atom] = []
    title_end: int | None = None
    if xyz is not None:
        records.append(XYZHeader(count=xyz[1], units=xyz[2], title=xyz[3]))
        brace = next(token for token in _tokens(node) if token.text == "{")
        title_end = result.source_span(brace)[1] + xyz.end()
    for record in _children(body):
        if title_end is not None and result.source_span(record)[0] < title_end:
            continue
        value = _molecule_record(result, record, atoms)
        records.append(value)
        if isinstance(value, Atom):
            atoms.append(value)
    return Molecule(name=_name(node, "molecule_name"), records=tuple(records))


def _option_value(result: ParseResult, node: ParserRuleContext) -> OptionValue:
    text = result.source_text(node)
    arrays = [
        child for child in contexts(node) if rule_name(child) == "set_option_array"
    ]
    if not arrays:
        reference = re.fullmatch(r"\$([A-Za-z]\w*)", text)
        return (
            OptionReference(name=reference[1])
            if reference
            else OptionExpression(source=text)
        )
    array = arrays[0]
    start, stop = result.source_span(array)
    own_start, own_stop = result.source_span(node)
    if (start, stop) != (own_start, own_stop):
        return OptionExpression(source=text)
    nested = [
        child
        for child in contexts(array)
        if child is not array
        and rule_name(child) == "set_option_array"
        and not any(
            rule_name(parent) == "set_option_array" and parent is not array
            for parent in _parents(child, array)
        )
    ]
    parts: list[OptionValue] = []
    cursor = start + 1
    for child in nested:
        first, last = result.source_span(child)
        if first > cursor:
            parts.append(OptionExpression(source=result.source[cursor:first]))
        parts.append(_option_value(result, child))
        cursor = last
    if cursor < stop - 1:
        parts.append(OptionExpression(source=result.source[cursor : stop - 1]))
    return OptionArray(parts=tuple(parts))


def _parents(
    node: ParserRuleContext, stop: ParserRuleContext
) -> Iterator[ParserRuleContext]:
    current = node
    while True:
        parent = current.parentCtx
        if isinstance(parent, ParserRuleContext) and parent is not stop:
            # PyCharm loses this isinstance guard when checking the yield type.
            # noinspection PyTypeChecker
            yield parent
            current = parent
        else:
            return


def _set(result: ParseResult, node: ParserRuleContext) -> SetOptions:
    modules = _children(node, "module_list")
    module_names = tuple(modules[0].getText().split(",")) if modules else ()
    assignments = _children(node, "option_assignment")
    inline = rule_name(node) == "set_command"
    if inline:
        assignments = [node]
    values = []
    for assignment in assignments:
        value_name = "inline_option_value" if inline else "set_option_value"
        values.append(
            OptionAssignment(
                key=_child(assignment, "option_key").getText(),
                value=_option_value(result, _child(assignment, value_name)),
            )
        )
    return SetOptions(
        modules=module_names,
        assignments=tuple(values),
        style="inline" if inline else "block",
    )


def _basis(result: ParseResult, node: ParserRuleContext) -> Basis:
    records: list[BasisRecord] = []
    for line in _children(node, "basis_line"):
        field = _children(line)[0]
        match rule_name(field):
            case "basis_assignment":
                text = result.source_text(_child(field, "basis_name"))
                match text.split():
                    case [target, basis]:
                        records.append(BasisAssignment(target=target, basis=basis))
                    case _:
                        records.append(BasisAssignment(basis=text))
            case "basis_label":
                records.append(BasisLabel(name=_child(field, "basis_name").getText()))
            case "basis_record":
                records.append(BasisData(text=result.source_text(field)))
            case _:
                raise ValueError("Unmapped basis production: " + rule_name(field))
    return Basis(
        role=next(_tokens(node)).text.lower(),
        name=_name(node),
        records=tuple(records),
    )


def _external(result: ParseResult, node: ParserRuleContext) -> External:
    records: list[ExternalRecord] = []
    for line in _children(node, "external_line"):
        first = next(_tokens(line)).text.lower()
        if first in {"unit", "units"}:
            records.append(Units(name=_child(line, "unit_name").getText()))
        elif first == "--":
            records.append(FragmentSeparator())
        elif _children(line, "external_basis_line"):
            basis = _child(line, "external_basis_line")
            key = _child(basis, "external_basis_key")
            pieces = _children(basis, "literal_piece")
            start = result.source_span(pieces[0])[0]
            stop = result.source_span(pieces[-1])[1]
            role: Literal["basis", "df_basis_scf"] = (
                "basis" if key.getText().lower() == "basis" else "df_basis_scf"
            )
            records.append(ExternalBasis(role=role, value=result.source[start:stop]))
        elif _children(line, "nucleus"):
            nucleus = _child(line, "nucleus")
            coords = [
                Number(value=child.getText())
                for child in terminals(line)
                if _NUMBER.fullmatch(child.getText())
            ]
            x, y, z = coords
            records.append(ExternalAtom(nucleus=_nucleus(nucleus), position=(x, y, z)))
        else:
            charge, x, y, z = _numbers(line)
            records.append(PointCharge(charge=charge, position=(x, y, z)))
    return External(name=_name(node), records=tuple(records))


def _pcm(result: ParseResult, node: ParserRuleContext) -> PCM:
    return PCM(name=_name(node), body=_body(result, node))


def _cfour(result: ParseResult, node: ParserRuleContext) -> CFour:
    return CFour(name=_name(node), body=_body(result, node))


def _memory(result: ParseResult, node: ParserRuleContext) -> Memory:
    match = re.fullmatch(
        r"(.*?)memory\s+([\d.]+)\s*([a-z]+)", result.source_text(node), re.IGNORECASE
    )
    if match is None:
        raise ValueError("Unmapped memory directive")
    return Memory(
        prefix=match[1],
        amount=Number(value=match[2]),
        units=match[3],
    )


BUILDERS: dict[str, Callable[[ParseResult, ParserRuleContext], NativeNode]] = {
    "molecule_block": _molecule,
    "set_command": _set,
    "set_block": _set,
    "basis_block": _basis,
    "external_block": _external,
    "pcm_block": _pcm,
    "cfour_block": _cfour,
    "memory_line": _memory,
}


def _statement(result: ParseResult, node: ParserRuleContext) -> Node:
    start, stop = result.source_span(node)
    source = result.source[start:stop].rstrip("\r\n")
    native = [child for child in contexts(node) if rule_name(child) in BUILDERS]
    if not native:
        return Python(source=source)
    if len(native) == 1 and result.source_span(native[0])[0] == start:
        end = result.source_span(native[0])[1]
        if not result.source[end:stop].strip():
            return BUILDERS[rule_name(native[0])](result, native[0])
    parts: list[TemplatePart] = []
    cursor = start
    for child in native:
        first, last = result.source_span(child)
        if first > cursor:
            parts.append(Python(source=result.source[cursor:first]))
        parts.append(BUILDERS[rule_name(child)](result, child))
        cursor = last
    if cursor < start + len(source):
        parts.append(Python(source=result.source[cursor : start + len(source)]))
    return PythonTemplate(parts=tuple(parts))


def read_job(source: str | ParseResult) -> Job:
    """Construct first-class native nodes without reading or executing job data.

    Args:
        source: Input text or an existing ANTLR parse result.

    Returns:
        JSON-compatible job with Python-only source and explicit native children.

    Raises:
        JobSyntaxError: Native or contextual Python validation rejects the input.
        ValueError: A native production has no explicit model conversion.
    """  # noqa: DOC502 - Native conversion helpers also raise ValueError.
    result = parse(source) if isinstance(source, str) else source
    if result.diagnostics:
        raise JobSyntaxError(result.diagnostics)
    statements = _children(result.tree, "statements")
    if not statements:
        return (
            Job(body=(Python(source=result.source),))
            if result.source.strip()
            else Job()
        )
    body: list[Node] = []
    cursor = result.input_span[0] if result.input_span is not None else 0
    for statement in _children(statements[0], "statement"):
        start, stop = result.source_span(statement)
        gap = result.source[cursor:start]
        if gap.strip():
            body.append(Python(source=gap.rstrip("\r\n")))
        body.append(_statement(result, statement))
        cursor = stop
    end = result.input_span[1] if result.input_span is not None else len(result.source)
    if result.source[cursor:end].strip():
        body.append(Python(source=result.source[cursor:end].rstrip("\r\n")))
    return Job(body=tuple(body))
