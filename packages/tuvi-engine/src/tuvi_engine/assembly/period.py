from __future__ import annotations

from src.refactored.context.period import (
    DaiHanContext,
    LuuNienDaiHanContext,
    PeriodKind,
    TieuHanContext,
)
from src.refactored.placement.bundle import get_default_placement_rule_compiler
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.model.layer import (
    DaiHanLayerId,
    LuuNienDaiHanLayerId,
    PeriodLayerId,
    PlacementLayer,
    TieuHanLayerId,
)
from src.refactored.placement.scopes import (
    DAI_HAN_SCOPE,
    LUU_NIEN_DAI_HAN_SCOPE,
    TIEU_HAN_SCOPE,
)
from src.refactored.placement.registry import ComponentId
from src.refactored.model.tinh_ban import TinhBan


PERIOD_SCOPE_BY_KIND: dict[PeriodKind, frozenset[ComponentId]] = {
    PeriodKind.TIEU_HAN: TIEU_HAN_SCOPE,
    PeriodKind.DAI_HAN: DAI_HAN_SCOPE,
    PeriodKind.LUU_NIEN_DAI_HAN: LUU_NIEN_DAI_HAN_SCOPE,
}


PeriodLayerContext = TieuHanContext | DaiHanContext | LuuNienDaiHanContext


def build_period_layer_id(
    kind: PeriodKind,
    context: PeriodLayerContext,
) -> PeriodLayerId:
    if kind is PeriodKind.TIEU_HAN and isinstance(context, TieuHanContext):
        return TieuHanLayerId(year=context.year)
    if kind is PeriodKind.DAI_HAN and isinstance(context, DaiHanContext):
        return DaiHanLayerId(
            start_age=context.age_range.start_age,
            end_age=context.age_range.end_age,
        )
    if (
        kind is PeriodKind.LUU_NIEN_DAI_HAN
        and isinstance(context, LuuNienDaiHanContext)
    ):
        return LuuNienDaiHanLayerId(year=context.year)
    raise TypeError(f"Period kind {kind!r} does not match context {context!r}.")


def build_period_layer(
    *,
    kind: PeriodKind,
    context: PeriodLayerContext,
    tinh_ban: TinhBan,
    compiler: PlacementRuleCompiler | None = None,
) -> PlacementLayer:
    scope = PERIOD_SCOPE_BY_KIND[kind]
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
        id=build_period_layer_id(kind, context),
        positions={
            component_id: resolved_positions[component_id]
            for component_id in scope
        },
        focus_position=context.focus_position,
    )
