from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from src.refactored.component.elementary import ComponentBase


class Role(StrEnum):
    MENH = "menh"
    PHU_MAU = "phu_mau"
    PHUC_DUC = "phuc_duc"
    DIEN_TRACH = "dien_trach"
    QUAN_LOC = "quan_loc"
    NO_BOC = "no_boc"
    THIEN_DI = "thien_di"
    TAT_ACH = "tat_ach"
    TAI_BACH = "tai_bach"
    TU_TUC = "tu_tuc"
    PHU_THE = "phu_the"
    HUYNH_DE = "huynh_de"
    CUNG_THAN = "cung_than"


class CungRole(ComponentBase):
    model_config = {"frozen": True}

    role: Role

    @model_validator(mode="before")
    @classmethod
    def _normalize_role(cls, data: object):
        if not isinstance(data, dict):
            return data
        return {**data, "role": Role(data["id"])}
