"""Keep generation alive independently of the HTTP response consuming it."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI

logger = logging.getLogger(__name__)


class BackgroundStream:
    def __init__(self, app: FastAPI, source: AsyncIterator[str]) -> None:
        self.queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=256)
        self.connected = True
        tasks = getattr(app.state, "chat_tasks", None)
        if tasks is None:
            tasks = app.state.chat_tasks = set()
        task = asyncio.create_task(self._produce(source))
        tasks.add(task)  # A strong reference keeps disconnected runs alive.
        task.add_done_callback(tasks.discard)

    def _publish(self, event: str | None) -> None:
        if not self.connected:
            return
        if self.queue.full():
            # A suspended consumer must not block generation or grow memory.
            # End its stream; it can recover the persisted result with the same key.
            self._detach()
            self.queue.put_nowait(None)
            return
        self.queue.put_nowait(event)

    def _detach(self) -> None:
        self.connected = False
        while not self.queue.empty():
            self.queue.get_nowait()

    async def _produce(self, source: AsyncIterator[str]) -> None:
        try:
            async for event in source:
                self._publish(event)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Background chat stream failed")
        finally:
            self._publish(None)

    async def events(self) -> AsyncIterator[str]:
        try:
            while True:
                try:
                    event = await asyncio.wait_for(self.queue.get(), timeout=15)
                except TimeoutError:
                    yield ": keep-alive\n\n"
                    continue
                if event is None:
                    return
                yield event
        finally:
            self._detach()


async def stop_chat_tasks(app: FastAPI) -> None:
    """Finalize cancelled runs before closing the history store on shutdown."""
    tasks = list(getattr(app.state, "chat_tasks", ()))
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
