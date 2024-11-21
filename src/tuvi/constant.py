from src.tuvi.sao import PhuTinh
from src.tuvi.types import TYPE_DIA_CHI, TYPE_THIEN_CAN


MAP_LOC_TON_POSITION : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
        "Giap" : "Dan",
        "At" : "Mao",
        "Binh" : "Ti",
        "Dinh" : "Ngo",
        "Mau" : "Ti",
        "Ky" : "Ngo",
        "Canh" : "Than",
        "Tan" : "Dau",
        "Nham" : "Hoi",
        "Quy" : "Ty",
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
    "Giap": "Mui",
    "At": "Than",
    "Binh": "Dau",
    "Dinh": "Hoi",
    "Mau": "Suu",
    "Ky": "Ty",
    "Canh": "Suu",
    "Tan": "Dan",
    "Nham": "Mao",
    "Quy": "Ti"
}

MAP_THIEN_VIET : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Suu",
    "At": "Ty",
    "Binh": "Hoi",
    "Dinh": "Dau",
    "Mau": "Mui",
    "Ky": "Than",
    "Canh": "Mui",
    "Tan": "Ngo",
    "Nham": "Ti",
    "Quy": "Mao"
}



# TODO : there is difference between books and web
# https://lyso.vn/xem-tu-vi/lai-mot-van-de-tranh-cai-trong-tu-vi-lan-nay-la-cach-an-luu-ha-voi-tuoi-dinh-va-canh-t102897/
MAP_LUU_HA : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Dau",
    "At": "Tuat",
    "Binh": "Mui",
    "Dinh": "Thin",
    "Mau": "Ti",
    "Ky": "Ngo",
    "Canh": "Than",
    "Tan": "Thin",
    "Nham": "Hoi",
    "Quy": "Dan"
}

# http://tuvi.cohoc.net/sao-thien-tru-o-menh-va-cac-cung-khac-nid-6989.html
MAP_THIEN_TRU : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Ti",
    "At": "Ngo",
    "Binh": "Ty",
    "Dinh": "Ti",
    "Mau": "Ngo",
    "Ky": "Than",
    "Canh": "Dan",
    "Tan": "Ngo",
    "Nham": "Dau",
    "Quy": "Tuat"
}


MAP_THIEN_QUAN : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Mui",
    "At": "Mui",
    "Binh": "Thin",
    "Dinh": "Dan",
    "Mau": "Mao",
    "Ky": "Dau",
    "Canh": "Hoi",
    "Tan": "Dau",
    "Nham": "Tuat",
    "Quy": "Ngo"
}

MAP_THIEN_PHUC : dict[TYPE_THIEN_CAN, TYPE_DIA_CHI] = {
    "Giap": "Dau",
    "At": "Dau",
    "Binh": "Than",
    "Dinh": "Hoi",
    "Mau": "Mao",
    "Ky": "Dan",
    "Canh": "Ngo",
    "Tan": "Ti",
    "Nham": "Ngo",
    "Quy": "Ti"
}
