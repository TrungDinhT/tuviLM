"""Four-part output contract and deterministic Markdown rendering."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from tuvi_agent.workflow.contracts import WorkflowOutputInstruction

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PersonalityOverview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    net_chu_dao: NonEmptyText = Field(description="Một đoạn ngắn về một pattern chủ đạo.")
    bieu_hien_thuong_thay: list[NonEmptyText] = Field(
        min_length=1, max_length=2,
        description="Một hoặc hai biểu hiện có căn cứ của cùng khí chất, không phải sự kiện chắc chắn.",
    )
    mat_con_lai: NonEmptyText = Field(
        description="Sức ép, giới hạn hoặc mặt dễ vướng có căn cứ của cùng khí chất, không nhất thiết là khuyết điểm.",
    )
    mot_dieu_dang_de_y: NonEmptyText = Field(
        description="Một câu ngắn về một góc tự quan sát, hoặc điều kiện / dấu hiệu giúp nhận ra khi nét chủ đạo thay đổi, không yêu cầu trả lời.",
    )


PERSONALITY_OVERVIEW_OUTPUT = WorkflowOutputInstruction(
    name="personality_overview",
    output_type=PersonalityOverview,
    instruction="""
Trả đúng schema PersonalityOverview, nội dung tiếng Việt, gọi người dùng là bạn.
- net_chu_dao: một đoạn ngắn về nét nổi bật nhất và cách nó vận hành; không
  liệt kê tính từ hoặc ép thành hai mặt đối lập.
- bieu_hien_thuong_thay: chọn một hoặc hai biểu hiện có căn cứ,
  mỗi ý làm rõ thêm cách nghĩ hoặc cách làm của cùng khí chất.
  Đây là khả năng biểu hiện, không phải sự kiện đã xảy ra.
- mat_con_lai: mặt còn lại của cùng khí chất, không nhất thiết là khuyết điểm;
  có thể là sự chần chừ, sức ép hoặc giới hạn đi kèm nếu nguồn có căn cứ.
  Không kể lại nét chủ đạo, thêm khuyết điểm độc lập hay ép một mâu thuẫn.
  Nếu nguồn chỉ có mặt trái nặng, giữ đúng điều kiện và diễn đạt ngắn gọn;
  không tự chế một nhược điểm nhẹ hơn để bài dễ nghe. Nếu chưa đủ căn cứ,
  nêu giới hạn ngắn gọn thay vì gán một điểm yếu cho người dùng.
- mot_dieu_dang_de_y (Reflection Lens): một câu ngắn khoảng 20–40 từ về điều
  kiện hoặc dấu hiệu giúp người dùng nhận ra khi nét chủ đạo thay đổi cách biểu hiện.
  Chỉ dùng dữ kiện đã có; nếu chưa có góc mới đủ căn cứ, thu hẹp vào hoàn cảnh
  xuất hiện thay vì suy thêm động cơ. Xuất phát từ khí chất và mặt đánh đổi đã phân tích;
  không tóm tắt lại bài, đưa lời khuyên, gắn nhãn "nét đang chuyển", kiểm tra
  luận đoán hay yêu cầu người dùng trả lời.
Viết theo giọng luận Tử Vi bằng tiếng Việt đời thường: điềm đạm, có sắc thái,
súc tích, người không biết Tử Vi vẫn hiểu. Dẫn từ bố cục sao–cung sang khí chất,
rồi nói rõ cách nghĩ, cách làm; dùng những từ như khí chất, tự chủ, lập trường,
khuôn phép khi đúng nghĩa, không cố làm cổ kính hoặc huyền bí.
Ưu tiên giới thiệu tinh hệ Mệnh ở net_chu_dao khi có menh.interpretation. Có thể mở bằng
“Mệnh có…”, “… đồng cung tại Mệnh” hoặc “… độc tọa, khí chất thiên về…”
khi đúng dữ kiện; thay đổi nhịp câu, không bắt mọi bài theo một mẫu mở đầu.
Dùng địa chi thực tế nếu nhắc vị trí, không chép tên cặp địa chi của bản ghi.
Gọi tên khi giúp giải thích: có thể  nhắc thêm sao trong vòng Thái Tuế tọa mệnh, Thân
khi có ý nghĩa và có nguồn.
Mỗi thuật ngữ đi liền lời giải thích; không trang trí bằng tên sao, nhắc tên
liên tục hoặc thêm sao ngoài context.
Tránh công thức “sao X khiến bạn Y”; không lặp “tinh hệ X gợi lên khuynh hướng…”
như câu dẫn mặc định. Dùng “thường”, “có xu hướng”, “có thể” đúng chỗ,
không chồng nhiều từ dè dặt trong một câu hoặc khẳng định tính cách như định mệnh.
Mỗi câu tập trung một ý, đan xen câu ngắn và câu dài vừa phải. Chuyển những
cụm trừu tượng về cơ chế, vận dụng, điều kiện bộc lộ thành cách nghĩ hoặc hành
động cụ thể đã có căn cứ; không thêm tình huống đời sống để làm câu văn sinh động.
Phần mặt còn lại đi thẳng vào điều kiện và chỗ dễ vướng; không mặc định mở bằng
“Cái giá của lối vận hành này…”. Câu cuối không bắt buộc tìm dấu hiệu xấu đi.
Không thêm tiêu đề trong các field,
không thêm section ngoài bốn phần, không xuất evidence ID, suy luận nội bộ.
Tránh câu chung chung đúng với gần mọi người hoặc gán nhãn đạo đức như phán quyết.
Nếu thiếu căn cứ diễn giải, nói rõ giới hạn ngắn gọn trong net_chu_dao; chỉ dùng phần
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
