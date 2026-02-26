from typing import Literal

NGU_HANH = Literal["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]

AM_DUONG = Literal["Am", "Duong"]

ROLE_TYPE = Literal["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc",
               "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]

TYPE_DIA_CHI = Literal["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

LIST_DIA_CHI : list[TYPE_DIA_CHI] = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
]

TYPE_THIEN_CAN = Literal["Giấp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

LIST_THIEN_CAN : list[TYPE_THIEN_CAN] = ["Giấp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

TYPE_GENDER = Literal["M", "F"]

LIST_ROLES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc",
               "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]

STAR_STATUS = Literal["Hãm", "Bình", "Đắc", "Vượng", "Miếu", None]

MAP_COLOR : dict[NGU_HANH, str] = {
    "Kim" : "#808080",
    "Mộc" : "#008000",
    "Thủy" : "#00008B",
    "Hỏa" : "#FF0000",
    "Thổ" : "#B8860B",
}
