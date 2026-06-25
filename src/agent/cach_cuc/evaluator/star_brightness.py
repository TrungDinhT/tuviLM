"""Matcher for star brightness conditions."""

from __future__ import annotations

from src.agent.cach_cuc.evaluator.context import CachCucMatchContext
from src.agent.cach_cuc.models import StarBrightnessCondition
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import Status


STATUS_TO_BRIGHTNESS: dict[Status, str] = {
    Status.MIEU: "mieu",
    Status.VUONG: "vuong",
    Status.DAC: "dac",
    Status.BINH: "binh hoa",
    Status.HAM: "ham",
}


def _match_star_brightness(
    condition: StarBrightnessCondition,
    context: CachCucMatchContext,
) -> bool:
    """Require every listed star to have at least one allowed brightness position."""
    allowed = set(condition.brightness)
    for star_id in condition.stars:
        positions = context.positions_of_star(star_id)
        if not positions:
            return False
        if not any(
            STATUS_TO_BRIGHTNESS.get(MAP_SAO_STATUS.get(star_id, {}).get(position))
            in allowed
            for position in positions
        ):
            return False
    return True
