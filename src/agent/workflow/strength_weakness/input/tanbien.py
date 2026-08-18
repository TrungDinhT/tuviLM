"""Tân Biên evidence contract for capability strengths and weaknesses."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import ModelRetry, RunContext

from src.agent.deps import TuviAgentDeps
from src.agent.tool.cach_cuc.loader import load_cach_cuc_source
from src.agent.tool.cach_cuc.matcher import find_matching_cach_cuc
from src.agent.tool.cach_cuc.models import CachCuc, CachCucData, SourceKind
from src.agent.tool.tu_vi_tan_bien.constant import (
    MAP_ROLE_SECTION_ID_FUNC,
    get_sao_section_id,
)
from src.agent.workflow.strength_weakness.ontology import (
    CAPABILITY_ONTOLOGY_VERSION,
)
from src.refactored.components.definitions.cung_role import Role
from src.refactored.components.definitions.map_sao_status import MAP_SAO_STATUS
from src.refactored.components.definitions.sao import (
    ChinhPhuTinh,
    TuHoa,
    TuanTriet,
)
from src.refactored.la_so import LaSo
from src.refactored.model.elementary import DiaChi
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.placement.rules.loader import load_tu_hoa_target_mapping


_logger = logging.getLogger(__name__)
_BOOK_NAME = "Tử Vi Đẩu Số Tân Biên"
_TU_HOA_IDS = ("hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky")


class PalaceRelation(StrEnum):
    MENH = "menh"
    TAM_HOP = "tam_hop"
    XUNG_CHIEU = "xung_chieu"
    BO_SUNG = "bo_sung"


class SourceReference(BaseModel):
    source: str = _BOOK_NAME
    section_id: str | None = None
    page: int | None = None
    breadcrumb: str | None = None


class MeaningReference(BaseModel):
    section_id: str
    scope: str
    source: str = _BOOK_NAME


class MeaningContent(BaseModel):
    source: SourceReference
    content: str


class CapabilityMeaningEvidence(BaseModel):
    object_name: str
    role: Role | None = None
    meanings: list[MeaningContent] = Field(default_factory=list)
    note: str | None = None


class StarEvidence(BaseModel):
    evidence_id: str
    component_id: str
    name: str
    status: str | None = None
    classifications: list[str] = Field(default_factory=list)
    meaning_references: list[MeaningReference] = Field(default_factory=list)
    structure_ids: list[str] = Field(default_factory=list)


class TuHoaEvidence(BaseModel):
    evidence_id: str
    component_id: str
    name: str
    position: DiaChi
    palace_role: Role
    palace_evidence_id: str
    relation_to_menh: PalaceRelation
    target_star_id: str
    target_star_name: str
    meaning_references: list[MeaningReference] = Field(default_factory=list)
    structure_ids: list[str] = Field(default_factory=list)


class TuanTrietEvidence(BaseModel):
    evidence_id: str
    component_id: str
    name: str
    meaning_references: list[MeaningReference] = Field(default_factory=list)


class PalaceEvidence(BaseModel):
    evidence_id: str
    role: Role
    role_name: str
    position: DiaChi
    is_cung_than: bool
    relation_to_menh: PalaceRelation
    chinh_tinh: list[StarEvidence] = Field(default_factory=list)
    phu_tinh: list[StarEvidence] = Field(default_factory=list)
    tu_hoa_evidence_ids: list[str] = Field(default_factory=list)
    tuan_triet: list[TuanTrietEvidence] = Field(default_factory=list)


class CachCucEvidence(BaseModel):
    evidence_id: str
    structure_id: str
    id: str
    name: str
    priority: int
    meaning: str
    source_evidence: str | None = None
    related_roles: list[Role] = Field(default_factory=list)
    component_ids: list[str] = Field(default_factory=list)
    palace_evidence_ids: list[str] = Field(default_factory=list)
    source: SourceReference


class MenhThanEvidence(BaseModel):
    menh_palace_evidence_id: str
    than_palace_evidence_id: str
    same_palace: bool
    than_cu: str


class TamPhuongTuChinhEvidence(BaseModel):
    anchor_palace_evidence_id: str
    tam_hop_palace_evidence_ids: list[str]
    xung_chieu_palace_evidence_id: str


class CapabilityEvidence(BaseModel):
    """Compact initial evidence; detailed meanings and extra palaces are lazy."""

    model_config = ConfigDict(extra="ignore")

    ontology_version: str
    palaces: list[PalaceEvidence]
    menh_than: MenhThanEvidence
    tam_phuong_tu_chinh_menh: TamPhuongTuChinhEvidence
    cach_cuc: list[CachCucEvidence] = Field(default_factory=list)
    tu_hoa: list[TuHoaEvidence]


class SupplementalPalaceEvidence(BaseModel):
    palace: PalaceEvidence
    cach_cuc: list[CachCucEvidence] = Field(default_factory=list)
    tu_hoa: list[TuHoaEvidence] = Field(default_factory=list)


def _palace_evidence_id(position: DiaChi) -> str:
    return f"cung:{position.value}"


def _relation_to_menh(position: DiaChi, menh_position: DiaChi) -> PalaceRelation:
    if position == menh_position:
        return PalaceRelation.MENH
    if position == menh_position + 6:
        return PalaceRelation.XUNG_CHIEU
    if position in {menh_position + 4, menh_position + 8}:
        return PalaceRelation.TAM_HOP
    return PalaceRelation.BO_SUNG


def _meaning_references(
    object_name: str,
    roles: Iterable[Role] = (),
) -> list[MeaningReference]:
    references: list[MeaningReference] = []
    generic_section_id = get_sao_section_id(object_name)
    if generic_section_id is not None:
        references.append(
            MeaningReference(section_id=generic_section_id, scope="generic")
        )

    seen = {reference.section_id for reference in references}
    for role in roles:
        section_id_func = MAP_ROLE_SECTION_ID_FUNC.get(role)
        section_id = section_id_func(object_name) if section_id_func else None
        if section_id is None or section_id in seen:
            continue
        references.append(
            MeaningReference(section_id=section_id, scope=f"role:{role.value}")
        )
        seen.add(section_id)
    return references


def _condition_component_ids(value: Any, data: CachCucData) -> set[str]:
    """Collect authored star ids without exposing matcher conditions to the model."""
    if isinstance(value, BaseModel):
        return _condition_component_ids(value.model_dump(by_alias=True), data)
    if isinstance(value, list):
        component_ids: set[str] = set()
        for item in value:
            component_ids.update(_condition_component_ids(item, data))
        return component_ids
    if not isinstance(value, dict):
        return set()

    component_ids = set()
    star = value.get("star")
    if isinstance(star, str):
        component_ids.add(star)
    stars = value.get("stars")
    if isinstance(stars, list):
        component_ids.update(item for item in stars if isinstance(item, str))
    group_name = value.get("group_name")
    if isinstance(group_name, str) and group_name in data.groups:
        component_ids.update(data.groups[group_name].stars)
    for nested in value.values():
        if isinstance(nested, (dict, list, BaseModel)):
            component_ids.update(_condition_component_ids(nested, data))
    return component_ids


def _project_cach_cuc(
    la_so: LaSo,
    cach_cuc: CachCuc,
    data: CachCucData,
) -> CachCucEvidence:
    structure_id = f"cach_cuc:{cach_cuc.id}"
    component_ids = sorted(_condition_component_ids(cach_cuc.conditions, data))
    palace_ids: list[str] = []
    for role in cach_cuc.related_roles:
        position = la_so.position_of(role.value, NATAL_LAYER_ID)
        if position is not None:
            palace_ids.append(_palace_evidence_id(position))
    return CachCucEvidence(
        evidence_id=structure_id,
        structure_id=structure_id,
        id=cach_cuc.id,
        name=cach_cuc.name,
        priority=cach_cuc.priority,
        meaning=cach_cuc.meaning,
        source_evidence=cach_cuc.evidence,
        related_roles=list(cach_cuc.related_roles),
        component_ids=component_ids,
        palace_evidence_ids=list(dict.fromkeys(palace_ids)),
        source=SourceReference(page=cach_cuc.page or None),
    )


def _matching_cach_cuc_evidence(
    la_so: LaSo,
    roles: list[Role],
) -> list[CachCucEvidence]:
    data = load_cach_cuc_source(SourceKind.TUVITANBIEN)
    matches = find_matching_cach_cuc(
        la_so,
        data=data,
        source_kind=SourceKind.TUVITANBIEN,
        filtered_roles=roles,
    )
    return [_project_cach_cuc(la_so, cach_cuc, data) for cach_cuc in matches]


def _component_structure_map(
    cach_cuc: Iterable[CachCucEvidence],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for item in cach_cuc:
        for component_id in item.component_ids:
            result.setdefault(component_id, []).append(item.structure_id)
    return result


def _star_evidence(
    *,
    la_so: LaSo,
    component_id: str,
    position: DiaChi,
    roles: tuple[Role, ...],
    structure_map: dict[str, list[str]],
) -> StarEvidence:
    component = la_so.component(component_id)
    if not isinstance(component, ChinhPhuTinh):
        raise TypeError(f"Expected ChinhPhuTinh, got {type(component).__name__}.")
    status = MAP_SAO_STATUS.get(component_id, {}).get(position)
    return StarEvidence(
        evidence_id=f"star:{component_id}:{position.value}",
        component_id=component_id,
        name=component.name,
        status=status.value if status else None,
        classifications=[item.value for item in component.sao_type],
        meaning_references=_meaning_references(component.name, roles),
        structure_ids=structure_map.get(component_id, []),
    )


def _tu_hoa_evidence(
    *,
    la_so: LaSo,
    component_id: str,
    position: DiaChi,
    roles: tuple[Role, ...],
    structure_map: dict[str, list[str]],
    target_mapping: dict[str, str],
) -> TuHoaEvidence:
    component = la_so.component(component_id)
    target_id = target_mapping.get(component_id)
    if target_id is None:
        raise ModelRetry(f"Không xác định được sao chịu {component.name}.")
    target = la_so.component(target_id)
    return TuHoaEvidence(
        evidence_id=f"tu_hoa:{component_id}:{position.value}",
        component_id=component_id,
        name=component.name,
        position=position,
        palace_role=la_so.cung_at(position).natal_role,
        palace_evidence_id=_palace_evidence_id(position),
        relation_to_menh=_relation_to_menh(
            position,
            la_so.tinh_ban.menh_position,
        ),
        target_star_id=target_id,
        target_star_name=target.name,
        meaning_references=_meaning_references(component.name, roles),
        structure_ids=structure_map.get(component_id, []),
    )


def _build_palace_evidence(
    la_so: LaSo,
    position: DiaChi,
    *,
    menh_position: DiaChi,
    structure_map: dict[str, list[str]],
) -> PalaceEvidence:
    cung = la_so.cung_at(position)
    roles = (cung.natal_role,)
    if cung.is_cung_than and Role.CUNG_THAN not in roles:
        roles = (*roles, Role.CUNG_THAN)

    chinh_tinh: list[StarEvidence] = []
    phu_tinh: list[StarEvidence] = []
    tu_hoa_evidence_ids: list[str] = []
    tuan_triet: list[TuanTrietEvidence] = []

    for component_id in cung.components_in_layer(NATAL_LAYER_ID):
        component = la_so.component(component_id)
        if isinstance(component, ChinhPhuTinh):
            evidence = _star_evidence(
                la_so=la_so,
                component_id=component_id,
                position=position,
                roles=roles,
                structure_map=structure_map,
            )
            (chinh_tinh if component.is_chinh_tinh else phu_tinh).append(evidence)
        elif isinstance(component, TuHoa):
            tu_hoa_evidence_ids.append(
                f"tu_hoa:{component_id}:{position.value}"
            )
        elif isinstance(component, TuanTriet):
            tuan_triet.append(
                TuanTrietEvidence(
                    evidence_id=f"tuan_triet:{component_id}:{position.value}",
                    component_id=component_id,
                    name=component.name,
                    meaning_references=_meaning_references(component.name, roles),
                )
            )

    return PalaceEvidence(
        evidence_id=_palace_evidence_id(position),
        role=cung.natal_role,
        role_name=la_so.component(cung.natal_role.value).name,
        position=position,
        is_cung_than=cung.is_cung_than,
        relation_to_menh=_relation_to_menh(position, menh_position),
        chinh_tinh=chinh_tinh,
        phu_tinh=phu_tinh,
        tu_hoa_evidence_ids=tu_hoa_evidence_ids,
        tuan_triet=tuan_triet,
    )


def _build_all_tu_hoa_evidence(
    la_so: LaSo,
    structure_map: dict[str, list[str]],
) -> list[TuHoaEvidence]:
    target_mapping = load_tu_hoa_target_mapping()[la_so.natal_context.thien_can]
    evidence: list[TuHoaEvidence] = []
    for component_id in _TU_HOA_IDS:
        position = la_so.position_of(component_id, NATAL_LAYER_ID)
        if position is None:
            raise ModelRetry(f"Không tìm thấy vị trí của Tứ Hóa '{component_id}'.")
        cung = la_so.cung_at(position)
        roles = (cung.natal_role,)
        if cung.is_cung_than:
            roles = (*roles, Role.CUNG_THAN)
        evidence.append(
            _tu_hoa_evidence(
                la_so=la_so,
                component_id=component_id,
                position=position,
                roles=roles,
                structure_map=structure_map,
                target_mapping=target_mapping,
            )
        )
    return evidence


def get_strength_weakness_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> CapabilityEvidence:
    """Build the workflow's complete initial input contract exactly once."""
    _logger.info("Tool get_strength_weakness_evidence bắt đầu")
    la_so = ctx.deps.require_la_so()
    menh_position = la_so.tinh_ban.menh_position
    than_position = la_so.tinh_ban.than_position
    cach_cuc = _matching_cach_cuc_evidence(
        la_so,
        [Role.MENH, Role.CUNG_THAN],
    )
    structure_map = _component_structure_map(cach_cuc)
    tu_hoa = _build_all_tu_hoa_evidence(la_so, structure_map)

    tam_hop_positions = (menh_position + 4, menh_position + 8)
    xung_chieu_position = menh_position + 6
    ordered_positions = list(
        dict.fromkeys(
            (
                menh_position,
                than_position,
                *tam_hop_positions,
                xung_chieu_position,
            )
        )
    )
    palaces = [
        _build_palace_evidence(
            la_so,
            position,
            menh_position=menh_position,
            structure_map=structure_map,
        )
        for position in ordered_positions
    ]
    than_cung = la_so.cung_at(than_position)
    evidence = CapabilityEvidence(
        ontology_version=CAPABILITY_ONTOLOGY_VERSION,
        palaces=palaces,
        menh_than=MenhThanEvidence(
            menh_palace_evidence_id=_palace_evidence_id(menh_position),
            than_palace_evidence_id=_palace_evidence_id(than_position),
            same_palace=menh_position == than_position,
            than_cu=la_so.component(than_cung.natal_role.value).name,
        ),
        tam_phuong_tu_chinh_menh=TamPhuongTuChinhEvidence(
            anchor_palace_evidence_id=_palace_evidence_id(menh_position),
            tam_hop_palace_evidence_ids=[
                _palace_evidence_id(position) for position in tam_hop_positions
            ],
            xung_chieu_palace_evidence_id=_palace_evidence_id(
                xung_chieu_position
            ),
        ),
        cach_cuc=cach_cuc,
        tu_hoa=tu_hoa,
    )
    _logger.info(
        "Đã dựng capability evidence: palaces=%d cach_cuc=%d same_menh_than=%s",
        len(evidence.palaces),
        len(evidence.cach_cuc),
        evidence.menh_than.same_palace,
    )
    return evidence


def get_capability_palace_evidence(
    ctx: RunContext[TuviAgentDeps],
    role: Role,
) -> SupplementalPalaceEvidence:
    """Lazy retrieval for one additional palace when it can change a finding."""
    la_so = ctx.deps.require_la_so()
    position = la_so.position_of(role.value, NATAL_LAYER_ID)
    if position is None:
        raise ModelRetry(f"Không tìm thấy cung '{role.value}'.")
    cach_cuc = _matching_cach_cuc_evidence(la_so, [role])
    tu_hoa = _build_all_tu_hoa_evidence(
        la_so,
        _component_structure_map(cach_cuc),
    )
    return SupplementalPalaceEvidence(
        palace=_build_palace_evidence(
            la_so,
            position,
            menh_position=la_so.tinh_ban.menh_position,
            structure_map=_component_structure_map(cach_cuc),
        ),
        cach_cuc=cach_cuc,
        tu_hoa=[item for item in tu_hoa if item.position == position],
    )


def get_capability_meaning(
    ctx: RunContext[TuviAgentDeps],
    object_name: str,
    role: Role | None = None,
) -> CapabilityMeaningEvidence:
    """Read generic and role-specific Tân Biên meanings for one object."""
    references = _meaning_references(
        object_name,
        (role,) if role is not None else (),
    )
    meanings: list[MeaningContent] = []
    book = ctx.deps.require_book()
    for reference in references:
        section = book.read_section(reference.section_id)
        meanings.append(
            MeaningContent(
                source=SourceReference(
                    section_id=section.id,
                    breadcrumb=section.breadcrumb,
                ),
                content=section.content,
            )
        )
    note = None
    if not meanings:
        note = f"Không tìm thấy mục Tân Biên cho {object_name!r}."
    return CapabilityMeaningEvidence(
        object_name=object_name,
        role=role,
        meanings=meanings,
        note=note,
    )


STRENGTH_WEAKNESS_REASONING_INSTRUCTION = """
## Quy trình suy luận năng lực

Tool chỉ định vị, trích xuất, detect cấu trúc và truy xuất ý nghĩa Tử Vi. Bạn là
người đọc các ý nghĩa đó để luận; không dùng fixed mapping sao → năng lực.

1. Luôn gọi `get_strength_weakness_evidence` đúng một lần trước khi suy luận.
2. Đọc cấu trúc lớn trước: Mệnh/Thân, tam phương tứ chính Mệnh, cách cục và Tứ
   Hóa. `palaces` là danh sách cung duy nhất; các object quan hệ tham chiếu bằng
   `evidence_id`, vì vậy không đếm Mệnh/Thân đồng cung hai lần.
3. Cách cục đã có meaning và `structure_id`. Với chính tinh, phụ tinh, Tứ Hóa
   hoặc Tuần/Triệt trở thành căn cứ quan trọng, gọi `get_capability_meaning` để
   đọc meaning Tân Biên trước khi dùng. Không suy từ tên sao đơn thuần.
4. Chỉ gọi `get_capability_palace_evidence` khi context của Nô Bộc, Tật Ách,
   Phúc Đức hoặc cung khác có thể thay đổi/làm cụ thể một kết luận quan trọng;
   không gọi thêm chỉ để đạt số lượng findings.
5. Từ meaning, tổng hợp toàn bộ evidence liên quan trong tương quan với toàn lá
   số rồi hình thành các cụm khuynh hướng nhất quán. Không tách một evidence
   riêng lẻ để suy thẳng thành kết luận năng lực.
6. Với mỗi khuynh hướng quan trọng, xét cả constructive expression và failure
   mode: hạn chế trực tiếp, quá đà hoặc xung đột với khuynh hướng khác.
7. Chỉ sau đó mới map sang Danh mục năng lực. So sánh relative salience trong
   toàn profile, không chấm điểm tuyệt đối.
8. Không coi cát tinh = điểm mạnh, hung/sát/Kỵ = điểm yếu. Một cấu trúc khó có
   thể chứa năng lực hữu ích; một cấu trúc thuận có thể tạo blind spot.
9. Deduplicate theo meaning và evidence family. Nếu sao thành phần có cùng
   `structure_id` với một cách cục, không tính chúng thành các xác nhận độc lập.
10. Chỉ luận năng lực của bản thân. Không suy giàu nghèo, may rủi, địa vị, chức
    vụ, nghề cụ thể, chất lượng người thân/bạn bè hoặc thành công tương lai.
11. Trước khi output, đối chiếu mỗi finding với các tín hiệu củng cố, điều kiện
    hóa và xung đột trong toàn profile. `giai_thich` chỉ trình bày pattern hành
    vi tổng hợp; không xuất danh sách evidence, `evidence_id` hay reasoning
    chain nội bộ.
""".strip()


__all__ = [
    "CapabilityEvidence",
    "CapabilityMeaningEvidence",
    "CachCucEvidence",
    "MeaningContent",
    "PalaceEvidence",
    "STRENGTH_WEAKNESS_REASONING_INSTRUCTION",
    "SupplementalPalaceEvidence",
    "get_capability_meaning",
    "get_capability_palace_evidence",
    "get_strength_weakness_evidence",
]
