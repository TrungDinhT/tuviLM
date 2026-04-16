import src.refactored.placement.primitives as pp
from src.refactored.component.elementary import CircleDirection, DiaChi, ThienCan


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
    # Vong Bac Si
    pp.Vong(
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
        direction=pp.Vong.Direction.VAN,
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
    pp.Vong(
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
        reference_id="than",
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
