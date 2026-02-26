from src.tuvi.element.types import TYPE_DIA_CHI, TYPE_THIEN_CAN


MAP_LOC_TON_POSITION : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
        "Giấp" : "Dần",
        "Ất" : "Mão",
        "Bính" : "Tị",
        "Đinh" : "Ngọ",
        "Mậu" : "Tị",
        "Kỷ" : "Ngọ",
        "Canh" : "Thân",
        "Tân" : "Dậu",
        "Nhâm" : "Hợi",
        "Quý" : "Tý",
    }

# TODO : verify lực sĩ luôn đi cùng kình dương , quan phủ có theo vòng lộc tồn?
VONG_LOCTON = [
    ["Lộc Tồn", "Bác Sĩ"],
    ["Kình Dương"],
    ["Thanh Long"],
    ["Tiểu Hao", "LN Văn Tinh"],
    ["Tướng Quân"],
    ["Tấu Thư", "Đường Phù"],
    ["Phi Liêm"],
    ["Hỷ Thần"],
    ["Bệnh Phù", "Quốc Ấn"],
    ["Đại Hao"],
    ["Phục Binh"],
    ["Đà La", "Quan Phủ"],
]

# TODO : Có thêm đào không sát vào đây ?
VONG_THAI_TUE = [
    ["Thái Tuế"],
    ["Thiếu Dương", "Thiên Không"],
    ["Tang Môn"],
    ["Thiếu Âm"],
    ["Quan Phù", "Long Trì"],
    ["Tử Phù", "Nguyệt Đức"],
    ["Tuế Phá", "Thiên Hư"],
    ["Long Đức"],
    ["Bạch Hổ"],
    ["Phúc Đức", "Thiên Đức"],
    ["Điếu Khách"],
    ["Trực Phù"],
]


MAP_THIEN_KHOI : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giấp": "Sửu",
    "Ất": "Tý",
    "Bính": "Hợi",
    "Đinh": "Hợi",
    "Mậu": "Sửu",
    "Kỷ": "Tý",
    "Canh": "Ngọ",
    "Tân": "Ngọ",
    "Nhâm": "Mão",
    "Quý": "Mão"
}

MAP_THIEN_VIET : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giấp": "Mùi",
    "Ất": "Thân",
    "Bính": "Dậu",
    "Đinh": "Dậu",
    "Mậu": "Mùi",
    "Kỷ": "Thân",
    "Canh": "Dần",
    "Tân": "Dần",
    "Nhâm": "Tị",
    "Quý": "Tị"
}



# TODO : there is difference between books and web
# https://lyso.vn/xem-tu-vi/lai-mot-van-de-tranh-cai-trong-tu-vi-lan-nay-la-cach-an-luu-ha-voi-tuoi-dinh-va-canh-t102897/
MAP_LUU_HA : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giấp": "Dậu",
    "Ất": "Tuất",
    "Bính": "Mùi",
    "Đinh": "Thìn",
    "Mậu": "Tị",
    "Kỷ": "Ngọ",
    "Canh": "Thân",
    "Tân": "Thìn",
    "Nhâm": "Hợi",
    "Quý": "Dần"
}

# http://tuvi.cohoc.net/sao-thien-tru-o-menh-va-cac-cung-khac-nid-6989.html
MAP_THIEN_TRU : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giấp": "Tị",
    "Ất": "Ngọ",
    "Bính": "Tý",
    "Đinh": "Tị",
    "Mậu": "Ngọ",
    "Kỷ": "Thân",
    "Canh": "Dần",
    "Tân": "Ngọ",
    "Nhâm": "Dậu",
    "Quý": "Tuất"
}

# http://tuvi.cohoc.net/sao-thien-quan-thien-phuc-y-nghia-tai-menh-va-cung-khac-nid-6953.html
MAP_THIEN_QUAN : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giấp": "Mùi",
    "Ất": "Mùi",
    "Bính": "Thìn",
    "Đinh": "Dần",
    "Mậu": "Mão",
    "Kỷ": "Dậu",
    "Canh": "Hợi",
    "Tân": "Dậu",
    "Nhâm": "Tuất",
    "Quý": "Ngọ"
}

MAP_THIEN_PHUC : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giấp": "Dậu",
    "Ất": "Dậu",
    "Bính": "Thân",
    "Đinh": "Hợi",
    "Mậu": "Mão",
    "Kỷ": "Dần",
    "Canh": "Ngọ",
    "Tân": "Tị",
    "Nhâm": "Ngọ",
    "Quý": "Tị"
}


MAP_TUHOA : dict[TYPE_THIEN_CAN, list[str]] = {
    "Giấp": ["Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"],
    "Ất": ["Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"],
    "Bính": ["Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"],
    "Đinh": ["Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"],
    "Mậu": ["Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"],
    "Kỷ": ["Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"],
    "Canh": ["Thái Dương", "Vũ Khúc", "Thiên Đồng", "Thái Âm"],
    "Tân": ["Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"],
    "Nhâm": ["Thiên Lương", "Tử Vi", "Thiên Phủ", "Vũ Khúc"],
    "Quý": ["Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"]
}

MAP_TRIET : dict[TYPE_THIEN_CAN, list[TYPE_DIA_CHI]] = {
    "Giấp": ["Thân", "Dậu"],
    "Ất": ["Ngọ", "Mùi"],
    "Bính": ["Thìn", "Tị"],
    "Đinh": ["Dần", "Mão"],
    "Mậu": ["Tý", "Sửu"],
    "Kỷ": ["Thân", "Dậu"],
    "Canh": ["Ngọ", "Mùi"],
    "Tân": ["Thìn", "Tị"],
    "Nhâm": ["Dần", "Mão"],
    "Quý": ["Tý", "Sửu"],
}

MAP_TUAN : dict[TYPE_DIA_CHI, list[TYPE_DIA_CHI]] = {
    "Tý" : ["Tuất", "Hợi"],
    "Dần" : ["Tý", "Sửu"],
    "Thìn" : ["Dần", "Mão"],
    "Ngọ" : ["Thìn", "Tị"],
    "Thân" : ["Ngọ", "Mùi"],
    "Tuất" : ["Thân", "Dậu"],
}
