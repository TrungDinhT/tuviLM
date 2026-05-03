import src.refactored.placement.primitives as pp
from src.refactored.component.elementary import CircleDirection, DiaChi, ThienCan


# ---------------------------------------------------------------------------
# Cung role placement rules
# ---------------------------------------------------------------------------

ROLE_RULES = [
    pp.Circle(
        principal_id="menh",
        principal_position_fn=pp.menh_position_fn,
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
        component_id="cung_than",
        reference_id="menh",
        transform=pp.move_by_birth_hour(
            direction=CircleDirection.CW,
            step_multiplier=2,
        ),
    ),
]


# ---------------------------------------------------------------------------
# Sao placement rules
# ---------------------------------------------------------------------------

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
    # Vong Bac Si
    pp.Circle(
        principal_id="bac_si",
        principal_position_fn=pp.loc_ton_position_fn,
        others=[
            "luc_si",
            "thanh_long",
            "tieu_hao",
            "tuong_quan",
            "tau_thu",
            "phi_liem",
            "hy_than",
            "benh_phu",
            "dai_hao",
            "phuc_binh",
            "quan_phur",
        ],
        direction=pp.Circle.Direction.VAN,
    ),
    # Group Loc Ton
    pp.OffsetGroup(
        anchor_id="loc_ton",
        anchor_position_fn=pp.loc_ton_position_fn,
        offsets={
            "kinh_duong": 1,
            "da_la": -1,
            "ln_van_tinh": 3,
            "duong_phu": 5,
            "quoc_an": 8,
        },
    ),

    # Vong Thai Tue
    pp.Circle(
        principal_id="thai_tue",
        principal_position_fn=pp.thai_tue_position_fn,
        others=[
            pp.SamePosition("thieu_duong", "thien_khong"),
            "tang_mon",
            "thieu_am",
            pp.SamePosition("quan_phuf", "long_tri"),
            pp.SamePosition("tu_phu", "nguyet_duc"),
            pp.SamePosition("tue_pha", "thien_hu"),
            "long_duc",
            "bach_ho",
            pp.SamePosition("sao_phuc_duc", "thien_duc"),
            "dieu_khach",
            "truc_phu",
        ],
    ),
    # Vong Trang Sinh
    pp.Circle(
        principal_id="trang_sinh",
        principal_position_fn=pp.trang_sinh_position_fn,
        others=[
            "moc_duc",
            "quan_doi",
            "lam_quan",
            "de_vuong",
            "suy",
            "benh",
            "tu",
            "mo",
            "tuyet",
            "thai",
            "duong",
        ],
        direction=pp.Circle.Direction.VAN,
    ),

    # An theo thien can
    pp.AbsolutePosition(
        component_id="thien_khoi",
        position_fn=pp.position_by_thien_can(
            {
                ThienCan.GIAP: DiaChi.SUU,
                ThienCan.AT: DiaChi.TY,
                ThienCan.BINH: DiaChi.HOI,
                ThienCan.DINH: DiaChi.HOI,
                ThienCan.MAU: DiaChi.SUU,
                ThienCan.KY: DiaChi.TY,
                ThienCan.CANH: DiaChi.NGO,
                ThienCan.TAN: DiaChi.NGO,
                ThienCan.NHAM: DiaChi.MEO,
                ThienCan.QUY: DiaChi.MEO,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="thien_viet",
        position_fn=pp.position_by_thien_can(
            {
                ThienCan.GIAP: DiaChi.MUI,
                ThienCan.AT: DiaChi.THAN,
                ThienCan.BINH: DiaChi.DAU,
                ThienCan.DINH: DiaChi.DAU,
                ThienCan.MAU: DiaChi.MUI,
                ThienCan.KY: DiaChi.THAN,
                ThienCan.CANH: DiaChi.DAN,
                ThienCan.TAN: DiaChi.DAN,
                ThienCan.NHAM: DiaChi.TI,
                ThienCan.QUY: DiaChi.TI,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="luu_ha",
        position_fn=pp.position_by_thien_can(
            {
                ThienCan.GIAP: DiaChi.DAU,
                ThienCan.AT: DiaChi.TUAT,
                ThienCan.BINH: DiaChi.MUI,
                ThienCan.DINH: DiaChi.THIN,
                ThienCan.MAU: DiaChi.TI,
                ThienCan.KY: DiaChi.NGO,
                ThienCan.CANH: DiaChi.THAN,
                ThienCan.TAN: DiaChi.THIN,
                ThienCan.NHAM: DiaChi.HOI,
                ThienCan.QUY: DiaChi.DAN,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="thien_tru",
        position_fn=pp.position_by_thien_can(
            {
                ThienCan.GIAP: DiaChi.TI,
                ThienCan.AT: DiaChi.NGO,
                ThienCan.BINH: DiaChi.TY,
                ThienCan.DINH: DiaChi.TI,
                ThienCan.MAU: DiaChi.NGO,
                ThienCan.KY: DiaChi.THAN,
                ThienCan.CANH: DiaChi.DAN,
                ThienCan.TAN: DiaChi.NGO,
                ThienCan.NHAM: DiaChi.DAU,
                ThienCan.QUY: DiaChi.TUAT,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="thien_quan",
        position_fn=pp.position_by_thien_can(
            {
                ThienCan.GIAP: DiaChi.MUI,
                ThienCan.AT: DiaChi.MUI,
                ThienCan.BINH: DiaChi.THIN,
                ThienCan.DINH: DiaChi.DAN,
                ThienCan.MAU: DiaChi.MEO,
                ThienCan.KY: DiaChi.DAU,
                ThienCan.CANH: DiaChi.HOI,
                ThienCan.TAN: DiaChi.DAU,
                ThienCan.NHAM: DiaChi.TUAT,
                ThienCan.QUY: DiaChi.NGO,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="thien_phuc",
        position_fn=pp.position_by_thien_can(
            {
                ThienCan.GIAP: DiaChi.DAU,
                ThienCan.AT: DiaChi.DAU,
                ThienCan.BINH: DiaChi.THAN,
                ThienCan.DINH: DiaChi.HOI,
                ThienCan.MAU: DiaChi.MEO,
                ThienCan.KY: DiaChi.DAN,
                ThienCan.CANH: DiaChi.NGO,
                ThienCan.TAN: DiaChi.TI,
                ThienCan.NHAM: DiaChi.NGO,
                ThienCan.QUY: DiaChi.TI,
            }
        ),
    ),

    # An theo dia chi
    pp.AbsolutePosition(
        component_id="co_than",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.DAN, DiaChi.MEO, DiaChi.THIN): DiaChi.TI,
                (DiaChi.TI, DiaChi.NGO, DiaChi.MUI): DiaChi.THAN,
                (DiaChi.THAN, DiaChi.DAU, DiaChi.TUAT): DiaChi.HOI,
                (DiaChi.HOI, DiaChi.TY, DiaChi.SUU): DiaChi.MUI,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="qua_tu",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.DAN, DiaChi.MEO, DiaChi.THIN): DiaChi.SUU,
                (DiaChi.TI, DiaChi.NGO, DiaChi.MUI): DiaChi.THIN,
                (DiaChi.THAN, DiaChi.DAU, DiaChi.TUAT): DiaChi.DAN,
                (DiaChi.HOI, DiaChi.TY, DiaChi.SUU): DiaChi.TUAT,
            }
        ),
    ),
    pp.FromAnchor(
        component_id="thien_hi",
        anchor=DiaChi.DAU,
        transform=pp.move_by_dia_chi(CircleDirection.CCW),
    ),
    pp.XungChieu(
        component_id="hong_loan",
        reference_id="thien_hi",
    ),
    pp.FromAnchor(
        component_id="giai_than",
        anchor=DiaChi.TUAT,
        transform=pp.move_by_dia_chi(CircleDirection.CCW),
    ),
    pp.SamePosition(
        component_id="phuong_cac",
        reference_id="giai_than",
    ),
    pp.FromAnchor(
        component_id="thien_khoc",
        anchor=DiaChi.NGO,
        transform=pp.move_by_dia_chi(CircleDirection.CCW),
    ),
    pp.AbsolutePosition(
        component_id="thien_ma",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.THAN, DiaChi.TY, DiaChi.THIN): DiaChi.DAN,
                (DiaChi.TI, DiaChi.DAU, DiaChi.SUU): DiaChi.HOI,
                (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT): DiaChi.THAN,
                (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI): DiaChi.TI,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="hoa_cai",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.THAN, DiaChi.TY, DiaChi.THIN): DiaChi.THIN,
                (DiaChi.TI, DiaChi.DAU, DiaChi.SUU): DiaChi.SUU,
                (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT): DiaChi.TUAT,
                (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI): DiaChi.MUI,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="dao_hoa",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.THAN, DiaChi.TY, DiaChi.THIN): DiaChi.DAU,
                (DiaChi.TI, DiaChi.DAU, DiaChi.SUU): DiaChi.NGO,
                (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT): DiaChi.MEO,
                (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI): DiaChi.TY,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="kiep_sat",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.THAN, DiaChi.TY, DiaChi.THIN): DiaChi.TI,
                (DiaChi.TI, DiaChi.DAU, DiaChi.SUU): DiaChi.DAN,
                (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT): DiaChi.HOI,
                (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI): DiaChi.THAN,
            }
        ),
    ),
    pp.AbsolutePosition(
        component_id="pha_toai",
        position_fn=pp.position_by_dia_chi_groups(
            {
                (DiaChi.TY, DiaChi.NGO, DiaChi.MEO, DiaChi.DAU): DiaChi.TI,
                (DiaChi.THIN, DiaChi.TUAT, DiaChi.SUU, DiaChi.MUI): DiaChi.SUU,
                (DiaChi.DAN, DiaChi.THAN, DiaChi.TI, DiaChi.HOI): DiaChi.DAU,
            }
        ),
    ),

    # An theo thang
    pp.FromAnchor(
        component_id="ta_phu",
        anchor=DiaChi.THIN,
        transform=pp.move_by_birth_month(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="huu_bat",
        anchor=DiaChi.TUAT,
        transform=pp.move_by_birth_month(CircleDirection.CCW),
    ),
    pp.FromAnchor(
        component_id="thien_giai",
        anchor=DiaChi.THAN,
        transform=pp.move_by_birth_month(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="dia_giai",
        anchor=DiaChi.MUI,
        transform=pp.move_by_birth_month(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="thien_hinh",
        anchor=DiaChi.DAU,
        transform=pp.move_by_birth_month(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="thien_dieu",
        anchor=DiaChi.SUU,
        transform=pp.move_by_birth_month(CircleDirection.CW),
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
        transform=pp.move_by_birth_hour(CircleDirection.CCW),
    ),
    pp.FromAnchor(
        component_id="dia_kiep",
        anchor=DiaChi.HOI,
        transform=pp.move_by_birth_hour(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="van_xuong",
        anchor=DiaChi.TUAT,
        transform=pp.move_by_birth_hour(CircleDirection.CCW),
    ),
    pp.FromAnchor(
        component_id="van_khuc",
        anchor=DiaChi.THIN,
        transform=pp.move_by_birth_hour(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="thai_phu",
        anchor=DiaChi.NGO,
        transform=pp.move_by_birth_hour(CircleDirection.CW),
    ),
    pp.FromAnchor(
        component_id="phong_cao",
        anchor=DiaChi.DAN,
        transform=pp.move_by_birth_hour(CircleDirection.CW),
    ),

    # An Dau Quan
    pp.AbsolutePosition(
        component_id="dau_quan",
        position_fn=pp.dau_quan_position_fn,
    ),

    # An Hoa Tinh, Linh Tinh
    pp.FromAnchor(
        component_id="hoa_tinh",
        anchor=pp.position_by_dia_chi_groups(
            {
                (DiaChi.THAN, DiaChi.TY, DiaChi.THIN): DiaChi.DAN,
                (DiaChi.TI, DiaChi.DAU, DiaChi.SUU): DiaChi.MEO,
                (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT): DiaChi.SUU,
                (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI): DiaChi.DAU,
            }
        ),
        transform=pp.move_by_van_direction(
            lambda context: context.prior.hour.index,
            step_multiplier=1,
        ),
    ),
    pp.FromAnchor(
        component_id="linh_tinh",
        anchor=pp.position_by_dia_chi_groups(
            {
                (DiaChi.THAN, DiaChi.TY, DiaChi.THIN): DiaChi.TUAT,
                (DiaChi.TI, DiaChi.DAU, DiaChi.SUU): DiaChi.TUAT,
                (DiaChi.DAN, DiaChi.NGO, DiaChi.TUAT): DiaChi.MEO,
                (DiaChi.HOI, DiaChi.MEO, DiaChi.MUI): DiaChi.TUAT,
            }
        ),
        transform=pp.move_by_van_direction(
            lambda context: context.prior.hour.index,
            step_multiplier=-1,
        ),
    ),

    # An theo cung
    pp.RelativePosition(
        component_id="thien_tai",
        reference_id="menh",
        transform=pp.move_by_dia_chi(CircleDirection.CW),
    ),
    pp.RelativePosition(
        component_id="thien_tho",
        reference_id="cung_than",
        transform=pp.move_by_dia_chi(CircleDirection.CW),
    ),
    pp.SamePosition(
        component_id="thien_su",
        reference_id="tat_ach",
    ),
    pp.SamePosition(
        component_id="thien_thuong",
        reference_id="no_boc",
    ),

    # Tuan, Triet
    pp.TuanTrietPosition(
        pair_ids=("triet_1", "triet_2"),
        pair_position_fn=pp.triet_positions_fn,
    ),
    pp.TuanTrietPosition(
        pair_ids=("tuan_1", "tuan_2"),
        pair_position_fn=pp.tuan_positions_fn,
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

# Tứ Hóa: same palace as mapped sao per year Thiên Can (legacy MAP_TUHOA).
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


LIST_SAO_LUU = [
    "thai_tue",
    "bach_ho",
    "tang_mon",
    "thien_ma",
    "loc_ton",
    "kinh_duong",
    "da_la",
    "thien_khoc",
    "thien_hu",
]
