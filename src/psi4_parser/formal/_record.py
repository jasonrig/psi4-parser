"""Keep scientific requests, plans, and evidence immutable and serializable."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """Reject undeclared fields, non-finite numbers, and unchecked nested values."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
        allow_inf_nan=False,
        revalidate_instances="always",
    )
