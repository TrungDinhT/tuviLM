from src.tuvi.element.sao import PhuTinh
from src.tuvi.element.types import TYPE_DIA_CHI, TYPE_THIEN_CAN


MAP_LOC_TON_POSITION : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
        "Giap" : "Dần",
        "At" : "Mão",
        "Binh" : "Tị",
        "Dinh" : "Ngọ",
        "Mau" : "Tị",
        "Ky" : "Ngọ",
        "Canh" : "Thân",
        "Tan" : "Dậu",
        "Nham" : "Hợi",
        "Quy" : "Tý",
    }

# TODO : verify lực sĩ luôn đi cùng kình dương , quan phủ có theo vòng lộc tồn?
VONG_LOCTON = [
    [PhuTinh(name="Lộc Tồn", elemental="Tho"), PhuTinh(name="Bác Sĩ", elemental="Thuy")],
    [PhuTinh(name="Kình Dương", elemental="Kim")],
    [PhuTinh(name="Thanh Long", elemental="Thuy")],
    [PhuTinh(name="Tiểu Hao", elemental="Hoa"), PhuTinh(name="LN Văn Tinh", elemental="Hoa")],
    [PhuTinh(name="Tướng Quân", elemental="Moc")],
    [PhuTinh(name="Tấu Thư", elemental="Kim"), PhuTinh(name="Đường Phù", elemental="Moc")],
    [PhuTinh(name="Phi Liêm", elemental="Hoa")],
    [PhuTinh(name="Hỷ Thần", elemental="Hoa")],
    [PhuTinh(name="Bệnh Phù", elemental="Tho"), PhuTinh(name="Quốc Ấn", elemental="Tho")],
    [PhuTinh(name="Đại Hao", elemental="Hoa")],
    [PhuTinh(name="Phuc Binh", elemental="Hoa")],
    [PhuTinh(name="Đà La", elemental="Kim"), PhuTinh(name="Quan Phủ", elemental="Hoa")],
]

# TODO : Có thêm đào không sát vào đây ?
VONG_THAI_TUE = [
    [PhuTinh(name="Thái Tuế", elemental="Hoa")],
    [PhuTinh(name="Thiếu Dương", elemental="Hoa"), PhuTinh(name="Thiên Không", elemental="Hoa")],
    [PhuTinh(name="Tang Môn", elemental="Moc")],
    [PhuTinh(name="Thiếu Âm", elemental="Thuy")],
    [PhuTinh(name="Quan Phù", elemental="Hoa"), PhuTinh(name="Long Trì", elemental="Thuy")],
    [PhuTinh(name="Tử Phù", elemental="Kim"), PhuTinh(name="Nguyệt Đức", elemental="Hoa")],
    [PhuTinh(name="Tuế Phá", elemental="Hoa"), PhuTinh(name="Thiên Hư", elemental="Thuy")],
    [PhuTinh(name="Long Đức", elemental="Thuy")],
    [PhuTinh(name="Bạch Hổ", elemental="Kim")],
    [PhuTinh(name="Phúc Đức", elemental="Tho"), PhuTinh(name="Thiên Đức", elemental="Hoa")],
    [PhuTinh(name="Điếu Khách", elemental="Hoa")],
    [PhuTinh(name="Trực Phù", elemental="Kim")],
]


MAP_THIEN_KHOI : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Sửu",
    "At": "Tý",
    "Binh": "Hợi",
    "Dinh": "Hợi",
    "Mau": "Sửu",
    "Ky": "Tý",
    "Canh": "Ngọ",
    "Tan": "Ngọ",
    "Nham": "Mão",
    "Quy": "Mão"
}

MAP_THIEN_VIET : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Mùi",
    "At": "Thân",
    "Binh": "Dậu",
    "Dinh": "Dậu",
    "Mau": "Mùi",
    "Ky": "Thân",
    "Canh": "Dần",
    "Tan": "Dần",
    "Nham": "Tị",
    "Quy": "Tị"
}



# TODO : there is difference between books and web
# https://lyso.vn/xem-tu-vi/lai-mot-van-de-tranh-cai-trong-tu-vi-lan-nay-la-cach-an-luu-ha-voi-tuoi-dinh-va-canh-t102897/
MAP_LUU_HA : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Dậu",
    "At": "Tuất",
    "Binh": "Mùi",
    "Dinh": "Thìn",
    "Mau": "Tị",
    "Ky": "Ngọ",
    "Canh": "Thân",
    "Tan": "Thìn",
    "Nham": "Hợi",
    "Quy": "Dần"
}

# http://tuvi.cohoc.net/sao-thien-tru-o-menh-va-cac-cung-khac-nid-6989.html
MAP_THIEN_TRU : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Tị",
    "At": "Ngọ",
    "Binh": "Tý",
    "Dinh": "Tị",
    "Mau": "Ngọ",
    "Ky": "Thân",
    "Canh": "Dần",
    "Tan": "Ngọ",
    "Nham": "Dậu",
    "Quy": "Tuất"
}

# http://tuvi.cohoc.net/sao-thien-quan-thien-phuc-y-nghia-tai-menh-va-cung-khac-nid-6953.html
MAP_THIEN_QUAN : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Mùi",
    "At": "Mùi",
    "Binh": "Thìn",
    "Dinh": "Dần",
    "Mau": "Mão",
    "Ky": "Dậu",
    "Canh": "Hợi",
    "Tan": "Dậu",
    "Nham": "Tuất",
    "Quy": "Ngọ"
}

MAP_THIEN_PHUC : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Dậu",
    "At": "Dậu",
    "Binh": "Thân",
    "Dinh": "Hợi",
    "Mau": "Mão",
    "Ky": "Dần",
    "Canh": "Ngọ",
    "Tan": "Tị",
    "Nham": "Ngọ",
    "Quy": "Tị"
}


MAP_TUHOA : dict[TYPE_THIEN_CAN, list[str]] = {
    "Giap": ["Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"],
    "At": ["Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"],
    "Binh": ["Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"],
    "Dinh": ["Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"],
    "Mau": ["Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"],
    "Ky": ["Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"],
    "Canh": ["Thái Dương", "Vũ Khúc", "Thiên Đồng", "Thái Âm"],
    "Tan": ["Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"],
    "Nham": ["Thiên Lương", "Tử Vi", "Thiên Phủ", "Vũ Khúc"],
    "Quy": ["Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"]
}

MAP_TRIET : dict[TYPE_THIEN_CAN, list[TYPE_DIA_CHI]] = {
    "Giap": ["Thân", "Dậu"],
    "At": ["Ngọ", "Mùi"],
    "Binh": ["Thìn", "Tị"],
    "Dinh": ["Dần", "Mão"],
    "Mau": ["Tý", "Sửu"],
    "Ky": ["Thân", "Dậu"],
    "Canh": ["Ngọ", "Mùi"],
    "Tan": ["Thìn", "Tị"],
    "Nham": ["Dần", "Mão"],
    "Quy": ["Tý", "Sửu"],
}

MAP_TUAN : dict[TYPE_DIA_CHI, TYPE_DIA_CHI] = {
    "Tý" : ["Tuất", "Hợi"],
    "Dần" : ["Tý", "Sửu"],
    "Thìn" : ["Dần", "Mão"],
    "Ngọ" : ["Thìn", "Tị"],
    "Thân" : ["Ngọ", "Mùi"],
    "Tuất" : ["Thân", "Dậu"],
}
