from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from typing import Mapping

from src.refactored.component.elementary import DiaChi, ThienCan
from src.refactored.context.natal import NatalContext
from src.refactored.context.period_focus import (
    PeriodFocusMaps,
    TenYearRange,
    luu_nien_dai_han_focus_position,
)
from src.refactored.context.prior import LunarYear
from src.refactored.cung import CungId
from src.refactored.placement.layer import (
    DaiHanLayerId,
    LayerId,
    LuuNienDaiHanLayerId,
    TieuHanLayerId,
)


class PeriodKind(StrEnum):
    TIEU_HAN = "tieu_han"
    DAI_HAN = "dai_han"
    LUU_NIEN_DAI_HAN = "luu_nien_dai_han"


def build_period_context(
    *,
    kind: PeriodKind,
    year: int,
    natal_context: NatalContext,
    focus_maps: PeriodFocusMaps,
    cung_ids: Mapping[DiaChi, CungId],
) -> TieuHanContext | DaiHanContext | LuuNienDaiHanContext:
    if kind is PeriodKind.TIEU_HAN:
        return TieuHanContext.from_focus_maps(
            natal_context=natal_context,
            year=year,
            focus_maps=focus_maps,
        )
    if kind is PeriodKind.DAI_HAN:
        return DaiHanContext.from_focus_maps(
            natal_context=natal_context,
            year=year,
            focus_maps=focus_maps,
            cung_ids=cung_ids,
        )
    if kind is PeriodKind.LUU_NIEN_DAI_HAN:
        dai_han_context = DaiHanContext.from_focus_maps(
            natal_context=natal_context,
            year=year,
            focus_maps=focus_maps,
            cung_ids=cung_ids,
        )
        return LuuNienDaiHanContext.from_dai_han_context(
            natal_context=natal_context,
            year=year,
            dai_han_context=dai_han_context,
        )
    raise ValueError(f"Unsupported period kind: {kind!r}")


@dataclass(frozen=True)
class TieuHanContext:
    year: int
    focus_position: DiaChi

    @classmethod
    def from_focus_maps(
        cls,
        *,
        natal_context: NatalContext,
        year: int,
        focus_maps: PeriodFocusMaps,
    ) -> TieuHanContext:
        lunar_year = LunarYear.from_year(year)
        return cls(
            year=year,
            focus_position=focus_maps.tieu_han[lunar_year.dia_chi],
        )

    @property
    def layer_id(self) -> LayerId:
        return TieuHanLayerId(year=self.year)

    @cached_property
    def lunar_year(self) -> LunarYear:
        return LunarYear.from_year(self.year)

    @property
    def dia_chi(self) -> DiaChi:
        return self.lunar_year.dia_chi

    @property
    def thien_can(self) -> ThienCan:
        return self.lunar_year.thien_can


@dataclass(frozen=True)
class DaiHanContext:
    age_range: TenYearRange
    focus_position: DiaChi
    thien_can: ThienCan

    @classmethod
    def from_focus_maps(
        cls,
        *,
        natal_context: NatalContext,
        year: int,
        focus_maps: PeriodFocusMaps,
        cung_ids: Mapping[DiaChi, CungId],
    ) -> DaiHanContext:
        age = natal_context.age(year)
        age_range = focus_maps.dai_han.range_for_age(age)
        focus_position = focus_maps.dai_han[age]
        return cls(
            age_range=age_range,
            focus_position=focus_position,
            thien_can=cung_ids[focus_position].thien_can,
        )

    @property
    def layer_id(self) -> LayerId:
        return DaiHanLayerId(
            start_age=self.age_range.start_age,
            end_age=self.age_range.end_age,
        )

    @property
    def menh_position(self) -> DiaChi:
        return self.focus_position


@dataclass(frozen=True)
class LuuNienDaiHanContext:
    year: int
    focus_position: DiaChi

    @classmethod
    def from_dai_han_context(
        cls,
        *,
        natal_context: NatalContext,
        year: int,
        dai_han_context: DaiHanContext,
    ) -> LuuNienDaiHanContext:
        age = natal_context.age(year)
        return cls(
            year=year,
            focus_position=luu_nien_dai_han_focus_position(
                dai_han_focus_position=dai_han_context.focus_position,
                dai_han_start_age=dai_han_context.age_range.start_age,
                current_age=age,
                van_direction=natal_context.van_direction,
            ),
        )

    @property
    def layer_id(self) -> LayerId:
        return LuuNienDaiHanLayerId(year=self.year)

    @cached_property
    def lunar_year(self) -> LunarYear:
        return LunarYear.from_year(self.year)

    @property
    def menh_position(self) -> DiaChi:
        return self.focus_position
