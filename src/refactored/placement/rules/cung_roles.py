import src.refactored.placement.primitives as pp
from src.refactored.model.elementary import CircleDirection

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
