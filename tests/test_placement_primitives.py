
import pytest

from src.refactored.component.elementary import CircleDirection, DiaChi, ThienCan
from src.refactored.component.prior import Gender, LaSoContext, LaSoPrior, LunarYear
from src.refactored.placement.primitives import (
    move_by_attr,
    move_by_van_direction,
    move_with,
)


@pytest.mark.parametrize(
    "attribute_name, direction, multiplier, expected",
    [
        ("month", CircleDirection.CW, 1, DiaChi.TI),
        ("month", CircleDirection.CCW, 2, DiaChi.THAN),
        ("hour", CircleDirection.CW, 1, DiaChi.TUAT),
    ],
)
def test_move_by_attr(
    attribute_name: str,
    direction: CircleDirection,
    multiplier: int,
    expected: DiaChi,
):
    context = LaSoContext.from_prior(
        LaSoPrior(
            hour=DiaChi.THAN,
            date=1,
            month=3,
            year=LunarYear(dia_chi=DiaChi.TY, thien_can=ThienCan.GIAP),
            gender=Gender.MALE,
        )
    )

    transform = move_by_attr(
        attribute_name,
        direction=direction,
        step_multiplier=multiplier,
    )

    assert transform(DiaChi.DAN, context) == expected


def test_move_with_uses_context_derived_steps():
    context = LaSoContext.from_prior(
        LaSoPrior(
            hour=DiaChi.MEO,
            date=1,
            month=4,
            year=LunarYear(dia_chi=DiaChi.TY, thien_can=ThienCan.GIAP),
            gender=Gender.MALE,
        )
    )
    transform = move_with(
        lambda current_context: current_context.prior.month,
        direction=CircleDirection.CW,
    )

    assert transform(DiaChi.DAN, context) == DiaChi.NGO


@pytest.mark.parametrize(
    "gender, expected",
    [
        (Gender.MALE, DiaChi.MEO),
        (Gender.FEMALE, DiaChi.SUU),
    ],
)
def test_move_by_van_direction_uses_chart_direction(
    gender: Gender, expected: DiaChi
):
    context = LaSoContext.from_prior(
        LaSoPrior(
            hour=DiaChi.TY,
            date=1,
            month=1,
            year=LunarYear(dia_chi=DiaChi.TY, thien_can=ThienCan.GIAP),
            gender=gender,
        )
    )
    transform = move_by_van_direction(lambda _context: 1)

    assert transform(DiaChi.DAN, context) == expected
