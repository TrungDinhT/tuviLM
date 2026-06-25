from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.agent.cach_cuc.loader import load_cach_cuc_source
from src.agent.cach_cuc.matcher import find_matching_cach_cuc
from src.agent.cach_cuc.models import (
    CachCucData,
    CachCucToolResult,
    Role,
    SourceKind,
)
from src.refactored.model.cung import Cung
from src.refactored.model.elementary import DiaChi, ThienCan
from src.refactored.model.layer import NATAL_LAYER_ID
from src.refactored.model.prior import Gender


@dataclass(frozen=True)
class _MinimalPrior:
    thien_can: ThienCan = ThienCan.CANH
    gender: Gender = Gender.MALE


class _MinimalLaSo:
    """Small chart double containing only positions needed by these tests."""

    prior = _MinimalPrior()

    def __init__(
        self,
        star_positions: dict[str, DiaChi],
        role_positions: dict[Role, DiaChi] | None = None,
    ) -> None:
        self._star_positions = star_positions
        base_role_positions = {
            Role.MENH.value: DiaChi.TY,
            Role.QUAN_LOC.value: DiaChi.THIN,
            Role.CUNG_THAN.value: DiaChi.TY,
            Role.THIEN_DI.value: DiaChi.NGO,
            Role.PHU_THE.value: DiaChi.TUAT,
            Role.DIEN_TRACH.value: DiaChi.MEO,
            Role.TAI_BACH.value: DiaChi.THAN,
        }
        if role_positions:
            base_role_positions.update(
                {role.value: position for role, position in role_positions.items()}
            )
        self._role_positions = base_role_positions

    def position_of(self, component_id: str, layer_id=NATAL_LAYER_ID) -> DiaChi | None:
        if layer_id != NATAL_LAYER_ID:
            return None
        return self._role_positions.get(component_id) or self._star_positions.get(
            component_id
        )

    def cung_at(self, dia_chi: DiaChi, layer_ids=(NATAL_LAYER_ID,)) -> Cung:
        role_by_position = {
            position: Role(role)
            for role, position in self._role_positions.items()
            if role != Role.CUNG_THAN.value
        }
        component_ids = tuple(
            component_id
            for component_id, position in self._star_positions.items()
            if position == dia_chi
        )
        return Cung(
            dia_chi=dia_chi,
            thien_can=ThienCan.GIAP,
            natal_role=role_by_position.get(dia_chi, Role.MENH),
            is_cung_than=dia_chi == self._role_positions[Role.CUNG_THAN.value],
            components=tuple(),
        )


def _reviewed_first_200_line_data() -> CachCucData:
    """Entries copied from the first 200 lines of data/cach_cuc_reviewed.yaml."""
    return _data_from_reviewed_entries(
        [
            {
                "id": "tam_am",
                "name": "Tam am hoi hop",
                "page": 41,
                "priority": 1,
                "meaning": "Bo sao nay thuong che lap anh sang cua Nhat Nguyet",
                "conditions": {
                    "all": [
                        {
                            "type": "stars_meeting",
                            "scope": "hoi_hop",
                            "stars": ["da_la", "hoa_ky", "thien_dieu"],
                        },
                        {
                            "any": [
                                {
                                    "type": "stars_meeting",
                                    "scope": "dong_cung",
                                    "stars": ["thai_duong", "da_la"],
                                },
                                {
                                    "type": "stars_meeting",
                                    "scope": "dong_cung",
                                    "stars": ["thai_am", "hoa_ky"],
                                },
                            ]
                        },
                    ]
                },
            },
            {
                "id": "ho_do_hom_sat",
                "name": "Ho doi hom sat",
                "page": 41,
                "priority": 1,
                "meaning": "Co loi cho viec hoc hanh, thi cu, cau cong danh",
                "conditions": {
                    "all": [
                        {
                            "type": "stars_meeting",
                            "scope": "dong_cung",
                            "stars": ["bach_ho", "tau_thu"],
                        },
                        {
                            "any": [
                                {
                                    "type": "star_with_palace",
                                    "palace": "menh",
                                    "scope": "dong_cung",
                                    "stars": ["bach_ho"],
                                },
                                {
                                    "type": "star_with_palace",
                                    "palace": "quan_loc",
                                    "scope": "dong_cung",
                                    "stars": ["bach_ho"],
                                },
                                {
                                    "type": "star_with_palace",
                                    "palace": "cung_than",
                                    "scope": "dong_cung",
                                    "stars": ["bach_ho"],
                                },
                            ]
                        },
                        {
                            "not": {
                                "type": "stars_meeting",
                                "scope": "dong_cung",
                                "stars": ["tuan", "bach_ho"],
                            }
                        },
                        {
                            "not": {
                                "type": "stars_meeting",
                                "scope": "dong_cung",
                                "stars": ["triet", "bach_ho"],
                            }
                        },
                    ]
                },
            },
        ]
    )


def _data_from_reviewed_entries(entries: list[dict]) -> CachCucData:
    return CachCucData.model_validate(
        {
            "groups": {
                "luc_sat": {
                    "stars": [
                        "kinh_duong",
                        "da_la",
                        "dia_khong",
                        "dia_kiep",
                        "linh_tinh",
                        "hoa_tinh",
                    ]
                },
                "cat_tinh": {
                    "stars": [
                        "ta_phu",
                        "huu_bat",
                        "thien_khoi",
                        "thien_viet",
                        "van_xuong",
                        "van_khuc",
                    ]
                },
            },
            "cach_cuc": entries,
        }
    )


MORE_REVIEWED_CASES = [
    pytest.param(
        {
            "id": "loc_ma_giao_tri",
            "name": "Loc ma giao tri",
            "page": 42,
            "priority": 1,
            "meaning": "Chu tai loc nho dong",
            "conditions": {
                "all": [
                    {
                        "type": "stars_meeting",
                        "scope": "xung_chieu",
                        "stars": ["thien_ma", "loc_ton"],
                    },
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["thien_ma"],
                    },
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": [
                                "tuan",
                                "triet",
                                "da_la",
                                "linh_tinh",
                                "liem_trinh",
                                "hoa_tinh",
                                "tuyet",
                            ],
                        }
                    },
                ]
            },
        },
        _MinimalLaSo({"thien_ma": DiaChi.TY, "loc_ton": DiaChi.NGO}),
        [Role.MENH, Role.CUNG_THAN, Role.THIEN_DI],
        id="loc_ma_giao_tri",
    ),
    pytest.param(
        {
            "id": "phu_du_ma",
            "name": "Phu Du Ma",
            "page": 42,
            "priority": 3,
            "meaning": "Ngua keo xe vua",
            "conditions": {
                "all": [
                    {
                        "type": "stars_meeting",
                        "scope": "dong_cung",
                        "stars": ["thien_ma", "thien_phu", "tu_vi"],
                    },
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["thien_ma"],
                    },
                    {
                        "type": "star_at_chi",
                        "stars": ["thien_ma"],
                        "at_chi": ["dan", "than"],
                    },
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": [
                                "tuan",
                                "triet",
                                "dia_khong",
                                "dia_kiep",
                                "da_la",
                            ],
                        }
                    },
                ]
            },
        },
        _MinimalLaSo(
            {
                "thien_ma": DiaChi.DAN,
                "thien_phu": DiaChi.DAN,
                "tu_vi": DiaChi.DAN,
            },
            {Role.MENH: DiaChi.DAN},
        ),
        Role.MENH,
        id="phu_du_ma",
    ),
    pytest.param(
        {
            "id": "thu_hung_ma",
            "name": "Thu Hung Ma",
            "page": 42,
            "priority": 3,
            "meaning": "Mot doi ngua tot",
            "conditions": {
                "all": [
                    {
                        "type": "stars_meeting",
                        "scope": "hoi_hop",
                        "stars": ["thien_ma", "thai_duong", "thai_am"],
                    },
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["thien_ma"],
                    },
                    {
                        "type": "star_brightness",
                        "stars": ["thai_duong"],
                        "brightness": ["dac", "vuong", "mieu"],
                    },
                    {
                        "type": "star_brightness",
                        "stars": ["thai_am"],
                        "brightness": ["dac", "vuong", "mieu"],
                    },
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": ["tuan", "triet", "dia_khong", "dia_kiep"],
                        }
                    },
                ]
            },
        },
        _MinimalLaSo(
            {
                "thien_ma": DiaChi.SUU,
                "thai_am": DiaChi.SUU,
                "thai_duong": DiaChi.MUI,
            },
            {Role.MENH: DiaChi.SUU},
        ),
        Role.MENH,
        id="thu_hung_ma",
    ),
    pytest.param(
        {
            "id": "dich_ma",
            "name": "Dich Ma",
            "page": 42,
            "priority": 1,
            "meaning": "Nang dong, thao vat",
            "conditions": {
                "all": [
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": [
                                "tuan",
                                "triet",
                                "da_la",
                                "tuyet",
                                "thien_hinh",
                                "hoa_ky",
                                "dia_khong",
                                "dia_kiep",
                                "hoa_tinh",
                                "linh_tinh",
                            ],
                        }
                    },
                    {
                        "any": [
                            {
                                "type": "star_with_palace",
                                "palace": "menh",
                                "scope": "dong_cung",
                                "stars": ["thien_ma"],
                            },
                            {
                                "type": "star_with_palace",
                                "palace": "menh",
                                "scope": "dong_cung",
                                "stars": ["thien_ma"],
                            },
                        ]
                    },
                ]
            },
        },
        _MinimalLaSo({"thien_ma": DiaChi.TY}),
        Role.MENH,
        id="dich_ma",
    ),
    pytest.param(
        {
            "id": "ma_khoc_khach",
            "name": "Ma Khoc Khach",
            "page": 42,
            "priority": 1,
            "meaning": "Co tai, co nghi luc",
            "conditions": {
                "all": [
                    {
                        "type": "stars_meeting",
                        "scope": "dong_cung",
                        "stars": ["thien_ma", "thien_khoc", "thien_hu"],
                    },
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["thien_ma"],
                    },
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": [
                                "dia_khong",
                                "dia_kiep",
                                "tuan",
                                "triet",
                                "kinh_duong",
                                "da_la",
                                "tuyet",
                                "hoa_tinh",
                                "linh_tinh",
                            ],
                        }
                    },
                ]
            },
        },
        _MinimalLaSo(
            {
                "thien_ma": DiaChi.TY,
                "thien_khoc": DiaChi.TY,
                "thien_hu": DiaChi.TY,
            }
        ),
        [Role.MENH, Role.CUNG_THAN],
        id="ma_khoc_khach",
    ),
    pytest.param(
        {
            "id": "chien_ma",
            "name": "Chien Ma",
            "page": 42,
            "priority": 0,
            "meaning": "Dung manh",
            "conditions": {
                "all": [
                    {
                        "any": [
                            {
                                "all": [
                                    {
                                        "type": "stars_meeting",
                                        "scope": "dong_cung",
                                        "stars": ["thien_ma", "hoa_tinh"],
                                    },
                                    {
                                        "type": "star_brightness",
                                        "stars": ["hoa_tinh"],
                                        "brightness": ["dac", "vuong", "mieu"],
                                    },
                                ]
                            },
                            {
                                "all": [
                                    {
                                        "type": "stars_meeting",
                                        "scope": "dong_cung",
                                        "stars": ["thien_ma", "linh_tinh"],
                                    },
                                    {
                                        "type": "star_brightness",
                                        "stars": ["linh_tinh"],
                                        "brightness": ["dac", "vuong", "mieu"],
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        "any": [
                            {
                                "type": "star_with_palace",
                                "palace": "menh",
                                "scope": "dong_cung",
                                "stars": ["thien_ma"],
                            },
                            {
                                "type": "star_with_palace",
                                "palace": "cung_than",
                                "scope": "dong_cung",
                                "stars": ["thien_ma"],
                            },
                        ]
                    },
                ]
            },
        },
        _MinimalLaSo(
            {"thien_ma": DiaChi.DAN, "hoa_tinh": DiaChi.DAN},
            {Role.MENH: DiaChi.DAN},
        ),
        Role.MENH,
        id="chien_ma",
    ),
    pytest.param(
        {
            "id": "phu_thi_ma",
            "name": "Phu Thi Ma",
            "page": 42,
            "priority": 1,
            "meaning": "Ngua cho xac chet",
            "conditions": {
                "all": [
                    {
                        "type": "stars_meeting",
                        "scope": "dong_cung",
                        "stars": ["thien_ma", "thien_hinh"],
                    }
                ]
            },
        },
        _MinimalLaSo({"thien_ma": DiaChi.TY, "thien_hinh": DiaChi.TY}),
        [Role.MENH, Role.CUNG_THAN],
        id="phu_thi_ma",
    ),
    pytest.param(
        {
            "id": "chiet_tuc_ma",
            "name": "Chiet Tuc Ma",
            "page": 42,
            "priority": 0,
            "meaning": "Ngua que",
            "conditions": {
                "all": [
                    {
                        "type": "stars_meeting",
                        "scope": "dong_hoac_xung",
                        "stars": ["thien_ma", "da_la"],
                    },
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["thien_ma"],
                    },
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": ["tuan", "triet"],
                        }
                    },
                ]
            },
        },
        _MinimalLaSo({"thien_ma": DiaChi.TY, "da_la": DiaChi.NGO}),
        [Role.MENH, Role.CUNG_THAN, Role.THIEN_DI],
        id="chiet_tuc_ma",
    ),
    pytest.param(
        {
            "id": "tu_ma",
            "name": "Tu Ma",
            "page": 42,
            "priority": 0,
            "meaning": "Ma lac Khong Vong",
            "conditions": {
                "all": [
                    {
                        "any": [
                            {
                                "type": "stars_meeting",
                                "scope": "dong_cung",
                                "stars": ["thien_ma", "tuan"],
                            },
                            {
                                "type": "stars_meeting",
                                "scope": "dong_cung",
                                "stars": ["thien_ma", "triet"],
                            },
                        ]
                    },
                    {
                        "any": [
                            {
                                "type": "star_with_palace",
                                "palace": "menh",
                                "scope": "dong_cung",
                                "stars": ["thien_ma"],
                            },
                            {
                                "type": "star_with_palace",
                                "palace": "cung_than",
                                "scope": "dong_cung",
                                "stars": ["thien_ma"],
                            },
                        ]
                    },
                ]
            },
        },
        _MinimalLaSo({"thien_ma": DiaChi.TY, "tuan_1": DiaChi.TY}),
        [Role.MENH, Role.CUNG_THAN],
        id="tu_ma",
    ),
    pytest.param(
        {
            "id": "ho_ham_kiem",
            "name": "Ho ham kiem",
            "page": 43,
            "priority": 1,
            "meaning": "Dung manh tai gioi",
            "conditions": {
                "all": [
                    {"type": "palace_at", "palace": "menh", "chi": ["dan"]},
                    {
                        "type": "star_with_palace",
                        "palace": "menh",
                        "scope": "dong_cung",
                        "stars": ["thien_hinh"],
                    },
                    {
                        "type": "stars_meeting",
                        "scope": "dong_cung",
                        "stars": ["bach_ho", "thien_hinh"],
                    },
                    {
                        "not": {
                            "type": "star_with_palace",
                            "palace": "menh",
                            "scope": "dong_cung",
                            "stars": ["tuan", "triet"],
                        }
                    },
                ]
            },
        },
        _MinimalLaSo(
            {"bach_ho": DiaChi.DAN, "thien_hinh": DiaChi.DAN},
            {Role.MENH: DiaChi.DAN},
        ),
        Role.MENH,
        id="ho_ham_kiem",
    ),
]


def _minimal_laso_for_reviewed_entries() -> _MinimalLaSo:
    return _MinimalLaSo(
        {
            "bach_ho": DiaChi.TY,
            "tau_thu": DiaChi.TY,
            "thai_duong": DiaChi.TY,
            "da_la": DiaChi.TY,
            "hoa_ky": DiaChi.NGO,
            "thien_dieu": DiaChi.THIN,
        }
    )


def test_reviewed_cach_cuc_source_loads():
    data = load_cach_cuc_source(SourceKind.TUVITANBIEN)

    assert data.cach_cuc
    assert data.groups


def test_matches_reviewed_cach_cuc_chosen_from_first_200_lines():
    matches = find_matching_cach_cuc(
        _minimal_laso_for_reviewed_entries(),
        data=_reviewed_first_200_line_data(),
    )

    assert [match.id for match in matches] == ["tam_am", "ho_do_hom_sat"]
    assert matches[0].related_roles == [Role.MENH, Role.CUNG_THAN]
    assert matches[1].related_roles == [Role.MENH, Role.CUNG_THAN]


@pytest.mark.parametrize("entry,la_so,expected_related_roles", MORE_REVIEWED_CASES)
def test_more_reviewed_cach_cuc_use_cases(
    entry: dict,
    la_so: _MinimalLaSo,
    expected_related_roles: Role | list[Role] | None,
):
    matches = find_matching_cach_cuc(
        la_so,
        data=_data_from_reviewed_entries([entry]),
    )

    assert [match.id for match in matches] == [entry["id"]]
    if isinstance(expected_related_roles, Role):
        expected_related_roles = [expected_related_roles]
    assert matches[0].related_roles == (expected_related_roles or [])


def test_filtered_roles_include_general_reviewed_cach_cuc():
    matches = find_matching_cach_cuc(
        _minimal_laso_for_reviewed_entries(),
        data=_reviewed_first_200_line_data(),
        filtered_roles=[Role.MENH],
    )

    assert [match.id for match in matches] == ["tam_am", "ho_do_hom_sat"]
    assert matches[0].related_roles == [Role.MENH, Role.CUNG_THAN]
    assert matches[1].related_roles == [Role.MENH, Role.CUNG_THAN]


def test_tuan_triet_aliases_can_block_reviewed_cach_cuc():
    blocked_laso = _MinimalLaSo(
        {
            "bach_ho": DiaChi.TY,
            "tau_thu": DiaChi.TY,
            "tuan_1": DiaChi.TY,
            "thai_duong": DiaChi.TY,
            "da_la": DiaChi.TY,
            "hoa_ky": DiaChi.NGO,
            "thien_dieu": DiaChi.THIN,
        }
    )

    matches = find_matching_cach_cuc(
        blocked_laso,
        data=_reviewed_first_200_line_data(),
    )

    assert [match.id for match in matches] == ["tam_am"]


def test_tool_result_projection_omits_conditions():
    matches = find_matching_cach_cuc(
        _minimal_laso_for_reviewed_entries(),
        data=_reviewed_first_200_line_data(),
    )

    result = CachCucToolResult.from_cach_cuc(matches[1])

    assert result.id == "ho_do_hom_sat"
    assert result.related_roles == [Role.MENH, Role.CUNG_THAN]
    assert "conditions" not in CachCucToolResult.model_fields
