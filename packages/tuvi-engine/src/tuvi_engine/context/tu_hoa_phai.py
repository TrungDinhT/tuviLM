from dataclasses import dataclass

from tuvi_engine.model.elementary import DiaChi, ThienCan


@dataclass(frozen=True)
class TuHoaPhaiContext:
    source_dia_chi: DiaChi
    thien_can: ThienCan
