from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


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


class RedeemCodeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coins: Balance = Field(gt=0)
    kind: Literal["single_use", "per_account"]
    expires_at: AwareDatetime

    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, value: datetime) -> datetime:
        if value <= datetime.now(UTC):
            raise ValueError("Expiration must be in the future.")
        return value.astimezone(UTC)


class RedeemCode(BaseModel):
    code: str
    coins: Balance = Field(gt=0)
    kind: Literal["single_use", "per_account"]
    expires_at: AwareDatetime


class RedeemCodeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: Annotated[
        str,
        StringConstraints(strip_whitespace=True, to_upper=True, min_length=1, max_length=64),
    ]


class RedeemCodeResult(BaseModel):
    coins: Balance = Field(gt=0)
