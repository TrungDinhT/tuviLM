from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from src.refactored.assembly.natal import build_natal_tinh_ban
from src.refactored.assembly.period import build_period_layer, build_period_layer_id
from src.refactored.components.definitions import Component
from src.refactored.components.repository import (
    ComponentRepository,
    get_default_repository,
)
from src.refactored.context.natal import NatalContext
from src.refactored.context.period import PeriodKind, build_period_context
from src.refactored.model.cung import Cung
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import LayerId, NATAL_LAYER_ID, PlacementLayer
from src.refactored.model.period_focus import DaiHanFocusMap
from src.refactored.model.prior import LaSoPrior
from src.refactored.model.tinh_ban import TinhBan
from src.refactored.placement.registry import ComponentId


@dataclass
class LaSo:
    prior: LaSoPrior
    natal_context: NatalContext
    catalog: ComponentRepository
    tinh_ban: TinhBan

    @classmethod
    def from_prior(
        cls,
        prior: LaSoPrior,
        catalog: ComponentRepository | None = None,
    ) -> "LaSo":
        natal_context = NatalContext.from_prior(prior)
        return cls(
            prior=prior,
            natal_context=natal_context,
            catalog=catalog or get_default_repository(),
            tinh_ban=build_natal_tinh_ban(natal_context),
        )

    def cung_at(
        self,
        dia_chi: DiaChi,
        layer_ids: Iterable[LayerId] = (NATAL_LAYER_ID,),
    ) -> Cung:
        return self.tinh_ban.cung_at(dia_chi, layer_ids)

    def position_of(
        self,
        component_id: ComponentId,
        layer_id: LayerId = NATAL_LAYER_ID,
    ) -> DiaChi | None:
        return self.tinh_ban.position_of(component_id, layer_id)

    def component(self, component_id: ComponentId) -> Component:
        return self.catalog.get(component_id)

    def tieu_han_focus_map(self) -> dict[DiaChi, DiaChi]:
        return self.tinh_ban.tieu_han_focus_map()

    def dai_han_focus_map(self) -> DaiHanFocusMap:
        return self.tinh_ban.dai_han_focus_map()

    def period_layer(self, kind: PeriodKind, year: int) -> PlacementLayer:
        context = build_period_context(
            kind=kind,
            year=year,
            natal_context=self.natal_context,
            focus_maps=self.tinh_ban.period_focus_maps,
            cung_ids=self.tinh_ban.cung_ids,
        )
        layer_id = build_period_layer_id(kind, context)
        return self.tinh_ban.period_layer(
            layer_id=layer_id,
            build_fn=lambda: build_period_layer(
                kind=kind,
                context=context,
                tinh_ban=self.tinh_ban,
            ),
        )
