from src.refactored.model.elementary import DiaChi
from src.refactored.components.definitions.sao import Status


# Source : https://hocvienlyso.org/14-chinh-tinh.html
MAP_SAO_STATUS: dict[str, dict[DiaChi, Status]] = {
    "tu_vi": {
        DiaChi.TY: Status.DAC, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.BINH,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.MIEU, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.BINH, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.DAC,
    },
    "thien_phu": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.BINH, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.BINH,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.BINH, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.DAC,
    },
    "vu_khuc": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.MIEU, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.DAC,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.MIEU,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.DAC, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.HAM,
    },
    "thien_tuong": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.DAC,
    },
    "that_sat": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.MIEU, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.MIEU,
    },
    "pha_quan": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.MIEU, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.DAC, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.MIEU,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.DAC, DiaChi.HOI: Status.HAM,
    },
    "liem_trinh": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.HAM,
    },
    "tham_lang": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.MIEU, DiaChi.DAN: Status.DAC, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.MIEU,
        DiaChi.THAN: Status.DAC, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.HAM,
    },
    "thien_co": {
        DiaChi.TY: Status.DAC, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.MIEU,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.MIEU, DiaChi.NGO: Status.DAC, DiaChi.MUI: Status.MIEU,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.MIEU, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.HAM,
    },
    "thai_am": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.MIEU, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.MIEU,
    },
    "thien_dong": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.DAC,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.DAC,
    },
    "thien_luong": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.MIEU,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.MIEU, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.HAM,
    },
    "cu_mon": {
        DiaChi.TY: Status.MIEU, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.MIEU,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.DAC, DiaChi.DAU: Status.MIEU, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.DAC,
    },
    "thai_duong": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.MIEU,
        DiaChi.THIN: Status.MIEU, DiaChi.TI: Status.MIEU, DiaChi.NGO: Status.MIEU, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.HAM,
    },
    "dia_khong": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.DAC, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.DAC, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.DAC,
    },
    "dia_kiep": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.DAC, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.DAC, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.DAC,
    },
    "kinh_duong": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.DAC, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.DAC, DiaChi.HOI: Status.HAM,
    },
    "da_la": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.DAC, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.DAC, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.DAC,
    },
    "hoa_tinh": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.DAC, DiaChi.MEO: Status.DAC,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.DAC, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.HAM,
    },
    "linh_tinh": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.HAM,
        DiaChi.THIN: Status.DAC, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.HAM, DiaChi.TUAT: Status.DAC, DiaChi.HOI: Status.HAM,
    },
    "van_xuong": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.DAC,
        DiaChi.THIN: Status.DAC, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.DAC, DiaChi.TUAT: Status.DAC, DiaChi.HOI: Status.DAC,
    },
    "van_khuc": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.DAC, DiaChi.DAN: Status.HAM, DiaChi.MEO: Status.DAC,
        DiaChi.THIN: Status.DAC, DiaChi.TI: Status.DAC, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.DAC,
        DiaChi.THAN: Status.HAM, DiaChi.DAU: Status.DAC, DiaChi.TUAT: Status.DAC, DiaChi.HOI: Status.DAC,
    },
    "thien_dieu": {
        DiaChi.TY: Status.HAM, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.DAC, DiaChi.MEO: Status.DAC,
        DiaChi.THIN: Status.HAM, DiaChi.TI: Status.HAM, DiaChi.NGO: Status.HAM, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.DAC, DiaChi.DAU: Status.DAC, DiaChi.TUAT: Status.HAM, DiaChi.HOI: Status.HAM,
    },
    "thien_hinh": { # Source: https://tuvinamphai.vn/sao-thien-hinh-d82
        DiaChi.TY: Status.BINH, DiaChi.SUU: Status.HAM, DiaChi.DAN: Status.MIEU, DiaChi.MEO: Status.MIEU,
        DiaChi.THIN: Status.BINH, DiaChi.TI: Status.BINH, DiaChi.NGO: Status.BINH, DiaChi.MUI: Status.HAM,
        DiaChi.THAN: Status.BINH, DiaChi.DAU: Status.MIEU, DiaChi.TUAT: Status.MIEU, DiaChi.HOI: Status.BINH,
    },
}
