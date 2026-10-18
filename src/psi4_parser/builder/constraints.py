"""Describe internal coordinates and OptKing constraints using stable atom IDs."""

from typing import Annotated, Literal

from pydantic import Field, model_validator

from psi4_parser.builder._model import Angle, Length, Model

type CoordinateKind = Literal[
    "distance", "angle", "dihedral", "out_of_plane", "cartesian"
]


class Coordinate(Model):
    """Identify one internal or Cartesian coordinate by stable atom IDs."""

    kind: CoordinateKind = Field(description="Coordinate interpreted by the optimizer.")
    atoms: tuple[str, ...] = Field(
        min_length=1, max_length=4, description="Ordered stable atom IDs."
    )
    axes: str = Field(
        default="",
        pattern="^[xyz]*$",
        description="Cartesian axes, or empty for an internal coordinate.",
    )

    @model_validator(mode="after")
    def check_shape(self) -> Coordinate:
        """Return the coordinate after checking its atom count and axes.

        Raises:
            ValueError: Atom counts or axes do not match the coordinate.
        """
        count = {
            "distance": 2,
            "angle": 3,
            "dihedral": 4,
            "out_of_plane": 4,
            "cartesian": 1,
        }[self.kind]
        if len(self.atoms) != count or len(set(self.atoms)) != count:
            raise ValueError(
                "Coordinate requires the appropriate number of distinct atoms"
            )
        if self.kind == "cartesian":
            if not self.axes or len(set(self.axes)) != len(self.axes):
                raise ValueError("Cartesian coordinates require distinct axes")
        elif self.axes:
            raise ValueError("Axes apply only to Cartesian coordinates")
        return self


class Frozen(Model):
    """Keep the initial value of a coordinate during optimization."""

    kind: Literal["frozen"] = Field(
        default="frozen", description="Frozen coordinate constraint."
    )
    coordinate: Coordinate = Field(description="Coordinate to freeze.")


class Bounded(Model):
    """Restrict an OptKing coordinate to a finite, dimensioned interval."""

    kind: Literal["bounded"] = Field(
        default="bounded", description="Ranged coordinate constraint."
    )
    coordinate: Coordinate = Field(description="Coordinate to bound.")
    lower: Annotated[
        Length | Angle,
        Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
    ] = Field(description="Lower bound with units.")
    upper: Annotated[
        Length | Angle,
        Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
    ] = Field(description="Upper bound with units.")

    @model_validator(mode="after")
    def check_bounds(self) -> Bounded:
        """Return the constraint after checking interval order and dimensions.

        Raises:
            ValueError: Bounds have incompatible dimensions or order.
        """
        length = self.coordinate.kind in {"distance", "cartesian"}
        if length:
            if not isinstance(self.lower, Length) or not isinstance(self.upper, Length):
                raise ValueError("This coordinate requires length bounds")
            low, high = self.lower.angstroms, self.upper.angstroms
        else:
            if not isinstance(self.lower, Angle) or not isinstance(self.upper, Angle):
                raise ValueError("This coordinate requires angular bounds")
            low, high = self.lower.degrees, self.upper.degrees
        if low >= high:
            raise ValueError(
                "Lower bound must be below upper bound; freeze exact targets"
            )
        if self.coordinate.kind == "cartesian" and len(self.coordinate.axes) != 1:
            raise ValueError("Ranged Cartesian constraints require one axis")
        return self


type Constraint = Annotated[
    Frozen | Bounded,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


def distance(a: str, b: str) -> Coordinate:
    """Return the distance coordinate between two atoms."""
    return Coordinate(kind="distance", atoms=(a, b))


def angle(a: str, b: str, c: str) -> Coordinate:
    """Return the angle coordinate with its vertex at the second atom."""
    return Coordinate(kind="angle", atoms=(a, b, c))


def dihedral(a: str, b: str, c: str, d: str) -> Coordinate:
    """Return the signed torsion coordinate around the central bond."""
    return Coordinate(kind="dihedral", atoms=(a, b, c, d))


def out_of_plane(a: str, b: str, c: str, d: str) -> Coordinate:
    """Return an OptKing out-of-plane coordinate in the supplied atom order."""
    return Coordinate(kind="out_of_plane", atoms=(a, b, c, d))


def cartesian(atom: str, axes: str = "xyz") -> Coordinate:
    """Return one or more Cartesian components of an atom."""
    return Coordinate(kind="cartesian", atoms=(atom,), axes=axes)


def freeze(coordinate: Coordinate) -> Frozen:
    """Return a constraint that freezes the starting coordinate value."""
    return Frozen(coordinate=coordinate)


def bound(
    coordinate: Coordinate, lower: Length | Angle, upper: Length | Angle
) -> Bounded:
    """Return a constraint that restricts a coordinate to an interval."""
    return Bounded(coordinate=coordinate, lower=lower, upper=upper)
