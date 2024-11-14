from tuvi.sao import PhuTinh
from tuvi.types import TYPE_DIA_CHI, TYPE_THIEN_CAN


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
