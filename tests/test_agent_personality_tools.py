from types import SimpleNamespace

from src.agent.deps import TuviAgentDeps
from src.agent.skills import luan_tinh_cach_b1_b2, luan_tinh_cach_b3_b4
from src.agent.tool.personality import (
    _sao_ban_menh_relation,
    get_tinh_cach_b3_b4_context,
)
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi, NguHanh
from src.refactored.model.prior import Gender, LaSoPrior


def test_luan_tinh_cach_b3_b4_embeds_distilled_knowledge_without_file_tool():
    skill = luan_tinh_cach_b3_b4()

    assert "trục hiện đại" in skill
    assert "Cô đọng" in skill
    assert "Tuần" in skill
    assert "Triệt" in skill
    assert "Hạt nhân 14 chính tinh" not in skill
    assert "read_luan_tinh_cach_b3_b4_knowledge" not in skill


def test_luan_tinh_cach_b1_b2_orchestrates_foundation_and_thai_tue_tools():
    skill = luan_tinh_cach_b1_b2()

    assert "get_laso_foundation" in skill
    assert "get_vong_thai_tue" in skill
    assert "Bản Mệnh là \"mình\"" in skill
    assert "Chính Phái, Khôn Ngoan, Đối Lập và Nhường Nhịn" in skill
    assert "nếu tuan_triet không rỗng" in skill
    assert "thai_tue_sat_tinh_at_menh" in skill
    assert "không được đọc file knowledge" in skill


def test_get_tinh_cach_b3_b4_context_runs_on_laso():
    la_so = LaSo.from_prior(
        LaSoPrior(
            hour=DiaChi.MEO,
            date=10,
            month=11,
            year=1996,
            gender=Gender.MALE,
        )
    )

    content = get_tinh_cach_b3_b4_context(SimpleNamespace(deps=TuviAgentDeps(la_so=la_so)))

    assert "Bản Mệnh:" in content
    assert "Cung Mệnh:" in content
    assert "Chính tinh Mệnh" in content
    assert "Chính tinh xung chiếu Mệnh:" in content
    assert "Chính tinh tam hợp Mệnh:" in content
    assert "Tuần/Triệt tại các cung liên quan:" in content
    assert "Cung xung chiếu Mệnh:" in content


def test_sao_ban_menh_relation_uses_direction():
    assert _sao_ban_menh_relation(NguHanh.KIM, NguHanh.THUY).startswith("sao sinh")
    assert _sao_ban_menh_relation(NguHanh.THUY, NguHanh.KIM).startswith("Bản Mệnh sinh")
