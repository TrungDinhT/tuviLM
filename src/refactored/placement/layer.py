from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping, TypeAlias

from src.refactored.component.cung_role import Role
from src.refactored.component.elementary import DiaChi
from src.refactored.placement.registry import ComponentId


class LayerKind(StrEnum):
    NATAL = "natal"
    TIEU_HAN = "tieu_han"
    DAI_HAN = "dai_han"
    LUU_NIEN_DAI_HAN = "luu_nien_dai_han"
    TU_HOA_PHAI = "tu_hoa_phai"


@dataclass(frozen=True)
class NatalLayerId:
    @property
    def kind(self) -> LayerKind:
        return LayerKind.NATAL


@dataclass(frozen=True)
class TieuHanLayerId:
    year: int

    @property
    def kind(self) -> LayerKind:
        return LayerKind.TIEU_HAN


@dataclass(frozen=True)
class DaiHanLayerId:
    start_age: int
    end_age: int

    @property
    def kind(self) -> LayerKind:
        return LayerKind.DAI_HAN


@dataclass(frozen=True)
class LuuNienDaiHanLayerId:
    year: int

    @property
    def kind(self) -> LayerKind:
        return LayerKind.LUU_NIEN_DAI_HAN


@dataclass(frozen=True)
class TuHoaPhaiLayerId:
    source_dia_chi: DiaChi

    @property
    def kind(self) -> LayerKind:
        return LayerKind.TU_HOA_PHAI


LayerId: TypeAlias = (
    NatalLayerId
    | TieuHanLayerId
    | DaiHanLayerId
    | LuuNienDaiHanLayerId
    | TuHoaPhaiLayerId
)

NATAL_LAYER_ID = NatalLayerId()


@dataclass(frozen=True)
class PlacementLayer:
    id: LayerId
    by_component: Mapping[ComponentId, DiaChi]
    by_position: Mapping[DiaChi, frozenset[ComponentId]]
    focus_position: DiaChi | None = None

    @classmethod
    def from_component_positions(
        cls,
        *,
        id: LayerId,
        positions: Mapping[ComponentId, DiaChi],
        focus_position: DiaChi | None = None,
    ) -> "PlacementLayer":
        by_component = dict(positions)
        by_position: dict[DiaChi, set[ComponentId]] = {}
        for component_id, dia_chi in by_component.items():
            by_position.setdefault(dia_chi, set()).add(component_id)

        return cls(
            id=id,
            by_component=by_component,
            by_position={
                dia_chi: frozenset(component_ids)
                for dia_chi, component_ids in by_position.items()
            },
            focus_position=focus_position,
        )

    @property
    def kind(self) -> LayerKind:
        return self.id.kind

    def position_of(self, component_id: ComponentId) -> DiaChi | None:
        return self.by_component.get(component_id)

    def components_at(self, dia_chi: DiaChi) -> frozenset[ComponentId]:
        return self.by_position.get(dia_chi, frozenset())


ROLE_COMPONENT_IDS: frozenset[ComponentId] = frozenset(role.value for role in Role)
STRUCTURAL_COMPONENT_IDS: frozenset[ComponentId] = ROLE_COMPONENT_IDS
