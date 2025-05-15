from enum import Enum, auto

class DiaChi(Enum):
    Ty = 0
    Suu = auto()
    Dan = auto()
    Meo = auto()
    Thin = auto()
    Ti = auto()
    Ngo = auto()
    Mui = auto()
    Than = auto()
    Dau = auto()
    Tuat = auto()
    Hoi = auto()

    def __str__(self) -> str:
        _DIA_CHI_NAMES = [
            "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
            "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
        ]
        return _DIA_CHI_NAMES[self.value]

    def __add__(self, val: int) -> 'DiaChi':
        return DiaChi((self.value + val % 12 + 12) % 12)

    def __sub__(self, val: int):
        return self + (-1) * val

    @classmethod
    def list_dia_chi(cls) -> list['DiaChi']:
        return list(cls)
