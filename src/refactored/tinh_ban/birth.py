import datetime as dt
from time import strftime
from lunarcalendar import Converter, Solar
import pydantic

from src.external_lib.day_from_js import LunarDate, get_lunar_date
from src.refactored.element.dia_chi import DiaChi
from src.refactored.element.thien_can import ThienCan
from src.refactored.element.luong_nghi import LuongNghi


class LunarYear(pydantic.BaseModel):
    dia_chi: DiaChi
    thien_can: ThienCan

    @classmethod
    def from_solar_year(cls, lunar_date: LunarDate) -> 'LunarYear':
        dia_chi = DiaChi((lunar_date.year + 8) % 12)
        thien_can = ThienCan((lunar_date.year + 6) % 10)
        return cls(
            dia_chi=dia_chi,
            thien_can=thien_can,
        )


class BirthTime(pydantic.BaseModel):

    hour : DiaChi
    date : int
    month : int
    year: LunarYear

    @classmethod
    def from_solar_day(cls, time : dt.datetime) -> 'BirthTime':

        is_tomorrow = False

        # Move to tomorrow if 23h
        if time.hour == 23 :
            time += dt.timedelta(days=1)
            is_tomorrow = True

        if is_tomorrow or time.hour == 0:
            hour = DiaChi.Ty
        else:
            hour = DiaChi((time.hour + 1) // 2)

        lunar_date = get_lunar_date(time.day, time.month, time.year)

        return cls(
            hour=hour,
            date=lunar_date.day,
            month=lunar_date.month,
            year=LunarYear.from_solar_year(lunar_date),  # type: ignore
        )

    def get_am_duong(self) -> LuongNghi:
        return LuongNghi(self.year.dia_chi.value % 2)

