from types import SimpleNamespace

from src.agent.deps import TuviAgentDeps
from src.agent.tool.personality import (
    _sao_ban_menh_relation,
    get_tinh_cach_b3_b4_context,
)
from src.agent.workflow.personality.input.tanbien import luan_tinh_cach_skill
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi, NguHanh
from src.refactored.model.prior import Gender, LaSoPrior


def test_luan_tinh_cach_skill_only_keeps_non_redundant_reasoning_rules():
    skill = luan_tinh_cach_skill()

    assert "không tính lại quan hệ ngũ hành" in skill
    assert "hai chính tinh" in skill
    assert "miếu/vượng" in skill
    assert "Tuần" in skill
    assert "Triệt" in skill
    assert "Lục Cát" in skill
    assert "Tứ Hóa" in skill
    assert "Tuyệt + Hỏa Tinh + Thất Sát" in skill
    assert "priority cao nhất" in skill
    assert "động cơ, cách quyết định" in skill

    assert "## Bước" not in skill
    assert "B1" not in skill
    assert "B2" not in skill
    assert "B3" not in skill
    assert "B4" not in skill
    assert "B5" not in skill
    assert "B6" not in skill
    assert "get_laso_foundation" not in skill
    assert "get_vong_thai_tue" not in skill
    assert "environment_alignment" not in skill
    assert "reading_hint" not in skill
    assert "technical_support" not in skill
    assert "Chính Phái" not in skill
    assert "Vô Chính Diệu" not in skill


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
