"""Structured radar output contract and instructions."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrengthWeaknessDimension(StrEnum):
    ANALYSIS_REASONING = "analysis_reasoning"
    LEARNING_ABSORPTION = "learning_absorption"
    FORESIGHT_PREPAREDNESS = "foresight_preparedness"
    DECISION_MAKING = "decision_making"
    ACTION_EXECUTION = "action_execution"
    STRUCTURING_ORGANIZATION = "structuring_organization"
    EXPRESSION_PERSUASION = "expression_persuasion"
    ADAPTABILITY = "adaptability"
    CREATIVITY_NEW_APPROACHES = "creativity_new_approaches"
    COLLABORATION_COORDINATION = "collaboration_coordination"
    LEADERSHIP_MOBILIZATION = "leadership_mobilization"


class StrengthWeaknessLevel(StrEnum):
    NEARLY_ABSENT = "nearly_absent"
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    IMPROVABLE = "improvable"
    NORMAL = "normal"
    ABOVE_NORMAL = "above_normal"
    GOOD = "good"
    VERY_GOOD = "very_good"
    EXCELLENT = "excellent"


class StrengthWeaknessBasis(StrEnum):
    """Machine-readable reason for a level; UI may choose not to display it."""

    SUPPORTED = "supported"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    BALANCED_CONFLICT = "balanced_conflict"


class StrengthWeaknessScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_reasoning: StrengthWeaknessLevel
    learning_absorption: StrengthWeaknessLevel
    foresight_preparedness: StrengthWeaknessLevel
    decision_making: StrengthWeaknessLevel
    action_execution: StrengthWeaknessLevel
    structuring_organization: StrengthWeaknessLevel
    expression_persuasion: StrengthWeaknessLevel
    adaptability: StrengthWeaknessLevel
    creativity_new_approaches: StrengthWeaknessLevel
    collaboration_coordination: StrengthWeaknessLevel
    leadership_mobilization: StrengthWeaknessLevel

    def for_dimension(
        self,
        dimension: StrengthWeaknessDimension,
    ) -> StrengthWeaknessLevel:
        return getattr(self, dimension.value)


class StrengthWeaknessBases(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_reasoning: StrengthWeaknessBasis
    learning_absorption: StrengthWeaknessBasis
    foresight_preparedness: StrengthWeaknessBasis
    decision_making: StrengthWeaknessBasis
    action_execution: StrengthWeaknessBasis
    structuring_organization: StrengthWeaknessBasis
    expression_persuasion: StrengthWeaknessBasis
    adaptability: StrengthWeaknessBasis
    creativity_new_approaches: StrengthWeaknessBasis
    collaboration_coordination: StrengthWeaknessBasis
    leadership_mobilization: StrengthWeaknessBasis

    def for_dimension(
        self,
        dimension: StrengthWeaknessDimension,
    ) -> StrengthWeaknessBasis:
        return getattr(self, dimension.value)


class StrengthWeaknessExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: StrengthWeaknessDimension
    level: StrengthWeaknessLevel
    summary: str
    reasoning: str
    tradeoff: str | None = None
    potential: str | None = None


class StrengthWeaknessAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scores: StrengthWeaknessScores
    score_bases: StrengthWeaknessBases
    overview: str
    notable_dimensions: list[StrengthWeaknessExplanation] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def _validate_cross_field_contract(self) -> StrengthWeaknessAssessment:
        explanations: dict[StrengthWeaknessDimension, StrengthWeaknessExplanation] = {}
        for explanation in self.notable_dimensions:
            if explanation.dimension in explanations:
                raise ValueError(
                    f"Duplicate explanation for {explanation.dimension.value}."
                )
            expected_level = self.scores.for_dimension(explanation.dimension)
            if explanation.level is not expected_level:
                raise ValueError(
                    f"Explanation level for {explanation.dimension.value} "
                    f"must equal its score."
                )
            explanations[explanation.dimension] = explanation

        for dimension in StrengthWeaknessDimension:
            level = self.scores.for_dimension(dimension)
            basis = self.score_bases.for_dimension(dimension)
            if (
                level is not StrengthWeaknessLevel.NORMAL
                and basis is not StrengthWeaknessBasis.SUPPORTED
            ):
                raise ValueError(
                    f"Non-normal score for {dimension.value} must be supported."
                )
            if basis in {
                StrengthWeaknessBasis.INSUFFICIENT_EVIDENCE,
                StrengthWeaknessBasis.BALANCED_CONFLICT,
            } and level is not StrengthWeaknessLevel.NORMAL:
                raise ValueError(
                    f"{basis.value} is only valid with a normal score."
                )
            if basis is StrengthWeaknessBasis.BALANCED_CONFLICT and dimension not in explanations:
                raise ValueError(
                    f"Balanced conflict for {dimension.value} requires an explanation."
                )
            if basis is StrengthWeaknessBasis.INSUFFICIENT_EVIDENCE and dimension in explanations:
                raise ValueError(
                    f"Insufficient evidence for {dimension.value} must not be narrated."
                )
        return self


RADAR_OUTPUT_INSTRUCTION = """
## Structured output: Strength/Weakness radar

Trả đúng `StrengthWeaknessAssessment` được enforce bởi output type.

Trước khi trả contract này, xác nhận phase `search_star_info` đã hoàn tất cho
toàn bộ `sao_can_tra_cuu`. Nếu chưa, tiếp tục gọi tool; không dùng output tool
để kết thúc sớm.

- `scores` phải có đủ 11 dimension, dùng đúng một trong chín level theo thứ tự
  từ hạn chế nhất đến nổi trội nhất:
  - `nearly_absent` — Gần như không có: năng lực hầu như không biểu hiện một
    cách khả dụng; chỉ dùng khi có evidence giới hạn rất rõ và nhất quán, không
    bao giờ dùng chỉ vì thiếu evidence.
  - `very_weak` — Rất yếu: hạn chế sâu, lặp lại và khó tự bù trong điều kiện
    thông thường.
  - `weak` — Yếu: có khả năng vận hành nhưng thường hụt, chậm hoặc thiếu ổn định
    theo evidence trực tiếp.
  - `improvable` — Có thể cải thiện được: nền năng lực đã hiện diện nhưng còn
    non, phụ thuộc điều kiện hoặc chưa chuyển thành biểu hiện ổn định. Đây không
    phải cách nói giảm của `weak`.
  - `normal` — Bình thường: vận hành ở vùng thông thường, hoặc chưa đủ evidence
    để kết luận lệch khỏi vùng này; phân biệt hai trường hợp bằng `score_bases`.
  - `above_normal` — Hơn bình thường: tín hiệu thuận rõ và khá ổn định nhưng
    chưa đủ đậm để gọi là một điểm mạnh nổi bật.
  - `good` — Tốt: là điểm mạnh rõ, có thể trông cậy trong nhiều tình huống phù
    hợp với evidence.
  - `very_good` — Rất tốt: điểm mạnh nổi trội, bền và được nhiều nguồn evidence
    thực sự độc lập củng cố.
  - `excellent` — Xuất sắc: năng lực đặc biệt nổi bật và mang tính trung tâm;
    dùng hiếm, chỉ khi gestalt toàn bộ evidence hội tụ rất mạnh.
- Chọn level bằng so sánh định tính với các ranh giới trên sau khi tổng hợp bộ
  sao. Không đổi evidence thành điểm số, không cộng/trừ từng sao và không coi
  chín level là chín mốc số học cách đều.
- `score_bases` phải có đủ 11 dimension. Dùng `supported` khi evidence thực sự
  hỗ trợ level, `insufficient_evidence` khi giữ NORMAL do thiếu signal, và
  `balanced_conflict` khi hai hướng evidence mạnh cân nhau.
- `overview` dài khoảng 2-5 câu, mô tả shape tổng thể, không lặp đủ 11 score.
- `notable_dimensions` ưu tiên giải thích `nearly_absent`, `very_weak`,
  `excellent`, `very_good` trước, rồi các lệch mức đáng kể hoặc contrast cần
  hiểu rõ. Không viết đủ 11 đoạn theo mặc định.
- Mọi dimension có `balanced_conflict` bắt buộc xuất hiện trong
  `notable_dimensions`, dù score là NORMAL.
- Không viết explanation cho dimension có `insufficient_evidence`.
- `summary` nói về biểu hiện con người trước, không dump tên sao.
- `reasoning` chỉ tóm tắt căn cứ có thể kiểm tra như tinh hệ nào, Mệnh/Thân có
  cùng hướng hay Tứ Hóa nào củng cố. Không trình bày chain-of-thought chi tiết.
- `tradeoff` là mặt trái cùng cơ chế với strength; shadow không tự hạ score.
- Evidence Tật Ách, nếu đã gọi, chỉ được xuất hiện trong `tradeoff`.
- `potential` chỉ có khi Mệnh, Thân và Tứ Hóa cùng củng cố một hướng phát triển;
  diễn đạt trừu tượng, không dự đoán nghề nghiệp.
- Viết nội dung user-facing bằng tiếng Việt, trực tiếp với người đọc bằng “bạn”,
  có điều kiện và không định mệnh hóa.
""".strip()
