"""Chart access helpers for cach_cuc matching."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import ModelRetry

from src.agent.cach_cuc.models import CachCucData, Role
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID


STAR_ALIASES: dict[str, tuple[str, ...]] = {
    "tuan": ("tuan_1", "tuan_2"),
    "triet": ("triet_1", "triet_2"),
}


@dataclass(frozen=True)
class CachCucMatchContext:
    """Precomputed access layer around a ``LaSo`` for condition evaluation."""

    la_so: LaSo
    data: CachCucData
    star_aliases: dict[str, tuple[str, ...]]

    @classmethod
    def from_la_so(
        cls,
        la_so: LaSo,
        data: CachCucData,
        star_aliases: dict[str, tuple[str, ...]] | None = None,
    ) -> CachCucMatchContext:
        return cls(
            la_so=la_so,
            data=data,
            star_aliases=star_aliases or STAR_ALIASES,
        )

    def position_of_role(self, role: Role) -> DiaChi:
        """Return a role position or fail loudly for malformed chart state."""
        position = self.la_so.position_of(role.value, NATAL_LAYER_ID)
        if position is None:
            raise ModelRetry(f"Khong tim thay vi tri cung {role.value}.")
        return position

    def positions_of_star(self, star_id: str) -> tuple[DiaChi, ...]:
        """Return all natal positions for a star id, expanding logical aliases."""
        positions: list[DiaChi] = []
        for resolved_id in self.star_aliases.get(star_id, (star_id,)):
            position = self.la_so.position_of(resolved_id, NATAL_LAYER_ID)
            if position is not None and position not in positions:
                positions.append(position)
        return tuple(positions)

    def roles_at_position(self, position: DiaChi) -> tuple[Role, ...]:
        """Return natal and structural roles attached to one position."""
        cung = self.la_so.cung_at(position)
        roles = [cung.natal_role]
        if cung.is_cung_than and Role.CUNG_THAN not in roles:
            roles.append(Role.CUNG_THAN)
        return tuple(roles)
