from __future__ import annotations

from typing import Self

from src.refactored.component.cung import Cung, Role
from src.refactored.component.elementary import DiaChi, ThienCan
from src.refactored.placement.registry import ComponentId


class CungBuilder:
    """Build a :class:`Cung` in stages: set fields, add sao, then :meth:`build`."""

    def __init__(self, dia_chi: DiaChi, thien_can: ThienCan) -> None:
        self._dia_chi = dia_chi
        self._thien_can = thien_can
        self._role: Role | None = None
        self._is_cung_than: bool = False
        self._saos: list[ComponentId] = []

    def set_role(self, role: Role) -> Self:
        self._role = role
        return self

    def set_is_cung_than(self, is_cung_than: bool) -> Self:
        self._is_cung_than = is_cung_than
        return self

    def add_sao(self, *sao: ComponentId) -> Self:
        self._saos.extend(sao)
        return self

    def build(self) -> Cung:
        if self._role is None:
            raise ValueError("role is not set")
        if not self._saos:
            raise ValueError("saos are not set")
        return Cung(
            dia_chi=self._dia_chi,
            thien_can=self._thien_can,
            role=self._role,
            saos=tuple(self._saos),
            is_cung_than=self._is_cung_than,
        )
