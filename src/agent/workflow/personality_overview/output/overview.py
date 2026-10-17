"""Four-part output contract and deterministic Markdown rendering."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.agent.workflow.contracts import WorkflowOutputInstruction

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PersonalityOverview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    net_chu_dao: NonEmptyText = Field(description="Một đoạn ngắn về một pattern chủ đạo.")
    bieu_hien_thuong_thay: list[NonEmptyText] = Field(
        min_length=2, max_length=3,
        description="Hai hoặc ba biểu hiện cụ thể của cùng pattern trong đời sống.",
    )
    mat_con_lai: NonEmptyText = Field(description="Tension hoặc cái giá của chính pattern đó.")
    mot_dieu_dang_de_y: NonEmptyText = Field(
        description="Một câu gợi mở thêm góc tự quan sát, không yêu cầu người dùng trả lời.",
    )


PERSONALITY_OVERVIEW_OUTPUT = WorkflowOutputInstruction(
    name="personality_overview",
    output_type=PersonalityOverview,
    instruction="""
Trả đúng schema PersonalityOverview, nội dung tiếng Việt, gọi người dùng là bạn.
- net_chu_dao: một đoạn ngắn về MỘT pattern quan trọng nhất; không liệt kê tính từ.
- bieu_hien_thuong_thay: 2–3 biểu hiện cụ thể, dễ liên hệ đời sống; không bịa sự
  kiện đã xảy ra. Các ví dụ là khả năng biểu hiện, không phải tiểu sử.
- mat_con_lai: tension hoặc cái giá của cùng pattern, không thêm khuyết điểm
  độc lập, không bắt buộc đưa mọi tension của nhóm/sao vào bài.
- mot_dieu_dang_de_y: đúng một câu gợi mở một góc nhìn mới, không lặp kết luận,
  không kiểm tra luận đoán đúng sai, không yêu cầu trả lời. Có thể gợi quan sát
  điều kiện, ngoại lệ, khoảng cách suy nghĩ–hành động hoặc tác động lên người khác.
Viết ngắn gọn cho người không biết Tử Vi, không thêm tiêu đề trong các field,
không thêm section Thân/Tật Ách, không xuất evidence ID, suy luận nội bộ hay
trích sách dài. Chỉ gọi tên sao/cung khi thật sự cần để hiểu nhận định.
Dùng ngôn ngữ có điều kiện phù hợp; tránh câu chung chung đúng với gần mọi người.
Nếu thiếu nghĩa sao, nói rõ giới hạn ngắn gọn trong net_chu_dao; chỉ dùng phần
giả thuyết còn có căn cứ, không bịa để tạo cảm giác đầy đủ hoặc cá nhân hóa.
""".strip(),
)


def render_personality_overview(profile: PersonalityOverview) -> str:
    return "\n\n".join([
        "### Nét chủ đạo", profile.net_chu_dao,
        "### Biểu hiện thường thấy",
        "\n".join(f"- {item}" for item in profile.bieu_hien_thuong_thay),
        "### Mặt còn lại", profile.mat_con_lai,
        "### Một điều đáng để ý", profile.mot_dieu_dang_de_y,
    ])
