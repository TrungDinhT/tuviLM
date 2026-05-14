from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable

from src.refactored.model.layer import (
    LayerId,
    LayerKind,
    PERIOD_LAYER_KINDS,
    PeriodLayerId,
    PlacementLayer,
)


class _LayerIdLruOrder:
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
        self._order_by_kind: dict[LayerKind, _LayerIdLruOrder] = {}

    def mark_used(self, layer_id: PeriodLayerId) -> None:
        self._order_for(layer_id.kind).mark_used(layer_id)

    def remember(self, layer_id: PeriodLayerId) -> LayerId | None:
        return self._order_for(layer_id.kind).remember(
            layer_id,
            self.max_layers_per_kind,
        )

    def _order_for(self, kind: LayerKind) -> _LayerIdLruOrder:
        if kind not in self._order_by_kind:
            self._order_by_kind[kind] = _LayerIdLruOrder()
        return self._order_by_kind[kind]


@dataclass
class PeriodLayerStore:
    layers: dict[PeriodLayerId, PlacementLayer] = field(default_factory=dict)
    cache: PeriodLayerCache = field(default_factory=PeriodLayerCache)

    def get_or_build(
        self,
        layer_id: PeriodLayerId,
        build_fn: Callable[[], PlacementLayer],
    ) -> PlacementLayer:
        if layer_id.kind not in PERIOD_LAYER_KINDS:
            raise ValueError(f"Expected period layer id, got {layer_id!r}.")
        if layer := self.layers.get(layer_id):
            self.cache.mark_used(layer_id)
            return layer

        layer = build_fn()
        if layer.id != layer_id:
            raise ValueError(
                f"Built layer id {layer.id!r} does not match requested "
                f"{layer_id!r}."
            )
        evicted_layer_id = self.cache.remember(layer_id)
        self.layers[layer_id] = layer
        if evicted_layer_id is not None:
            self.layers.pop(evicted_layer_id, None)
        return layer
