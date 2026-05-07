from __future__ import annotations

import datetime as dt
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
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
    ChatToolCall,
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
    agent_deps = TuviAgentDeps(book_root="./data/tuvitanbien_chunking_compact/part_2")
    agent_deps.agent = build_tuvi_agent(model="openai:gpt-5.4-mini")
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


def _json_safe(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    try:
        return jsonable_encoder(value)
    except Exception:
        return repr(value)


def _get_field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _get_tool_args(part: Any) -> Any:
    args_as_dict = getattr(part, "args_as_dict", None)
    if callable(args_as_dict):
        try:
            return args_as_dict()
        except Exception:
            pass

    args_as_json_str = getattr(part, "args_as_json_str", None)
    if callable(args_as_json_str):
        try:
            return args_as_json_str()
        except Exception:
            pass

    return _get_field(part, "args")


def _extract_tool_calls(result: Any) -> list[ChatToolCall]:
    get_messages = getattr(result, "new_messages", None)
    if not callable(get_messages):
        get_messages = getattr(result, "all_messages", None)

    messages = get_messages() if callable(get_messages) else []
    tool_calls: list[ChatToolCall] = []

    for message in messages:
        for part in _get_field(message, "parts", []):
            part_kind = _get_field(part, "part_kind") or _get_field(part, "kind")
            tool_name = _get_field(part, "tool_name")
            args = _get_tool_args(part)

            if not tool_name:
                continue
            if part_kind and part_kind not in {"tool-call", "tool_call"}:
                continue
            if args is None:
                continue

            tool_calls.append(
                ChatToolCall(
                    id=_get_field(part, "tool_call_id"),
                    name=tool_name,
                    arguments=_json_safe(args),
                )
            )

    return tool_calls


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
        tool_calls=_extract_tool_calls(result),
    )
