import src.refactored.placement.primitives as pp
from src.refactored.model.elementary import ThienCan

TU_HOA_TARGET_BY_THIEN_CAN: dict[ThienCan, dict[pp.TuHoaEntity, str]] = {
    ThienCan.GIAP: {
        "hoa_loc": "liem_trinh",
        "hoa_quyen": "pha_quan",
        "hoa_khoa": "vu_khuc",
        "hoa_ky": "thai_duong",
    },
    ThienCan.AT: {
        "hoa_loc": "thien_co",
        "hoa_quyen": "thien_luong",
        "hoa_khoa": "tu_vi",
        "hoa_ky": "thai_am",
    },
    ThienCan.BINH: {
        "hoa_loc": "thien_dong",
        "hoa_quyen": "thien_co",
        "hoa_khoa": "van_xuong",
        "hoa_ky": "liem_trinh",
    },
    ThienCan.DINH: {
        "hoa_loc": "thai_am",
        "hoa_quyen": "thien_dong",
        "hoa_khoa": "thien_co",
        "hoa_ky": "cu_mon",
    },
    ThienCan.MAU: {
        "hoa_loc": "tham_lang",
        "hoa_quyen": "thai_am",
        "hoa_khoa": "huu_bat",
        "hoa_ky": "thien_co",
    },
    ThienCan.KY: {
        "hoa_loc": "vu_khuc",
        "hoa_quyen": "tham_lang",
        "hoa_khoa": "thien_luong",
        "hoa_ky": "van_khuc",
    },
    ThienCan.CANH: {
        "hoa_loc": "thai_duong",
        "hoa_quyen": "vu_khuc",
        "hoa_khoa": "thien_dong",
        "hoa_ky": "thai_am",
    },
    ThienCan.TAN: {
        "hoa_loc": "cu_mon",
        "hoa_quyen": "thai_duong",
        "hoa_khoa": "van_khuc",
        "hoa_ky": "van_xuong",
    },
    ThienCan.NHAM: {
        "hoa_loc": "thien_luong",
        "hoa_quyen": "tu_vi",
        "hoa_khoa": "thien_phu",
        "hoa_ky": "vu_khuc",
    },
    ThienCan.QUY: {
        "hoa_loc": "pha_quan",
        "hoa_quyen": "cu_mon",
        "hoa_khoa": "thai_am",
        "hoa_ky": "tham_lang",
    },
}

TU_HOA_RULES = [pp.TuHoaPosition(mapping=TU_HOA_TARGET_BY_THIEN_CAN)]
