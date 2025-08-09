from typing import Literal

NGU_HANH = Literal["Kim", "Moc", "Thuy", "Hoa", "Tho"]

AM_DUONG = Literal["Am", "Duong"]

ROLE_TYPE = Literal["Menh", "Phu Mậu", "Phuc Duc", "Dien Trach", "Quan Loc", "No Boc",
               "Thien Di", "Tat Ach", "Tai Bach", "Tu Tuc", "Phu The", "Huynh De"]

TYPE_DIA_CHI = Literal["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

LIST_DIA_CHI : list[TYPE_DIA_CHI] = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
]

TYPE_THIEN_CAN = Literal["Giấp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

LIST_THIEN_CAN : TYPE_THIEN_CAN = ["Giấp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

TYPE_GENDER = Literal["M", "F"]

LIST_ROLES = ["Menh", "Phu Mậu", "Phuc Duc", "Dien Trach", "Quan Loc", "No Boc",
               "Thien Di", "Tat Ach", "Tai Bach", "Tu Tuc", "Phu The", "Huynh De"]

STAR_STATUS = Literal["Ham", "Bính", "Dac", "Vuong", "Mieu", None]

MAP_COLOR : dict[NGU_HANH, str] = {
    "Kim" : "#808080",
    "Moc" : "#008000",
    "Thuy" : "#00008B",
    "Hoa" : "#FF0000",
    "Tho" : "#B8860B",
}
