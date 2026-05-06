from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from src.refactored.assembly.natal import build_natal_tinh_ban
from src.refactored.assembly.period import build_period_layer
from src.refactored.component import Component
from src.refactored.component.elementary import DiaChi
from src.refactored.component_catalog import ComponentCatalog, get_default_catalog
from src.refactored.context.natal import NatalContext
from src.refactored.context.period import PeriodKind, build_period_context
from src.refactored.context.period_focus import DaiHanFocusMap
from src.refactored.context.prior import LaSoPrior
from src.refactored.cung import Cung
from src.refactored.placement.layer import LayerId, NATAL_LAYER_ID, PlacementLayer
from src.refactored.placement.registry import ComponentId
from src.refactored.tinh_ban import TinhBan


@dataclass
class LaSo:
    prior: LaSoPrior
    natal_context: NatalContext
    catalog: ComponentCatalog
    tinh_ban: TinhBan

    @classmethod
    def from_prior(
        cls,
        prior: LaSoPrior,
        catalog: ComponentCatalog | None = None,
    ) -> "LaSo":
        natal_context = NatalContext.from_prior(prior)
        return cls(
            prior=prior,
            natal_context=natal_context,
            catalog=catalog or get_default_catalog(),
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
        return self.tinh_ban.period_layer(
            context=context,
            build_fn=lambda ctx: build_period_layer(
                context=ctx,
                tinh_ban=self.tinh_ban,
            ),
        )
