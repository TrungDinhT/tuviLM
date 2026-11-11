from __future__ import annotations

from typing import Mapping

from src.refactored.context.protocol import PlacementContext
from src.refactored.model.elementary import DiaChi, NguHanh, ThienCan
from src.refactored.placement.registry import AbsolutePositionResolver

ThienCanPositionMap = Mapping[ThienCan, DiaChi]


def menh_position_fn(context: PlacementContext) -> DiaChi:
    return context.menh_position


def tuvi_position_fn(context: PlacementContext) -> DiaChi:
    """An Tử Vi khởi tại Dần, tính theo ngày sinh và cục số."""
    cuc_number = context.cuc.number
    date = context.prior.date

    mod = date % cuc_number
    if mod == 0:
        div = date // cuc_number
        borrow = 0
    else:
        div = date // cuc_number + 1
        borrow = cuc_number - mod

    offset = (div - 1 + borrow) if borrow % 2 == 0 else (div - 1 - borrow)
    return DiaChi.DAN + offset


def thai_tue_position_fn(context: PlacementContext) -> DiaChi:
    return context.dia_chi


def loc_ton_position_fn(context: PlacementContext) -> DiaChi:
    position_fn = position_by_thien_can(
        {
            ThienCan.GIAP: DiaChi.DAN,
            ThienCan.AT: DiaChi.MEO,
            ThienCan.BINH: DiaChi.TI,
            ThienCan.DINH: DiaChi.NGO,
            ThienCan.MAU: DiaChi.TI,
            ThienCan.KY: DiaChi.NGO,
            ThienCan.CANH: DiaChi.THAN,
            ThienCan.TAN: DiaChi.DAU,
            ThienCan.NHAM: DiaChi.HOI,
            ThienCan.QUY: DiaChi.TY,
        }
    )
    return position_fn(context)


def dau_quan_position_fn(context: PlacementContext) -> DiaChi:
    month_position = context.dia_chi - (context.prior.month - 1)
    return month_position + context.prior.hour.index


def trang_sinh_position_fn(context: PlacementContext) -> DiaChi:
    return {
        NguHanh.KIM: DiaChi.TI,
        NguHanh.MOC: DiaChi.HOI,
        NguHanh.HOA: DiaChi.DAN,
        NguHanh.THO: DiaChi.THAN,
        NguHanh.THUY: DiaChi.THAN,
    }[context.cuc.ngu_hanh]


def triet_positions_fn(context: PlacementContext) -> tuple[DiaChi, DiaChi]:
    positions: dict[ThienCan, tuple[DiaChi, DiaChi]] = {
        ThienCan.GIAP: (DiaChi.THAN, DiaChi.DAU),
        ThienCan.AT: (DiaChi.NGO, DiaChi.MUI),
        ThienCan.BINH: (DiaChi.THIN, DiaChi.TI),
        ThienCan.DINH: (DiaChi.DAN, DiaChi.MEO),
        ThienCan.MAU: (DiaChi.TY, DiaChi.SUU),
        ThienCan.KY: (DiaChi.THAN, DiaChi.DAU),
        ThienCan.CANH: (DiaChi.NGO, DiaChi.MUI),
        ThienCan.TAN: (DiaChi.THIN, DiaChi.TI),
        ThienCan.NHAM: (DiaChi.DAN, DiaChi.MEO),
        ThienCan.QUY: (DiaChi.TY, DiaChi.SUU),
    }
    return positions[context.thien_can]


def tuan_positions_fn(context: PlacementContext) -> tuple[DiaChi, DiaChi]:
    positions: dict[DiaChi, tuple[DiaChi, DiaChi]] = {
        DiaChi.TY: (DiaChi.TUAT, DiaChi.HOI),
        DiaChi.DAN: (DiaChi.TY, DiaChi.SUU),
        DiaChi.THIN: (DiaChi.DAN, DiaChi.MEO),
        DiaChi.NGO: (DiaChi.THIN, DiaChi.TI),
        DiaChi.THAN: (DiaChi.NGO, DiaChi.MUI),
        DiaChi.TUAT: (DiaChi.THAN, DiaChi.DAU),
    }
    return positions[context.dia_chi - context.thien_can.index]


def position_by_thien_can(
    mapping: ThienCanPositionMap,
) -> AbsolutePositionResolver:
    return lambda context: mapping[context.thien_can]

