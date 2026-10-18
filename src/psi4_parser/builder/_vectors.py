"""Compute three-dimensional geometry with NumPy and explicit degeneracy checks."""

import numpy as np

type Vector = tuple[float, float, float]
type VectorArray = np.ndarray[tuple[int], np.dtype[np.float64]]
type MatrixArray = np.ndarray[tuple[int, int], np.dtype[np.float64]]


VECTOR_EPSILON = 1e-12
PERPENDICULAR_AXIS_LIMIT = 0.9
PSI4_COLLINEARITY_LIMIT = 1e-5
BEND_REFERENCES = 2


class DegenerateGeometryError(ValueError):
    """Report a zero vector or an undefined internal coordinate."""


def vector_tuple(values: VectorArray) -> Vector:
    """Return three Python floats for immutable coordinate records."""
    return float(values.item(0)), float(values.item(1)), float(values.item(2))


def add(a: Vector, b: Vector) -> Vector:
    """Return vector addition."""
    return vector_tuple(np.add(a, b, dtype=np.float64))


def scale(a: Vector, factor: float) -> Vector:
    """Return a scaled vector."""
    return vector_tuple(np.multiply(a, factor, dtype=np.float64))


def sub(a: Vector, b: Vector) -> Vector:
    """Return the displacement from b to a."""
    return vector_tuple(np.subtract(a, b, dtype=np.float64))


def dot(a: Vector, b: Vector) -> float:
    """Return a scalar product."""
    left: VectorArray = np.asarray(a, dtype=np.float64)
    right: VectorArray = np.asarray(b, dtype=np.float64)
    return float(np.dot(left, right))


def cross(a: Vector, b: Vector) -> Vector:
    """Return a right-handed vector product."""
    return vector_tuple(
        np.linalg.cross(
            np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
        )
    )


def norm(a: Vector) -> float:
    """Return the Euclidean vector length."""
    return float(np.linalg.vector_norm(np.asarray(a, dtype=np.float64)))


def unit(a: Vector) -> Vector:
    """Return a unit vector, rejecting coincident reference points.

    Raises:
        DegenerateGeometryError: The vector has no defined direction.
    """
    size = norm(a)
    if size < VECTOR_EPSILON:
        raise DegenerateGeometryError("Coincident or collinear reference points")
    return vector_tuple(np.divide(a, size, dtype=np.float64))


def perpendicular(a: Vector) -> Vector:
    """Return a deterministic perpendicular unit vector."""
    axis: Vector = (
        (1.0, 0.0, 0.0)
        if abs(unit(a)[0]) < PERPENDICULAR_AXIS_LIMIT
        else (0.0, 1.0, 0.0)
    )
    return unit(cross(axis, a))


def separation(a: Vector, b: Vector) -> float:
    """Return a distance in the positions' length unit."""
    return norm(sub(a, b))


def bend(a: Vector, b: Vector, c: Vector) -> float:
    """Return the angle in degrees with b as its vertex."""
    cosine = dot(unit(sub(a, b)), unit(sub(c, b)))
    clipped = np.clip(np.float64(cosine), -1.0, 1.0)
    angle = np.arccos(clipped, dtype=np.float64)
    return float(np.rad2deg(angle, dtype=np.float64))


def torsion(a: Vector, b: Vector, c: Vector, d: Vector) -> float:
    """Return Psi4's signed dihedral in degrees.

    Raises:
        DegenerateGeometryError: Reference atoms are coincident or collinear.
    """
    z = unit(sub(b, c))
    y = unit(cross(unit(sub(c, d)), z))
    x = cross(y, z)
    direction = unit(sub(a, b))
    if norm(cross(direction, z)) < VECTOR_EPSILON:
        raise DegenerateGeometryError(
            "Requested dihedral is undefined for collinear atoms"
        )
    angle = np.arctan2(dot(direction, y), dot(direction, x), dtype=np.float64)
    return float(np.rad2deg(angle, dtype=np.float64))


def rotated(point: Vector, axis: Vector, angle: float, origin: Vector) -> Vector:
    """Return a point rotated around an axis by an angle in radians."""
    k: VectorArray = np.asarray(unit(axis), dtype=np.float64)
    center = np.asarray(origin, dtype=np.float64)
    displacement: VectorArray = np.asarray(point, dtype=np.float64) - center
    cosine = float(np.cos(angle, dtype=np.float64))
    sine = float(np.sin(angle, dtype=np.float64))
    return vector_tuple(
        center
        + displacement * cosine
        + np.linalg.cross(k, displacement) * sine
        + k * np.dot(k, displacement) * (1.0 - cosine)
    )


def placed(anchors: tuple[Vector, ...], values: tuple[float, ...]) -> Vector:
    """Return Psi4's canonical Z-matrix placement in angstroms."""
    if not anchors:
        return 0.0, 0.0, 0.0
    b = anchors[0]
    if len(anchors) == 1:
        return 0.0, 0.0, values[0]
    z = unit(sub(b, anchors[1]))
    angular_values: VectorArray = np.asarray(values[1:], dtype=np.float64)
    angles: VectorArray = np.deg2rad(angular_values, dtype=np.float64)
    sines: VectorArray = np.sin(angles, dtype=np.float64)
    cosines: VectorArray = np.cos(angles, dtype=np.float64)
    sine, cosine = float(sines.item(0)), float(cosines.item(0))
    if len(anchors) == BEND_REFERENCES:
        y = (
            unit(cross((1.0, 0.0, 0.0), z))
            if abs(1 - abs(z[0])) >= PSI4_COLLINEARITY_LIMIT
            else unit(cross(unit(cross((0.0, 1.0, 0.0), z)), z))
        )
        direction = (
            np.asarray(y, dtype=np.float64) * sine
            - np.asarray(z, dtype=np.float64) * cosine
        )
    else:
        y = unit(cross(unit(sub(anchors[1], anchors[2])), z))
        x = cross(y, z)
        coefficients = np.asarray(
            (
                sine * float(cosines.item(1)),
                sine * float(sines.item(1)),
                -cosine,
            ),
            dtype=np.float64,
        )
        direction = coefficients @ np.asarray((x, y, z), dtype=np.float64)
    return vector_tuple(np.asarray(b, dtype=np.float64) + values[0] * direction)


def alignment_error(reference: tuple[Vector, ...], target: tuple[Vector, ...]) -> float:
    """Return the maximum residual after least-squares proper rigid alignment.

    Raises:
        ValueError: The coordinate sets do not contain the same number of sites.
    """
    if len(reference) != len(target):
        raise ValueError("Alignment requires the same number of sites")
    if not reference:
        return 0.0
    a: MatrixArray = np.asarray(reference, dtype=np.float64)
    b: MatrixArray = np.asarray(target, dtype=np.float64)
    a = a - np.mean(a, axis=0)
    b = b - np.mean(b, axis=0)
    left: MatrixArray
    right: MatrixArray
    left, _singular_values, right = np.linalg.svd(a.T @ b)
    rotation: MatrixArray = left @ right
    if np.linalg.det(rotation) < 0:
        left[:, -1] *= -1.0
        rotation = left @ right
    residuals = np.linalg.vector_norm(a @ rotation - b, axis=1)
    return float(np.max(residuals))
