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
    get_capability_definition,
)


class WeaknessKind(StrEnum):
    HAN_CHE_TRUC_TIEP = "han_che_truc_tiep"
    QUA_DA = "qua_da"
    XUNG_DOT = "xung_dot"


class StrengthFinding(BaseModel):
    nang_luc_id: str
    mo_ta: str = Field(
        min_length=1,
        description=(
            "Giải nghĩa năng lực bằng biểu hiện đời thường và mô tả bằng lời "
            "mức độ nổi bật, ổn định, phạm vi hoặc điều kiện phát huy của năng "
            "lực này ở chính người được luận; không dùng điểm số hay thang mức."
        ),
    )
    giai_thich: str = Field(
        min_length=1,
        description=(
            "Luận giải Tử Vi chuyên sâu vì sao người này có biểu hiện và mức "
            "độ đã nêu trong mo_ta, dựa trên pattern tổng hợp của toàn bộ "
            "evidence liên quan trong profile."
        ),
    )

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
    mo_ta: str = Field(
        min_length=1,
        description=(
            "Giải nghĩa điểm cần lưu ý, hạn chế hoặc biểu hiện bất lợi bằng "
            "biểu hiện đời thường và mô tả bằng lời mức độ nổi bật, ổn định, "
            "phạm vi hoặc điều kiện nó xuất hiện ở chính người được luận; "
            "không dùng điểm số hay thang mức."
        ),
    )
    giai_thich: str = Field(
        min_length=1,
        description=(
            "Luận giải Tử Vi chuyên sâu vì sao người này có biểu hiện và mức "
            "độ đã nêu trong mo_ta, dựa trên pattern tổng hợp của toàn bộ "
            "evidence liên quan trong profile."
        ),
    )
class CapabilityProfile(BaseModel):
    tong_quan: str = Field(min_length=1)
    diem_manh: list[StrengthFinding] = Field(
        default_factory=list,
        max_length=6,
        description=(
            "Các điểm mạnh khác biệt đủ rõ về hành vi cốt lõi, kết quả tạo ra "
            "hoặc bối cảnh phát huy; không chứa các capability gần như đồng nghĩa."
        ),
    )
    diem_yeu: list[WeaknessFinding] = Field(
        default_factory=list,
        max_length=6,
        description=(
            "Các điểm cần lưu ý khác biệt đủ rõ về cơ chế, biểu hiện hoặc bối "
            "cảnh; không lặp lại cùng một hạn chế bằng nhiều cách gọi gần nghĩa."
        ),
    )

    @model_validator(mode="after")
    def _validate_duplicate_strengths(self) -> Self:
        strength_ids = [finding.nang_luc_id for finding in self.diem_manh]
        if len(strength_ids) != len(set(strength_ids)):
            raise ValueError("Strength capability ids must be unique.")
        return self


CAPABILITY_PROFILE_OUTPUT_INSTRUCTION = """
## Output instruction: Hồ sơ năng lực

Trả kết quả theo đúng output type `CapabilityProfile`.

- `tong_quan` mô tả shape chung của profile, không lặp lại danh sách findings.
- Chọn tối đa 6 điểm mạnh và tối đa 6 điểm yếu; ưu tiên ít findings nhưng được
  nâng đỡ bởi pattern tổng hợp rõ ràng hơn một danh sách dài và generic.
- Cố gắng có ít nhất 2 điểm mạnh và 2 điểm yếu, nhưng tuyệt đối không bịa để đủ
  số lượng khi evidence không hỗ trợ. Số lượng hai phía độc lập và không cần
  bằng nhau.
- `nang_luc_id` phải lấy nguyên văn từ Danh mục năng lực trong instruction.
- Mỗi capability chỉ xuất hiện một lần trong `diem_manh`.
- Chọn `diem_manh` và `diem_yeu` như hai phép đọc độc lập từ toàn bộ profile.
  Không bắt đầu từ một điểm mạnh rồi đảo dấu, kéo quá đà hoặc tạo một điểm yếu
  tương ứng chỉ để thành cặp; cũng không buộc thứ tự hai danh sách tương ứng.
- Một cấu trúc Tử Vi có thể góp phần vào cả hai phía khi hai kết luận đều được
  pattern tổng hợp hỗ trợ độc lập, nhưng không vì vậy mà hai finding trở thành
  một cặp bắt buộc.

### Đa dạng ngữ nghĩa giữa các findings

- Giới hạn 6 là mức trần, không phải mục tiêu phải lấp đầy. Trước khi output,
  so sánh từng cặp finding trong `diem_manh`, và làm tương tự trong `diem_yeu`.
- Hai finding là quá gần nhau khi chúng chủ yếu mô tả cùng một hành vi cốt lõi,
  cùng kết quả tạo ra và cùng bối cảnh phát huy, dù dùng capability ID, tiêu đề
  hoặc category khác nhau. Khi đó chỉ giữ finding có tên chính xác hơn và được
  pattern hỗ trợ nổi trội hơn; gộp sắc thái hữu ích của finding còn lại vào
  `mo_ta`, không tạo thêm một card.
- Chỉ giữ hai finding có phần giao nhau khi có thể nêu rõ khác biệt thực chất về
  ít nhất một trong ba trục: hành vi cốt lõi, kết quả tạo ra, hoặc bối cảnh/điều
  kiện phát huy. Cùng category không tự động là trùng; khác category cũng không
  tự động là khác biệt.
- Ví dụ, `khoi_dong_hanh_dong` và `quyet_doan` phải gộp nếu cả hai chỉ đang nói
  người này nhanh chóng bắt tay và chốt việc. Chỉ giữ cả hai khi kết luận phân
  biệt rõ khả năng vượt quán tính để bắt đầu hành động với khả năng cam kết một
  lựa chọn khi có nhiều phương án hoặc thông tin bất định.
- Áp dụng cùng nguyên tắc cho điểm yếu: không tách một hạn chế thành nhiều
  finding chỉ vì có thể đặt nhiều tên gần nghĩa.

### Phân định `mo_ta` và `giai_thich`

- `mo_ta` của mỗi finding phải có đủ hai ý, viết liền thành 2–4 câu tự nhiên:
  1. Giải nghĩa năng lực, hạn chế hoặc biểu hiện bất lợi đó bằng hành vi dễ hiểu:
     người này thường làm gì, xử lý thế nào hoặc dễ gặp khó ở đâu.
  2. Mô tả bằng lời mức độ nó hiện diện ở chính người này: nổi trội đến đâu, có
     ổn định không, phát huy rộng hay chỉ trong một số bối cảnh, và điều kiện
     nào làm biểu hiện đó mạnh lên, yếu đi hoặc thay đổi.
- Không dùng điểm số, phần trăm, cấp bậc, nhãn thang mức như "level cao/thấp",
  hoặc chỉ nói chung chung "rất mạnh", "khá yếu" mà không diễn tả mạnh/yếu
  theo cách nào. `mo_ta` không luận sao, cung hay thuật ngữ Tử Vi.
- `giai_thich` là phần luận giải Tử Vi chuyên sâu trả lời vì sao người này có
  đúng biểu hiện và mức độ đã nêu trong `mo_ta`. Phải phân tích sự phối hợp,
  điều kiện hóa và xung đột giữa Mệnh/Thân, tam phương tứ chính, cách cục, chính
  tinh/phụ tinh, Tứ Hóa và Tuần/Triệt khi chúng thực sự liên quan.
- `giai_thich` không được chỉ diễn đạt lại `mo_ta`. Có thể gọi tên sao, cung và
  cấu trúc Tử Vi trong mạch phân tích, nhưng không trình bày thành danh sách
  evidence rời rạc và không suy một evidence riêng lẻ thẳng thành kết luận.

### Nguyên tắc tổng hợp

- Mỗi finding phải là kết quả tổng hợp các evidence liên quan trong tương quan
  với toàn profile, bao gồm cả tín hiệu củng cố, điều kiện hóa và xung đột.
- Không tách một sao, cung, cách cục hay evidence riêng lẻ rồi xem đó là nguyên
  nhân đủ cho kết luận. Không xuất evidence ID, chain-of-thought hoặc trích đoạn
  sách dài.
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
    WeaknessKind.QUA_DA: "Biểu hiện quá đà",
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
    lines.extend(["", "## Điểm cần lưu ý"])
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
