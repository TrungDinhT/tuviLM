import src.refactored.builder.rule_primitives as rp
from src.refactored.component.cung import Cung
from src.refactored.component.sao import Sao
from src.refactored.component.elementary import NguHanh

CUNG_RULES = [
    rp.Vong(
        principal=Cung.MENH,
        principal_position_fn=lambda context: context.menh_position,
        others=[
            Cung.PHU,
            Cung.PHUC,
            Cung.DIEN,
            Cung.QUAN,
            Cung.NO,
            Cung.DI,
            Cung.TAT,
            Cung.TAI,
            Cung.TU,
            Cung.PHOI,
            Cung.HUYNH,
        ],
    ),
    rp.RelativePosition(
        component=Cung.THAN,
        reference=Cung.MENH,
        transform=rp.move_by_la_so_attr("hour", multiplier=2),
    ),
]

SAO_RULES = [
    # An theo cung
    rp.RelativePosition(
        component=Sao(name="Thiên Tài", ngu_hanh=NguHanh.THO),
        reference=Cung.MENH,
        transform=rp.move_by_la_so_attr("dia_chi"),
    ),
    rp.RelativePosition(
        component=Sao(name="Thiên Thọ", ngu_hanh=NguHanh.THO),
        reference=Cung.THAN,
        transform=rp.move_by_la_so_attr("dia_chi"),
    ),
    rp.SamePosition(
        component=Sao(name="Thiên Sứ", ngu_hanh=NguHanh.THUY),
        reference=Cung.TAT,
    ),
    rp.SamePosition(
        component=Sao(name="Thiên Thuơng", ngu_hanh=NguHanh.THO),
        reference=Cung.NO,
    ),
]
