from __future__ import annotations

from dataclasses import dataclass

from src.tuvi.cung import Cung
from src.tuvi.tinh_ban import TinhBan
from pydantic_ai import Agent


@dataclass(slots=True)
class TuviAgentDeps:
    agent: Agent | None = None
    tinh_ban: TinhBan | None = None

    def require_agent(self) -> Agent:
        if self.agent is None:
            raise ValueError("Agent chưa được gán vào deps.")
        return self.agent

    def require_tinh_ban(self) -> TinhBan:
        if self.tinh_ban is None:
            raise ValueError("TinhBan chưa được gán vào deps.")
        return self.tinh_ban

    def get_cung_by_position(self, position: str) -> Cung:
        tinh_ban = self.require_tinh_ban()
        normalized_position = position.strip()
        if normalized_position not in tinh_ban.map_cung:
            valid_positions = ", ".join(tinh_ban.map_cung.keys())
            raise ValueError(
                f"Position '{position}' không hợp lệ. Các vị trí hợp lệ: {valid_positions}"
            )
        return tinh_ban.map_cung[normalized_position]

    def get_cung_by_role(self, role: str) -> Cung:
        tinh_ban = self.require_tinh_ban()
        normalized_role = role.strip()
        position = tinh_ban.get_role_position(normalized_role)
        return tinh_ban.map_cung[position]
