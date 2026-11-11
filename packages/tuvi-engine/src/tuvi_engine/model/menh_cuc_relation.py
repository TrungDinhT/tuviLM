from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel
from src.refactored.model.elementary import NguHanh


class MenhCucRelationType(StrEnum):
    SINH_XUAT = "sinh_xuat"
    SINH_NHAP = "sinh_nhap"
    KHAC_XUAT = "khac_xuat"
    KHAC_NHAP = "khac_nhap"
    BINH_HOA = "binh_hoa"


class MenhCucRelation(BaseModel):
    model_config = {"frozen": True}

    label: str
    relation_type: MenhCucRelationType
    ngu_hanh_menh: NguHanh
    ngu_hanh_cuc: NguHanh
    direction: str | None
    description: str

    @classmethod
    def compute(cls, ngu_hanh_menh: NguHanh, ngu_hanh_cuc: NguHanh) -> "MenhCucRelation":

        if ngu_hanh_menh.sinh_xuat(ngu_hanh_cuc):
            return cls(
                label="Mệnh sinh cục",
                relation_type=MenhCucRelationType.SINH_XUAT,
                ngu_hanh_menh=ngu_hanh_menh,
                ngu_hanh_cuc=ngu_hanh_cuc,
                direction="mệnh -> cục",
                description=f"Ngũ hành mệnh ({ngu_hanh_menh.value}) sinh ra ngũ hành cục ({ngu_hanh_cuc.value})",
            )
        if ngu_hanh_menh.sinh_nhap(ngu_hanh_cuc):
            return cls(
                label="Cục sinh mệnh",
                relation_type=MenhCucRelationType.SINH_NHAP,
                ngu_hanh_menh=ngu_hanh_menh,
                ngu_hanh_cuc=ngu_hanh_cuc,
                direction="cục -> mệnh",
                description=f"Ngũ hành cục ({ngu_hanh_cuc.value}) sinh ra ngũ hành mệnh ({ngu_hanh_menh.value})",
            )
        if ngu_hanh_menh.khac_xuat(ngu_hanh_cuc):
            return cls(
                label="Mệnh khắc cục",
                relation_type=MenhCucRelationType.KHAC_XUAT,
                ngu_hanh_menh=ngu_hanh_menh,
                ngu_hanh_cuc=ngu_hanh_cuc,
                direction="mệnh -> cục",
                description=f"Ngũ hành mệnh ({ngu_hanh_menh.value}) khắc ngũ hành cục ({ngu_hanh_cuc.value})",
            )
        if ngu_hanh_menh.khac_nhap(ngu_hanh_cuc):
            return cls(
                label="Cục khắc mệnh",
                relation_type=MenhCucRelationType.KHAC_NHAP,
                ngu_hanh_menh=ngu_hanh_menh,
                ngu_hanh_cuc=ngu_hanh_cuc   ,
                direction="cục -> mệnh",
                description=f"Ngũ hành cục ({ngu_hanh_cuc.value}) khắc ngũ hành mệnh ({ngu_hanh_menh.value})",
            )
        return cls(
            label="Mệnh cục bình hoà",
            relation_type=MenhCucRelationType.BINH_HOA,
            ngu_hanh_menh=ngu_hanh_menh,
            ngu_hanh_cuc=ngu_hanh_cuc,
            direction=None,
            description=f"Mệnh và cục có cùng ngũ hành ({ngu_hanh_cuc.value}), không sinh không khắc",
        )
