import datetime as dt
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml


MIN_SUPPORTED_YEAR = 1800
MAX_SUPPORTED_YEAR = 2199

LUNAR_YEARS_PATH = Path(__file__).with_name("data") / "lunar_years.yaml"


@dataclass(frozen=True)
class LunarDate:
    day: int
    month: int
    year: int
    is_leap_month: bool
    julian_day_number: int

    @property
    def leap(self) -> bool:
        return self.is_leap_month

    @property
    def jd(self) -> int:
        return self.julian_day_number


@dataclass(frozen=True)
class LunarYearInfo:
    tet_offset_days: int
    regular_month_lengths: tuple[int, ...]
    leap_month: int | None
    leap_month_length_days: int | None


def jdn(dd: int, mm: int, yy: int) -> int:
    a = int((14 - mm) / 12)
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = (
        dd
        + int((153 * m + 2) / 5)
        + 365 * y
        + int(y / 4)
        - int(y / 100)
        + int(y / 400)
        - 32045
    )
    return jd


def decode_lunar_year(yy: int, year_info: LunarYearInfo) -> list[LunarDate]:
    solar_ny = jdn(1, 1, yy)
    current_jd = solar_ny + year_info.tet_offset_days
    ly = []

    if year_info.leap_month is None:
        for mm in range(1, 13):
            ly.append(LunarDate(1, mm, yy, False, current_jd))
            current_jd += year_info.regular_month_lengths[mm - 1]
    else:
        for mm in range(1, year_info.leap_month + 1):
            ly.append(LunarDate(1, mm, yy, False, current_jd))
            current_jd += year_info.regular_month_lengths[mm - 1]
        ly.append(LunarDate(1, year_info.leap_month, yy, True, current_jd))
        if year_info.leap_month_length_days is None:
            raise ValueError(f"Lunar year {yy} has a leap month without a length")
        current_jd += year_info.leap_month_length_days
        for mm in range(year_info.leap_month + 1, 13):
            ly.append(LunarDate(1, mm, yy, False, current_jd))
            current_jd += year_info.regular_month_lengths[mm - 1]

    return ly


@cache
def _load_lunar_years() -> dict[int, LunarYearInfo]:
    raw = yaml.safe_load(LUNAR_YEARS_PATH.read_text(encoding="utf-8"))
    return {
        int(year): _parse_lunar_year_info(year, year_info)
        for year, year_info in raw["years"].items()
    }


def _parse_lunar_year_info(year: Any, raw: dict[str, Any]) -> LunarYearInfo:
    regular_month_lengths = tuple(
        int(length) for length in raw["regular_month_lengths"]
    )
    if len(regular_month_lengths) != 12:
        raise ValueError(f"Lunar year {year} must define 12 regular month lengths")

    leap_month = raw["leap_month"]
    leap_month_length_days = raw["leap_month_length_days"]
    return LunarYearInfo(
        tet_offset_days=int(raw["tet_offset_days"]),
        regular_month_lengths=regular_month_lengths,
        leap_month=int(leap_month) if leap_month is not None else None,
        leap_month_length_days=(
            int(leap_month_length_days) if leap_month_length_days is not None else None
        ),
    )


def _lunar_year_info(year: int) -> LunarYearInfo:
    if year < MIN_SUPPORTED_YEAR or year > MAX_SUPPORTED_YEAR:
        raise ValueError(
            f"Can not transform year {year}; supported range is "
            f"{MIN_SUPPORTED_YEAR}-{MAX_SUPPORTED_YEAR}"
        )
    return _load_lunar_years()[year]


def get_year_info(year: int) -> list[LunarDate]:
    return decode_lunar_year(year, _lunar_year_info(year))


def find_lunar_date(jd: int, ly: list[LunarDate]) -> LunarDate:
    i = len(ly) - 1
    while jd < ly[i].julian_day_number:
        i -= 1

    off = jd - ly[i].julian_day_number
    return LunarDate(
        ly[i].day + off,
        ly[i].month,
        ly[i].year,
        ly[i].is_leap_month,
        jd,
    )


def get_lunar_date(day: int, month: int, year: int) -> LunarDate:
    ly = get_year_info(year)

    jd = jdn(day, month, year)

    if jd < ly[0].julian_day_number:
        ly = get_year_info(year - 1)

    return find_lunar_date(jd, ly)


def solar_to_lunar_date(time: dt.datetime) -> LunarDate:
    """Convert a solar datetime to the Vietnamese lunar date.

    The conversion uses precomputed lunar year data for years 1800-2199.
    Timezone and hour-boundary rules are handled by callers before conversion.
    """
    return get_lunar_date(time.day, time.month, time.year)
