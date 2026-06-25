from __future__ import annotations
import logging

from pydantic_ai import RunContext

from src.agent.cach_cuc.matcher import get_cach_cuc_tool_results
from src.agent.cach_cuc.models import CachCucToolResult, Role, SourceKind
from src.agent.deps import TuviAgentDeps

_logger = logging.getLogger(__name__)


def get_list_cach_cuc(
    ctx: RunContext[TuviAgentDeps],
    source_kind: SourceKind = SourceKind.TUVITANBIEN,
    filtered_roles: list[Role] | None = None,
) -> list[CachCucToolResult]:
    """Lấy các cách cục đang ứng với lá số hiện tại.

    Dùng tool này khi cần kiểm tra riêng các cách cục xuất hiện trong lá số,
    không dùng để đọc toàn bộ tinh bàn hay phân tích một cung.

    source_kind hiện chỉ hỗ trợ "tuvitanbien".

    filtered_roles là danh sách role id như menh, quan_loc, tai_bach.
    Chỉ truyền filtered_roles khi muốn nhắm vào một hoặc vài cung cụ thể, ví dụ
    khi người dùng đang hỏi về Mệnh, Quan Lộc, Tài Bạch. Khi có filtered_roles,
    tool trả về các cách cục có related_to thuộc các role đó, đồng thời vẫn giữ
    các cách cục tổng quát có related_to = None. Nếu người dùng không nhắm vào
    một cung cụ thể, không truyền filtered_roles để lấy tất cả cách cục.

    Kết quả chỉ gồm id, tên, ý nghĩa, trang, priority và related_to; không trả
    về điều kiện nội bộ.
    """
    _logger.info(
        "Lấy danh sách cách cục: source_kind=%s, filtered_roles=%s",
        source_kind,
        filtered_roles,
    )
    return get_cach_cuc_tool_results(
        ctx.deps.require_la_so(),
        source_kind=source_kind,
        filtered_roles=filtered_roles,
    )
