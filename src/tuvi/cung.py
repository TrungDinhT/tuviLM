import pydantic

from src.tuvi.element.base import Element
from src.tuvi.element.sao import ChinhTinh, PhuTinh
from src.tuvi.element.types import AM_DUONG, NGU_HANH, ROLE_TYPE, TYPE_DIA_CHI
from src.tuvi.element.trangsinh import TypeTrangSinh
from src.tuvi.element.tuhoa import TypeTuHoa

class Cung(pydantic.BaseModel):

    element : NGU_HANH | None = None
    "Ngũ hành của cung"

    sign : AM_DUONG
    "Âm hoặc Dương"

    role : ROLE_TYPE | None = None
    "Vai trò của cung, ví dụ: Mệnh, Phụ Mẫu, Phúc Đức,..."

    chinhTinh : list[ChinhTinh] = pydantic.Field(default_factory=list)
    "Danh sách chính tinh trong cung"

    phuTinh : list[PhuTinh] = pydantic.Field(default_factory=list)
    "Danh sách phụ tinh trong cung"

    trang_sinh : TypeTrangSinh | None = None
    "Trạng thái Tràng Sinh của cung"

    tuhoa : list[TypeTuHoa] = pydantic.Field(default_factory=list)
    "Danh sách Tứ Hỏa trong cung"

    is_tuan : bool = False
    "Cung có bị Tuần"

    is_triet : bool = False
    "Cung có bị Triệt"

    is_cung_than : bool = False
    "Cung có phải là Cung Thân"

    dia_chi : TYPE_DIA_CHI | None = None
    "Địa chi của cung"

    thien_can : str = ""
    "Thiên can của cung"

    age_daivan : int | None = None
    "Tuổi đại vận của cung"

    saoLuu : list[PhuTinh] = pydantic.Field(default_factory=list)
    "Danh sách sao lưu của cung, ví dụ: Lưu Văn Xương, Lưu Văn Khúc,..."

    @property
    def all_element(self) -> list[Element]:
        elements: list[Element] = [*self.chinhTinh, *self.phuTinh, *self.tuhoa]
        if self.trang_sinh is not None:
            elements.append(self.trang_sinh)
        return elements

    def __repr__(self) -> str:
        role_str = self.role if self.role else "Unknown"
        if self.is_cung_than:
            role_str = f"{role_str} - Than"
        return f"Cung(role={role_str}, dia_chi={self.dia_chi}, age_daivan={self.age_daivan})"

    # TODO: need a convertor to transform to representation that agent can understand
    def to_detail(self) -> str:
        info = f"Cung: {self.role} ({self.dia_chi})\n"

        info += "\nChinh Tinh : " + "\n - ".join([star.name for star in self.chinhTinh]) if self.chinhTinh else "Vô Chính Diệu"
        info += "\nPhụ Tinh : " + "\n - ".join([star.name for star in self.phuTinh]) if self.phuTinh else ""
        info += "\nTứ Hỏa : " + "\n - ".join([tuhoa.name for tuhoa in self.tuhoa]) if self.tuhoa else ""
        info += f"\nTràng Sinh : {self.trang_sinh.name}"
        info += "\n Có Tuần" if self.is_tuan else ""
        info += "\n Có Triệt" if self.is_triet else ""
        info += "\n Đây là Cung Thân" if self.is_cung_than else ""
        info += f"\nTuổi Đại Vận: {self.age_daivan}" if self.age_daivan else ""
        info += "\nSao Lưu: " + "\n - ".join([star.name for star in self.saoLuu]) if self.saoLuu else ""

        return info
