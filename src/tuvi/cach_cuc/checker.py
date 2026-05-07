"""Cách Cục checker — evaluates structured YAML conditions against a TinhBan.

Ported from tuvi_agent's tan_bien.cach_cuc_checker. Adapted to read from
tuviLM's `TinhBan` / `Cung` model. Each of the 12 cung is treated as a
possible "anchor" — conditions reference the anchor as `palace: Menh`.

Entries that explicitly target a non-anchor palace (a role like `QuanLoc`
or a fixed chi like `Dan`) attach only to that specific palace.
"""

from __future__ import annotations

import json
import logging
from enum import Enum
from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from src.tuvi.element.map_star_status import MAP_START_STATUS
from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI
from src.tuvi.tinh_ban import TinhBan

logger = logging.getLogger(__name__)


_DATA_DIR = Path(__file__).parent / "data"
_CACH_CUC_PATH = _DATA_DIR / "cach_cuc.yaml"
_STARS_PATH = _DATA_DIR / "stars.json"


# ── Tam hợp triangles by chi index ──
TAM_HOP_GROUPS: tuple[frozenset[int], ...] = (
    frozenset({0, 4, 8}),
    frozenset({1, 5, 9}),
    frozenset({2, 6, 10}),
    frozenset({3, 7, 11}),
)

# Nhị hợp pairs.
NHI_HOP_PAIRS: dict[int, int] = {
    0: 1, 1: 0,
    2: 11, 11: 2,
    3: 10, 10: 3,
    4: 9, 9: 4,
    5: 8, 8: 5,
    6: 7, 7: 6,
}


# ── Cung role alias (YAML key → tuviLM role) ──
_CUNG_ALIASES: dict[str, str] = {
    "menh": "Mệnh",
    "phumau": "Phụ Mẫu",
    "phumy": "Phụ Mẫu",
    "phucduc": "Phúc Đức",
    "dientrach": "Điền Trạch",
    "quanloc": "Quan Lộc",
    "noboc": "Nô Bộc",
    "thiendi": "Thiên Di",
    "tatach": "Tật Ách",
    "taibach": "Tài Bạch",
    "tutuc": "Tử Tức",
    "thethiep": "Phu Thê",
    "phuthe": "Phu Thê",
    "huynhde": "Huynh Đệ",
}


def _normalize_cung_alias(s: str) -> str | None:
    key = s.replace(" ", "").replace("_", "").lower()
    return _CUNG_ALIASES.get(key)


# ── Chi resolution ──
# YAML chi tokens are ASCII-stripped enum names (e.g. "Dan", "Mao"). The
# diacritic "Tỵ" / "Ti" / "Ty_Snake" all resolve to the Snake (index 5).
# Bare "Ty" resolves to Tý (index 0).
_CHI_NAME_TO_INDEX: dict[str, int] = {
    "ty": 0,
    "suu": 1,
    "dan": 2,
    "mao": 3,
    "thin": 4,
    "ti": 5,
    "ty_snake": 5,
    "tỵ": 5,
    "ngo": 6,
    "mui": 7,
    "than": 8,
    "dau": 9,
    "tuat": 10,
    "hoi": 11,
}

_DISPLAY_TO_INDEX: dict[str, int] = {
    display.lower(): idx for idx, display in enumerate(LIST_DIA_CHI)
}


def _resolve_chi(ref: str) -> int | None:
    low = ref.lower()
    if low in _CHI_NAME_TO_INDEX:
        return _CHI_NAME_TO_INDEX[low]
    if low in _DISPLAY_TO_INDEX:
        return _DISPLAY_TO_INDEX[low]
    return None


# ── Year can ASCII conversion ──
_CAN_TO_ASCII: dict[str, str] = {
    "Giấp": "Giap",
    "Ất": "At",
    "Bính": "Binh",
    "Đinh": "Dinh",
    "Mậu": "Mau",
    "Kỷ": "Ki",
    "Canh": "Canh",
    "Tân": "Tan",
    "Nhâm": "Nham",
    "Quý": "Quy",
}


def _can_to_ascii(can: str) -> str:
    return _CAN_TO_ASCII.get(can, can)


_GENDER_TO_ASCII: dict[str, str] = {"M": "male", "F": "female"}


# ── Brightness ──
_STATUS_TO_BRIGHT: dict[str, str] = {
    "Hãm": "ham",
    "Bình": "binh",
    "Đắc": "dac",
    "Vượng": "vuong",
    "Miếu": "mieu",
}


# ── Star id registry (id → display name + categories) ──
# Overrides for stars whose tuviLM display name differs from stars.json.
_STAR_NAME_OVERRIDES: dict[str, str] = {
    "thien_rieu": "Thiên Diêu",   # tuviLM uses Diêu
    "de_vuong": "Đế  Vương",       # tuviLM has typo (double space + Vương)
    "luc_sy": "Lực Sĩ",
    "thien_thuong": "Thiên Thuơng",  # tuviLM typo (Thuơng)
    "tuan_trung": "Tuần Trung",
    "triet_lo": "Triệt Lộ",
}


@cache
def _stars_data() -> dict[str, dict]:
    if not _STARS_PATH.exists():
        return {}
    with open(_STARS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return raw.get("stars", {})


@cache
def _star_id_to_name() -> dict[str, str]:
    out: dict[str, str] = {}
    for sid, info in _stars_data().items():
        out[sid] = _STAR_NAME_OVERRIDES.get(sid, info.get("name", sid))
    for sid, name in _STAR_NAME_OVERRIDES.items():
        out.setdefault(sid, name)
    return out


@cache
def _category_star_names() -> dict[str, list[str]]:
    cats: dict[str, list[str]] = {}
    for sid, info in _stars_data().items():
        name = _STAR_NAME_OVERRIDES.get(sid, info.get("name", sid))
        for cat in info.get("categories", []):
            cats.setdefault(cat, []).append(name)
    return cats


@cache
def _chinh_tinh_names() -> set[str]:
    return set(_category_star_names().get("chinh_tinh", []))


# ── Enums ──
class Scope(str, Enum):
    DONG_CUNG = "dong_cung"
    XUNG_CHIEU = "xung_chieu"
    TAM_HOP = "tam_hop"
    HOI_HOP = "hoi_hop"
    NHI_HOP = "nhi_hop"
    DONG_HOAC_XUNG = "dong_hoac_xung"


class ConditionType(str, Enum):
    STAR_IN_PALACE = "star_in_palace"
    STARS_TOGETHER = "stars_together"
    STARS_OPPOSITE = "stars_opposite"
    STARS_MEETING = "stars_meeting"
    STAR_BRIGHTNESS = "star_brightness"
    CAN_MATCH = "can_match"
    CAN_EXCLUDE = "can_exclude"
    GENDER_MATCH = "gender_match"
    PALACE_AT = "palace_at"
    NO_STARS = "no_stars"
    STAR_AT_CHI = "star_at_chi"
    STAR_AT_FIXED_CHI = "star_at_fixed_chi"
    STARS_GIAP = "stars_giap"
    STARS_GIAP_ORDERED = "stars_giap_ordered"
    BRIGHT_CHINH_TINH = "bright_chinh_tinh"
    ONLY_CHINH_TINH = "only_chinh_tinh"
    STARS_XOR = "stars_xor"


# ── Pydantic models ──
class Condition(BaseModel):
    type: ConditionType
    stars: list[str] | None = None
    palace: str | None = None
    scope: Scope | None = None
    star: str | None = None
    brightness: list[str] | None = None
    can: list[str] | None = None
    gender: str | None = None
    chi: list[str] | None = None
    group: str | None = None
    in_palace: str | None = None
    at_chi: list[str] | None = None
    mode: str | None = None
    prev_stars: list[str] | None = None
    next_stars: list[str] | None = None

    model_config = {"extra": "forbid"}


class ConditionBlock(BaseModel):
    all: list[Condition | ConditionBlock] | None = None
    any: list[Condition | ConditionBlock] | None = None

    model_config = {"extra": "forbid"}


class CachCucEntry(BaseModel):
    id: str
    name: str
    page: int
    meaning: str
    applicable_palaces: list[str] | None = Field(default_factory=lambda: ["Menh"])
    conditions: ConditionBlock

    model_config = {"extra": "forbid"}


class StarGroup(BaseModel):
    stars: list[str] | None = None
    categories: list[str] | None = None

    model_config = {"extra": "forbid"}


class CachCucConfig(BaseModel):
    groups: dict[str, StarGroup] = {}
    cach_cuc: list[CachCucEntry]

    model_config = {"extra": "forbid"}


class CachCucMatch(BaseModel):
    id: str
    name: str
    page: int
    meaning: str
    palace: TYPE_DIA_CHI
    role: str | None = None


# ── Board ──
class BoardIndex:
    """Pre-computed lookups from a TinhBan, parameterized by anchor."""

    def __init__(
        self,
        tinh_ban: TinhBan,
        year_can_ascii: str,
        gender_ascii: str,
        anchor_idx: int,
    ) -> None:
        self.star_positions: dict[str, list[int]] = {}
        self.star_brightness: dict[str, list[tuple[int, str | None]]] = {}
        self.stars_at: dict[int, set[str]] = {idx: set() for idx in range(12)}
        self.menh_index: int | None = None
        self.than_index: int | None = None

        for idx, dia_chi in enumerate(LIST_DIA_CHI):
            cung = tinh_ban.map_cung[dia_chi]
            if cung.role == "Mệnh":
                self.menh_index = idx
            if cung.is_cung_than:
                self.than_index = idx

            stars: list[tuple[str, str | None]] = []

            for star in cung.chinhTinh:
                status = MAP_START_STATUS.get(star.name, {}).get(dia_chi)
                bright = _STATUS_TO_BRIGHT.get(status) if status else None
                stars.append((star.name, bright))

            for star in cung.phuTinh:
                stars.append((star.name, None))

            for tuhoa in cung.tuhoa:
                stars.append((tuhoa.name, None))

            if cung.trang_sinh is not None:
                stars.append((cung.trang_sinh.name, None))

            if cung.is_tuan:
                stars.append(("Tuần Trung", None))
            if cung.is_triet:
                stars.append(("Triệt Lộ", None))

            for sname, bright in stars:
                self.stars_at[idx].add(sname)
                self.star_positions.setdefault(sname, []).append(idx)
                self.star_brightness.setdefault(sname, []).append((idx, bright))

        self.year_can = year_can_ascii
        self.gender = gender_ascii
        self.anchor_idx = anchor_idx
        self._tinh_ban = tinh_ban

    def resolve_palace_index(self, palace: str) -> int | None:
        if palace == "Menh":
            return self.anchor_idx
        if palace == "Than":
            return self.than_index
        alias = _normalize_cung_alias(palace)
        if alias is not None:
            for idx, dia_chi in enumerate(LIST_DIA_CHI):
                if self._tinh_ban.map_cung[dia_chi].role == alias:
                    return idx
        for idx, dia_chi in enumerate(LIST_DIA_CHI):
            if self._tinh_ban.map_cung[dia_chi].role == palace:
                return idx
        return _resolve_chi(palace)

    def stars_in_palace(self, idx: int) -> set[str]:
        return self.stars_at.get(idx, set())

    def star_at_indices(self, star: str) -> list[int]:
        return self.star_positions.get(star, [])


# ── Group resolver ──
class GroupResolver:
    def __init__(self, config: CachCucConfig) -> None:
        self.groups = config.groups
        self._id_map = _star_id_to_name()

    def _resolve_star(self, ref: str) -> list[str]:
        if ref in self.groups:
            return self._expand_group(ref)
        if ref in self._id_map:
            return [self._id_map[ref]]
        return [ref]

    def _expand_group(self, name: str) -> list[str]:
        g = self.groups[name]
        result: list[str] = []
        if g.stars:
            for sid in g.stars:
                if sid in self._id_map:
                    result.append(self._id_map[sid])
                else:
                    result.append(sid)
        if g.categories:
            cat_map = _category_star_names()
            for cat in g.categories:
                result.extend(cat_map.get(cat, []))
        return result

    def resolve(self, refs: list[str] | None, group: str | None) -> list[str]:
        result: list[str] = []
        if refs:
            for r in refs:
                result.extend(self._resolve_star(r))
        if group:
            result.extend(self._expand_group(group))
        return result


# ── Scope helpers ──
def _tam_hop_group(idx: int) -> frozenset[int]:
    for group in TAM_HOP_GROUPS:
        if idx in group:
            return group
    return frozenset({idx})


def _in_scope(pos_a: int, pos_b: int, scope: Scope) -> bool:
    if scope == Scope.DONG_CUNG:
        return pos_a == pos_b
    if scope == Scope.XUNG_CHIEU:
        return (pos_a + 6) % 12 == pos_b
    if scope == Scope.TAM_HOP:
        return pos_b in _tam_hop_group(pos_a)
    if scope == Scope.HOI_HOP:
        return (
            pos_a == pos_b
            or (pos_a + 6) % 12 == pos_b
            or pos_b in _tam_hop_group(pos_a)
        )
    if scope == Scope.NHI_HOP:
        return NHI_HOP_PAIRS.get(pos_a) == pos_b
    if scope == Scope.DONG_HOAC_XUNG:
        return pos_a == pos_b or (pos_a + 6) % 12 == pos_b
    return False


# ── Condition evaluator (anchor-aware) ──
def _eval_condition(cond: Condition, board: BoardIndex, resolver: GroupResolver) -> bool:
    try:
        return _eval_inner(cond, board, resolver)
    except Exception:
        logger.debug("Error evaluating condition %s", cond.type, exc_info=True)
        return False


def _eval_inner(cond: Condition, board: BoardIndex, resolver: GroupResolver) -> bool:
    t = cond.type
    anchor = board.anchor_idx

    if t == ConditionType.STAR_IN_PALACE:
        stars = resolver.resolve(cond.stars, cond.group)
        palace_idx = board.resolve_palace_index(cond.palace)
        if palace_idx is None:
            return False
        return any(s in board.stars_in_palace(palace_idx) for s in stars)

    if t == ConditionType.STARS_TOGETHER:
        stars = resolver.resolve(cond.stars, cond.group)
        if not stars:
            return False
        return all(anchor in board.star_at_indices(s) for s in stars)

    if t == ConditionType.STARS_OPPOSITE:
        stars = resolver.resolve(cond.stars, cond.group)
        if len(stars) < 2:
            return False
        if anchor not in board.star_at_indices(stars[0]):
            return False
        xung = (anchor + 6) % 12
        return all(xung in board.star_at_indices(s) for s in stars[1:])

    if t == ConditionType.STARS_MEETING:
        stars = resolver.resolve(cond.stars, cond.group)
        scope = cond.scope or Scope.HOI_HOP
        mode = (cond.mode or "all").lower()
        if not stars:
            return False
        per_star = (
            any(_in_scope(anchor, sp, scope) for sp in board.star_at_indices(s))
            for s in stars
        )
        if mode == "any":
            return any(per_star)
        return all(per_star)

    if t == ConditionType.STAR_BRIGHTNESS:
        star = cond.star
        if star:
            resolved = resolver.resolve([star], None)
            star = resolved[0] if resolved else ""
        if not star:
            return False
        target_idx = board.resolve_palace_index(cond.palace or "Menh")
        allowed = set(cond.brightness or [])
        for idx, bright in board.star_brightness.get(star, []):
            if target_idx is not None and idx != target_idx:
                continue
            if bright in allowed:
                return True
        return False

    if t == ConditionType.CAN_MATCH:
        return board.year_can in (cond.can or [])

    if t == ConditionType.CAN_EXCLUDE:
        return board.year_can not in (cond.can or [])

    if t == ConditionType.GENDER_MATCH:
        return board.gender == cond.gender

    if t == ConditionType.PALACE_AT:
        palace_idx = board.resolve_palace_index(cond.palace or "Menh")
        if palace_idx is None or not cond.chi:
            return False
        chi_targets: set[int] = set()
        for c in cond.chi:
            idx = _resolve_chi(c)
            if idx is not None:
                chi_targets.add(idx)
        return palace_idx in chi_targets

    if t == ConditionType.NO_STARS:
        forbidden = resolver.resolve(cond.stars, cond.group)
        target_ref = cond.in_palace or "Menh"
        idx = board.resolve_palace_index(target_ref)
        if idx is None:
            return True
        palace_stars = board.stars_in_palace(idx)
        return not any(s in palace_stars for s in forbidden)

    if t == ConditionType.STAR_AT_CHI:
        stars = resolver.resolve(cond.stars, cond.group)
        target_indices: set[int] = set()
        for c in cond.at_chi or []:
            idx = _resolve_chi(c)
            if idx is not None:
                target_indices.add(idx)
        if anchor not in target_indices:
            return False
        return any(anchor in board.star_at_indices(s) for s in stars)

    if t == ConditionType.STAR_AT_FIXED_CHI:
        if not cond.star:
            return False
        resolved = resolver.resolve([cond.star], None)
        if not resolved:
            return False
        star = resolved[0]
        target_indices: set[int] = set()
        for c in cond.chi or []:
            idx = _resolve_chi(c)
            if idx is not None:
                target_indices.add(idx)
        if not target_indices:
            return False
        return any(p in target_indices for p in board.star_at_indices(star))

    if t == ConditionType.STARS_GIAP:
        stars = resolver.resolve(cond.stars, cond.group)
        if not stars:
            return False
        prev_idx = (anchor - 1) % 12
        next_idx = (anchor + 1) % 12
        prev_set = board.stars_in_palace(prev_idx)
        next_set = board.stars_in_palace(next_idx)
        if len(stars) == 2:
            a, b = stars
            return (a in prev_set and b in next_set) or (b in prev_set and a in next_set)
        adjacent = prev_set | next_set
        return all(s in adjacent for s in stars)

    if t == ConditionType.STARS_GIAP_ORDERED:
        prev_set = board.stars_in_palace((anchor - 1) % 12)
        next_set = board.stars_in_palace((anchor + 1) % 12)
        prev_resolved = resolver.resolve(cond.prev_stars, None)
        next_resolved = resolver.resolve(cond.next_stars, None)
        if not prev_resolved or not next_resolved:
            return False
        return any(s in prev_set for s in prev_resolved) and any(
            s in next_set for s in next_resolved
        )

    if t == ConditionType.BRIGHT_CHINH_TINH:
        chinh = _chinh_tinh_names()
        bright_set = {"mieu", "vuong", "dac"}
        for sname in board.stars_in_palace(anchor):
            if sname not in chinh:
                continue
            for idx, b in board.star_brightness.get(sname, []):
                if idx == anchor and b in bright_set:
                    return True
        return False

    if t == ConditionType.ONLY_CHINH_TINH:
        target = cond.palace or "Menh"
        idx = board.resolve_palace_index(target)
        if idx is None or not cond.star:
            return False
        resolved = resolver.resolve([cond.star], None)
        if not resolved:
            return False
        target_name = resolved[0]
        chinh = _chinh_tinh_names()
        present = [s for s in board.stars_in_palace(idx) if s in chinh]
        return present == [target_name]

    if t == ConditionType.STARS_XOR:
        stars = resolver.resolve(cond.stars, cond.group)
        scope = cond.scope or Scope.HOI_HOP
        if not stars:
            return False
        count = sum(
            1
            for s in stars
            if any(_in_scope(anchor, sp, scope) for sp in board.star_at_indices(s))
        )
        return count == 1

    return False


def _eval_node(node: Condition | ConditionBlock, board: BoardIndex, resolver: GroupResolver) -> bool:
    if isinstance(node, Condition):
        return _eval_condition(node, board, resolver)
    return _eval_block(node, board, resolver)


def _eval_block(block: ConditionBlock, board: BoardIndex, resolver: GroupResolver) -> bool:
    if not block.all and not block.any:
        return False
    if block.all and not all(_eval_node(n, board, resolver) for n in block.all):
        return False
    if block.any and not any(_eval_node(n, board, resolver) for n in block.any):
        return False
    return True


# ── Explicit-palace detection ──
def _explicit_palace_ref(block: ConditionBlock) -> str | None:
    for n in block.all or []:
        if isinstance(n, Condition):
            for ref in (n.palace, n.in_palace):
                if ref and ref != "Menh":
                    return ref
        else:
            r = _explicit_palace_ref(n)
            if r:
                return r
    return None


# ── Config loader ──
@cache
def load_config() -> CachCucConfig:
    if not _CACH_CUC_PATH.exists():
        logger.warning("Cach cuc YAML not found at %s", _CACH_CUC_PATH)
        return CachCucConfig(cach_cuc=[])
    with open(_CACH_CUC_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return CachCucConfig.model_validate(data)


# ── Filter helper ──
def _palace_matches_filter(
    tinh_ban: TinhBan, idx: int, filter_list: list[str]
) -> bool:
    dia_chi = LIST_DIA_CHI[idx]
    cung = tinh_ban.map_cung[dia_chi]
    pname = cung.role
    for ref in filter_list:
        if ref == "Menh" and cung.role == "Mệnh":
            return True
        if ref == "Than" and cung.is_cung_than:
            return True
        norm = _normalize_cung_alias(ref)
        if norm and norm == pname:
            return True
        if ref == pname:
            return True
    return False


# ── Public entry ──
def check_cach_cuc(
    tinh_ban: TinhBan,
    year_can: str = "",
    gender: str | None = None,
) -> dict[TYPE_DIA_CHI, list[CachCucMatch]]:
    """Return matched cách cục per palace (keyed by địa chi).

    Each of the 12 palaces is evaluated as the anchor cung. Entries with an
    explicit non-anchor palace reference attach only to that specific palace;
    other entries attach to any cung where their conditions hold.

    Args:
        tinh_ban: complete TinhBan
        year_can: year heavenly stem in tuviLM Vietnamese form (e.g. "Giấp")
        gender: "M" or "F"; defaults to tinh_ban.gender
    """
    config = load_config()
    result: dict[TYPE_DIA_CHI, list[CachCucMatch]] = {dc: [] for dc in LIST_DIA_CHI}
    if not config.cach_cuc:
        return result

    resolver = GroupResolver(config)
    year_can_ascii = _can_to_ascii(year_can)
    gender_raw = gender or tinh_ban.gender or ""
    gender_ascii = _GENDER_TO_ASCII.get(gender_raw, "")

    boards: dict[int, BoardIndex] = {
        idx: BoardIndex(tinh_ban, year_can_ascii, gender_ascii, anchor_idx=idx)
        for idx in range(12)
    }

    def _build_match(entry: CachCucEntry, idx: int) -> CachCucMatch:
        dc = LIST_DIA_CHI[idx]
        return CachCucMatch(
            id=entry.id,
            name=entry.name,
            page=entry.page,
            meaning=entry.meaning,
            palace=dc,
            role=tinh_ban.map_cung[dc].role,
        )

    for entry in config.cach_cuc:
        explicit = _explicit_palace_ref(entry.conditions)
        if explicit is not None:
            any_board = boards[0]
            target_idx = any_board.resolve_palace_index(explicit)
            if target_idx is None:
                continue
            if _eval_block(entry.conditions, boards[target_idx], resolver):
                result[LIST_DIA_CHI[target_idx]].append(_build_match(entry, target_idx))
        else:
            for idx, board in boards.items():
                if entry.applicable_palaces is not None:
                    if not _palace_matches_filter(tinh_ban, idx, entry.applicable_palaces):
                        continue
                if _eval_block(entry.conditions, board, resolver):
                    result[LIST_DIA_CHI[idx]].append(_build_match(entry, idx))

    return result


def check_cach_cuc_for_palace(
    tinh_ban: TinhBan,
    palace: TYPE_DIA_CHI,
    year_can: str = "",
    gender: str | None = None,
) -> list[CachCucMatch]:
    return check_cach_cuc(tinh_ban, year_can=year_can, gender=gender).get(palace, [])
