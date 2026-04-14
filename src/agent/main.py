from __future__ import annotations

from pydantic_ai import Agent, RunContext

from src.agent.deps import TuviAgentDeps
from src.tuvi.cung import Cung
from src.tuvi.element.types import TYPE_DIA_CHI
from src.tuvi.tinh_ban import TinhBan
from src.retrieval.search.tool import search_role_info, search_start_info


DEFAULT_MODEL = "gpt-4.1-mini"

TUVI_AGENT_INSTRUCTION = """
Bạn là trợ lý Tử Vi cho ứng dụng xem Tử Vi.
Nhiệm vụ của bạn là phân tích lá số Tử Vi dựa trên thông tin về tinh bàn (TinhBan) được cung cấp qua các tool.
TinhBan bao gồm 12 cung, mỗi cung có một vị trí (địa chi) và một vai trò (Mệnh, Phụ Mẫu, Quan Lộc,...), cùng với các sao chính tinh, phụ tinh, tứ hóa và trạng thái của chúng.
Bạn sẽ sử dụng thông tin này để trả lời các câu hỏi liên quan đến lá số Tử Vi, giải thích ý nghĩa của các sao, cung, và mối quan hệ giữa chúng.

Khi được yêu cầu luận một vấn đề cụ thể, hãy tưởng tượng mối liên hệ giữa cung và sao trong tinh bàn, dựa trên kiến thức về Tử Vi để đưa ra phân tích chi tiết.
Khi không biết thông tin, hãy tìm kiếm, đừng đoán. Ví dụng
Sử dung get_cung_by_position hoặc get_cung_by_role để lấy thông tin chi tiết của một cung cụ thể nào đó khi cần, thay vì lấy toàn bộ tinh bàn.
Sử dụng get_role_info để tìm kiếm thông tin về vai trò cung, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc.
Sử dụng get_star_info để tìm kiếm thông tin về sao, ví dụ: Tử Vi, Thiên Phủ.

Chỉ trả lời dựa trên dữ liệu lấy từ các tool này.
"""


def build_tuvi_agent(model: str = DEFAULT_MODEL) -> Agent:
    agent = Agent(
        model=model,
        deps_type=TuviAgentDeps,
        output_type=str,
        system_prompt=TUVI_AGENT_INSTRUCTION,
        retries=2,
    )

    @agent.tool
    def get_tinh_ban(ctx: RunContext[TuviAgentDeps]) -> TinhBan:
        """Lấy toàn bộ cấu trúc TinhBan hiện có trong deps."""
        return ctx.deps.require_tinh_ban()

    @agent.tool
    def get_cung_by_position(
        ctx: RunContext[TuviAgentDeps],
        position: TYPE_DIA_CHI
    ) -> Cung:
        """Lấy cung theo vị trí địa chi, ví dụ: Tý, Sửu, Dần."""
        return ctx.deps.get_cung_by_position(position)

    @agent.tool
    def get_cung_by_role(
        ctx: RunContext[TuviAgentDeps],
        role: str
    ) -> Cung:
        """Lấy cung theo vai trò, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
        return ctx.deps.get_cung_by_role(role)

    @agent.tool
    def get_role_info(ctx: RunContext[TuviAgentDeps], role: str) -> str:
        """Tìm kiếm thông tin về vai trò cung, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
        raw_info = search_role_info(role=role)
        if raw_info:
            return "\n".join(f"{item['title']}: {item['content']}" for item in raw_info)
        return "Không tìm thấy thông tin về vai trò này."

    @agent.tool
    def get_star_info(ctx: RunContext[TuviAgentDeps], query: str) -> str:
        """Tìm kiếm thông tin về sao, ví dụ: Tử Vi, Thiên Phủ."""
        _logger.info(f"Tìm kiếm thông tin về sao: {query}")
        raw_info = search_star_info(name=query)
        if raw_info:
            return "\n".join(f"{item['title']}: {item['content']}" for item in raw_info)
        return "Không tìm thấy thông tin về sao này."

    return agent


async def run_tuvi_agent(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    agent = ctx.deps.require_agent()
    result = await agent.run(request, deps=ctx.deps, usage=ctx.usage)
    return result.output
