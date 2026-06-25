from __future__ import annotations

from dataclasses import dataclass

import pytest
from pydantic import ValidationError
from pydantic_ai import ModelRetry

from src.agent.cach_cuc import matcher as matcher_module
from src.agent.cach_cuc.matcher import (
    CachCucMatchContext,
    MatchOutcome,
    _match_count,
    _match_only_chinh_tinh,
    _match_star_brightness,
    _match_stars_meeting,
    _match_supported_stars,
    _resolve_condition_stars,
    _star_at_any_chi,
    find_matching_cach_cuc,
    get_cach_cuc_tool_results,
    match_condition,
    positions_for_scope,
)
from src.agent.cach_cuc.models import (
    CachCucData,
    Role,
    StarBrightnessCondition,
    StarWithPalaceCondition,
    StarsMeetingCondition,
)
from src.refactored.components.definitions.sao import ChinhPhuTinh
from src.refactored.model.cung import Cung, LayeredComponent
from src.refactored.model.elementary import DiaChi, NguHanh, ThienCan
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.model.prior import Gender


@dataclass(frozen=True)
class _Prior:
    thien_can: ThienCan = ThienCan.CANH
    gender: Gender = Gender.MALE


class _CatalogLaSo:
    """Small LaSo double with enough behavior for matcher unit tests."""

    prior = _Prior()

    def __init__(
        self,
        *,
        star_positions: dict[str, DiaChi] | None = None,
        role_positions: dict[Role, DiaChi] | None = None,
        palace_components: dict[DiaChi, tuple[str, ...]] | None = None,
        components: dict[str, object] | None = None,
    ) -> None:
        self._star_positions = star_positions or {}
        self._role_positions = {
            Role.MENH.value: DiaChi.TY,
            Role.CUNG_THAN.value: DiaChi.TY,
            Role.QUAN_LOC.value: DiaChi.THIN,
            Role.THIEN_DI.value: DiaChi.NGO,
        }
        if role_positions:
            self._role_positions.update(
                {role.value: position for role, position in role_positions.items()}
            )
        self._palace_components = palace_components or {}
        self._components = components or {}

    def position_of(self, component_id: str, layer_id=NATAL_LAYER_ID) -> DiaChi | None:
        if layer_id != NATAL_LAYER_ID:
            return None
        return self._role_positions.get(component_id) or self._star_positions.get(
            component_id
        )

    def cung_at(self, dia_chi: DiaChi, layer_ids=(NATAL_LAYER_ID,)) -> Cung:
        return Cung(
            dia_chi=dia_chi,
            thien_can=ThienCan.GIAP,
            natal_role=Role.MENH,
            is_cung_than=dia_chi == self._role_positions[Role.CUNG_THAN.value],
            components=tuple(
                LayeredComponent(layer_id=NATAL_LAYER_ID, component_id=component_id)
                for component_id in self._palace_components.get(dia_chi, ())
            ),
        )

    def component(self, component_id: str) -> object:
        return self._components[component_id]


def _data(entries: list[dict] | None = None) -> CachCucData:
    return CachCucData.model_validate(
        {
            "groups": {
                "luc_sat": {
                    "stars": ["dia_khong", "dia_kiep", "hoa_tinh"],
                }
            },
            "cach_cuc": entries or [],
        }
    )


def _context(la_so: _CatalogLaSo | None = None) -> CachCucMatchContext:
    return CachCucMatchContext.from_la_so(la_so or _CatalogLaSo(), _data())


def _entry(
    cc_id: str,
    condition: dict,
    *,
    priority: int = 0,
) -> dict:
    return {
        "id": cc_id,
        "name": cc_id,
        "page": 1,
        "priority": priority,
        "meaning": cc_id,
        "conditions": condition,
    }


def test_context_resolves_roles_and_alias_positions():
    context = _context(
        _CatalogLaSo(
            star_positions={
                "tuan_1": DiaChi.TY,
                "tuan_2": DiaChi.SUU,
                "van_xuong": DiaChi.NGO,
            }
        )
    )

    assert context.position_of_role(Role.MENH) is DiaChi.TY
    assert context.positions_of_star("tuan") == (DiaChi.TY, DiaChi.SUU)
    assert context.positions_of_star("van_xuong") == (DiaChi.NGO,)
    assert context.positions_of_star("missing") == ()


def test_context_missing_role_raises_model_retry():
    context = _context(_CatalogLaSo(role_positions={Role.MENH: DiaChi.TY}))
    context.la_so._role_positions.pop(Role.QUAN_LOC.value)

    with pytest.raises(ModelRetry):
        context.position_of_role(Role.QUAN_LOC)


def test_positions_for_scope_covers_all_scopes():
    assert positions_for_scope(DiaChi.TY, "dong_cung") == frozenset({DiaChi.TY})
    assert positions_for_scope(DiaChi.TY, "xung_chieu") == frozenset({DiaChi.NGO})
    assert positions_for_scope(DiaChi.TY, "dong_hoac_xung") == frozenset(
        {DiaChi.TY, DiaChi.NGO}
    )
    assert positions_for_scope(DiaChi.TY, "tam_hop") == frozenset(
        {DiaChi.TY, DiaChi.THIN, DiaChi.THAN}
    )
    assert positions_for_scope(DiaChi.TY, "hoi_hop") == frozenset(
        {DiaChi.TY, DiaChi.THIN, DiaChi.THAN, DiaChi.NGO}
    )
    assert positions_for_scope(DiaChi.TY, "giap") == frozenset(
        {DiaChi.HOI, DiaChi.SUU}
    )
    assert positions_for_scope(DiaChi.TY, "nhi_hop") == frozenset({DiaChi.SUU})


def test_positions_for_scope_rejects_unknown_scope():
    with pytest.raises(ValueError):
        positions_for_scope(DiaChi.TY, "bad_scope")


@pytest.mark.parametrize(
    ("matched_count", "total_count", "mode", "at_least", "expected"),
    [
        (0, 0, "any", None, False),
        (1, 3, "any", None, True),
        (0, 3, "any", None, False),
        (3, 3, "all", None, True),
        (2, 3, "all", None, False),
        (2, 3, None, 2, True),
        (1, 3, None, 2, False),
    ],
)
def test_match_count(
    matched_count: int,
    total_count: int,
    mode: str | None,
    at_least: int | None,
    expected: bool,
):
    assert (
        _match_count(
            matched_count,
            total_count,
            mode=mode,
            at_least=at_least,
        )
        is expected
    )


def test_resolve_condition_stars_returns_explicit_or_group_stars():
    context = _context()
    explicit = StarWithPalaceCondition.model_validate(
        {
            "type": "star_with_palace",
            "palace": "menh",
            "scope": "dong_cung",
            "stars": ["thien_ma"],
        }
    )
    grouped = StarWithPalaceCondition.model_validate(
        {
            "type": "star_with_palace",
            "palace": "menh",
            "scope": "dong_cung",
            "group_name": "luc_sat",
            "mode": "any",
        }
    )

    assert _resolve_condition_stars(explicit, context) == ["thien_ma"]
    assert _resolve_condition_stars(grouped, context) == [
        "dia_khong",
        "dia_kiep",
        "hoa_tinh",
    ]


def test_resolve_condition_stars_unknown_group_raises_model_retry():
    condition = StarWithPalaceCondition.model_validate(
        {
            "type": "star_with_palace",
            "palace": "menh",
            "scope": "dong_cung",
            "group_name": "sat_tinh",
            "mode": "any",
        }
    )

    with pytest.raises(ModelRetry):
        _resolve_condition_stars(condition, _context())


def test_match_supported_stars_uses_explicit_logic_and_group_threshold():
    context = _context()
    explicit = StarWithPalaceCondition.model_validate(
        {
            "type": "star_with_palace",
            "palace": "menh",
            "scope": "dong_cung",
            "stars": ["a", "b"],
            "stars_matching_logic": "all",
        }
    )
    grouped = StarWithPalaceCondition.model_validate(
        {
            "type": "star_with_palace",
            "palace": "menh",
            "scope": "dong_cung",
            "group_name": "luc_sat",
            "at_least": 2,
        }
    )

    assert (
        _match_supported_stars(
            explicit,
            context,
            lambda star_id: star_id == "a",
            explicit_mode=explicit.stars_matching_logic,
        )
        is False
    )
    assert (
        _match_supported_stars(
            grouped,
            context,
            lambda star_id: star_id in {"dia_khong", "hoa_tinh"},
            explicit_mode=None,
        )
        is True
    )


def test_star_at_chi_explicit_stars_always_require_all_even_if_any_is_authored():
    context = _context(_CatalogLaSo(star_positions={"a": DiaChi.TY}))
    condition = _data(
        [
            _entry(
                "star_at_chi",
                {
                    "type": "star_at_chi",
                    "stars": ["a", "b"],
                    "stars_matching_logic": "any",
                    "at_chi": ["ty"],
                },
            )
        ]
    ).cach_cuc[0].conditions

    assert match_condition(condition, context) == MatchOutcome(False)


def test_star_with_palace_respects_stars_matching_logic():
    context = _context(_CatalogLaSo(star_positions={"a": DiaChi.TY}))
    any_condition = _data(
        [
            _entry(
                "star_with_palace_any",
                {
                    "type": "star_with_palace",
                    "palace": "menh",
                    "scope": "dong_cung",
                    "stars": ["a", "b"],
                    "stars_matching_logic": "any",
                },
            )
        ]
    ).cach_cuc[0].conditions
    all_condition = _data(
        [
            _entry(
                "star_with_palace_all",
                {
                    "type": "star_with_palace",
                    "palace": "menh",
                    "scope": "dong_cung",
                    "stars": ["a", "b"],
                    "stars_matching_logic": "all",
                },
            )
        ]
    ).cach_cuc[0].conditions

    assert match_condition(any_condition, context) == MatchOutcome(True, Role.MENH)
    assert match_condition(all_condition, context) == MatchOutcome(False)


def test_star_with_palace_requires_explicit_stars_and_group_when_both_authored():
    condition = _data(
        [
            _entry(
                "explicit_and_group",
                {
                    "type": "star_with_palace",
                    "palace": "menh",
                    "scope": "hoi_hop",
                    "stars": ["hoa_loc", "hoa_quyen"],
                    "stars_matching_logic": "all",
                    "group_name": "luc_sat",
                    "mode": "all",
                },
            )
        ]
    ).cach_cuc[0].conditions
    assert isinstance(condition, StarWithPalaceCondition)
    assert condition.stars_matching_logic == "all"

    both_pass = _context(
        _CatalogLaSo(
            star_positions={
                "hoa_loc": DiaChi.TY,
                "hoa_quyen": DiaChi.NGO,
                "dia_khong": DiaChi.TY,
                "dia_kiep": DiaChi.THIN,
                "hoa_tinh": DiaChi.THAN,
            }
        )
    )
    explicit_fails = _context(
        _CatalogLaSo(
            star_positions={
                "hoa_loc": DiaChi.TY,
                "dia_khong": DiaChi.TY,
                "dia_kiep": DiaChi.THIN,
                "hoa_tinh": DiaChi.THAN,
            }
        )
    )
    group_fails = _context(
        _CatalogLaSo(
            star_positions={
                "hoa_loc": DiaChi.TY,
                "hoa_quyen": DiaChi.NGO,
                "dia_khong": DiaChi.TY,
                "hoa_tinh": DiaChi.THAN,
            }
        )
    )

    assert match_condition(condition, both_pass) == MatchOutcome(True, Role.MENH)
    assert match_condition(condition, explicit_fails) == MatchOutcome(False)
    assert match_condition(condition, group_fails) == MatchOutcome(False)


def test_star_at_any_chi_expands_alias_positions():
    context = _context(
        _CatalogLaSo(star_positions={"tuan_1": DiaChi.TY, "tuan_2": DiaChi.SUU})
    )

    assert _star_at_any_chi("tuan", [DiaChi.SUU], context) is True
    assert _star_at_any_chi("tuan", [DiaChi.NGO], context) is False


def test_match_stars_meeting_explicit_stars_always_require_all():
    context = _context(
        _CatalogLaSo(
            star_positions={
                "a": DiaChi.TY,
                "b": DiaChi.TY,
                "c": DiaChi.NGO,
            }
        )
    )
    condition = StarsMeetingCondition.model_validate(
        {
            "type": "stars_meeting",
            "scope": "dong_cung",
            "stars": ["a", "b", "c"],
        }
    )

    assert _match_stars_meeting(condition, context) is False


def test_stars_meeting_rejects_stars_matching_logic():
    with pytest.raises(ValidationError):
        StarsMeetingCondition.model_validate(
            {
                "type": "stars_meeting",
                "scope": "dong_cung",
                "stars": ["a", "b"],
                "stars_matching_logic": "any",
            }
        )


def test_match_stars_meeting_rejects_disconnected_pairs():
    context = _context(
        _CatalogLaSo(
            star_positions={
                "a": DiaChi.TY,
                "b": DiaChi.TY,
                "c": DiaChi.NGO,
                "d": DiaChi.NGO,
            }
        )
    )
    condition = StarsMeetingCondition.model_validate(
        {
            "type": "stars_meeting",
            "scope": "dong_cung",
            "stars": ["a", "b", "c", "d"],
        }
    )

    assert _match_stars_meeting(condition, context) is False


def test_match_stars_meeting_accepts_any_star_as_anchor():
    context = _context(
        _CatalogLaSo(
            star_positions={
                "a": DiaChi.TY,
                "b": DiaChi.THIN,
                "c": DiaChi.THAN,
            }
        )
    )
    condition = StarsMeetingCondition.model_validate(
        {
            "type": "stars_meeting",
            "scope": "tam_hop",
            "stars": ["a", "b", "c"],
        }
    )

    assert _match_stars_meeting(condition, context) is True


def test_match_stars_meeting_returns_false_when_fewer_than_two_stars_present():
    condition = StarsMeetingCondition.model_validate(
        {
            "type": "stars_meeting",
            "scope": "dong_cung",
            "stars": ["a", "b"],
        }
    )

    assert _match_stars_meeting(condition, _context(_CatalogLaSo())) is False


def test_match_star_brightness_requires_every_star_to_have_allowed_status():
    bright_context = _context(
        _CatalogLaSo(star_positions={"thai_duong": DiaChi.DAN, "thai_am": DiaChi.TY})
    )
    dim_context = _context(_CatalogLaSo(star_positions={"thai_duong": DiaChi.TY}))
    bright_condition = StarBrightnessCondition.model_validate(
        {
            "type": "star_brightness",
            "stars": ["thai_duong", "thai_am"],
            "brightness": ["mieu"],
        }
    )
    dim_condition = StarBrightnessCondition.model_validate(
        {
            "type": "star_brightness",
            "stars": ["thai_duong"],
            "brightness": ["mieu"],
        }
    )

    assert _match_star_brightness(bright_condition, bright_context) is True
    assert _match_star_brightness(dim_condition, dim_context) is False


def test_match_only_chinh_tinh_requires_exact_single_main_star():
    tu_vi = ChinhPhuTinh(
        id="tu_vi",
        name="Tu Vi",
        ngu_hanh=NguHanh.THO,
        is_chinh_tinh=True,
    )
    thien_phu = ChinhPhuTinh(
        id="thien_phu",
        name="Thien Phu",
        ngu_hanh=NguHanh.THO,
        is_chinh_tinh=True,
    )
    helper = ChinhPhuTinh(
        id="van_xuong",
        name="Van Xuong",
        ngu_hanh=NguHanh.KIM,
        is_chinh_tinh=False,
    )
    condition = {
        "type": "only_chinh_tinh",
        "palace": "menh",
        "star": "tu_vi",
    }

    single_context = _context(
        _CatalogLaSo(
            palace_components={DiaChi.TY: ("tu_vi", "van_xuong")},
            components={"tu_vi": tu_vi, "van_xuong": helper},
        )
    )
    multiple_context = _context(
        _CatalogLaSo(
            palace_components={DiaChi.TY: ("tu_vi", "thien_phu")},
            components={"tu_vi": tu_vi, "thien_phu": thien_phu},
        )
    )

    matched = _match_only_chinh_tinh(
        _data([_entry("only", condition)]).cach_cuc[0].conditions,
        single_context,
    )
    not_matched = _match_only_chinh_tinh(
        _data([_entry("only", condition)]).cach_cuc[0].conditions,
        multiple_context,
    )

    assert matched == MatchOutcome(True, Role.MENH)
    assert not_matched == MatchOutcome(False)


def test_match_condition_covers_all_any_not_and_leaf_conditions():
    context = _context(
        _CatalogLaSo(
            star_positions={
                "thien_ma": DiaChi.TY,
                "loc_ton": DiaChi.NGO,
                "dia_khong": DiaChi.TY,
            }
        )
    )
    condition = {
        "all": [
            {"type": "can_match", "can": ["canh"]},
            {"type": "can_exclude", "can": ["giap"]},
            {"type": "gender_match", "gender": "male"},
            {"type": "palace_at", "palace": "menh", "chi": ["ty"]},
            {"type": "cung_than_at_palace", "palace": "menh"},
            {
                "type": "star_at_chi",
                "stars": ["thien_ma"],
                "at_chi": ["ty"],
            },
            {
                "type": "star_with_palace",
                "palace": "menh",
                "scope": "dong_cung",
                "stars": ["thien_ma"],
            },
            {
                "type": "stars_meeting",
                "scope": "xung_chieu",
                "stars": ["thien_ma", "loc_ton"],
            },
            {
                "not": {
                    "type": "star_with_palace",
                    "palace": "menh",
                    "scope": "dong_cung",
                    "stars": ["tuan"],
                }
            },
            {
                "any": [
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["missing"],
                    },
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["dia_khong"],
                    },
                ]
            },
        ]
    }

    outcome = match_condition(
        _data([_entry("condition", condition)]).cach_cuc[0].conditions,
        context,
    )

    assert outcome == MatchOutcome(True, Role.MENH)


def test_find_matching_cach_cuc_sorts_by_priority_and_filters_roles():
    la_so = _CatalogLaSo(
        star_positions={"a": DiaChi.TY, "b": DiaChi.THIN},
    )
    data = _data(
        [
            _entry(
                "low",
                {
                    "type": "star_with_palace",
                    "palace": "menh",
                    "scope": "dong_cung",
                    "stars": ["a"],
                },
                priority=1,
            ),
            _entry(
                "general",
                {
                    "type": "can_match",
                    "can": ["canh"],
                },
                priority=3,
            ),
            _entry(
                "high",
                {
                    "type": "star_with_palace",
                    "palace": "quan_loc",
                    "scope": "dong_cung",
                    "stars": ["b"],
                },
                priority=5,
            ),
        ]
    )

    all_matches = find_matching_cach_cuc(la_so, data=data)
    filtered = find_matching_cach_cuc(la_so, data=data, filtered_roles=[Role.MENH])

    assert [match.id for match in all_matches] == ["high", "general", "low"]
    assert all_matches[0].related_to is Role.QUAN_LOC
    assert all_matches[1].related_to is None
    assert [match.id for match in filtered] == ["general", "low"]


def test_get_cach_cuc_tool_results_projects_without_conditions(monkeypatch):
    matched = _data(
        [
            _entry(
                "tool",
                {
                    "type": "star_with_palace",
                    "palace": "menh",
                    "scope": "dong_cung",
                    "stars": ["a"],
                },
            )
        ]
    ).cach_cuc[0].model_copy(update={"related_to": Role.MENH})

    def fake_find_matching_cach_cuc(
        la_so,
        *,
        source_kind,
        filtered_roles,
    ):
        assert isinstance(la_so, _CatalogLaSo)
        assert filtered_roles == [Role.MENH]
        return [matched]

    monkeypatch.setattr(
        matcher_module,
        "find_matching_cach_cuc",
        fake_find_matching_cach_cuc,
    )

    results = get_cach_cuc_tool_results(
        _CatalogLaSo(),
        filtered_roles=[Role.MENH],
    )

    assert results[0].id == "tool"
    assert results[0].related_to is Role.MENH
    assert "conditions" not in results[0].model_dump()
