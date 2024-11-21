import pydantic

from src.tuvi.sao import ChinhTinh, PhuTinh
from src.tuvi.types import AM_DUONG, MAP_COLOR, NGU_HANH, ROLE_TYPE

class Cung(pydantic.BaseModel):

    element : NGU_HANH | None = None

    sign : AM_DUONG

    role : ROLE_TYPE | None = None

    chinhTinh : list[ChinhTinh] = []

    phuTinh : list[PhuTinh] = []

    is_cung_than : bool = False

    def __repr__(self) -> str:
        role_str = self.role if not self.is_cung_than else f"{self.role} - Than"

        markdown_content = f"<h3 style='text-align: center;'><b>{role_str}</b></h3>\n\n"

        for chinhTinh in self.chinhTinh:
            markdown_content += f"<p style='color: {MAP_COLOR[chinhTinh.elemental]};font-size: 20px;'>{chinhTinh.name}</p>\n"

        for phuTinh in self.phuTinh:
            markdown_content += f"<p style='color: {MAP_COLOR[phuTinh.elemental]};font-size: 15px;'>{phuTinh.name}</p>\n"

        return markdown_content
