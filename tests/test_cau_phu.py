from __future__ import annotations

import json
from datetime import datetime

import pytest
from fastapi import HTTPException

from api.main import read_cau_phu
from api.schemas import BuildLasoRequest
from src.refactored.cau_phu import (
    DEFAULT_CAU_PHU_PATH,
    CauPhuLookupKey,
    extract_cau_phu_lookup_key,
    find_cau_phu,
    get_cau_phu,
    load_cau_phu_catalog,
)
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


def test_catalog_indexes_every_case_without_changing_phu_text() -> None:
    with DEFAULT_CAU_PHU_PATH.open(encoding="utf-8") as file:
        raw_cases = json.load(file)["truong_hop"]

    catalog = load_cau_phu_catalog()

    assert len(catalog) == len(raw_cases) == 480
    for raw_case in raw_cases:
        entry = find_cau_phu(
            CauPhuLookupKey(
                vi_tri=raw_case["vi_tri"],
                chinh_tinh=tuple(reversed(raw_case["chinh_tinh"])),
                co_tuan=raw_case["co_tuan"],
                co_triet=raw_case["co_triet"],
            )
        )
        assert entry.cau_phu == raw_case["cau_phu"]
        assert list(entry.cac_cau) == raw_case["cac_cau"]


def test_completed_chart_matches_its_exact_catalog_entry() -> None:
    la_so = LaSo.from_prior(FIXTURE_PRIOR_A)
    lookup_key = extract_cau_phu_lookup_key(la_so)

    entry = get_cau_phu(la_so)

    assert entry.vi_tri == lookup_key.vi_tri
    assert sorted(entry.chinh_tinh) == sorted(lookup_key.chinh_tinh)
    assert entry.co_tuan is lookup_key.co_tuan
    assert entry.co_triet is lookup_key.co_triet
    assert entry.cau_phu == "\n".join(entry.cac_cau)


def test_api_returns_original_phu_for_requested_birth() -> None:
    payload = BuildLasoRequest(year=1990, month=5, day=15, hour=10, gender="M")
    la_so = LaSo.from_prior(
        LaSoPrior.from_solar_day(datetime(1990, 5, 15, 10), Gender.MALE)
    )

    response = read_cau_phu(payload)
    expected = get_cau_phu(la_so)

    assert response.cau_phu == expected.cau_phu
    assert response.cac_cau == list(expected.cac_cau)
    assert response.tieu_de == expected.tieu_de


def test_api_rejects_invalid_birth_date() -> None:
    payload = BuildLasoRequest(year=2000, month=2, day=31, hour=10, gender="M")

    with pytest.raises(HTTPException) as exc_info:
        read_cau_phu(payload)

    assert exc_info.value.status_code == 422
