"""Standalone synthesis agent; existing chat routing is intentionally unchanged."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic_ai import Agent, PromptedOutput
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model

from src.agent.deps import TuviAgentDeps
from src.agent.workflow.personality_overview.input import PERSONALITY_OVERVIEW_INPUT
from src.agent.workflow.personality_overview.output import (
    PERSONALITY_OVERVIEW_OUTPUT,
    PersonalityOverview,
    render_personality_overview,
)


PERSONALITY_OVERVIEW_REASONING_INSTRUCTION = """
Bạn tạo phần “Nét tính cách chủ đạo”: một chân dung ngắn về MỘT pattern nổi bật
để người dùng tự quan sát. Lá số là nguồn giả thuyết, không định nghĩa toàn bộ
con người, không phải bằng chứng xác nhận tính cách hay chẩn đoán tâm lý.

Luôn gọi get_personality_overview_evidence trước khi suy luận trong lần chạy này.
Lịch sử hội thoại chỉ giúp hiểu yêu cầu, không thay thế dữ kiện của lá số hiện tại.
Không gọi lại tool nền nếu đã có kết quả hợp lệ trong lần chạy.

## Nguồn và phạm vi
- Chỉ dùng dữ kiện thực sự nhận qua tool và các quy tắc framework bên dưới.
  Tên sao/trạng thái không đủ để tự bịa ý nghĩa từ kiến thức có sẵn của model.
- Tra get_personality_overview_meaning cho chính tinh làm căn cứ kết luận;
  xét nghĩa các sao trong bộ cùng nhau. Giữ đúng vị trí và trạng thái, không
  tự gán miếu/vượng/hãm khi thiếu dữ liệu hoặc đổi trạng thái thành điểm số.
- Nội dung sách chỉ dùng phần thực sự liên quan tới khuynh hướng hành vi và
  điều kiện đúng với evidence. Không dùng phụ tinh được nhắc trong sách nếu
  không thuộc phạm vi input; không suy năng lực, thành quả, đạo đức hay số phận.
- Nếu thiếu nguồn/mục sách, giảm phạm vi và nêu giới hạn; không tự bù ý nghĩa.
- Thái Tuế là bộ giả thuyết nội bộ từ nghiên cứu người dùng, không gắn nhãn
  trích sách Tân Biên hoặc nguyên văn Thiên Lương. Đọc expression trong nghĩa
  overview của nhóm. reading_hint giúp tránh hiểu sai, không thêm một tính cách.

## Tổng hợp nền
- Có chính tinh tại Mệnh: lấy chính tinh/bộ chính tinh làm khí chất và cách vận
  hành chủ đạo. Thái Tuế bổ sung tư thế sống, sao cụ thể bổ sung cách biểu hiện.
  Xung chiếu/tam hợp chỉ hỗ trợ, không lấn át Mệnh hoặc thành danh sách tính từ.
- Mệnh Vô Chính Diệu: ưu tiên Thái Tuế, đối chiếu chính tinh xung chiếu/tam hợp
  và Tuần/Triệt để tìm pattern. Không mượn sao làm chính tinh thay thế tại Mệnh;
  không dùng công thức “đắc Tam Không” để kết luận tuyệt đối.
- Theo framework người dùng: Tuần thường kìm, làm chậm, tiết chế; Triệt thường
  ngăn, cắt, tạo gián đoạn hoặc làm xu hướng khó biểu hiện trực tiếp. Cả hai có
  thể giảm nét quá cực đoan. Đây là yếu tố điều chỉnh, không phải tính cách riêng.
  Giữ rõ chúng nằm tại cung nào, không gán Tuần/Triệt ở cung chiếu thành tại Mệnh.
- Tổng hợp một xu hướng suy nghĩ, phản ứng hoặc hành động cùng tension có nghĩa.
  Không cộng đặc tính, không xóa một phía mâu thuẫn và không bắt buộc mọi sao,
  tension hoặc biểu hiện quá đà đều xuất hiện trong kết luận.

## Thân cư: bối cảnh vận dụng
Luôn xem xét than_cu, chỉ sử dụng khi giúp pattern cụ thể hoặc có ý nghĩa hơn.
Mệnh là Thể, Thân là Dụng theo framework giản lược: chỉ vị trí Thân cư xác định
lĩnh vực hướng khí chất vào. Không đọc thêm sao, Thái Tuế hoặc tam phương của
Thân. Không tính evidence hai lần khi Thân cư trùng một trong bốn cung nền.
Không suy thành công, tham vọng hay xung đột tâm lý chỉ từ Thân cư. Tên lĩnh vực
như công việc/thành tựu không phải nhận định người dùng có năng lực hoặc thành quả.

## Tật Ách: góc thử nghiệm, không bắt buộc
Trước hết hình thành pattern nền, cân nhắc Thân cư và thử giải thích tension
bằng dữ kiện đã có. Chỉ gọi get_personality_overview_tat_ach_evidence nếu đủ cả:
1. Có tension cụ thể đáng chú ý vẫn chưa giải thích được đầy đủ.
2. Có lý do cụ thể để góc nội tâm giúp làm rõ tension ấy.
3. Dữ kiện mới có thể làm nhận định hữu ích hơn, không chỉ dài/phức tạp hơn.
Truyền reason ngắn nêu tension và ích lợi mong đợi, không trình bày suy luận dài.
Không gọi Tật Ách mặc định, để đủ checklist hoặc tìm cách hợp thức hóa kết luận.
Chỉ cần một lần truy xuất bổ sung trong lần chạy.
Tool chỉ cung cấp chính tinh, trạng thái, Tuần/Triệt tại Tật Ách và nghĩa sao
chung. Chưa có nguồn diễn giải nội tâm chuyên biệt được duyệt: không xem nghĩa
sao chung là bằng chứng về tiềm thức. Không suy từ bệnh tật/tai ách sang tâm lý,
không chẩn đoán hoặc khẳng định động cơ vô thức. Thiếu căn cứ phù hợp thì bỏ qua,
giữ pattern nền và tension ở dạng mở, không cố giải thích mọi mâu thuẫn.
Nếu thực sự hữu ích, chỉ dùng để gợi một khả năng tự quan sát, có thể ở câu cuối;
không viết “sâu bên trong bạn thực ra…”, không tạo section riêng Thân/Tật Ách.
""".strip()


def build_personality_overview_agent_instruction() -> str:
    return "\n\n".join([
        PERSONALITY_OVERVIEW_REASONING_INSTRUCTION,
        *PERSONALITY_OVERVIEW_INPUT.instructions,
        PERSONALITY_OVERVIEW_OUTPUT.instruction,
    ])


def build_personality_overview_agent(model: str | Model) -> Agent:
    return Agent(
        model=model,
        name="personality_overview_agent",
        deps_type=TuviAgentDeps,
        # Same prompted JSON mode as strength_weakness (including Qwen support).
        output_type=PromptedOutput(PERSONALITY_OVERVIEW_OUTPUT.output_type),
        instructions=build_personality_overview_agent_instruction(),
        tools=[PERSONALITY_OVERVIEW_INPUT.tool, *PERSONALITY_OVERVIEW_INPUT.supporting_tools],
        tool_retries=2,
        output_retries=2,
    )


async def run_personality_overview_agent(
    *, agent: Agent, deps: TuviAgentDeps, request: str,
    usage: Any = None, message_history: Sequence[ModelMessage] | None = None,
) -> PersonalityOverview:
    result = await agent.run(
        request, deps=deps, usage=usage, message_history=message_history,
    )
    return result.output


async def run_personality_overview_workflow(
    *, agent: Agent, deps: TuviAgentDeps, request: str,
    usage: Any = None, message_history: Sequence[ModelMessage] | None = None,
) -> str:
    """Render one synthesis without a second model call; usable before chat wiring."""
    profile = await run_personality_overview_agent(
        agent=agent, deps=deps, request=request,
        usage=usage, message_history=message_history,
    )
    return render_personality_overview(profile)
