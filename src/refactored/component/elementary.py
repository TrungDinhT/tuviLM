from enum import Enum, StrEnum
from pydantic import BaseModel
from typing import Optional


class IndexedEnumMixin:
    @property
    def index(self) -> int:
        return tuple(type(self)).index(self)


class CyclicEnumMixin(IndexedEnumMixin):
    @classmethod
    def from_index(cls, index: int):
        members = tuple(cls)
        return members[index % len(members)]

    def __add__(self, val: int):
        if not isinstance(val, int):
            return NotImplemented
        return type(self).from_index(self.index + val)

    def __sub__(self, val: int):
        if not isinstance(val, int):
            return NotImplemented
        return self + (-1) * val


class ThienCan(CyclicEnumMixin, StrEnum):
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


class DiaChi(CyclicEnumMixin, StrEnum):
    TY = "Tý"
    SUU = "Sửu"
    DAN = "Dần"
    MEO = "Mão"
    THIN = "Thìn"
    TI = "Tỵ"
    NGO = "Ngọ"
    MUI = "Mùi"
    THAN = "Thân"
    DAU = "Dậu"
    TUAT = "Tuất"
    HOI = "Hợi"

    @classmethod
    def list_dia_chi(cls) -> list["DiaChi"]:
        return list(cls)


class LuongNghi(Enum):
    DUONG = 0
    AM = 1

    def __str__(self) -> str:
        return "Dương" if self.value == 0 else "Âm"


class NguHanh(IndexedEnumMixin, StrEnum):
    THO = "Thổ"
    KIM = "Kim"
    THUY = "Thủy"
    MOC = "Mộc"
    HOA = "Hỏa"

    @classmethod
    def list_ngu_hanh(cls) -> list["NguHanh"]:
        return list(cls)

    def sinh_xuat(self, other: "NguHanh") -> bool:
        return (other.index - self.index) % 5 == 1

    def sinh_nhap(self, other: "NguHanh") -> bool:
        return other.sinh_xuat(self)

    def khac_xuat(self, other: "NguHanh") -> bool:
        return (self.index - other.index) % 5 == 3

    def khac_nhap(self, other: "NguHanh") -> bool:
        return other.khac_xuat(self)

    def tuong_sinh(self, other: "NguHanh") -> bool:
        return self.sinh_xuat(other) or self.sinh_nhap(other)

    def tuong_khac(self, other: "NguHanh") -> bool:
        return self.khac_xuat(other) or self.khac_nhap(other)


class ComponentBase(BaseModel):
    model_config = {"frozen": True}

    name: str
    ngu_hanh: Optional[NguHanh] = None

    def __hash__(self) -> int:
        return hash(self.name)
