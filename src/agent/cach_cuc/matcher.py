"""Runtime matcher for cach_cuc condition trees.

This module intentionally lives in ``src.agent`` because the cach_cuc search is an
agent tool concern: it evaluates a currently loaded ``LaSo`` and returns a compact
list of applicable configurations for the model to consider.

Maintenance notes for the error-prone parts:
- ``related_roles`` is not persisted in YAML. It is inferred from matched
  positive role-bearing conditions in YAML order.
- ``not`` conditions never contribute ``related_roles``. They only validate absence.
- ``star_with_palace`` explicit star lists use ``stars_matching_logic`` and
  groups use ``mode``/``at_least``. When both explicit stars and ``group_name``
  are authored, both checks must match.
- For ``star_at_chi`` and ``stars_meeting``, explicit star lists always require
  all listed stars to match. Group conditions use ``mode``/``at_least`` from
  ``GroupSupportMixin``.
- ``stars_meeting`` is anchor-based: any listed star can be the anchor, but one
  anchor scope must contain every required explicit star, or enough group stars
  for the group ``mode``/``at_least`` rule. When explicit stars and a group are
  both authored, explicit stars are the anchor candidates and the group is
  checked against those anchors.
- ``tuan`` and ``triet`` are logical ids in cach_cuc data, but split marker ids in
  the chart. Keep the alias table in sync with catalog marker ids.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable, Iterable

from pydantic_ai import ModelRetry

from src.agent.cach_cuc.loader import load_cach_cuc_source
from src.agent.cach_cuc.models import (
    AllCondition,
    AnyCondition,
    CachCuc,
    CachCucData,
    CachCucToolResult,
    CanExcludeCondition,
    CanMatchCondition,
    Condition,
    CungThanAtPalaceCondition,
    GenderMatchCondition,
    GroupSupportMixin,
    Mode,
    NotCondition,
    OnlyChinhTinhCondition,
    PalaceAtCondition,
    Role,
    SourceKind,
    StarAtChiCondition,
    StarBrightnessCondition,
    StarWithPalaceCondition,
    StarsMeetingCondition,
)
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import ChinhPhuTinh, Status
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.model.prior import Gender as PriorGender


_logger = logging.getLogger(__name__)


STAR_ALIASES: dict[str, tuple[str, ...]] = {
    "tuan": ("tuan_1", "tuan_2"),
    "triet": ("triet_1", "triet_2"),
}


NHI_HOP_PAIRS: dict[DiaChi, DiaChi] = {
    DiaChi.TY: DiaChi.SUU,
    DiaChi.SUU: DiaChi.TY,
    DiaChi.DAN: DiaChi.HOI,
    DiaChi.HOI: DiaChi.DAN,
    DiaChi.MEO: DiaChi.TUAT,
    DiaChi.TUAT: DiaChi.MEO,
    DiaChi.THIN: DiaChi.DAU,
    DiaChi.DAU: DiaChi.THIN,
    DiaChi.TI: DiaChi.THAN,
    DiaChi.THAN: DiaChi.TI,
    DiaChi.NGO: DiaChi.MUI,
    DiaChi.MUI: DiaChi.NGO,
}


STATUS_TO_BRIGHTNESS: dict[Status, str] = {
    Status.MIEU: "mieu",
    Status.VUONG: "vuong",
    Status.DAC: "dac",
    Status.BINH: "binh hoa",
    Status.HAM: "ham",
}


@dataclass(frozen=True)
class MatchOutcome:
    """Boolean condition result plus roles inferred for filtering."""

    matched: bool
    related_roles: tuple[Role, ...] = ()


def merge_related_roles(*role_groups: Iterable[Role]) -> tuple[Role, ...]:
    """Merge role groups while preserving first-seen YAML order."""
    roles: list[Role] = []
    for role_group in role_groups:
        for role in role_group:
            if role not in roles:
                roles.append(role)
    return tuple(roles)


@dataclass(frozen=True)
class CachCucMatchContext:
    """Precomputed access layer around a ``LaSo`` for condition evaluation."""

    la_so: LaSo
    data: CachCucData
    star_aliases: dict[str, tuple[str, ...]]

    @classmethod
    def from_la_so(
        cls,
        la_so: LaSo,
        data: CachCucData,
        star_aliases: dict[str, tuple[str, ...]] | None = None,
    ) -> CachCucMatchContext:
        return cls(
            la_so=la_so,
            data=data,
            star_aliases=star_aliases or STAR_ALIASES,
        )

    def position_of_role(self, role: Role) -> DiaChi:
        """Return a role position or fail loudly for malformed chart state."""
        position = self.la_so.position_of(role.value, NATAL_LAYER_ID)
        if position is None:
            raise ModelRetry(f"Khong tim thay vi tri cung {role.value}.")
        return position

    def positions_of_star(self, star_id: str) -> tuple[DiaChi, ...]:
        """Return all natal positions for a star id, expanding logical aliases."""
        positions: list[DiaChi] = []
        for resolved_id in self.star_aliases.get(star_id, (star_id,)):
            position = self.la_so.position_of(resolved_id, NATAL_LAYER_ID)
            if position is not None and position not in positions:
                positions.append(position)
        return tuple(positions)

    def roles_at_position(self, position: DiaChi) -> tuple[Role, ...]:
        """Return natal and structural roles attached to one position."""
        cung = self.la_so.cung_at(position)
        roles = [cung.natal_role]
        if cung.is_cung_than and Role.CUNG_THAN not in roles:
            roles.append(Role.CUNG_THAN)
        return tuple(roles)


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
        _logger.debug(
            "Checked cach_cuc[%d]: id=%s matched=%s related_roles=%s",
            index,
            cach_cuc.id,
            outcome.matched,
            [role.value for role in outcome.related_roles],
        )
        if not outcome.matched:
            continue
        raw_match_count += 1
        if (
            role_filter is not None
            and outcome.related_roles
            and role_filter.isdisjoint(outcome.related_roles)
        ):
            filtered_out_count += 1
            _logger.debug(
                "Filtered matched cach_cuc[%d]: id=%s related_roles=%s filtered_roles=%s",
                index,
                cach_cuc.id,
                [role.value for role in outcome.related_roles],
                sorted(role.value for role in role_filter),
            )
            continue
        matches.append(
            (
                index,
                cach_cuc.model_copy(
                    update={"related_roles": list(outcome.related_roles)}
                ),
            )
        )

    results = [
        cach_cuc
        for _, cach_cuc in sorted(
            matches,
            key=lambda item: (-item[1].priority, item[0]),
        )
    ]
    _logger.info(
        "Finished cach_cuc matching: checked=%d matched=%d filtered_out=%d returned=%d",
        checked_count,
        raw_match_count,
        filtered_out_count,
        len(results),
    )
    return results


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


def match_condition(
    condition: Condition,
    context: CachCucMatchContext,
) -> MatchOutcome:
    """Evaluate one normalized condition node.

    Logical nodes keep role order from YAML. ``any`` evaluates every child so all
    matched branch roles can be returned instead of the first matching branch only.
    """
    if isinstance(condition, AllCondition):
        related_roles: tuple[Role, ...] = ()
        for child in condition.all_:
            outcome = match_condition(child, context)
            if not outcome.matched:
                return MatchOutcome(False)
            related_roles = merge_related_roles(related_roles, outcome.related_roles)
        return MatchOutcome(True, related_roles)

    if isinstance(condition, AnyCondition):
        related_roles: tuple[Role, ...] = ()
        matched = False
        for child in condition.any_:
            outcome = match_condition(child, context)
            if outcome.matched:
                matched = True
                related_roles = merge_related_roles(related_roles, outcome.related_roles)
        return MatchOutcome(matched, related_roles if matched else ())

    if isinstance(condition, NotCondition):
        return MatchOutcome(not match_condition(condition.not_, context).matched)

    if isinstance(condition, CanMatchCondition):
        return MatchOutcome(context.la_so.prior.thien_can in condition.can)

    if isinstance(condition, CanExcludeCondition):
        return MatchOutcome(context.la_so.prior.thien_can not in condition.can)

    if isinstance(condition, GenderMatchCondition):
        gender = "male" if context.la_so.prior.gender is PriorGender.MALE else "female"
        return MatchOutcome(gender == condition.gender)

    if isinstance(condition, PalaceAtCondition):
        matched = context.position_of_role(condition.palace) in condition.chi
        return MatchOutcome(matched, (condition.palace,) if matched else ())

    if isinstance(condition, CungThanAtPalaceCondition):
        matched = context.position_of_role(Role.CUNG_THAN) == context.position_of_role(
            condition.palace
        )
        return MatchOutcome(matched, (condition.palace,) if matched else ())

    if isinstance(condition, OnlyChinhTinhCondition):
        return _match_only_chinh_tinh(condition, context)

    if isinstance(condition, StarBrightnessCondition):
        return MatchOutcome(_match_star_brightness(condition, context))

    if isinstance(condition, StarAtChiCondition):
        return _match_star_at_chi(condition, context)

    if isinstance(condition, StarWithPalaceCondition):
        anchor = context.position_of_role(condition.palace)
        scope_positions = positions_for_scope(anchor, condition.scope)
        matched = _match_supported_stars(
            condition,
            context,
            lambda star_id: _star_at_any_chi(star_id, scope_positions, context),
            explicit_mode=condition.stars_matching_logic,
        )
        return MatchOutcome(matched, (condition.palace,) if matched else ())

    if isinstance(condition, StarsMeetingCondition):
        return _match_stars_meeting_outcome(condition, context)

    raise TypeError(f"Unsupported cach_cuc condition: {condition!r}")


def positions_for_scope(anchor: DiaChi, scope: str) -> frozenset[DiaChi]:
    """Expand a scope name into concrete positions relative to an anchor."""
    if scope == "dong_cung":
        return frozenset((anchor,))
    if scope == "xung_chieu":
        return frozenset((anchor + 6,))
    if scope == "dong_hoac_xung":
        return frozenset((anchor, anchor + 6))
    if scope == "tam_hop":
        return frozenset((anchor, anchor + 4, anchor + 8))
    if scope == "hoi_hop":
        return frozenset((anchor, anchor + 4, anchor + 8, anchor + 6))
    if scope == "giap":
        return frozenset((anchor - 1, anchor + 1))
    if scope == "nhi_hop":
        return frozenset((NHI_HOP_PAIRS[anchor],))
    raise ValueError(f"Unsupported cach_cuc scope: {scope}")


def _match_supported_stars(
    condition: GroupSupportMixin,
    context: CachCucMatchContext,
    predicate: Callable[[str], bool],
    *,
    explicit_mode: Mode | None,
) -> bool:
    """Apply explicit-star or group matching rules to a star predicate.

    ``star_with_palace`` passes its authored ``stars_matching_logic`` here.
    ``star_at_chi`` passes ``all`` for explicit stars. Group conditions use
    ``mode``/``at_least`` because a group is an open set defined by the YAML
    source. When a condition has both explicit stars and a group, both sides
    must pass.
    """
    explicit_stars = list(getattr(condition, "stars", []))
    has_matchable_clause = False
    if explicit_stars:
        has_matchable_clause = True
        explicit_matched_count = sum(
            1 for star_id in explicit_stars if predicate(star_id)
        )
        if not _match_count(
            explicit_matched_count,
            len(explicit_stars),
            mode=explicit_mode or "any",
            at_least=None,
        ):
            return False

    if condition.group_name is not None:
        has_matchable_clause = True
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

    return has_matchable_clause


def _resolve_condition_stars(
    condition: GroupSupportMixin,
    context: CachCucMatchContext,
) -> list[str]:
    """Resolve a condition's explicit stars or named group into concrete ids."""
    if condition.group_name is None:
        return list(getattr(condition, "stars", []))
    try:
        return context.data.groups[condition.group_name].stars
    except KeyError as exc:
        raise ModelRetry(f"Khong tim thay nhom sao {condition.group_name}.") from exc


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
    return any(position in position_set for position in context.positions_of_star(star_id))


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
        if not _match_count(
            sum(1 for positions in explicit_matches if positions),
            len(explicit_stars),
            mode="all",
            at_least=None,
        ):
            return MatchOutcome(False)
        for positions in explicit_matches:
            matched_positions.extend(positions)

    if condition.group_name is not None:
        has_matchable_clause = True
        group_stars = _resolve_group_stars(condition, context)
        if not group_stars:
            return MatchOutcome(False)
        group_matches = [
            _star_positions_at_any_chi(star_id, condition.at_chi, context)
            for star_id in group_stars
        ]
        if not _match_count(
            sum(1 for positions in group_matches if positions),
            len(group_stars),
            mode=condition.mode,
            at_least=condition.at_least,
        ):
            return MatchOutcome(False)
        for positions in group_matches:
            matched_positions.extend(positions)

    if not has_matchable_clause:
        return MatchOutcome(False)
    return MatchOutcome(True, _roles_for_positions(matched_positions, context))


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
    """Evaluate star meeting and infer roles from matched anchor positions.

    A meeting is not just disconnected pairwise contact. One candidate anchor
    must relate to every required explicit star, or to enough group members for
    the group condition. The anchor itself counts as present even for scopes like
    ``xung_chieu`` and ``giap`` whose related positions do not include the
    anchor position. If explicit stars and a group are both present, explicit
    stars are anchors and group members are the related stars to count.
    """
    explicit_stars = list(condition.stars)
    group_stars = _resolve_group_stars(condition, context)
    anchor_stars = explicit_stars or group_stars
    if not anchor_stars:
        return MatchOutcome(False)

    explicit_positions = {
        star_id: positions
        for star_id in explicit_stars
        if (positions := context.positions_of_star(star_id))
    }
    group_positions = {
        star_id: positions
        for star_id in group_stars
        if (positions := context.positions_of_star(star_id))
    }
    anchor_positions_by_star = {
        star_id: positions
        for star_id in anchor_stars
        if (positions := context.positions_of_star(star_id))
    }

    if explicit_stars and condition.group_name is None and len(explicit_positions) < 2:
        return MatchOutcome(False)
    if not explicit_stars and len(group_positions) < 2:
        return MatchOutcome(False)

    matched_anchor_positions: list[DiaChi] = []
    for anchor_id, anchor_positions in anchor_positions_by_star.items():
        for anchor_position in anchor_positions:
            scope_positions = positions_for_scope(anchor_position, condition.scope)

            if explicit_stars:
                explicit_related_count = _count_stars_related_to_anchor(
                    explicit_positions,
                    anchor_id=anchor_id,
                    scope_positions=scope_positions,
                    count_anchor_self=True,
                )
                if not _match_count(
                    explicit_related_count,
                    len(explicit_stars),
                    mode="all",
                    at_least=None,
                ):
                    continue

            if condition.group_name is None:
                matched_anchor_positions.append(anchor_position)
                continue

            group_related_count = _count_stars_related_to_anchor(
                group_positions,
                anchor_id=anchor_id,
                scope_positions=scope_positions,
                count_anchor_self=not explicit_stars,
            )
            group_matched = _match_count(
                group_related_count,
                len(group_stars),
                mode=condition.mode,
                at_least=condition.at_least,
            )
            if (
                not explicit_stars
                and condition.at_least is None
                and condition.mode == "any"
            ):
                group_matched = group_related_count >= 2
            if group_matched:
                matched_anchor_positions.append(anchor_position)

    return MatchOutcome(
        bool(matched_anchor_positions),
        _roles_for_positions(matched_anchor_positions, context),
    )


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
