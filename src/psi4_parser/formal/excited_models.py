"""Declare response equations and the finite excited-root set to construct."""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from psi4_parser.formal._record import Record

type RootCount = Annotated[int, Field(ge=0)]


class TDSCFAnalysis(Record):
    """Request TD-SCF roots using RPA or the Tamm--Dancoff approximation.

    An integer requests the native total-root allocation across irreps. A tuple
    supplies counts in native computational-irrep order and needs an explicit
    molecular point group. Product root numbers refer to energy order within
    this requested set, without claiming physical state tracking.
    """

    states: (
        Annotated[int, Field(ge=1)]
        | Annotated[tuple[RootCount, ...], Field(min_length=2, max_length=8)]
    ) = Field(description="Total root count or complete per-irrep count tuple.")
    spin: Literal["singlet", "triplet", "both", "unrestricted"] = Field(
        default="singlet",
        description="RHF singlets, triplets, their native split, or unrestricted "
        "spin-conserving response. Both favors singlets for odd counts.",
    )
    approximation: Literal["rpa", "tda"] = Field(
        default="rpa", description="Full linear response or Tamm--Dancoff equations."
    )
    residual_threshold: float = Field(
        default=1e-4,
        gt=0,
        lt=1,
        description="Positive response residual norm threshold below one.",
    )
    max_iterations: int = Field(
        default=60, ge=1, description="Maximum iterative response-solver iterations."
    )

    @model_validator(mode="after")
    def check_roots(self) -> Self:
        """Return a nonempty requested root set.

        Raises:
            ValueError: Every per-irrep count is zero.
        """
        if self.state_count == 0:
            raise ValueError("Request at least one TD-SCF root")
        return self

    @property
    def state_count(self) -> int:
        """Return the total number of roots requested across all sectors."""
        return self.states if isinstance(self.states, int) else sum(self.states)

    @property
    def native_states(self) -> tuple[int, ...]:
        """Return Psi4's array form; a one-member array means a total root count."""
        return (self.states,) if isinstance(self.states, int) else self.states

    @property
    def native_triplets(self) -> str:
        """Return Psi4's explicit triplet-sector option."""
        return {
            "singlet": "NONE",
            "triplet": "ONLY",
            "both": "ALSO",
            "unrestricted": "NONE",
        }[self.spin]

    @property
    def sector_counts(self) -> tuple[int, ...]:
        """Return requested root counts in the separate spin response spaces."""
        if self.spin != "both":
            return (self.state_count,)
        counts = self.native_states
        return (
            sum((value + 1) // 2 for value in counts),
            sum(value // 2 for value in counts),
        )
