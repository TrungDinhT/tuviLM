from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.refactored.components.definitions import Component
from src.refactored.components.definitions.cung_role import CungRole
from src.refactored.components.definitions.elementary import (
    DiaChiEntity,
    ThienCanEntity,
)
from src.refactored.model.elementary import (
    DiaChi,
    ThienCan,
)
from src.refactored.model.prior import Gender
from src.refactored.model.layer import LayerKind


class LayeredComponentView(BaseModel):
    model_config = ConfigDict(frozen=True)

    layer_kind: LayerKind
    component: Component


class CungView(BaseModel):
    model_config = ConfigDict(frozen=True)

    dia_chi_entity: DiaChiEntity
    thien_can_entity: ThienCanEntity
    role: CungRole
    is_cung_than: bool
    components: tuple[LayeredComponentView, ...]


class TieuHanFocusView(BaseModel):
    model_config = ConfigDict(frozen=True)

    year_dia_chi: DiaChi
    focus_position: DiaChi


class DaiHanFocusView(BaseModel):
    model_config = ConfigDict(frozen=True)

    start_age: int
    end_age: int
    focus_position: DiaChi


class LaSoView(BaseModel):
    model_config = ConfigDict(frozen=True)

    hour: DiaChi
    date: int
    month: int
    year: int
    gender: Gender
    dia_chi_natal_year: DiaChi
    thien_can_natal_year: ThienCan
    study_year: int
    ban_menh_name: str
    cuc_name: str
    menh_cuc_relation_label: str
    tieu_han_focus_map: tuple[TieuHanFocusView, ...]
    dai_han_focus_map: tuple[DaiHanFocusView, ...]
    cungs: tuple[CungView, ...]
