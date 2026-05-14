from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi

# TODO: This map is temporary and should be replaced by a more robust solution,
# such as loading from a config file or defining in the model layer.

MAP_STR_TO_DIACHI = {
    "Tý": DiaChi.TY,
    "Sửu": DiaChi.SUU,
    "Dần": DiaChi.DAN,
    "Mão": DiaChi.MEO,
    "Thìn": DiaChi.THIN,
    "Tỵ": DiaChi.TI,
    "Ngọ": DiaChi.NGO,
    "Mùi": DiaChi.MUI,
    "Thân": DiaChi.THAN,
    "Dậu": DiaChi.DAU,
    "Tuất": DiaChi.TUAT,
    "Hợi": DiaChi.HOI,
}

MAP_STR_TO_ROLE = {
    "Mệnh": Role.MENH,
    "Phụ Mẫu": Role.PHU_MAU,
    "Phúc Đức": Role.PHUC_DUC,
    "Điền Trạch": Role.DIEN_TRACH,
    "Quan Lộc": Role.QUAN_LOC,
    "Nô Bộc": Role.NO_BOC,
    "Thiên Di": Role.THIEN_DI,
    "Tật Ách": Role.TAT_ACH,
    "Tài Bạch": Role.TAI_BACH,
    "Tử Tức": Role.TU_TUC,
    "Phu Thê": Role.PHU_THE,
    "Huynh Đệ": Role.HUYNH_DE,
    "Thân": Role.CUNG_THAN,
}
