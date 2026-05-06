from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, TypeAlias

from src.refactored.component.elementary import CircleDirection, DiaChi
from src.refactored.placement.transforms import get_xung_chieu

if TYPE_CHECKING:
    from src.refactored.component.cuc import Cuc
    from src.refactored.context.natal import NatalContext


@dataclass(frozen=True, order=True)
class TenYearRange:
    start_age: int

    @property
    def end_age(self) -> int:
        return self.start_age + 9

    def contains(self, age: int) -> bool:
        return self.start_age <= age <= self.end_age

    @classmethod
    def from_age(cls, *, age: int, first_start_age: int) -> TenYearRange:
        if age < first_start_age:
            raise ValueError(
                f"Age {age} is lower than first Dai Han start age {first_start_age}."
            )
        offset = (age - first_start_age) // 10
        return cls(start_age=first_start_age + offset * 10)


TieuHanFocusMap: TypeAlias = Mapping[DiaChi, DiaChi]


@dataclass(frozen=True)
class DaiHanFocusMap:
    first_start_age: int
    by_range: Mapping[TenYearRange, DiaChi]

    def __getitem__(self, age: int) -> DiaChi:
        return self.focus_position_for_age(age)

    def focus_position_for_age(self, age: int) -> DiaChi:
        return self.by_range[self.range_for_age(age)]

    def range_for_age(self, age: int) -> TenYearRange:
        return TenYearRange.from_age(
            age=age,
            first_start_age=self.first_start_age,
        )


@dataclass(frozen=True)
class PeriodFocusMaps:
    tieu_han: TieuHanFocusMap
    dai_han: DaiHanFocusMap


def build_period_focus_maps(natal_context: NatalContext) -> PeriodFocusMaps:
    return PeriodFocusMaps(
        tieu_han=build_tieu_han_focus_map(
            natal_year_dia_chi=natal_context.dia_chi,
            van_direction=natal_context.van_direction,
        ),
        dai_han=build_dai_han_focus_map(
            cuc=natal_context.cuc,
            menh_position=natal_context.menh_position,
            van_direction=natal_context.van_direction,
        ),
    )


def build_tieu_han_focus_map(
    *,
    natal_year_dia_chi: DiaChi,
    van_direction: CircleDirection,
) -> TieuHanFocusMap:
    anchor_position = tieu_han_anchor_position(natal_year_dia_chi)
    return {
        natal_year_dia_chi + offset: anchor_position + offset * van_direction
        for offset in range(len(DiaChi))
    }


def build_dai_han_focus_map(
    *,
    cuc: Cuc,
    menh_position: DiaChi,
    van_direction: CircleDirection,
) -> DaiHanFocusMap:
    by_range = {
        TenYearRange(start_age=cuc.number + offset * 10): (
            menh_position + van_direction * offset
        )
        for offset, _dia_chi in enumerate(DiaChi)
    }
    return DaiHanFocusMap(first_start_age=cuc.number, by_range=by_range)


def tieu_han_anchor_position(natal_year_dia_chi: DiaChi) -> DiaChi:
    if natal_year_dia_chi in (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT):
        return DiaChi.THIN
    if natal_year_dia_chi in (DiaChi.THAN, DiaChi.TY, DiaChi.THIN):
        return DiaChi.TUAT
    if natal_year_dia_chi in (DiaChi.TI, DiaChi.DAU, DiaChi.SUU):
        return DiaChi.MUI
    if natal_year_dia_chi in (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI):
        return DiaChi.SUU
    raise ValueError(f"Unsupported natal year DiaChi: {natal_year_dia_chi!r}")


def luu_nien_dai_han_focus_position(
    *,
    dai_han_focus_position: DiaChi,
    dai_han_start_age: int,
    current_age: int,
    van_direction: CircleDirection,
) -> DiaChi:
    delta = current_age - dai_han_start_age
    if delta < 0:
        raise ValueError(
            "Current age must not be lower than Dai Han start age: "
            f"{current_age} < {dai_han_start_age}"
        )
    if delta == 0:
        return dai_han_focus_position

    xung_chieu_position = get_xung_chieu(dai_han_focus_position)
    if delta == 1:
        return xung_chieu_position

    return xung_chieu_position + van_direction * (delta - 3)
