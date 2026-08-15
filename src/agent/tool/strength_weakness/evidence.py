"""Deterministic, factual evidence builders for strength/weakness assessment."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal

from pydantic_ai import ModelRetry, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.strength_weakness.models import (
    CungBoSungEvidence,
    CungStructureEvidence,
    PhuTinhTuanTrietEvidence,
    PhuTinhTuanTrietKind,
    SaoEvidence,
    TinhHeEvidence,
    TinhHeScope,
    TuHoaEvidence,
)
from src.refactored.components.definitions.cung_role import Role
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import ChinhPhuTinh, TuanTriet
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import CircleDirection, DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.placement.rules.loader import load_tu_hoa_target_mapping
from src.refactored.placement.transforms import get_tam_hop, get_xung_chieu

_logger = logging.getLogger(__name__)

type CungBoSung = Literal["phuc_duc", "no_boc", "tat_ach"]
_CUNG_BO_SUNG_ROLES = frozenset((Role.PHUC_DUC, Role.NO_BOC, Role.TAT_ACH))


@dataclass(frozen=True, slots=True)
class TinhHeDefinition:
    id: str
    ten: str
    chinh_tinh_ids: tuple[str, ...]


# This is deliberately a small workflow-specific catalog. It does not depend on
# or alter the repository's classical cách-cục matcher.
TINH_HE_DEFINITIONS: tuple[TinhHeDefinition, ...] = (
    TinhHeDefinition(
        "tu_phu_vu_tuong",
        "Tử Phủ Vũ Tướng",
        ("tu_vi", "thien_phu", "vu_khuc", "thien_tuong"),
    ),
    TinhHeDefinition(
        "sat_pha_tham",
        "Sát Phá Tham",
        ("that_sat", "pha_quan", "tham_lang"),
    ),
    TinhHeDefinition(
        "sat_pha_liem_tham",
        "Sát Phá Liêm Tham",
        ("that_sat", "pha_quan", "liem_trinh", "tham_lang"),
    ),
    TinhHeDefinition(
        "co_nguyet_dong_luong",
        "Cơ Nguyệt Đồng Lương",
        ("thien_co", "thai_am", "thien_dong", "thien_luong"),
    ),
    TinhHeDefinition("cu_nhat", "Cự Nhật", ("cu_mon", "thai_duong")),
    TinhHeDefinition("co_cu", "Cơ Cự", ("thien_co", "cu_mon")),
    TinhHeDefinition("co_luong", "Cơ Lương", ("thien_co", "thien_luong")),
    TinhHeDefinition("tu_phu", "Tử Phủ", ("tu_vi", "thien_phu")),
    TinhHeDefinition("phu_tuong", "Phủ Tướng", ("thien_phu", "thien_tuong")),
    TinhHeDefinition("vu_tuong", "Vũ Tướng", ("vu_khuc", "thien_tuong")),
    TinhHeDefinition("nhat_nguyet", "Nhật Nguyệt", ("thai_duong", "thai_am")),
)

_TU_HOA_IDS = ("hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky")


def _dia_chi_name(la_so: LaSo, dia_chi: DiaChi) -> str:
    return la_so.catalog.get_dia_chi(dia_chi).name


def _cung_name(la_so: LaSo, role: Role) -> str:
    return la_so.component(role.value).name


def _required_dia_chi(la_so: LaSo, component_id: str) -> DiaChi:
    dia_chi = la_so.position_of(component_id, NATAL_LAYER_ID)
    if dia_chi is None:
        raise ModelRetry(f"Không tìm thấy vị trí natal của '{component_id}'.")
    return dia_chi


def _trang_thai_sao(sao_id: str, dia_chi: DiaChi) -> str | None:
    trang_thai = MAP_SAO_STATUS.get(sao_id, {}).get(dia_chi)
    return trang_thai.value if trang_thai is not None else None


def _sao_evidence(
    la_so: LaSo,
    sao_id: str,
    *,
    dia_chi: DiaChi | None = None,
) -> SaoEvidence:
    resolved_dia_chi = dia_chi or _required_dia_chi(la_so, sao_id)
    component = la_so.component(sao_id)
    cung = la_so.cung_at(resolved_dia_chi)
    return SaoEvidence(
        sao_id=sao_id,
        ten=component.name,
        dia_chi=resolved_dia_chi,
        dia_chi_name=_dia_chi_name(la_so, resolved_dia_chi),
        cung=cung.natal_role,
        cung_name=_cung_name(la_so, cung.natal_role),
        trang_thai=_trang_thai_sao(sao_id, resolved_dia_chi),
    )


def build_cung_structure(la_so: LaSo, anchor: Role) -> CungStructureEvidence:
    """Dựng dữ kiện chính tinh trực tiếp cho một cung gốc."""
    dia_chi = _required_dia_chi(la_so, anchor.value)
    cung = la_so.cung_at(dia_chi)
    chinh_tinh: list[SaoEvidence] = []
    for component_id in cung.components_in_layer(NATAL_LAYER_ID):
        component = la_so.component(component_id)
        if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
            chinh_tinh.append(_sao_evidence(la_so, component_id, dia_chi=dia_chi))
    return CungStructureEvidence(
        cung_goc=anchor,
        dia_chi=dia_chi,
        dia_chi_name=_dia_chi_name(la_so, dia_chi),
        cung=cung.natal_role,
        cung_name=_cung_name(la_so, cung.natal_role),
        la_cung_than=cung.is_cung_than,
        chinh_tinh=chinh_tinh,
    )


def build_menh_than_evidence(la_so: LaSo) -> list[CungStructureEvidence]:
    """Dựng Mệnh và Thân riêng, kể cả khi Thân Mệnh đồng cung."""
    return [
        build_cung_structure(la_so, Role.MENH),
        build_cung_structure(la_so, Role.CUNG_THAN),
    ]


def _pham_vi_dia_chi(
    anchor: DiaChi,
) -> tuple[tuple[TinhHeScope, frozenset[DiaChi]], ...]:
    tam_phuong = frozenset(
        (
            anchor,
            get_tam_hop(anchor, CircleDirection.CW),
            get_tam_hop(anchor, CircleDirection.CCW),
        )
    )
    return (
        (TinhHeScope.DONG_CUNG, frozenset((anchor,))),
        (TinhHeScope.TAM_PHUONG, tam_phuong),
        (
            TinhHeScope.TAM_PHUONG_TU_CHINH,
            tam_phuong | frozenset((get_xung_chieu(anchor),)),
        ),
    )


def _narrowest_tinh_he_scope(
    *,
    anchor: DiaChi,
    chinh_tinh_dia_chi: dict[str, DiaChi],
) -> TinhHeScope | None:
    for pham_vi, dia_chi_set in _pham_vi_dia_chi(anchor):
        if all(dia_chi in dia_chi_set for dia_chi in chinh_tinh_dia_chi.values()):
            return pham_vi
    return None


def build_tinh_he_evidence(
    la_so: LaSo,
    *,
    anchors: Iterable[Role] = (Role.MENH, Role.CUNG_THAN),
) -> list[TinhHeEvidence]:
    """Nhận diện các tinh hệ chính tinh theo phạm vi hẹp nhất."""
    results: list[TinhHeEvidence] = []
    for anchor in anchors:
        anchor_dia_chi = _required_dia_chi(la_so, anchor.value)
        cung_an_tai = la_so.cung_at(anchor_dia_chi).natal_role
        for definition in TINH_HE_DEFINITIONS:
            chinh_tinh_dia_chi = {
                sao_id: _required_dia_chi(la_so, sao_id)
                for sao_id in definition.chinh_tinh_ids
            }
            pham_vi = _narrowest_tinh_he_scope(
                anchor=anchor_dia_chi,
                chinh_tinh_dia_chi=chinh_tinh_dia_chi,
            )
            if pham_vi is None:
                continue
            chinh_tinh = [
                _sao_evidence(la_so, sao_id, dia_chi=chinh_tinh_dia_chi[sao_id])
                for sao_id in definition.chinh_tinh_ids
            ]
            cung_lien_quan = list(dict.fromkeys(sao.cung for sao in chinh_tinh))
            results.append(
                TinhHeEvidence(
                    tinh_he_id=definition.id,
                    ten=definition.ten,
                    evidence_family_id=f"{definition.id}:{anchor.value}",
                    cung_goc=anchor,
                    cung_an_tai=cung_an_tai,
                    pham_vi=pham_vi,
                    chinh_tinh=chinh_tinh,
                    cung_lien_quan=cung_lien_quan,
                )
            )
    return results


def build_tu_hoa_evidence(
    la_so: LaSo,
    *,
    tinh_he: Sequence[TinhHeEvidence] = (),
) -> list[TuHoaEvidence]:
    """Dựng đủ Tứ Hóa nguyên cục cùng sao được Hóa."""
    target_mapping = load_tu_hoa_target_mapping()[la_so.prior.thien_can]
    results: list[TuHoaEvidence] = []
    for tu_hoa_id in _TU_HOA_IDS:
        sao_duoc_hoa_id = target_mapping[tu_hoa_id]
        dia_chi = _required_dia_chi(la_so, tu_hoa_id)
        sao_dia_chi = _required_dia_chi(la_so, sao_duoc_hoa_id)
        if dia_chi != sao_dia_chi:
            raise ModelRetry(f"{tu_hoa_id} không đồng vị trí với {sao_duoc_hoa_id}.")
        cung = la_so.cung_at(dia_chi)
        tinh_he_lien_quan = [
            item
            for item in tinh_he
            if any(sao.sao_id == sao_duoc_hoa_id for sao in item.chinh_tinh)
        ]
        results.append(
            TuHoaEvidence(
                tu_hoa_id=tu_hoa_id,
                tu_hoa=la_so.component(tu_hoa_id).name,
                sao_duoc_hoa_id=sao_duoc_hoa_id,
                sao_duoc_hoa=la_so.component(sao_duoc_hoa_id).name,
                dia_chi=dia_chi,
                dia_chi_name=_dia_chi_name(la_so, dia_chi),
                cung=cung.natal_role,
                cung_name=_cung_name(la_so, cung.natal_role),
                tinh_he_lien_quan_ids=list(
                    dict.fromkeys(item.tinh_he_id for item in tinh_he_lien_quan)
                ),
                related_evidence_family_ids=[
                    item.evidence_family_id for item in tinh_he_lien_quan
                ],
            )
        )
    return results


def build_phu_tinh_tuan_triet_evidence(
    la_so: LaSo,
    *,
    anchors: Iterable[Role],
) -> list[PhuTinhTuanTrietEvidence]:
    """Dựng phụ tinh và Tuần/Triệt, không gắn nhãn tốt hoặc xấu."""
    results: list[PhuTinhTuanTrietEvidence] = []
    for anchor in anchors:
        dia_chi = _required_dia_chi(la_so, anchor.value)
        cung = la_so.cung_at(dia_chi)
        for component_id in cung.components_in_layer(NATAL_LAYER_ID):
            component = la_so.component(component_id)
            if isinstance(component, ChinhPhuTinh):
                if component.is_chinh_tinh:
                    continue
                loai = PhuTinhTuanTrietKind.PHU_TINH
                trang_thai = _trang_thai_sao(component_id, dia_chi)
                loai_sao = [sao_type.value for sao_type in component.sao_type]
            elif isinstance(component, TuanTriet):
                loai = PhuTinhTuanTrietKind.TUAN_TRIET
                trang_thai = None
                loai_sao = []
            else:
                continue
            results.append(
                PhuTinhTuanTrietEvidence(
                    cung_goc=anchor,
                    component_id=component_id,
                    ten=component.name,
                    loai=loai,
                    dia_chi=dia_chi,
                    dia_chi_name=_dia_chi_name(la_so, dia_chi),
                    cung=cung.natal_role,
                    cung_name=_cung_name(la_so, cung.natal_role),
                    trang_thai=trang_thai,
                    loai_sao=loai_sao,
                )
            )
    return results


def build_menh_than_phu_tinh_tuan_triet(
    la_so: LaSo,
) -> list[PhuTinhTuanTrietEvidence]:
    """Dựng phụ tinh/Tuần/Triệt của Mệnh và Thân thành hai nguồn riêng."""
    return build_phu_tinh_tuan_triet_evidence(
        la_so,
        anchors=(Role.MENH, Role.CUNG_THAN),
    )


def build_cung_bo_sung_evidence(
    la_so: LaSo,
    cung: CungBoSung,
) -> CungBoSungEvidence:
    """Dựng dữ kiện cho một cung bổ sung được cho phép rõ ràng."""
    role = Role(cung)
    if role not in _CUNG_BO_SUNG_ROLES:
        allowed = ", ".join(sorted(item.value for item in _CUNG_BO_SUNG_ROLES))
        raise ValueError(
            f"Cung bổ sung {cung!r} không được hỗ trợ. Các cung hợp lệ: {allowed}."
        )
    tinh_he = build_tinh_he_evidence(la_so, anchors=(role,))
    tu_hoa = [
        item
        for item in build_tu_hoa_evidence(
            la_so,
            tinh_he=tinh_he,
        )
        if item.cung is role
    ]
    return CungBoSungEvidence(
        cau_truc_cung=build_cung_structure(la_so, role),
        tinh_he=tinh_he,
        tu_hoa=tu_hoa,
        phu_tinh_tuan_triet=build_phu_tinh_tuan_triet_evidence(
            la_so,
            anchors=(role,),
        ),
    )


def get_strength_weakness_cung_bo_sung(
    ctx: RunContext[TuviAgentDeps],
    cung: CungBoSung,
) -> CungBoSungEvidence:
    """Lấy evidence lazy cho Phúc Đức, Nô Bộc hoặc Tật Ách.

    Phúc Đức và Nô Bộc chỉ là context có điều kiện. Tật Ách chỉ được dùng để
    giải thích trade-off, không được thay đổi mức đánh giá.
    """
    _logger.info("Lấy cung bổ sung cho strength/weakness: cung=%s", cung)
    result = build_cung_bo_sung_evidence(ctx.deps.require_la_so(), cung)
    _logger.info(
        "Đã lấy cung bổ sung: cung=%s tinh_he=%d phu_tinh_tuan_triet=%d",
        cung,
        len(result.tinh_he),
        len(result.phu_tinh_tuan_triet),
    )
    return result
