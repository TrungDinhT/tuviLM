"""Matcher for ``star_at_chi`` conditions."""

from __future__ import annotations

from typing import Iterable

from src.agent.cach_cuc.evaluator.context import CachCucMatchContext
from src.agent.cach_cuc.evaluator.match_types import MatchOutcome
from src.agent.cach_cuc.models import Mode, StarAtChiCondition
from src.agent.cach_cuc.evaluator.star_utils import (
    _match_count,
    _resolve_group_stars,
    _roles_for_positions,
    _star_positions_at_any_chi,
)
from src.refactored.model.elementary import DiaChi


def _match_star_at_chi(
    condition: StarAtChiCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    """Match stars at exact positions and infer roles from matched positions."""
    matched_positions: list[DiaChi] = []
    explicit_stars = list(condition.stars)
    has_matchable_clause = False

    if explicit_stars:
        has_matchable_clause = True
        explicit_matches = [
            _star_positions_at_any_chi(star_id, condition.at_chi, context)
            for star_id in explicit_stars
        ]
        if not _has_required_star_count(
            explicit_matches,
            total_count=len(explicit_stars),
            mode="all",
            at_least=None,
        ):
            return MatchOutcome(False)
        matched_positions.extend(_flatten_positions(explicit_matches))

    if condition.group_name is not None:
        has_matchable_clause = True
        group_stars = _resolve_group_stars(condition, context)
        group_matches = [
            _star_positions_at_any_chi(star_id, condition.at_chi, context)
            for star_id in group_stars
        ]
        if not _has_required_star_count(
            group_matches,
            total_count=len(group_stars),
            mode=condition.mode,
            at_least=condition.at_least,
        ):
            return MatchOutcome(False)
        matched_positions.extend(_flatten_positions(group_matches))

    if not has_matchable_clause:
        return MatchOutcome(False)
    return MatchOutcome(True, _roles_for_positions(matched_positions, context))


def _has_required_star_count(
    star_positions: list[tuple[DiaChi, ...]],
    *,
    total_count: int,
    mode: Mode | None,
    at_least: int | None,
) -> bool:
    matched_count = sum(1 for positions in star_positions if positions)
    return _match_count(
        matched_count,
        total_count,
        mode=mode,
        at_least=at_least,
    )


def _flatten_positions(star_positions: Iterable[tuple[DiaChi, ...]]) -> list[DiaChi]:
    return [position for positions in star_positions for position in positions]
