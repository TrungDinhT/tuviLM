"""Default factual input contract for strength/weakness assessment."""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict
from pydantic_ai import RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.strength_weakness import (
    CungStructureEvidence,
    PhuTinhTuanTrietEvidence,
    PhuTinhTuanTrietKind,
    TinhHeEvidence,
    TuHoaEvidence,
    build_menh_than_evidence,
    build_menh_than_phu_tinh_tuan_triet,
    build_tinh_he_evidence,
    build_tu_hoa_evidence,
)

_logger = logging.getLogger(__name__)


class StrengthWeaknessEvidence(BaseModel):
    """Only the natal evidence consumed by this workflow's primary pass."""

    model_config = ConfigDict(extra="ignore")

    menh_than: list[CungStructureEvidence]
    tinh_he: list[TinhHeEvidence]
    tu_hoa: list[TuHoaEvidence]
    phu_tinh_tuan_triet: list[PhuTinhTuanTrietEvidence]
    sao_can_tra_cuu: list[str]


STRENGTH_WEAKNESS_REASONING_INSTRUCTION = """
## Phạm vi đánh giá

Bạn đánh giá điểm mạnh, điểm yếu và hướng phát triển của những năng lực chung,
không dự đoán may rủi, giàu nghèo, chức vụ, nghề nghiệp, thi cử, gia đình hay
thành công khách quan. Score ability, not outcome and not virtue.

Mười một dimension và ranh giới của chúng:

1. `analysis_reasoning`: phân rã, đối chiếu và suy luận từ thông tin đã có.
2. `learning_absorption`: tiếp nhận điều mới và cập nhật hiểu biết.
3. `foresight_preparedness`: thấy hệ quả tiếp theo, risk và phương án dự phòng.
4. `decision_making`: cân trade-off và chốt lựa chọn khi thông tin chưa đủ.
5. `action_execution`: chuyển lựa chọn thành hành động, momentum và output cụ
   thể. Không đồng nhất với kiên trì dài hạn hoặc giữ mãi một mục tiêu.
6. `structuring_organization`: tổ chức thông tin, dependency, tài nguyên và quy
   trình; không cần có người khác.
7. `expression_persuasion`: diễn đạt, giải thích, lập luận và thuyết phục.
8. `adaptability`: đổi cách vận hành khi hoàn cảnh hoặc feedback thay đổi.
9. `creativity_new_approaches`: tạo possibility hoặc cách tiếp cận chưa có sẵn.
10. `collaboration_coordination`: phối hợp ngang với người mình không kiểm soát.
11. `leadership_mobilization`: đặt hướng và khiến tập thể cùng hành động.

## Cách dùng evidence

- Luôn đọc cấu trúc Mệnh và Thân như hai nguồn riêng. Nếu đồng cung, chúng vẫn
  là hai nguồn reinforcement độc lập theo contract sản phẩm.
- `tinh_he` chỉ là tên của một cấu trúc chính tinh đã được detector xác nhận;
  nó không phải kết luận sẵn về năng lực và không được ưu tiên mặc định hơn
  các sao thực tế trong Mệnh/Thân. `pham_vi` là phạm vi hẹp nhất đủ tạo tinh hệ:
  đồng cung, tam phương, rồi tam phương tứ chính.
- Một tinh hệ và các chính tinh cấu thành nó thuộc cùng một evidence family;
  không tính tên tinh hệ và từng sao thành các xác nhận độc lập. Các tinh hệ
  overlap nhiều sao cũng không tự động là các reinforcement độc lập.
- Không dùng hierarchy mặc định đặt tinh hệ hoặc chính tinh cao hơn phụ tinh.
  Chính tinh dựng khung vận hành; phụ tinh có thể đổi sắc thái, nhịp độ, cách
  biểu hiện, điều kiện phát huy hoặc mâu thuẫn bên trong của chính khung đó.
- `phu_tinh_tuan_triet` là facts chứ không phải modifier số học. Đọc từng phụ
  tinh như một tín hiệu có nghĩa riêng; tự quyết định nó cộng hưởng, chuyển
  hướng, kìm, kích hoạt hay tạo hai mặt khi đi cùng toàn bộ bộ sao.
- Tứ Hóa được lấy trên toàn lá số. Vị trí cung quyết định độ liên quan nhưng
  không phải lý do loại cứng. Không coi Lộc/Khoa là cộng điểm hoặc Kỵ là trừ
  điểm. Đọc Hóa cùng sao được Hóa và tinh hệ liên quan.

Sau khi nhận primary evidence và trước khi chọn score:

- Bắt buộc gọi `search_star_info` cho toàn bộ `sao_can_tra_cuu`; khử trùng tên
  và chia nhiều lần gọi nếu quá giới hạn của tool. Danh sách này đã gồm chính
  tinh Mệnh/Thân, toàn bộ phụ tinh trực tiếp và sao được Hóa; không chỉ gồm sao
  thuộc một tinh hệ đã match.
- Tự giữ checklist các tên đã tra. Một tên chỉ được coi là hoàn tất khi nó xuất
  hiện trong `requested_star_names` của kết quả tool; nếu nằm trong `not_found`
  thì ghi nhận là sách chưa có thông tin và tuyệt đối không tự bịa ý nghĩa.
  Trước output, đối chiếu checklist với `sao_can_tra_cuu` và gọi tiếp các batch
  còn thiếu.
- Dùng ý nghĩa sách như nguyên liệu semantic: cách tiếp nhận và xử lý thông
  tin, nhịp phản ứng, kiểu tạo cấu trúc, mức chủ động, quan hệ với bất định,
  cách biểu đạt và cách phối hợp. Bỏ outcome cổ như phú quý, chức nghiệp, gia
  đình, sức khỏe, thọ yểu hoặc may rủi.
- Tổng hợp theo bộ sao và bối cảnh Mệnh/Thân, không ánh xạ từng sao sang một
  dimension rồi cộng `+1`, `+2` hay trừ điểm. Một sao có thể đồng thời tạo khả
  năng và trade-off; ý nghĩa cuối phụ thuộc sao đi cùng, trạng thái, Tứ Hóa và
  cung chứa nó.
- Chỉ dùng `get_star_role_interaction` khi ý nghĩa chung chưa đủ để hiểu một
  sao ở đúng cung thực tế. Không cần gọi tool này cho mọi sao.

Completion gate: nếu chưa tra đủ `sao_can_tra_cuu`, hoặc mới chỉ đọc tên tinh
hệ mà chưa đọc ý nghĩa chính tinh và phụ tinh cấu thành bộ sao, chưa được chấm
level và chưa được trả structured output.

Lăng kính hai mặt cho Tứ Hóa:

- Lộc: sức hút, hứng thú và động lực; quá mức có thể chạy theo phần thưởng.
- Quyền: agency, quyết đoán và kiểm soát; quá mức có thể áp đặt hoặc nóng vội.
- Khoa: học hỏi, phương pháp và tinh chỉnh; quá mức có thể trí thức hóa và chậm
  hành động.
- Kỵ: ma sát, chiều sâu và bám vấn đề; quá mức có thể thành cố định hoặc rumination.

Tên tinh hệ chỉ giúp nhận ra một motif cần kiểm tra. Không dùng bảng mapping cố
định từ tinh hệ sang dimension; phải quay lại ý nghĩa của các chính tinh và phụ
tinh thực có trong evidence rồi diễn giải motif ở mức trừu tượng. Không dùng
kiến thức về sao không có trong evidence.

Chỉ gọi `get_strength_weakness_cung_bo_sung` khi Phúc Đức hoặc Nô Bộc có thể
materially change một judgment đang có tín hiệu từ Mệnh/Thân. Không gọi context
chỉ để ép score rời NORMAL. Tật Ách chỉ được bổ sung `tradeoff`; evidence từ Tật
Ách tuyệt đối không được thay đổi score hoặc score basis.

## Quy tắc chấm hoàn toàn bằng reasoning của model

- Python tools không chấm điểm. Chính bạn phải tổng hợp toàn bộ evidence.
- Chọn level sau khi đã tổng hợp gestalt của bộ sao; NORMAL là một kết luận có
  nghĩa, không phải điểm xuất phát số học để cộng/trừ.
- Thiếu evidence không phải evidence của weakness.
- Chỉ rời NORMAL khi có evidence khẳng định trực tiếp cho chính dimension đó.
- `EXCELLENT`, `NEARLY_ABSENT`, `VERY_GOOD` và `VERY_WEAK` là các vùng cực;
  dùng thận trọng và cần evidence family thực sự độc lập cùng hội tụ.
- Shadow của một strength không tự động hạ strength. Ghi shadow vào trade-off.
- Chỉ dùng `NEARLY_ABSENT`/`VERY_WEAK`/`WEAK` khi evidence trực tiếp cho thấy
  năng lực bị hạn chế. `IMPROVABLE` cần đồng thời thấy nền năng lực và lý do nó
  chưa biểu hiện ổn định; không dùng như nhãn mặc định cho evidence mơ hồ.
- Nếu constructive và limiting evidence mạnh, độc lập và cân nhau, giữ NORMAL,
  đặt basis `balanced_conflict`, và bắt buộc giải thích contrast đó.
- NORMAL thật sự có evidence ở vùng giữa dùng `supported`; NORMAL vì không đủ
  evidence dùng `insufficient_evidence`.
""".strip()


def get_strength_weakness_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> StrengthWeaknessEvidence:
    """Build the complete primary evidence contract exactly once."""
    _logger.info("Tool get_strength_weakness_evidence bắt đầu")
    la_so = ctx.deps.require_la_so()
    menh_than = build_menh_than_evidence(la_so)
    tinh_he = build_tinh_he_evidence(la_so)
    tu_hoa = build_tu_hoa_evidence(
        la_so,
        tinh_he=tinh_he,
    )
    phu_tinh_tuan_triet = build_menh_than_phu_tinh_tuan_triet(la_so)
    sao_can_tra_cuu = list(
        dict.fromkeys(
            [sao.ten for item in menh_than for sao in item.chinh_tinh]
            + [
                item.ten
                for item in phu_tinh_tuan_triet
                if item.loai is PhuTinhTuanTrietKind.PHU_TINH
            ]
            + [item.sao_duoc_hoa for item in tu_hoa]
        )
    )
    evidence = StrengthWeaknessEvidence(
        menh_than=menh_than,
        tinh_he=tinh_he,
        tu_hoa=tu_hoa,
        phu_tinh_tuan_triet=phu_tinh_tuan_triet,
        sao_can_tra_cuu=sao_can_tra_cuu,
    )
    _logger.info(
        "Tool get_strength_weakness_evidence hoàn tất: tinh_he=%d "
        "phu_tinh_tuan_triet=%d",
        len(evidence.tinh_he),
        len(evidence.phu_tinh_tuan_triet),
    )
    return evidence
