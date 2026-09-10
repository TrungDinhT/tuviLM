from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from src.refactored.components.definitions import ChinhPhuTinh, TuanTriet
from src.refactored.la_so import LaSo
from src.refactored.model.layer import NATAL_LAYER_ID

DEFAULT_CAU_PHU_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "cung_menh_phu_luc_bat_v3_tieu_de_moi.json"
)

type CaseKey = tuple[str, tuple[str, ...], bool, bool]


class CauPhuDataError(RuntimeError):
    """Raised when the phú catalog is malformed or contains duplicate cases."""


class CauPhuNotFoundError(LookupError):
    """Raised when a natal chart has no corresponding phú in the catalog."""


@dataclass(frozen=True, slots=True)
class CauPhuLookupKey:
    vi_tri: str
    chinh_tinh: tuple[str, ...]
    co_tuan: bool
    co_triet: bool

    @property
    def key(self) -> CaseKey:
        return _case_key(
            vi_tri=self.vi_tri,
            chinh_tinh=self.chinh_tinh,
            co_tuan=self.co_tuan,
            co_triet=self.co_triet,
        )


@dataclass(frozen=True, slots=True)
class CauPhuEntry:
    vi_tri: str
    chinh_tinh: tuple[str, ...]
    co_tuan: bool
    co_triet: bool
    tuan_triet: str
    tieu_de: str
    cau_phu: str
    cac_cau: tuple[str, ...]


def _case_key(
    *,
    vi_tri: str,
    chinh_tinh: tuple[str, ...],
    co_tuan: bool,
    co_triet: bool,
) -> CaseKey:
    # Thứ tự hai chính tinh không làm thay đổi cấu hình cần đối chiếu.
    return vi_tri, tuple(sorted(chinh_tinh)), co_tuan, co_triet


def _required_value(
    raw_case: dict[str, Any],
    field_name: str,
    expected_type: type,
    *,
    case_number: int,
) -> Any:
    value = raw_case.get(field_name)
    if not isinstance(value, expected_type):
        raise CauPhuDataError(
            f"Trường hợp {case_number}: field {field_name!r} phải có kiểu "
            f"{expected_type.__name__}."
        )
    return value


@cache
def load_cau_phu_catalog(
    path: Path = DEFAULT_CAU_PHU_PATH,
) -> Mapping[CaseKey, CauPhuEntry]:
    """Load and index all phú entries without modifying their original text."""
    try:
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise CauPhuDataError(f"Không thể đọc dữ liệu câu phú: {path}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("truong_hop"), list):
        raise CauPhuDataError(
            "Dữ liệu câu phú phải là object có field 'truong_hop' dạng array."
        )

    index: dict[CaseKey, CauPhuEntry] = {}
    for case_number, raw_case in enumerate(payload["truong_hop"], start=1):
        if not isinstance(raw_case, dict):
            raise CauPhuDataError(f"Trường hợp {case_number} phải là một JSON object.")

        raw_chinh_tinh = _required_value(
            raw_case, "chinh_tinh", list, case_number=case_number
        )
        raw_cac_cau = _required_value(
            raw_case, "cac_cau", list, case_number=case_number
        )
        if not all(isinstance(star, str) for star in raw_chinh_tinh):
            raise CauPhuDataError(
                f"Trường hợp {case_number}: mọi chính tinh phải là chuỗi."
            )
        if not all(isinstance(line, str) for line in raw_cac_cau):
            raise CauPhuDataError(
                f"Trường hợp {case_number}: mọi câu phú phải là chuỗi."
            )

        entry = CauPhuEntry(
            vi_tri=_required_value(raw_case, "vi_tri", str, case_number=case_number),
            chinh_tinh=tuple(raw_chinh_tinh),
            co_tuan=_required_value(raw_case, "co_tuan", bool, case_number=case_number),
            co_triet=_required_value(
                raw_case, "co_triet", bool, case_number=case_number
            ),
            tuan_triet=_required_value(
                raw_case, "tuan_triet", str, case_number=case_number
            ),
            tieu_de=_required_value(raw_case, "tieu_de", str, case_number=case_number),
            cau_phu=_required_value(raw_case, "cau_phu", str, case_number=case_number),
            cac_cau=tuple(raw_cac_cau),
        )
        key = _case_key(
            vi_tri=entry.vi_tri,
            chinh_tinh=entry.chinh_tinh,
            co_tuan=entry.co_tuan,
            co_triet=entry.co_triet,
        )
        if key in index:
            raise CauPhuDataError(
                f"Trùng cấu hình câu phú tại trường hợp {case_number}: {key!r}."
            )
        index[key] = entry

    declared_count = payload.get("so_truong_hop")
    if declared_count is not None and declared_count != len(index):
        raise CauPhuDataError(
            "Field 'so_truong_hop' không khớp số trường hợp thực tế: "
            f"{declared_count!r} != {len(index)}."
        )

    return MappingProxyType(index)


def extract_cau_phu_lookup_key(la_so: LaSo) -> CauPhuLookupKey:
    """Extract the exact four-part lookup key from a completed natal chart."""
    menh_position = la_so.position_of("menh", NATAL_LAYER_ID)
    if menh_position is None:
        raise CauPhuNotFoundError("Không tìm thấy cung Mệnh trong lá số.")

    chinh_tinh: list[str] = []
    co_tuan = False
    co_triet = False

    for component_id in la_so.cung_at(menh_position).components_in_layer(
        NATAL_LAYER_ID
    ):
        component = la_so.component(component_id)
        if isinstance(component, ChinhPhuTinh) and component.is_chinh_tinh:
            chinh_tinh.append(component.name)
        elif isinstance(component, TuanTriet):
            co_tuan = co_tuan or component.name == "Tuần"
            co_triet = co_triet or component.name == "Triệt"

    return CauPhuLookupKey(
        vi_tri=la_so.component(menh_position.value).name,
        chinh_tinh=tuple(chinh_tinh),
        co_tuan=co_tuan,
        co_triet=co_triet,
    )


def find_cau_phu(
    lookup_key: CauPhuLookupKey,
    *,
    catalog_path: Path = DEFAULT_CAU_PHU_PATH,
) -> CauPhuEntry:
    """Return the Câu Phú matching one normalized lookup key."""
    try:
        return load_cau_phu_catalog(catalog_path)[lookup_key.key]
    except KeyError as exc:
        raise CauPhuNotFoundError(
            "Không có câu phú cho cấu hình cung Mệnh: "
            f"vị trí={lookup_key.vi_tri!r}, "
            f"chính tinh={list(lookup_key.chinh_tinh)!r}, "
            f"Tuần={lookup_key.co_tuan}, Triệt={lookup_key.co_triet}."
        ) from exc


def get_cau_phu(la_so: LaSo) -> CauPhuEntry:
    """Extract a completed chart's signature and return its matching phú."""
    return find_cau_phu(extract_cau_phu_lookup_key(la_so))
