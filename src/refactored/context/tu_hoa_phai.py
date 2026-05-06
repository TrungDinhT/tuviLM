from dataclasses import dataclass

from src.refactored.component.elementary import DiaChi, ThienCan
from src.refactored.placement.layer import LayerId, TuHoaPhaiLayerId


@dataclass(frozen=True)
class TuHoaPhaiContext:
    source_dia_chi: DiaChi
    thien_can: ThienCan

    @property
    def layer_id(self) -> LayerId:
        return TuHoaPhaiLayerId(source_dia_chi=self.source_dia_chi)
