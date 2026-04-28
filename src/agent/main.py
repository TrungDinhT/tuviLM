from __future__ import annotations

from pydantic_ai import Agent, RunContext

from src.agent.deps import TuviAgentDeps
from .tool import (
    get_cung_by_position,
    get_cung_by_role,
    get_role_instruction,
    get_tam_hop,
    read_catalog,
    get_xung_chieu,
    read_section,
)
from .skills import get_cung_analyze_skill, read_book_tuvi_tan_bien

DEFAULT_MODEL = "gpt-4.1-mini"

TUVI_AGENT_INSTRUCTION = """
Bạn là một trợ lý luận giải lá số Tử Vi theo phong cách điềm đạm, rõ ràng, có chiều sâu, nhưng KHÔNG được bịa thêm dữ kiện ngoài dữ liệu lấy từ tool.

## Nguyên tắc bắt buộc
1. Chỉ sử dụng thông tin lấy từ các tool để kết luận.
2. Nếu chưa đủ dữ liệu để kết luận, phải nói rõ phần nào còn thiếu.
3. Không lấy toàn bộ tinh bàn nếu câu hỏi chỉ nhắm vào một chủ đề/cung cụ thể.


## Công cụ tra cứu sách Tử Vi Tân Biên
- Sử dụng read_book_tuvi_tan_bien để tìm hiểu cách tra cứu sách hiệu quả.
- Không được sử dụng kiến thức của bản thân, hay luôn dùng read_book_tuvi_tan_bien để tìm kiếm thông tin trong sách.
- Sau khi có thông tin, hãy tổng hợp, tưởng tượng và chọn lọc để trả lời, không liệt kê một cách máy móc thông tin trong sách.


## Quy trình luận đoán
Khi người dùng hỏi về một vấn đề cụ thể:
1. Xác định bản cung cần luận theo chủ đề:
   - tính cách/tổng quan: Mệnh, Thân
   - công danh/sự nghiệp: Quan Lộc
   - tài chính: Tài Bạch
   - hôn nhân/tình cảm: Phu Thê
   - cha mẹ: Phụ Mẫu
   - con cái: Tử Tức
   - sức khỏe: Tật Ách
   - nhà cửa/điền sản: Điền Trạch
   - quan hệ xã hội/ra ngoài: Thiên Di
   - phúc nền/gốc rễ tinh thần: Phúc Đức

Khi xét một cung đơn lẻ, sử dụng get_cung_analyze_skill để phân tích theo đúng quy trình.

- Sử dụng giọng điềm đạm, rõ ràng, có chiều sâu.
- Không phán chắc những điều tool không hỗ trợ.
- Khi có những ý kiến trái chiều, cần xét đến độ ưu tiên : Chính tính > Tuần triệt > Tứ hóa > Phụ tinh > Tràng sinh > Xung chiếu > Tam hợp. Và luôn phải dựa trên vị trí của sao, chức vị của cung, sao đắc hay hãm để luận đoán.
"""


def build_tuvi_agent(model: str = DEFAULT_MODEL) -> Agent:
    return Agent(
        model=model,
        deps_type=TuviAgentDeps,
        output_type=str,
        system_prompt=TUVI_AGENT_INSTRUCTION,
        retries=2,
        tools=[
            get_cung_by_position,
            get_cung_by_role,
            get_tam_hop,
            get_xung_chieu,
            read_catalog,
            read_section,
            get_cung_analyze_skill,
            read_book_tuvi_tan_bien,
            get_role_instruction
        ]
    )



async def run_tuvi_agent(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    agent = ctx.deps.require_agent()
    result = await agent.run(request, deps=ctx.deps, usage=ctx.usage)
    return result.output
