from src.refactored.component.elementary import ComponentBase, NguHanh


class Cuc(ComponentBase):
    number: int


LIST_CUC = (
    Cuc(name="Thủy Nhị cục", number=2, ngu_hanh=NguHanh.THUY),
    Cuc(name="Mộc Tam cục", number=3, ngu_hanh=NguHanh.MOC),
    Cuc(name="Kim Tứ cục", number=4, ngu_hanh=NguHanh.KIM),
    Cuc(name="Thổ Ngũ cục", number=5, ngu_hanh=NguHanh.THO),
    Cuc(name="Hỏa Lục cục", number=6, ngu_hanh=NguHanh.HOA),
)
