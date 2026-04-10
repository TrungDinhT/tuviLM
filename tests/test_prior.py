from types import SimpleNamespace

import pytest

from src.refactored.component.elementary import DiaChi, ThienCan
from src.refactored.component.prior import LunarYear


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
