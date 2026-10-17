"""Standalone synthesis agent; existing chat routing is intentionally unchanged."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic_ai import Agent, PromptedOutput, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.workflow.personality_overview.input import PERSONALITY_OVERVIEW_INPUT
from tuvi_agent.workflow.personality_overview.input.evidence import get_personality_overview_evidence
from tuvi_agent.workflow.personality_overview.output import (
    PERSONALITY_OVERVIEW_OUTPUT,
    PersonalityOverview,
    render_personality_overview,
)


PERSONALITY_OVERVIEW_REASONING_INSTRUCTION = """
Viết “Nét tính cách chủ đạo”: một chân dung thống nhất, có cơ chế và sắc
thái riêng để người dùng tự quan sát.
Tổng hợp A–E và viết trong cùng lượt sinh kết quả, không gọi model viết lại.
Mệnh–Thái Tuế–Thân–Tuần/Triệt là vai trò diễn giải của tuviLM, không chấm sức mạnh
sao hay khẳng định là quy tắc nguyên văn của một trường phái.

## Giới hạn chung
Chỉ dùng dữ kiện được cấp; không tự gán dữ kiện còn thiếu. Ưu tiên knowledge
và quy tắc được cấp. Không sử dụng Tật Ách trong Personality Overview.
Không dùng Tứ Hóa ngoài context: không tự thêm Tứ Hóa, phụ tá/sát tinh hoặc
những tương tác chưa được cung cấp. Thiếu knowledge thì dùng phần còn có căn cứ,
không biến sự thiếu dữ liệu thành đặc điểm con người.
Tử Vi là hệ diễn giải truyền thống, không phải đánh giá tâm lý học thực chứng;
có thể diễn giải thiên hướng và khả năng khi có căn cứ, không khẳng định mức độ
năng lực thực tế, thành quả, đạo đức hay số phận của người dùng.

## A. Mệnh — Khí chất nền
Chọn khí chất và cách vận hành chủ đạo từ menh.interpretation; có thể viết chân dung rõ dù trục chưa xác định.
Mệnh luôn có menh.xung_chieu và menh.tam_hop là dữ kiện tam phương tứ chính; sự hiện diện
của chúng không phải là cơ sở diễn giải, mà chỉ được sử dụng chủ yếu khi mệnh vô chính diệu (menh.interpretation là null).
Mệnh Vô Chính Diệu: chỉ tham khảo đối cung/tam hợp theo quy tắc VCD đã có; 
không bê nguyên bản ghi đối cung vào Mệnh, không gán sao chiếu
thành sao tọa Mệnh, không mặc định thụ động/thiếu bản sắc. Dữ kiện vị trí không
tự cung cấp ý nghĩa. Nếu thiếu tri thức nền VCD, nêu rõ giới hạn, không tạo một
khí chất giả. Quy tắc VCD về Tuần/Triệt nếu có và đủ điều kiện dùng ngay ở A,
không áp lại ở D.

## B. Thái Tuế — Cách ứng xử
group_meaning là nghĩa nhóm; star_meaning.expression và reading_hint là cách
biểu hiện riêng của sao tại Mệnh. Không gán tính riêng một sao cho cả nhóm,
suy nghĩa từ tên hoặc mặc định nhóm tốt/xấu.
Dùng thai_tue.knowledge để làm rõ lập trường, thái độ của khí chất Mệnh;
không thay thế Mệnh. Động lực Mệnh và tư thế Thái Tuế khác nhau có thể bổ sung nhau theo vai trò;
không viết hai chân dung rời rạc, không ép dung hòa nếu không có căn cứ.
Nếu gần nhau, hợp nhất thành một ý, không lặp hoặc nhân đôi độ chắc chắn

## C. Thân — Thể–Dụng
- than.application_context là bối cảnh Thân cư. basic_combination_id chỉ nhận
  diện tổ hợp theo hướng dẫn diễn giải theo Trung Châu phái; thiếu knowledge tổ hợp thì
  không tự tạo diễn giải tổ hợp từ mã này.
- Mệnh (Thể) là khí chất nền; Thân (Dụng) là phương thức đem khí chất vào lựa chọn, hành động,
  không phải một bản ngã độc lập. Chỉ giữ bối cảnh vận dụng có đóng góp cho chân dung.
- Thân cư Mệnh không đếm hai lần, không tự tăng mọi phẩm chất. Thân VCD không tạo khí chất từ khoảng trống; chỉ dùng
  vị trí cư và knowledge phù hợp nếu có. Không mở tam phương tứ chính Thân.
- Khác biệt Mệnh–Thân cần liên hệ động lực với phương thức vận dụng có nguồn;
  nếu chưa thể dung hòa thì giữ khác biệt có điều kiện

## D. Tuần/Triệt — Điều kiện bộc lộ
- Sau khi tổng hợp A–C, đọc tuan_triet theo đúng layer menh/than,
  role và position và kiểm tra xem Tuần/Triệt có tạo điều kiện làm thay đổi cách biểu hiện các khuynh hướng đó hay không.
  Tuần/Triệt chỉ điều chỉnh cách bộc lộ, không tạo tính cách mới.
- Được vận dụng kiến thức Tử Vi để suy luận ảnh hưởng từ placements và bối cảnh
  đã có. applicable_constraints rỗng không có nghĩa là không có ảnh hưởng;
  đây là các quy tắc bổ sung nếu được cung cấp, không phải điều kiện cho phép luận.
- Tuần/Triệt tại Thân chỉ xét cách vận dụng ở Thân, không tự suy yếu toàn bộ
  Mệnh. Mệnh–Thân cùng cung hoặc quy tắc VCD đã dùng ở A thì không áp hai lần.
  Không kéo ảnh hưởng từ cung khác vào toàn bộ chân dung.
- Không mặc định Triệt làm chính tinh mất tác dụng, Tuần gây thiếu quyết đoán,
  không đảo cực trục, biến mạnh thành yếu hoặc phủ định toàn bộ kết luận Mệnh.
  Không nhắc tên Tuần/Triệt trong luận giải.

## E. Tổng hợp
Giữ khí chất Mệnh làm trọng tâm, các lớp sau bổ sung theo vai trò B–D; không
viết hai chân dung rời rạc hoặc lần lượt kể từng nguồn.
Các khuynh hướng cùng hiện diện không tự chứng minh quan hệ nhân quả hay trình
tự trước–sau; chỉ liên hệ như vậy khi nguồn hỗ trợ. Khi có khác biệt, giữ đúng
điều kiện thay vì sáng tác động cơ hoặc ép dung hòa.
Chọn một hoặc hai biểu hiện, một mặt còn lại có căn cứ và một quan sát giúp
người dùng tự hiểu mình; viết theo hướng dẫn đầu ra.
""".strip()


def build_personality_overview_agent_instruction() -> str:
    return "\n\n".join([
        PERSONALITY_OVERVIEW_REASONING_INSTRUCTION,
        *PERSONALITY_OVERVIEW_INPUT.instructions,
        PERSONALITY_OVERVIEW_OUTPUT.instruction,
    ])


def build_personality_overview_agent(
    model: str | Model, *, model_settings: ModelSettings | None = None,
) -> Agent:
    agent = Agent(
        model=model,
        model_settings=model_settings,
        name="personality_overview_agent",
        deps_type=TuviAgentDeps,
        # Same prompted JSON mode as strength_weakness (including Qwen support).
        output_type=PromptedOutput(PERSONALITY_OVERVIEW_OUTPUT.output_type),
        instructions=build_personality_overview_agent_instruction(),
        output_retries=2,
    )

    @agent.instructions
    def evidence_context(ctx: RunContext[TuviAgentDeps]) -> str:
        return get_personality_overview_evidence(ctx).model_dump_json()

    return agent


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
