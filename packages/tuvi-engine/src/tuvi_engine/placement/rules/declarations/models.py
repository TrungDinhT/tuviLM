from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class FixedAnchorDeclaration(FrozenModel):
    kind: Literal["dia_chi"]
    value: str


class FormulaAnchorDeclaration(FrozenModel):
    kind: Literal["formula"]
    name: str


class DiaChiGroupDeclaration(FrozenModel):
    dia_chi: tuple[str, ...]
    position: str


class DiaChiGroupsAnchorDeclaration(FrozenModel):
    kind: Literal["dia_chi_groups"]
    groups: tuple[DiaChiGroupDeclaration, ...]


AnchorDeclaration = Annotated[
    FixedAnchorDeclaration | FormulaAnchorDeclaration | DiaChiGroupsAnchorDeclaration,
    Field(discriminator="kind"),
]


class SamePositionMemberDeclaration(FrozenModel):
    kind: Literal["same_position"]
    component_id: str
    reference_id: str


CircleMemberDeclaration = str | SamePositionMemberDeclaration


class AbsoluteFormulaDeclaration(FrozenModel):
    kind: Literal["absolute_formula"]
    component_id: str
    formula: str


class AbsoluteByThienCanDeclaration(FrozenModel):
    kind: Literal["absolute_by_thien_can"]
    component_id: str
    mapping: dict[str, str]


class AbsoluteByDiaChiGroupsDeclaration(FrozenModel):
    kind: Literal["absolute_by_dia_chi_groups"]
    component_id: str
    groups: tuple[DiaChiGroupDeclaration, ...]


class DefinitiveDeclaration(FrozenModel):
    kind: Literal["definitive"]
    component_id: str
    position: str


class RelativeDeclaration(FrozenModel):
    kind: Literal["relative"]
    component_id: str
    reference_id: str
    transform: str
    direction: str | None = None
    axis: tuple[str, str] | None = None
    step_multiplier: int = 1
    date_offset: int = 0


class FromAnchorDeclaration(FrozenModel):
    kind: Literal["from_anchor"]
    component_id: str
    anchor: AnchorDeclaration
    transform: str
    direction: str | None = None
    step_multiplier: int = 1
    step: str | int | None = None


class CircleDeclaration(FrozenModel):
    kind: Literal["circle"]
    principal_id: str
    anchor: AnchorDeclaration
    others: tuple[CircleMemberDeclaration, ...]
    direction: str = "cw"


class OffsetGroupDeclaration(FrozenModel):
    kind: Literal["offset_group"]
    anchor_id: str
    anchor: AnchorDeclaration
    offsets: dict[str, int]


class SamePositionDeclaration(FrozenModel):
    kind: Literal["same_position"]
    component_id: str
    reference_id: str


class TuanTrietPairDeclaration(FrozenModel):
    kind: Literal["tuan_triet_pair"]
    pair_ids: tuple[str, str]
    formula: str


class TuHoaDeclaration(FrozenModel):
    kind: Literal["tu_hoa"]
    mapping: dict[str, dict[str, str]]


PlacementRuleDeclaration = Annotated[
    AbsoluteFormulaDeclaration
    | AbsoluteByThienCanDeclaration
    | AbsoluteByDiaChiGroupsDeclaration
    | DefinitiveDeclaration
    | RelativeDeclaration
    | FromAnchorDeclaration
    | CircleDeclaration
    | OffsetGroupDeclaration
    | SamePositionDeclaration
    | TuanTrietPairDeclaration
    | TuHoaDeclaration,
    Field(discriminator="kind"),
]


class PlacementRuleGroup(FrozenModel):
    rules: tuple[PlacementRuleDeclaration, ...]
