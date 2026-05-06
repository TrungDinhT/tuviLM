from __future__ import annotations

from typing import Mapping

from src.refactored.context.protocol import PeriodContext
from src.refactored.component.cung_role import Role
from src.refactored.component.elementary import DiaChi
from src.refactored.placement.bundle import get_default_placement_rule_compiler
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.layer import LayerKind, PlacementLayer
from src.refactored.placement.layer_scopes import (
    DAI_HAN_SCOPE,
    LUU_NIEN_DAI_HAN_SCOPE,
    TIEU_HAN_SCOPE,
)
from src.refactored.placement.registry import ComponentId
from src.refactored.tinh_ban import TinhBan


PERIOD_SCOPE_BY_KIND: dict[LayerKind, frozenset[ComponentId]] = {
    LayerKind.TIEU_HAN: TIEU_HAN_SCOPE,
    LayerKind.DAI_HAN: DAI_HAN_SCOPE,
    LayerKind.LUU_NIEN_DAI_HAN: LUU_NIEN_DAI_HAN_SCOPE,
}


def build_period_layer(
    *,
    context: PeriodContext,
    tinh_ban: TinhBan,
    compiler: PlacementRuleCompiler | None = None,
) -> PlacementLayer:
    scope = PERIOD_SCOPE_BY_KIND[context.layer_id.kind]
    active_compiler = compiler or get_default_placement_rule_compiler()
    specialized_rules = active_compiler.compile(
        context,
        scope=scope,
        seed={
            **tinh_ban.natal_layer.by_component,
            **tinh_ban.natal_role_positions,
        },
    )
    resolved_positions = PlacementEngine(specialized_rules).resolve_all()
    return PlacementLayer.from_component_positions(
        id=context.layer_id,
        positions={
            component_id: resolved_positions[component_id]
            for component_id in scope
        },
        focus_position=context.focus_position,
    )
