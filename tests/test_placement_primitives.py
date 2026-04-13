
import pytest

from src.refactored.placement.primitives import move_by_la_so_attr
from src.refactored.component.elementary import DiaChi, ThienCan
from src.refactored.component.prior import Gender, LaSoContext, LaSoPrior, LunarYear


@pytest.mark.parametrize(
    "gender, attribute_name, multiplier, expected",
    [
        (Gender.MALE, "month", 1, DiaChi.TI),
        (Gender.FEMALE, "month", 2, DiaChi.THAN),
        (Gender.MALE, "hour", 1, DiaChi.TUAT),
    ],
)
def test_move_by_prior_attr(
    gender: Gender, attribute_name: str, multiplier: int, expected: DiaChi
):
    context = LaSoContext.from_prior(
        LaSoPrior(
            hour=DiaChi.THAN,
            date=1,
            month=3,
            year=LunarYear(dia_chi=DiaChi.TY, thien_can=ThienCan.GIAP),
            gender=gender,
        )
    )

    transform = move_by_la_so_attr(attribute_name, step_multiplier=multiplier)

    assert transform(DiaChi.DAN, context) == expected


def test_move_by_prior_attr_uses_prior_inside_context():
    context = LaSoContext.from_prior(
        LaSoPrior(
            hour=DiaChi.MEO,
            date=1,
            month=4,
            year=LunarYear(dia_chi=DiaChi.TY, thien_can=ThienCan.GIAP),
            gender=Gender.MALE,
        )
    )
    transform = move_by_la_so_attr("month", step_multiplier=1)

    assert transform(DiaChi.DAN, context) == DiaChi.NGO
