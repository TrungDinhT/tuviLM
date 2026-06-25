from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated, Literal

import annotated_types as at
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi, ThienCan


_BLANK_LINE_RE = re.compile(r"\n\s*\n+")


Gender = Literal["male", "female"]
Mode = Literal["any", "all"]
GroupName = Literal[
    "luc_sat",
    "sat_tinh",
    "luc_cat",
    "cat_tinh",
    "tu_hoa",
    "tam_hoa",
    "xuong_khuc_khoa_tue_tau",
    "cat_tinh_tam_hoa",
    "cat_tinh_tam_hoa_tam_minh",
    "khong_kiep_hao_ky_tue",
    "tu_phu_xuong_khuc_khoi_viet",
]
Scope = Literal[
    "tam_hop",
    "hoi_hop",
    "dong_hoac_xung",
    "dong_cung",
    "nhi_hop",
    "xung_chieu",
    "giap",
]
Brightness = Literal["mieu", "vuong", "dac", "binh hoa", "ham"]


class SourceKind(StrEnum):
    TUVITANBIEN = "tuvitanbien"


class BaseCondition(BaseModel):
    type: str


class GroupSupportMixin(BaseModel):
    group_name: GroupName | None = Field(
        default=None,
        validation_alias=AliasChoices("group_name", "group"),
    )
    mode: Mode | None = None
    at_least: int | None = None

    @model_validator(mode="after")
    def _validate_group_support(self) -> GroupSupportMixin:
        if self.group_name is None:
            if self.mode is not None or self.at_least is not None:
                raise ValueError(
                    "mode and at_least are only valid when group_name is set"
                )
        elif self.mode is None and self.at_least is None:
            raise ValueError("group_name requires mode or at_least")
        return self


class CanMatchCondition(BaseCondition):
    type: Literal["can_match"] = "can_match"
    can: Annotated[list[ThienCan], at.MinLen(1)]


class CanExcludeCondition(BaseCondition):
    type: Literal["can_exclude"] = "can_exclude"
    can: Annotated[list[ThienCan], at.MinLen(1)]


class GenderMatchCondition(BaseCondition):
    type: Literal["gender_match"] = "gender_match"
    gender: Gender


class PalaceAtCondition(BaseCondition):
    type: Literal["palace_at"] = "palace_at"
    palace: Role
    chi: Annotated[list[DiaChi], at.MinLen(1)]


class OnlyChinhTinhCondition(BaseCondition):
    type: Literal["only_chinh_tinh"] = "only_chinh_tinh"
    palace: Role
    star: str


class StarBrightnessCondition(BaseCondition):
    type: Literal["star_brightness"] = "star_brightness"
    stars: Annotated[list[str], at.MinLen(1)]
    brightness: Annotated[list[Brightness], at.MinLen(1)]


class StarWithPalaceCondition(BaseCondition, GroupSupportMixin):
    type: Literal["star_with_palace"] = "star_with_palace"
    palace: Role
    stars: list[str] = Field(default_factory=list)
    scope: Scope
    stars_matching_logic: Mode | None = "any"

    @model_validator(mode="after")
    def _validate_group_mode(self) -> StarWithPalaceCondition:
        if not self.stars and self.group_name is None:
            raise ValueError("star_with_palace requires stars or group_name")
        if self.group_name is not None:
            self.stars_matching_logic = None
        return self


class StarAtChiCondition(BaseCondition, GroupSupportMixin):
    type: Literal["star_at_chi"] = "star_at_chi"
    at_chi: Annotated[list[DiaChi], at.MinLen(1)]
    stars: list[str] = Field(default_factory=list)
    stars_matching_logic: Mode | None = "all"

    @model_validator(mode="after")
    def _validate_group_mode(self) -> StarAtChiCondition:
        if not self.stars and self.group_name is None:
            raise ValueError("star_at_chi requires stars or group_name")
        if self.group_name is not None:
            self.stars_matching_logic = None
        return self


class StarsMeetingCondition(BaseCondition, GroupSupportMixin):
    model_config = ConfigDict(extra="forbid")

    type: Literal["stars_meeting"] = "stars_meeting"
    scope: Scope
    stars: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_group_mode(self) -> StarsMeetingCondition:
        if not self.stars and self.group_name is None:
            raise ValueError("stars_meeting requires stars or group_name")
        return self


class CungThanAtPalaceCondition(BaseCondition):
    type: Literal["cung_than_at_palace"] = "cung_than_at_palace"
    palace: Role


LeafCondition = Annotated[
    CanMatchCondition
    | CanExcludeCondition
    | GenderMatchCondition
    | PalaceAtCondition
    | OnlyChinhTinhCondition
    | StarBrightnessCondition
    | StarWithPalaceCondition
    | StarAtChiCondition
    | StarsMeetingCondition
    | CungThanAtPalaceCondition,
    Field(discriminator="type"),
]


class AllCondition(BaseModel):
    all_: list[Condition] = Field(..., alias="all")


class AnyCondition(BaseModel):
    any_: list[Condition] = Field(..., alias="any")


class NotCondition(BaseModel):
    not_: Condition = Field(..., alias="not")


Condition = LeafCondition | AllCondition | AnyCondition | NotCondition


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
    related_to: Role | None = None

    @field_validator("evidence", mode="before")
    @classmethod
    def _collapse_blank_lines(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return _BLANK_LINE_RE.sub("\n", value).strip()


class CachCucData(BaseModel):
    groups: dict[str, Group] = Field(default_factory=dict)
    cach_cuc: list[CachCuc] = Field(default_factory=list)


class CachCucToolResult(BaseModel):
    id: str
    name: str
    page: int
    priority: int = 0
    meaning: str
    related_to: Role | None = None

    @classmethod
    def from_cach_cuc(cls, cach_cuc: CachCuc) -> CachCucToolResult:
        return cls(
            id=cach_cuc.id,
            name=cach_cuc.name,
            page=cach_cuc.page,
            priority=cach_cuc.priority,
            meaning=cach_cuc.meaning,
            related_to=cach_cuc.related_to,
        )


AllCondition.model_rebuild()
AnyCondition.model_rebuild()
NotCondition.model_rebuild()
CachCuc.model_rebuild()
CachCucData.model_rebuild()


__all__ = [
    "AllCondition",
    "AnyCondition",
    "BaseCondition",
    "Brightness",
    "CachCuc",
    "CachCucData",
    "CachCucToolResult",
    "CanExcludeCondition",
    "CanMatchCondition",
    "Condition",
    "CungThanAtPalaceCondition",
    "DiaChi",
    "Gender",
    "GenderMatchCondition",
    "Group",
    "GroupName",
    "GroupSupportMixin",
    "Mode",
    "NotCondition",
    "OnlyChinhTinhCondition",
    "PalaceAtCondition",
    "Role",
    "Scope",
    "SourceKind",
    "StarAtChiCondition",
    "StarBrightnessCondition",
    "StarWithPalaceCondition",
    "StarsMeetingCondition",
    "ThienCan",
]
