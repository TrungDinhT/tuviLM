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
from pydantic_ai.models.openrouter import OpenRouterModelSettings
from pymongo import AsyncMongoClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from tuvi_api._parse import to_cung_payload_map
from tuvi_api.accounts.capability import (
    capability_chart_key,
    ensure_capability_report_indexes,
    find_capability_report,
    reserve_capability_coins,
    save_capability_report,
    settle_capability_coins,
)
from tuvi_api.accounts.routes import router as accounts_router
from tuvi_api.accounts.redeem_codes import (
    ensure_redeem_code_indexes,
    router as redeem_codes_router,
)
from tuvi_api.auth.dependencies import Principal, ReconciledUser
from tuvi_api.auth.rate_limit import RateLimiter
from tuvi_api.auth.routes import router as auth_router
from tuvi_api.auth.store import MongoAuthStore
from tuvi_api.chat.contracts import (
    ConversationHistoryError,
    ConversationHistoryStore,
    DuplicateStreamInProgressError,
    IdempotencyConflictError,
    InsufficientChatCoinsError,
    MissingOwnerIdError,
    NotFoundError,
)
from tuvi_api.chat.models import BirthInfo
from tuvi_api.chat.routes import router as chat_router
from tuvi_api.chat.storage.store import MongoConversationHistoryStore
from tuvi_api.schemas import (
    AmDuongRelationKey,
    BuildLasoRequest,
    BuildLasoResponse,
    BuildSaoLuuRequest,
    BuildSaoLuuResponse,
    CauPhuResponse,
    DiaChiKey,
    MenhCucRelationKey,
    NguHanhKey,
    PreviewLasoRequest,
    PreviewLasoResponse,
)
from tuvi_api.settings import get_settings
from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.main import build_tuvi_agent
from tuvi_agent.tool.ban_menh.laso_foundation import build_laso_foundation_payload
from tuvi_agent.workflow.personality.agent import build_personality_agent
from tuvi_agent.workflow.strength_weakness.agent import (
    build_strength_weakness_agent,
    run_strength_weakness_agent,
)
from tuvi_agent.workflow.strength_weakness.output import (
    CapabilityProfile,
)
from tuvi_engine.cau_phu import (
    CauPhuNotFoundError,
    get_cau_phu,
)
from tuvi_engine.components.definitions.sao import ChinhPhuTinh
from tuvi_engine.la_so import LaSo
from tuvi_engine.model.prior import Gender, LaSoPrior
from tuvi_engine.view.builder import build_laso_view

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.auth.cookie_secure and not settings.auth.email_enabled:
        raise RuntimeError(
            "Set AUTH__RESEND_API_KEY and AUTH__EMAIL_FROM: on https the API must send "
            "verification and password reset emails."
        )
    conversation_history_store = await MongoConversationHistoryStore.connect(
        settings.conversation_history_store,
    )
    model = settings.agent_model
    agent_deps = TuviAgentDeps(
        agent=build_tuvi_agent(model=model),
        personality_agent=build_personality_agent(model=model),
        strength_weakness_agent=build_strength_weakness_agent(
            model=settings.strength_weakness.model,
            model_settings=OpenRouterModelSettings(
                openrouter_provider={
                    "order": [settings.strength_weakness.provider],
                    "allow_fallbacks": settings.strength_weakness.allow_fallbacks,
                    "sort": settings.strength_weakness.provider_sort,
                },
                openrouter_reasoning={"effort": settings.strength_weakness.reasoning_effort},
            ),
        ),
        book_root=settings.book_root,
    )
    app.state.api_state = ApiState(
        agent_deps=agent_deps,
        conversation_history_store=conversation_history_store,
    )
    auth_mongo = AsyncMongoClient(settings.auth.mongo_uri, serverSelectionTimeoutMS=5000)
    app.state.auth_database = auth_mongo[settings.auth.database_name]
    try:
        await MongoAuthStore(app.state.auth_database).ensure_indexes()
        await ensure_redeem_code_indexes(app.state.auth_database)
        await ensure_capability_report_indexes(app.state.auth_database)
        yield
    finally:
        await auth_mongo.close()
        await conversation_history_store.close()


app = FastAPI(title="TuviLM API", version="0.1.0", lifespan=lifespan)
app.state.auth_rate_limiter = RateLimiter()
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(accounts_router)
app.include_router(redeem_codes_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
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
    if isinstance(exc, InsufficientChatCoinsError):
        return 402, "Not enough coins. AI chat costs 3 coins per message."
    return 500, "Conversation history error."


def _log_http_exception(request: Request, *, status_code: int, detail: object) -> None:
    logger.warning(
        "HTTP exception: method=%s path=%s status_code=%s detail=%r",
        request.method,
        request.url.path,
        status_code,
        detail,
    )


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/me")
def me(user: ReconciledUser) -> Principal:
    return user


@app.post("/api/v1/laso/preview", response_model=PreviewLasoResponse)
def preview_laso(payload: PreviewLasoRequest) -> PreviewLasoResponse:
    """Return the main stars for a preview without storing chart state."""
    try:
        solar_dt = dt.datetime(
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


def _build_la_so(birth_info: BirthInfo) -> LaSo:
    try:
        solar_dt = dt.datetime(
            year=birth_info.year,
            month=birth_info.month,
            day=birth_info.day,
            hour=birth_info.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    prior = LaSoPrior.from_solar_day(
        solar_dt, Gender.MALE if birth_info.gender == "M" else Gender.FEMALE
    )
    return LaSo.from_prior(prior)


@app.post("/api/v1/laso/build", response_model=BuildLasoResponse)
def build_laso(payload: BuildLasoRequest) -> BuildLasoResponse:
    la_so = _build_la_so(payload)
    la_so_view = build_laso_view(la_so, study_year=datetime.now().year)

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
    user: ReconciledUser,
) -> CapabilityProfile:
    """Return the account's capability profile for one chart, paid once per chart."""
    la_so = _build_la_so(payload)
    database = request.app.state.auth_database
    chart_key = capability_chart_key(payload)
    saved = await find_capability_report(database, user.user_id, chart_key)
    if saved is not None:
        return saved

    attempt = await reserve_capability_coins(database, user.user_id, chart_key)
    try:
        base_deps = request.app.state.api_state.agent_deps
        workflow_agent = base_deps.require_strength_weakness_agent()
        deps = TuviAgentDeps(
            strength_weakness_agent=workflow_agent,
            la_so=la_so,
            book=base_deps.book,
            book_root=base_deps.book_root,
        )
        report = await run_strength_weakness_agent(
            agent=workflow_agent,
            deps=deps,
            request=(
                "Hãy khám phá những điểm mạnh, điểm yếu và mặt trái nổi bật nhất "
                "trong cách tôi sử dụng năng lực của mình."
            ),
        )
        await save_capability_report(database, user.user_id, chart_key, report)
    except BaseException:
        if attempt is not None:
            await settle_capability_coins(
                database, user.user_id, chart_key, attempt, confirmed=False
            )
        raise
    if attempt is not None:
        await settle_capability_coins(
            database, user.user_id, chart_key, attempt, confirmed=True
        )
    return report


@app.post("/api/v1/laso/cau-phu", response_model=CauPhuResponse)
def read_cau_phu(payload: BuildLasoRequest) -> CauPhuResponse:
    try:
        entry = get_cau_phu(_build_la_so(payload))
    except CauPhuNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return CauPhuResponse(
        vi_tri=entry.vi_tri,
        chinh_tinh=list(entry.chinh_tinh),
        co_tuan=entry.co_tuan,
        co_triet=entry.co_triet,
        tuan_triet=entry.tuan_triet,
        tieu_de=entry.tieu_de,
        cau_phu=entry.cau_phu,
        cac_cau=list(entry.cac_cau),
    )


@app.post("/api/v1/laso/build_sao_luu", response_model=BuildSaoLuuResponse)
def build_sao_luu(payload: BuildSaoLuuRequest) -> BuildSaoLuuResponse:
    try:
        observed_solar_dt = dt.datetime(
            year=payload.observation_time.year,
            month=payload.observation_time.month,
            day=payload.observation_time.day,
            hour=payload.observation_time.hour,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    la_so = _build_la_so(payload.birth_info)
    la_so_view = build_laso_view(la_so, study_year=observed_solar_dt.year)

    return BuildSaoLuuResponse(
        cung_by_position=to_cung_payload_map(la_so_view),
    )
