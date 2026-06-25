"""Matcher for anchor-based ``stars_meeting`` conditions."""

from __future__ import annotations

from typing import Iterable

from src.agent.cach_cuc.evaluator.context import CachCucMatchContext
from src.agent.cach_cuc.evaluator.match_types import MatchOutcome
from src.agent.cach_cuc.models import StarsMeetingCondition
from src.agent.cach_cuc.evaluator.scopes import positions_for_scope
from src.agent.cach_cuc.evaluator.star_utils import (
    _match_count,
    _resolve_group_stars,
    _roles_for_positions,
)
from src.refactored.model.elementary import DiaChi


def _match_stars_meeting(
    condition: StarsMeetingCondition,
    context: CachCucMatchContext,
) -> bool:
    """Evaluate star meeting by trying candidate star positions as anchors."""
    return _match_stars_meeting_outcome(condition, context).matched


def _match_stars_meeting_outcome(
    condition: StarsMeetingCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    """Evaluate star meeting and infer roles from matched anchor positions."""
    explicit_stars = list(condition.stars)
    group_stars = _resolve_group_stars(condition, context)
    anchor_stars = explicit_stars or group_stars
    if not anchor_stars:
        return MatchOutcome(False)

    explicit_positions = _positions_by_star(explicit_stars, context)
    group_positions = _positions_by_star(group_stars, context)
    anchor_positions = _positions_by_star(anchor_stars, context)

    if explicit_stars and condition.group_name is None and len(explicit_positions) < 2:
        return MatchOutcome(False)
    if not explicit_stars and len(group_positions) < 2:
        return MatchOutcome(False)

    matched_anchor_positions = _matched_meeting_anchor_positions(
        condition,
        explicit_stars=explicit_stars,
        explicit_positions=explicit_positions,
        group_stars=group_stars,
        group_positions=group_positions,
        anchor_positions=anchor_positions,
    )
    return MatchOutcome(
        bool(matched_anchor_positions),
        _roles_for_positions(matched_anchor_positions, context),
    )


def _positions_by_star(
    star_ids: Iterable[str],
    context: CachCucMatchContext,
) -> dict[str, tuple[DiaChi, ...]]:
    return {
        star_id: positions
        for star_id in star_ids
        if (positions := context.positions_of_star(star_id))
    }


def _matched_meeting_anchor_positions(
    condition: StarsMeetingCondition,
    *,
    explicit_stars: list[str],
    explicit_positions: dict[str, tuple[DiaChi, ...]],
    group_stars: list[str],
    group_positions: dict[str, tuple[DiaChi, ...]],
    anchor_positions: dict[str, tuple[DiaChi, ...]],
) -> list[DiaChi]:
    matched_positions: list[DiaChi] = []
    for anchor_id, positions in anchor_positions.items():
        for anchor_position in positions:
            scope_positions = positions_for_scope(anchor_position, condition.scope)
            if not _anchor_satisfies_explicit_stars(
                explicit_stars,
                explicit_positions,
                anchor_id=anchor_id,
                scope_positions=scope_positions,
            ):
                continue
            if not _anchor_satisfies_group_stars(
                condition,
                explicit_stars=explicit_stars,
                group_stars=group_stars,
                group_positions=group_positions,
                anchor_id=anchor_id,
                scope_positions=scope_positions,
            ):
                continue
            matched_positions.append(anchor_position)
    return matched_positions


def _anchor_satisfies_explicit_stars(
    explicit_stars: list[str],
    explicit_positions: dict[str, tuple[DiaChi, ...]],
    *,
    anchor_id: str,
    scope_positions: frozenset[DiaChi],
) -> bool:
    if not explicit_stars:
        return True
    related_count = _count_stars_related_to_anchor(
        explicit_positions,
        anchor_id=anchor_id,
        scope_positions=scope_positions,
        count_anchor_self=True,
    )
    return _match_count(
        related_count,
        len(explicit_stars),
        mode="all",
        at_least=None,
    )


def _anchor_satisfies_group_stars(
    condition: StarsMeetingCondition,
    *,
    explicit_stars: list[str],
    group_stars: list[str],
    group_positions: dict[str, tuple[DiaChi, ...]],
    anchor_id: str,
    scope_positions: frozenset[DiaChi],
) -> bool:
    if condition.group_name is None:
        return True
    related_count = _count_stars_related_to_anchor(
        group_positions,
        anchor_id=anchor_id,
        scope_positions=scope_positions,
        count_anchor_self=not explicit_stars,
    )
    group_matched = _match_count(
        related_count,
        len(group_stars),
        mode=condition.mode,
        at_least=condition.at_least,
    )
    if not explicit_stars and condition.at_least is None and condition.mode == "any":
        return related_count >= 2
    return group_matched


def _count_stars_related_to_anchor(
    star_positions: dict[str, tuple[DiaChi, ...]],
    *,
    anchor_id: str,
    scope_positions: frozenset[DiaChi],
    count_anchor_self: bool,
) -> int:
    """Count star ids that are represented in an anchor's meeting scope."""
    related_count = 0
    for star_id, positions in star_positions.items():
        if count_anchor_self and star_id == anchor_id:
            related_count += 1
        elif any(position in scope_positions for position in positions):
            related_count += 1
    return related_count
