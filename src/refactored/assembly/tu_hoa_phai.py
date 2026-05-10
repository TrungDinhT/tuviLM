from __future__ import annotations

from typing import Mapping

from src.refactored.model.elementary import DiaChi
from src.refactored.context.tu_hoa_phai import TuHoaPhaiContext
from src.refactored.model.cung import CungId
from src.refactored.placement.bundle import get_default_placement_rule_compiler
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.model.layer import PlacementLayer, TuHoaPhaiLayerId
from src.refactored.placement.scopes import TU_HOA_PHAI_SCOPE
from src.refactored.placement.registry import ComponentId


def build_tu_hoa_phai_layers(
    *,
    cung_ids: Mapping[DiaChi, CungId],
    natal_layer: PlacementLayer,
    compiler: PlacementRuleCompiler | None = None,
) -> tuple[PlacementLayer, ...]:
    return tuple(
        build_tu_hoa_phai_layer(
            layer_id=TuHoaPhaiLayerId(source_dia_chi=cung_id.dia_chi),
            context=TuHoaPhaiContext(
                source_dia_chi=cung_id.dia_chi,
                thien_can=cung_id.thien_can,
            ),
            natal_layer=natal_layer,
            compiler=compiler,
        )
        for cung_id in cung_ids.values()
    )


def build_tu_hoa_phai_layer(
    *,
    layer_id: TuHoaPhaiLayerId,
    context: TuHoaPhaiContext,
    natal_layer: PlacementLayer,
    compiler: PlacementRuleCompiler | None = None,
) -> PlacementLayer:
    active_compiler = compiler or get_default_placement_rule_compiler()
    specialized_rules = active_compiler.compile(
        context,
        scope=TU_HOA_PHAI_SCOPE,
        seed=natal_layer.by_component,
    )
    resolved_positions = PlacementEngine(specialized_rules).resolve_all()
    return PlacementLayer.from_component_positions(
        id=layer_id,
        positions={
            component_id: resolved_positions[component_id]
            for component_id in TU_HOA_PHAI_SCOPE
        },
    )
