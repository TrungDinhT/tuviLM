"""Workflow registration. New workflows need no transport or retry code."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request

from api.chat.contracts import NotFoundError
from api.chat.models import ChatMessageStatus
from api.background_runs import RunContext, Workflow


class ChatInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(min_length=1, max_length=128)
    content: str = Field(min_length=1, max_length=32_000)


class PersonalityInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chart_profile_id: str = Field(min_length=1, max_length=128)
    request: str = Field(
        default="Luận tính cách của tôi", min_length=1, max_length=32_000
    )


def registered_workflows(app) -> dict[str, Workflow]:
    # Imports stay here so route registration does not create a circular import.
    from api.chat.routes import _build_la_so, _stream_session_chat_events
    from src.agent.deps import TuviAgentDeps
    from src.agent.workflow.personality.agent import run_personality_workflow

    store = app.state.api_state.conversation_history_store

    async def authorize_chat(owner_id: str, inputs: ChatInputs) -> str:
        await store.load_session_context(owner_id, inputs.session_id)
        return f"session:{inputs.session_id}"

    async def chat(context: RunContext, inputs: ChatInputs):
        session = await store.load_session_context(
            context.run.owner_id, inputs.session_id
        )
        request = Request({"type": "http", "app": app})
        async for event in _stream_session_chat_events(
            request=request,
            context=session,
            content=inputs.content,
            history_messages=list(session.session.messages),
        ):
            if event["type"] == "text":
                if context.run.state.progress is not None:
                    await context.progress(None)
                await context.text(str(event.get("delta", "")))
            elif event["type"] == "tool_call":
                await context.progress(str(event.get("name", "")))
            elif event["type"] == "error":
                raise RuntimeError("Chat generation failed")
        return {"answer": context.run.state.text}

    async def finalize_chat(context: RunContext, inputs: ChatInputs):
        # Reserve when saving the answer so
        # a queued/long-running job is not subject to legacy pending-message expiry.
        pair = await store.reserve_message_pair(
            context.run.owner_id,
            inputs.session_id,
            user_content=inputs.content,
            idempotency_key=f"run:{context.run.id}",
        )
        status = {
            "succeeded": ChatMessageStatus.CONFIRMED,
            "failed": ChatMessageStatus.FAILED,
            "cancelled": ChatMessageStatus.CANCELLED,
        }[context.status]
        await store.finalize_assistant_message(
            context.run.owner_id,
            inputs.session_id,
            pair.assistant_message.id,
            content=context.run.state.text,
            status=status,
        )
        await context.emit(
            "metadata",
            {
                "user_message_id": pair.user_message.id,
                "assistant_message_id": pair.assistant_message.id,
            },
        )

    async def get_profile(owner_id: str, inputs: PersonalityInputs):
        profiles = await store.list_chart_profiles(owner_id)
        profile = next((p for p in profiles if p.id == inputs.chart_profile_id), None)
        if profile is None:
            raise NotFoundError
        return profile

    async def authorize_personality(owner_id: str, inputs: PersonalityInputs) -> str:
        await get_profile(owner_id, inputs)
        return f"personality:{inputs.chart_profile_id}"

    async def personality(context: RunContext, inputs: PersonalityInputs):
        profile = await get_profile(context.run.owner_id, inputs)
        base = app.state.api_state.agent_deps
        deps = TuviAgentDeps(
            agent=base.agent,
            personality_agent=base.personality_agent,
            la_so=_build_la_so(profile.birth_info),
            book=base.book,
            book_root=base.book_root,
        )
        await context.progress("run_tinh_cach_workflow")
        answer = await run_personality_workflow(
            agent=deps.require_personality_agent(),
            deps=deps,
            request=inputs.request,
        )
        await context.text(answer)
        return {"answer": answer}

    return {
        "chat": Workflow(ChatInputs, authorize_chat, chat, finalize_chat),
        "personality": Workflow(PersonalityInputs, authorize_personality, personality),
    }
