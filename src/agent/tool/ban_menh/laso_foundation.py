from __future__ import annotations

import logging

from pydantic_ai import RunContext

from src.agent.tool.ban_menh.ban_menh_meaning import (
    build_ban_menh_meaning,
    build_menh_cuc_lens,
)
from src.agent.deps import TuviAgentDeps
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import (
    DiaChi,
    LuongNghi,
)


_logger = logging.getLogger(__name__)


def get_laso_foundation(ctx: RunContext[TuviAgentDeps]) -> dict[str, object]:
    """Lấy phần gốc của lá số trước khi luận chi tiết.

    Tool này trả về ba nền tảng cần xét trước khi luận một lá số: Âm/Dương
    thuận-nghịch giữa năm sinh và cung Mệnh, Bản Mệnh theo hành, và quan hệ
    sinh-khắc giữa Mệnh với Cục.

    Dùng tool này trước khi luận tổng quan lá số, luận cung Mệnh, hoặc khi cần
    cân nhắc nền mạnh/yếu của toàn cục. Payload chỉ tập trung vào ba điểm:
    Âm/Dương thuận-nghịch, Bản Mệnh theo hành và quan hệ sinh-khắc Mệnh-Cục.
    Không dùng tool này thay thế cho get_list_cach_cuc hay get_cung_by_role;
    nó chỉ là lớp nền để định khung luận giải.
    """
    _logger.info("Lấy gốc lá số")
    result = build_laso_foundation_payload(ctx.deps.require_la_so())
    _logger.info(
        "Đã lấy gốc lá số: am_duong=%s, ban_menh=%s, menh_cuc=%s",
        result["am_duong_thuan_nghich"]["relation"],
        result["ban_menh"]["name"],
        result["menh_cuc_relation"]["relation"],
    )
    return result


def build_laso_foundation_payload(la_so: LaSo) -> dict[str, object]:
    """Return a plain payload derived from the existing refactored chart model."""
    prior = la_so.prior
    context = la_so.natal_context
    relation = la_so.menh_cuc_relation()
    ban_menh_meaning = build_ban_menh_meaning(la_so.ban_menh.id)
    menh_cuc_lens = build_menh_cuc_lens(
        relation.relation_type,
    )
    year_menh_polarity_relation = _year_menh_polarity_relation(
        prior.dia_chi,
        context.menh_position,
    )

    return {
        "am_duong_thuan_nghich": {
            "relation": year_menh_polarity_relation,
            **_year_menh_polarity_lens(year_menh_polarity_relation),
        },
        "ban_menh": {
            "id": la_so.ban_menh.id,
            "name": la_so.ban_menh.name,
            "ngu_hanh": la_so.ban_menh.ngu_hanh.value,
            "meaning": ban_menh_meaning,
        },
        "cuc": {
            "name": context.cuc.name,
            "ngu_hanh": context.cuc.ngu_hanh.value,
        },
        "menh_cuc_relation": menh_cuc_lens,
    }


def _am_duong_of_dia_chi(dia_chi: DiaChi) -> LuongNghi:
    return LuongNghi(dia_chi.index % 2)


def _year_menh_polarity_relation(
    natal_year_dia_chi: DiaChi,
    menh_position: DiaChi,
) -> str:
    if _am_duong_of_dia_chi(natal_year_dia_chi) is _am_duong_of_dia_chi(menh_position):
        return "thuận lý"
    return "nghịch lý"


def _year_menh_polarity_lens(relation: str) -> dict[str, object]:
    lens = _YEAR_MENH_POLARITY_LENS[relation]
    return {
        "environment_alignment": lens["environment_alignment"],
        "thinking_consistency": lens["thinking_consistency"],
        "action_style": lens["action_style"],
        "resilience_pattern": lens["resilience_pattern"],
        "development_focus": lens["development_focus"],
    }


_YEAR_MENH_POLARITY_LENS: dict[str, dict[str, str]] = {
    "thuận lý": {
        "environment_alignment": (
            "Hòa hợp cao với không gian sống nơi sinh ra; thường hợp lập nghiệp "
            "và phát triển tại quê hương hoặc môi trường gốc."
        ),
        "thinking_consistency": (
            "Tư tưởng thường có một dòng mạch lạc, xu hướng nói được làm được, "
            "ít đổi ý giữa chừng."
        ),
        "action_style": (
            "Quyết liệt, bộc trực, coi trọng đúng sai và muốn làm chủ hướng đi "
            "của mình."
        ),
        "resilience_pattern": (
            "Thường có đà tiến thuận hơn; khi gặp khó cần xem thêm sao tại "
            "Mệnh/Thân để biết lực chịu va đập."
        ),
        "development_focus": (
            "Rèn cách sống đúng đắn và tiết chế sự quyết liệt để không gây tổn "
            "hại cho xung quanh."
        ),
    },
    "nghịch lý": {
        "environment_alignment": (
            "Lệch pha với bối cảnh ban đầu; cá tính hoặc tư tưởng dễ cảm thấy "
            "không đồng điệu với môi trường xung quanh."
        ),
        "thinking_consistency": (
            "Tư duy thường đa luồng, hay suy nghĩ lại và tự phản biện để tìm "
            "cách giải quyết nhẹ nhàng hơn."
        ),
        "action_style": (
            "Uyển chuyển, cân nhắc, ưu tiên tìm sự đồng thuận thay vì chỉ tranh "
            "luận đúng sai."
        ),
        "resilience_pattern": (
            "Bối cảnh đầu đời có thể không thuận, nhưng dễ rèn được độ bền bỉ "
            "và sức vượt khó cao."
        ),
        "development_focus": (
            "Rèn dĩ hòa vi quý, hàm dưỡng bản thân và xử lý bất hòa giữa người "
            "với người."
        ),
    },
}
