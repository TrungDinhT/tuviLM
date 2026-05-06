from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable, Iterable

from src.refactored.component.cung_role import Role
from src.refactored.component.elementary import DiaChi
from src.refactored.context.period_focus import (
    DaiHanFocusMap,
    PeriodFocusMaps,
    TieuHanFocusMap
)
from src.refactored.context.protocol import PeriodContext
from src.refactored.cung import Cung, CungId, LayeredComponent
from src.refactored.placement.layer import (
    LayerId,
    LayerKind,
    NATAL_LAYER_ID,
    PlacementLayer,
)
from src.refactored.placement.registry import ComponentId


class LayerIdLruOrder:
    def __init__(self) -> None:
        # Ordered set implemented with OrderedDict keys.
        # Values are always None; only key order matters for LRU.
        self._order: OrderedDict[LayerId, None] = OrderedDict()

    def mark_used(self, layer_id: LayerId) -> None:
        self._order[layer_id] = None
        self._order.move_to_end(layer_id)

    def remember(self, layer_id: LayerId, max_size: int) -> LayerId | None:
        self.mark_used(layer_id)
        if len(self._order) <= max_size:
            return None
        evicted_layer_id, _ = self._order.popitem(last=False)
        return evicted_layer_id


class PeriodLayerCache:
    def __init__(self, max_layers_per_kind: int = 10) -> None:
        self.max_layers_per_kind = max_layers_per_kind
        self._order_by_kind: dict[LayerKind, LayerIdLruOrder] = {}

    def mark_used(self, layer_id: LayerId) -> None:
        self._order_for(layer_id.kind).mark_used(layer_id)

    def remember(self, layer_id: LayerId) -> LayerId | None:
        return self._order_for(layer_id.kind).remember(
            layer_id,
            self.max_layers_per_kind,
        )

    def _order_for(self, kind: LayerKind) -> LayerIdLruOrder:
        if kind not in self._order_by_kind:
            self._order_by_kind[kind] = LayerIdLruOrder()
        return self._order_by_kind[kind]


@dataclass
class TinhBan:
    cung_ids: dict[DiaChi, CungId]
    natal_layer: PlacementLayer
    period_focus_maps: PeriodFocusMaps
    overlay_layers: dict[LayerId, PlacementLayer] = field(default_factory=dict)

    _period_layer_cache: PeriodLayerCache = field(
        default_factory=PeriodLayerCache,
        init=False,
        repr=False,
        compare=False
    )

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
        return self.overlay_layers[layer_id]

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
        context: PeriodContext,
        build_fn: Callable[[PeriodContext], PlacementLayer],
    ) -> PlacementLayer:
        layer_id = context.layer_id
        if layer := self.overlay_layers.get(layer_id):
            self._period_layer_cache.mark_used(layer_id)
            return layer

        layer = build_fn(context)
        evicted_layer_id = self._period_layer_cache.remember(layer_id)
        self.overlay_layers[layer_id] = layer
        if evicted_layer_id is not None:
            self.overlay_layers.pop(evicted_layer_id, None)
        return layer
