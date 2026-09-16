from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from api.runs.models import RunSnapshot
from api.runs.service import RunService

router = APIRouter(prefix="/api/v1")


class SubmitRun(BaseModel):
    workflow: str = Field(min_length=1, max_length=128)
    inputs: dict[str, Any]


def service(request: Request) -> RunService:
    return request.app.state.run_service


@router.post("/runs", response_model=RunSnapshot, status_code=202)
async def submit_run(payload: SubmitRun, request: Request,
                     owner_id: str = Header(alias="X-Anonymous-Owner-Id", min_length=1),
                     idempotency_key: str = Header(alias="Idempotency-Key", min_length=1)):
    try:
        run = await service(request).submit(
            workflow=payload.workflow, inputs=payload.inputs, owner_id=owner_id,
            idempotency_key=idempotency_key,
        )
    except ValidationError as exc:
        raise HTTPException(422, "Invalid workflow inputs") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return run.snapshot()


@router.get("/runs", response_model=list[RunSnapshot])
async def latest_runs(request: Request, workflow: str, resource_id: str,
                      owner_id: str = Header(alias="X-Anonymous-Owner-Id", min_length=1)):
    run = await service(request).store.latest(owner_id, workflow, resource_id)
    return [run.snapshot()] if run else []


@router.get("/runs/{run_id}", response_model=RunSnapshot)
async def get_run(run_id: str, request: Request,
                  owner_id: str = Header(alias="X-Anonymous-Owner-Id", min_length=1)):
    return (await service(request).store.get(run_id, owner_id)).snapshot()


@router.post("/runs/{run_id}/cancel", response_model=RunSnapshot)
async def cancel_run(run_id: str, request: Request,
                     owner_id: str = Header(alias="X-Anonymous-Owner-Id", min_length=1)):
    return (await service(request).store.cancel(run_id, owner_id)).snapshot()


class ChatRunBody(BaseModel):
    content: str


@router.post("/sessions/{session_id}/chat/runs", response_model=RunSnapshot, status_code=202)
async def submit_chat_run(session_id: str, payload: ChatRunBody, request: Request,
                          owner_id: str = Header(alias="X-Anonymous-Owner-Id", min_length=1),
                          idempotency_key: str = Header(alias="Idempotency-Key", min_length=1)):
    return await submit_run(SubmitRun(workflow="chat", inputs={
        "session_id": session_id, "content": payload.content,
    }), request, owner_id, idempotency_key)


class PersonalityRunBody(BaseModel):
    request: str = "Luận tính cách của tôi"


@router.post("/chart-profiles/{profile_id}/personality/runs", response_model=RunSnapshot, status_code=202)
async def submit_personality_run(profile_id: str, payload: PersonalityRunBody, request: Request,
                                 owner_id: str = Header(alias="X-Anonymous-Owner-Id", min_length=1),
                                 idempotency_key: str = Header(alias="Idempotency-Key", min_length=1)):
    return await submit_run(SubmitRun(workflow="personality", inputs={
        "chart_profile_id": profile_id, "request": payload.request,
    }), request, owner_id, idempotency_key)
