from enum import StrEnum
from pydantic import BaseModel


class Role(StrEnum):
    MENH = "Mệnh"
    PHU = "Phụ Mẫu"
    PHUC = "Phúc Đức"
    DIEN = "Điền Trạch"
    QUAN = "Quan Lộc"
    NO = "Nô Bộc"
    DI = "Thiên Di"
    TAT = "Tật Ách"
    TAI = "Tài Bạch"
    TU = "Tử Tức"
    PHOI = "Phu Thê"
    HUYNH = "Huynh Đệ"
    THAN = "Thân"


class Cung(BaseModel):
    model_config = {"frozen": True}

    id: str
    role: Role

    @property
    def name(self):
        return self.role.value

    def __hash__(self) -> int:
        return hash(self.id)
