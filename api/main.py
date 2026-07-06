from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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
from api.laso.routes import router as laso_router
from api.settings import get_settings
from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    conversation_history_store = await MongoConversationHistoryStore.connect(
        settings.conversation_history_store,
    )
    agent_deps = TuviAgentDeps(
        agent=build_tuvi_agent(model="openai:gpt-5.4-mini"),
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
app.include_router(laso_router)

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
def health() -> dict[str, str]:
    return {"status": "ok"}
