from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from tuvi_agent.deps import TuviAgentDeps
from tuvi_agent.skills import get_cung_analyze_skill, read_book_tuvi_tan_bien
from tuvi_agent.tool.ban_menh.laso_foundation import get_laso_foundation
from tuvi_agent.tool.book import read_catalog, read_section
from tuvi_agent.tool.cach_cuc.tool import get_list_cach_cuc
from tuvi_agent.tool.chart import (
    get_cung_by_position,
    get_cung_by_role,
    get_tam_hop,
    get_xung_chieu,
)
from tuvi_agent.tool.guidance import get_role_instruction
from tuvi_agent.tool.personality import get_tinh_cach_b3_b4_context
from tuvi_agent.tool.phu_tinh.tool import (
    get_phu_tinh_tam_phuong_tu_chinh,
    get_trang_sinh,
)
from tuvi_agent.tool.thai_tue.vong_thai_tue import get_vong_thai_tue
from tuvi_agent.workflow.personality.input.tanbien import get_personality_evidence
from tuvi_engine.components.definitions.cung_role import Role
from tuvi_engine.la_so import LaSo
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


BOOK_ROOT = Path("data/tuvitanbien_chunking_compact/part_2")


@pytest.mark.skipif(not BOOK_ROOT.is_dir(), reason=f"book files are missing: {BOOK_ROOT}")
def test_agent_tools_log_start_and_compact_completion_metadata(caplog):
    caplog.set_level(logging.INFO, logger="tuvi_agent")
    la_so = LaSo.from_prior(FIXTURE_PRIOR_A)
    deps = TuviAgentDeps(
        la_so=la_so,
        book_root=BOOK_ROOT,
    )
    ctx = SimpleNamespace(deps=deps)
    menh_position = la_so.tinh_ban.menh_position

    get_laso_foundation(ctx)
    get_vong_thai_tue(ctx)
    get_cung_by_position(ctx, menh_position)
    get_cung_by_role(ctx, Role.MENH)
    get_tam_hop(ctx, menh_position)
    get_xung_chieu(ctx, menh_position)
    get_list_cach_cuc(ctx, filtered_roles=[Role.MENH])
    get_phu_tinh_tam_phuong_tu_chinh(ctx, Role.MENH)
    get_trang_sinh(ctx, Role.MENH)
    get_tinh_cach_b3_b4_context(ctx)
    read_catalog(ctx, depth=1)
    read_section(ctx, "4.2.11")
    get_role_instruction("menh")
    get_cung_analyze_skill()
    read_book_tuvi_tan_bien()
    get_personality_evidence(ctx)

    expected_messages = (
        "Đã lấy gốc lá số",
        "Đã lấy vòng Thái Tuế",
        "Đã lấy cung theo vị trí",
        "Đã lấy cung theo vai trò",
        "Đã lấy cung tam hợp",
        "Đã lấy cung xung chiếu",
        "Đã gom phụ tinh theo nhóm",
        "Đã lấy Tràng Sinh",
        "Đã lấy context chính tinh tính cách",
        "Đã đọc catalog sách",
        "Đã đọc mục sách",
        "Đã lấy hướng dẫn luận cung",
        "Đã lấy skill phân tích cung",
        "Đã lấy skill đọc sách Tử Vi Tân Biên",
        "Tool get_personality_evidence hoàn tất",
    )
    for message in expected_messages:
        assert message in caplog.text
