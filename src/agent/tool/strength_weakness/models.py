"""Factual evidence models for the strength/weakness workflow."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi


class TinhHeScope(StrEnum):
    """Phạm vi hẹp nhất mà một tinh hệ chính tinh được hình thành đầy đủ."""

    DONG_CUNG = "dong_cung"
    TAM_PHUONG = "tam_phuong"
    TAM_PHUONG_TU_CHINH = "tam_phuong_tu_chinh"


class PhuTinhTuanTrietKind(StrEnum):
    """Loại dữ kiện; không hàm ý tốt, xấu, cộng hay trừ điểm."""

    PHU_TINH = "phu_tinh"
    TUAN_TRIET = "tuan_triet"


class SaoEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    sao_id: str
    ten: str
    dia_chi: DiaChi
    dia_chi_name: str
    cung: Role
    cung_name: str
    trang_thai: str | None = None


class CungStructureEvidence(BaseModel):
    """Cấu trúc chính tinh trực tiếp tại một cung gốc được yêu cầu."""

    model_config = ConfigDict(frozen=True)

    cung_goc: Role
    dia_chi: DiaChi
    dia_chi_name: str
    cung: Role
    cung_name: str
    la_cung_than: bool
    chinh_tinh: list[SaoEvidence] = Field(default_factory=list)


class TinhHeEvidence(BaseModel):
    """Một tinh hệ chính tinh đã khớp, chưa kèm diễn giải mạnh/yếu."""

    model_config = ConfigDict(frozen=True)

    tinh_he_id: str
    ten: str
    evidence_family_id: str
    cung_goc: Role
    cung_an_tai: Role
    pham_vi: TinhHeScope
    chinh_tinh: list[SaoEvidence]
    cung_lien_quan: list[Role]


class TuHoaEvidence(BaseModel):
    """Một Tứ Hóa nguyên cục và sao được Hóa tương ứng."""

    model_config = ConfigDict(frozen=True)

    tu_hoa_id: str
    tu_hoa: str
    sao_duoc_hoa_id: str
    sao_duoc_hoa: str
    dia_chi: DiaChi
    dia_chi_name: str
    cung: Role
    cung_name: str
    tinh_he_lien_quan_ids: list[str] = Field(default_factory=list)
    related_evidence_family_ids: list[str] = Field(default_factory=list)


class PhuTinhTuanTrietEvidence(BaseModel):
    """Phụ tinh hoặc Tuần/Triệt trực tiếp tại một cung gốc."""

    model_config = ConfigDict(frozen=True)

    cung_goc: Role
    component_id: str
    ten: str
    loai: PhuTinhTuanTrietKind
    dia_chi: DiaChi
    dia_chi_name: str
    cung: Role
    cung_name: str
    trang_thai: str | None = None
    loai_sao: list[str] = Field(default_factory=list)


class CungBoSungEvidence(BaseModel):
    """Dữ kiện lazy giới hạn ở Phúc Đức, Nô Bộc hoặc Tật Ách."""

    model_config = ConfigDict(frozen=True)

    cau_truc_cung: CungStructureEvidence
    tinh_he: list[TinhHeEvidence] = Field(default_factory=list)
    tu_hoa: list[TuHoaEvidence] = Field(default_factory=list)
    phu_tinh_tuan_triet: list[PhuTinhTuanTrietEvidence] = Field(
        default_factory=list
    )
