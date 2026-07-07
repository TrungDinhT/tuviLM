from __future__ import annotations

import datetime as dt

from fastapi import HTTPException

from api.chat.models import BirthInfo
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.prior import Gender, LaSoPrior


DIA_CHI_LABELS: dict[DiaChi, str] = {
    DiaChi.TY: "Tý",
    DiaChi.SUU: "Sửu",
    DiaChi.DAN: "Dần",
    DiaChi.MEO: "Mão",
    DiaChi.THIN: "Thìn",
    DiaChi.TI: "Tỵ",
    DiaChi.NGO: "Ngọ",
    DiaChi.MUI: "Mùi",
    DiaChi.THAN: "Thân",
    DiaChi.DAU: "Dậu",
    DiaChi.TUAT: "Tuất",
    DiaChi.HOI: "Hợi",
}


def solar_datetime(payload: BirthInfo) -> dt.datetime:
    if payload.hour is None:
        raise HTTPException(status_code=422, detail="Vui lòng nhập giờ sinh dương lịch")
    try:
        return dt.datetime(
            year=payload.year,
            month=payload.month,
            day=payload.day,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def build_la_so(payload: BirthInfo) -> LaSo:
    gender = Gender.MALE if payload.gender == "M" else Gender.FEMALE
    try:
        if payload.calendar == "lunar":
            if payload.hour_in_dia_chi is None:
                raise ValueError("Vui lòng chọn giờ sinh theo Địa Chi")
            prior = LaSoPrior.from_lunar_day(
                year=payload.year,
                month=payload.month,
                day=payload.day,
                hour=payload.hour_in_dia_chi,
                gender=gender,
                is_leap_month=payload.is_leap_month,
            )
        else:
            prior = LaSoPrior.from_solar_day(solar_datetime(payload), gender)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return LaSo.from_prior(prior)


def birth_summary(payload: BirthInfo) -> str:
    if payload.calendar == "lunar":
        if payload.hour_in_dia_chi is None:
            raise HTTPException(status_code=422, detail="Vui lòng chọn giờ sinh theo Địa Chi")
        leap = " nhuận" if payload.is_leap_month else ""
        return (
            f"Sinh âm lịch: {payload.day:02d}/{payload.month:02d}{leap}/"
            f"{payload.year} giờ {DIA_CHI_LABELS[payload.hour_in_dia_chi]}"
        )

    if payload.hour is None:
        raise HTTPException(status_code=422, detail="Vui lòng nhập giờ sinh dương lịch")
    return (
        f"Sinh dương lịch: "
        f"{payload.day:02d}/{payload.month:02d}/{payload.year} {payload.hour:02d}:00"
    )


def birth_response_id(payload: BirthInfo) -> str:
    leap = "L" if payload.is_leap_month else "R"
    hour = payload.hour_in_dia_chi.value if payload.calendar == "lunar" else payload.hour
    return (
        f"{payload.calendar}-{payload.year:04d}{payload.month:02d}"
        f"{payload.day:02d}-{leap}-{hour}-{payload.gender}"
    )
