import src.refactored.builder.placement_primitives as pp

_move_by_year_dia_chi = pp.move_by_van_direction(
    lambda context: context.prior.get_dia_chi().index
)


CUNG_RULES = [
    pp.Vong(
        principal_name="Mệnh",
        principal_position_fn=lambda context: context.menh_position,
        others=[
            "Phụ Mẫu",
            "Phúc Đức",
            "Điền Trạch",
            "Quan Lộc",
            "Nô Bộc",
            "Thiên Di",
            "Tật Ách",
            "Tài Bạch",
            "Tử Tức",
            "Phu Thê",
            "Huynh Đệ",
        ],
    ),
    pp.RelativePosition(
        component_name="Thân",
        reference_name="Mệnh",
        transform=pp.move_by_la_so_attr("hour", multiplier=2),
    ),
]

SAO_RULES = [
    # An theo cung
    pp.RelativePosition(
        component_name="Thiên Tài",
        reference_name="Mệnh",
        transform=_move_by_year_dia_chi,
    ),
    pp.RelativePosition(
        component_name="Thiên Thọ",
        reference_name="Thân",
        transform=_move_by_year_dia_chi,
    ),
    pp.SamePosition(
        component_name="Thiên Sứ",
        reference_name="Tật Ách",
    ),
    pp.SamePosition(
        component_name="Thiên Thuơng",
        reference_name="Nô Bộc",
    ),
    # Chinh tinh
]
