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
    having_luu: bool = False
    short_names: list[str] | None = None


STAR_REGISTRY: dict[str, StarDefinition] = {
    "Tử Vi": StarDefinition(name="Tử Vi", elemental="Thổ", star_type="chinh_tinh", short_names=["Tử"]),
    "Thiên Phủ": StarDefinition(name="Thiên Phủ", elemental="Thổ", star_type="chinh_tinh", short_names=["Phủ"]),
    "Thái Dương": StarDefinition(name="Thái Dương", elemental="Hỏa", star_type="chinh_tinh", short_names=["Dương", "Nhật"]),
    "Vũ Khúc": StarDefinition(name="Vũ Khúc", elemental="Kim", star_type="chinh_tinh", short_names=["Vũ"]),
    "Liêm Trinh": StarDefinition(name="Liêm Trinh", elemental="Hỏa", star_type="chinh_tinh", short_names=["Liêm"]),
    "Thất Sát": StarDefinition(name="Thất Sát", elemental="Kim", star_type="chinh_tinh", short_names=["Sát"]),
    "Tham Lang": StarDefinition(name="Tham Lang", elemental="Thủy", star_type="chinh_tinh", short_names=["Tham"]),
    "Phá Quân": StarDefinition(name="Phá Quân", elemental="Thủy", star_type="chinh_tinh", short_names=["Phá"]),
    "Thiên Đồng": StarDefinition(name="Thiên Đồng", elemental="Thủy", star_type="chinh_tinh", short_names=["Đồng"]),
    "Thiên Cơ": StarDefinition(name="Thiên Cơ", elemental="Mộc", star_type="chinh_tinh", short_names=["Cơ"]),
    "Thái Âm": StarDefinition(name="Thái Âm", elemental="Thủy", star_type="chinh_tinh", short_names=["Âm", "Nguyệt"]),
    "Thiên Lương": StarDefinition(name="Thiên Lương", elemental="Mộc", star_type="chinh_tinh", short_names=["Lương"]),
    "Cự Môn": StarDefinition(name="Cự Môn", elemental="Thủy", star_type="chinh_tinh", short_names=["Cự"]),
    "Thiên Tướng": StarDefinition(name="Thiên Tướng", elemental="Thủy", star_type="chinh_tinh", short_names=["Tướng"]),
    "Thiên Sứ": StarDefinition(name="Thiên Sứ", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Thuơng": StarDefinition(name="Thiên Thuơng", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Thọ": StarDefinition(name="Thiên Thọ", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Tài": StarDefinition(name="Thiên Tài", elemental="Thổ", star_type="phu_tinh"),
    "Tả Phù": StarDefinition(name="Tả Phù", elemental="Thổ", star_type="phu_tinh", short_names=["Tả", "Phù"]),
    "Hữu Bật": StarDefinition(name="Hữu Bật", elemental="Thủy", star_type="phu_tinh", short_names=["Hữu", "Bật"]),
    "Thiên Giải": StarDefinition(name="Thiên Giải", elemental="Hỏa", star_type="phu_tinh"),
    "Địa Giải": StarDefinition(name="Địa Giải", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Hình": StarDefinition(name="Thiên Hình", elemental="Hỏa", star_type="phu_tinh", short_names=["Hình"]),
    "Tam Thai": StarDefinition(name="Tam Thai", elemental="Thủy", star_type="phu_tinh", short_names=["Thai"]),
    "Bát Toạ": StarDefinition(name="Bát Toạ", elemental="Mộc", star_type="phu_tinh", short_names=["Tọa"]),
    "Thiên Diêu": StarDefinition(name="Thiên Diêu", elemental="Thủy", star_type="phu_tinh", short_names=["Diêu", "Riêu"]),
    "Thiên Y": StarDefinition(name="Thiên Y", elemental="Thủy", star_type="phu_tinh", short_names=["Y"]),
    "Địa Không": StarDefinition(name="Địa Không", elemental="Hỏa", star_type="phu_tinh", short_names=["Không"]),
    "Địa Kiếp": StarDefinition(name="Địa Kiếp", elemental="Hỏa", star_type="phu_tinh", short_names=["Kiếp"]),
    "Văn Xương": StarDefinition(name="Văn Xương", elemental="Kim", star_type="phu_tinh", having_luu=True, short_names=["Xương"]),
    "Văn Khúc": StarDefinition(name="Văn Khúc", elemental="Thủy", star_type="phu_tinh", having_luu=True, short_names=["Khúc"]),
    "Ân Quang": StarDefinition(name="Ân Quang", elemental="Mộc", star_type="phu_tinh", short_names=["Quang"]),
    "Thiên Quý": StarDefinition(name="Thiên Quý", elemental="Thổ", star_type="phu_tinh", short_names=["Quý"]),
    "Thai Phụ": StarDefinition(name="Thai Phụ", elemental="Kim", star_type="phu_tinh"),
    "Phong Cáo": StarDefinition(name="Phong Cáo", elemental="Thổ", star_type="phu_tinh", short_names=["Phong", "Cáo"]),
    "Thiên Khôi": StarDefinition(name="Thiên Khôi", elemental="Hỏa", star_type="phu_tinh", having_luu=True, short_names=["Khôi"]),
    "Thiên Việt": StarDefinition(name="Thiên Việt", elemental="Hỏa", star_type="phu_tinh", having_luu=True, short_names=["Việt"]),
    "Lực Sĩ": StarDefinition(name="Lực Sĩ", elemental="Thủy", star_type="phu_tinh"),
    "Hỏa Tinh": StarDefinition(name="Hỏa Tinh", elemental="Hỏa", star_type="phu_tinh", short_names=["Hỏa"]),
    "Linh Tinh": StarDefinition(name="Linh Tinh", elemental="Hỏa", star_type="phu_tinh", short_names=["Linh"]),
    "Lưu Hà": StarDefinition(name="Lưu Hà", elemental="Thủy", star_type="phu_tinh"),
    "Thiên Trù": StarDefinition(name="Thiên Trù", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Quan": StarDefinition(name="Thiên Quan", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Phúc": StarDefinition(name="Thiên Phúc", elemental="Thổ", star_type="phu_tinh"),
    "Cô Thần": StarDefinition(name="Cô Thần", elemental="Thổ", star_type="phu_tinh", short_names=["Cô"]),
    "Quả Tú": StarDefinition(name="Quả Tú", elemental="Thổ", star_type="phu_tinh", short_names=["Quả"]),
    "Đẩu Quân": StarDefinition(name="Đẩu Quân", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Hỉ": StarDefinition(name="Thiên Hỉ", elemental="Hỏa", star_type="phu_tinh", short_names=["Hỉ"]),
    "Hồng Loan": StarDefinition(name="Hồng Loan", elemental="Thủy", star_type="phu_tinh", having_luu=True, short_names=["Hồng"]),
    "Thiên Mã": StarDefinition(name="Thiên Mã", elemental="Hỏa", star_type="phu_tinh", having_luu=True, short_names=["Mã"]),
    "Giải Thần": StarDefinition(name="Giải Thần", elemental="Mộc", star_type="phu_tinh"),
    "Phượng Các": StarDefinition(name="Phượng Các", elemental="Thổ", star_type="phu_tinh"),
    "Phá Toái": StarDefinition(name="Phá Toái", elemental="Hỏa", star_type="phu_tinh"),
    "Hoa Cái": StarDefinition(name="Hoa Cái", elemental="Kim", star_type="phu_tinh", short_names=["Cái"]),
    "Đào Hoa": StarDefinition(name="Đào Hoa", elemental="Mộc", star_type="phu_tinh", short_names=["Đào"]),
    "Thiên Khốc": StarDefinition(name="Thiên Khốc", elemental="Thủy", star_type="phu_tinh", having_luu=True, short_names=["Khốc"]),
    "Kiếp Sát": StarDefinition(name="Kiếp Sát", elemental="Hỏa", star_type="phu_tinh", short_names=["Sát"]),
    "Thiên La": StarDefinition(name="Thiên La", elemental="Kim", star_type="phu_tinh", short_names=["La"]),
    "Địa Võng": StarDefinition(name="Địa Võng", elemental="Kim", star_type="phu_tinh", short_names=["Võng"]),
    "Lộc Tồn": StarDefinition(name="Lộc Tồn", elemental="Thổ", star_type="phu_tinh", having_luu=True, short_names=["Lộc", "Tồn"]),
    "Bác Sĩ": StarDefinition(name="Bác Sĩ", elemental="Thủy", star_type="phu_tinh"),
    "Kình Dương": StarDefinition(name="Kình Dương", elemental="Kim", star_type="phu_tinh", short_names=["Kình"]),
    "Thanh Long": StarDefinition(name="Thanh Long", elemental="Thủy", star_type="phu_tinh", short_names=["Long"]),
    "Tiểu Hao": StarDefinition(name="Tiểu Hao", elemental="Hỏa", star_type="phu_tinh", short_names=["Hao"]),
    "LN Văn Tinh": StarDefinition(name="LN Văn Tinh", elemental="Hỏa", star_type="phu_tinh", short_names=["Văn Tinh", "Lưu Niên"]),
    "Tướng Quân": StarDefinition(name="Tướng Quân", elemental="Mộc", star_type="phu_tinh", short_names=["Tướng"]),
    "Tấu Thư": StarDefinition(name="Tấu Thư", elemental="Kim", star_type="phu_tinh", short_names=["Thư"]),
    "Đường Phù": StarDefinition(name="Đường Phù", elemental="Mộc", star_type="phu_tinh"),
    "Phi Liêm": StarDefinition(name="Phi Liêm", elemental="Hỏa", star_type="phu_tinh", short_names=["Phi"]),
    "Hỷ Thần": StarDefinition(name="Hỷ Thần", elemental="Hỏa", star_type="phu_tinh"),
    "Bệnh Phù": StarDefinition(name="Bệnh Phù", elemental="Thổ", star_type="phu_tinh", short_names=["Bệnh"]),
    "Quốc Ấn": StarDefinition(name="Quốc Ấn", elemental="Thổ", star_type="phu_tinh", short_names=["Ấn"]),
    "Đại Hao": StarDefinition(name="Đại Hao", elemental="Hỏa", star_type="phu_tinh", short_names=["Hao"]),
    "Phục Binh": StarDefinition(name="Phục Binh", elemental="Hỏa", star_type="phu_tinh", short_names=["Binh"]),
    "Đà La": StarDefinition(name="Đà La", elemental="Kim", star_type="phu_tinh", short_names=["Đà"]),
    "Quan Phủ": StarDefinition(name="Quan Phủ", elemental="Hỏa", star_type="phu_tinh"),
    "Thái Tuế": StarDefinition(name="Thái Tuế", elemental="Hỏa", star_type="phu_tinh", short_names=["Tuế"]),
    "Thiếu Dương": StarDefinition(name="Thiếu Dương", elemental="Hỏa", star_type="phu_tinh"),
    "Thiên Không": StarDefinition(name="Thiên Không", elemental="Hỏa", star_type="phu_tinh", short_names=["Không"]),
    "Tang Môn": StarDefinition(name="Tang Môn", elemental="Mộc", star_type="phu_tinh", short_names=["Tang"]),
    "Thiếu Âm": StarDefinition(name="Thiếu Âm", elemental="Thủy", star_type="phu_tinh"),
    "Quan Phù": StarDefinition(name="Quan Phù", elemental="Hỏa", star_type="phu_tinh"),
    "Long Trì": StarDefinition(name="Long Trì", elemental="Thủy", star_type="phu_tinh", short_names=["Long"]),
    "Tử Phù": StarDefinition(name="Tử Phù", elemental="Kim", star_type="phu_tinh"),
    "Nguyệt Đức": StarDefinition(name="Nguyệt Đức", elemental="Hỏa", star_type="phu_tinh"),
    "Tuế Phá": StarDefinition(name="Tuế Phá", elemental="Hỏa", star_type="phu_tinh", short_names=["Tuế"]),
    "Thiên Hư": StarDefinition(name="Thiên Hư", elemental="Thủy", star_type="phu_tinh", having_luu=True, short_names=["Hư"]),
    "Long Đức": StarDefinition(name="Long Đức", elemental="Thủy", star_type="phu_tinh"),
    "Bạch Hổ": StarDefinition(name="Bạch Hổ", elemental="Kim", star_type="phu_tinh", short_names=["Hổ"]),
    "Phúc Đức": StarDefinition(name="Phúc Đức", elemental="Thổ", star_type="phu_tinh"),
    "Thiên Đức": StarDefinition(name="Thiên Đức", elemental="Hỏa", star_type="phu_tinh"),
    "Điếu Khách": StarDefinition(name="Điếu Khách", elemental="Hỏa", star_type="phu_tinh", short_names=["Khách", "Điếu"]),
    "Trực Phù": StarDefinition(name="Trực Phù", elemental="Kim", star_type="phu_tinh"),
}

STAR_NAME = Literal[tuple(STAR_REGISTRY.keys())]

def _get_star_definition(star_name: str) -> StarDefinition:
    if star_name not in STAR_REGISTRY:
        raise KeyError(f"Star '{star_name}' is not registered")
    return STAR_REGISTRY[star_name]


def make_chinh_tinh(star_name: str) -> ChinhTinh:
    star_definition = _get_star_definition(star_name)
    if star_definition.star_type != "chinh_tinh":
        raise ValueError(f"Star '{star_name}' is not a ChinhTinh")
    return ChinhTinh(
        name=star_definition.name,
        elemental=star_definition.elemental,
        have_luu=star_definition.having_luu,
        short_names=star_definition.short_names
    )


def make_phu_tinh(star_name: str) -> PhuTinh:
    star_definition = _get_star_definition(star_name)
    if star_definition.star_type != "phu_tinh":
        raise ValueError(f"Star '{star_name}' is not a PhuTinh")
    return PhuTinh(
        name=star_definition.name,
        elemental=star_definition.elemental,
        have_luu=star_definition.having_luu,
        short_names=star_definition.short_names
    )
