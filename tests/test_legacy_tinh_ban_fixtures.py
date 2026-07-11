from __future__ import annotations

import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from src.refactored.model.elementary import DiaChi
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.la_so import LaSo
from src.refactored.view.builder import build_laso_view


RESOURCE_DIR = Path(__file__).parent / "resources"

LEGACY_FIXTURES = (
    pytest.param(
        RESOURCE_DIR / "tinh_ban_phuoc_khanh.json",
        id="phuoc_khanh",
    ),
    pytest.param(
        RESOURCE_DIR / "tinh_ban_quoc_hung.json",
        marks=pytest.mark.xfail(
            reason=(
                "Legacy fixture currently disagrees broadly with the refactored "
                "chart: cuc, cung than, dai han focus map, and placements differ."
            ),
            strict=True,
        ),
        id="quoc_hung",
    ),
    pytest.param(
        RESOURCE_DIR / "tinh_ban_thu_uyen.json",
        id="thu_uyen",
    ),
)

LEGACY_DIA_CHI_BY_NAME = {
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
}

NAME_ALIASES = {
    "Hỏa Cái": "Hoa Cái",
    "Đế Vương": "Đế Vượng",
    "Thiên Thuơng": "Thiên Thương",
}


def _load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _laso_from_legacy_fixture(data: dict[str, Any]) -> LaSo:
    input_data = data["input"]
    prior = LaSoPrior.from_solar_day(
        dt.datetime(
            input_data["year"],
            input_data["month"],
            input_data["day"],
            input_data["hour"],
        ),
        Gender.MALE if input_data["gender"] == "M" else Gender.FEMALE,
    )
    return LaSo.from_prior(prior)


def _normalize_name(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name).strip()
    return NAME_ALIASES.get(normalized, normalized)


def _legacy_dia_chi(name: str) -> DiaChi:
    return LEGACY_DIA_CHI_BY_NAME[name]


def _legacy_component_names(cung_data: dict[str, Any]) -> Counter[str]:
    names: list[str] = []
    for bucket in ("chinhTinh", "phuTinh"):
        names.extend(
            _normalize_name(component["name"])
            for component in cung_data.get(bucket) or ()
        )

    if trang_sinh := cung_data.get("trang_sinh"):
        names.append(_normalize_name(trang_sinh["name"]))

    names.extend(
        _normalize_name(component["name"])
        for component in cung_data.get("tuhoa") or ()
    )

    if cung_data["is_tuan"]:
        names.append("Tuần")
    if cung_data["is_triet"]:
        names.append("Triệt")

    return Counter(names)


def _legacy_components_by_position(data: dict[str, Any]) -> dict[DiaChi, Counter[str]]:
    return {
        _legacy_dia_chi(position): _legacy_component_names(cung_data)
        for position, cung_data in data["map_cung"].items()
    }


def _refactored_components_by_position(la_so: LaSo) -> dict[DiaChi, Counter[str]]:
    return {
        dia_chi: Counter(
            _normalize_name(
                la_so.catalog.get(layered_component.component_id).name
            )
            for layered_component in la_so.cung_at(dia_chi).components
        )
        for dia_chi in DiaChi
    }


def _legacy_roles_by_position(data: dict[str, Any]) -> dict[DiaChi, str]:
    return {
        _legacy_dia_chi(position): cung_data["role"]
        for position, cung_data in data["map_cung"].items()
    }


def _refactored_roles_by_position(la_so: LaSo) -> dict[DiaChi, str]:
    return {
        dia_chi: la_so.catalog.get(la_so.cung_at(dia_chi).natal_role.value).name
        for dia_chi in DiaChi
    }


def _legacy_dai_han_start_age_by_position(data: dict[str, Any]) -> dict[DiaChi, int]:
    return {
        _legacy_dia_chi(position): cung_data["age_daivan"]
        for position, cung_data in data["map_cung"].items()
    }


def _refactored_dai_han_start_age_by_position(la_so: LaSo) -> dict[DiaChi, int]:
    view = build_laso_view(
        la_so,
        study_year=la_so.prior.year + la_so.natal_context.cuc.number,
    )
    return {
        row.focus_position: row.start_age
        for row in view.dai_han_focus_map
    }


@pytest.mark.parametrize("fixture_path", LEGACY_FIXTURES)
def test_legacy_fixture_natal_placement_parity(fixture_path: Path):
    data = _load_fixture(fixture_path)
    la_so = _laso_from_legacy_fixture(data)

    assert _refactored_roles_by_position(la_so) == _legacy_roles_by_position(data)
    assert (
        _refactored_components_by_position(la_so)
        == _legacy_components_by_position(data)
    )
    assert la_so.tinh_ban.than_position == _legacy_dia_chi(data["cung_than"])


@pytest.mark.parametrize("fixture_path", LEGACY_FIXTURES)
def test_legacy_fixture_metadata_parity(fixture_path: Path):
    data = _load_fixture(fixture_path)
    la_so = _laso_from_legacy_fixture(data)

    assert la_so.natal_context.cuc.name == data["cuc"]["name"]
    assert la_so.natal_context.cuc.number == data["cuc"]["number"]
    assert int(la_so.natal_context.van_direction) == data["direction"]
    assert la_so.prior.gender == (
        Gender.MALE if data["gender"] == "M" else Gender.FEMALE
    )
    assert la_so.tinh_ban.than_position == _legacy_dia_chi(data["cung_than"])
    assert (
        "Duong" if la_so.natal_context.am_duong.name == "DUONG" else "Am"
    ) == data["am_duong"]


@pytest.mark.parametrize("fixture_path", LEGACY_FIXTURES)
def test_legacy_fixture_dai_han_focus_parity(fixture_path: Path):
    data = _load_fixture(fixture_path)
    la_so = _laso_from_legacy_fixture(data)

    assert (
        _refactored_dai_han_start_age_by_position(la_so)
        == _legacy_dai_han_start_age_by_position(data)
    )
