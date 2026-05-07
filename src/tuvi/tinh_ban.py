from typing import Literal
import pydantic

from src.tuvi.cung import Cung
from src.tuvi.element.types import AM_DUONG, LIST_DIA_CHI, TYPE_DIA_CHI, TYPE_GENDER, TYPE_THIEN_CAN
from src.tuvi.element.cuc import Cuc

class TinhBan(pydantic.BaseModel):

    map_cung : dict[TYPE_DIA_CHI, Cung]

    cuc : Cuc | None = None

    direction : Literal[1, -1] | None = None

    gender : TYPE_GENDER | None = None

    am_duong : AM_DUONG | None = None

    cung_than : TYPE_DIA_CHI | None = None

    year_can : TYPE_THIEN_CAN | None = None
    "Thiên Can của năm sinh, dùng để tra cứu cách cục"

    year_chi : TYPE_DIA_CHI | None = None
    "Địa Chi của năm sinh"

    @classmethod
    def init_empty_plate(cls):

        return cls(
            map_cung={
                dia_chi : Cung(
                    sign="Am" if idx % 2 == 1 else "Duong",
                    dia_chi=dia_chi,
                ) for idx, dia_chi in enumerate(LIST_DIA_CHI)}
        )

    @property
    def menh_position(self):
        for dia_chi, cung in self.map_cung.items():
            if cung.role == "Mệnh":
                return dia_chi

        raise ValueError("Non role tinh ban")

    def get_role_position(self, role: str) -> TYPE_DIA_CHI:
        for dia_chi, cung in self.map_cung.items():
            if cung.role == role:
                return dia_chi
        raise ValueError(f"Role '{role}' is not assigned")

    def validate_complete(self) -> None:
        if self.cuc is None:
            raise ValueError("TinhBan missing 'cuc'")
        if self.direction not in (1, -1):
            raise ValueError("TinhBan missing 'direction'")
        if self.gender is None:
            raise ValueError("TinhBan missing 'gender'")
        if self.am_duong is None:
            raise ValueError("TinhBan missing 'am_duong'")
        if self.cung_than is None:
            raise ValueError("TinhBan missing 'cung_than'")
        if self.cung_than not in self.map_cung:
            raise ValueError(f"Invalid cung_than: {self.cung_than}")

        roles = [cung.role for cung in self.map_cung.values()]
        if any(role is None for role in roles):
            raise ValueError("At least one cung has no role")
        if len(set(roles)) != 12:
            raise ValueError("Roles are duplicated or incomplete")

        if not self.map_cung[self.cung_than].is_cung_than:
            raise ValueError("cung_than flag is not set at cung_than position")

        if sum(1 for cung in self.map_cung.values() if cung.is_tuan) != 2:
            raise ValueError("Expected exactly 2 Tuan positions")
        if sum(1 for cung in self.map_cung.values() if cung.is_triet) != 2:
            raise ValueError("Expected exactly 2 Triet positions")

        for dia_chi, cung in self.map_cung.items():
            if cung.dia_chi != dia_chi:
                raise ValueError(f"Mismatched dia_chi at {dia_chi}")
            if cung.trang_sinh is None:
                raise ValueError(f"Missing trang_sinh at {dia_chi}")
