from __future__ import annotations

import datetime as dt
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api._parse import to_cung_payload_map
from api.chat.contracts import (
    ConversationHistoryError,
    ConversationHistoryStore,
    DuplicateStreamInProgressError,
    IdempotencyConflictError,
    MissingOwnerIdError,
    NotFoundError,
)
from api.chat.routes import router as chat_router
from api.chat.storage.store import MongoConversationHistoryStore
from api.schemas import (
    AmDuongRelationKey,
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
    DiaChiKey,
    MenhCucRelationKey,
    NguHanhKey,
    PreviewLasoRequest,
    PreviewLasoResponse,
)
from api.settings import get_settings
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.agent.tool.ban_menh.laso_foundation import build_laso_foundation_payload
from src.agent.workflow.personality.agent import build_personality_agent
from src.agent.workflow.strength_weakness.agent import (
    build_strength_weakness_agent,
    run_strength_weakness_agent,
)
from src.agent.workflow.strength_weakness.output import (
    CapabilityProfile,
)
from src.refactored.components.definitions.sao import ChinhPhuTinh
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.view.builder import build_laso_view

logger = logging.getLogger(__name__)

# The foundation payload's polarity relation is a Vietnamese phrase; the API
# exposes it as a stable slug so clients can key content off it.
_AM_DUONG_RELATION_KEYS: dict[str, AmDuongRelationKey] = {
    "thuận lý": "thuan_ly",
    "nghịch lý": "nghich_ly",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    force=True,
)


@dataclass(slots=True)
class ApiState:
    agent_deps: TuviAgentDeps
    conversation_history_store: ConversationHistoryStore

    @property
    def has_la_so(self) -> bool:
        return self.agent_deps.la_so is not None

    def set_la_so(self, la_so: LaSo) -> None:
        self.agent_deps.la_so = la_so

    def require_la_so(self) -> LaSo:
        return self.agent_deps.require_la_so()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    conversation_history_store = await MongoConversationHistoryStore.connect(
        settings.conversation_history_store,
    )
    model = "openrouter:qwen/qwen3.7-max"
    agent_deps = TuviAgentDeps(
        agent=build_tuvi_agent(model=model),
        personality_agent=build_personality_agent(model=model),
        strength_weakness_agent=build_strength_weakness_agent(model=model),
        book_root="./data/tuvitanbien_chunking_compact/part_2",
    )
    app.state.api_state = ApiState(
        agent_deps=agent_deps,
        conversation_history_store=conversation_history_store,
    )
    try:
        yield
    finally:
        await conversation_history_store.close()


app = FastAPI(title="TuviLM API", version="0.1.0", lifespan=lifespan)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def log_http_exception(request: Request, exc: StarletteHTTPException):
    _log_http_exception(request, status_code=exc.status_code, detail=exc.detail)
    return await http_exception_handler(request, exc)


@app.exception_handler(ConversationHistoryError)
async def conversation_history_exception_handler(
    request: Request,
    exc: ConversationHistoryError,
):
    status_code, detail = _conversation_history_http_error(exc)
    _log_http_exception(request, status_code=status_code, detail=detail)
    return JSONResponse(status_code=status_code, content={"detail": detail})


def _conversation_history_http_error(exc: ConversationHistoryError) -> tuple[int, str]:
    if isinstance(exc, MissingOwnerIdError):
        return 400, "Owner id is required."
    if isinstance(exc, NotFoundError):
        return 404, "Resource not found."
    if isinstance(exc, IdempotencyConflictError):
        return 409, "Idempotency key conflict."
    if isinstance(exc, DuplicateStreamInProgressError):
        return 409, "Stream already in progress."
    return 500, "Conversation history error."


def _log_http_exception(request: Request, *, status_code: int, detail: object) -> None:
    logger.warning(
        "HTTP exception: method=%s path=%s status_code=%s detail=%r",
        request.method,
        request.url.path,
        status_code,
        detail,
    )


def get_api_state(request: Request) -> ApiState:
    return request.app.state.api_state


@app.get("/api/v1/health")
def health(request: Request) -> dict[str, str | bool]:
    api_state = get_api_state(request)
    return {
        "status": "ok",
        "la_so_created": api_state.has_la_so,
    }


@app.post("/api/v1/laso/preview", response_model=PreviewLasoResponse)
def preview_laso(payload: PreviewLasoRequest) -> PreviewLasoResponse:
    """Return cung Mệnh's chính tinh for the reward preview.

    Side-effect free on purpose: unlike `/laso/build` this does not touch the
    process-wide la-so state, so debounced calls while the user enters birth
    data cannot disturb a previously built chart.
    """
    try:
        solar_dt = dt.datetime(  # noqa: DTZ001
            year=payload.year,
            month=payload.month,
            day=payload.day,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Gender only steers vận direction, never cung Mệnh's chính tinh — a fixed
    # stand-in keeps the preview gender-free.
    prior = LaSoPrior.from_solar_day(solar_dt, Gender.MALE)
    la_so = LaSo.from_prior(prior)

    menh_position = la_so.natal_context.menh_position
    menh_cung = la_so.cung_at(menh_position)
    chinh_tinh: list[str] = []
    for layered_component in menh_cung.components:
        component = la_so.component(layered_component.component_id)
        if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
            chinh_tinh.append(component.name)

    return PreviewLasoResponse(
        chinh_tinh=chinh_tinh,
        menh_position=la_so.catalog.get_dia_chi(menh_position).name,
    )


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest, request: Request) -> BuildLasoResponse:
    la_so = _la_so_from_build_request(payload)

    # TODO : This is inefficient as we are building the LaSo and LaSoView again in the agent deps.
    # We should refactor to build it only once and reuse.
    la_so_view = build_laso_view(la_so, study_year=datetime.now().year)
    get_api_state(request).set_la_so(la_so)

    cung_by_position = to_cung_payload_map(la_so_view)

    # Foundation fields are values the domain already computes — no new
    # derivation here (see laso-build-foundation).
    foundation = build_laso_foundation_payload(la_so)
    am_duong_relation = _AM_DUONG_RELATION_KEYS[
        cast(dict[str, str], foundation["am_duong_thuan_nghich"])["relation"]
    ]

    # TODO : How to use view to extract general summary about the LaSo?
    summary = f"Sinh dương lịch: {payload.day:02d}/{payload.month:02d}/{payload.year} {payload.hour:02d}:00"

    response_id = f"{payload.year:04d}{payload.month:02d}{payload.day:02d}{payload.hour:02d}{payload.gender}"

    return BuildLasoResponse(
        id=response_id,
        summary=summary,
        ban_menh_name=la_so_view.ban_menh_name,
        cuc_name=la_so_view.cuc_name,
        menh_cuc_relation_label=la_so_view.menh_cuc_relation_label,
        menh_cuc_relation=cast(
            MenhCucRelationKey, la_so.menh_cuc_relation().relation_type.value
        ),
        am_duong_relation=am_duong_relation,
        dia_chi_natal_year=cast(DiaChiKey, la_so_view.dia_chi_natal_year.value),
        ban_menh_ngu_hanh=cast(NguHanhKey, la_so.ban_menh.ngu_hanh.value),
        cung_by_position=cung_by_position,
    )


@app.post(
    "/api/v1/laso/strength-weakness",
    response_model=CapabilityProfile,
)
async def analyze_strength_weakness(
    payload: BuildLasoRequest,
    request: Request,
) -> CapabilityProfile:
    """Return a structured capability profile for one explicit birth chart."""
    la_so = _la_so_from_build_request(payload)
    base_deps = get_api_state(request).agent_deps
    workflow_agent = base_deps.require_strength_weakness_agent()
    deps = TuviAgentDeps(
        strength_weakness_agent=workflow_agent,
        la_so=la_so,
        book=base_deps.book,
        book_root=base_deps.book_root,
    )
    return await run_strength_weakness_agent(
        agent=workflow_agent,
        deps=deps,
        request=(
            "Hãy khám phá những điểm mạnh, điểm yếu và mặt trái nổi bật nhất "
            "trong cách tôi sử dụng năng lực của mình."
        ),
    )


def _la_so_from_build_request(payload: BuildLasoRequest) -> LaSo:
    try:
        solar_dt = dt.datetime(
            year=payload.year,
            month=payload.month,
            day=payload.day,
            hour=payload.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    prior = LaSoPrior.from_solar_day(
        solar_dt, Gender.MALE if payload.gender == "M" else Gender.FEMALE
    )
    return LaSo.from_prior(prior)


@app.post("/api/v1/laso/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest, request: Request) -> BuildSaoLuuResponse:
    try:
        observed_solar_dt = dt.datetime(
            year=payload.observation_time.year,
            month=payload.observation_time.month,
            day=payload.observation_time.day,
            hour=payload.observation_time.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    la_so = get_api_state(request).require_la_so()
    la_so_view = build_laso_view(la_so, study_year=observed_solar_dt.year)

    return BuildSaoLuuResponse(
        cung_by_position=to_cung_payload_map(la_so_view),
    )
