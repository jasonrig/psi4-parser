"""Describe internal coordinates and OptKing constraints using stable atom IDs."""

from typing import Annotated, Literal

from pydantic import Field, model_validator

from psi4_parser.builder._model import Angle, Length, Model

type CoordinateKind = Literal[
    "distance", "angle", "dihedral", "out_of_plane", "cartesian"
]


class Coordinate(Model):
    """A distance, angle, torsion, or atom position to constrain."""

    kind: CoordinateKind = Field(
        description=(
            "Distance, bond angle, torsion, out-of-plane angle, or x/y/z position."
        )
    )
    atoms: tuple[str, ...] = Field(
        min_length=1,
        max_length=4,
        description=(
            "Atom IDs in coordinate order: 2 for distance, 3 for angle, 4 for "
            "torsion or out-of-plane, 1 for x/y/z."
        ),
    )
    axes: str = Field(
        default="",
        pattern="^[xyz]*$",
        description=(
            "Axes to constrain, such as x or xyz; use an empty string for "
            "distances and angles."
        ),
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
    """Hold a coordinate at its starting value during geometry optimization."""

    kind: Literal["frozen"] = Field(
        default="frozen", description="Selects a coordinate held at its starting value."
    )
    coordinate: Coordinate = Field(
        description="Coordinate to hold at its value at the start of optimization."
    )


class Bounded(Model):
    """Keep a coordinate within a chosen range during geometry optimization."""

    kind: Literal["bounded"] = Field(
        default="bounded", description="Selects a coordinate restricted to a range."
    )
    coordinate: Coordinate = Field(
        description="Coordinate whose value must remain within the bounds."
    )
    lower: Annotated[
        Length | Angle,
        Field(
            discriminator="kind",
            json_schema_extra={"required": ["kind"]},
            description=(
                "Minimum value with length or angle units matching the coordinate."
            ),
        ),
    ] = Field(
        description=(
            "Minimum value with length or angle units matching the coordinate."
        )
    )
    upper: Annotated[
        Length | Angle,
        Field(
            discriminator="kind",
            json_schema_extra={"required": ["kind"]},
            description=(
                "Maximum value, greater than lower, with matching length or angle "
                "units."
            ),
        ),
    ] = Field(
        description=(
            "Maximum value, greater than lower, with matching length or angle units."
        )
    )

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
    Field(
        discriminator="kind",
        json_schema_extra={"required": ["kind"]},
        description=(
            "A coordinate held fixed or restricted to a range during optimization."
        ),
    ),
]


def distance(a: str, b: str) -> Coordinate:
    """Select a distance between two distinct atom IDs for an optimization constraint.

    Returns:
        A coordinate for freeze(), bound(), or a requested Z-matrix parameter;
        this specifies the atoms rather than measuring their separation.
    """
    return Coordinate(kind="distance", atoms=(a, b))


def angle(a: str, b: str, c: str) -> Coordinate:
    """Select the bond angle a-b-c, with its vertex at b, by distinct atom IDs.

    Returns:
        A coordinate for freeze(), bound(), or a requested Z-matrix parameter.
    """
    return Coordinate(kind="angle", atoms=(a, b, c))


def dihedral(a: str, b: str, c: str, d: str) -> Coordinate:
    """Select the signed torsion a-b-c-d around b-c by distinct atom IDs.

    Returns:
        A coordinate for freeze(), bound(), or a requested Z-matrix parameter.
        The torsion compares planes abc and bcd.
    """
    return Coordinate(kind="dihedral", atoms=(a, b, c, d))


def out_of_plane(a: str, b: str, c: str, d: str) -> Coordinate:
    """Select OptKing's signed out-of-plane angle a-b-c-d by atom IDs.

    The angle is between the b-a bond and the plane through c, b, and d;
    b is the vertex. Keep the supplied atom order for signed bounds.

    Returns:
        A four-atom coordinate for freeze() or bound().
    """
    return Coordinate(kind="out_of_plane", atoms=(a, b, c, d))


def cartesian(atom: str, axes: str = "xyz") -> Coordinate:
    """Select Cartesian position components of one atom for a constraint.

    Args:
        atom: Stable ID of the atom to constrain.
        axes: Distinct letters from xyz, such as x or yz. Bounds require one axis;
            freezing accepts multiple axes.

    Returns:
        A coordinate for freeze() or bound(). Use Cartesian molecular geometry;
        Cartesian bounds also require fixed_com=True and fixed_orientation=True.
    """
    return Coordinate(kind="cartesian", atoms=(atom,), axes=axes)


def freeze(coordinate: Coordinate) -> Frozen:
    """Hold a coordinate at its starting value during an OptKing optimization.

    Args:
        coordinate: Atom IDs and coordinate type from distance(), angle(),
            dihedral(), out_of_plane(), or cartesian().

    Returns:
        A constraint to pass in ``optimize(..., constraints=(constraint,))``.
        To target a particular value, edit the geometry first and then freeze it.
    """
    return Frozen(coordinate=coordinate)


def bound(
    coordinate: Coordinate, lower: Length | Angle, upper: Length | Angle
) -> Bounded:
    """Restrict an OptKing optimization coordinate to a range.

    Args:
        coordinate: Distance, angle, torsion, out-of-plane angle, or one Cartesian
            axis selected by atom IDs.
        lower: Minimum value from angstrom()/bohr() for a length, or
            degrees()/radians() for an angle.
        upper: Maximum value, strictly greater than lower. Units may differ
            from lower but must describe the same dimension.

    Returns:
        A constraint to pass in ``optimize(..., constraints=(constraint,))``.
        Cartesian bounds require Cartesian geometry with fixed_com=True and
        fixed_orientation=True.
    """
    return Bounded(coordinate=coordinate, lower=lower, upper=upper)
