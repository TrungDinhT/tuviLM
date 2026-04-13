import src.refactored.placement.primitives as pp

_move_by_year_dia_chi = pp.move_by_van_direction(
    lambda context: context.prior.get_dia_chi().index
)


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
        transform=pp.move_by_la_so_attr("hour", step_multiplier=2),
    ),
]

SAO_RULES = [
    # An theo cung
    pp.RelativePosition(
        component_id="thien_tai",
        reference_id="menh",
        transform=_move_by_year_dia_chi,
    ),
    pp.RelativePosition(
        component_id="thien_tho",
        reference_id="than",
        transform=_move_by_year_dia_chi,
    ),
    pp.SamePosition(
        component_id="thien_su",
        reference_id="tat_ach",
    ),
    pp.SamePosition(
        component_id="thien_thuong",
        reference_id="no_boc",
    ),
    # Chinh tinh
]
