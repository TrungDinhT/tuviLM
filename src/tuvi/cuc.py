import pydantic

from src.tuvi.types import NGU_HANH

class Cuc(pydantic.BaseModel):

    name : str
    number : int
    elemental : NGU_HANH

LIST_CUC = [
    Cuc(name="Thủy Nhị cục", number=2, elemental="Thuy"),
    Cuc(name="Mộc Tam cục", number=3, elemental="Moc"),
    Cuc(name="Kim Tứ cục", number=4, elemental="Kim"),
    Cuc(name="Thổ Ngũ cục", number=5, elemental="Tho"),
    Cuc(name="Hỏa Lục cục", number=6, elemental="Hoa"),
]
