"""Tử Vi Tân Biên evidence contract for the personality workflow."""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.ban_menh.laso_foundation import build_laso_foundation_payload
from src.agent.tool.cach_cuc.matcher import get_cach_cuc_tool_results
from src.agent.tool.cach_cuc.models import CachCucToolResult
from src.agent.tool.personality import build_tinh_cach_b3_b4_context
from src.agent.tool.phu_tinh.tool import (
    PhuTinhGroupedResult,
    TrangSinhResult,
    build_phu_tinh_tam_phuong_tu_chinh,
    build_trang_sinh,
)
from src.agent.tool.thai_tue.vong_thai_tue import build_vong_thai_tue_payload
from src.refactored.components.definitions.cung_role import Role
from src.refactored.la_so import LaSo


_logger = logging.getLogger(__name__)


class AmDuongEvidence(BaseModel):
    relation: str
    environment_alignment: str
    thinking_consistency: str
    action_style: str
    resilience_pattern: str
    development_focus: str


class BanMenhEvidence(BaseModel):
    id: str
    name: str
    ngu_hanh: str


class CucEvidence(BaseModel):
    name: str
    ngu_hanh: str


class MenhCucEvidence(BaseModel):
    relation: str
    meaning: str


class FoundationEvidence(BaseModel):
    am_duong_thuan_nghich: AmDuongEvidence
    ban_menh: BanMenhEvidence
    cuc: CucEvidence
    menh_cuc_relation: MenhCucEvidence


class ComponentEvidence(BaseModel):
    id: str
    name: str
    ngu_hanh: str | None = None


class ThaiTueGroupEvidence(BaseModel):
    id: str
    name: str
    archetype: str
    overview: str
    reading_lens: str
    trap: str


class ThaiTueStarMeaningEvidence(BaseModel):
    keywords: list[str]
    at_menh: str
    shadow: str
    reading_hint: str


class ThaiTueMenhEvidence(BaseModel):
    position: ComponentEvidence
    thai_tue_star: ComponentEvidence
    group: ThaiTueGroupEvidence
    star_meaning: ThaiTueStarMeaningEvidence


class ThienMaLensEvidence(BaseModel):
    element: str
    will_style: str


class ThienMaEvidence(BaseModel):
    available: bool
    reason: str | None = None
    star: ComponentEvidence | None = None
    position: ComponentEvidence | None = None
    at_menh: bool | None = None
    lens: ThienMaLensEvidence | None = None
    tuan_triet: list[ComponentEvidence] = Field(default_factory=list)


class SatTinhEvidence(BaseModel):
    stars: list[ComponentEvidence]


class ThaiTueTechnicalEvidence(BaseModel):
    ego_and_collaboration_note: str | None = None
    thien_ma: ThienMaEvidence | None = None
    thai_tue_sat_tinh_at_menh: SatTinhEvidence | None = None


class VongThaiTueEvidence(BaseModel):
    menh: ThaiTueMenhEvidence
    technical_support: ThaiTueTechnicalEvidence


class PersonalityEvidence(BaseModel):
    """Complete deterministic Tân Biên evidence for personality synthesis."""

    model_config = ConfigDict(extra="forbid")

    foundation: FoundationEvidence
    vong_thai_tue: VongThaiTueEvidence
    b3_b4_context: str
    cach_cuc: list[CachCucToolResult]
    phu_tinh: PhuTinhGroupedResult
    trang_sinh_menh: TrangSinhResult
    trang_sinh_than: TrangSinhResult


def luan_tinh_cach_skill() -> str:
    """Return only reasoning rules that are not already encoded in the evidence."""

    return """## Quy tắc suy luận bổ sung cho evidence Tân Biên

Các trường diễn giải trong evidence đã chứa sẵn ý nghĩa của chính chúng. Dùng
trực tiếp nội dung đó; không tính lại quan hệ ngũ hành, không suy diễn từ tên
nhóm và không biến keywords thành kết luận độc lập.

### Xác định lõi và các lớp điều chỉnh

- Chính tinh tại Mệnh là lõi vận hành. Nếu có hai chính tinh, xác định sao nào
  định mục tiêu, sao nào định cách làm, chúng hỗ trợ hay giằng co và khi áp lực
  thì xu hướng nào lấn át. Không cộng hai danh sách tính từ.
- Trạng thái sao điều chỉnh khả năng biểu hiện: miếu/vượng là mạnh và chủ động;
  đắc là có chỗ phát huy; bình là không nổi trội hoặc thiếu nhất quán; hãm là
  khó dùng mặt xây dựng và dễ thành cơ chế phòng vệ.
- Tuần thiên về bao, giữ, trì hoãn, tự giới hạn hoặc làm đường phát triển vòng
  vèo. Triệt thiên về cắt, chặn, gây gãy khúc và buộc đổi cách biểu hiện. Chúng
  không đảo tốt thành xấu hay xấu thành tốt; phải xác định phẩm chất nào bị
  giảm, bị chặn, được kiềm hoặc phải đổi đường biểu hiện.
- Cách cục có priority cao nhất là khung cấu trúc chính; cách thấp hơn chỉ bổ
  trợ. Chỉ dùng cách cục đã có trong evidence, không tự dựng cách mới từ sao.

### Các dữ kiện chỉ có tên hoặc trạng thái

- Lục Cát là lớp trợ lực; Lục Sát là lớp áp lực và biến động. Phải xét cả hai,
  không dùng một phía để xóa phía còn lại.
- Với Tứ Hóa: Lộc tăng thuận lợi hoặc sức hút; Quyền tăng chủ động hoặc kiểm
  soát; Khoa tăng học hỏi hoặc uy tín; Kỵ tạo vướng mắc hoặc nút thắt.
- Tứ Linh bổ sung tài hoa và phong thái; Tam Minh bổ sung sức hút, giao tế và
  sắc thái tình cảm. Đắc/miếu/vượng nghiêng về biểu hiện xây dựng, hãm nghiêng
  về khó vận hành.
- Sao đồng cung tác động trực tiếp hơn sao xung chiếu hoặc tam hợp.
- Tràng Sinh có trọng số thấp nhất. Chỉ dùng khi tạo tổ hợp có nghĩa với Mệnh
  hoặc Thân, chẳng hạn Tuyệt + Hỏa Tinh + Thất Sát, Thiên Mã + Trường Sinh,
  hoặc Mộ + Phá Quân tại Tứ Mộ; nếu không có tổ hợp thì bỏ qua.

### Tổng hợp

- Khi dữ kiện xung đột, ưu tiên chính tinh, rồi Tuần/Triệt, Tứ Hóa, phụ tinh và
  cuối cùng là Tràng Sinh; dùng cách cục priority cao để tổ chức toàn bộ khung.
- Tìm cả chứng cứ xác nhận và phản chứng. Giữ khác biệt hợp lý thành các lớp
  nền khí, hành vi quan sát được và xu hướng khi trưởng thành thay vì ép thành
  một nhãn duy nhất.
- Chuyển ý nghĩa Tử Vi sang các trục: động cơ, cách quyết định, tự kiểm soát,
  phản ứng dưới áp lực, quan hệ, khả năng thích nghi và nguồn phục hồi. Không
  dùng nhãn cổ nặng định kiến làm kết luận trực tiếp.
"""


def collect_personality_evidence(la_so: LaSo) -> PersonalityEvidence:
    """Collect Tân Biên evidence without model-selected tool calls."""
    _logger.info("Thu thập evidence tính cách Tân Biên")
    evidence = PersonalityEvidence(
        foundation=FoundationEvidence.model_validate(
            build_laso_foundation_payload(la_so)
        ),
        vong_thai_tue=VongThaiTueEvidence.model_validate(
            build_vong_thai_tue_payload(la_so)
        ),
        b3_b4_context=build_tinh_cach_b3_b4_context(la_so),
        cach_cuc=get_cach_cuc_tool_results(la_so, filtered_roles=[Role.MENH]),
        phu_tinh=build_phu_tinh_tam_phuong_tu_chinh(la_so, Role.MENH),
        trang_sinh_menh=build_trang_sinh(la_so, Role.MENH),
        trang_sinh_than=build_trang_sinh(la_so, Role.CUNG_THAN),
    )
    _logger.info(
        "Đã thu thập evidence tính cách Tân Biên: cach_cuc=%d, phu_tinh=%d, "
        "trang_sinh_menh=%s, trang_sinh_than=%s",
        len(evidence.cach_cuc),
        sum(len(group.stars) for group in evidence.phu_tinh.groups)
        + len(evidence.phu_tinh.khac),
        evidence.trang_sinh_menh.star,
        evidence.trang_sinh_than.star,
    )
    return evidence


def get_personality_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> PersonalityEvidence:
    """Thu thập đầy đủ evidence Tân Biên cho một lần luận độc lập.

    Luôn gọi tool này trước khi luận nếu prompt chưa cung cấp sẵn evidence.
    """
    _logger.info("Tool get_personality_evidence bắt đầu")
    result = collect_personality_evidence(ctx.deps.require_la_so())
    _logger.info("Tool get_personality_evidence hoàn tất")
    return result
