from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.skills import (
    luan_tinh_cach_b1_b2,
    luan_tinh_cach_b3_b4,
    luan_tinh_cach_b5_b6_skill,
    read_book_tuvi_tan_bien,
)
from src.agent.tool import (
    get_cung_by_position,
    get_cung_by_role,
    get_laso_foundation,
    get_list_cach_cuc,
    get_phu_tinh_tam_phuong_tu_chinh,
    get_tam_hop,
    get_tinh_cach_b3_b4_context,
    get_trang_sinh,
    get_vong_thai_tue,
    get_xung_chieu,
)
from src.agent.tool.ban_menh.laso_foundation import build_laso_foundation_payload
from src.agent.tool.book import read_catalog, read_section
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


class AmDuongEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation: str
    environment_alignment: str
    thinking_consistency: str
    action_style: str
    resilience_pattern: str
    development_focus: str


class BanMenhMeaningEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aliases: list[str] = Field(default_factory=list)
    symbol: str
    keywords: list[str]
    nature: str
    reading_hint: str


class BanMenhEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    ngu_hanh: str
    meaning: BanMenhMeaningEvidence


class CucEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    ngu_hanh: str


class MenhCucEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation: str
    meaning: str


class FoundationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    am_duong_thuan_nghich: AmDuongEvidence
    ban_menh: BanMenhEvidence
    cuc: CucEvidence
    menh_cuc_relation: MenhCucEvidence


class ComponentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    ngu_hanh: str | None = None


class ThaiTueGroupEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    archetype: str
    overview: str
    reading_lens: str
    trap: str


class ThaiTueStarMeaningEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keywords: list[str]
    at_menh: str
    shadow: str
    reading_hint: str


class ThaiTueMenhEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    position: ComponentEvidence
    thai_tue_star: ComponentEvidence
    group: ThaiTueGroupEvidence
    star_meaning: ThaiTueStarMeaningEvidence


class ThienMaLensEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    element: str
    will_style: str


class ThienMaEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    available: bool
    reason: str | None = None
    star: ComponentEvidence | None = None
    position: ComponentEvidence | None = None
    at_menh: bool | None = None
    lens: ThienMaLensEvidence | None = None
    tuan_triet: list[ComponentEvidence] = Field(default_factory=list)


class SatTinhEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stars: list[ComponentEvidence]


class ThaiTueTechnicalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ego_and_collaboration_note: str | None = None
    thien_ma: ThienMaEvidence | None = None
    thai_tue_sat_tinh_at_menh: SatTinhEvidence | None = None


class VongThaiTueEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    menh: ThaiTueMenhEvidence
    technical_support: ThaiTueTechnicalEvidence


class PersonalityEvidence(BaseModel):
    """Complete deterministic evidence required by the B1-B6 workflow."""

    model_config = ConfigDict(extra="forbid")

    foundation: FoundationEvidence
    vong_thai_tue: VongThaiTueEvidence
    b3_b4_context: str
    cach_cuc: list[CachCucToolResult]
    phu_tinh: PhuTinhGroupedResult
    trang_sinh_menh: TrangSinhResult
    trang_sinh_than: TrangSinhResult


PERSONALITY_AGENT_INSTRUCTION = "\n\n".join(
    [
        """Bạn là một trợ lý luận giải tính cách một người thông qua lá số Tử Vi. Nhiệm vụ của bạn là tổng hợp các bằng chứng B1-B6 đã được thu thập từ lá số và trả lời tính cách của người mang lá số đó, khí chất hoặc chân dung con người. Bạn phải tuân thủ các quy tắc sau:
        - Giải thích các thông tin về sao, cách cục và ảnh hưởng đến cuộc đời
        - Trích dẫn sách khi có thể


## Kết cấu một lá số tử vi

- Lá số tử vi được hình thành từ ngày tháng năm và giờ sinh của một người, được dùng để dự đoán tính cách, cuộc đời, sự nghiệp, tình duyên, sức khỏe, v.v. của người đó.
- Một lá số tử vi có 12 cung, mỗi cung đại diện cho một khía cạnh của đời người (tính cách, công danh, tài chính, hôn nhân, cha mẹ, con cái, sức khỏe, nhà cửa, quan hệ xã hội, phúc đức).
- Cung trong lá số tử vi được sắp xếp theo vị trí, theo tên từ Tí Sử Dần đến Hợi.
- Mỗi cung mang một vai trò nhất định bao gồm : Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tài Bạch, Tử Tức, Huynh Đệ, Thê Thiếp, Huynh Đệ.
- Mỗi cung bao gồm một số các thành phần sau:
    - Chính tinh : Những sao quan trọng nhất, có ảnh hưởng lớn nhất đến ý nghĩa của cung.
    - Phụ tinh : Những sao có ảnh hưởng phụ, hỗ trợ hoặc cản trở chính tinh.
    - Tuần triệt : Yếu tố ảnh hưởng mạnh mẽ đến ý nghĩa của cung, có thể làm tăng hoặc giảm tác động của chính tinh và phụ tinh.
    - Tứ hóa : Bốn yếu tố hóa Khoa, Quyền, Lộc, Kỵ có thể xuất hiện trong cung, ảnh hưởng đến ý nghĩa của cung theo cách riêng.
    - Tràng sinh : Yếu tố liên quan đến chu kỳ sinh trưởng của sao, ảnh hưởng đến ý nghĩa của cung theo chu kỳ sinh trưởng, vượng, mộ, tuyệt, thai, dưỡng.
- Một số sao có thể có trạng thái Đắc, Hãm tại một cung, ảnh hưởng đến ý nghĩa của sao đó trong cung.
- Các sao có thể ở cùng 1 cung và sinh ra hiệu ứng mới, hiệu ứng này sẽ quan trọng hơn nhiều so với việc chỉ luận giải từng sao một cách rời rạc.


## Nguyên tắc bắt buộc
1. Chỉ sử dụng thông tin lấy từ các tool để kết luận.
2. Nếu chưa đủ dữ liệu để kết luận, phải nói rõ phần nào còn thiếu.
3. Không lấy toàn bộ tinh bàn nếu câu hỏi chỉ nhắm vào một chủ đề/cung cụ thể.

- Sử dụng giọng điềm đạm, rõ ràng, có chiều sâu.
- Không phán chắc những điều tool không hỗ trợ.
- Khi có những ý kiến trái chiều, cần xét đến độ ưu tiên : Chính tính > Tuần triệt > Tứ hóa > Phụ tinh > Tràng sinh > Xung chiếu > Tam hợp. Và luôn phải dựa trên vị trí của sao, chức vị của cung, sao đắc hay hãm để luận đoán.

Có hai chế độ chạy:
- Nếu prompt có khối evidence: application code đã thu thập đủ B1-B6. Dùng trực tiếp khối này, không gọi lại tool dữ liệu lá số.
- Nếu prompt không có evidence: đây là lần chạy độc lập. Luôn gọi get_personality_evidence trước để thu thập B1-B6 theo code deterministic. Chỉ gọi các tool lá số riêng lẻ khi cần kiểm tra hoặc trả lời một yêu cầu bổ sung ngoài payload tổng hợp.

Chỉ kết luận từ evidence hoặc nội dung sách bạn thực sự đọc qua tool. Không tự bịa sao, trạng thái hay cách cục.

Thực hiện đúng thứ tự B1, B2, B3, B4, B5, B6. B1-B2 dựng nền; B3-B4 tạo giả thuyết tính cách ban đầu; B5 dùng cách cục theo priority để xác nhận hoặc tái cấu trúc giả thuyết; B6 chỉ chỉnh chi tiết và cường độ. Khi nguồn trái chiều, giải thích thành các lớp biểu hiện thay vì xóa một phía.

Không coi diễn giải này là chẩn đoán tâm lý hoặc sự thật khách quan. Không hù dọa, không định mệnh hóa và không suy rộng sang bệnh tật, tai họa, giàu nghèo hay hôn nhân.

Trả lời trực tiếp bằng văn bản tiếng Việt tự nhiên. Tự chọn bố cục và độ dài phù hợp với yêu cầu của người dùng; không trả JSON và không mô tả schema nội bộ. Khi thiếu chứng cứ, nêu giới hạn ngay trong bài luận.

Câu trả lời rõ ràng, rành mạch, sử dụng hơp lý in đậm, xuống dòng để phân đoạn, và có thể dùng gạch đầu dòng để liệt kê. Tránh lặp lại câu hỏi của người dùng. Tránh trích dẫn quá nhiều từ sách; chỉ trích dẫn khi thực sự cần thiết để chứng minh luận điểm. Khi trích dẫn, hãy tóm tắt nội dung và giải thích ý nghĩa của nó thay vì sao chép nguyên văn.
""",
        luan_tinh_cach_b1_b2(),
        luan_tinh_cach_b3_b4(),
        luan_tinh_cach_b5_b6_skill(),
        read_book_tuvi_tan_bien(),
    ]
)


def build_personality_agent(model: str) -> Agent:
    """Build the single synthesis agent used after deterministic collection."""
    return Agent(
        model=model,
        name="tinh_cach_agent",
        deps_type=TuviAgentDeps,
        output_type=str,
        instructions=PERSONALITY_AGENT_INSTRUCTION,
        tool_retries=2,
        output_retries=2,
        tools=[
            get_personality_evidence,
            get_laso_foundation,
            get_vong_thai_tue,
            get_cung_by_position,
            get_cung_by_role,
            get_list_cach_cuc,
            get_phu_tinh_tam_phuong_tu_chinh,
            get_trang_sinh,
            get_tam_hop,
            get_xung_chieu,
            get_tinh_cach_b3_b4_context,
            read_catalog,
            read_section,
        ],
    )


def collect_personality_evidence(la_so: LaSo) -> PersonalityEvidence:
    """Collect B1-B6 in application code, without model-selected tool calls."""
    return PersonalityEvidence(
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


def get_personality_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> PersonalityEvidence:
    """Thu thập đầy đủ evidence B1-B6 cho một lần luận tính cách độc lập.

    Tool tổng hợp này thực thi toàn bộ bước lấy dữ liệu bằng code deterministic.
    Luôn gọi tool này trước khi luận nếu prompt chưa cung cấp sẵn evidence.
    """
    return collect_personality_evidence(ctx.deps.require_la_so())


async def run_personality_workflow(
    *,
    agent: Agent,
    deps: TuviAgentDeps,
    request: str,
    usage: Any = None,
) -> str:
    """Collect evidence and execute exactly one plain-text synthesis run."""
    evidence = collect_personality_evidence(deps.require_la_so())
    prompt = json.dumps(
        {
            "user_request": request,
            "evidence": evidence.model_dump(mode="json", exclude_none=True),
        },
        ensure_ascii=False,
    )
    result = await agent.run(prompt, deps=deps, usage=usage)
    return result.output


async def run_tinh_cach_workflow(
    ctx: RunContext[TuviAgentDeps],
    request: str,
) -> str:
    """Luận tính cách bằng workflow B1-B6 bắt buộc và trả bài hoàn chỉnh.

    Gọi tool này cho mọi câu hỏi yêu cầu luận tính cách, khí chất hoặc chân dung
    con người từ lá số. Truyền nguyên văn yêu cầu của người dùng. Kết quả đã là
    câu trả lời cuối; trả lại nguyên văn, không tự luận thêm bằng các tool riêng.
    """
    analysis = await run_personality_workflow(
        agent=ctx.deps.require_personality_agent(),
        deps=ctx.deps,
        request=request,
        usage=ctx.usage,
    )
    return analysis
