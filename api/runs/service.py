from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, TypeAdapter

from api.chat.contracts import MissingOwnerIdError
from api.runs.models import RunRecord, RunSettings, now
from api.runs.store import RunFinished, RunStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Workflow:
    inputs: type[BaseModel]
    authorize: Callable[[str, BaseModel], Awaitable[str]]
    execute: Callable[..., Awaitable[Any]]
    finalize: Callable[..., Awaitable[None]] | None = None
    output: type[BaseModel] | TypeAdapter | None = None


class RunContext:
    def __init__(self, store: RunStore, run: RunRecord):
        self.store = store
        self.run = run
        self.status = "succeeded"
        self.result: Any = None
        self.error: str | None = None
        self.lock = asyncio.Lock()

    async def emit(self, event_type: str, data: dict[str, Any]) -> None:
        if len(json.dumps(data, ensure_ascii=False, allow_nan=False).encode()) > 32_000:
            raise ValueError("Progress update is too large")
        async with self.lock:
            state = self.run.state.model_copy(deep=True)
            if event_type == "text":
                state.text += data["delta"]
            elif event_type == "progress":
                state.progress = data.get("message")
            elif event_type == "metadata":
                state.metadata.update(data)
            else:
                raise ValueError("Unsupported progress update")
            if len(state.model_dump_json().encode()) > 1_000_000:
                raise ValueError("Workflow state is too large")
            self.run = await self.store.write(self.run, {"state": state.model_dump()})

    async def text(self, delta: str) -> None:
        for start in range(0, len(delta), 4_000):
            await self.emit("text", {"delta": delta[start:start + 4_000]})

    async def progress(self, message: str | None) -> None:
        await self.emit("progress", {"message": message})


class RunService:
    """Tasks live in this API process, independently of HTTP connections."""

    def __init__(self, store: RunStore, workflows: dict[str, Workflow], settings: RunSettings):
        self.store, self.workflows, self.settings = store, workflows, settings
        self._slots = asyncio.Semaphore(settings.concurrency)
        self._submissions: set[asyncio.Task] = set()
        self._tasks: set[asyncio.Task] = set()
        self._generations: set[asyncio.Task] = set()
        self._closing = False

    async def submit(self, *, workflow: str, inputs: dict, owner_id: str, idempotency_key: str) -> RunRecord:
        if self._closing:
            raise RuntimeError("Run service is shutting down")
        if not owner_id.strip():
            raise MissingOwnerIdError
        if not idempotency_key.strip():
            raise ValueError("Idempotency key is required")
        definition = self.workflows.get(workflow)
        if definition is None:
            raise ValueError("Unknown workflow")
        validated = definition.inputs.model_validate(inputs)
        resource_id = await definition.authorize(owner_id, validated)
        encoded = json.dumps([workflow, validated.model_dump(mode="json")], sort_keys=True, ensure_ascii=False).encode()
        if len(encoded) > 128_000:
            raise ValueError("Workflow input is too large")
        stamp = now()
        run = RunRecord(
            id=str(uuid4()), workflow=workflow, resource_id=resource_id,
            inputs=validated.model_dump(mode="json"), owner_id=owner_id,
            idempotency_key=idempotency_key, fingerprint=hashlib.sha256(encoded).hexdigest(),
            created_at=stamp, updated_at=stamp,
            expires_at=stamp + timedelta(seconds=self.settings.timeout_seconds + 15),
        )

        async def schedule():
            saved = await self.store.insert(run)
            if saved.id == run.id:
                task = asyncio.create_task(self._execute(saved))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
            return saved

        # Insertion and scheduling finish even if the submitting request is
        # cancelled after MongoDB accepted the write but before sending the reply.
        task = asyncio.create_task(schedule())
        self._submissions.add(task)
        task.add_done_callback(self._submission_done)
        return await asyncio.shield(task)

    def _submission_done(self, task: asyncio.Task) -> None:
        self._submissions.discard(task)
        if not task.cancelled():
            task.exception()  # Retrieve failures even when the HTTP caller left.

    async def _generate(self, context: RunContext, definition: Workflow):
        if self._closing:
            raise asyncio.CancelledError
        async with asyncio.timeout(self.settings.timeout_seconds):
            async with self._slots:
                inputs = definition.inputs.model_validate(context.run.inputs)
                await definition.authorize(context.run.owner_id, inputs)
                context.run = await self.store.write(context.run, {"status": "running"})
                if context.run.cancel_requested:
                    raise asyncio.CancelledError
                result = await definition.execute(context, inputs)
                if definition.output is not None:
                    adapter = definition.output if isinstance(definition.output, TypeAdapter) else TypeAdapter(definition.output)
                    result = adapter.dump_python(adapter.validate_python(result), mode="json")
                elif isinstance(result, BaseModel):
                    result = result.model_dump(mode="json")
                if len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode()) > 1_000_000:
                    raise ValueError("Workflow result is too large")
                return result

    async def _watch_cancel(self, context: RunContext, generation: asyncio.Task):
        # The Stop request can reach another API process sharing the same store.
        while not generation.done():
            await asyncio.sleep(self.settings.poll_seconds)
            try:
                run = await self.store.get(context.run.id, context.run.owner_id)
                if run.cancel_requested or not run.active:
                    generation.cancel()
                    return
            except Exception:
                logger.warning("Could not check cancellation for run %s", context.run.id, exc_info=True)

    async def _execute(self, run: RunRecord) -> None:
        context = RunContext(self.store, run)
        definition = self.workflows[run.workflow]
        generation = asyncio.create_task(self._generate(context, definition))
        self._generations.add(generation)
        generation.add_done_callback(self._generations.discard)
        observer = asyncio.create_task(self._watch_cancel(context, generation))
        try:
            try:
                context.result = await generation
            except asyncio.CancelledError:
                context.status = "cancelled"
            except Exception:
                logger.exception("Workflow failed: run_id=%s workflow=%s", run.id, run.workflow)
                context.status, context.error = "failed", "Workflow could not complete"
            # Publication is done once, in this process. There is no restart or
            # model retry. Keep the saved result immutable once terminal.
            async with asyncio.timeout(10):
                context.run = await self.store.write(context.run, {"publishing": True})
                if context.run.cancel_requested:
                    context.status, context.result, context.error = "cancelled", None, None
                if definition.finalize is not None:
                    await definition.finalize(context, definition.inputs.model_validate(run.inputs))
                await self.store.write(context.run, {
                    "status": context.status, "result": context.result, "error": context.error, "active": False,
                })
        except RunFinished:
            pass
        except Exception:
            logger.exception("Could not save workflow result: %s", run.id)
            try:
                await asyncio.wait_for(self.store.write(context.run, {
                    "status": "failed", "active": False, "result": None,
                    "error": "Workflow result could not be saved",
                }), timeout=2)
            except Exception:
                logger.exception("Could not mark failed workflow: %s", run.id)
        finally:
            observer.cancel()
            generation.cancel()
            await asyncio.gather(observer, generation, return_exceptions=True)

    async def close(self) -> None:
        self._closing = True
        await asyncio.gather(*list(self._submissions), return_exceptions=True)
        tasks = list(self._tasks)
        for task in list(self._generations):
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
