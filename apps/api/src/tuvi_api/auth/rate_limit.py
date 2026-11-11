"""A small in-memory rate limit for login and the routes that send email.

Keys are per email address, not per client IP: the API sits behind the web
app's proxy, so the client IP is not reliable here. The counts live in this
process only, so each API replica limits on its own.
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException


class RateLimiter:
    def __init__(self, *, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}

    def check(self, key: str, *, limit: int, window_seconds: float) -> None:
        """Count one attempt for `key`. Raise 429 when the limit is already reached."""
        now = self._clock()
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] <= now - window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            raise HTTPException(429, "Too many attempts. Wait a moment and try again.")
        hits.append(now)
        if len(self._hits) > 10_000:
            self._forget_idle(now, window_seconds)

    def _forget_idle(self, now: float, window_seconds: float) -> None:
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= now - window_seconds]:
            del self._hits[key]
