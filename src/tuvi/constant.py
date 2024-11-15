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
    [PhuTinh(name="Tieu Hao", elemental="Hoa")],
    [PhuTinh(name="Tướng Quân", elemental="Moc")],
    [PhuTinh(name="Tấu Thư", elemental="Kim")],
    [PhuTinh(name="Phi Liêm", elemental="Hoa")],
    [PhuTinh(name="Hỷ Thần", elemental="Hoa")],
    [PhuTinh(name="Bệnh Phù", elemental="Tho")],
    [PhuTinh(name="Đại Hao", elemental="Hoa")],
    [PhuTinh(name="Phuc Binh", elemental="Hoa")],
    [PhuTinh(name="Đà La", elemental="Kim")],
]

# TODO : Có thêm đào không sát vào đây ?
VONG_THAI_TUE = [
    [PhuTinh(name="Thái Tuế", elemental="Hoa")],
    [PhuTinh(name="Thiếu Dương", elemental="Hoa")],
    [PhuTinh(name="Tang Môn", elemental="Moc")],
    [PhuTinh(name="Thiếu Âm", elemental="Thuy")],
    [PhuTinh(name="Quan Phù", elemental="Hoa")],
    [PhuTinh(name="Tử Phù", elemental="Kim")],
    [PhuTinh(name="Tuế Phá", elemental="Hoa")],
    [PhuTinh(name="Long Đức", elemental="Thuy")],
    [PhuTinh(name="Bạch Hổ", elemental="Kim")],
    [PhuTinh(name="Phúc Đức", elemental="Tho")],
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
