from enum import Enum


class LuongNghi(Enum):
    Duong = 0
    Am = 1

    def __str__(self) -> str:
        return "Dương" if self.value == 0 else "Âm"
