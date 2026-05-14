"""Cung structural helpers and lightweight query models."""

from dataclasses import dataclass

from src.refactored.components.definitions.cung_role import CungRole, Role
from src.refactored.model.elementary import DiaChi, ThienCan
from src.refactored.model.layer import LayerId
from src.refactored.placement.registry import ComponentId


# Ngũ Hổ Độn anchor table: maps the natal year Thiên Can to the Thiên Can
# assigned to the Dần Cung. Other Cung Thiên Can values advance from Dần.
NGU_HO_DON_THIEN_CAN: dict[ThienCan, ThienCan] = {
    ThienCan.GIAP: ThienCan.BINH,
    ThienCan.KY: ThienCan.BINH,
    ThienCan.AT: ThienCan.MAU,
    ThienCan.CANH: ThienCan.MAU,
    ThienCan.BINH: ThienCan.CANH,
    ThienCan.TAN: ThienCan.CANH,
    ThienCan.DINH: ThienCan.NHAM,
    ThienCan.NHAM: ThienCan.NHAM,
    ThienCan.MAU: ThienCan.GIAP,
    ThienCan.QUY: ThienCan.GIAP,
}


def derive_cung_thien_can(
    year_thien_can: ThienCan,
    cung_dia_chi: DiaChi,
) -> ThienCan:
    """Derive the Thiên Can of a Cung from natal year Thiên Can."""
    dan_thien_can = NGU_HO_DON_THIEN_CAN[year_thien_can]
    return dan_thien_can + (cung_dia_chi - DiaChi.DAN)


@dataclass(frozen=True)
class CungId:
    dia_chi: DiaChi
    thien_can: ThienCan
    natal_role: Role
    is_cung_than: bool


@dataclass(frozen=True)
class LayeredComponent:
    layer_id: LayerId
    component_id: ComponentId


@dataclass(frozen=True)
class Cung:
    dia_chi: DiaChi
    thien_can: ThienCan
    natal_role: Role
    is_cung_than: bool
    components: tuple[LayeredComponent, ...]

    def components_in_layer(self, layer_id: LayerId) -> tuple[ComponentId, ...]:
        return tuple(
            component.component_id
            for component in self.components
            if component.layer_id == layer_id
        )

    def has(
        self,
        component_id: ComponentId,
        layer_id: LayerId | None = None,
    ) -> bool:
        return any(
            component.component_id == component_id
            and (layer_id is None or component.layer_id == layer_id)
            for component in self.components
        )
