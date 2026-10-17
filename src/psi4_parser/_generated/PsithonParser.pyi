"""Public interface used from the generated parser."""

from antlr4 import Parser, ParserRuleContext

class PsithonParser(Parser):
    def file_input(self) -> ParserRuleContext: ...
    # Development reference checks inspect the grammar-owned projection.
    def psithon_project(
        self, root: ParserRuleContext, source: str
    ) -> tuple[str, list[int]]: ...
