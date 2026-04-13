from enum import StrEnum

from pydantic import Field

from src.refactored.component.elementary import ComponentBase


class Status(StrEnum):
    HAM = "Hãm"
    BINH = "Bình"
    DAC = "Đắc"
    VUONG = "Vượng"
    MIEU = "Miếu"


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


class TuHoa(ComponentBase):
    pass
