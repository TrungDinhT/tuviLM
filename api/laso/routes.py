from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, HTTPException

from api._parse import to_cung_payload_map
from api.chat.models import BirthInfo
from api.schemas import (
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
)
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.view.builder import build_laso_view


router = APIRouter(prefix="/api/v1/laso")


def _solar_datetime(payload: BirthInfo) -> dt.datetime:
    try:
        return dt.datetime(
            year=payload.year,
            month=payload.month,
            day=payload.day,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _build_la_so(payload: BirthInfo) -> LaSo:
    prior = LaSoPrior.from_solar_day(
        _solar_datetime(payload),
        Gender.MALE if payload.gender == "M" else Gender.FEMALE,
    )
    return LaSo.from_prior(prior)


@router.post("/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest) -> BuildLasoResponse:
    la_so = _build_la_so(payload)
    la_so_view = build_laso_view(la_so, study_year=dt.datetime.now().year)

    summary = (
        f"Sinh dương lịch: "
        f"{payload.day:02d}/{payload.month:02d}/{payload.year} {payload.hour:02d}:00"
    )
    response_id = (
        f"{payload.year:04d}{payload.month:02d}"
        f"{payload.day:02d}{payload.hour:02d}{payload.gender}"
    )

    return BuildLasoResponse(
        id=response_id,
        summary=summary,
        ban_menh_name=la_so_view.ban_menh_name,
        cuc_name=la_so_view.cuc_name,
        menh_cuc_relation_label=la_so_view.menh_cuc_relation_label,
        cung_by_position=to_cung_payload_map(la_so_view),
    )


@router.post("/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest) -> BuildSaoLuuResponse:
    la_so = _build_la_so(payload.birth_info)
    observed_solar_dt = _solar_datetime(payload.observation_time)
    la_so_view = build_laso_view(la_so, study_year=observed_solar_dt.year)

    return BuildSaoLuuResponse(
        cung_by_position=to_cung_payload_map(la_so_view),
    )
