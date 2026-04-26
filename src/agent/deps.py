from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, ModelRetry

from src.agent.book_index import BookIndex
from src.tuvi.tinh_ban import TinhBan


DEFAULT_BOOK_ROOT = Path(__file__).resolve().parents[2] / "data" / "tuvitanbien_chunking"


@dataclass(slots=True)
class TuviAgentDeps:
    agent: Agent | None = None
    tinh_ban: TinhBan | None = None
    book: BookIndex | None = None
    book_root: Path = DEFAULT_BOOK_ROOT

    def require_agent(self) -> Agent:
        if self.agent is None:
            raise ModelRetry("Agent chưa được gán vào deps.")
        return self.agent

    def require_tinh_ban(self) -> TinhBan:
        if self.tinh_ban is None:
            raise ModelRetry("TinhBan chưa được gán vào deps.")
        return self.tinh_ban

    def require_book(self) -> BookIndex:
        if self.book is None:
            try:
                self.book = BookIndex(self.book_root)
            except FileNotFoundError as exc:
                raise ModelRetry(str(exc)) from exc
        return self.book

    def get_cung_by_position(self, position: str) -> str:
        tinh_ban = self.require_tinh_ban()
        normalized_position = position.strip()
        if normalized_position not in tinh_ban.map_cung:
            valid_positions = ", ".join(tinh_ban.map_cung.keys())
            raise ModelRetry(
                f"Position '{position}' không hợp lệ. Các vị trí hợp lệ: {valid_positions}"
            )
        return tinh_ban.map_cung[normalized_position].to_detail()

    def get_cung_by_role(self, role: str) -> str:
        tinh_ban = self.require_tinh_ban()
        normalized_role = role.strip()
        position = tinh_ban.get_role_position(normalized_role)
        return tinh_ban.map_cung[position].to_detail()
