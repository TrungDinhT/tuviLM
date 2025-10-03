from enum import Enum, StrEnum, auto
from pydantic import BaseModel
from typing import Optional


class DiaChi(Enum):
    TY = 0
    SUU = auto()
    DAN = auto()
    MEO = auto()
    THIN = auto()
    TI = auto()
    NGO = auto()
    MUI = auto()
    THAN = auto()
    DAU = auto()
    TUAT = auto()
    HOI = auto()

    def __str__(self) -> str:
        _DIA_CHI_NAMES = [
            "Tý",
            "Sửu",
            "Dần",
            "Mão",
            "Thìn",
            "Tỵ",
            "Ngọ",
            "Mùi",
            "Thân",
            "Dậu",
            "Tuất",
            "Hợi",
        ]
        return _DIA_CHI_NAMES[self.value]

    def __add__(self, val: int) -> "DiaChi":
        return DiaChi((self.value + val % 12 + 12) % 12)

    def __sub__(self, val: int):
        return self + (-1) * val

    @classmethod
    def list_dia_chi(cls) -> list["DiaChi"]:
        return list(cls)


class LuongNghi(Enum):
    DUONG = 0
    AM = 1

    def __str__(self) -> str:
        return "Dương" if self.value == 0 else "Âm"


class NguHanh(Enum):
    THO = 0
    KIM = auto()
    THUY = auto()
    MOC = auto()
    HOA = auto()

    def __str__(self) -> str:
        _NGU_HANH_NAMES = [
            "Thổ", "Kim", "Thủy", "Mộc", "Hỏa"
        ]
        return _NGU_HANH_NAMES[self.value]

    @classmethod
    def list_ngu_hanh(cls) -> list['NguHanh']:
        return list(cls)

    def tuong_sinh(self, other: 'NguHanh') -> bool:
        return (self.value - other.value) % 5 == 1

    def tuong_khac(self, other: 'NguHanh') -> bool:
        return (self.value - other.value) % 5 == 3


class ThienCan(StrEnum):
    GIAP = "Giáp"
    AT = "Ất"
    BINH = "Bính"
    DINH = "Đinh"
    MAU = "Mậu"
    KY = "Kỷ"
    CANH = "Canh"
    TAN = "Tân"
    NHAM = "Nhâm"
    QUY = "Quý"


class ComponentBase(BaseModel):
    model_config = {"frozen": True}

    name: str
    ngu_hanh: Optional[NguHanh] = None

    def __hash__(self) -> int:
        return hash(self.name)
