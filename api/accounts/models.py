from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


Plan = Literal["normal", "full_unlock"]
Balance = Annotated[int, Field(strict=True, ge=0, le=9_007_199_254_740_991)]


class AccountAccess(BaseModel):
    plan: Plan = "normal"
    balance: Balance = 0


class AccountAccessUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: Plan | None = None
    balance: Balance | None = None

    @model_validator(mode="after")
    def validate_changes(self) -> Self:
        if not self.model_fields_set or any(
            getattr(self, field) is None for field in self.model_fields_set
        ):
            raise ValueError("Provide a plan or balance value; null is not allowed.")
        return self
