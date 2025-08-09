from src.tuvi.element.types import STAR_STATUS, TYPE_DIA_CHI

# Source : https://hocvienlyso.org/14-chinh-tinh.html
MAP_START_STATUS: dict[str, dict[TYPE_DIA_CHI, STAR_STATUS]] = {
    "Tử Vi": {
        "Tý": "Đắc", "Sửu": "Đắc", "Dần": "Miếu", "Mão": "Bình", "Thìn": "Miếu", "Tị": "Miếu",
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Bình", "Tuất": "Miếu", "Hợi": "Đắc"
    },
    "Thiên Phủ": {
        "Tý": "Miếu", "Sửu": "Bình", "Dần": "Miếu", "Mão": "Bình", "Thìn": "Miếu", "Tị": None,
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Bình", "Tuất": "Miếu", "Hợi": "Đắc"
    },
    "Vũ Khúc": {
        "Tý": "Miếu", "Sửu": "Miếu", "Dần": "Miếu", "Mão": "Đắc", "Thìn": "Miếu", "Tị": "Hãm",
        "Ngọ": "Miếu", "Mùi": "Miếu", "Thân": "Miếu", "Dậu": "Đắc", "Tuất": "Miếu", "Hợi": "Hãm"
    },
    "Thiên Tướng": {
        "Tý": "Miếu", "Sửu": "Đắc", "Dần": "Miếu", "Mão": "Hãm", "Thìn": "Miếu", "Tị": "Đắc",
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Hãm", "Tuất": "Miếu", "Hợi": "Đắc"
    },
    "Thất Sát": {
        "Tý": "Miếu", "Sửu": "Đắc", "Dần": "Miếu", "Mão": "Hãm", "Thìn": "Hãm", "Tị": "Miếu",
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Hãm", "Tuất": "Hãm", "Hợi": "Miếu"
    },
    "Phá Quân": {
        "Tý": "Miếu", "Sửu": "Miếu", "Dần": "Hãm", "Mão": "Hãm", "Thìn": "Đắc", "Tị": "Hãm",
        "Ngọ": "Miếu", "Mùi": "Miếu", "Thân": "Hãm", "Dậu": "Hãm", "Tuất": "Đắc", "Hợi": "Hãm"
    },
    "Liêm Trinh": {
        "Tý": "Miếu", "Sửu": "Đắc", "Dần": "Miếu", "Mão": "Hãm", "Thìn": "Miếu", "Tị": "Hãm",
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Hãm", "Tuất": "Miếu", "Hợi": "Hãm"
    },
    "Tham Lang": {
        "Tý": "Hãm", "Sửu": "Miếu", "Dần": "Đắc", "Mão": "Hãm", "Thìn": "Miếu", "Tị": "Hãm",
        "Ngọ": "Hãm", "Mùi": "Miếu", "Thân": "Đắc", "Dậu": "Hãm", "Tuất": "Miếu", "Hợi": "Hãm"
    },
    "Thiên Cơ": {
        "Tý": "Đắc", "Sửu": "Đắc", "Dần": "Hãm", "Mão": "Miếu", "Thìn": "Miếu", "Tị": "Miếu",
        "Ngọ": "Đắc", "Mùi": "Miếu", "Thân": None, "Dậu": "Miếu", "Tuất": "Miếu", "Hợi": "Hãm"
    },
    "Thái Âm": {
        "Tý": "Miếu", "Sửu": "Đắc", "Dần": "Hãm", "Mão": "Hãm", "Thìn": "Hãm", "Tị": "Hãm",
        "Ngọ": "Hãm", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Miếu", "Tuất": "Miếu", "Hợi": "Miếu"
    },
    "Thiên Đồng": {
        "Tý": "Miếu", "Sửu": "Hãm", "Dần": "Miếu", "Mão": "Đắc", "Thìn": "Hãm", "Tị": "Đắc",
        "Ngọ": "Hãm", "Mùi": "Hãm", "Thân": "Miếu", "Dậu": "Hãm", "Tuất": "Hãm", "Hợi": "Đắc"
    },
    "Thiên Lương": {
        "Tý": "Miếu", "Sửu": "Đắc", "Dần": "Miếu", "Mão": "Miếu", "Thìn": "Miếu", "Tị": "Hãm",
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Miếu", "Dậu": "Hãm", "Tuất": "Miếu", "Hợi": "Hãm"
    },
    "Cự Môn": {
        "Tý": "Miếu", "Sửu": "Hãm", "Dần": "Miếu", "Mão": "Miếu", "Thìn": "Hãm", "Tị": "Hãm",
        "Ngọ": "Miếu", "Mùi": "Hãm", "Thân": "Đắc", "Dậu": "Miếu", "Tuất": "Hãm", "Hợi": "Đắc"
    },
    "Thái Dương": {
        "Tý": "Hãm", "Sửu": "Đắc", "Dần": "Miếu", "Mão": "Miếu", "Thìn": "Miếu", "Tị": "Miếu",
        "Ngọ": "Miếu", "Mùi": "Đắc", "Thân": "Hãm", "Dậu": "Hãm", "Tuất": "Hãm", "Hợi": "Hãm"
    },
    # Lục sát
    "Không Kiếp": {
        "Tý": "Hãm", "Sửu": "Hãm", "Dần": "Đắc", "Mão": "Hãm", "Thìn": "Hãm", "Tị": "Đắc",
        "Ngọ": "Hãm", "Mùi": "Hãm", "Thân": "Đắc", "Dậu": "Hãm", "Tuất": "Hãm", "Hợi": "Đắc"
    },
    "Kình Dương": {
        "Tý": "Hãm", "Sửu": "Đắc", "Dần": "Hãm", "Mão": "Hãm", "Thìn": "Đắc", "Tị": "Hãm",
        "Ngọ": "Hãm", "Mùi": "Đắc", "Thân": "Hãm", "Dậu": "Hãm", "Tuất": "Đắc", "Hợi": "Hãm"
    },
    "Đà La": {
        "Tý": "Hãm", "Sửu": "Hãm", "Dần": "Đắc", "Mão": "Hãm", "Thìn": "Hãm", "Tị": "Đắc",
        "Ngọ": "Hãm", "Mùi": "Hãm", "Thân": "Đắc", "Dậu": "Hãm", "Tuất": "Hãm", "Hợi": "Đắc"
    },
    "Hỏa Tinh": {
        "Tý": "Hãm", "Sửu": "Hãm", "Dần": "Đắc", "Mão": "Đắc", "Thìn": "Hãm", "Tị": "Đắc",
        "Ngọ": "Đắc", "Mùi": "Hãm", "Thân": "Hãm", "Dậu": "Hãm", "Tuất": "Hãm", "Hợi": "Hãm"
    },
    "Linh Tinh": {
        "Tý": "Hãm", "Sửu": "Đắc", "Dần": "Hãm", "Mão": "Hãm", "Thìn": "Đắc", "Tị": "Hãm",
        "Ngọ": "Hãm", "Mùi": "Đắc", "Thân": "Hãm", "Dậu": "Hãm", "Tuất": "Đắc", "Hợi": "Hãm"
    }
}
