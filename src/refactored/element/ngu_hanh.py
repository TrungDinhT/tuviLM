from enum import Enum, auto


class NguHanh(Enum):
    Tho = 0
    Kim = auto()
    Thuy = auto()
    Moc = auto()
    Hoa = auto()

    def __str__(self) -> str:
        _NGU_HANH_NAMES = [
            "Tho", "Kim", "Thủy", "Mộc", "Hỏa"
        ]
        return _NGU_HANH_NAMES[self.value]

    @classmethod
    def list_ngu_hanh(cls) -> list['NguHanh']:
        return list(cls)


    def tuong_sinh(self, other: 'NguHanh') -> bool:
        return (self.value - other.value) % 5 == 1

    def tuong_khac(self, other: 'NguHanh') -> bool:
        return (self.value - other.value) % 5 == 3

