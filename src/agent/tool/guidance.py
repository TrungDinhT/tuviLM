from __future__ import annotations

from pydantic_ai import ModelRetry

from src.agent.prompt.skill_analyze_cung import (
    CUNG_DIEN_TRACH_INSTRUCTION,
    CUNG_HUYNH_DE_INSTRUCTION,
    CUNG_MENH_INSTRUCTION,
    CUNG_NO_BOC_INSTRUCTION,
    CUNG_PHU_MAU_INSTRUCTION,
    CUNG_PHU_THE_INSTRUCTION,
    CUNG_PHUC_DUC_INSTRUCTION,
    CUNG_QUAN_LOC_INSTRUCTION,
    CUNG_TAI_BACH_INSTRUCTION,
    CUNG_TAT_ACH_INSTRUCTION,
    CUNG_THIEN_DI_INSTRUCTION,
    CUNG_TU_TUC_INSTRUCTION,
)


_ROLE_INSTRUCTION_MAP: dict[str, str] = {
    "Mệnh": CUNG_MENH_INSTRUCTION,
    "Quan Lộc": CUNG_QUAN_LOC_INSTRUCTION,
    "Tài Bạch": CUNG_TAI_BACH_INSTRUCTION,
    "Phụ Mẫu": CUNG_PHU_MAU_INSTRUCTION,
    "Huynh Đệ": CUNG_HUYNH_DE_INSTRUCTION,
    "Nô Bộc": CUNG_NO_BOC_INSTRUCTION,
    "Phu Thê": CUNG_PHU_THE_INSTRUCTION,
    "Phúc Đức": CUNG_PHUC_DUC_INSTRUCTION,
    "Thiên Di": CUNG_THIEN_DI_INSTRUCTION,
    "Tật Ách": CUNG_TAT_ACH_INSTRUCTION,
    "Tử Tức": CUNG_TU_TUC_INSTRUCTION,
    "Điền Trạch": CUNG_DIEN_TRACH_INSTRUCTION,
}


def get_role_instruction(role: str) -> str:
    """Lấy hướng dẫn phân tích cho một cung dựa trên vai trò của nó.

    role phải là một trong các giá trị sau: Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ.
    """
    instruction = _ROLE_INSTRUCTION_MAP.get(role)
    if instruction is None:
        raise ModelRetry(
            f"Vai trò '{role}' không hợp lệ. "
            f"Các vai trò hợp lệ là: {', '.join(_ROLE_INSTRUCTION_MAP.keys())}."
        )
    return instruction
