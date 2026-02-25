from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.tuvi.element.sao import ChinhTinh, PhuTinh
from src.tuvi.element.types import NGU_HANH


StarType = Literal["chinh_tinh", "phu_tinh"]


@dataclass(frozen=True)
class StarDefinition:
    name: str
    elemental: NGU_HANH
    star_type: StarType
    description: str | None = None


STAR_REGISTRY: dict[str, StarDefinition] = {
    "Tử Vi": StarDefinition(name="Tử Vi", elemental="Thổ", star_type="chinh_tinh"),
    "Thiên Phủ": StarDefinition(name="Thiên Phủ", elemental="Thổ", star_type="chinh_tinh"),
    "Thái Dương": StarDefinition(name="Thái Dương", elemental="Hỏa", star_type="chinh_tinh"),
    "Vũ Khúc": StarDefinition(name="Vũ Khúc", elemental="Kim", star_type="chinh_tinh"),
    "Liêm Trinh": StarDefinition(name="Liêm Trinh", elemental="Hỏa", star_type="chinh_tinh"),
    "Thất Sát": StarDefinition(name="Thất Sát", elemental="Kim", star_type="chinh_tinh"),
    "Tham Lang": StarDefinition(name="Tham Lang", elemental="Thủy", star_type="chinh_tinh"),
    "Phá Quân": StarDefinition(name="Phá Quân", elemental="Thủy", star_type="chinh_tinh"),
    "Thiên Đồng": StarDefinition(name="Thiên Đồng", elemental="Thủy", star_type="chinh_tinh"),
    "Thiên Cơ": StarDefinition(name="Thiên Cơ", elemental="Mộc", star_type="chinh_tinh"),
    "Thái Âm": StarDefinition(name="Thái Âm", elemental="Thủy", star_type="chinh_tinh"),
    "Thiên Lương": StarDefinition(name="Thiên Lương", elemental="Mộc", star_type="chinh_tinh"),
    "Cự Môn": StarDefinition(name="Cự Môn", elemental="Thủy", star_type="chinh_tinh"),
    "Thiên Tướng": StarDefinition(name="Thiên Tướng", elemental="Thủy", star_type="chinh_tinh"),
    "Thiên Sứ": StarDefinition(name="Thiên Sứ", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Thuơng": StarDefinition(name="Thiên Thuơng", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Thọ": StarDefinition(name="Thiên Thọ", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Tài": StarDefinition(name="Thiên Tài", elemental="Thổ", star_type="phu_tinh"),
    "Tả Phù": StarDefinition(name="Tả Phù", elemental="Thổ", star_type="phu_tinh"),
    "Hữu Bật": StarDefinition(name="Hữu Bật", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Giải": StarDefinition(name="Thiên Giải", elemental="Hỏa", star_type="phu_tinh"),
    "Địa Giải": StarDefinition(name="Địa Giải", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Hình": StarDefinition(name="Thiên Hình", elemental="Hỏa", star_type="phu_tinh"),
    "Tam Thai": StarDefinition(name="Tam Thai", elemental="Thủy", star_type="phu_tinh"),
    "Bát Toạ": StarDefinition(name="Bát Toạ", elemental="Mộc", star_type="phu_tinh"),
    "Thiên Diêu": StarDefinition(name="Thiên Diêu", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Y": StarDefinition(name="Thiên Y", elemental="Thủy", star_type="phu_tinh"),
    "Địa Không": StarDefinition(name="Địa Không", elemental="Hỏa", star_type="phu_tinh"),
    "Địa Kiếp": StarDefinition(name="Địa Kiếp", elemental="Hỏa", star_type="phu_tinh"),
    "Văn Xương": StarDefinition(name="Văn Xương", elemental="Kim", star_type="phu_tinh"),
    "Văn Khúc": StarDefinition(name="Văn Khúc", elemental="Thủy", star_type="phu_tinh"),
    "Ân Quang": StarDefinition(name="Ân Quang", elemental="Mộc", star_type="phu_tinh"),
    "Thiên Quý": StarDefinition(name="Thiên Quý", elemental="Thổ", star_type="phu_tinh"),
    "Thai Phụ": StarDefinition(name="Thai Phụ", elemental="Kim", star_type="phu_tinh"),
    "Phong Cáo": StarDefinition(name="Phong Cáo", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Khôi": StarDefinition(name="Thiên Khôi", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Việt": StarDefinition(name="Thiên Việt", elemental="Hỏa", star_type="phu_tinh"),
    "Lực Sĩ": StarDefinition(name="Lực Sĩ", elemental="Thủy", star_type="phu_tinh"),
    "Hỏa Tinh": StarDefinition(name="Hỏa Tinh", elemental="Hỏa", star_type="phu_tinh"),
    "Linh Tinh": StarDefinition(name="Linh Tinh", elemental="Hỏa", star_type="phu_tinh"),
    "Lưu Hà": StarDefinition(name="Lưu Hà", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Trù": StarDefinition(name="Thiên Trù", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Quan": StarDefinition(name="Thiên Quan", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Phúc": StarDefinition(name="Thiên Phúc", elemental="Thổ", star_type="phu_tinh"),
    "Cô Thần": StarDefinition(name="Cô Thần", elemental="Thổ", star_type="phu_tinh"),
    "Quả Tú": StarDefinition(name="Quả Tú", elemental="Thổ", star_type="phu_tinh"),
    "Đẩu Quân": StarDefinition(name="Đẩu Quân", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Hỉ": StarDefinition(name="Thiên Hỉ", elemental="Hỏa", star_type="phu_tinh"),
    "Hồng Loan": StarDefinition(name="Hồng Loan", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Mã": StarDefinition(name="Thiên Mã", elemental="Hỏa", star_type="phu_tinh"),
    "Giải Thần": StarDefinition(name="Giải Thần", elemental="Mộc", star_type="phu_tinh"),
    "Phượng Các": StarDefinition(name="Phượng Các", elemental="Thổ", star_type="phu_tinh"),
    "Phá Toái": StarDefinition(name="Phá Toái", elemental="Hỏa", star_type="phu_tinh"),
    "Hỏa Cái": StarDefinition(name="Hỏa Cái", elemental="Kim", star_type="phu_tinh"),
    "Đào Hỏa": StarDefinition(name="Đào Hỏa", elemental="Mộc", star_type="phu_tinh"),
    "Thiên Khốc": StarDefinition(name="Thiên Khốc", elemental="Thủy", star_type="phu_tinh"),
    "Kiếp Sát": StarDefinition(name="Kiếp Sát", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên La": StarDefinition(name="Thiên La", elemental="Kim", star_type="phu_tinh"),
    "Địa Võng": StarDefinition(name="Địa Võng", elemental="Kim", star_type="phu_tinh"),
    "Lộc Tồn": StarDefinition(name="Lộc Tồn", elemental="Thổ", star_type="phu_tinh"),
    "Bác Sĩ": StarDefinition(name="Bác Sĩ", elemental="Thủy", star_type="phu_tinh"),
    "Kình Dương": StarDefinition(name="Kình Dương", elemental="Kim", star_type="phu_tinh"),
    "Thanh Long": StarDefinition(name="Thanh Long", elemental="Thủy", star_type="phu_tinh"),
    "Tiểu Hao": StarDefinition(name="Tiểu Hao", elemental="Hỏa", star_type="phu_tinh"),
    "LN Văn Tinh": StarDefinition(name="LN Văn Tinh", elemental="Hỏa", star_type="phu_tinh"),
    "Tướng Quân": StarDefinition(name="Tướng Quân", elemental="Mộc", star_type="phu_tinh"),
    "Tấu Thư": StarDefinition(name="Tấu Thư", elemental="Kim", star_type="phu_tinh"),
    "Đường Phù": StarDefinition(name="Đường Phù", elemental="Mộc", star_type="phu_tinh"),
    "Phi Liêm": StarDefinition(name="Phi Liêm", elemental="Hỏa", star_type="phu_tinh"),
    "Hỷ Thần": StarDefinition(name="Hỷ Thần", elemental="Hỏa", star_type="phu_tinh"),
    "Bệnh Phù": StarDefinition(name="Bệnh Phù", elemental="Thổ", star_type="phu_tinh"),
    "Quốc Ấn": StarDefinition(name="Quốc Ấn", elemental="Thổ", star_type="phu_tinh"),
    "Đại Hao": StarDefinition(name="Đại Hao", elemental="Hỏa", star_type="phu_tinh"),
    "Phục Binh": StarDefinition(name="Phục Binh", elemental="Hỏa", star_type="phu_tinh"),
    "Đà La": StarDefinition(name="Đà La", elemental="Kim", star_type="phu_tinh"),
    "Quan Phủ": StarDefinition(name="Quan Phủ", elemental="Hỏa", star_type="phu_tinh"),
    "Thái Tuế": StarDefinition(name="Thái Tuế", elemental="Hỏa", star_type="phu_tinh"),
    "Thiếu Dương": StarDefinition(name="Thiếu Dương", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Không": StarDefinition(name="Thiên Không", elemental="Hỏa", star_type="phu_tinh"),
    "Tang Môn": StarDefinition(name="Tang Môn", elemental="Mộc", star_type="phu_tinh"),
    "Thiếu Âm": StarDefinition(name="Thiếu Âm", elemental="Thủy", star_type="phu_tinh"),
    "Quan Phù": StarDefinition(name="Quan Phù", elemental="Hỏa", star_type="phu_tinh"),
    "Long Trì": StarDefinition(name="Long Trì", elemental="Thủy", star_type="phu_tinh"),
    "Tử Phù": StarDefinition(name="Tử Phù", elemental="Kim", star_type="phu_tinh"),
    "Nguyệt Đức": StarDefinition(name="Nguyệt Đức", elemental="Hỏa", star_type="phu_tinh"),
    "Tuế Phá": StarDefinition(name="Tuế Phá", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Hư": StarDefinition(name="Thiên Hư", elemental="Thủy", star_type="phu_tinh"),
    "Long Đức": StarDefinition(name="Long Đức", elemental="Thủy", star_type="phu_tinh"),
    "Bạch Hổ": StarDefinition(name="Bạch Hổ", elemental="Kim", star_type="phu_tinh"),
    "Phúc Đức": StarDefinition(name="Phúc Đức", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Đức": StarDefinition(name="Thiên Đức", elemental="Hỏa", star_type="phu_tinh"),
    "Điếu Khách": StarDefinition(name="Điếu Khách", elemental="Hỏa", star_type="phu_tinh"),
    "Trực Phù": StarDefinition(name="Trực Phù", elemental="Kim", star_type="phu_tinh"),
}


def _get_star_definition(star_name: str) -> StarDefinition:
    if star_name not in STAR_REGISTRY:
        raise KeyError(f"Star '{star_name}' is not registered")
    return STAR_REGISTRY[star_name]


def make_chinh_tinh(star_name: str) -> ChinhTinh:
    star_definition = _get_star_definition(star_name)
    if star_definition.star_type != "chinh_tinh":
        raise ValueError(f"Star '{star_name}' is not a ChinhTinh")
    return ChinhTinh(name=star_definition.name, elemental=star_definition.elemental)


def make_phu_tinh(star_name: str) -> PhuTinh:
    star_definition = _get_star_definition(star_name)
    if star_definition.star_type != "phu_tinh":
        raise ValueError(f"Star '{star_name}' is not a PhuTinh")
    return PhuTinh(name=star_definition.name, elemental=star_definition.elemental)
