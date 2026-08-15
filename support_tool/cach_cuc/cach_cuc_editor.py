"""Streamlit editor for cach_cuc entries.

Run with:
    streamlit run support_tool/cach_cuc/cach_cuc_editor.py
"""

from __future__ import annotations

import json
import hashlib
import sys
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, get_args

import streamlit as st
import yaml
from pydantic import ValidationError

from support_tool.cach_cuc.condition_models import (
    Brightness,
    CachCuc,
    DiaChi,
    Gender,
    Mode,
    Role,
    Scope,
    ThienCan,
)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STARS_PATH = ROOT / "src/refactored/components/data/sao.json"
DEFAULT_EXPORT_FILENAME = "cach_cuc_reviewed.yaml"
SELECTED_ENTRY_WIDGET_KEY = "selected_entry_select"
ORIGINAL_ENTRY_PLACEHOLDER = ""

PALACES = [role.value for role in Role]
CHI = [chi.value for chi in DiaChi]
CAN = [can.value for can in ThienCan]
SCOPES_MEETING = list(get_args(Scope))
SCOPES_XOR = ["hoi_hop", "dong_hoac_xung", "dong_cung", "nhi_hop", "xung_chieu"]
GROUPS = [
    "luc_sat",
    "sat_tinh",
    "luc_cat",
    "cat_tinh",
    "tu_hoa",
    "tam_hoa",
    "xuong_khuc_khoa_tue_tau",
]
BRIGHTNESS = list(get_args(Brightness))
GENDERS = list(get_args(Gender))
MODES = list(get_args(Mode))
OPERATORS = ["all", "any"]

CONDITION_TYPES = [
    "can_exclude",
    "can_match",
    "cung_than_at_palace",
    "gender_match",
    "only_chinh_tinh",
    "palace_at",
    "star_at_chi",
    "star_brightness",
    "star_with_palace",
    "stars_meeting",
]
INCOMPATIBLE_CONDITION_TYPES = {"no_stars", "bright_chinh_tinh", "stars_xor"}
INCOMPATIBLE_EMPTY_FIELDS = {
    ("can_exclude", "can"),
    ("can_match", "can"),
    ("palace_at", "chi"),
    ("star_at_chi", "at_chi"),
    ("star_brightness", "brightness"),
}

DEFAULT_GROUPS = {
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
    "sat_tinh": {
        "stars": [
            "kinh_duong",
            "da_la",
            "dia_khong",
            "dia_kiep",
            "linh_tinh",
            "hoa_tinh",
        ]
    },
    "luc_cat": {
        "stars": [
            "ta_phu",
            "huu_bat",
            "thien_khoi",
            "thien_viet",
            "van_xuong",
            "van_khuc",
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
    "tu_hoa": {"stars": ["hoa_khoa", "hoa_quyen", "hoa_loc", "hoa_ky"]},
    "tam_hoa": {"stars": ["hoa_khoa", "hoa_quyen", "hoa_loc"]},
    "xuong_khuc_khoa_tue_tau": {
        "stars": ["van_xuong", "van_khuc", "hoa_khoa", "thai_tue", "tau_thu"]
    },
    "khong_kiep_hao_ky_tue": {
        "stars": ["dia_khong", "dia_kiep", "dai_hao", "tieu_hao", "hoa_ky", "thai_tue"]
    },
    "tu_phu_xuong_khuc_khoi_viet": {
        "stars": [
            "tu_vi",
            "thien_phu",
            "van_xuong",
            "van_khuc",
            "thien_khoi",
            "thien_viet",
        ]
    },
}

PALACE_ALIASES = {
    "menh": "menh",
    "mệnh": "menh",
    "than": "cung_than",
    "thân": "cung_than",
}

CAN_ALIASES = {
    "giap": "giap",
    "giáp": "giap",
    "at": "at",
    "ất": "at",
    "binh": "binh",
    "bính": "binh",
    "dinh": "dinh",
    "đinh": "dinh",
    "mau": "mau",
    "mậu": "mau",
    "ky": "ky",
    "kỷ": "ky",
    "canh": "canh",
    "tan": "tan",
    "tân": "tan",
    "nham": "nham",
    "nhâm": "nham",
    "quy": "quy",
    "quý": "quy",
}

CHI_ALIASES = {
    "ty": "ty",
    "tý": "ty",
    "ty_snake": "ti",
    "ti": "ti",
    "tị": "ti",
    "suu": "suu",
    "sửu": "suu",
    "dan": "dan",
    "dần": "dan",
    "mao": "meo",
    "mão": "meo",
    "meo": "meo",
    "mẹo": "meo",
    "thin": "thin",
    "thìn": "thin",
    "ngo": "ngo",
    "ngọ": "ngo",
    "mui": "mui",
    "mùi": "mui",
    "than": "than",
    "thân": "than",
    "dau": "dau",
    "dậu": "dau",
    "tuat": "tuat",
    "tuất": "tuat",
    "hoi": "hoi",
    "hợi": "hoi",
}

BRIGHTNESS_ALIASES = {
    "mieu": "mieu",
    "miếu": "mieu",
    "vuong": "vuong",
    "vượng": "vuong",
    "dac": "dac",
    "đắc": "dac",
    "binh hoa": "binh hoa",
    "bình hòa": "binh hoa",
    "binh_hoa": "binh hoa",
    "binh": "binh hoa",
    "bình": "binh hoa",
    "ham": "ham",
    "hãm": "ham",
}

STAR_ALIASES = {
    "thien_rieu": "thien_dieu",
}


@st.cache_data
def load_stars() -> list[str]:
    with STARS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    all_id = [s["id"] for s in data]
    all_id.extend(["hoa_quyen", "hoa_loc", "hoa_khoa", "hoa_ky", "tuan", "triet"])
    return all_id


def _new_key(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def normalize_token(value: Any, aliases: dict[str, str]) -> Any:
    if not isinstance(value, str):
        return value
    key = value.strip().casefold()
    return aliases.get(key, value)


def normalize_tokens(values: Any, aliases: dict[str, str]) -> Any:
    if not isinstance(values, list):
        return values
    return [normalize_token(value, aliases) for value in values]


def normalize_star_fields(cond: dict, notes: list[str]) -> None:
    if "star" in cond:
        old = cond["star"]
        cond["star"] = normalize_token(old, STAR_ALIASES)
        if old != cond["star"]:
            notes.append(f"star {old!r} -> {cond['star']!r}")
    if "stars" in cond:
        old = cond["stars"]
        cond["stars"] = normalize_tokens(old, STAR_ALIASES)
        if old != cond["stars"]:
            notes.append("star values normalized")


def normalize_leaf(raw: dict, notes: list[str]) -> dict:
    cond = deepcopy(raw)
    ctype = cond.get("type")

    legacy_scope_by_type = {
        "stars_together": "dong_cung",
        "stars_opposite": "xung_chieu",
        "stars_giap": "giap",
    }
    if ctype in legacy_scope_by_type:
        cond["type"] = "stars_meeting"
        cond.setdefault("scope", legacy_scope_by_type[ctype])
        notes.append(f"{ctype} -> stars_meeting(scope={cond['scope']})")
    elif ctype == "star_at_fixed_chi":
        cond["type"] = "star_at_chi"
        cond["at_chi"] = cond.pop("chi", cond.get("at_chi", []))
        notes.append("star_at_fixed_chi -> star_at_chi")
    elif ctype == "star_in_palace":
        cond["type"] = "star_with_palace"
        cond.setdefault("scope", "dong_cung")
        notes.append("star_in_palace -> star_with_palace(scope=dong_cung)")

    if (
        cond.get("type")
        in {"star_brightness", "star_with_palace", "star_at_chi", "stars_meeting"}
        and "star" in cond
        and "stars" not in cond
    ):
        cond["stars"] = [cond.pop("star")]
        notes.append("star -> stars")
    normalize_star_fields(cond, notes)
    if "group" in cond and "group_name" not in cond:
        cond["group_name"] = cond.pop("group")
        notes.append("group -> group_name")
    if (
        cond.get("type") in {"star_with_palace", "star_at_chi", "stars_meeting"}
        and cond.get("group_name") is None
    ):
        for field in ("mode", "at_least"):
            if cond.pop(field, None) is not None:
                notes.append(f"dropped {field} because no group_name is set")
    if cond.get("type") in {"star_with_palace", "stars_meeting"}:
        if cond.get("group_name") is None:
            cond.setdefault("stars_matching_logic", "any")
        else:
            cond["stars_matching_logic"] = None

    if "can" in cond:
        old = cond["can"]
        cond["can"] = normalize_tokens(old, CAN_ALIASES)
        if old != cond["can"]:
            notes.append("can values normalized")
    if "palace" in cond:
        old = cond["palace"]
        cond["palace"] = normalize_token(old, PALACE_ALIASES)
        if old != cond["palace"]:
            notes.append(f"palace {old!r} -> {cond['palace']!r}")
        elif cond.get("type") == "star_with_palace":
            chi_value = normalize_token(old, CHI_ALIASES)
            if chi_value in CHI:
                cond["type"] = "star_at_chi"
                cond["at_chi"] = [chi_value]
                cond.pop("palace", None)
                notes.append(
                    f"star_with_palace with chi-like palace {old!r} -> star_at_chi"
                )
    if "in_palace" in cond:
        old = cond["in_palace"]
        cond["in_palace"] = normalize_token(old, PALACE_ALIASES)
        if old != cond["in_palace"]:
            notes.append(f"in_palace {old!r} -> {cond['in_palace']!r}")
    for chi_field in ("chi", "at_chi"):
        if chi_field in cond:
            old = cond[chi_field]
            cond[chi_field] = normalize_tokens(old, CHI_ALIASES)
            if old != cond[chi_field]:
                notes.append(f"{chi_field} values normalized")
    if "brightness" in cond:
        old = cond["brightness"]
        cond["brightness"] = normalize_tokens(old, BRIGHTNESS_ALIASES)
        if old != cond["brightness"]:
            notes.append("brightness values normalized")

    for ctype_with_min_len, field in INCOMPATIBLE_EMPTY_FIELDS:
        if cond.get("type") == ctype_with_min_len and cond.get(field) == []:
            notes.append(
                f"{cond.get('type')}.{field} is empty but the model requires at least one value; kept as raw YAML"
            )
            return raw_node(cond)

    if cond.get("type") in INCOMPATIBLE_CONDITION_TYPES:
        notes.append(
            f"{cond.get('type')} is outside the normalized language; kept as raw YAML"
        )
        return raw_node(cond)
    if cond.get("type") not in CONDITION_TYPES:
        notes.append(
            f"unsupported condition type {cond.get('type')!r}; kept as raw YAML"
        )
        return raw_node(cond)

    return dict_to_node(cond, normalize=False, notes=notes)


def dict_to_node(
    raw: Any, normalize: bool = True, notes: list[str] | None = None
) -> dict:
    notes = notes if notes is not None else []
    if not isinstance(raw, dict):
        notes.append("non-dict condition kept as raw YAML")
        return raw_node(raw)
    if "all" in raw or "any" in raw:
        operator = "all" if "all" in raw else "any"
        return {
            "_kind": "group",
            "_key": _new_key("group"),
            "operator": operator,
            "children": [
                dict_to_node(child, normalize=normalize, notes=notes)
                for child in raw.get(operator, []) or []
            ],
        }
    if "not" in raw:
        return {
            "_kind": "not",
            "_key": _new_key("not"),
            "children": [dict_to_node(raw["not"], normalize=normalize, notes=notes)],
        }
    if normalize:
        return normalize_leaf(raw, notes)

    node = {"_kind": "leaf", "_key": _new_key("leaf")}
    node.update(deepcopy(raw))
    return node


def raw_node(raw: Any) -> dict:
    return {"_kind": "raw", "_key": _new_key("raw"), "raw": deepcopy(raw)}


def collect_incompatible_conditions(node: dict, path: str = "conditions") -> list[dict]:
    found: list[dict] = []
    if node.get("_kind") == "raw":
        raw = node.get("raw", {})
        found.append({"path": path, "condition": raw})
        return found
    for index, child in enumerate(node.get("children", []) or []):
        child_path = (
            f"{path}.{node.get('operator', node.get('_kind', 'node'))}[{index}]"
        )
        found.extend(collect_incompatible_conditions(child, child_path))
    return found


def imported_entry_to_state(entry: dict) -> dict:
    notes: list[str] = []
    normalized = {
        "id": entry.get("id", ""),
        "name": entry.get("name", ""),
        "page": int(entry.get("page") or 0),
        "priority": int(entry.get("priority") or 0),
        "meaning": entry.get("meaning", ""),
        "evidence": entry.get("evidence"),
        "conditions": entry.get("conditions", {"all": []}),
    }
    if "applicable_palaces" in entry:
        notes.append("dropped legacy applicable_palaces field")
    normalized["root"] = dict_to_node(
        normalized.pop("conditions"), normalize=True, notes=notes
    )
    normalized["import_notes"] = notes
    return normalized


def load_cach_cuc_file(path: Path) -> tuple[dict[str, dict], dict]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return load_cach_cuc_data(data)


def load_cach_cuc_data(data: dict) -> tuple[dict[str, dict], dict]:
    entries = {
        entry.get("id", f"entry_{i}"): imported_entry_to_state(entry)
        for i, entry in enumerate(data.get("cach_cuc", []) or [])
        if isinstance(entry, dict)
    }
    return entries, data


def entry_state_to_cach_cuc(entry: dict) -> dict:
    out = {
        "id": entry.get("id", ""),
        "name": entry.get("name", ""),
        "page": int(entry.get("page") or 0),
        "priority": int(entry.get("priority") or 0),
        "meaning": entry.get("meaning", ""),
        "conditions": node_to_dict(entry.get("root", new_group("all"))),
    }
    if entry.get("evidence"):
        out["evidence"] = entry["evidence"]
    return out


def validation_errors(cach_cuc: dict) -> list[str]:
    errors = unknown_star_errors(cach_cuc)
    try:
        CachCuc.model_validate(cach_cuc)
    except ValidationError as exc:
        errors.extend(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
    return errors


def unknown_star_errors(cach_cuc: dict) -> list[str]:
    known_stars = set(load_stars())
    errors: list[str] = []

    def visit(condition: Any, path: str) -> None:
        if not isinstance(condition, dict):
            return
        if "all" in condition:
            for index, child in enumerate(condition.get("all") or []):
                visit(child, f"{path}.all[{index}]")
            return
        if "any" in condition:
            for index, child in enumerate(condition.get("any") or []):
                visit(child, f"{path}.any[{index}]")
            return
        if "not" in condition:
            visit(condition.get("not"), f"{path}.not")
            return
        if condition.get("star") and condition["star"] not in known_stars:
            errors.append(f"{path}.star: unknown star id {condition['star']!r}")
        for index, star in enumerate(condition.get("stars") or []):
            if star not in known_stars:
                errors.append(f"{path}.stars[{index}]: unknown star id {star!r}")

    visit(cach_cuc.get("conditions"), "conditions")
    return errors


def new_leaf(ctype: str = "stars_meeting") -> dict:
    return {
        "_kind": "leaf",
        "_key": f"leaf_{uuid.uuid4().hex[:8]}",
        "type": ctype,
    }


def new_not_node() -> dict:
    return {
        "_kind": "not",
        "_key": f"not_{uuid.uuid4().hex[:8]}",
        "children": [],
    }


def new_tuan_triet_leaf() -> dict:
    leaf = new_leaf("star_with_palace")
    leaf["palace"] = PALACES[0]
    leaf["stars"] = ["tuan", "triet"]
    leaf["group_name"] = None
    leaf["mode"] = None
    leaf["at_least"] = None
    return leaf


def new_no_tuan_triet_not_node() -> dict:
    not_node = new_not_node()
    not_node["children"].append(new_tuan_triet_leaf())
    return not_node


def new_group(operator: str = "all") -> dict:
    return {
        "_kind": "group",
        "_key": f"group_{uuid.uuid4().hex[:8]}",
        "operator": operator,
        "children": [],
    }


def safe_index(options: list[str], value, default: int = 0) -> int:
    if value in options:
        return options.index(value)
    return default


def safe_default_list(options: list[str], values) -> list[str]:
    if not values:
        return []
    return [v for v in values if v in options]


def options_with_current_values(options: list[str], values) -> list[str]:
    current_values = values if isinstance(values, list) else [values] if values else []
    extras = [value for value in current_values if value not in options]
    return [*options, *extras]


def render_group_support(cond: dict, key: str) -> bool:
    use_group = st.checkbox(
        "use group",
        value=cond.get("group_name") is not None,
        key=f"{key}_use_group",
    )
    if not use_group:
        cond["group_name"] = None
        cond["mode"] = None
        cond["at_least"] = None
        return False

    cond["group_name"] = st.selectbox(
        "group_name",
        GROUPS,
        index=safe_index(GROUPS, cond.get("group_name")),
        key=f"{key}_group_name",
    )
    strategy = st.selectbox(
        "group strategy",
        ["mode", "at_least"],
        index=1 if cond.get("at_least") is not None else 0,
        key=f"{key}_group_strategy",
    )
    if strategy == "mode":
        cond["mode"] = st.selectbox(
            "mode",
            MODES,
            index=safe_index(MODES, cond.get("mode")),
            key=f"{key}_mode",
        )
        cond["at_least"] = None
    else:
        cond["at_least"] = int(
            st.number_input(
                "at_least",
                min_value=1,
                value=max(1, cond.get("at_least") or 1),
                step=1,
                key=f"{key}_at_least",
            )
        )
        cond["mode"] = None
    return True


def render_leaf(cond: dict, stars: list[str]) -> None:
    """Render fields for a leaf condition and update the dict in place."""
    key = cond["_key"]

    new_type = st.selectbox(
        "type",
        CONDITION_TYPES,
        index=safe_index(CONDITION_TYPES, cond.get("type")),
        key=f"{key}_type",
    )
    if new_type != cond.get("type"):
        cond.clear()
        cond["_kind"] = "leaf"
        cond["_key"] = key
        cond["type"] = new_type

    ctype = cond["type"]

    if ctype in ("can_exclude", "can_match"):
        cond["can"] = st.multiselect(
            "can",
            CAN,
            default=safe_default_list(CAN, cond.get("can")),
            key=f"{key}_can",
        )

    elif ctype == "gender_match":
        cond["gender"] = st.selectbox(
            "gender",
            GENDERS,
            index=safe_index(GENDERS, cond.get("gender")),
            key=f"{key}_gender",
        )

    elif ctype == "cung_than_at_palace":
        cond["palace"] = st.selectbox(
            "palace",
            PALACES,
            index=safe_index(PALACES, cond.get("palace")),
            key=f"{key}_palace",
        )

    elif ctype == "only_chinh_tinh":
        cond["palace"] = st.selectbox(
            "palace",
            PALACES,
            index=safe_index(PALACES, cond.get("palace")),
            key=f"{key}_palace",
        )
        star_options = options_with_current_values(stars, cond.get("star"))
        cond["star"] = st.selectbox(
            "star",
            star_options,
            index=safe_index(star_options, cond.get("star")),
            key=f"{key}_star",
        )

    elif ctype == "palace_at":
        cond["palace"] = st.selectbox(
            "palace",
            PALACES,
            index=safe_index(PALACES, cond.get("palace")),
            key=f"{key}_palace",
        )
        cond["chi"] = st.multiselect(
            "chi",
            CHI,
            default=safe_default_list(CHI, cond.get("chi")),
            key=f"{key}_chi",
        )

    elif ctype == "star_at_chi":
        render_group_support(cond, key)
        star_options = options_with_current_values(stars, cond.get("stars"))
        cond["stars"] = st.multiselect(
            "stars",
            star_options,
            default=safe_default_list(star_options, cond.get("stars")),
            key=f"{key}_stars",
        )
        cond["at_chi"] = st.multiselect(
            "at_chi",
            CHI,
            default=safe_default_list(CHI, cond.get("at_chi")),
            key=f"{key}_at_chi",
        )

    elif ctype == "star_brightness":
        star_options = options_with_current_values(stars, cond.get("stars"))
        cond["stars"] = st.multiselect(
            "stars",
            star_options,
            default=safe_default_list(star_options, cond.get("stars")),
            key=f"{key}_stars",
        )
        cond["brightness"] = st.multiselect(
            "brightness",
            BRIGHTNESS,
            default=safe_default_list(BRIGHTNESS, cond.get("brightness")),
            key=f"{key}_brightness",
        )

    elif ctype == "star_with_palace":
        cond["palace"] = st.selectbox(
            "palace",
            PALACES,
            index=safe_index(PALACES, cond.get("palace")),
            key=f"{key}_palace",
        )
        cond["scope"] = st.selectbox(
            "scope",
            SCOPES_MEETING,
            index=safe_index(SCOPES_MEETING, cond.get("scope", "dong_cung")),
            key=f"{key}_scope",
        )
        has_group = render_group_support(cond, key)
        if not has_group:
            cond["stars_matching_logic"] = st.selectbox(
                "stars matching logic",
                MODES,
                index=safe_index(MODES, cond.get("stars_matching_logic")),
                key=f"{key}_stars_matching_logic",
            )
        else:
            cond["stars_matching_logic"] = None
        star_options = options_with_current_values(stars, cond.get("stars"))
        cond["stars"] = st.multiselect(
            "stars",
            star_options,
            default=safe_default_list(star_options, cond.get("stars")),
            key=f"{key}_stars",
        )

    elif ctype == "stars_meeting":
        cond["scope"] = st.selectbox(
            "scope",
            SCOPES_MEETING,
            index=safe_index(SCOPES_MEETING, cond.get("scope")),
            key=f"{key}_scope",
        )
        has_group = render_group_support(cond, key)
        if not has_group:
            cond["stars_matching_logic"] = st.selectbox(
                "stars matching logic",
                MODES,
                index=safe_index(MODES, cond.get("stars_matching_logic")),
                key=f"{key}_stars_matching_logic",
            )
        else:
            cond["stars_matching_logic"] = None
        star_options = options_with_current_values(stars, cond.get("stars"))
        cond["stars"] = st.multiselect(
            "stars",
            star_options,
            default=safe_default_list(star_options, cond.get("stars")),
            key=f"{key}_stars",
        )

    elif ctype == "stars_xor":
        star_options = options_with_current_values(stars, cond.get("stars"))
        cond["stars"] = st.multiselect(
            "stars",
            star_options,
            default=safe_default_list(star_options, cond.get("stars")),
            key=f"{key}_stars",
        )
        cond["scope"] = st.selectbox(
            "scope",
            SCOPES_XOR,
            index=safe_index(SCOPES_XOR, cond.get("scope")),
            key=f"{key}_scope",
        )


def leaf_to_dict(cond: dict) -> dict:
    ctype = cond["type"]
    out: dict = {"type": ctype}

    fields_by_type = {
        "can_exclude": ["can"],
        "can_match": ["can"],
        "cung_than_at_palace": ["cung_than", "palace"],
        "gender_match": ["gender"],
        "only_chinh_tinh": ["palace", "star"],
        "palace_at": ["palace", "chi"],
        "star_at_chi": ["stars", "at_chi", "group_name", "mode", "at_least"],
        "star_brightness": ["stars", "brightness"],
        "star_with_palace": [
            "palace",
            "scope",
            "stars",
            "stars_matching_logic",
            "group_name",
            "mode",
            "at_least",
        ],
        "stars_meeting": [
            "scope",
            "stars",
            "stars_matching_logic",
            "group_name",
            "mode",
            "at_least",
        ],
        "stars_xor": ["stars", "scope"],
    }
    for field in fields_by_type.get(ctype, []):
        value = cond.get(field)
        if value is None:
            continue
        if (
            isinstance(value, list)
            and not value
            and (ctype, field) not in {("palace_at", "chi")}
        ):
            continue
        out[field] = value
    return out


def node_to_dict(node: dict) -> dict:
    if node["_kind"] == "leaf":
        return leaf_to_dict(node)
    if node["_kind"] == "raw":
        return deepcopy(node.get("raw", {}))
    if node["_kind"] == "not":
        children = node.get("children", [])
        if children:
            return {"not": node_to_dict(children[0])}
        return {}
    return {node["operator"]: [node_to_dict(child) for child in node["children"]]}


def rekey_node(node: dict) -> dict:
    copied = deepcopy(node)
    kind = copied.get("_kind", "node")
    copied["_key"] = _new_key(kind)
    if copied.get("_kind") == "raw":
        return copied
    copied["children"] = [rekey_node(child) for child in copied.get("children", [])]
    return copied


def render_node(
    node: dict, stars: list[str], parent_list: list, index: int, depth: int = 0
) -> None:
    key = node["_key"]
    with st.container(border=True):
        header = st.columns([5, 1, 1, 1])
        with header[0]:
            if node["_kind"] == "leaf":
                label = "Leaf"
            elif node["_kind"] == "raw":
                label = "Raw YAML"
            elif node["_kind"] == "not":
                label = "NOT"
            else:
                label = f"Group ({node['operator']})"
            st.markdown(f"**#{index + 1} — {label}**")
        with header[1]:
            if index > 0 and st.button("↑", key=f"{key}_up"):
                parent_list[index - 1], parent_list[index] = (
                    parent_list[index],
                    parent_list[index - 1],
                )
                st.rerun()
        with header[2]:
            if st.button("Copy", key=f"{key}_copy"):
                parent_list.insert(index + 1, rekey_node(node))
                st.rerun()
        with header[3]:
            if st.button("✕", key=f"{key}_remove"):
                parent_list.pop(index)
                st.rerun()

        if node["_kind"] == "leaf":
            render_leaf(node, stars)
        elif node["_kind"] == "raw":
            raw_text = st.text_area(
                "raw condition",
                value=yaml.safe_dump(
                    node.get("raw", {}), allow_unicode=True, sort_keys=False
                ).strip(),
                key=f"{key}_raw",
                height=180,
            )
            try:
                parsed = yaml.safe_load(raw_text) or {}
            except yaml.YAMLError as exc:
                st.error(f"Invalid YAML: {exc}")
            else:
                node["raw"] = parsed
                if isinstance(parsed, dict) and parsed.get("type") in CONDITION_TYPES:
                    if st.button("Convert raw to form", key=f"{key}_convert_raw"):
                        parent_list[index] = dict_to_node(parsed, normalize=False)
                        st.rerun()
        elif node["_kind"] == "not":
            children = node.setdefault("children", [])
            if children:
                render_node(children[0], stars, children, 0, depth + 1)
            else:
                ac = st.columns(2)
                with ac[0]:
                    if st.button("+ Leaf", key=f"{key}_add_leaf"):
                        children.append(new_leaf())
                        st.rerun()
                with ac[1]:
                    if st.button("+ Group", key=f"{key}_add_group"):
                        children.append(new_group("all"))
                        st.rerun()
        else:
            node["operator"] = st.radio(
                "operator",
                OPERATORS,
                horizontal=True,
                index=safe_index(OPERATORS, node.get("operator")),
                key=f"{key}_op",
            )
            for j, child in enumerate(list(node["children"])):
                render_node(child, stars, node["children"], j, depth + 1)

            ac = st.columns(4)
            with ac[0]:
                if st.button("+ Leaf", key=f"{key}_add_leaf"):
                    node["children"].append(new_leaf())
                    st.rerun()
            with ac[1]:
                if st.button("+ No Tuan/Triet", key=f"{key}_add_no_tuan_triet"):
                    node["children"].append(new_no_tuan_triet_not_node())
                    st.rerun()
            with ac[2]:
                nested_op = "any" if node["operator"] == "all" else "all"
                if st.button(f"+ Nested {nested_op}", key=f"{key}_add_group"):
                    node["children"].append(new_group(operator=nested_op))
                    st.rerun()
            with ac[3]:
                if st.button("+ NOT", key=f"{key}_add_not"):
                    node["children"].append(new_not_node())
                    st.rerun()


def init_state() -> None:
    if st.session_state.get("export_path") is None:
        st.session_state.pop("export_path", None)
    if "entries" not in st.session_state:
        st.session_state.entries = {}
    if "original_entries" not in st.session_state:
        st.session_state.original_entries = {}
    if "modified_ids" not in st.session_state:
        st.session_state.modified_ids = set()
    if "modified_order" not in st.session_state:
        st.session_state.modified_order = []
    if "skipped_remediated_ids" not in st.session_state:
        st.session_state.skipped_remediated_ids = set()
    if "saved_ids" not in st.session_state:
        st.session_state.saved_ids = set()
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None
    if "source_data" not in st.session_state:
        st.session_state.source_data = {}
    if "loaded_import_upload_token" not in st.session_state:
        st.session_state.loaded_import_upload_token = None
    if "entry_list_refresh" not in st.session_state:
        st.session_state.entry_list_refresh = 0
    if "export_cache_path" not in st.session_state:
        st.session_state.export_cache_path = None
    if "export_payload" not in st.session_state:
        st.session_state.export_payload = {"groups": DEFAULT_GROUPS, "cach_cuc": []}
    if "export_entries_by_id" not in st.session_state:
        st.session_state.export_entries_by_id = {}


def refresh_entry_lists() -> None:
    st.session_state.entry_list_refresh = (
        st.session_state.get("entry_list_refresh", 0) + 1
    )


def select_entry(cc_id: str) -> None:
    st.session_state.selected_id = cc_id


def sync_entry_widget_to_selection(ids: list[str], widget_key: str) -> None:
    st.session_state[widget_key] = (
        st.session_state.selected_id
        if st.session_state.selected_id in ids
        else ORIGINAL_ENTRY_PLACEHOLDER
    )


def entry_review_status(cc_id: str) -> str:
    is_modified = cc_id in st.session_state.modified_ids
    is_saved = cc_id in st.session_state.export_entries_by_id
    if is_modified and is_saved:
        return "modified in memory, already saved"
    if is_modified:
        return "modified in memory"
    if is_saved:
        return "saved in export file"
    return "original"


def review_entry_ids() -> list[str]:
    return list(dict.fromkeys(in_progress_entry_ids() + saved_entry_ids()))


def in_progress_entry_ids() -> list[str]:
    ordered_ids = [
        cc_id
        for cc_id in st.session_state.modified_order
        if cc_id in st.session_state.modified_ids
    ]
    missing_ids = [
        cc_id
        for cc_id in st.session_state.modified_ids
        if cc_id not in set(ordered_ids)
    ]
    return ordered_ids + missing_ids


def saved_entry_ids() -> list[str]:
    return list(st.session_state.export_entries_by_id)


def mark_entry_modified(cc_id: str) -> None:
    if not cc_id:
        return
    st.session_state.modified_ids.add(cc_id)
    st.session_state.modified_order = [
        cc_id,
        *[
            existing_id
            for existing_id in st.session_state.modified_order
            if existing_id != cc_id
        ],
    ]


def unmark_entry_modified(cc_id: str) -> None:
    st.session_state.modified_ids.discard(cc_id)
    st.session_state.modified_order = [
        existing_id
        for existing_id in st.session_state.modified_order
        if existing_id != cc_id
    ]


def mark_entry_saved_clean(previous_id: str | None, saved_entry: dict) -> str | None:
    saved_id = saved_entry.get("id")
    for cc_id in {previous_id, saved_id}:
        if cc_id:
            unmark_entry_modified(cc_id)
            st.session_state.skipped_remediated_ids.discard(cc_id)
    if saved_id and saved_id in st.session_state.export_entries_by_id:
        st.session_state.entries[saved_id] = imported_entry_to_state(
            st.session_state.export_entries_by_id[saved_id]
        )
        select_entry(saved_id)
    return saved_id


def baseline_cach_cuc_for_entry(cc_id: str) -> dict | None:
    if cc_id in st.session_state.export_entries_by_id:
        return entry_state_to_cach_cuc(
            imported_entry_to_state(st.session_state.export_entries_by_id[cc_id])
        )
    if cc_id in st.session_state.original_entries:
        return entry_state_to_cach_cuc(st.session_state.original_entries[cc_id])
    return None


def entry_matches_baseline(cc_id: str, current_cach_cuc: dict) -> bool:
    baseline = baseline_cach_cuc_for_entry(cc_id)
    return baseline is not None and current_cach_cuc == baseline


def is_review_only_remediation(cc_id: str, current_cach_cuc: dict) -> bool:
    return (
        cc_id in st.session_state.modified_ids
        and cc_id not in st.session_state.export_entries_by_id
        and st.session_state.entries.get(cc_id, {}).get("import_notes")
        and entry_matches_baseline(cc_id, current_cach_cuc)
    )


def skip_remediated_entry(cc_id: str) -> None:
    st.session_state.skipped_remediated_ids.add(cc_id)
    unmark_entry_modified(cc_id)


def sync_current_entry_modified_state(cc_id: str, current_cach_cuc: dict) -> None:
    was_modified = cc_id in st.session_state.modified_ids
    baseline = baseline_cach_cuc_for_entry(cc_id)
    if baseline is None or current_cach_cuc != baseline:
        mark_entry_modified(cc_id)
    elif (
        cc_id in st.session_state.modified_ids
        and cc_id not in st.session_state.export_entries_by_id
        and st.session_state.entries.get(cc_id, {}).get("import_notes")
        and cc_id not in st.session_state.skipped_remediated_ids
    ):
        mark_entry_modified(cc_id)
    else:
        unmark_entry_modified(cc_id)
    if was_modified != (cc_id in st.session_state.modified_ids):
        refresh_entry_lists()
        st.rerun()


def mark_remediated_entries_modified() -> None:
    for cc_id in reversed(list(st.session_state.entries)):
        if (
            st.session_state.entries[cc_id].get("import_notes")
            and cc_id not in st.session_state.skipped_remediated_ids
        ):
            mark_entry_modified(cc_id)


def sync_export_cache_to_memory() -> None:
    for cc_id, entry in st.session_state.export_entries_by_id.items():
        state_entry = imported_entry_to_state(entry)
        st.session_state.entries[cc_id] = state_entry
        st.session_state.saved_ids.add(cc_id)


def select_entry_from_widget(widget_key: str) -> None:
    cc_id = st.session_state.get(widget_key)
    if cc_id:
        select_entry(cc_id)


def reset_form() -> None:
    selected_id = st.session_state.get("selected_id")
    if not selected_id:
        return
    if selected_id in st.session_state.export_entries_by_id:
        st.session_state.entries[selected_id] = imported_entry_to_state(
            st.session_state.export_entries_by_id[selected_id]
        )
    elif selected_id in st.session_state.original_entries:
        st.session_state.entries[selected_id] = deepcopy(
            st.session_state.original_entries[selected_id]
        )
    else:
        return
    unmark_entry_modified(selected_id)
    refresh_entry_lists()


def add_blank_entry() -> None:
    base_id = "new_cach_cuc"
    cc_id = base_id
    index = 2
    while cc_id in st.session_state.entries:
        cc_id = f"{base_id}_{index}"
        index += 1
    entry = {
        "id": cc_id,
        "name": "",
        "page": 0,
        "priority": 0,
        "meaning": "",
        "evidence": None,
        "root": new_group(operator="all"),
        "import_notes": ["created manually"],
    }
    st.session_state.entries[cc_id] = entry
    mark_entry_modified(cc_id)
    st.session_state.saved_ids.discard(cc_id)
    select_entry(cc_id)
    refresh_entry_lists()


def duplicate_entry(source_key: str) -> str | None:
    source_entry = st.session_state.entries.get(source_key)
    if source_entry is None:
        return None

    source_id = source_entry.get("id") or source_key
    copied_id = f"{source_id}_copy"
    if (
        copied_id in st.session_state.entries
        or copied_id in st.session_state.export_entries_by_id
    ):
        return None

    copied_entry = deepcopy(source_entry)
    copied_entry["id"] = copied_id
    copied_entry["root"] = rekey_node(source_entry["root"])
    copied_entry["import_notes"] = [f"duplicated from {source_id}"]
    st.session_state.entries[copied_id] = copied_entry
    mark_entry_modified(copied_id)
    st.session_state.saved_ids.discard(copied_id)
    select_entry(copied_id)
    refresh_entry_lists()
    return copied_id


def load_import_into_state(path: Path, mark_remediated: bool = True) -> None:
    entries, source_data = load_cach_cuc_file(path)
    st.session_state.entries = entries
    st.session_state.original_entries = deepcopy(entries)
    st.session_state.modified_ids = set()
    st.session_state.modified_order = []
    st.session_state.skipped_remediated_ids = set()
    st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
    st.session_state.source_data = source_data
    sync_export_cache_to_memory()
    if mark_remediated:
        mark_remediated_entries_modified()
    select_entry(next(iter(entries), None))
    refresh_entry_lists()


def load_uploaded_import_into_state(
    uploaded_file, mark_remediated: bool = True
) -> None:
    data = yaml.safe_load(uploaded_file.getvalue().decode("utf-8")) or {}
    entries, source_data = load_cach_cuc_data(data)
    st.session_state.entries = entries
    st.session_state.original_entries = deepcopy(entries)
    st.session_state.modified_ids = set()
    st.session_state.modified_order = []
    st.session_state.skipped_remediated_ids = set()
    st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
    st.session_state.source_data = source_data
    sync_export_cache_to_memory()
    if mark_remediated:
        mark_remediated_entries_modified()
    select_entry(next(iter(entries), None))
    refresh_entry_lists()


def render_entry_selector() -> None:
    st.sidebar.header("Import")
    mark_remediated = st.sidebar.checkbox(
        "Add remediated entries to In-progress",
        value=True,
        help="When import changes legacy YAML into the normalized model, mark those entries for review.",
    )
    uploaded_file = st.sidebar.file_uploader("YAML file", type=("yaml", "yml"))
    if uploaded_file is not None:
        payload_bytes = uploaded_file.getvalue()
        upload_token = (
            uploaded_file.name,
            uploaded_file.size,
            hashlib.sha1(payload_bytes).hexdigest(),
            mark_remediated,
        )
        if st.session_state.loaded_import_upload_token != upload_token:
            try:
                load_uploaded_import_into_state(
                    uploaded_file, mark_remediated=mark_remediated
                )
            except Exception as exc:  # noqa: BLE001 - show Streamlit users the load failure.
                st.sidebar.error(f"Could not load file: {exc}")
            else:
                st.session_state.loaded_import_upload_token = upload_token
                st.sidebar.success(f"Loaded {len(st.session_state.entries)} entries")
                st.rerun()

    st.sidebar.header("Entries")
    if st.sidebar.button("+ New entry"):
        add_blank_entry()
        st.rerun()

    original_ids = list(st.session_state.original_entries.keys())
    if not original_ids:
        st.sidebar.info("Load a cach_cuc YAML file to begin.")
        return

    entry_number_by_id = {
        cc_id: index for index, cc_id in enumerate(original_ids, start=1)
    }
    entry_filter = st.sidebar.selectbox(
        "Show",
        ["All entries", "Modified entries", "Unmodified entries"],
        key="entry_selector_filter",
    )
    if entry_filter == "Modified entries":
        visible_ids = [
            cc_id for cc_id in original_ids if entry_review_status(cc_id) != "original"
        ]
    elif entry_filter == "Unmodified entries":
        visible_ids = [
            cc_id for cc_id in original_ids if entry_review_status(cc_id) == "original"
        ]
    else:
        visible_ids = original_ids
    selector_key_by_filter = {
        "All entries": f"{SELECTED_ENTRY_WIDGET_KEY}_all",
        "Modified entries": f"{SELECTED_ENTRY_WIDGET_KEY}_modified",
        "Unmodified entries": f"{SELECTED_ENTRY_WIDGET_KEY}_unmodified",
    }
    selected_entry_widget_key = selector_key_by_filter[entry_filter]

    def label_for(cc_id: str) -> str:
        if not cc_id:
            return "Choose an original entry..."
        entry = st.session_state.entries[cc_id]
        status = entry_review_status(cc_id)
        prefix = "" if status == "original" else "[M] "
        number = entry_number_by_id[cc_id]
        return f"{prefix}{number}. {entry.get('id') or cc_id} - {entry.get('name') or '(no name)'}"

    if st.session_state.selected_id not in st.session_state.entries:
        select_entry(original_ids[0])
    sync_entry_widget_to_selection(visible_ids, selected_entry_widget_key)

    if not visible_ids:
        st.sidebar.info(f"No {entry_filter.casefold()} to show.")
        return

    st.sidebar.selectbox(
        "Select cach_cuc",
        [ORIGINAL_ENTRY_PLACEHOLDER] + visible_ids,
        format_func=label_for,
        key=selected_entry_widget_key,
        on_change=select_entry_from_widget,
        args=(selected_entry_widget_key,),
    )

    query = st.sidebar.text_input("Filter", placeholder="id or name")
    if query:
        matches = [
            cc_id
            for cc_id in visible_ids
            if query.casefold() in cc_id.casefold()
            or query.casefold()
            in str(st.session_state.entries[cc_id].get("name", "")).casefold()
        ]
        st.sidebar.caption(f"{len(matches)} matches")
        for cc_id in matches[:20]:
            if st.sidebar.button(label_for(cc_id), key=f"jump_{cc_id}"):
                select_entry(cc_id)
                st.rerun()


def load_export_payload(path: Path) -> dict:
    if not path.exists():
        return {"groups": DEFAULT_GROUPS, "cach_cuc": []}
    with path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}
    return normalize_export_payload(payload)


def normalize_export_payload(payload: Any) -> dict:
    if not isinstance(payload, dict):
        return {"groups": DEFAULT_GROUPS, "cach_cuc": []}
    payload.setdefault("groups", DEFAULT_GROUPS)
    if not isinstance(payload.get("cach_cuc"), list):
        payload["cach_cuc"] = []
    return payload


def index_export_entries(payload: dict) -> dict[str, dict]:
    entries_by_id = {}
    for entry in payload.get("cach_cuc", []):
        if isinstance(entry, dict) and entry.get("id"):
            entries_by_id[entry["id"]] = entry
    return entries_by_id


def ensure_export_cache(path: Path) -> None:
    normalized_path = str(path.expanduser())
    if st.session_state.export_cache_path == normalized_path:
        return
    payload = load_export_payload(Path(normalized_path))
    st.session_state.export_cache_path = normalized_path
    st.session_state.export_payload = payload
    st.session_state.export_entries_by_id = index_export_entries(payload)
    st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
    sync_export_cache_to_memory()


def load_export_payload_into_cache(payload: dict, path: Path) -> None:
    st.session_state.export_cache_path = str(path.expanduser())
    st.session_state.export_payload = normalize_export_payload(payload)
    st.session_state.export_entries_by_id = index_export_entries(
        st.session_state.export_payload
    )
    st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
    sync_export_cache_to_memory()
    refresh_entry_lists()


def current_export_path() -> Path:
    export_file = st.session_state.get("export_path") or DEFAULT_EXPORT_FILENAME
    return Path(export_file).expanduser()


def write_export_cache(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            st.session_state.export_payload, f, allow_unicode=True, sort_keys=False
        )


def upsert_entries_to_export(path: Path, entries: list[dict]) -> None:
    ensure_export_cache(path)
    payload = st.session_state.export_payload
    existing_entries = [
        entry for entry in payload.get("cach_cuc", []) if isinstance(entry, dict)
    ]
    index_by_id = {
        entry.get("id"): index
        for index, entry in enumerate(existing_entries)
        if entry.get("id")
    }

    for entry in entries:
        entry_id = entry.get("id")
        if not entry_id:
            continue
        if entry_id in index_by_id:
            existing_entries[index_by_id[entry_id]] = entry
        else:
            index_by_id[entry_id] = len(existing_entries)
            existing_entries.append(entry)

    payload["cach_cuc"] = existing_entries
    st.session_state.export_payload = payload
    st.session_state.export_entries_by_id = index_export_entries(payload)
    st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
    write_export_cache(path)


def render_entry_id_dropdown(
    label: str,
    ids: list[str],
    names_by_id: dict[str, str],
    empty_message: str,
    key: str,
    status_by_id: dict[str, str] | None = None,
    on_change=None,
    args: tuple = (),
) -> None:
    if not ids:
        st.session_state[key] = ""
        st.caption(empty_message)
        return
    sync_entry_widget_to_selection(ids, key)
    st.selectbox(
        label,
        [ORIGINAL_ENTRY_PLACEHOLDER] + ids,
        format_func=lambda cc_id: (
            "Choose an entry..."
            if not cc_id
            else (
                f"[{status_by_id[cc_id]}] "
                if status_by_id and cc_id in status_by_id
                else ""
            )
            + f"{cc_id} - {names_by_id.get(cc_id) or '(no name)'}"
        ),
        key=key,
        on_change=on_change,
        args=args,
    )


def render_save_panel(current_cach_cuc: dict) -> None:
    st.caption("Export file")
    export_cols = st.columns([3, 1])
    with export_cols[0]:
        export_file = (
            st.text_input("Save path", value=DEFAULT_EXPORT_FILENAME, key="export_path")
            or DEFAULT_EXPORT_FILENAME
        )
    export_path = Path(export_file).expanduser()
    ensure_export_cache(export_path)
    with export_cols[1]:
        if st.button("Reload from path"):
            st.session_state.export_cache_path = None
            ensure_export_cache(export_path)
            refresh_entry_lists()
            st.rerun()

    in_progress_ids = in_progress_entry_ids()
    saved_ids = saved_entry_ids()
    review_ids = sorted(set(in_progress_ids) | set(saved_ids))
    review_names = {
        cc_id: st.session_state.entries.get(cc_id, {}).get("name")
        or st.session_state.export_entries_by_id.get(cc_id, {}).get("name")
        or "(no name)"
        for cc_id in review_ids
    }
    saved_status = {
        cc_id: "edited" for cc_id in saved_ids if cc_id in st.session_state.modified_ids
    }

    st.subheader(f"Modified entries ({len(review_ids)})")
    modified_cols = st.columns(2)
    with modified_cols[0]:
        render_entry_id_dropdown(
            "In-progress",
            in_progress_ids,
            review_names,
            "No entries are currently marked for saving.",
            "in_progress_entries_dropdown",
            on_change=select_entry_from_widget,
            args=("in_progress_entries_dropdown",),
        )
    with modified_cols[1]:
        render_entry_id_dropdown(
            "Saved",
            saved_ids,
            review_names,
            "The export file does not contain saved entries yet.",
            "saved_entries_dropdown",
            status_by_id=saved_status,
            on_change=select_entry_from_widget,
            args=("saved_entries_dropdown",),
        )

    allow_invalid = st.checkbox(
        "Allow saving entries that still have validation errors", value=False
    )

    selected_id = st.session_state.selected_id

    save_cols = st.columns([1, 2])
    with save_cols[0]:
        save_modified = st.button("Save modified entries")
    with save_cols[1]:
        save_selected = st.button("Save current entry only")

    if save_selected:
        errors = validation_errors(current_cach_cuc)
        if errors and not allow_invalid:
            st.error(
                "Selected entry has validation errors. Fix it or enable invalid saves."
            )
        else:
            upsert_entries_to_export(export_path, [current_cach_cuc])
            saved_id = mark_entry_saved_clean(selected_id, current_cach_cuc)
            st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
            refresh_entry_lists()
            st.success(f"Saved {saved_id or selected_id} to {export_path}")
            st.rerun()

    if save_modified:
        memory_modified_ids = in_progress_entry_ids()
        if not memory_modified_ids:
            st.info("No modified entries to save.")
            return
        entries = [
            entry_state_to_cach_cuc(st.session_state.entries[cc_id])
            for cc_id in memory_modified_ids
        ]
        errors_by_id = {entry["id"]: validation_errors(entry) for entry in entries}
        errors_by_id = {
            cc_id: errors for cc_id, errors in errors_by_id.items() if errors
        }
        if errors_by_id and not allow_invalid:
            st.error(
                "Some modified entries have validation errors. Fix them or enable invalid saves."
            )
            with st.expander("Validation errors", expanded=True):
                st.json(errors_by_id)
        else:
            upsert_entries_to_export(export_path, entries)
            for previous_id, entry in zip(memory_modified_ids, entries, strict=False):
                mark_entry_saved_clean(previous_id, entry)
            st.session_state.saved_ids = set(st.session_state.export_entries_by_id)
            refresh_entry_lists()
            st.success(f"Saved {len(entries)} modified entries to {export_path}")
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="Cach Cuc Editor", layout="wide")
    st.title("Cach Cuc Editor")

    init_state()
    ensure_export_cache(current_export_path())
    stars = load_stars()
    render_entry_selector()

    selected_id = st.session_state.get("selected_id")
    if not selected_id:
        st.info("Load a cach_cuc YAML file or create a new entry.")
        return
    entry = st.session_state.entries[selected_id]

    st.subheader("Basic info")
    c1, c2 = st.columns(2)
    with c1:
        cc_id = st.text_input(
            "id", value=entry.get("id", ""), key=f"{selected_id}_cc_id"
        )
        cc_name = st.text_input(
            "name", value=entry.get("name", ""), key=f"{selected_id}_cc_name"
        )
    with c2:
        cc_page = st.number_input(
            "page",
            min_value=0,
            step=1,
            value=int(entry.get("page") or 0),
            key=f"{selected_id}_cc_page",
        )
        cc_priority = st.number_input(
            "priority",
            min_value=0,
            step=1,
            value=int(entry.get("priority") or 0),
            key=f"{selected_id}_cc_priority",
        )
    cc_meaning = st.text_area(
        "meaning", value=entry.get("meaning", ""), key=f"{selected_id}_cc_meaning"
    )
    cc_evidence = st.text_area(
        "evidence", value=entry.get("evidence") or "", key=f"{selected_id}_cc_evidence"
    )

    entry["id"] = cc_id
    entry["name"] = cc_name
    entry["page"] = int(cc_page)
    entry["priority"] = int(cc_priority)
    entry["meaning"] = cc_meaning
    entry["evidence"] = cc_evidence or None

    if entry.get("import_notes"):
        with st.expander("Import remediation notes"):
            for note in entry["import_notes"]:
                st.caption(note)

    incompatible_conditions = collect_incompatible_conditions(entry["root"])
    if incompatible_conditions:
        st.warning(
            f"{len(incompatible_conditions)} incompatible condition(s) need manual migration."
        )
        with st.expander("Incompatible condition YAML", expanded=True):
            st.text_area(
                "Current incompatible syntax",
                value=yaml.safe_dump(
                    incompatible_conditions, allow_unicode=True, sort_keys=False
                ),
                height=220,
                disabled=True,
                key=f"{selected_id}_incompatible_conditions",
            )

    st.markdown("---")
    st.subheader("Conditions")
    root = entry["root"]
    root["operator"] = st.radio(
        "Root operator",
        OPERATORS,
        horizontal=True,
        index=safe_index(OPERATORS, root.get("operator")),
        key=f"{selected_id}_root_op",
    )

    for i, child in enumerate(list(root["children"])):
        render_node(child, stars, root["children"], i, depth=0)

    add_cols = st.columns(4)
    with add_cols[0]:
        if st.button("+ Add condition"):
            root["children"].append(new_leaf())
            st.rerun()
    with add_cols[1]:
        if st.button("+ Add no Tuan/Triet"):
            root["children"].append(new_no_tuan_triet_not_node())
            st.rerun()
    with add_cols[2]:
        if st.button("+ Add nested group"):
            root["children"].append(new_group())
            st.rerun()
    with add_cols[3]:
        if st.button("+ Add NOT"):
            root["children"].append(new_not_node())
            st.rerun()

    st.markdown("---")
    st.subheader("Preview & Save")

    cach_cuc = entry_state_to_cach_cuc(entry)
    sync_current_entry_modified_state(selected_id, cach_cuc)
    errors = validation_errors(cach_cuc)

    with st.expander("YAML preview", expanded=True):
        st.code(
            yaml.safe_dump(cach_cuc, allow_unicode=True, sort_keys=False),
            language="yaml",
        )

    if errors:
        with st.expander("Validation errors", expanded=True):
            for error in errors:
                st.error(error)
    else:
        st.success("Entry validates against the normalized condition model.")

    can_discard_to_original = (
        selected_id in st.session_state.original_entries
        and entry_review_status(selected_id) != "original"
    )
    can_skip_remediated = is_review_only_remediation(selected_id, cach_cuc)
    action_cols = st.columns([1, 1, 1, 3])
    with action_cols[0]:
        if st.button(
            "Discard edits for current entry", disabled=not can_discard_to_original
        ):
            reset_form()
            st.rerun()
    with action_cols[1]:
        if st.button("Skip remediated entry", disabled=not can_skip_remediated):
            skip_remediated_entry(selected_id)
            refresh_entry_lists()
            st.rerun()
    with action_cols[2]:
        if st.button("Duplicate current entry"):
            copied_id = duplicate_entry(selected_id)
            if copied_id is None:
                source_id = entry.get("id") or selected_id
                st.error(f"Cannot duplicate: {source_id}_copy already exists.")
            else:
                st.rerun()

    render_save_panel(cach_cuc)


if __name__ == "__main__":
    main()
