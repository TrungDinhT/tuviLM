from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, Iterable

from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi
from src.refactored.model.period_focus import (
    DaiHanFocusMap,
    PeriodFocusMaps,
    TieuHanFocusMap
)
from src.refactored.model.cung import Cung, CungId, LayeredComponent
from src.refactored.model.layer import (
    LayerId,
    NATAL_LAYER_ID,
    PeriodLayerId,
    PlacementLayer,
)
from src.refactored.model.period_layer_store import PeriodLayerStore
from src.refactored.placement.registry import ComponentId


@dataclass
class TinhBan:
    cung_ids: dict[DiaChi, CungId]
    natal_layer: PlacementLayer
    period_focus_maps: PeriodFocusMaps
    period_layers: PeriodLayerStore = field(default_factory=PeriodLayerStore)

    @cached_property
    def natal_role_positions(self) -> dict[ComponentId, DiaChi]:
        role_positions: dict[ComponentId, DiaChi] = {}
        for cung_id in self.cung_ids.values():
            role_positions[cung_id.natal_role.value] = cung_id.dia_chi
            if cung_id.is_cung_than:
                role_positions[Role.CUNG_THAN.value] = cung_id.dia_chi
        return role_positions

    @property
    def menh_position(self) -> DiaChi:
        return self.natal_role_positions[Role.MENH.value]

    @property
    def than_position(self) -> DiaChi:
        return self.natal_role_positions[Role.CUNG_THAN.value]

    def layer(self, layer_id: LayerId = NATAL_LAYER_ID) -> PlacementLayer:
        if layer_id == self.natal_layer.id:
            return self.natal_layer
        return self.period_layers.layers[layer_id]

    def position_of(
        self,
        component_id: ComponentId,
        layer_id: LayerId = NATAL_LAYER_ID,
    ) -> DiaChi | None:
        if layer_id == NATAL_LAYER_ID:
            if position := self.natal_role_positions.get(component_id):
                return position
        return self.layer(layer_id).position_of(component_id)

    def components_at(
        self,
        dia_chi: DiaChi,
        layer_ids: Iterable[LayerId] = (NATAL_LAYER_ID,),
    ) -> tuple[LayeredComponent, ...]:
        components: list[LayeredComponent] = []
        for layer_id in layer_ids:
            layer = self.layer(layer_id)
            components.extend(
                LayeredComponent(layer_id=layer.id, component_id=component_id)
                for component_id in sorted(layer.components_at(dia_chi))
            )
        return tuple(components)

    def cung_at(
        self,
        dia_chi: DiaChi,
        layer_ids: Iterable[LayerId] = (NATAL_LAYER_ID,),
    ) -> Cung:
        cung_id = self.cung_ids[dia_chi]
        return Cung(
            dia_chi=cung_id.dia_chi,
            thien_can=cung_id.thien_can,
            natal_role=cung_id.natal_role,
            is_cung_than=cung_id.is_cung_than,
            components=self.components_at(dia_chi, layer_ids),
        )

    def tieu_han_focus_map(self) -> TieuHanFocusMap:
        return self.period_focus_maps.tieu_han

    def dai_han_focus_map(self) -> DaiHanFocusMap:
        return self.period_focus_maps.dai_han

    def period_layer(
        self,
        layer_id: PeriodLayerId,
        build_fn: Callable[[], PlacementLayer],
    ) -> PlacementLayer:
        return self.period_layers.get_or_build(layer_id, build_fn)
