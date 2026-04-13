from types import SimpleNamespace

import pytest

from src.refactored.component.elementary import DiaChi, NguHanh, ThienCan
from src.refactored.component.prior import Gender, LaSoContext, LaSoPrior, LunarYear


@pytest.mark.parametrize(
    "year, expected_thien_can, expected_dia_chi",
    [
        (1984, ThienCan.GIAP, DiaChi.TY),
        (1996, ThienCan.BINH, DiaChi.TY),
        (2025, ThienCan.AT, DiaChi.TI),
    ],
)
def test_lunar_year_from_solar_year_uses_cyclic_enum_indexes(
    year: int,
    expected_thien_can: ThienCan,
    expected_dia_chi: DiaChi,
):
    lunar_date = SimpleNamespace(year=year)

    lunar_year = LunarYear.from_solar_year(lunar_date)  # type: ignore[arg-type]

    assert lunar_year.thien_can == expected_thien_can
    assert lunar_year.dia_chi == expected_dia_chi


def test_laso_context_from_prior_derives_menh_position_and_cuc():
    prior = LaSoPrior(
        hour=DiaChi.MEO,
        date=10,
        month=11,
        year=LunarYear(dia_chi=DiaChi.TY, thien_can=ThienCan.BINH),
        gender=Gender.MALE,
    )

    context = LaSoContext.from_prior(prior)

    assert context.menh_position == DiaChi.DAU
    assert context.cuc.id == "hoa_luc_cuc"
    assert context.cuc.name == "Hỏa Lục cục"
    assert context.cuc.number == 6
    assert context.cuc.ngu_hanh == NguHanh.HOA


def test_laso_context_moves_am_duong_and_van_direction_from_prior():
    prior = LaSoPrior(
        hour=DiaChi.TY,
        date=1,
        month=1,
        year=LunarYear(dia_chi=DiaChi.SUU, thien_can=ThienCan.AT),
        gender=Gender.FEMALE,
    )

    context = LaSoContext.from_prior(prior)

    assert context.get_am_duong().value == 1
    assert context.van_direction() == 1
