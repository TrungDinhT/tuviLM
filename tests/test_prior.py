import datetime as dt

import pytest

from src.refactored.context.natal import NatalContext
from src.refactored.model.elementary import (
    CircleDirection,
    DiaChi,
    NguHanh,
    ThienCan,
)
from src.refactored.model.prior import Gender, LaSoPrior, LunarYear


def test_circle_direction_supports_multiplier_semantics():
    assert CircleDirection.CW.multiplier == 1
    assert CircleDirection.CCW.multiplier == -1
    assert CircleDirection.CW * 3 == 3
    assert 2 * CircleDirection.CCW == -2
    assert -CircleDirection.CW == CircleDirection.CCW


@pytest.mark.parametrize(
    "year, expected_thien_can, expected_dia_chi",
    [
        (1984, ThienCan.GIAP, DiaChi.TY),
        (1996, ThienCan.BINH, DiaChi.TY),
        (2025, ThienCan.AT, DiaChi.TI),
    ],
)
def test_lunar_year_from_year_uses_cyclic_enum_indexes(
    year: int,
    expected_thien_can: ThienCan,
    expected_dia_chi: DiaChi,
):
    lunar_year = LunarYear.from_year(year)

    assert lunar_year.thien_can == expected_thien_can
    assert lunar_year.dia_chi == expected_dia_chi


@pytest.mark.parametrize(
    "solar_day, expected_lunar",
    [
        (dt.date(1998, 4, 4), (8, 3, 1998)),
        (dt.date(1996, 12, 19), (10, 11, 1996)),
        (dt.date(1999, 3, 9), (22, 1, 1999)),
        (dt.date(2000, 3, 18), (13, 2, 2000)),
        (dt.date(1999, 9, 2), (23, 7, 1999)),
        (dt.date(2024, 2, 10), (1, 1, 2024)),
        (dt.date(2024, 2, 9), (30, 12, 2023)),
        (dt.date(2023, 3, 22), (1, 2, 2023)),
        (dt.date(2000, 1, 1), (25, 11, 1999)),
        (dt.date(1999, 12, 31), (24, 11, 1999)),
    ],
)
def test_from_solar_day_preserves_current_lunar_conversion_fixtures(
    solar_day: dt.date,
    expected_lunar: tuple[int, int, int],
):
    prior = LaSoPrior.from_solar_day(
        dt.datetime.combine(solar_day, dt.time(hour=12)),
        Gender.MALE,
    )

    assert (prior.date, prior.month, prior.year) == expected_lunar
    assert prior.hour == DiaChi.NGO


@pytest.mark.parametrize(
    "solar_day, expected_lunar",
    [
        (dt.date(1996, 12, 19), (11, 11, 1996)),
        (dt.date(2024, 2, 9), (1, 1, 2024)),
    ],
)
def test_from_solar_day_keeps_23h_rollover_behavior(
    solar_day: dt.date,
    expected_lunar: tuple[int, int, int],
):
    prior = LaSoPrior.from_solar_day(
        dt.datetime.combine(solar_day, dt.time(hour=23)),
        Gender.MALE,
    )

    assert (prior.date, prior.month, prior.year) == expected_lunar
    assert prior.hour == DiaChi.TY


def test_from_lunar_day_builds_prior_directly():
    prior = LaSoPrior.from_lunar_day(
        year=1989,
        month=12,
        day=27,
        hour=DiaChi.TI,
        gender=Gender.MALE,
    )

    assert (prior.date, prior.month, prior.year) == (27, 12, 1989)
    assert prior.hour == DiaChi.TI
    assert prior.thien_can == ThienCan.KY
    assert prior.dia_chi == DiaChi.TI


def test_from_lunar_day_rejects_missing_lunar_day():
    with pytest.raises(ValueError, match="chỉ có 29 ngày"):
        LaSoPrior.from_lunar_day(
            year=1990,
            month=1,
            day=30,
            hour=DiaChi.TY,
            gender=Gender.MALE,
        )


def test_from_lunar_day_preserves_leap_month_choice():
    prior = LaSoPrior.from_lunar_day(
        year=1990,
        month=5,
        day=1,
        hour=DiaChi.TY,
        gender=Gender.MALE,
        is_leap_month=True,
    )

    assert prior.is_leap_month is True


def test_natal_context_from_prior_derives_menh_position_and_cuc():
    prior = LaSoPrior(
        hour=DiaChi.MEO,
        date=10,
        month=11,
        year=1996,
        gender=Gender.MALE,
    )

    context = NatalContext.from_prior(prior)

    assert prior.lunar_year is prior.lunar_year
    assert prior.lunar_year.thien_can == ThienCan.BINH
    assert prior.lunar_year.dia_chi == DiaChi.TY
    assert context.menh_position == DiaChi.DAU
    assert context.age(2002) == 7
    assert context.cuc.id == "hoa_luc_cuc"
    assert context.cuc.name == "Hỏa Lục cục"
    assert context.cuc.number == 6
    assert context.cuc.ngu_hanh == NguHanh.HOA


def test_natal_context_moves_am_duong_and_van_direction_from_prior():
    prior = LaSoPrior(
        hour=DiaChi.TY,
        date=1,
        month=1,
        year=1985,
        gender=Gender.FEMALE,
    )

    context = NatalContext.from_prior(prior)

    assert context.am_duong.value == 1
    assert context.van_direction == CircleDirection.CW
