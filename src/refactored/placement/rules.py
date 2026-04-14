import src.refactored.placement.primitives as pp
from src.refactored.component.elementary import CircleDirection, DiaChi


CUNG_RULES = [
    pp.Vong(
        principal_id="menh",
        principal_position_fn=lambda context: context.menh_position,
        others=[
            "phu_mau",
            "phuc_duc",
            "dien_trach",
            "quan_loc",
            "no_boc",
            "thien_di",
            "tat_ach",
            "tai_bach",
            "tu_tuc",
            "phu_the",
            "huynh_de",
        ],
    ),
    pp.RelativePosition(
        component_id="than",
        reference_id="menh",
        transform=pp.move_by_birth_hour(
            direction=CircleDirection.CW,
            step_multiplier=2,
        ),
    ),
]

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

PHU_TINH_RULES = [
    # Vong Loc Ton
    pp.Vong(
        principal_id="loc_ton",
        principal_position_fn=pp.loc_ton_position_fn,
        others=[
            "kinh_duong",
            "thanh_long",
            pp.same_slot("tieu_hao", "ln_van_tinh"),
            "tuong_quan",
            pp.same_slot("tau_thu", "duong_phu"),
            "phi_liem",
            "hy_than",
            pp.same_slot("benh_phu", "quoc_an"),
            "dai_hao",
            "phuc_binh",
            pp.same_slot("da_la", "quan_phur"),
        ],
    ),
    pp.SamePosition(
        component_id="bac_si",
        reference_id="loc_ton",
    ),
    pp.RelativePosition(
        component_id="luc_si",
        reference_id="loc_ton",
        transform=pp.move_by_van_direction(lambda _context: 1),
    ),

    # Vong Thai Tue
    pp.Vong(
        principal_id="thai_tue",
        principal_position_fn=pp.thai_tue_position_fn,
        others=[
            pp.same_slot("thieu_duong", "thien_khong"),
            "tang_mon",
            "thieu_am",
            pp.same_slot("quan_phuf", "long_tri"),
            pp.same_slot("tu_phu", "nguyet_duc"),
            pp.same_slot("tue_pha", "thien_hu"),
            "long_duc",
            "bach_ho",
            pp.same_slot("sao_phuc_duc", "thien_duc"),
            "dieu_khach",
            "truc_phu",
        ],
    ),

    # An theo thang
    pp.FromAnchor(
        component_id="ta_phu",
        anchor=DiaChi.THIN,
        transform=pp.move_by_birth_month(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="huu_bat",
        anchor=DiaChi.TUAT,
        transform=pp.move_by_birth_month(direction=CircleDirection.CCW),
    ),
    pp.FromAnchor(
        component_id="thien_giai",
        anchor=DiaChi.THAN,
        transform=pp.move_by_birth_month(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="dia_giai",
        anchor=DiaChi.MUI,
        transform=pp.move_by_birth_month(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="thien_hinh",
        anchor=DiaChi.DAU,
        transform=pp.move_by_birth_month(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="thien_dieu",
        anchor=DiaChi.SUU,
        transform=pp.move_by_birth_month(direction=CircleDirection.CW),
    ),
    pp.SamePosition(
        component_id="thien_y",
        reference_id="thien_dieu",
    ),

    # An theo ngay
    pp.RelativePosition(
        component_id="tam_thai",
        reference_id="ta_phu",
        transform=pp.move_with(
            lambda context: context.prior.date - 1,
            direction=CircleDirection.CW,
        ),
    ),
    pp.RelativePosition(
        component_id="bat_toa",
        reference_id="huu_bat",
        transform=pp.move_with(
            lambda context: context.prior.date - 1,
            direction=CircleDirection.CCW,
        ),
    ),
    pp.RelativePosition(
        component_id="an_quang",
        reference_id="van_xuong",
        transform=pp.move_with(
            lambda context: context.prior.date - 2,
            direction=CircleDirection.CW,
        ),
    ),
    pp.RelativePosition(
        component_id="thien_quy",
        reference_id="van_khuc",
        transform=pp.move_with(
            lambda context: context.prior.date - 2,
            direction=CircleDirection.CCW,
        ),
    ),

    # An theo gio
    pp.FromAnchor(
        component_id="dia_khong",
        anchor=DiaChi.HOI,
        transform=pp.move_by_birth_hour(direction=CircleDirection.CCW),
    ),
    pp.FromAnchor(
        component_id="dia_kiep",
        anchor=DiaChi.HOI,
        transform=pp.move_by_birth_hour(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="van_xuong",
        anchor=DiaChi.TUAT,
        transform=pp.move_by_birth_hour(direction=CircleDirection.CCW),
    ),
    pp.FromAnchor(
        component_id="van_khuc",
        anchor=DiaChi.THIN,
        transform=pp.move_by_birth_hour(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="thai_phu",
        anchor=DiaChi.NGO,
        transform=pp.move_by_birth_hour(direction=CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="phong_cao",
        anchor=DiaChi.DAN,
        transform=pp.move_by_birth_hour(direction=CircleDirection.CW),
    ),

    # An theo cung
    pp.RelativePosition(
        component_id="thien_tai",
        reference_id="menh",
        transform=pp.move_by_birth_dia_chi(direction=CircleDirection.CW),
    ),
    pp.RelativePosition(
        component_id="thien_tho",
        reference_id="than",
        transform=pp.move_by_birth_dia_chi(direction=CircleDirection.CW),
    ),
    pp.SamePosition(
        component_id="thien_su",
        reference_id="tat_ach",
    ),
    pp.SamePosition(
        component_id="thien_thuong",
        reference_id="no_boc",
    ),

    # Thien La, Dia Vong
    pp.DefinitivePosition(
        component_id="thien_la",
        position=DiaChi.THIN,
    ),
    pp.DefinitivePosition(
        component_id="dia_vong",
        position=DiaChi.TUAT,
    ),
]
