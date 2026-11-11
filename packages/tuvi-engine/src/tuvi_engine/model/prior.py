import datetime as dt
from enum import StrEnum
from functools import cached_property

import pydantic

from src.refactored.calendar import solar_to_lunar_date
from src.refactored.model.elementary import DiaChi, ThienCan


class LunarYear(pydantic.BaseModel):
    dia_chi: DiaChi
    thien_can: ThienCan

    model_config = {"frozen": True}

    @classmethod
    def from_year(cls, year: int) -> "LunarYear":
        dia_chi = DiaChi.from_index(year + 8)
        thien_can = ThienCan.from_index(year + 6)
        return cls(
            dia_chi=dia_chi,
            thien_can=thien_can,
        )


class Gender(StrEnum):
    MALE = "Nam"
    FEMALE = "Nữ"


class LaSoPrior(pydantic.BaseModel):
    hour: DiaChi
    date: int
    month: int
    year: int

    gender: Gender

    model_config = {"frozen": True}

    @cached_property
    def lunar_year(self) -> LunarYear:
        return LunarYear.from_year(self.year)

    @classmethod
    def from_solar_day(cls, time: dt.datetime, gender: Gender) -> "LaSoPrior":
        is_tomorrow = False

        # Move to tomorrow if 23h
        if time.hour == 23:
            time += dt.timedelta(days=1)
            is_tomorrow = True

        if is_tomorrow or time.hour == 0:
            hour = DiaChi.TY
        else:
            hour = DiaChi.from_index((time.hour + 1) // 2)

        lunar_date = solar_to_lunar_date(time)

        return cls(
            hour=hour,
            date=lunar_date.day,
            month=lunar_date.month,
            year=lunar_date.year,
            gender=gender,
        )

    @property
    def thien_can(self) -> ThienCan:
        return self.lunar_year.thien_can

    @property
    def dia_chi(self) -> DiaChi:
        return self.lunar_year.dia_chi
