from enum import Enum, IntEnum, StrEnum
from typing import Self


class IndexedEnumMixin:
    @property
    def index(self) -> int:
        return tuple(type(self)).index(self)


class CyclicEnumMixin(IndexedEnumMixin):
    @classmethod
    def from_index(cls, index: int):
        members = tuple(cls)
        return members[index % len(members)]

    def __add__(self, val: int) -> "Self":
        if not isinstance(val, int):
            return NotImplemented
        return type(self).from_index(self.index + val)

    def __sub__(self, val: "Self | int") -> "Self | int":
        if isinstance(val, type(self)):
            return (self.index - val.index) % len(type(self))
        if isinstance(val, int):
            return self + (-1) * val
        return NotImplemented


class ThienCan(CyclicEnumMixin, StrEnum):
    GIAP = "giap"
    AT = "at"
    BINH = "binh"
    DINH = "dinh"
    MAU = "mau"
    KY = "ky"
    CANH = "canh"
    TAN = "tan"
    NHAM = "nham"
    QUY = "quy"


class DiaChi(CyclicEnumMixin, StrEnum):
    TY = "ty"
    SUU = "suu"
    DAN = "dan"
    MEO = "meo"
    THIN = "thin"
    TI = "ti"
    NGO = "ngo"
    MUI = "mui"
    THAN = "than"
    DAU = "dau"
    TUAT = "tuat"
    HOI = "hoi"

    @classmethod
    def list_dia_chi(cls) -> list["DiaChi"]:
        return list(cls)


class CircleDirection(IntEnum):
    CW = 1
    CCW = -1

    @property
    def multiplier(self) -> int:
        return int(self)

    def __str__(self) -> str:
        return "CLOCKWISE" if self is type(self).CW else "COUNTER-CLOCKWISE"

    def __mul__(self, other: int) -> int:
        if not isinstance(other, int):
            return NotImplemented
        return self.multiplier * other

    def __rmul__(self, other: int) -> int:
        return self * other

    def __neg__(self) -> "CircleDirection":
        return type(self).CCW if self is type(self).CW else type(self).CW


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

    def dong_hanh(self, other: "NguHanh") -> bool:
        return self.index == other.index

    def tuong_sinh(self, other: "NguHanh") -> bool:
        return self.sinh_xuat(other) or self.sinh_nhap(other)

    def tuong_khac(self, other: "NguHanh") -> bool:
        return self.khac_xuat(other) or self.khac_nhap(other)
