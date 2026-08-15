import pytest
from pydantic import ValidationError

from api.laso.routes import build_laso
from api.schemas import BuildLasoRequest


def test_build_laso_route_accepts_lunar_birth_info():
    response = build_laso(
        BuildLasoRequest(
            calendar="lunar",
            year=1989,
            month=12,
            day=27,
            hour_in_dia_chi="ti",
            gender="M",
        )
    )

    assert response.summary == "Sinh âm lịch: 27/12/1989 giờ Tỵ"
    assert len(response.cung_by_position) == 12


def test_build_laso_request_rejects_missing_lunar_day():
    with pytest.raises(ValidationError, match="chỉ có 29 ngày"):
        BuildLasoRequest(
            calendar="lunar",
            year=1990,
            month=1,
            day=30,
            hour_in_dia_chi="ty",
            gender="M",
        )


def test_build_laso_request_rejects_solar_with_dia_chi_hour():
    with pytest.raises(ValidationError, match="Dương lịch không dùng giờ sinh theo Địa Chi"):
        BuildLasoRequest(
            calendar="solar",
            year=1990,
            month=1,
            day=1,
            hour=0,
            hour_in_dia_chi="ty",
            gender="M",
        )


def test_build_laso_request_rejects_lunar_with_solar_hour():
    with pytest.raises(ValidationError, match="Âm lịch không dùng giờ sinh dương lịch"):
        BuildLasoRequest(
            calendar="lunar",
            year=1989,
            month=12,
            day=27,
            hour=0,
            hour_in_dia_chi="ty",
            gender="M",
        )
