import src.refactored.placement.primitives as pp
from src.refactored.model.elementary import CircleDirection, DiaChi

CHINH_TINH_RULES = [
    # tu, vu, liem
    pp.AbsolutePosition(
        component_id="tu_vi",
        position_fn=pp.tuvi_position_fn,
    ),
    pp.TamHop(
        component_id="vu_khuc",
        reference_id="tu_vi",
        direction=CircleDirection.CCW,
    ),
    pp.TamHop(
        component_id="liem_trinh",
        reference_id="tu_vi",
        direction=CircleDirection.CW,
    ),
    # sat, pha, tham
    pp.XungChieu(
        component_id="that_sat",
        reference_id="thien_phu",
    ),
    pp.TamHop(
        component_id="pha_quan",
        reference_id="that_sat",
        direction=CircleDirection.CW,
    ),
    pp.TamHop(
        component_id="tham_lang",
        reference_id="that_sat",
        direction=CircleDirection.CCW,
    ),
    # co, nguyet, dong, luong
    pp.NhiHop(
        component_id="thien_co",
        reference_id="pha_quan",
    ),
    pp.NhiHop(
        component_id="thai_am",
        reference_id="vu_khuc",
    ),
    pp.NhiHop(
        component_id="thien_dong",
        reference_id="tham_lang",
    ),
    pp.NhiHop(
        component_id="thien_luong",
        reference_id="liem_trinh",
    ),
    # cu, nhat
    pp.LucHai(
        component_id="cu_mon",
        reference_id="tu_vi",
    ),
    pp.NhiHop(
        component_id="thai_duong",
        reference_id="thien_phu",
    ),
    # phu, tuong
    pp.MirrorAcross(
        component_id="thien_phu",
        reference_id="tu_vi",
        axis=(DiaChi.DAN, DiaChi.THAN),
    ),
    pp.XungChieu(
        component_id="thien_tuong",
        reference_id="pha_quan",
    ),
]
