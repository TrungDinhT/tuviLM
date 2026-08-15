from __future__ import annotations

import datetime as dt
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime

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
from api.llm import build_qwen_openrouter_model
from api.schemas import (
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
)
from api.settings import get_settings
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.agent.workflow.personality.agent import build_personality_agent
from src.agent.workflow.strength_weakness.agent import (
    build_strength_weakness_agent,
)
from src.refactored.la_so import LaSo
from src.refactored.model.prior import Gender, LaSoPrior
from src.refactored.view.builder import build_laso_view


logger = logging.getLogger(__name__)

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
    model = build_qwen_openrouter_model()
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


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest, request: Request) -> BuildLasoResponse:
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

    # TODO : This is inefficient as we are building the LaSo and LaSoView again in the agent deps.
    # We should refactor to build it only once and reuse.
    la_so = LaSo.from_prior(prior)
    la_so_view = build_laso_view(la_so, study_year=datetime.now().year)
    get_api_state(request).set_la_so(la_so)

    cung_by_position = to_cung_payload_map(la_so_view)

    # TODO : How to use view to extract general summary about the LaSo?
    summary = f"Sinh dương lịch: {payload.day:02d}/{payload.month:02d}/{payload.year} {payload.hour:02d}:00"

    response_id = f"{payload.year:04d}{payload.month:02d}{payload.day:02d}{payload.hour:02d}{payload.gender}"

    return BuildLasoResponse(
        id=response_id,
        summary=summary,
        ban_menh_name=la_so_view.ban_menh_name,
        cuc_name=la_so_view.cuc_name,
        menh_cuc_relation_label=la_so_view.menh_cuc_relation_label,
        cung_by_position=cung_by_position,
    )


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
