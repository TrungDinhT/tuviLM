import datetime as dt
import pydantic
from typing import Literal
from enum import StrEnum

from src.external_lib.day_from_js import LunarDate, get_lunar_date
from src.refactored.component.elementary import DiaChi, LuongNghi, ThienCan


class LunarYear(pydantic.BaseModel):
    dia_chi: DiaChi
    thien_can: ThienCan

    @classmethod
    def from_solar_year(cls, lunar_date: LunarDate) -> "LunarYear":
        dia_chi = DiaChi.from_index(lunar_date.year + 8)
        thien_can = ThienCan.from_index(lunar_date.year + 6)
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
    year: LunarYear

    gender: Gender

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

        lunar_date = get_lunar_date(time.day, time.month, time.year)

        return cls(
            hour=hour,
            date=lunar_date.day,
            month=lunar_date.month,
            year=LunarYear.from_solar_year(lunar_date),  # type: ignore
            gender=gender,
        )

    def get_am_duong(self) -> LuongNghi:
        return LuongNghi(self.year.dia_chi.index % 2)

    def get_thien_can(self) -> ThienCan:
        return self.year.thien_can

    def get_dia_chi(self) -> DiaChi:
        return self.year.dia_chi

    def van_direction(self) -> Literal[1, -1]:
        return (
            1
            if (self.gender == Gender.MALE and self.get_am_duong() == LuongNghi.DUONG)
            or (self.gender == Gender.FEMALE and self.get_am_duong() == LuongNghi.AM)
            else -1
        )
