import datetime as dt

import pytest

from src.refactored.builder.meta_rules import menh_position_fn
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import Gender, LaSoPrior


@pytest.mark.parametrize(
    "solar, gender, expected_menh",
    [
        (
            dt.datetime(1996, 12, 19, 6, 30),
            Gender.MALE,
            DiaChi.DAU,
        ),
    ],
)
def test_menh_position_fn(solar: dt.datetime, gender: Gender, expected_menh: DiaChi):
    # 19/12/1996 6:30 a.m. (day/month/year)
    prior = LaSoPrior.from_solar_day(solar, gender)
    assert menh_position_fn(prior) == expected_menh
