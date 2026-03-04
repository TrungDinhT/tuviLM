from __future__ import annotations

import datetime as dt

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    AnalyzeCungRequest,
    AnalyzeCungResponse,
    BuildLasoRequest,
    BuildLasoResponse,
    CungPayload,
    DummyChatRequest,
    DummyChatResponse,
    StarPayload,
)
from src.tuvi.birth import BirthTime
from src.tuvi.builder import Builder


app = FastAPI(title="TuviLM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest) -> BuildLasoResponse:
    solar_dt = dt.datetime(
        year=payload.year,
        month=payload.month,
        day=payload.date,
        hour=payload.hour,
    )

    birth_time = BirthTime.from_solar_day(solar_dt, payload.gender)
    tinh_ban = Builder().build(birth_time)

    cung_by_position: dict[str, CungPayload] = {}
    for position, cung in tinh_ban.map_cung.items():
        cung_by_position[position] = CungPayload(
            position=position,
            role=cung.role,
            chinh_tinh=[star.star_name_with_status(position) for star in cung.chinhTinh],
            phu_tinh=[
                StarPayload(
                    name=star.name,
                    display=star.star_name_with_status(position),
                    element=star.elemental,
                )
                for star in cung.phuTinh
            ],
            tuhoa=[tuhoa.name for tuhoa in cung.tuhoa],
            trang_sinh=cung.trang_sinh.name if cung.trang_sinh else None,
            is_tuan=cung.is_tuan,
            is_triet=cung.is_triet,
            is_cung_than=cung.is_cung_than,
        )

    summary = (
        f"Cục: {tinh_ban.cuc.name if tinh_ban.cuc else 'N/A'} | "
        f"Âm Dương: {tinh_ban.am_duong} | "
        f"Giới tính: {payload.gender} | "
        f"Sinh dương lịch: {payload.date:02d}/{payload.month:02d}/{payload.year} {payload.hour:02d}:00"
    )

    response_id = f"{payload.year:04d}{payload.month:02d}{payload.date:02d}{payload.hour:02d}{payload.gender}"

    return BuildLasoResponse(
        id=response_id,
        summary=summary,
        cung_by_position=cung_by_position,
    )


@app.post("/api/v1/laso/analyze", response_model=AnalyzeCungResponse)
def analyze_cung(payload: AnalyzeCungRequest) -> AnalyzeCungResponse:
    try:
        solar_dt = dt.datetime(
            year=payload.year,
            month=payload.month,
            day=payload.date,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    birth_time = BirthTime.from_solar_day(solar_dt, payload.gender)
    tinh_ban = Builder().build(birth_time)

    position = payload.position.strip()
    if position not in tinh_ban.map_cung:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid position '{payload.position}'. Must be one of: {', '.join(tinh_ban.map_cung.keys())}",
        )

    cung = tinh_ban.map_cung[position]

    try:
        from src.agent.cung_analyzer import CungAnalyzer
        analyzer = CungAnalyzer(model=payload.model)
        analysis = analyzer.analyze_cung(position, cung)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cung analysis failed: {exc}") from exc

    return AnalyzeCungResponse(
        position=position,
        role=cung.role,
        analysis=analysis,
    )


@app.post("/api/v1/chat", response_model=DummyChatResponse)
def chat_dummy(payload: DummyChatRequest) -> DummyChatResponse:
    return DummyChatResponse(
        answer=f"Dummy chat route. Received: {payload.message}",
    )
