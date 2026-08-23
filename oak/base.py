"""The shared OAK base model: strict, closed, Rust regex."""

from pydantic import BaseModel, ConfigDict


class OakModel(BaseModel):
    """Every OAK model validates strictly, rejects unknown fields, and runs patterns in rust-regex."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        regex_engine="rust-regex",
        allow_inf_nan=False,
        validate_default=True,
    )
