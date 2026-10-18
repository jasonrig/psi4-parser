"""Check rigid alignment, reflection rejection, and axis rotation conventions."""

import numpy as np
import pytest

# noinspection PyProtectedMember
from psi4_parser.builder._vectors import Vector, alignment_error, rotated


@pytest.mark.parametrize(
    ("reference", "target"),
    [
        pytest.param((), (), id="empty"),
        pytest.param(((1.0, 2.0, 3.0),), ((8.0, -1.0, 4.0),), id="single-atom"),
        pytest.param(
            ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
            ((5.0, -2.0, 3.0), (5.0, -2.0, 3.0)),
            id="coincident",
        ),
        pytest.param(
            ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)),
            ((5.0, -2.0, 3.0), (5.0, -1.0, 3.0), (5.0, 0.0, 3.0)),
            id="collinear",
        ),
        pytest.param(
            ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 2.0, 0.0)),
            ((5.0, -2.0, 3.0), (5.0, -1.0, 3.0), (5.0, -2.0, 5.0)),
            id="planar",
        ),
        pytest.param(
            ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 3.0)),
            ((5.0, -2.0, 3.0), (5.0, -1.0, 3.0), (5.0, -2.0, 5.0), (8.0, -2.0, 3.0)),
            id="three-dimensional",
        ),
    ],
)
def test_proper_alignment_handles_coordinate_rank(
    reference: tuple[Vector, ...], target: tuple[Vector, ...]
) -> None:
    """Align corresponding atoms through translation and a proper rotation.

    Args:
        reference: Coordinates spanning zero to three dimensions.
        target: The same sites after a known rigid transformation.
    """
    assert alignment_error(reference, target) == pytest.approx(0.0, abs=1e-12)


def test_alignment_rejects_a_reflected_tetrahedron() -> None:
    """Keep a finite residual when only a reflection can match ordered sites."""
    reference: tuple[Vector, ...] = (
        (1.0, 1.0, 1.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, -1.0),
        (1.0, -1.0, -1.0),
    )
    reflected: tuple[Vector, ...] = (
        (-1.0, 1.0, 1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, -1.0),
        (-1.0, -1.0, -1.0),
    )
    assert alignment_error(reference, reflected) > 1.0


def test_rotation_keeps_its_origin_and_normalizes_the_axis() -> None:
    """Rotate a point by a quarter turn about an offset, non-unit axis."""
    actual = rotated((3.0, -1.0, 4.0), (0.0, 0.0, 7.0), np.pi / 2, (2.0, -1.0, 4.0))
    assert actual == pytest.approx((2.0, 0.0, 4.0), abs=1e-12)


@pytest.mark.parametrize("target", [(), ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0))])
def test_alignment_rejects_different_site_counts(target: tuple[Vector, ...]) -> None:
    """Reject incompatible shapes before NumPy can broadcast coordinates.

    Args:
        target: Coordinates with a different site count from the reference.
    """
    with pytest.raises(ValueError, match="same number of sites"):
        alignment_error(((0.0, 0.0, 0.0),), target)
