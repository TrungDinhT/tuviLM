from __future__ import annotations

import logging

from pydantic_ai import RunContext

from src.agent.ban_menh_meaning import (
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
    return build_laso_foundation_payload(ctx.deps.require_la_so())


def build_laso_foundation_payload(la_so: LaSo) -> dict[str, object]:
    """Return a plain payload derived from the existing refactored chart model."""
    prior = la_so.prior
    context = la_so.natal_context
    relation = la_so.menh_cuc_relation()
    ban_menh_meaning = build_ban_menh_meaning(la_so.ban_menh.id)
    menh_cuc_lens = build_menh_cuc_lens(
        la_so.ban_menh.ngu_hanh,
        context.cuc.ngu_hanh,
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
        "status": lens["status"],
        "environment_alignment": lens["environment_alignment"],
        "thinking_consistency": lens["thinking_consistency"],
        "action_style": lens["action_style"],
        "resilience_pattern": lens["resilience_pattern"],
        "development_focus": lens["development_focus"],
        "usage": list(_YEAR_MENH_POLARITY_USAGE),
        "scope_note": _YEAR_MENH_POLARITY_SCOPE_NOTE,
        "combination_note": _YEAR_MENH_POLARITY_COMBINATION_NOTE,
    }


_YEAR_MENH_POLARITY_USAGE: tuple[str, ...] = (
    "Đánh giá sơ bộ độ hòa hợp của cá nhân với môi trường sống và nơi sinh ra.",
    "Xét luồng tư duy thiên về nhất quán một dòng hay đa luồng, hay tự phản biện.",
    "Xem khuynh hướng phản ứng trước thuận cảnh hoặc nghịch cảnh.",
)

_YEAR_MENH_POLARITY_SCOPE_NOTE = (
    "Đây chỉ là dữ kiện nền tảng trong nhiều lớp của lá số; không dùng riêng "
    "nó để kết luận hoàn toàn tính cách."
)

_YEAR_MENH_POLARITY_COMBINATION_NOTE = (
    "Phải phối hợp thêm Mệnh/Thân, chính tinh, sát tinh và các cách cục tại "
    "cung Mệnh trước khi kết luận."
)

_YEAR_MENH_POLARITY_LENS: dict[str, dict[str, str]] = {
    "thuận lý": {
        "status": "Thuận Lý",
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
        "status": "Nghịch Lý",
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
