"""Public cach_cuc matcher facade.

The matching implementation is split by responsibility:
- ``evaluator.context`` reads roles and star positions from the chart.
- ``evaluator.scopes`` expands scopes such as hoi_hop and xung_chieu.
- ``evaluator.core`` walks the condition tree.
- ``evaluator.star_conditions`` exposes star-specific algorithms.

Maintenance notes for the error-prone parts:
- ``related_roles`` is not persisted in YAML. It is inferred from matched
  positive role-bearing conditions in YAML order.
- ``not`` conditions never contribute ``related_roles``. They only validate absence.
- ``star_with_palace`` requires both explicit stars and group stars to match when
  both are authored.
- ``stars_meeting`` is anchor-based. When explicit stars and a group are both
  authored, explicit stars are the anchor candidates and the group is checked
  against those anchors.
"""

from __future__ import annotations

import logging

from src.agent.cach_cuc.evaluator import (
    CachCucMatchContext,
    MatchOutcome,
    STAR_ALIASES,
    match_condition,
    merge_related_roles,
)
from src.agent.cach_cuc.loader import load_cach_cuc_source
from src.agent.cach_cuc.models import (
    CachCuc,
    CachCucData,
    CachCucToolResult,
    Role,
    SourceKind,
)
from src.agent.cach_cuc.evaluator.scopes import NHI_HOP_PAIRS, positions_for_scope
from src.agent.cach_cuc.evaluator.star_conditions import (
    _match_count,
    _match_only_chinh_tinh,
    _match_star_brightness,
    _match_stars_meeting,
    _match_supported_stars,
    _resolve_condition_stars,
    _star_at_any_chi,
)
from src.refactored.la_so import LaSo


_logger = logging.getLogger(__name__)


def find_matching_cach_cuc(
    la_so: LaSo,
    *,
    data: CachCucData | None = None,
    source_kind: SourceKind = SourceKind.TUVITANBIEN,
    filtered_roles: list[Role] | None = None,
) -> list[CachCuc]:
    """Evaluate every cach_cuc and return matches sorted by priority descending.

    The YAML order is kept as the tie-breaker so equal-priority results remain
    deterministic for the agent.
    """
    source_data = data or load_cach_cuc_source(source_kind)
    context = CachCucMatchContext.from_la_so(la_so, source_data)
    role_filter = set(filtered_roles) if filtered_roles is not None else None
    checked_count = len(source_data.cach_cuc)
    raw_match_count = 0
    filtered_out_count = 0

    _logger.info(
        "Starting cach_cuc matching: source_kind=%s entries=%d filtered_roles=%s",
        source_kind,
        checked_count,
        sorted(role.value for role in role_filter) if role_filter is not None else None,
    )

    matches: list[tuple[int, CachCuc]] = []
    for index, cach_cuc in enumerate(source_data.cach_cuc):
        outcome = match_condition(cach_cuc.conditions, context)
        _log_checked(index, cach_cuc, outcome)
        if not outcome.matched:
            continue

        raw_match_count += 1
        if _is_filtered_out(outcome, role_filter):
            filtered_out_count += 1
            _log_filtered(index, cach_cuc, outcome, role_filter)
            continue

        matches.append(
            (
                index,
                cach_cuc.model_copy(
                    update={"related_roles": list(outcome.related_roles)}
                ),
            )
        )

    results = _sort_matches(matches)
    _logger.info(
        "Finished cach_cuc matching: checked=%d matched=%d filtered_out=%d returned=%d",
        checked_count,
        raw_match_count,
        filtered_out_count,
        len(results),
    )
    return results


def _log_checked(index: int, cach_cuc: CachCuc, outcome: MatchOutcome) -> None:
    _logger.debug(
        "Checked cach_cuc[%d]: id=%s matched=%s related_roles=%s",
        index,
        cach_cuc.id,
        outcome.matched,
        [role.value for role in outcome.related_roles],
    )


def _is_filtered_out(
    outcome: MatchOutcome,
    role_filter: set[Role] | None,
) -> bool:
    if role_filter is None or not outcome.related_roles:
        return False
    return role_filter.isdisjoint(outcome.related_roles)


def _log_filtered(
    index: int,
    cach_cuc: CachCuc,
    outcome: MatchOutcome,
    role_filter: set[Role] | None,
) -> None:
    _logger.debug(
        "Filtered matched cach_cuc[%d]: id=%s related_roles=%s filtered_roles=%s",
        index,
        cach_cuc.id,
        [role.value for role in outcome.related_roles],
        sorted(role.value for role in role_filter or ()),
    )


def _sort_matches(matches: list[tuple[int, CachCuc]]) -> list[CachCuc]:
    return [
        cach_cuc
        for _, cach_cuc in sorted(
            matches,
            key=lambda item: (-item[1].priority, item[0]),
        )
    ]


def get_cach_cuc_tool_results(
    la_so: LaSo,
    *,
    source_kind: SourceKind = SourceKind.TUVITANBIEN,
    filtered_roles: list[Role] | None = None,
) -> list[CachCucToolResult]:
    """Return agent-facing cach_cuc summaries without exposing conditions."""
    results = [
        CachCucToolResult.from_cach_cuc(cach_cuc)
        for cach_cuc in find_matching_cach_cuc(
            la_so,
            source_kind=source_kind,
            filtered_roles=filtered_roles,
        )
    ]
    _logger.info("Projected cach_cuc tool results: returned=%d", len(results))
    return results


__all__ = [
    "CachCucMatchContext",
    "MatchOutcome",
    "NHI_HOP_PAIRS",
    "STAR_ALIASES",
    "_match_count",
    "_match_only_chinh_tinh",
    "_match_star_brightness",
    "_match_stars_meeting",
    "_match_supported_stars",
    "_resolve_condition_stars",
    "_star_at_any_chi",
    "find_matching_cach_cuc",
    "get_cach_cuc_tool_results",
    "match_condition",
    "merge_related_roles",
    "positions_for_scope",
]
