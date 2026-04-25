from enum import StrEnum
from typing import Optional

from pydantic import Field

from src.refactored.component.elementary import ComponentBase, NguHanh


class Status(StrEnum):
    HAM = "Hãm"
    BINH = "Bình"
    DAC = "Đắc"
    VUONG = "Vượng"
    MIEU = "Miếu"
    NONE = "Không xác định"

    @classmethod
    def _missing_(cls, value: Optional[str]) -> "Status | None":
        if value is None:
            return cls.NONE
        return None


class SaoType(StrEnum):
    CAT = "Cát"
    SAT = "Sát"
    PHUC = "Phúc"
    VAN = "Văn"
    QUY = "Quý"
    PHU = "Phú"


class Sao(ComponentBase):
    is_chinh_tinh: bool = False
    sao_type: list[SaoType] = Field(default_factory=list)
    ngu_hanh: NguHanh


class TuHoa(ComponentBase):
    ngu_hanh: NguHanh


class VongTrangSinh(ComponentBase):
    """Catalog entry for Tràng Sinh stars (no ngũ hành)."""


class TuanTriet(ComponentBase):
    """Catalog entry for Tuần / Triệt split markers (no ngũ hành)."""
