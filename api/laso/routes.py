from __future__ import annotations

import datetime as dt

from fastapi import APIRouter

from api._parse import to_cung_payload_map
from api.laso.build import birth_response_id, birth_summary, build_la_so, solar_datetime
from api.schemas import (
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
)
from src.refactored.view.builder import build_laso_view


router = APIRouter(prefix="/api/v1/laso")


@router.post("/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest) -> BuildLasoResponse:
    la_so = build_la_so(payload)
    la_so_view = build_laso_view(la_so, study_year=dt.datetime.now().year)

    return BuildLasoResponse(
        id=birth_response_id(payload),
        summary=birth_summary(payload),
        ban_menh_name=la_so_view.ban_menh_name,
        cuc_name=la_so_view.cuc_name,
        menh_cuc_relation_label=la_so_view.menh_cuc_relation_label,
        cung_by_position=to_cung_payload_map(la_so_view),
    )


@router.post("/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest) -> BuildSaoLuuResponse:
    la_so = build_la_so(payload.birth_info)
    observed_solar_dt = solar_datetime(payload.observation_time)
    la_so_view = build_laso_view(la_so, study_year=observed_solar_dt.year)

    return BuildSaoLuuResponse(
        cung_by_position=to_cung_payload_map(la_so_view),
    )
