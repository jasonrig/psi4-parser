"""Check the shared diagnostic contract of independently catchable errors."""

import pytest

from psi4_parser.api import Diagnostic
from psi4_parser.ast import InvalidInputError
from psi4_parser.job import JobSyntaxError


@pytest.mark.parametrize("error_type", [InvalidInputError, JobSyntaxError])
def test_input_errors_retain_all_diagnostics_and_describe_the_first(
    error_type: type[InvalidInputError | JobSyntaxError],
) -> None:
    """Retain the complete diagnostic tuple and its established message spelling.

    Args:
        error_type: Public AST or job-input exception type.
    """
    diagnostics = (
        Diagnostic(line=3, column=2, message="invalid statement"),
        Diagnostic(line=4, column=0, message="another error"),
    )
    error = error_type(diagnostics)
    assert error.diagnostics is diagnostics
    assert str(error) == "3:2: invalid statement"
    assert isinstance(error, ValueError)
