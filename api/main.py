from __future__ import annotations

import datetime as dt
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    AnalyzeCungRequest,
    AnalyzeCungResponse,
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
    CungPayload,
    ChatRequest,
    ChatResponse,
    StarPayload,
)
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.tuvi.birth import TuviTime
from src.tuvi.builder import Builder
from src.tuvi.tinh_ban import TinhBan

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    force=True,
)


@dataclass(slots=True)
class ApiState:
    agent_deps: TuviAgentDeps

    @property
    def has_tinh_ban(self) -> bool:
        return self.agent_deps.tinh_ban is not None

    def set_tinh_ban(self, tinh_ban: TinhBan) -> None:
        self.agent_deps.tinh_ban = tinh_ban

    def require_tinh_ban(self) -> TinhBan:
        return self.agent_deps.require_tinh_ban()


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_deps = TuviAgentDeps()
    agent_deps.agent = build_tuvi_agent()
    app.state.api_state = ApiState(
        agent_deps=agent_deps,
    )
    yield


app = FastAPI(title="TuviLM API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_api_state(request: Request) -> ApiState:
    return request.app.state.api_state


@app.get("/api/v1/health")
def health(request: Request) -> dict[str, str | bool]:
    api_state = get_api_state(request)
    return {
        "status": "ok",
        "tinh_ban_created": api_state.has_tinh_ban,
    }


def _to_cung_payload_map(tinh_ban: TinhBan) -> dict[str, CungPayload]:
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
            age_daivan=cung.age_daivan,
            saoLuu=[
                StarPayload(
                    name=star.name,
                    display=star.star_name_with_status(position),
                    element=star.elemental,
                )
                for star in cung.saoLuu
            ],
        )
    return cung_by_position


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest, request: Request) -> BuildLasoResponse:
    try:
        solar_dt = dt.datetime(
            year=payload.year,
            month=payload.month,
            day=payload.date,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    birth_time = TuviTime.from_solar_day(solar_dt, payload.gender)
    tinh_ban = Builder().build(birth_time)
    get_api_state(request).set_tinh_ban(tinh_ban)

    cung_by_position = _to_cung_payload_map(tinh_ban)

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
        tinhBan=tinh_ban,
        cung_by_position=cung_by_position,
    )


@app.post("/api/v1/laso/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest, request: Request) -> BuildSaoLuuResponse:
    try:
        observed_solar_dt = dt.datetime(
            year=payload.observation_time.year,
            month=payload.observation_time.month,
            day=payload.observation_time.date,
            hour=payload.observation_time.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    observed_time = TuviTime.from_solar_day(observed_solar_dt, payload.observation_time.gender)

    builder = Builder()
    builder.tinhBan = payload.tinhBan
    tinh_ban = builder.build_current_year(observed_time)
    get_api_state(request).set_tinh_ban(tinh_ban)

    return BuildSaoLuuResponse(
        tinhBan=tinh_ban,
        cung_by_position=_to_cung_payload_map(tinh_ban),
    )


@app.post("/api/v1/laso/analyze", response_model=AnalyzeCungResponse)
def analyze_cung(payload: AnalyzeCungRequest, request: Request) -> AnalyzeCungResponse:
    api_state = get_api_state(request)

    try:
        tinh_ban = api_state.require_tinh_ban()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

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


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_dummy(payload: ChatRequest, request: Request) -> ChatResponse:
    api_state = get_api_state(request)
    if not api_state.has_tinh_ban:
        return ChatResponse(
            answer="TinhBan chưa được tạo trong state.",
        )

    agent = api_state.agent_deps.require_agent()
    result = await agent.run(payload.message, deps=api_state.agent_deps)
    return ChatResponse(
        answer=result.output,
    )
