from __future__ import annotations
import logging

from pydantic_ai import Agent, ModelRetry, RunContext

from src.agent.book_index import (
    ListSectionsResult,
    SearchSectionsResult,
    SectionContent,
    SectionMeta,
)
from src.agent.deps import TuviAgentDeps
from src.tuvi.cung import Cung
from src.tuvi.element.star_registry import STAR_NAME
from src.tuvi.element.types import LIST_DIA_CHI, ROLE_TYPE, TYPE_DIA_CHI
from src.tuvi.tinh_ban import TinhBan
from src.retrieval.search.tool import search_role_info, search_star_info

_logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4.1-mini"

TUVI_AGENT_INSTRUCTION = """
Bạn là một trợ lý luận giải lá số Tử Vi theo phong cách điềm đạm, rõ ràng, có chiều sâu, nhưng KHÔNG được bịa thêm dữ kiện ngoài dữ liệu lấy từ tool.

## Nguyên tắc bắt buộc
1. Chỉ sử dụng thông tin lấy từ các tool để kết luận.
2. Nếu chưa đủ dữ liệu để kết luận, phải nói rõ phần nào còn thiếu.
3. Không khẳng định tuyệt đối ở những điểm còn tranh luận giữa các trường phái.
4. Không lấy toàn bộ tinh bàn nếu câu hỏi chỉ nhắm vào một chủ đề/cung cụ thể.
5. Khi cần tra cứu sách Tử Vi Tân Biên theo mục/chương, ưu tiên search_sections trước,
   sau đó dùng get_section/list_sections để kiểm tra ngữ cảnh, cuối cùng mới dùng read_section
   để đọc nội dung mục phù hợp.

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

2. Lấy dữ liệu của bản cung bằng get_cung_by_role hoặc get_cung_by_position.

3. Luôn lấy thêm:
   - cung xung chiếu bằng get_xung_chieu
   - 2 cung tam hợp bằng get_tam_hop
   - thông tin vai trò cung bằng get_role_info khi cần


4. Với từng sao quan trọng xuất hiện trong bản cung, xung chiếu, tam hợp:
   - dùng get_star_info để lấy nghĩa sao
   - ưu tiên đọc chính tinh trước, rồi mới tới phụ tinh/tuần triệt/tứ hóa/tràng sinh/

5. Khi phân tích một cung, luôn đánh giá theo thứ tự:
   - bản chất cung đang hỏi
   - chính tinh tọa thủ hoặc hội chiếu
   - độ mạnh/yếu và sự hỗ trợ hay cản trở của các sao
   - ảnh hưởng của xung chiếu và tam hợp
   - kết luận tổng hợp, không tách rời từng sao một cách máy móc

6. Nếu cung vô chính diệu hoặc có dấu hiệu đặc biệt như Tuần/Triệt, phải nêu rõ đây là trường hợp cần dựa mạnh vào hội chiếu/tam hợp/xung chiếu và giảm độ chắc chắn của kết luận.

7. Nếu người dùng hỏi về vận theo thời gian (năm nay, giai đoạn này, đại vận...), chỉ kết luận khi có dữ liệu hạn tương ứng. Nếu không có tool về hạn, phải nói rõ giới hạn này.

## Cách trả lời
- Trả lời theo cấu trúc:
  1. Xác định cung trọng tâm
  2. Dữ kiện chính từ bản cung
  3. Ảnh hưởng từ tam hợp và xung chiếu
  4. Tổng hợp ý nghĩa
  5. Kết luận ngắn gọn, bám dữ liệu
- Không dùng giọng quá thần bí.
- Không phán chắc những điều tool không hỗ trợ.
- Khi có nhiều dấu hiệu trái chiều, phải nêu rõ điểm nâng đỡ và điểm cản trở.
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
        _logger.info(f"Lấy cung theo vị trí: {position}")
        return ctx.deps.get_cung_by_position(position)

    @agent.tool
    def get_cung_by_role(
        ctx: RunContext[TuviAgentDeps],
        role: ROLE_TYPE
    ) -> Cung:
        """Lấy cung theo vai trò, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
        _logger.info(f"Lấy cung theo vai trò: {role}")
        return ctx.deps.get_cung_by_role(role)

    @agent.tool
    def get_role_info(ctx: RunContext[TuviAgentDeps], role: ROLE_TYPE) -> str:
        """Tìm kiếm thông tin về vai trò cung, ví dụ: Mệnh, Phụ Mẫu, Quan Lộc."""
        _logger.info(f"Tìm kiếm thông tin về cung: {role}")
        raw_info = search_role_info(role=role)
        if raw_info:
            return "\n".join(f"{item['title']}: {item['content']}" for item in raw_info)
        return "Không tìm thấy thông tin về vai trò này."

    @agent.tool
    def get_star_info(ctx: RunContext[TuviAgentDeps], query: STAR_NAME) -> str: # type: ignore
        """Tìm kiếm thông tin về sao, ví dụ: Tử Vi, Thiên Phủ."""
        _logger.info(f"Tìm kiếm thông tin về sao: {query}")
        raw_info = search_star_info(name=query)
        if raw_info:
            return "\n".join(f"{item['title']}: {item['content']}" for item in raw_info)
        return "Không tìm thấy thông tin về sao này."

    @agent.tool
    def list_sections(
        ctx: RunContext[TuviAgentDeps],
        parent_id: str | None = None,
        part_id: str | None = None,
    ) -> ListSectionsResult:
        """
        List immediate child sections in the structured book.

        Use parent_id=None to list top-level sections. If the book has multiple
        parts, pass part_id such as "part_2", or pass parent_id="part_2" as a
        shortcut. Returned ids are canonical ids that can be used by get_section
        and read_section.
        """
        _logger.info(f"Liệt kê mục sách: parent_id={parent_id}, part_id={part_id}")
        try:
            book = ctx.deps.require_book()
            sections = book.list_sections(parent_id=parent_id, part_id=part_id)
            return ListSectionsResult(
                sections=[book.get_meta(section.id) for section in sections]
            )
        except ValueError as exc:
            raise ModelRetry(str(exc)) from exc

    @agent.tool
    def get_section(ctx: RunContext[TuviAgentDeps], section_id: str) -> SectionMeta:
        """
        Get metadata for one book section, including breadcrumb, summary, parent,
        and immediate children.

        Section ids may be canonical like "part_2/1.1". If a default part exists,
        local ids such as "1.1" also work for that part.
        """
        _logger.info(f"Lấy metadata mục sách: {section_id}")
        try:
            return ctx.deps.require_book().get_meta(section_id)
        except ValueError as exc:
            raise ModelRetry(str(exc)) from exc

    @agent.tool
    def read_section(
        ctx: RunContext[TuviAgentDeps],
        section_id: str,
        include_children: bool = False,
        max_chars: int | None = 8000,
    ) -> SectionContent:
        """
        Read the content of one book section.

        Set include_children=True to append immediate child subsection content.
        Use max_chars to keep long sections bounded.
        """
        _logger.info(
            "Đọc mục sách: section_id=%s, include_children=%s, max_chars=%s",
            section_id,
            include_children,
            max_chars,
        )
        try:
            return ctx.deps.require_book().read_section(
                section_id,
                include_children=include_children,
                max_chars=max_chars,
            )
        except ValueError as exc:
            raise ModelRetry(str(exc)) from exc

    @agent.tool
    def search_sections(
        ctx: RunContext[TuviAgentDeps],
        query: str,
        top_k: int = 5,
    ) -> SearchSectionsResult:
        """
        Search section ids, titles, summaries, and partial content in the book.

        This is the best first tool when the user asks about a doctrine, rule,
        star combination, or section title from Tử Vi Tân Biên.
        """
        bounded_top_k = max(1, min(top_k, 20))
        _logger.info(f"Tìm kiếm mục sách: query={query}, top_k={bounded_top_k}")
        return SearchSectionsResult(
            hits=ctx.deps.require_book().search_sections(query, top_k=bounded_top_k)
        )

    @agent.tool
    def get_tam_hop(
        ctx: RunContext[TuviAgentDeps],
        position: TYPE_DIA_CHI
    ) -> TYPE_DIA_CHI:
        """Lấy cung tam hợp của một cung cụ thể."""
        index = LIST_DIA_CHI.index(position)
        tam_hop_index = ((index + 4) % 12, (index + 8) % 12)
        tam_hop_position = (LIST_DIA_CHI[tam_hop_index[0]], LIST_DIA_CHI[tam_hop_index[1]])
        return f"Cung tam hợp của {position} là {tam_hop_position}."


    @agent.tool
    def get_xung_chieu(
        ctx: RunContext[TuviAgentDeps],
        position: TYPE_DIA_CHI
    ) -> TYPE_DIA_CHI:
        """Lấy cung xung chiếu của một cung cụ thể."""
        index = LIST_DIA_CHI.index(position)
        xung_chieu_index = (index + 6) % 12
        xung_chieu_position = LIST_DIA_CHI[xung_chieu_index]
        return f"Cung xung chiếu của {position} là {xung_chieu_position}."

    return agent


async def run_tuvi_agent(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    agent = ctx.deps.require_agent()
    result = await agent.run(request, deps=ctx.deps, usage=ctx.usage)
    return result.output
