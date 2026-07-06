from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import (
    ChinhPhuTinh,
    TuHoa,
    TuanTriet,
    VongTrangSinh,
)
from src.refactored.model.elementary import DiaChi
from src.refactored.view.models import CungView, LaSoView

from .schemas import (
    CungPayload,
    StarPayload,
)

# TODO : This logic brigde the gaps between the view and the payload,
# but it is not ideal. We should consider refactoring the view to be
# more aligned with the payload, or introducing a separate layer of
# abstraction to handle this conversion more cleanly.


def _get_sao_status(sao_id: str, position: DiaChi) -> str:
    return MAP_SAO_STATUS.get(sao_id, {}).get(position, "")


def to_cung_payload_map(la_so: LaSoView) -> dict[str, CungPayload]:
    return {
        cung_view.dia_chi_entity.name: to_cung_payload(cung_view)
        for cung_view in la_so.cungs
    }


def to_cung_payload(cung_view: CungView) -> CungPayload:
    chinh_tinh: list[str] = []
    phu_tinh: list[StarPayload] = []
    is_tuan: bool = False
    is_triet: bool = False
    tu_hoa: list[StarPayload] = []
    trang_sinh: str

    for component_view in cung_view.components:
        if component_view.layer_kind != "natal":
            continue
        component = component_view.component
        if isinstance(component, ChinhPhuTinh):
            status = _get_sao_status(component.id, cung_view.dia_chi_entity.value)
            sao_str = f"{component.name} ({status})" if status else component.name
            if component.is_chinh_tinh:
                chinh_tinh.append(sao_str)
            else:
                phu_tinh.append(to_sao_payload(component, cung_view))
        elif isinstance(component, TuHoa):
            tu_hoa.append(
                StarPayload(
                    name=component.name,
                    display=component.name,
                    element=component.ngu_hanh.value,
                    sao_type=[st.value for st in component.sao_type],
                )
            )
        elif isinstance(component, VongTrangSinh):
            trang_sinh = component.name
        elif isinstance(component, TuanTriet):
            if component.name == "Triệt":
                is_triet = True
            if component.name == "Tuần":
                is_tuan = True

    return CungPayload(
        position=cung_view.dia_chi_entity.name,
        role=cung_view.role.name,
        chinh_tinh=chinh_tinh,
        phu_tinh=phu_tinh,
        tuhoa=tu_hoa,
        trang_sinh=trang_sinh if trang_sinh else None,
        is_tuan=is_tuan,
        is_triet=is_triet,
        is_cung_than=cung_view.is_cung_than,
        saoLuu=[
            to_sao_payload(comp.component, cung_view)
            for comp in cung_view.components
            if isinstance(comp.component, (ChinhPhuTinh, TuHoa))
            and comp.layer_kind == "tieu_han"
        ],
    )


def to_sao_payload(component: ChinhPhuTinh | TuHoa, cung_view: CungView) -> StarPayload:
    status = _get_sao_status(component.id, cung_view.dia_chi_entity.value)
    sao_str = f"{component.name} ({status})" if status else component.name
    return StarPayload(
        name=component.name,
        display=sao_str,
        element=component.ngu_hanh.value,
        sao_type=[st.value for st in component.sao_type],
    )
