from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import Agent, ModelRetry

from src.agent.book_index import BookIndex
from src.agent.constant import MAP_STR_TO_DIACHI, MAP_STR_TO_ROLE
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import (
    ChinhPhuTinh,
    TuHoa,
    TuanTriet,
    VongTrangSinh,
)
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.view.builder import build_cung_view
from src.refactored.view.models import CungView


DEFAULT_BOOK_ROOT = (
    Path(__file__).resolve().parents[2] / "data" / "tuvitanbien_chunking"
)


@dataclass(slots=True)
class TuviAgentDeps:
    agent: Agent | None = None
    la_so: LaSo | None = None
    book: BookIndex | None = None
    book_root: Path = DEFAULT_BOOK_ROOT

    def require_agent(self) -> Agent:
        if self.agent is None:
            raise ModelRetry("Agent chưa được gán vào deps.")
        return self.agent

    def require_la_so(self) -> LaSo:
        if self.la_so is None:
            raise ModelRetry("LaSo chưa được gán vào deps.")
        return self.la_so

    def require_book(self) -> BookIndex:
        if self.book is None:
            try:
                self.book = BookIndex(self.book_root)
            except FileNotFoundError as exc:
                raise ModelRetry(str(exc)) from exc
        return self.book

    # TODO : all this logic is temporary and should be moved to a more appropriate place,
    def _get_sao_status(self, sao_id: str, position: DiaChi) -> str:
        return MAP_SAO_STATUS.get(sao_id, {}).get(position, "")

    def _cung_to_detail(self, cung: CungView) -> str:
        info = f"Cung: {cung.role.role.value} Vị Trí : {cung.dia_chi_entity.value}) - Thiên can : {cung.thien_can_entity.value}\n"

        if cung.is_cung_than:
            info += "Đây là Cung Thân\n"

        chinh_tinh: list[str] = []
        phu_tinh: list[str] = []
        is_tuan: bool = False
        is_triet: bool = False
        tu_hoa: list[str] = []
        trang_sinh: str

        for component_view in cung.components:
            # TODO: Use only layer natal for now but we should consider other layers in the future when we have more complex components such as DaVan, HuuBat, etc.
            if component_view.layer_kind != "natal":
                continue
            component = component_view.component
            if isinstance(component, ChinhPhuTinh):
                status = self._get_sao_status(component.id, cung.dia_chi_entity.value)
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

        info += (
            "\nChính Tinh : " + "\n - ".join(chinh_tinh)
            if chinh_tinh
            else "Vô Chính Diệu"
        )

        info += "\nPhụ Tinh : " + "\n - ".join(phu_tinh) if phu_tinh else ""
        info += "\nTứ Hỏa : " + "\n - ".join(tu_hoa) if tu_hoa else ""
        info += f"\nTràng Sinh : {trang_sinh}" if trang_sinh else ""
        info += "\n Có Tuần" if is_tuan else ""
        info += "\n Có Triệt" if is_triet else ""

        return info

    def get_cung_by_position(self, position: str) -> str:

        try:
            la_so = self.require_la_so()
            cung = la_so.cung_at(MAP_STR_TO_DIACHI.get(position))

            return self._cung_to_detail(build_cung_view(la_so=la_so, cung=cung))

        except:  # noqa: E722
            raise ModelRetry(
                f"Không tìm thấy cung tại vị trí '{position}'. Các vị trí hợp lệ là: {', '.join(MAP_STR_TO_DIACHI.keys())}."
            )

    def get_cung_by_role(self, role: str) -> str:
        la_so = self.require_la_so()
        role_enum = MAP_STR_TO_ROLE.get(role)
        if role_enum is None:
            raise ModelRetry(
                f"Vai trò '{role}' không hợp lệ. Các vai trò hợp lệ là: {', '.join(MAP_STR_TO_ROLE.keys())}."
            )
        for position, cung_id in la_so.tinh_ban.cung_ids.items():
            if cung_id.natal_role == role_enum:
                cung = la_so.cung_at(position)
                return self._cung_to_detail(build_cung_view(la_so=la_so, cung=cung))
