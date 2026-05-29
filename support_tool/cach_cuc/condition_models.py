from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


_BLANK_LINE_RE = re.compile(r"\n\s*\n+")


Gender = Literal["male", "female"]
Mode = Literal["any", "all"]
Scope = Literal[
    "tam_hop",
    "hoi_hop",
    "dong_hoac_xung",
    "dong_cung",
    "nhi_hop",
    "xung_chieu",
    "giap",
]


class BaseCondition(BaseModel):
    type: str


class CanMatchCondition(BaseCondition):
    type: Literal["can_match"] = "can_match"
    can: list[str]


class CanExcludeCondition(BaseCondition):
    type: Literal["can_exclude"] = "can_exclude"
    can: list[str]


class GenderMatchCondition(BaseCondition):
    type: Literal["gender_match"] = "gender_match"
    gender: Gender


class PalaceAtCondition(BaseCondition):
    type: Literal["palace_at"] = "palace_at"
    palace: str
    chi: list[str]


class NoStarsCondition(BaseCondition):
    type: Literal["no_stars"] = "no_stars"
    in_palace: str
    stars: list[str] | None = None
    group: str | None = None


class OnlyChinhTinhCondition(BaseCondition):
    type: Literal["only_chinh_tinh"] = "only_chinh_tinh"
    palace: str
    star: str


class StarBrightnessCondition(BaseCondition):
    type: Literal["star_brightness"] = "star_brightness"
    stars: list[str]
    brightness: list[str]


class StarInPalaceCondition(BaseCondition):
    type: Literal["star_in_palace"] = "star_in_palace"
    palace: str
    stars: list[str] | None = None
    group: str | None = None
    mode: Mode | None = None

    @model_validator(mode="after")
    def _validate_group_mode(self) -> StarInPalaceCondition:
        if self.mode is not None and self.group is None:
            raise ValueError("mode is only valid when group is set")
        if self.stars is None and self.group is None:
            raise ValueError("star_in_palace requires stars or group")
        return self


class StarAtChiCondition(BaseCondition):
    type: Literal["star_at_chi"] = "star_at_chi"
    at_chi: list[str]
    stars: list[str] | None = None
    group: str | None = None
    mode: Mode | None = None

    @model_validator(mode="after")
    def _validate_group_mode(self) -> StarAtChiCondition:
        if self.mode is not None and self.group is None:
            raise ValueError("mode is only valid when group is set")
        if self.stars is None and self.group is None:
            raise ValueError("star_at_chi requires stars or group")
        return self


class StarsMeetingCondition(BaseCondition):
    type: Literal["stars_meeting"] = "stars_meeting"
    scope: Scope
    stars: list[str] | None = None
    group: str | None = None
    mode: Mode | None = None

    @model_validator(mode="after")
    def _validate_group_mode(self) -> StarsMeetingCondition:
        if self.mode is not None and self.group is None:
            raise ValueError("mode is only valid when group is set")
        if self.stars is None and self.group is None:
            raise ValueError("stars_meeting requires stars or group")
        return self


LeafCondition = Annotated[
    CanMatchCondition
    | CanExcludeCondition
    | GenderMatchCondition
    | PalaceAtCondition
    | NoStarsCondition
    | OnlyChinhTinhCondition
    | StarBrightnessCondition
    | StarInPalaceCondition
    | StarAtChiCondition
    | StarsMeetingCondition,
    Field(discriminator="type"),
]


class AllCondition(BaseModel):
    all: list[Condition]


class AnyCondition(BaseModel):
    any: list[Condition]


Condition = LeafCondition | AllCondition | AnyCondition


class Group(BaseModel):
    stars: list[str]


class CachCuc(BaseModel):
    id: str
    name: str
    page: int
    priority: int = 0
    meaning: str
    evidence: str | None = None
    conditions: Condition

    @field_validator("evidence", mode="before")
    @classmethod
    def _collapse_blank_lines(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return _BLANK_LINE_RE.sub("\n", value).strip()


class CachCucData(BaseModel):
    groups: dict[str, Group] = {}
    cach_cuc: list[CachCuc] = []


AllCondition.model_rebuild()
AnyCondition.model_rebuild()
CachCuc.model_rebuild()
CachCucData.model_rebuild()
