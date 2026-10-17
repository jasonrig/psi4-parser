"""Public interface used from the generated parser."""

from typing import ClassVar, Literal

from antlr4 import Parser, ParserRuleContext

class PsithonParser(Parser):
    ruleNames: ClassVar[list[str]]
    python_source: str | None
    native_payloads: tuple[
        tuple[Literal["pcm", "from_file", "anonymous_basis", "external"], str], ...
    ]
    def file_input(self) -> ParserRuleContext: ...
    # Development reference checks inspect the grammar-owned projection.
    def psithon_project(
        self, root: ParserRuleContext, source: str, *, for_ast: bool = False
    ) -> tuple[str, list[int]]: ...
