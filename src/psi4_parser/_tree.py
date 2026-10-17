"""Share traversal of the generated ANTLR rule contexts."""

from collections.abc import Iterator

from antlr4 import ParserRuleContext

from psi4_parser._generated.PsithonParser import PsithonParser


def contexts(root: ParserRuleContext) -> Iterator[ParserRuleContext]:
    """Visit contexts in source order without depending on generated subclasses.

    Args:
        root: Root of the concrete syntax tree.

    Yields:
        The root and each descendant rule context.
    """
    pending = [root]
    while pending:
        node = pending.pop()
        yield node
        children = [
            child
            for child in node.getChildren()
            if isinstance(child, ParserRuleContext)
        ]
        pending.extend(reversed(children))


def rule_name(node: ParserRuleContext) -> str:
    """Return a context's name from the generated grammar vocabulary.

    Args:
        node: A Psithon or imported Python context.

    Returns:
        The grammar production name.
    """
    return PsithonParser.ruleNames[node.getRuleIndex()]
