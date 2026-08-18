"""Structured capability profile and its deterministic chat renderer."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from src.agent.workflow.contracts import WorkflowOutputInstruction
from src.agent.workflow.strength_weakness.ontology import (
    CAPABILITY_BY_ID,
    get_capability_definition,
)


class WeaknessKind(StrEnum):
    HAN_CHE_TRUC_TIEP = "han_che_truc_tiep"
    QUA_DA = "qua_da"
    XUNG_DOT = "xung_dot"


class StrengthFinding(BaseModel):
    nang_luc_id: str
    mo_ta: str = Field(min_length=1)
    giai_thich: str = Field(min_length=1)

    @field_validator("nang_luc_id")
    @classmethod
    def _known_capability(cls, value: str) -> str:
        get_capability_definition(value)
        return value

    @computed_field
    @property
    def nang_luc(self) -> str:
        return get_capability_definition(self.nang_luc_id).label


class WeaknessFinding(BaseModel):
    ten: str = Field(min_length=1)
    loai: WeaknessKind
    mo_ta: str = Field(min_length=1)
    giai_thich: str = Field(min_length=1)
    lien_quan_diem_manh: list[str] = Field(default_factory=list)

    @field_validator("lien_quan_diem_manh")
    @classmethod
    def _known_related_capabilities(cls, values: list[str]) -> list[str]:
        for value in values:
            get_capability_definition(value)
        if len(values) != len(set(values)):
            raise ValueError("Related strength ids must be unique.")
        return values


class CapabilityProfile(BaseModel):
    tong_quan: str = Field(min_length=1)
    diem_manh: list[StrengthFinding] = Field(default_factory=list, max_length=5)
    diem_yeu: list[WeaknessFinding] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def _validate_references_and_duplicates(self) -> Self:
        strength_ids = [finding.nang_luc_id for finding in self.diem_manh]
        if len(strength_ids) != len(set(strength_ids)):
            raise ValueError("Strength capability ids must be unique.")

        selected = set(strength_ids)
        for weakness in self.diem_yeu:
            unknown = set(weakness.lien_quan_diem_manh) - selected
            if unknown:
                raise ValueError(
                    "Weakness references capabilities that are not selected "
                    f"strengths: {sorted(unknown)}."
                )
        return self


CAPABILITY_PROFILE_OUTPUT_INSTRUCTION = """
## Output instruction: Hồ sơ năng lực

Trả kết quả theo đúng output type `CapabilityProfile`.

- `tong_quan` mô tả shape chung của profile, không lặp lại danh sách findings.
- Chọn tối đa 5 điểm mạnh và tối đa 4 điểm yếu; ưu tiên ít findings nhưng được
  nâng đỡ bởi pattern tổng hợp rõ ràng hơn một danh sách dài và generic.
- Cố gắng có ít nhất 2 điểm mạnh và 2 điểm yếu, nhưng tuyệt đối không bịa để đủ
  số lượng khi evidence không hỗ trợ.
- `nang_luc_id` phải lấy nguyên văn từ Danh mục năng lực trong instruction.
- Mỗi capability chỉ xuất hiện một lần trong `diem_manh`.
- Điểm yếu `qua_da` hoặc `xung_dot` nên dùng `lien_quan_diem_manh` để tham chiếu
  đúng capability ID đã chọn trong `diem_manh`.
- Mỗi finding phải là kết quả tổng hợp các evidence liên quan trong tương quan
  với toàn profile, bao gồm cả tín hiệu củng cố, điều kiện hóa và xung đột.
- Không tách một sao, cung, cách cục hay evidence riêng lẻ rồi xem đó là nguyên
  nhân đủ cho kết luận. `giai_thich` diễn đạt pattern hành vi đã tổng hợp, không
  liệt kê evidence, evidence ID, chain-of-thought hoặc trích đoạn sách.
- Viết tiếng Việt tự nhiên, điềm đạm, dùng ngôn ngữ có điều kiện và nói trực
  tiếp với người dùng bằng "bạn".
""".strip()


CAPABILITY_PROFILE_OUTPUT = WorkflowOutputInstruction(
    name="capability_profile",
    instruction=CAPABILITY_PROFILE_OUTPUT_INSTRUCTION,
    output_type=CapabilityProfile,
)


_WEAKNESS_LABELS = {
    WeaknessKind.HAN_CHE_TRUC_TIEP: "Hạn chế trực tiếp",
    WeaknessKind.QUA_DA: "Mặt quá đà",
    WeaknessKind.XUNG_DOT: "Xung đột khuynh hướng",
}


def render_capability_profile(profile: CapabilityProfile) -> str:
    """Render structured output without adding or changing any conclusion."""
    lines = ["## Tổng quan", "", profile.tong_quan, "", "## Điểm mạnh"]
    if not profile.diem_manh:
        lines.extend(["", "Chưa có đủ căn cứ để chọn điểm mạnh nổi bật."])
    for index, finding in enumerate(profile.diem_manh, start=1):
        lines.extend(
            [
                "",
                f"### {index}. {finding.nang_luc}",
                "",
                finding.mo_ta,
                "",
                finding.giai_thich,
            ]
        )
    lines.extend(["", "## Điểm yếu và mặt trái"])
    if not profile.diem_yeu:
        lines.extend(["", "Chưa có đủ căn cứ để chọn hạn chế nổi bật."])
    for index, finding in enumerate(profile.diem_yeu, start=1):
        lines.extend(
            [
                "",
                f"### {index}. {finding.ten}",
                "",
                f"Loại: {_WEAKNESS_LABELS[finding.loai]}.",
                "",
                finding.mo_ta,
                "",
                finding.giai_thich,
            ]
        )
        if finding.lien_quan_diem_manh:
            labels = [
                CAPABILITY_BY_ID[capability_id].label
                for capability_id in finding.lien_quan_diem_manh
            ]
            lines.extend(["", "Liên quan điểm mạnh: " + "; ".join(labels) + "."])
    return "\n".join(lines).strip()


__all__ = [
    "CAPABILITY_PROFILE_OUTPUT",
    "CAPABILITY_PROFILE_OUTPUT_INSTRUCTION",
    "CapabilityProfile",
    "StrengthFinding",
    "WeaknessFinding",
    "WeaknessKind",
    "render_capability_profile",
]
