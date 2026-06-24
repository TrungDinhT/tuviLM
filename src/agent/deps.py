from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, ModelRetry

from src.agent.book_index import BookIndex
from src.refactored.la_so import LaSo


DEFAULT_BOOK_ROOT = (
    Path(__file__).resolve().parents[2] / "data" / "tuvitanbien_chunking"
)


@dataclass(slots=True)
class TuviAgentDeps:
    agent: Agent | None = None
    la_so: LaSo | None = None
    book: BookIndex | None = None
    book_root: Path = DEFAULT_BOOK_ROOT

    def require_agent(self) -> Agent:
        if self.agent is None:
            raise ModelRetry("Agent chưa được gán vào deps.")
        return self.agent

    def require_la_so(self) -> LaSo:
        if self.la_so is None:
            raise ModelRetry("LaSo chưa được gán vào deps.")
        return self.la_so

    def require_book(self) -> BookIndex:
        if self.book is None:
            try:
                self.book = BookIndex(self.book_root)
            except FileNotFoundError as exc:
                raise ModelRetry(str(exc)) from exc
        return self.book
