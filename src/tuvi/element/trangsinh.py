import pydantic

from src.tuvi.element.types import NGU_HANH, TYPE_DIA_CHI


class TypeTrangSinh(pydantic.BaseModel):

    name : str


VONG_TRANG_SINH = [
    TypeTrangSinh(name="Tràng Sinh"),
    TypeTrangSinh(name="Mộc Dục"),
    TypeTrangSinh(name="Quan Đới"),
    TypeTrangSinh(name="Lâm Quan"),
    TypeTrangSinh(name="Đế  Vương"),
    TypeTrangSinh(name="Suy"),
    TypeTrangSinh(name="Bệnh"),
    TypeTrangSinh(name="Tử"),
    TypeTrangSinh(name="Mộ"),
    TypeTrangSinh(name="Tuyệt"),
    TypeTrangSinh(name="Thai"),
    TypeTrangSinh(name="Dưỡng"),
]

MAP_TRANGSINH_POSITION : dict[NGU_HANH, TYPE_DIA_CHI] = {
    "Kim" : "Ti",
    "Moc" : "Hoi",
    "Hoa" : "Dan",
    "Tho" : "Than",
    "Thuy" : "Than",
}
