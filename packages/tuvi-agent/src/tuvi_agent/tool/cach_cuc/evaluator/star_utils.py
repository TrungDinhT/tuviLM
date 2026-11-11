"""Shared helpers for cach_cuc star condition matching."""

from __future__ import annotations

from typing import Callable, Iterable

from pydantic_ai import ModelRetry

from src.agent.tool.cach_cuc.evaluator.context import CachCucMatchContext
from src.agent.tool.cach_cuc.evaluator.match_types import merge_related_roles
from src.agent.tool.cach_cuc.models import GroupSupportMixin, Mode, Role
from src.refactored.model.elementary import DiaChi


def _match_supported_stars(
    condition: GroupSupportMixin,
    context: CachCucMatchContext,
    predicate: Callable[[str], bool],
    *,
    explicit_mode: Mode | None,
) -> bool:
    """Apply explicit-star and group matching rules to a star predicate.

    Explicit stars and named groups are independent clauses. When both are
    authored, both clauses must pass.
    """
    if not _match_explicit_stars(condition, predicate, explicit_mode=explicit_mode):
        return False
    if not _match_group_stars(condition, context, predicate):
        return False
    return bool(getattr(condition, "stars", [])) or condition.group_name is not None


def _match_explicit_stars(
    condition: GroupSupportMixin,
    predicate: Callable[[str], bool],
    *,
    explicit_mode: Mode | None,
) -> bool:
    explicit_stars = list(getattr(condition, "stars", []))
    if not explicit_stars:
        return True
    matched_count = sum(1 for star_id in explicit_stars if predicate(star_id))
    return _match_count(
        matched_count,
        len(explicit_stars),
        mode=explicit_mode or "any",
        at_least=None,
    )


def _match_group_stars(
    condition: GroupSupportMixin,
    context: CachCucMatchContext,
    predicate: Callable[[str], bool],
) -> bool:
    if condition.group_name is None:
        return True
    stars = _resolve_group_stars(condition, context)
    if not stars:
        return False
    matched_count = sum(1 for star_id in stars if predicate(star_id))
    return _match_count(
        matched_count,
        len(stars),
        mode=condition.mode,
        at_least=condition.at_least,
    )


def _resolve_condition_stars(
    condition: GroupSupportMixin,
    context: CachCucMatchContext,
) -> list[str]:
    """Resolve a condition's explicit stars or named group into concrete ids."""
    if condition.group_name is None:
        return list(getattr(condition, "stars", []))
    return _resolve_group_stars(condition, context)


def _resolve_group_stars(
    condition: GroupSupportMixin,
    context: CachCucMatchContext,
) -> list[str]:
    """Resolve only the named group stars for a grouped condition."""
    if condition.group_name is None:
        return []
    try:
        return context.data.groups[condition.group_name].stars
    except KeyError as exc:
        raise ModelRetry(f"Khong tim thay nhom sao {condition.group_name}.") from exc


def _match_count(
    matched_count: int,
    total_count: int,
    *,
    mode: Mode | None,
    at_least: int | None,
) -> bool:
    """Evaluate count semantics shared by explicit-star and group checks."""
    if total_count == 0:
        return False
    if at_least is not None:
        return matched_count >= at_least
    if mode == "all":
        return matched_count == total_count
    return matched_count > 0


def _star_at_any_chi(
    star_id: str,
    positions: Iterable[DiaChi],
    context: CachCucMatchContext,
) -> bool:
    """Return true if any alias-expanded star position is in the target set."""
    position_set = set(positions)
    return any(
        position in position_set for position in context.positions_of_star(star_id)
    )


def _star_positions_at_any_chi(
    star_id: str,
    positions: Iterable[DiaChi],
    context: CachCucMatchContext,
) -> tuple[DiaChi, ...]:
    """Return alias-expanded star positions that are in the target set."""
    position_set = set(positions)
    return tuple(
        position
        for position in context.positions_of_star(star_id)
        if position in position_set
    )


def _roles_for_positions(
    positions: Iterable[DiaChi],
    context: CachCucMatchContext,
) -> tuple[Role, ...]:
    """Return all roles attached to positions while preserving encounter order."""
    return merge_related_roles(
        *(context.roles_at_position(position) for position in positions)
    )
