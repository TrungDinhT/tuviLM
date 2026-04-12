import datetime as dt
from dataclasses import dataclass
import pydantic
from typing import Literal
from enum import StrEnum

from src.external_lib.day_from_js import LunarDate, get_lunar_date
from src.refactored.component.cuc import Cuc, LIST_CUC
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

    def get_thien_can(self) -> ThienCan:
        return self.year.thien_can

    def get_dia_chi(self) -> DiaChi:
        return self.year.dia_chi


@dataclass(frozen=True)
class LaSoContext:
    prior: LaSoPrior
    menh_position: DiaChi

    @classmethod
    def from_prior(cls, prior: LaSoPrior) -> "LaSoContext":
        menh_position = _get_menh_position(prior)
        return cls(prior=prior, menh_position=menh_position)

    def get_am_duong(self) -> LuongNghi:
        return LuongNghi(self.prior.year.dia_chi.index % 2)

    def van_direction(self) -> Literal[1, -1]:
        return (
            1
            if (
                self.prior.gender == Gender.MALE
                and self.get_am_duong() == LuongNghi.DUONG
            )
            or (
                self.prior.gender == Gender.FEMALE
                and self.get_am_duong() == LuongNghi.AM
            )
            else -1
        )

    @property
    def cuc(self) -> Cuc:
        return _get_cuc(self.prior, self.menh_position)


def _get_menh_position(prior: LaSoPrior) -> DiaChi:
    month_anchor = DiaChi.DAN + (prior.month - 1)
    return month_anchor - prior.hour.index


def _get_cuc(prior: LaSoPrior, menh_position: DiaChi) -> Cuc:
    cuc_index_orders = {
        ThienCan.GIAP: [0, 4, 1, 3, 2],
        ThienCan.KY: [0, 4, 1, 3, 2],
        ThienCan.AT: [4, 3, 2, 1, 0],
        ThienCan.CANH: [4, 3, 2, 1, 0],
        ThienCan.BINH: [3, 1, 0, 2, 4],
        ThienCan.TAN: [3, 1, 0, 2, 4],
        ThienCan.DINH: [1, 2, 4, 0, 3],
        ThienCan.NHAM: [1, 2, 4, 0, 3],
        ThienCan.MAU: [2, 0, 3, 4, 1],
        ThienCan.QUY: [2, 0, 3, 4, 1],
    }
    cuc_group = _match_cuc_group(menh_position)
    cuc_index = cuc_index_orders[prior.get_thien_can()][cuc_group]
    return LIST_CUC[cuc_index]


def _match_cuc_group(menh_position: DiaChi) -> int:
    if menh_position in (DiaChi.TY, DiaChi.SUU):
        return 0
    if menh_position in (DiaChi.DAN, DiaChi.MEO, DiaChi.TUAT, DiaChi.HOI):
        return 1
    if menh_position in (DiaChi.THIN, DiaChi.TI):
        return 2
    if menh_position in (DiaChi.NGO, DiaChi.MUI):
        return 3
    if menh_position in (DiaChi.THAN, DiaChi.DAU):
        return 4
    raise ValueError(f"Unsupported menh position for cuc: {menh_position}")
