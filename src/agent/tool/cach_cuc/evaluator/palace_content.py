"""Matchers that inspect palace component contents."""

from __future__ import annotations

from src.agent.tool.cach_cuc.evaluator.context import CachCucMatchContext
from src.agent.tool.cach_cuc.evaluator.match_types import MatchOutcome
from src.agent.tool.cach_cuc.models import OnlyChinhTinhCondition
from src.refactored.components.definitions.sao import ChinhPhuTinh
from src.refactored.model.layer import NATAL_LAYER_ID


def _match_only_chinh_tinh(
    condition: OnlyChinhTinhCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    """Match when a palace has exactly one main star and it is the requested star."""
    palace_position = context.position_of_role(condition.palace)
    component_ids = context.la_so.cung_at(palace_position).components_in_layer(
        NATAL_LAYER_ID
    )
    chinh_tinh_ids = []
    for component_id in component_ids:
        component = context.la_so.component(component_id)
        if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
            chinh_tinh_ids.append(component_id)

    matched = chinh_tinh_ids == [condition.star]
    return MatchOutcome(matched, (condition.palace,) if matched else ())
