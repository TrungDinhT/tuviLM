"""Condition-tree evaluator for cach_cuc matching."""

from __future__ import annotations

from src.agent.tool.cach_cuc.evaluator.context import CachCucMatchContext
from src.agent.tool.cach_cuc.evaluator.match_types import (
    MatchOutcome,
    merge_related_roles,
)
from src.agent.tool.cach_cuc.models import (
    AllCondition,
    AnyCondition,
    CanExcludeCondition,
    CanMatchCondition,
    Condition,
    CungThanAtPalaceCondition,
    GenderMatchCondition,
    NotCondition,
    OnlyChinhTinhCondition,
    PalaceAtCondition,
    Role,
    StarAtChiCondition,
    StarBrightnessCondition,
    StarWithPalaceCondition,
    StarsMeetingCondition,
)
from src.agent.tool.cach_cuc.evaluator.scopes import positions_for_scope
from src.agent.tool.cach_cuc.evaluator.star_conditions import (
    _match_only_chinh_tinh,
    _match_star_at_chi,
    _match_star_brightness,
    _match_stars_meeting_outcome,
    _match_supported_stars,
    _star_at_any_chi,
)
from src.refactored.model.prior import Gender as PriorGender


def match_condition(
    condition: Condition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    """Evaluate one normalized condition node.

    Logical nodes keep role order from YAML. ``any`` evaluates every child so all
    matched branch roles can be returned instead of the first matching branch only.
    """
    if isinstance(condition, AllCondition):
        return _match_all(condition, context)
    if isinstance(condition, AnyCondition):
        return _match_any(condition, context)
    if isinstance(condition, NotCondition):
        return MatchOutcome(not match_condition(condition.not_, context).matched)

    if isinstance(condition, CanMatchCondition):
        return MatchOutcome(context.la_so.prior.thien_can in condition.can)
    if isinstance(condition, CanExcludeCondition):
        return MatchOutcome(context.la_so.prior.thien_can not in condition.can)
    if isinstance(condition, GenderMatchCondition):
        return _match_gender(condition, context)
    if isinstance(condition, PalaceAtCondition):
        return _match_palace_at(condition, context)
    if isinstance(condition, CungThanAtPalaceCondition):
        return _match_cung_than_at_palace(condition, context)

    if isinstance(condition, OnlyChinhTinhCondition):
        return _match_only_chinh_tinh(condition, context)
    if isinstance(condition, StarBrightnessCondition):
        return MatchOutcome(_match_star_brightness(condition, context))
    if isinstance(condition, StarAtChiCondition):
        return _match_star_at_chi(condition, context)
    if isinstance(condition, StarWithPalaceCondition):
        return _match_star_with_palace(condition, context)
    if isinstance(condition, StarsMeetingCondition):
        return _match_stars_meeting_outcome(condition, context)

    raise TypeError(f"Unsupported cach_cuc condition: {condition!r}")


def _match_all(
    condition: AllCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    related_roles: tuple[Role, ...] = ()
    for child in condition.all_:
        outcome = match_condition(child, context)
        if not outcome.matched:
            return MatchOutcome(False)
        related_roles = merge_related_roles(related_roles, outcome.related_roles)
    return MatchOutcome(True, related_roles)


def _match_any(
    condition: AnyCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    related_roles: tuple[Role, ...] = ()
    matched = False
    for child in condition.any_:
        outcome = match_condition(child, context)
        if outcome.matched:
            matched = True
            related_roles = merge_related_roles(related_roles, outcome.related_roles)
    return MatchOutcome(matched, related_roles if matched else ())


def _match_gender(
    condition: GenderMatchCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    gender = "male" if context.la_so.prior.gender is PriorGender.MALE else "female"
    return MatchOutcome(gender == condition.gender)


def _match_palace_at(
    condition: PalaceAtCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    matched = context.position_of_role(condition.palace) in condition.chi
    return MatchOutcome(matched, (condition.palace,) if matched else ())


def _match_cung_than_at_palace(
    condition: CungThanAtPalaceCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    matched = context.position_of_role(Role.CUNG_THAN) == context.position_of_role(
        condition.palace
    )
    return MatchOutcome(matched, (condition.palace,) if matched else ())


def _match_star_with_palace(
    condition: StarWithPalaceCondition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    anchor = context.position_of_role(condition.palace)
    scope_positions = positions_for_scope(anchor, condition.scope)
    matched = _match_supported_stars(
        condition,
        context,
        lambda star_id: _star_at_any_chi(star_id, scope_positions, context),
        explicit_mode=condition.stars_matching_logic,
    )
    return MatchOutcome(matched, (condition.palace,) if matched else ())
