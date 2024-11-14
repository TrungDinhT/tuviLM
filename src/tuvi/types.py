from typing import Literal

NGU_HANH = Literal["Kim", "Moc", "Thuy", "Hoa", "Tho"]

AM_DUONG = Literal["Am", "Duong"]

ROLE_TYPE = Literal["Menh", "Phu Mau", "Phuc Duc", "Dien Trach", "Quan Loc", "No Boc",
               "Thien Di", "Tat Ach", "Tai Bach", "Tu Tuc", "Phu The", "Huynh De"]

TYPE_DIA_CHI = Literal["Ty", "Suu", "Dan", "Mao", "Thin", "Ti", "Ngo", "Mui", "Than", "Dau", "Tuat", "Hoi"]

LIST_DIA_CHI : list[TYPE_DIA_CHI] = [
    "Ty", "Suu", "Dan", "Mao", "Thin", "Ti", "Ngo", "Mui", "Than", "Dau", "Tuat", "Hoi"
]

TYPE_THIEN_CAN = Literal["Giap", "At", "Binh", "Dinh", "Mau", "Ky", "Canh", "Tan", "Nham", "Quy"]

LIST_THIEN_CAN : TYPE_THIEN_CAN = ["Giap", "At", "Binh", "Dinh", "Mau", "Ky", "Canh", "Tan", "Nham", "Quy"]

LIST_ROLES = ["Menh", "Phu Mau", "Phuc Duc", "Dien Trach", "Quan Loc", "No Boc",
               "Thien Di", "Tat Ach", "Tai Bach", "Tu Tuc", "Phu The", "Huynh De"]

STAR_STATUS = Literal["Ham", "Binh", "Dac", "Vuong", "Mieu", None]

MAP_COLOR : dict[NGU_HANH, str] = {
    "Kim" : "#808080",
    "Moc" : "#008000",
    "Thuy" : "#A9A9A9",
    "Hoa" : "#FF0000",
    "Tho" : "#B8860B",
}
