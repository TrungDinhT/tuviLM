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
from src.refactored.components.definitions.cung_role import Role


_ROLE_INSTRUCTION_MAP: dict[str, str] = {
    "menh": CUNG_MENH_INSTRUCTION,
    "quan_loc": CUNG_QUAN_LOC_INSTRUCTION,
    "tai_bach": CUNG_TAI_BACH_INSTRUCTION,
    "phu_mau": CUNG_PHU_MAU_INSTRUCTION,
    "huynh_de": CUNG_HUYNH_DE_INSTRUCTION,
    "no_boc": CUNG_NO_BOC_INSTRUCTION,
    "phu_the": CUNG_PHU_THE_INSTRUCTION,
    "phuc_duc": CUNG_PHUC_DUC_INSTRUCTION,
    "thien_di": CUNG_THIEN_DI_INSTRUCTION,
    "tat_ach": CUNG_TAT_ACH_INSTRUCTION,
    "tu_tuc": CUNG_TU_TUC_INSTRUCTION,
    "dien_trach": CUNG_DIEN_TRACH_INSTRUCTION,
}


def get_role_instruction(role: Role) -> str:
    """Lấy hướng dẫn phân tích cho một cung dựa trên vai trò của nó."""
    instruction = _ROLE_INSTRUCTION_MAP.get(role.value)
    if instruction is None:
        raise ModelRetry(
            f"Vai trò '{role.value}' không hợp lệ. "
            f"Các vai trò hợp lệ là: {', '.join(_ROLE_INSTRUCTION_MAP.keys())}."
        )
    return instruction
