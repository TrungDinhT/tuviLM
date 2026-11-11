from __future__ import annotations

from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import (
    ChinhPhuTinh,
    TuHoa,
    TuanTriet,
    VongTrangSinh,
)
from src.refactored.model.elementary import DiaChi
from src.refactored.view.models import CungView


def _get_sao_status(sao_id: str, position: DiaChi) -> str:
    return MAP_SAO_STATUS.get(sao_id, {}).get(position, "")


def format_cung_detail(cung: CungView) -> str:
    """Format a cung view into compact, agent-readable Vietnamese text."""
    info = (
        f"Cung: {cung.role.role.value} "
        f"Vị Trí : {cung.dia_chi_entity.value}) - "
        f"Thiên can : {cung.thien_can_entity.value}\n"
    )

    if cung.is_cung_than:
        info += "Đây là Cung Thân\n"

    chinh_tinh: list[str] = []
    phu_tinh: list[str] = []
    is_tuan = False
    is_triet = False
    tu_hoa: list[str] = []
    trang_sinh: str | None = None

    for component_view in cung.components:
        # Use only the natal layer for now. Period layers can be added when the
        # agent starts handling Đại Vận/Tiểu Vận style questions.
        if component_view.layer_kind != "natal":
            continue

        component = component_view.component
        if isinstance(component, ChinhPhuTinh):
            status = _get_sao_status(component.id, cung.dia_chi_entity.value)
            sao_str = f"{component.name} ({status})" if status else component.name
            if component.is_chinh_tinh:
                chinh_tinh.append(sao_str)
            else:
                phu_tinh.append(sao_str)
        elif isinstance(component, TuHoa):
            tu_hoa.append(component.name)
        elif isinstance(component, VongTrangSinh):
            trang_sinh = component.name
        elif isinstance(component, TuanTriet):
            if component.name == "Triệt":
                is_triet = True
            if component.name == "Tuần":
                is_tuan = True

    if chinh_tinh:
        info += "\nChính Tinh : " + "\n - ".join(chinh_tinh)
    else:
        info += "Vô Chính Diệu"

    if phu_tinh:
        info += "\nPhụ Tinh : " + "\n - ".join(phu_tinh)
    if tu_hoa:
        info += "\nTứ Hóa : " + "\n - ".join(tu_hoa)
    if trang_sinh:
        info += f"\nTràng Sinh : {trang_sinh}"
    if is_tuan:
        info += "\n Có Tuần"
    if is_triet:
        info += "\n Có Triệt"

    return info
