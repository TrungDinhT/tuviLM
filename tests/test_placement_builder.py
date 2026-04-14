import datetime as dt

import pytest

from src.refactored.builder.placement_builder import PlacementBuilder
from src.refactored.placement.primitives import Vong, same_slot
from src.refactored.placement.rules import CHINH_TINH_RULES, PHU_TINH_RULES
from src.refactored.placement.registry import (
    AbsolutePositionSpec,
    RelativePositionSpec,
)
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import Gender
from src.tuvi.birth import BirthTime
from src.tuvi.builder import Builder as LegacyBuilder


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
        position = DiaChi(dia_chi_text)
        for sao in cung.chinhTinh:
            positions[CHINH_TINH_COMPONENT_IDS[sao.name]] = position

    return positions


def _build_legacy_phu_tinh_positions(
    time: dt.datetime, component_ids: dict[str, str]
) -> dict[str, DiaChi]:
    tinh_ban = LegacyBuilder().build(BirthTime.from_solar_day(time, "M"))
    positions: dict[str, DiaChi] = {}

    for dia_chi_text, cung in tinh_ban.map_cung.items():
        position = DiaChi(dia_chi_text)
        for sao in cung.phuTinh:
            component_id = component_ids.get(sao.name)
            if component_id is not None:
                positions[component_id] = position

    return positions


def test_builder_resolves_chained_specs_in_any_order():
    component_a = "A"
    component_b = "B"
    component_c = "C"

    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)

    builder.register_component_lazy(
        component_c,
        RelativePositionSpec(component_b, lambda position: position + 1),
    )
    builder.register_component_lazy(
        component_b,
        RelativePositionSpec(component_a, lambda position: position + 1),
    )
    builder.register_component_lazy(
        component_a,
        AbsolutePositionSpec(lambda _context: DiaChi.DAN),
    )

    builder.resolve_pending()

    assert builder.get_or_resolve_position(component_a) == DiaChi.DAN
    assert builder.get_or_resolve_position(component_b) == DiaChi.MEO
    assert builder.get_or_resolve_position(component_c) == DiaChi.THIN


def test_vong_supports_same_slot_groups():
    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    rules = [
        Vong(
            principal_id="anchor",
            principal_position_fn=lambda _context: DiaChi.DAN,
            others=[
                same_slot("slot_one_a", "slot_one_b"),
                "slot_two",
            ],
        )
    ]

    builder.register_rules(rules)
    builder.resolve_pending()

    assert builder.get_or_resolve_position("anchor") == DiaChi.DAN
    assert builder.get_or_resolve_position("slot_one_a") == DiaChi.MEO
    assert builder.get_or_resolve_position("slot_one_b") == DiaChi.MEO
    assert builder.get_or_resolve_position("slot_two") == DiaChi.THIN


def test_builder_supports_prior_aware_relative_specs():
    component_a = "A"
    component_b = "B"

    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    builder.register_component_lazy(
        component_b,
        RelativePositionSpec(
            component_a,
            lambda position, context: position + context.van_direction(),
        ),
    )
    builder.register_component_lazy(
        component_a,
        AbsolutePositionSpec(lambda _context: DiaChi.DAN),
    )

    builder.resolve_pending()

    assert builder.get_or_resolve_position(component_b) == DiaChi.MEO


def test_builder_detects_circular_position_dependencies():
    component_a = "A"
    component_b = "B"

    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    builder.register_component_lazy(
        component_a,
        RelativePositionSpec(component_b, lambda position: position + 1),
    )
    builder.register_component_lazy(
        component_b,
        RelativePositionSpec(component_a, lambda position: position + 1),
    )

    with pytest.raises(ValueError, match="Circular position dependency detected"):
        builder.resolve_pending()


def test_builder_resolves_chinh_tinh_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules(CHINH_TINH_RULES)

    positions = builder.resolve_all()
    legacy_positions = _build_legacy_chinh_tinh_positions(time)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_thai_tue_ring_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules([PHU_TINH_RULES[3]])

    positions = builder.resolve_all()
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
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules(PHU_TINH_RULES[:3])

    positions = builder.resolve_all()
    legacy_positions = _build_legacy_phu_tinh_positions(time, LOC_TON_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["loc_ton"] == positions["bac_si"]
    assert positions["tieu_hao"] == positions["ln_van_tinh"]
    assert positions["tau_thu"] == positions["duong_phu"]
    assert positions["benh_phu"] == positions["quoc_an"]
    assert positions["da_la"] == positions["quan_phur"]


def test_builder_resolves_month_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules(
        _select_rules_by_component_ids(set(MONTH_COMPONENT_IDS.values()))
    )

    positions = builder.resolve_all()
    legacy_positions = _build_legacy_phu_tinh_positions(time, MONTH_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["thien_dieu"] == positions["thien_y"]


def test_builder_resolves_hour_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules(
        _select_rules_by_component_ids(set(HOUR_COMPONENT_IDS.values()))
    )

    positions = builder.resolve_all()
    legacy_positions = _build_legacy_phu_tinh_positions(time, HOUR_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_thien_can_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules(
        _select_rules_by_component_ids(set(THIEN_CAN_COMPONENT_IDS.values()))
    )

    positions = builder.resolve_all()
    legacy_positions = _build_legacy_phu_tinh_positions(time, THIEN_CAN_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )


def test_builder_resolves_year_branch_rules_like_legacy_builder():
    time = dt.datetime(1996, 12, 19, 6, 30)
    builder = PlacementBuilder(time, Gender.MALE)
    builder.register_rules(
        _select_rules_by_component_ids(set(YEAR_BRANCH_COMPONENT_IDS.values()))
    )

    positions = builder.resolve_all()
    legacy_positions = _build_legacy_phu_tinh_positions(time, YEAR_BRANCH_COMPONENT_IDS)

    assert {component_id: positions[component_id] for component_id in legacy_positions} == (
        legacy_positions
    )

    assert positions["hong_loan"] == positions["thien_hi"] + 6
    assert positions["phuong_cac"] == positions["giai_than"]
