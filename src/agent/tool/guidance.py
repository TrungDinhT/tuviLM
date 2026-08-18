from __future__ import annotations

import logging

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


_logger = logging.getLogger(__name__)


_ROLE_INSTRUCTION_MAP: dict[Role, str] = {
    Role.MENH: CUNG_MENH_INSTRUCTION,
    Role.QUAN_LOC: CUNG_QUAN_LOC_INSTRUCTION,
    Role.TAI_BACH: CUNG_TAI_BACH_INSTRUCTION,
    Role.PHU_MAU: CUNG_PHU_MAU_INSTRUCTION,
    Role.HUYNH_DE: CUNG_HUYNH_DE_INSTRUCTION,
    Role.NO_BOC: CUNG_NO_BOC_INSTRUCTION,
    Role.PHU_THE: CUNG_PHU_THE_INSTRUCTION,
    Role.PHUC_DUC: CUNG_PHUC_DUC_INSTRUCTION,
    Role.THIEN_DI: CUNG_THIEN_DI_INSTRUCTION,
    Role.TAT_ACH: CUNG_TAT_ACH_INSTRUCTION,
    Role.TU_TUC: CUNG_TU_TUC_INSTRUCTION,
    Role.DIEN_TRACH: CUNG_DIEN_TRACH_INSTRUCTION,
}


def get_role_instruction(role: Role) -> str:
    """Lấy hướng dẫn phân tích cho một cung dựa trên vai trò của nó.

    role phải là một trong các giá trị sau: menh, quan_loc, tai_bach, phu_mau, huynh_de, no_boc, phu_the, phuc_duc, thien_di, tat_ach, tu_tuc, dien_trach.
    """
    _logger.info("Lấy hướng dẫn luận cung: role=%s", role)
    instruction = _ROLE_INSTRUCTION_MAP.get(role)
    if instruction is None:
        raise ModelRetry(
            f"Vai trò '{role}' không hợp lệ. "
            "Các vai trò hợp lệ là: "
            f"{', '.join(role.value for role in _ROLE_INSTRUCTION_MAP)}."
        )
    _logger.info(
        "Đã lấy hướng dẫn luận cung: role=%s, chars=%d", role, len(instruction)
    )
    return instruction
