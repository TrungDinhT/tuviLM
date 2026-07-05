from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TypedDict

from pydantic_ai import RunContext

from src.agent.deps import TuviAgentDeps
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.placement.registry import ComponentId


_logger = logging.getLogger(__name__)


THAI_TUE_RING_STAR_IDS: tuple[ComponentId, ...] = (
    "thai_tue",
    "thieu_duong",
    "tang_mon",
    "thieu_am",
    "quan_phuf",
    "tu_phu",
    "tue_pha",
    "long_duc",
    "bach_ho",
    "sao_phuc_duc",
    "dieu_khach",
    "truc_phu",
)


@dataclass(frozen=True)
class ThaiTueGroupMeaning:
    """Static interpretation for one three-star group in the Thái Tuế ring."""

    id: str
    name: str
    archetype: str
    star_ids: tuple[ComponentId, ...]
    overview: str
    reading_lens: str
    trap: str

    def as_payload(self) -> dict[str, object]:
        """Return an agent-facing JSON-safe representation of the group."""
        return {
            "id": self.id,
            "name": self.name,
            "archetype": self.archetype,
            "star_ids": list(self.star_ids),
            "overview": self.overview,
            "reading_lens": self.reading_lens,
            "trap": self.trap,
        }


@dataclass(frozen=True)
class ThaiTueStarMeaning:
    """Static interpretation for a single Thái Tuế ring star at Mệnh."""

    id: ComponentId
    group_id: str
    keywords: tuple[str, ...]
    at_menh: str
    shadow: str
    reading_hint: str

    def as_payload(self) -> dict[str, object]:
        """Return an agent-facing JSON-safe representation of the star."""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "keywords": list(self.keywords),
            "at_menh": self.at_menh,
            "shadow": self.shadow,
            "reading_hint": self.reading_hint,
        }


class TuanTrietMarkerPayload(TypedDict):
    """Compact marker summary for Tuần/Triệt at a position."""

    markers: list[dict[str, object]]
    has_tuan: bool
    has_triet: bool


def get_vong_thai_tue(ctx: RunContext[TuviAgentDeps]) -> dict[str, object]:
    """Lấy dữ kiện luận vòng Thái Tuế tại cung Mệnh.

    Tool này xác định sao nào trong 12 sao vòng Thái Tuế đang tọa thủ cung
    Mệnh, sau đó trả về nhóm tư cách, biến thể sao tại Mệnh và dữ kiện bổ trợ
    khi thật sự liên quan. Thiên Mã chỉ được xét khi Mệnh thuộc Nhóm Đối Lập:
    Tuế Phá, Tang Môn, Điếu Khách; Tuần/Triệt chỉ xuất hiện như dữ kiện phụ
    của Thiên Mã; sát tinh chỉ xuất hiện khi Thái Tuế thủ Mệnh gặp
    Không/Kiếp/Hỏa/Linh.

    Dùng tool này khi luận tư cách, khí chất sống, thái độ trước đời, cách dùng
    nghị lực hoặc khi người dùng hỏi trực tiếp về vòng Thái Tuế. Không dùng
    riêng tool này để kết luận toàn bộ số phận; cần phối hợp thêm Cung Mệnh,
    tam phương tứ chính, Lộc Tồn, Trường Sinh và các cách cục khác.
    """
    _logger.info("Lấy vòng Thái Tuế tại Mệnh")
    return build_vong_thai_tue_payload(ctx.deps.require_la_so())


def build_vong_thai_tue_payload(la_so: LaSo) -> dict[str, object]:
    """Build the full Thái Tuế reading payload for the chart's Mệnh palace.

    The chart model already places all natal stars. This function only reads
    the natal Mệnh palace, identifies the one Thái Tuế-ring star there, and
    expands it into group meaning plus narrowly scoped technical support.
    """
    menh_position = la_so.tinh_ban.menh_position
    menh_components = la_so.tinh_ban.layer(NATAL_LAYER_ID).components_at(menh_position)
    star_id = _thai_tue_star_at_menh(menh_components)
    star_meaning = _THAI_TUE_STAR_MEANINGS[star_id]
    group = _THAI_TUE_GROUP_MEANINGS[star_meaning.group_id]
    technical_support = {
        "ego_and_collaboration_note": _ego_payload(star_id, group.id),
    }
    reading_steps = [
        "Xác định sao vòng Thái Tuế tọa thủ Mệnh trước, rồi mới mở rộng sang tam phương tứ chính.",
        "Luận theo nhóm tư cách của sao thủ Mệnh, sau đó dùng biến thể từng sao để chỉnh sắc thái.",
    ]

    if group.id == "doi_lap":
        technical_support["thien_ma"] = _thien_ma_payload(la_so, menh_position)
        reading_steps.append(
            "Với Nhóm Đối Lập, dùng Thiên Mã để đọc nghị lực và xem Tuần/Triệt tại vị trí Thiên Mã nếu có."
        )

    if _thai_tue_meets_sat_tinh(star_id, menh_components):
        technical_support["thai_tue_sat_tinh_at_menh"] = _thai_tue_sat_tinh_payload(
            la_so,
            menh_components,
        )
        reading_steps.append(
            "Khi Thái Tuế thủ Mệnh gặp Không/Kiếp/Hỏa/Linh, đọc theo bài học rèn tâm để không bị sát khí kéo lệch."
        )

    reading_steps.append(
        "Không dùng vòng Thái Tuế một mình để kết luận giàu nghèo, nghề nghiệp, bệnh tật, hôn nhân hoặc vận hạn."
    )

    return {
        "scope": _scope_payload(),
        "menh": {
            "position": _dia_chi_payload(la_so, menh_position),
            "thai_tue_star": _component_payload(la_so, star_id),
            "group": group.as_payload(),
            "star_meaning": star_meaning.as_payload(),
        },
        "ring_positions": _ring_positions_payload(la_so, menh_position),
        "technical_support": technical_support,
        "reading_steps": reading_steps,
    }


def _scope_payload() -> dict[str, object]:
    """Describe what this tool is allowed to conclude and what it must not replace."""
    return {
        "name": "Vòng Thái Tuế",
        "method": (
            "Xác định sao nào trong 12 sao vòng Thái Tuế đang tọa thủ cung "
            "Mệnh: Thái Tuế, Thiếu Dương, Tang Môn, Thiếu Âm, Quan Phù, "
            "Tử Phù, Tuế Phá, Long Đức, Bạch Hổ, Phúc Đức, Điếu Khách, "
            "Trực Phù."
        ),
        "system_context": (
            "Vòng Thái Tuế là lớp định vị tư cách và thái độ nhập thế. Khi "
            "luận sâu về thành tựu, cách kiếm tiền hoặc sức khỏe, cần phối "
            "hợp thêm hai vòng còn lại trong Tam Luân là Lộc Tồn và Trường Sinh."
        ),
        "ring_order": list(THAI_TUE_RING_STAR_IDS),
        "scope_note": (
            "Payload này phục vụ luận tư cách tại Mệnh. Nó không thay thế dữ "
            "liệu cung Mệnh, chính tinh, sát tinh, tứ hóa, Tuần/Triệt, tam hợp "
            "và xung chiếu."
        ),
    }


def _thai_tue_star_at_menh(menh_components: frozenset[ComponentId]) -> ComponentId:
    """Return the Thái Tuế-ring star present in Mệnh components.

    A valid natal chart should contain exactly one star from the ring at each
    palace. Iterating by the canonical ring order keeps the result stable even
    though the input component collection is a set.
    """
    for star_id in THAI_TUE_RING_STAR_IDS:
        if star_id in menh_components:
            return star_id
    raise ValueError("Không tìm thấy sao vòng Thái Tuế tại cung Mệnh.")


def _ring_positions_payload(
    la_so: LaSo,
    menh_position: DiaChi,
) -> list[dict[str, object]]:
    """Return all natal positions of the Thái Tuế ring and mark the Mệnh one."""
    positions: list[dict[str, object]] = []
    for star_id in THAI_TUE_RING_STAR_IDS:
        position = la_so.position_of(star_id)
        if position is None:
            continue
        positions.append(
            {
                "star": _component_payload(la_so, star_id),
                "position": _dia_chi_payload(la_so, position),
                "is_menh": position == menh_position,
            }
        )
    return positions


def _thai_tue_meets_sat_tinh(
    thai_tue_star_id: ComponentId,
    menh_components: frozenset[ComponentId],
) -> bool:
    """Return true only when Thái Tuế thủ Mệnh is with key sát tinh at Mệnh."""
    return thai_tue_star_id == "thai_tue" and bool(
        set(_THAI_TUE_SAT_TINH_IDS) & menh_components
    )


def _thien_ma_payload(
    la_so: LaSo,
    menh_position: DiaChi,
) -> dict[str, object]:
    """Return Thiên Mã support for Nhóm Đối Lập readings.

    The caller is responsible for adding this payload only when Mệnh belongs
    to Nhóm Đối Lập: Tuế Phá, Tang Môn, Điếu Khách.
    """

    position = la_so.position_of("thien_ma")
    if position is None:
        return {
            "available": False,
            "reason": "Không tìm thấy Thiên Mã trong natal layer.",
        }

    lens = _THIEN_MA_POSITION_LENS.get(position)
    thien_ma_components = la_so.tinh_ban.layer(NATAL_LAYER_ID).components_at(position)
    tuan_triet_at_thien_ma = _tuan_triet_marker_payload(
        la_so,
        thien_ma_components,
    )
    return {
        "available": True,
        "star": _component_payload(la_so, "thien_ma"),
        "position": _dia_chi_payload(la_so, position),
        "at_menh": position == menh_position,
        "lens": lens,
        "blocked_by_tuan_triet": bool(tuan_triet_at_thien_ma["markers"]),
        "tuan_triet_at_position": tuan_triet_at_thien_ma,
        "reading_hint": (
            "Với Nhóm Đối Lập, Thiên Mã cho biết kiểu nghị lực và cách bật "
            "lên trong nghịch cảnh; nếu Thiên Mã bị Tuần/Triệt thì ý chí và "
            "đà hành động bị giảm đáng kể."
        ),
    }


def _tuan_triet_marker_payload(
    la_so: LaSo,
    components: frozenset[ComponentId],
) -> TuanTrietMarkerPayload:
    """Convert raw component ids at one position into Tuần/Triệt marker flags."""
    markers = [
        _component_payload(la_so, marker_id)
        for marker_id in _TUAN_TRIET_IDS
        if marker_id in components
    ]
    return {
        "markers": markers,
        "has_tuan": any(marker["name"] == "Tuần" for marker in markers),
        "has_triet": any(marker["name"] == "Triệt" for marker in markers),
    }


def _thai_tue_sat_tinh_payload(
    la_so: LaSo,
    menh_components: frozenset[ComponentId],
) -> dict[str, object]:
    """Summarize the direct Thái Tuế gặp Không/Kiếp/Hỏa/Linh case at Mệnh."""
    sat_tinh = [
        _component_payload(la_so, star_id)
        for star_id in _THAI_TUE_SAT_TINH_IDS
        if star_id in menh_components
    ]

    return {
        "stars": sat_tinh,
        "reading_hint": (
            "Thái Tuế thủ Mệnh gặp sát tinh Không/Kiếp/Hỏa/Linh: đây là bài "
            "học rèn tư cách quân tử rất mạnh. Đương số phải rèn tâm nhiều "
            "để không bị sát khí kéo theo hướng xấu; vẫn phải kiểm tra chính "
            "tinh và toàn bộ cách cục trước khi kết luận."
        ),
    }


def _ego_payload(star_id: ComponentId, group_id: str) -> dict[str, object]:
    """Return the collaboration warning for strong Thái Tuế-style self-regard."""
    if star_id == "thai_tue":
        note = (
            "Thái Tuế thủ Mệnh làm lòng tự trọng và cảm giác chính danh rất "
            "mạnh. Khi hợp tác, cần tránh xúc phạm danh dự vì họ có thể bất "
            "cần và sẵn sàng bỏ ngang nếu thấy bị hạ thấp."
        )
    elif group_id == "chinh_phai":
        note = (
            "Nhóm Chính Phái coi trọng danh dự và đúng sai. Khi giao tiếp, nên "
            "rõ nguyên tắc, minh bạch trách nhiệm và tránh cách nói hạ thấp họ."
        )
    else:
        note = (
            "Ghi chú cái tôi cực đoan áp dụng mạnh nhất khi Thái Tuế thủ Mệnh; "
            "với các nhóm khác chỉ dùng như điểm kiểm tra phụ nếu lá số có thêm "
            "Thái Tuế hoặc cách cục làm tự trọng tăng mạnh."
        )

    return {
        "applies_strongly": star_id == "thai_tue",
        "note": note,
    }


def _component_payload(la_so: LaSo, component_id: ComponentId) -> dict[str, object]:
    """Return id, display name, and optional ngũ hành for a catalog component."""
    component = la_so.component(component_id)
    payload: dict[str, object] = {
        "id": component.id,
        "name": component.name,
    }
    ngu_hanh = getattr(component, "ngu_hanh", None)
    if ngu_hanh is not None:
        payload["ngu_hanh"] = ngu_hanh.value
    return payload


def _dia_chi_payload(la_so: LaSo, dia_chi: DiaChi) -> dict[str, object]:
    """Return id, display name, and ngũ hành for a địa chi position."""
    entity = la_so.catalog.get_dia_chi(dia_chi)
    return {
        "id": entity.id,
        "name": entity.name,
        "ngu_hanh": entity.ngu_hanh.value,
    }


_THAI_TUE_GROUP_MEANINGS: dict[str, ThaiTueGroupMeaning] = {
    "chinh_phai": ThaiTueGroupMeaning(
        id="chinh_phai",
        name="Nhóm Chính Phái",
        archetype="Nhóm Thái Tuế - Người Quân tử",
        star_ids=("thai_tue", "quan_phuf", "bach_ho"),
        overview=(
            "Mẫu người sống có lý tưởng, trách nhiệm cao và hành động vì sự "
            "chính danh, danh chính ngôn thuận."
        ),
        reading_lens=(
            "Luận trọng tâm ở danh dự, trách nhiệm, nguyên tắc sống và khả "
            "năng đứng ra gánh việc. Thường xét thêm bộ Tứ Linh nếu có."
        ),
        trap=(
            "Dễ quá cứng nhắc về đúng sai, tự trọng cao, tạo cảm giác bề trên "
            "hoặc rơi vào thế cô độc nếu thiếu mềm dẻo."
        ),
    ),
    "khon_ngoan": ThaiTueGroupMeaning(
        id="khon_ngoan",
        name="Nhóm Khôn Ngoan",
        archetype="Nhóm Thiếu Dương - Thiên Không, bài học Sắc tức thị Không",
        star_ids=("thieu_duong", "tu_phu", "sao_phuc_duc"),
        overview=(
            "Mẫu người thông minh, sắc sảo, biết đi trước và có xu hướng muốn "
            "lấn lướt, vượt lên người khác."
        ),
        reading_lens=(
            "Luận trọng tâm ở trí tuệ, tham vọng, khả năng nhìn cơ hội và bài "
            "học biết dừng đúng lúc. Nhóm này luôn có sắc thái Thiên Không đi "
            "kèm nên phải đọc thêm bài học được-mất rất nhanh."
        ),
        trap=(
            "Nếu dùng trí khôn để lấn lướt, thủ đoạn hoặc lợi dụng người khác "
            "thì dễ rơi vào bài học 'Sắc tức thị Không', trắng tay hoặc về Zero."
        ),
    ),
    "doi_lap": ThaiTueGroupMeaning(
        id="doi_lap",
        name="Nhóm Đối Lập",
        archetype="Nhóm Tuế Phá - Sức mạnh nghịch cảnh",
        star_ids=("tang_mon", "tue_pha", "dieu_khach"),
        overview=(
            "Mẫu người luôn bất mãn với thực tại, thích bàn ra, đi ngược đám "
            "đông và chống đối những gì người khác đề ra."
        ),
        reading_lens=(
            "Luận trọng tâm ở nghị lực trong nghịch cảnh, khả năng phản biện, "
            "cải tổ và chịu áp lực. Sự thành bại của nhóm này phụ thuộc nhiều "
            "vào nghị lực và sao Thiên Mã."
        ),
        trap=(
            "Dễ biến phản biện thành chống đối cực đoan, than vãn hoặc lôi kéo "
            "người khác bằng bất mãn."
        ),
    ),
    "nhuong_nhin": ThaiTueGroupMeaning(
        id="nhuong_nhin",
        name="Nhóm Nhường Nhịn",
        archetype="Nhóm Thiếu Âm - Sự nhẹ dạ",
        star_ids=("thieu_am", "long_duc", "truc_phu"),
        overview=(
            "Mẫu người cam chịu, hiền lành, hay chịu phần thiệt về mình trong "
            "quan hệ và lấy đạo đức làm chỗ dựa."
        ),
        reading_lens=(
            "Luận trọng tâm ở đạo đức, sự nhẫn nhịn, khả năng giữ hòa khí và "
            "cách họ gánh phần nặng cho người khác. Đạo đức và sự nhường "
            "nhịn thường trở thành tôn chỉ sống của nhóm này."
        ),
        trap=(
            "Dễ bị lợi dụng, làm nhiều hưởng ít hoặc nhường quá mức khiến bản "
            "thân thiệt thòi; dễ rơi vào cảnh đào giếng cho người khác uống nước."
        ),
    ),
}


_THAI_TUE_STAR_MEANINGS: dict[ComponentId, ThaiTueStarMeaning] = {
    "thai_tue": ThaiTueStarMeaning(
        id="thai_tue",
        group_id="chinh_phai",
        keywords=(
            "lãnh đạo",
            "chính danh",
            "tự trọng",
            "sứ mệnh",
            "quân tử",
            "tình cảm khó hòa hợp",
        ),
        at_menh=(
            "Là chúa tể của vòng Thái Tuế tại Mệnh: có khí chất lãnh đạo, "
            "tư duy hoạch định lớn và cảm giác mình sinh ra để làm việc chính đáng."
        ),
        shadow=(
            "Dễ luôn cho mình đúng, nói thẳng khó nghe, tự trọng rất cao và "
            "khó nhận sai; trong tình cảm dễ làm đối phương khó hòa hợp vì "
            "luôn giữ lập trường mình đúng."
        ),
        reading_hint=(
            "Khi luận, nhấn vào bài học tư cách quân tử, danh dự, trách nhiệm, "
            "sứ mệnh và cách họ xử lý va chạm bằng lập trường chính danh. "
            "Nếu Thái Tuế đi cùng Không/Kiếp/Hỏa/Linh thì phải xem thêm bài "
            "học rèn tâm để không bị sát khí kéo theo hướng xấu."
        ),
    ),
    "quan_phuf": ThaiTueStarMeaning(
        id="quan_phuf",
        group_id="chinh_phai",
        keywords=(
            "cẩn trọng",
            "suy tính",
            "nguyên tắc",
            "phong thái",
            "tránh đụng chạm",
        ),
        at_menh=(
            "Quan Phù tại Mệnh nghiêng về suy xét kỹ trước khi hành động, "
            "biết giữ phép tắc và tránh va chạm không cần thiết."
        ),
        shadow=(
            "Có thể tạo cảm giác bề trên, trịnh thượng hoặc quá giữ thế nếu "
            "thiếu sự gần gũi."
        ),
        reading_hint=(
            "Đọc theo hướng người có phong thái, biết cân nhắc lợi hại và cần "
            "học cách giảm khoảng cách với người xung quanh."
        ),
    ),
    "bach_ho": ThaiTueStarMeaning(
        id="bach_ho",
        group_id="chinh_phai",
        keywords=("hành động", "quyết liệt", "lăn xả", "tranh cãi", "hình thương"),
        at_menh=(
            "Bạch Hổ tại Mệnh là mẫu người hành động, nói được làm được và "
            "sẵn sàng lăn xả để hoàn thành việc."
        ),
        shadow=(
            "Bạch Hổ là bại tinh nên cuộc đời dễ có va đập, hình thương, cực "
            "khổ hoặc tranh cãi; lời nói đôi khi gắt và châm chọc."
        ),
        reading_hint=(
            "Luận sức làm, độ quyết liệt và khả năng chịu việc nặng; đồng thời "
            "kiểm tra sát tinh và Tuần/Triệt để tránh phóng đại hình thương."
        ),
    ),
    "thieu_duong": ThaiTueStarMeaning(
        id="thieu_duong",
        group_id="khon_ngoan",
        keywords=(
            "thông minh",
            "đi trước",
            "tham vọng",
            "Thiên Không",
            "Đường Tăng",
            "cơ hội hứa hẹn",
        ),
        at_menh=(
            "Thiếu Dương tại Mệnh là kiểu rất thông minh, muốn đứng trước "
            "người khác và thường có tham vọng lớn."
        ),
        shadow=(
            "Vì thường đi cùng Thiên Không, nếu dùng trí khôn để lợi dụng "
            "người khác, chạy theo tham vọng hoặc các cơ hội hứa hẹn như "
            "Đào Hoa/Hồng Loan thì dễ dẫn đến mất trắng ở cuối đường."
        ),
        reading_hint=(
            "Đọc trí sáng và khả năng nắm thời cơ theo hình tượng Đường Tăng, "
            "nhưng luôn nhắc bài học Sắc tức thị Không: biết dừng và dùng trí "
            "tuệ có đạo đức."
        ),
    ),
    "tu_phu": ThaiTueStarMeaning(
        id="tu_phu",
        group_id="khon_ngoan",
        keywords=("thông minh", "thiệt thòi", "quản lý", "mẹ thiên hạ", "Nguyệt Đức"),
        at_menh=(
            "Tử Phù tại Mệnh cũng thông minh, nhưng hay thấy mình gặp trở "
            "ngại hoặc bị thiệt trong công việc và quan hệ."
        ),
        shadow=(
            "Dễ có tâm lý thích quản người khác; nếu thiếu hài hòa và thiếu "
            "tinh thần Nguyệt Đức thì dễ bị cô lập."
        ),
        reading_hint=(
            "Luận khả năng quản việc và nhìn ra vấn đề, rồi xét họ có biết "
            "mềm hóa quan hệ hay không."
        ),
    ),
    "sao_phuc_duc": ThaiTueStarMeaning(
        id="sao_phuc_duc",
        group_id="khon_ngoan",
        keywords=("khôn ngoan", "đức độ", "biết dừng", "đắc nhân tâm", "khéo ứng xử"),
        at_menh=(
            "Phúc Đức tại Mệnh là người khôn ngoan nhưng có đức độ và biết điểm dừng."
        ),
        shadow=(
            "Nếu các sao khác làm tham vọng tăng mạnh, cần kiểm tra họ có còn "
            "giữ được điểm dừng và lòng người hay không."
        ),
        reading_hint=(
            "Đọc theo hướng thu phục lòng người bằng tri thức, đức độ và cách "
            "ứng xử khiến người khác tự nhiên yêu mến."
        ),
    ),
    "tue_pha": ThaiTueStarMeaning(
        id="tue_pha",
        group_id="doi_lap",
        keywords=(
            "lì lợm",
            "phản nghịch",
            "tư duy ngược",
            "Tôn Ngộ Không",
            "cải tổ",
            "nhìn thẳng sai lầm",
        ),
        at_menh=(
            "Tuế Phá tại Mệnh là kiểu phản nghịch và lì lợm nhất trong nhóm, "
            "thường không dễ chấp nhận ý kiến sẵn có, có tư duy ngược như "
            "hình tượng Tôn Ngộ Không."
        ),
        shadow=(
            "Dễ chống đối kịch liệt, bác bỏ người khác trước khi nghe hết "
            "hoặc biến phản biện thành phá ngang."
        ),
        reading_hint=(
            "Dùng tốt trong bối cảnh cải tổ tổ chức đang đi xuống, vì họ dám "
            "nhìn thẳng lỗi sai mà đám đông đang tin là đúng và nói điều khó "
            "nghe. Thành bại phải đọc kèm nghị lực và vị trí Thiên Mã."
        ),
    ),
    "tang_mon": ThaiTueStarMeaning(
        id="tang_mon",
        group_id="doi_lap",
        keywords=("lo âu", "buồn phiền", "gánh vác", "than vãn", "không thỏa mãn"),
        at_menh=(
            "Tang Môn tại Mệnh chủ lo âu, buồn phiền và cảm giác phải gánh "
            "trách nhiệm cho người khác."
        ),
        shadow=(
            "Dễ than vãn, không thỏa mãn với hiện tại hoặc đứng núi này trông núi nọ."
        ),
        reading_hint=(
            "Luận sức chịu gánh và nỗi bất an bên trong; cần xem thêm cát tinh "
            "để biết khả năng chuyển lo thành trách nhiệm hữu ích."
        ),
    ),
    "dieu_khach": ThaiTueStarMeaning(
        id="dieu_khach",
        group_id="doi_lap",
        keywords=("thuyết phục", "nói giỏi", "chứng tỏ", "hưởng thụ", "lôi kéo"),
        at_menh=(
            "Điếu Khách tại Mệnh có khả năng nói năng, thuyết phục và khơi "
            "gợi cảm xúc của người khác."
        ),
        shadow=(
            "Dễ thích chứng tỏ qua lời nói, hưởng thụ hoặc lôi kéo người khác "
            "bằng sự đồng cảm và bất mãn."
        ),
        reading_hint=(
            "Đọc năng lực truyền thông và tập hợp người, nhưng kiểm tra động "
            "cơ để phân biệt thuyết phục chính đáng với kích động bất mãn."
        ),
    ),
    "thieu_am": ThaiTueStarMeaning(
        id="thieu_am",
        group_id="nhuong_nhin",
        keywords=(
            "nhẹ dạ",
            "cả tin",
            "thiếu dã tâm",
            "dễ bị dụ dỗ",
            "lợi ích nhỏ trước mắt",
            "Trư Bát Giới",
        ),
        at_menh=(
            "Thiếu Âm tại Mệnh là kiểu mềm, nhẹ dạ, cả tin và không nhiều "
            "dã tâm; dễ bị dụ bởi lợi ích nhỏ trước mắt theo hình tượng "
            "Trư Bát Giới."
        ),
        shadow=(
            "Dễ mắc sai lầm hoặc bị lợi dụng nhưng không muốn trả thù hay hại "
            "lại người khác."
        ),
        reading_hint=(
            "Luận sự hiền lành và khả năng chịu thiệt; cần nhắc bài học ranh "
            "giới cá nhân để không bị lợi dụng."
        ),
    ),
    "long_duc": ThaiTueStarMeaning(
        id="long_duc",
        group_id="nhuong_nhin",
        keywords=("nhường lợi", "hòa khí", "tích đức", "an ủi tinh thần", "nhân hòa"),
        at_menh=(
            "Long Đức tại Mệnh chủ động nhường phần lợi cho người khác để giữ "
            "hòa khí và tích đức."
        ),
        shadow=(
            "Có thể chịu thiệt hiện tại quá nhiều vì tin vào đạo đức và sự an "
            "ủi tinh thần."
        ),
        reading_hint=(
            "Đọc theo hướng đổi lợi trước mắt lấy bình an, nhân hòa và sự nâng "
            "đỡ tinh thần về sau."
        ),
    ),
    "truc_phu": ThaiTueStarMeaning(
        id="truc_phu",
        group_id="nhuong_nhin",
        keywords=(
            "gánh việc",
            "cần mẫn",
            "làm nặng",
            "không đòi hỏi",
            "thiệt thành quả",
        ),
        at_menh=(
            "Trực Phù tại Mệnh là mẫu người của công việc, sẵn sàng nhận phần "
            "nặng nhọc mà không đòi hỏi quyền lợi tương xứng."
        ),
        shadow=(
            "Dễ rơi vào cảnh đào giếng cho người khác uống nước, làm nhiều "
            "nhưng thành quả bị người khác hưởng."
        ),
        reading_hint=(
            "Luận sự cần mẫn và trách nhiệm thực tế; nên kiểm tra khả năng tự "
            "bảo vệ quyền lợi và chọn môi trường công bằng."
        ),
    ),
}


_THIEN_MA_POSITION_LENS: dict[DiaChi, dict[str, str]] = {
    DiaChi.DAN: {
        "element": "Mộc",
        "will_style": "Bền bỉ, tăng lực bằng tích lũy và sức sống dài hơi.",
    },
    DiaChi.TI: {
        "element": "Hỏa",
        "will_style": "Bùng nổ nhanh, hành động mạnh nhưng cần tránh nóng vội.",
    },
    DiaChi.THAN: {
        "element": "Kim",
        "will_style": "Dứt khoát, quyết định nhanh, hợp xử lý việc cần cắt gọn.",
    },
    DiaChi.HOI: {
        "element": "Thủy",
        "will_style": "Biết chờ thời, đi đường vòng và bật lên khi đúng nhịp.",
    },
}


_TUAN_TRIET_IDS: tuple[ComponentId, ...] = (
    "tuan_1",
    "tuan_2",
    "triet_1",
    "triet_2",
)

_THAI_TUE_SAT_TINH_IDS: tuple[ComponentId, ...] = (
    "dia_khong",
    "dia_kiep",
    "hoa_tinh",
    "linh_tinh",
)
