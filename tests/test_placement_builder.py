import datetime as dt

import pytest

from src.refactored.builder.component_catalog import get_default_catalog
from src.refactored.builder.placement_builder import PlacementBuilder
from src.refactored.component.sao import TuanTriet
from src.refactored.placement.compiler import (
    PlacementRuleCompiler,
    SpecializedAbsoluteSpec,
    SpecializedPlacementRules,
    SpecializedRelativeSpec,
)
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.primitives import (
    Circle,
    SamePosition,
    TuanTrietPosition,
    triet_positions_fn,
    tuan_positions_fn,
)
from src.refactored.placement.rules import (
    CHINH_TINH_RULES,
    ROLE_RULES,
    PHU_TINH_RULES,
    TU_HOA_RULES,
    TU_HOA_TARGET_BY_THIEN_CAN,
    get_default_placement_rule_compiler,
)
from src.refactored.placement.registry import (
    AbsolutePositionSpec,
    RelativePositionSpec,
)
from src.refactored.component.elementary import DiaChi
from src.refactored.context.prior import Gender, LaSoPrior
from src.refactored.context.natal import NatalContext
from src.tuvi.birth import BirthTime
from src.tuvi.builder import Builder as LegacyBuilder
from src.tuvi.constant import MAP_TRIET, MAP_TUAN
from src.tuvi.element.types import LIST_DIA_CHI, LIST_THIEN_CAN


CHINH_TINH_COMPONENT_IDS = {
    "Tử Vi": "tu_vi",
    "Vũ Khúc": "vu_khuc",
    "Liêm Trinh": "liem_trinh",
    "Thất Sát": "that_sat",
    "Phá Quân": "pha_quan",
    "Tham Lang": "tham_lang",
    "Thiên Cơ": "thien_co",
    "Thái Âm": "thai_am",
    "Thiên Đồng": "thien_dong",
    "Thiên Lương": "thien_luong",
    "Cự Môn": "cu_mon",
    "Thái Dương": "thai_duong",
    "Thiên Phủ": "thien_phu",
    "Thiên Tướng": "thien_tuong",
}

THAI_TUE_COMPONENT_IDS = {
    "Thái Tuế": "thai_tue",
    "Thiếu Dương": "thieu_duong",
    "Thiên Không": "thien_khong",
    "Tang Môn": "tang_mon",
    "Thiếu Âm": "thieu_am",
    "Quan Phù": "quan_phuf",
    "Long Trì": "long_tri",
    "Tử Phù": "tu_phu",
    "Nguyệt Đức": "nguyet_duc",
    "Tuế Phá": "tue_pha",
    "Thiên Hư": "thien_hu",
    "Long Đức": "long_duc",
    "Bạch Hổ": "bach_ho",
    "Phúc Đức": "sao_phuc_duc",
    "Thiên Đức": "thien_duc",
    "Điếu Khách": "dieu_khach",
    "Trực Phù": "truc_phu",
}

LOC_TON_COMPONENT_IDS = {
    "Lộc Tồn": "loc_ton",
    "Bác Sĩ": "bac_si",
    "Lực Sĩ": "luc_si",
    "Kình Dương": "kinh_duong",
    "Thanh Long": "thanh_long",
    "Tiểu Hao": "tieu_hao",
    "LN Văn Tinh": "ln_van_tinh",
    "Tướng Quân": "tuong_quan",
    "Tấu Thư": "tau_thu",
    "Đường Phù": "duong_phu",
    "Phi Liêm": "phi_liem",
    "Hỷ Thần": "hy_than",
    "Bệnh Phù": "benh_phu",
    "Quốc Ấn": "quoc_an",
    "Đại Hao": "dai_hao",
    "Phục Binh": "phuc_binh",
    "Đà La": "da_la",
    "Quan Phủ": "quan_phur",
}

MONTH_COMPONENT_IDS = {
    "Tả Phù": "ta_phu",
    "Hữu Bật": "huu_bat",
    "Tam Thai": "tam_thai",
    "Bát Toạ": "bat_toa",
    "Thiên Giải": "thien_giai",
    "Địa Giải": "dia_giai",
    "Thiên Hình": "thien_hinh",
    "Thiên Diêu": "thien_dieu",
    "Thiên Y": "thien_y",
}

HOUR_COMPONENT_IDS = {
    "Địa Không": "dia_khong",
    "Địa Kiếp": "dia_kiep",
    "Văn Xương": "van_xuong",
    "Văn Khúc": "van_khuc",
    "Ân Quang": "an_quang",
    "Thiên Quý": "thien_quy",
    "Thai Phụ": "thai_phu",
    "Phong Cáo": "phong_cao",
}

THIEN_CAN_COMPONENT_IDS = {
    "Thiên Khôi": "thien_khoi",
    "Thiên Việt": "thien_viet",
    "Lưu Hà": "luu_ha",
    "Thiên Trù": "thien_tru",
    "Thiên Quan": "thien_quan",
    "Thiên Phúc": "thien_phuc",
}

YEAR_BRANCH_COMPONENT_IDS = {
    "Cô Thần": "co_than",
    "Quả Tú": "qua_tu",
    "Thiên Hỉ": "thien_hi",
    "Hồng Loan": "hong_loan",
    "Giải Thần": "giai_than",
    "Phượng Các": "phuong_cac",
    "Thiên Khốc": "thien_khoc",
    "Thiên Mã": "thien_ma",
    "Phá Toái": "pha_toai",
    "Hỏa Cái": "hoa_cai",
    "Đào Hỏa": "dao_hoa",
    "Kiếp Sát": "kiep_sat",
}

DAU_QUAN_COMPONENT_IDS = {
    "Đẩu Quân": "dau_quan",
}

LINH_HOA_COMPONENT_IDS = {
    "Hỏa Tinh": "hoa_tinh",
    "Linh Tinh": "linh_tinh",
}

TUHOA_COMPONENT_IDS = {
    "Hóa Lộc": "hoa_loc",
    "Hóa Quyền": "hoa_quyen",
    "Hóa Khoa": "hoa_khoa",
    "Hóa Kỵ": "hoa_ky",
}

TRANG_SINH_COMPONENT_IDS = {
    "Tràng Sinh": "trang_sinh",
    "Mộc Dục": "moc_duc",
    "Quan Đới": "quan_doi",
    "Lâm Quan": "lam_quan",
    "Đế  Vương": "de_vuong",
    "Suy": "suy",
    "Bệnh": "benh",
    "Tử": "tu",
    "Mộ": "mo",
    "Tuyệt": "tuyet",
    "Thai": "thai",
    "Dưỡng": "duong",
}


def _legacy_dia_chi(text: str) -> DiaChi:
    return {
        "Tý": DiaChi.TY,
        "Sửu": DiaChi.SUU,
        "Dần": DiaChi.DAN,
        "Mão": DiaChi.MEO,
        "Thìn": DiaChi.THIN,
        "Tị": DiaChi.TI,
        "Ngọ": DiaChi.NGO,
        "Mùi": DiaChi.MUI,
        "Thân": DiaChi.THAN,
        "Dậu": DiaChi.DAU,
        "Tuất": DiaChi.TUAT,
        "Hợi": DiaChi.HOI,
    }[text]


def _select_rules_by_component_ids(component_ids: set[str]):
    return [
        rule
        for rule in PHU_TINH_RULES
        if getattr(rule, "component_id", None) in component_ids
    ]


def _build_legacy_chinh_tinh_positions(time: dt.datetime) -> dict[str, DiaChi]:
    tinh_ban = LegacyBuilder().build(BirthTime.from_solar_day(time, "M"))
    positions: dict[str, DiaChi] = {}

    for dia_chi_text, cung in tinh_ban.map_cung.items():
        position = _legacy_dia_chi(dia_chi_text)
        for sao in cung.chinhTinh:
            positions[CHINH_TINH_COMPONENT_IDS[sao.name]] = position

    return positions


def _build_legacy_phu_tinh_positions(
    time: dt.datetime, component_ids: dict[str, str]
) -> dict[str, DiaChi]:
    tinh_ban = LegacyBuilder().build(BirthTime.from_solar_day(time, "M"))
    positions: dict[str, DiaChi] = {}

    for dia_chi_text, cung in tinh_ban.map_cung.items():
        position = _legacy_dia_chi(dia_chi_text)
        for sao in cung.phuTinh:
            component_id = component_ids.get(sao.name)
            if component_id is not None:
                positions[component_id] = position

    return positions


def _build_legacy_tuhoa_positions(time: dt.datetime) -> dict[str, DiaChi]:
    tinh_ban = LegacyBuilder().build(BirthTime.from_solar_day(time, "M"))
    positions: dict[str, DiaChi] = {}
    for dia_chi_text, cung in tinh_ban.map_cung.items():
        position = _legacy_dia_chi(dia_chi_text)
        for tuhoa in cung.tuhoa:
            component_id = TUHOA_COMPONENT_IDS[tuhoa.name]
            positions[component_id] = position
    return positions


def _build_legacy_trang_sinh_positions(
    time: dt.datetime, component_ids: dict[str, str]
) -> dict[str, DiaChi]:
    tinh_ban = LegacyBuilder().build(BirthTime.from_solar_day(time, "M"))
    positions: dict[str, DiaChi] = {}

    for dia_chi_text, cung in tinh_ban.map_cung.items():
        position = _legacy_dia_chi(dia_chi_text)
        if cung.trang_sinh is None:
            continue
        component_id = component_ids.get(cung.trang_sinh.name)
        if component_id is not None:
            positions[component_id] = position

    return positions


def _legacy_tuan_triet_expected(time: dt.datetime, gender: Gender) -> dict[str, DiaChi]:
    g = "M" if gender == Gender.MALE else "F"
    bt = BirthTime.from_solar_day(time, g)
    triet_names = MAP_TRIET[bt.thien_can]
    tuan_key = LIST_DIA_CHI[
        (LIST_DIA_CHI.index(bt.dia_chi) - LIST_THIEN_CAN.index(bt.thien_can)) % 12
    ]
    tuan_names = MAP_TUAN[tuan_key]
    return {
        "triet_1": _legacy_dia_chi(triet_names[0]),
        "triet_2": _legacy_dia_chi(triet_names[1]),
        "tuan_1": _legacy_dia_chi(tuan_names[0]),
        "tuan_2": _legacy_dia_chi(tuan_names[1]),
    }


def _resolve_positions_with_rules(
    *,
    time: dt.datetime,
    gender: Gender,
    rules,
) -> dict[str, DiaChi]:
    compiler = PlacementRuleCompiler()
    compiler.register_rules(rules)
    context = NatalContext.from_prior(LaSoPrior.from_solar_day(time, gender))
    return PlacementBuilder(context, compiler=compiler).resolve_all()


def _resolve_positions_with_specs(
    *,
    time: dt.datetime,
    gender: Gender,
    specs: dict[str, AbsolutePositionSpec | RelativePositionSpec],
) -> dict[str, DiaChi]:
    compiler = PlacementRuleCompiler()
    for component_id, spec in specs.items():
        compiler.register_component_lazy(component_id, spec)
    context = NatalContext.from_prior(LaSoPrior.from_solar_day(time, gender))
    return PlacementBuilder(context, compiler=compiler).resolve_all()


def test_builder_resolves_chained_specs_in_any_order():
    component_a = "A"
    component_b = "B"
    component_c = "C"

    positions = _resolve_positions_with_specs(
        time=dt.datetime(1996, 12, 19, 6, 30),
        gender=Gender.MALE,
        specs={
            component_c: RelativePositionSpec(component_b, lambda position: position + 1),
            component_b: RelativePositionSpec(component_a, lambda position: position + 1),
            component_a: AbsolutePositionSpec(lambda _context: DiaChi.DAN),
        },
    )

    assert positions[component_a] == DiaChi.DAN
    assert positions[component_b] == DiaChi.MEO
    assert positions[component_c] == DiaChi.THIN


def test_vong_supports_same_position_groups():
    rules = [
        Circle(
            principal_id="anchor",
            principal_position_fn=lambda _context: DiaChi.DAN,
            others=[
                SamePosition("slot_one_a", "slot_one_b"),
                "slot_two",
            ],
        )
    ]

    positions = _resolve_positions_with_rules(
        time=dt.datetime(1996, 12, 19, 6, 30),
        gender=Gender.MALE,
        rules=rules,
    )

    assert positions["anchor"] == DiaChi.DAN
    assert positions["slot_one_a"] == DiaChi.MEO
    assert positions["slot_one_b"] == DiaChi.MEO
    assert positions["slot_two"] == DiaChi.THIN


def test_vong_can_follow_van_direction():
    rules = [
        Circle(
            principal_id="anchor",
            principal_position_fn=lambda _context: DiaChi.DAN,
            direction=Circle.Direction.VAN,
            others=[
                "slot_one",
                SamePosition("slot_two_a", "slot_two_b"),
            ],
        )
    ]

    positions = _resolve_positions_with_rules(
        time=dt.datetime(1996, 12, 19, 6, 30),
        gender=Gender.FEMALE,
        rules=rules,
    )

    assert positions["anchor"] == DiaChi.DAN
    assert positions["slot_one"] == DiaChi.SUU
    assert positions["slot_two_a"] == DiaChi.TY
    assert positions["slot_two_b"] == DiaChi.TY


def test_builder_supports_prior_aware_relative_specs():
    component_a = "A"
    component_b = "B"

    positions = _resolve_positions_with_specs(
        time=dt.datetime(1996, 12, 19, 6, 30),
        gender=Gender.MALE,
        specs={
            component_b: RelativePositionSpec(
                lambda _ctx: component_a,
                lambda position, context: position + context.van_direction,
            ),
            component_a: AbsolutePositionSpec(lambda _context: DiaChi.DAN),
        },
    )

    assert positions[component_b] == DiaChi.MEO


def test_builder_detects_circular_position_dependencies():
    component_a = "A"
    component_b = "B"

    compiler = PlacementRuleCompiler()
    compiler.register_component_lazy(
        component_a,
        RelativePositionSpec(component_b, lambda position: position + 1),
    )
    compiler.register_component_lazy(
        component_b,
        RelativePositionSpec(component_a, lambda position: position + 1),
    )
    context = NatalContext.from_prior(
        LaSoPrior.from_solar_day(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    )
    builder = PlacementBuilder(context, compiler=compiler)
    with pytest.raises(ValueError, match="Circular position dependency detected"):
        builder.resolve_all()


def test_builder_resolves_chinh_tinh_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time, gender=Gender.MALE, rules=CHINH_TINH_RULES
    )
    legacy_positions = _build_legacy_chinh_tinh_positions(time)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_thai_tue_ring_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time, gender=Gender.MALE, rules=[PHU_TINH_RULES[2]]
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, THAI_TUE_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["thieu_duong"] == positions["thien_khong"]
    assert positions["quan_phuf"] == positions["long_tri"]
    assert positions["tu_phu"] == positions["nguyet_duc"]
    assert positions["tue_pha"] == positions["thien_hu"]
    assert positions["sao_phuc_duc"] == positions["thien_duc"]


def test_builder_resolves_loc_ton_ring_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time, gender=Gender.MALE, rules=PHU_TINH_RULES[:2]
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, LOC_TON_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["loc_ton"] == positions["bac_si"]
    assert positions["tieu_hao"] == positions["ln_van_tinh"]
    assert positions["tau_thu"] == positions["duong_phu"]
    assert positions["benh_phu"] == positions["quoc_an"]
    assert positions["da_la"] == positions["quan_phur"]


def test_builder_resolves_trang_sinh_circle_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    trang_sinh_rule = next(
        rule for rule in PHU_TINH_RULES if getattr(rule, "principal_id", "") == "trang_sinh"
    )
    positions = _resolve_positions_with_rules(
        time=time, gender=Gender.MALE, rules=[trang_sinh_rule]
    )
    legacy_positions = _build_legacy_trang_sinh_positions(time, TRANG_SINH_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_catalog_loads_tuan_triet_entries():
    catalog = get_default_catalog()
    t1 = catalog.get("tuan_1")
    assert isinstance(t1, TuanTriet)
    assert t1.name == "Tuần"
    assert catalog.get("triet_1").name == "Triệt"


def test_builder_resolves_tuan_triet_like_legacy_maps():
    time = dt.datetime(1996, 12, 19, 6, 30)
    gender = Gender.MALE
    expected = _legacy_tuan_triet_expected(time, gender)

    positions = _resolve_positions_with_rules(
        time=time,
        gender=gender,
        rules=[
            TuanTrietPosition(
                pair_ids=("triet_1", "triet_2"),
                pair_position_fn=triet_positions_fn,
            ),
            TuanTrietPosition(
                pair_ids=("tuan_1", "tuan_2"),
                pair_position_fn=tuan_positions_fn,
            ),
        ],
    )

    for component_id, dia_chi in expected.items():
        assert positions[component_id] == dia_chi


def test_phu_tinh_rules_include_tuan_triet_position_rules():
    tuan_triet_rules = [r for r in PHU_TINH_RULES if isinstance(r, TuanTrietPosition)]
    assert len(tuan_triet_rules) == 2


def test_builder_resolves_month_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=_select_rules_by_component_ids(set(MONTH_COMPONENT_IDS.values())),
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, MONTH_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["thien_dieu"] == positions["thien_y"]


def test_builder_resolves_hour_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=_select_rules_by_component_ids(set(HOUR_COMPONENT_IDS.values())),
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, HOUR_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_thien_can_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=_select_rules_by_component_ids(set(THIEN_CAN_COMPONENT_IDS.values())),
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, THIEN_CAN_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_year_branch_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=_select_rules_by_component_ids(set(YEAR_BRANCH_COMPONENT_IDS.values())),
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, YEAR_BRANCH_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["hong_loan"] == positions["thien_hi"] + 6
    assert positions["phuong_cac"] == positions["giai_than"]


def test_builder_resolves_dau_quan_rule_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=_select_rules_by_component_ids(set(DAU_QUAN_COMPONENT_IDS.values())),
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, DAU_QUAN_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_linh_hoa_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=_select_rules_by_component_ids(set(LINH_HOA_COMPONENT_IDS.values())),
    )
    legacy_positions = _build_legacy_phu_tinh_positions(time, LINH_HOA_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_context_relative_position_spec_resolves():
    time = dt.datetime(1996, 12, 19, 6, 30)
    prior = LaSoPrior.from_solar_day(time, Gender.MALE)
    positions = _resolve_positions_with_specs(
        time=time,
        gender=Gender.MALE,
        specs={
            "ref": AbsolutePositionSpec(lambda _ctx: DiaChi.THIN),
            "child": RelativePositionSpec(
                reference=lambda _ctx: "ref",
                transform=lambda pos: pos,
            ),
            "child_two_arg_transform": RelativePositionSpec(
                reference=lambda _ctx: "ref",
                transform=lambda pos, ctx: pos + ctx.prior.hour.index,
            ),
        },
    )

    assert positions["child"] == DiaChi.THIN
    assert positions["child_two_arg_transform"] == (DiaChi.THIN + prior.hour.index)


def test_builder_resolves_tuhoa_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    positions = _resolve_positions_with_rules(
        time=time,
        gender=Gender.MALE,
        rules=ROLE_RULES + CHINH_TINH_RULES + PHU_TINH_RULES + TU_HOA_RULES,
    )
    legacy_positions = _build_legacy_tuhoa_positions(time)

    for hoa_id in ("hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky"):
        assert positions[hoa_id] == legacy_positions[hoa_id]


def test_tuhoa_without_star_rules_raises_key_error():
    compiler = PlacementRuleCompiler()
    compiler.register_rules(TU_HOA_RULES)
    context = NatalContext.from_prior(
        LaSoPrior.from_solar_day(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    )
    builder = PlacementBuilder(context, compiler=compiler)
    with pytest.raises(KeyError):
        builder.resolve_all()


def test_tuhoa_targets_are_registered_components():
    resolved = _resolve_positions_with_rules(
        time=dt.datetime(1996, 12, 19, 6, 30),
        gender=Gender.MALE,
        rules=ROLE_RULES + CHINH_TINH_RULES + PHU_TINH_RULES,
    )

    for thien_can, entities in TU_HOA_TARGET_BY_THIEN_CAN.items():
        for entity, target_id in entities.items():
            assert target_id in resolved, (
                f"Tứ Hóa target `{target_id}` for {thien_can} `{entity}` "
                "is not produced by ROLE_RULES + CHINH_TINH_RULES + PHU_TINH_RULES"
            )


def test_default_placement_rule_compiler_factory_returns_independent_instances():
    first = get_default_placement_rule_compiler()
    second = get_default_placement_rule_compiler()

    assert first is not second


def test_compiler_compile_validates_missing_reference():
    compiler = PlacementRuleCompiler()
    context = NatalContext.from_prior(
        LaSoPrior.from_solar_day(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    )
    compiler.register_component_lazy(
        "child",
        RelativePositionSpec(
            reference=lambda _ctx: "missing_ref",
            transform=lambda pos: pos,
        ),
    )

    with pytest.raises(KeyError):
        compiler.compile(context)


def test_engine_resolve_one_reuses_cached_dependencies():
    calls = {"base": 0}

    def _base_position() -> DiaChi:
        calls["base"] += 1
        return DiaChi.DAN

    rules = SpecializedPlacementRules(
        specs={
            "base": SpecializedAbsoluteSpec(position_fn=_base_position),
            "child": SpecializedRelativeSpec(
                reference_id="base",
                transform=lambda position: position + 1,
            ),
        }
    )
    engine = PlacementEngine(rules)

    assert engine.resolve_one("child") == DiaChi.MEO
    assert engine.resolve_one("child") == DiaChi.MEO
    assert calls["base"] == 1
