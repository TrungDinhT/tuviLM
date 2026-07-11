from types import SimpleNamespace

from src.agent.deps import TuviAgentDeps
from src.agent.skills import luan_tinh_cach_skill
from src.agent.tool.personality import (
    _sao_ban_menh_relation,
    get_tinh_cach_b3_b4_context,
)
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi, NguHanh
from src.refactored.model.prior import Gender, LaSoPrior


def test_luan_tinh_cach_skill_preserves_complete_b1_b6_workflow():
    skill = luan_tinh_cach_skill()

    assert "ngôn ngữ hiện đại" in skill
    assert "Tuần" in skill
    assert "Triệt" in skill
    assert "Hạt nhân 14 chính tinh" not in skill
    assert "read_luan_tinh_cach_b3_b4_knowledge" not in skill
    assert "get_laso_foundation" in skill
    assert "get_vong_thai_tue" in skill
    assert "get_tinh_cach_b3_b4_context" in skill
    assert "get_list_cach_cuc" in skill
    assert "get_phu_tinh_tam_phuong_tu_chinh" in skill
    assert "get_trang_sinh" in skill
    assert "Bản Mệnh là \"mình\"" in skill
    assert "Chính Phái, Khôn Ngoan, Đối Lập và Nhường Nhịn" in skill
    assert "nếu tuan_triet không rỗng" in skill
    assert "thai_tue_sat_tinh_at_menh" in skill
    assert "Tuyệt + Hỏa Tinh + Thất Sát" in skill
    assert "Hai chính tinh" in skill
    assert "Vô Chính Diệu" in skill
    assert "chính tinh > Tuần/Triệt > Tứ Hóa > phụ tinh > Tràng Sinh" in skill
    assert "không được đọc file knowledge" in skill
    for step in range(1, 7):
        assert f"## Bước {step}" in skill
    assert skill.count("## Nguyên tắc nguồn chung") == 1
    assert skill.count("## Cách viết") == 1
    assert "Skill luan_tinh_cach_b1_b2" not in skill
    assert "Skill luan_tinh_cach_b3_b4" not in skill


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
