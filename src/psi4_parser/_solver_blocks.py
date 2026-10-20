"""Share named solver input fields between the builder and job APIs.

Public models list their API base last to preserve its validation settings
and field order.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PCMFields(BaseModel):
    """Named PCMSolver configuration text."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["pcm"] = Field(
        default="pcm", description="Selects a solvent configuration for PCMSolver."
    )
    name: str | None = Field(
        default=None, description="Optional name for this solvent configuration block."
    )
    body: str = Field(
        description="PCMSolver input text, including its nested sections."
    )


class CFourFields(BaseModel):
    """Named CFOUR configuration text."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["cfour"] = Field(
        default="cfour", description="Selects a CFOUR configuration block."
    )
    name: str | None = Field(
        default=None, description="Optional name for this CFOUR configuration block."
    )
    body: str = Field(description="CFOUR input text to include in the block.")
