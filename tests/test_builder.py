"""Exercise immutable composition, serialization, and component annotations."""

import pytest
from pydantic import ValidationError

from psi4_parser.builder import (
    PCM,
    CFour,
    JobSpec,
    Memory,
    Python,
    compose,
    energy,
    options,
    pipe,
)


def test_composition_and_pipeline_are_equivalent() -> None:
    """Concatenate components without implicit declarations or settings merges."""
    a = options(basis="sto-3g")
    b = energy("unusual-method", assign="result", novel_argument=True)
    expected = compose(a, b)
    assert a + b == expected
    assert JobSpec() | a | b == expected
    assert pipe(JobSpec(), a, b) == expected
    assert compose(JobSpec(), compose(a), b) == expected
    assert (a + JobSpec()) + b == a + (JobSpec() + b)
    assert compose() == JobSpec()
    assert a.comments == ()


def test_comments_are_immutable_and_serializable() -> None:
    """Retain multiline annotations on their owning component in JSON."""
    component = Memory(amount=1.0)
    annotated = component.with_comment("First line\n\nA researcher's # note")
    job = compose(annotated, Python(source="x = 1", provides=("x",)))
    assert component.comments == ()
    assert annotated.comments[0].text == "First line\n\nA researcher's # note"
    assert JobSpec.model_validate_json(job.model_dump_json()) == job
    assert "schema_version" not in job.model_dump_json()
    with pytest.raises(ValidationError, match="frozen"):
        annotated.amount = 2.0  # type: ignore[misc]  # Verify runtime freezing as well as static typing.


@pytest.mark.parametrize("model", [PCM, CFour])
def test_solver_components_revalidate_copied_values(model: type[PCM | CFour]) -> None:
    """Check solver text again when a copied component is composed into a job.

    Args:
        model: Solver component whose instance-validation policy must be retained.
    """
    invalid_values: dict[str, int] = {"body": 42}
    unchecked = model(body="Solver text").model_copy(update=invalid_values)

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        compose(unchecked)
