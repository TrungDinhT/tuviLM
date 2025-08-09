import pydantic

from src.tuvi.element.types import NGU_HANH

class Cuc(pydantic.BaseModel):

    name : str
    number : int
    elemental : NGU_HANH

LIST_CUC = [
    Cuc(name="Thủy Nhị cục", number=2, elemental="Thủy"),
    Cuc(name="Mộc Tam cục", number=3, elemental="Mộc"),
    Cuc(name="Kim Tứ cục", number=4, elemental="Kim"),
    Cuc(name="Thổ Ngũ cục", number=5, elemental="Thổ"),
    Cuc(name="Hỏa Lục cục", number=6, elemental="Hỏa"),
]
