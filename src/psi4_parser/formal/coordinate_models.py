"""State required coordinate values independently from prepared geometries."""

from math import isfinite
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from psi4_parser.builder import Angle, Coordinate, Length
from psi4_parser.formal._record import Record

type CoordinateQuantity = Annotated[
    Length | Angle,
    Field(discriminator="kind", json_schema_extra={"required": ["kind"]}),
]


def coordinate_number(quantity: Length | Angle) -> float:
    """Return a coordinate quantity in angstroms or degrees, according to dimension."""
    return quantity.angstroms if isinstance(quantity, Length) else quantity.degrees


class _CoordinateRequirement(Record):
    geometry: str = Field(
        min_length=1,
        description="Molecular input, optimization, or subsystem geometry identity.",
    )
    coordinate: Coordinate = Field(
        description="Ordered stable atom IDs; Cartesian requirements select one axis."
    )
    tolerance: CoordinateQuantity = Field(
        description="Nonnegative absolute tolerance, with the coordinate's dimension."
    )

    def _check_quantities(self, *values: Length | Angle) -> None:
        if any(
            not isfinite(coordinate_number(value))
            for value in (*values, self.tolerance)
        ):
            raise ValueError("Converted coordinate quantities must be finite")
        length = self.coordinate.kind in {"distance", "cartesian"}
        if any(
            isinstance(value, Length) != length for value in (*values, self.tolerance)
        ):
            raise ValueError(
                "Coordinate values and tolerance must have matching dimensions"
            )
        if coordinate_number(self.tolerance) < 0:
            raise ValueError("Coordinate tolerance must be nonnegative")
        if self.coordinate.kind == "cartesian" and len(self.coordinate.axes) != 1:
            raise ValueError("A scalar Cartesian requirement needs exactly one axis")


class CoordinateValue(_CoordinateRequirement):
    """Require a coordinate to equal a target within an explicit absolute tolerance.

    Dihedrals compare modulo 360 degrees. Other coordinates use linear distance
    from the target. This describes input or constrained future geometry, not a
    numerical check to perform after a calculation.
    """

    kind: Literal["coordinate_value"] = Field(
        default="coordinate_value", description="Require one coordinate target."
    )
    value: CoordinateQuantity = Field(
        description="Target in length or angle units appropriate to the coordinate."
    )

    @model_validator(mode="after")
    def check_dimensions(self) -> Self:
        """Return a target after checking dimension and tolerance.

        Raises:
            ValueError: Dimensions, tolerance, or selected axes are incompatible.
        """  # noqa: DOC502 - _check_quantities validates the shared coordinate contract.
        self._check_quantities(self.value)
        return self


class CoordinateRange(_CoordinateRequirement):
    """Require a coordinate to remain within a closed interval, expanded by tolerance.

    A dihedral interval describes the arc from lower to upper in increasing
    degrees. For example, 170 to 190 crosses the signed-angle branch cut.
    """

    kind: Literal["coordinate_range"] = Field(
        default="coordinate_range", description="Require a closed coordinate interval."
    )
    lower: CoordinateQuantity = Field(description="Inclusive lower coordinate bound.")
    upper: CoordinateQuantity = Field(description="Inclusive upper coordinate bound.")

    @model_validator(mode="after")
    def check_dimensions(self) -> Self:
        """Return an interval after checking dimensions and increasing bounds.

        Raises:
            ValueError: Dimensions, tolerance, axes, or interval order are invalid.
        """
        self._check_quantities(self.lower, self.upper)
        if coordinate_number(self.lower) >= coordinate_number(self.upper):
            raise ValueError("Coordinate lower bound must be below upper bound")
        return self


type CoordinateRequirement = CoordinateValue | CoordinateRange
