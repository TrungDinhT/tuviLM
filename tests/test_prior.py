import pytest

from src.refactored.model.elementary import (
    CircleDirection,
    DiaChi,
    NguHanh,
    ThienCan,
)
from src.refactored.model.prior import Gender, LaSoPrior, LunarYear
from src.refactored.context.natal import NatalContext


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
