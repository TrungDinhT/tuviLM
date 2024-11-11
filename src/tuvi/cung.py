import pydantic

from src.tuvi.sao import ChinhTinh, PhuTinh
from src.tuvi.types import AM_DUONG, MAP_COLOR, NGU_HANH, ROLE_TYPE

class Cung(pydantic.BaseModel):

    element : NGU_HANH | None = None

    sign : AM_DUONG

    role : ROLE_TYPE | None = None

    chinhTinh : list[ChinhTinh] = []

    phuTinh : list[PhuTinh] = []

    def __repr__(self) -> str:
        markdown_content = f"<h5 style='text-align: center;'><b>{self.role}</b></h5>\n\n"

        for chinhTinh in self.chinhTinh:
            markdown_content += f"<p style='color: {MAP_COLOR[chinhTinh.elemental]};font-size: 20px;'>{chinhTinh.name}</p>\n"

        return markdown_content
