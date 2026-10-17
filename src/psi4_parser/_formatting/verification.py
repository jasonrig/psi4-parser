"""Compare native molecule fields while keeping Python literal comparison strict."""

import re

from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from psi4_parser._tree import contexts, rule_name
from psi4_parser.api import ParseResult


def restore_molecule_layout(before: ParseResult, after: ParseResult) -> str:
    """Restore only CST-verified molecule bodies for lowered-Python comparison.

    Call this only after significant CST equality has been established. That
    equality retains every geometry token, field rule and physical native newline.
    Additionally retain raw literal lines (XYZ titles and reader references),
    complete nucleus labels and unit spellings: their interior spacing is data.
    Replacing these verified bodies avoids normalizing arbitrary Python strings
    or relying on names such as geometry() to identify compiler-generated calls.

    Args:
        before: Valid original input.
        after: Valid candidate with an identical significant CST.

    Returns:
        Candidate source with the original native molecule body spelling restored.

    Raises:
        ValueError: A molecule's protected literal data differs.
    """
    original = [
        node for node in contexts(before.tree) if rule_name(node) == "molecule_block"
    ]
    candidate = [
        node for node in contexts(after.tree) if rule_name(node) == "molecule_block"
    ]
    source = after.source
    for left, right in reversed(list(zip(original, candidate, strict=True))):
        if _literals(before, left) != _literals(after, right):
            raise ValueError("Formatting changed literal molecule data")
        first, last = _body_span(before, left)
        start, stop = _body_span(after, right)
        source = source[:start] + before.source[first:last] + source[stop:]
    return source


def _literals(result: ParseResult, block: ParserRuleContext) -> tuple[str, ...]:
    body_end = _body_span(result, block)[1]
    title = xyz_title_span(result, block)
    literals = [result.source[title[0] : title[1]]] if title is not None else []
    for node in contexts(block):
        name = rule_name(node)
        if name == "literal_line":
            start, stop = result.source_span(node)
            while stop < body_end and result.source[stop] not in "\r\n":
                stop += 1
            literals.append(result.source[start:stop])
        elif name in {"nucleus", "unit_name"}:
            literals.append(result.source_text(node))
    return tuple(literals)


def _body_span(result: ParseResult, block: ParserRuleContext) -> tuple[int, int]:
    braces = [
        child.getSymbol()
        for child in block.getChildren()
        if isinstance(child, TerminalNodeImpl) and child.getText() in {"{", "}"}
    ]
    return result.source_span(braces[0])[1], result.source_span(braces[-1])[0]


def xyz_title_span(
    result: ParseResult, block: ParserRuleContext
) -> tuple[int, int] | None:
    """Locate the literal second XYZ record, including ambiguous CST derivations.

    XYZ headers can also match the permissive atom-line grammar. Detect the
    count record before applying atom styles so a parseable title stays literal.

    Args:
        result: Owning source and CST.
        block: Native molecule block.

    Returns:
        Exact title-line interval, or None for a non-XYZ molecule.
    """
    start, stop = _body_span(result, block)
    match = re.match(
        r"\s*\d+(?:[^\S\r\n]+[A-Za-z][\w.]*)?[^\S\r\n]*(?:\r\n|\r|\n)([^\r\n]*)",
        result.source[start:stop],
    )
    return (start + match.start(1), start + match.end(1)) if match is not None else None
