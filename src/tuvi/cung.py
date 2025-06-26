from functools import cached_property
import pydantic

from src.tuvi.element.base import Element
from src.tuvi.element.dia_chi import DiaChi
from src.tuvi.element.sao import ChinhTinh, PhuTinh
from src.tuvi.element.types import AM_DUONG, MAP_COLOR, NGU_HANH, ROLE_TYPE
from src.tuvi.element.trangsinh import TypeTrangSinh
from src.tuvi.element.tuhoa import TypeTuHoa

class Cung(pydantic.BaseModel):

    element : NGU_HANH | None = None

    sign : AM_DUONG

    role : ROLE_TYPE | None = None

    chinhTinh : list[ChinhTinh] = []

    phuTinh : list[PhuTinh] = []

    trang_sinh : TypeTrangSinh | None = None

    tuhoa : list[TypeTuHoa] = []

    is_tuan : bool = False

    is_triet : bool = False

    is_cung_than : bool = False

    dia_chi : str = ""

    thien_can : str = ""

    @cached_property
    def all_element(self) -> list[Element]:
        return [*self.chinhTinh, *self.phuTinh, self.trang_sinh, *self.tuhoa]

    def __repr__(self) -> str:
        role_str = self.role if not self.is_cung_than else f"{self.role} - Than"

        markdown_content = f"<h3 style='text-align: center;'><b>{role_str}</b></h3>\n\n"

        for chinhTinh in self.chinhTinh:
            markdown_content += f"<p style='color: {MAP_COLOR[chinhTinh.elemental]};font-size: 20px;'>{chinhTinh.name}</p>\n"

        if self.is_tuan:
            markdown_content += f"<p style='font-size: 15px;'>**Tuần**</p>\n"
        if self.is_triet:
            markdown_content += f"<p style='font-size: 15px;'>**Triệt**</p>\n"

        grouped_by_elemental = {}
        for item in self.phuTinh:
            if item.elemental not in grouped_by_elemental:
                grouped_by_elemental[item.elemental] = []
            grouped_by_elemental[item.elemental].append(item)

        markdown_content += "<table style='width: 100%; border-collapse: collapse;'>\n"
        markdown_content += "  <tr>\n"

        for elemental in grouped_by_elemental.keys():
            markdown_content += f"    <th style='text-align: center; color: {MAP_COLOR[elemental]}; width: 40%;'>{elemental}</th>\n"
        markdown_content += "  </tr>\n"
        markdown_content += "  <tr>\n"

        for elemental, items in grouped_by_elemental.items():
            markdown_content += "    <td style='vertical-align: top; padding: 5px;'>\n"
            for item in items:
                font_size = "15px"
                markdown_content += f"      <p style='color: {MAP_COLOR[item.elemental]}; font-size: {font_size}; white-space: nowrap;'>{item.name}</p>\n"
            markdown_content += "    </td>\n"

        markdown_content += "  </tr>\n"
        markdown_content += "</table>\n"

        if self.tuhoa:
            for tuhoa in self.tuhoa:
                markdown_content += f"<p style='font-size: 15px;'>--{tuhoa.name}--</p>\n"

        markdown_content += f"<p style='font-size: 15px;'>--{self.trang_sinh.name}--</p>\n"

        return markdown_content
