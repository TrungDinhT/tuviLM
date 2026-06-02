"""Streamlit editor for cach_cuc entries.

Run with:
    streamlit run support_tool/cach_cuc/cach_cuc_editor.py
"""
from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parents[2]
STARS_PATH = ROOT / "src/refactored/components/data/sao.json"
OUTPUT_DIR = ROOT / "data/cach_cuc"

PALACES = ["menh", "phu_mau", "phuc_duc", "dien_trach", "quan_loc", "no_boc", "thien_di", "tat_ach", "tai_bach", "tu_tuc", "phu_the", "huynh_de", "cung_than",]
CHI = ["Ti", "Suu", "Dan", "Mao", "Thin", "Ty", "Ngo", "Mui", "Than", "Dau", "Tuat", "Hoi"]
CAN = ["giap", "at", "binh", "dinh", "mau", "ky", "canh", "tan", "nham", "quy"]
SCOPES_MEETING = ["hoi_hop", "dong_hoac_xung", "dong_cung", "nhi_hop", "xung_chieu", "giap"]
SCOPES_XOR = ["hoi_hop", "dong_hoac_xung", "dong_cung", "nhi_hop", "xung_chieu"]
GROUPS = ["luc_sat", "sat_tinh", "luc_cat", "cat_tinh", "tu_hoa", "tam_hoa"]
BRIGHTNESS = ["mieu", "vuong", "dac", "binh_hoa", "binh", "bat_dac_dia", "ham"]
GENDERS = ["male", "female"]
MODES = ["any", "all"]
OPERATORS = ["all", "any"]

CONDITION_TYPES = [
    "can_exclude",
    "can_match",
    "gender_match",
    "no_stars",
    "only_chinh_tinh",
    "palace_at",
    "star_at_chi",
    "star_brightness",
    "star_in_palace",
    "stars_meeting",
]


def sanitize_id(value: str) -> str:
    """Reduce an id to a safe filename slug (alnum/underscore/dash)."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip()).strip("_")


@st.cache_data
def load_stars() -> list[str]:
    with STARS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    all_id = [s["id"] for s in data]
    all_id.extend(["hoa_quyen", "hoa_loc", "hoa_khoa", "hoa_ky", "tuan", "triet"])
    return all_id

def new_leaf(ctype: str = "stars_meeting") -> dict:
    return {
        "_kind": "leaf",
        "_key": f"leaf_{uuid.uuid4().hex[:8]}",
        "type": ctype,
    }


def new_no_tuan_triet_leaf() -> dict:
    leaf = new_leaf("no_stars")
    leaf["in_palace"] = PALACES[0]
    leaf["stars"] = ["tuan", "triet"]
    leaf["group"] = None
    return leaf


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

    elif ctype == "no_stars":
        cond["in_palace"] = st.selectbox(
            "in_palace",
            PALACES,
            index=safe_index(PALACES, cond.get("in_palace")),
            key=f"{key}_in_palace",
        )
        use_group = st.checkbox(
            "use group",
            value=cond.get("group") is not None,
            key=f"{key}_use_group",
        )
        if use_group:
            cond["group"] = st.selectbox(
                "group",
                GROUPS,
                index=safe_index(GROUPS, cond.get("group")),
                key=f"{key}_group",
            )
            cond["stars"] = None
        else:
            cond["stars"] = st.multiselect(
                "stars",
                stars,
                default=safe_default_list(stars, cond.get("stars")),
                key=f"{key}_stars",
            )
            cond["group"] = None

    elif ctype == "only_chinh_tinh":
        cond["palace"] = st.selectbox(
            "palace",
            PALACES,
            index=safe_index(PALACES, cond.get("palace")),
            key=f"{key}_palace",
        )
        cond["star"] = st.selectbox(
            "star",
            stars,
            index=safe_index(stars, cond.get("star")),
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
        use_group = st.checkbox(
            "use group",
            value=cond.get("group") is not None,
            key=f"{key}_use_group",
        )
        if use_group:
            cond["group"] = st.selectbox(
                "group",
                GROUPS,
                index=safe_index(GROUPS, cond.get("group")),
                key=f"{key}_group",
            )
            cond["mode"] = st.selectbox(
                "mode",
                MODES,
                index=safe_index(MODES, cond.get("mode")),
                key=f"{key}_mode",
            )
            cond["stars"] = None
        else:
            cond["stars"] = st.multiselect(
                "stars",
                stars,
                default=safe_default_list(stars, cond.get("stars")),
                key=f"{key}_stars",
            )
            cond["group"] = None
            cond["mode"] = None
        cond["at_chi"] = st.multiselect(
            "at_chi",
            CHI,
            default=safe_default_list(CHI, cond.get("at_chi")),
            key=f"{key}_at_chi",
        )

    elif ctype == "star_brightness":
        cond["stars"] = st.multiselect(
            "stars",
            stars,
            default=safe_default_list(stars, cond.get("stars")),
            key=f"{key}_stars",
        )
        cond["brightness"] = st.multiselect(
            "brightness",
            BRIGHTNESS,
            default=safe_default_list(BRIGHTNESS, cond.get("brightness")),
            key=f"{key}_brightness",
        )

    elif ctype == "star_in_palace":
        cond["palace"] = st.selectbox(
            "palace",
            PALACES,
            index=safe_index(PALACES, cond.get("palace")),
            key=f"{key}_palace",
        )
        use_group = st.checkbox(
            "use group",
            value=cond.get("group") is not None,
            key=f"{key}_use_group",
        )
        if use_group:
            cond["group"] = st.selectbox(
                "group",
                GROUPS,
                index=safe_index(GROUPS, cond.get("group")),
                key=f"{key}_group",
            )
            cond["mode"] = st.selectbox(
                "mode",
                MODES,
                index=safe_index(MODES, cond.get("mode")),
                key=f"{key}_mode",
            )
            cond["stars"] = None
        else:
            cond["stars"] = st.multiselect(
                "stars",
                stars,
                default=safe_default_list(stars, cond.get("stars")),
                key=f"{key}_stars",
            )
            cond["group"] = None
            cond["mode"] = None

    elif ctype == "stars_meeting":
        cond["scope"] = st.selectbox(
            "scope",
            SCOPES_MEETING,
            index=safe_index(SCOPES_MEETING, cond.get("scope")),
            key=f"{key}_scope",
        )
        use_group = st.checkbox(
            "use group",
            value=cond.get("group") is not None,
            key=f"{key}_use_group",
        )
        if use_group:
            cond["group"] = st.selectbox(
                "group",
                GROUPS,
                index=safe_index(GROUPS, cond.get("group")),
                key=f"{key}_group",
            )
            cond["mode"] = st.selectbox(
                "mode",
                MODES,
                index=safe_index(MODES, cond.get("mode")),
                key=f"{key}_mode",
            )
            cond["stars"] = None
        else:
            cond["stars"] = st.multiselect(
                "stars",
                stars,
                default=safe_default_list(stars, cond.get("stars")),
                key=f"{key}_stars",
            )
            cond["group"] = None
            cond["mode"] = None

    elif ctype == "stars_xor":
        cond["stars"] = st.multiselect(
            "stars",
            stars,
            default=safe_default_list(stars, cond.get("stars")),
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
        "gender_match": ["gender"],
        "no_stars": ["in_palace", "group", "stars"],
        "only_chinh_tinh": ["palace", "star"],
        "palace_at": ["palace", "chi"],
        "star_at_chi": ["stars", "at_chi", "group", "mode"],
        "star_brightness": ["stars", "brightness"],
        "star_in_palace": ["palace", "stars", "group", "mode"],
        "stars_meeting": ["scope", "stars", "group", "mode"],
        "stars_xor": ["stars", "scope"],
    }
    for field in fields_by_type.get(ctype, []):
        value = cond.get(field)
        if value is None:
            continue
        if isinstance(value, list) and not value:
            continue
        out[field] = value
    return out


def node_to_dict(node: dict) -> dict:
    if node["_kind"] == "leaf":
        return leaf_to_dict(node)
    return {node["operator"]: [node_to_dict(child) for child in node["children"]]}


def render_node(node: dict, stars: list[str], parent_list: list, index: int, depth: int = 0) -> None:
    key = node["_key"]
    with st.container(border=True):
        header = st.columns([5, 1, 1])
        with header[0]:
            label = "Leaf" if node["_kind"] == "leaf" else f"Group ({node['operator']})"
            st.markdown(f"**#{index + 1} — {label}**")
        with header[1]:
            if index > 0 and st.button("↑", key=f"{key}_up"):
                parent_list[index - 1], parent_list[index] = parent_list[index], parent_list[index - 1]
                st.rerun()
        with header[2]:
            if st.button("✕", key=f"{key}_remove"):
                parent_list.pop(index)
                st.rerun()

        if node["_kind"] == "leaf":
            render_leaf(node, stars)
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

            ac = st.columns(3)
            with ac[0]:
                if st.button("+ Leaf", key=f"{key}_add_leaf"):
                    node["children"].append(new_leaf())
                    st.rerun()
            with ac[1]:
                if st.button("+ No Tuan/Triet", key=f"{key}_add_no_tuan_triet"):
                    node["children"].append(new_no_tuan_triet_leaf())
                    st.rerun()
            with ac[2]:
                nested_op = "any" if node["operator"] == "all" else "all"
                if st.button(f"+ Nested {nested_op}", key=f"{key}_add_group"):
                    node["children"].append(new_group(operator=nested_op))
                    st.rerun()


def init_state() -> None:
    if "root" not in st.session_state:
        st.session_state.root = new_group(operator="all")


def reset_form() -> None:
    st.session_state.root = new_group(operator="all")
    for field in ("cc_id", "cc_name", "cc_meaning"):
        if field in st.session_state:
            del st.session_state[field]


def main() -> None:
    st.set_page_config(page_title="Cach Cuc Editor", layout="wide")
    st.title("Cach Cuc Editor")

    init_state()
    stars = load_stars()

    st.subheader("Basic info")
    c1, c2 = st.columns(2)
    with c1:
        cc_id = st.text_input("id", key="cc_id")
        cc_name = st.text_input("name", key="cc_name")
    with c2:
        cc_page = st.number_input("page", min_value=0, step=1, key="cc_page")
        cc_priority = st.number_input("priority", min_value=0, step=1, key="cc_priority")
    cc_meaning = st.text_area("meaning", key="cc_meaning")

    st.markdown("---")
    st.subheader("Conditions")
    root = st.session_state.root
    root["operator"] = st.radio(
        "Root operator",
        OPERATORS,
        horizontal=True,
        index=safe_index(OPERATORS, root.get("operator")),
        key="root_op",
    )

    for i, child in enumerate(list(root["children"])):
        render_node(child, stars, root["children"], i, depth=0)

    add_cols = st.columns(3)
    with add_cols[0]:
        if st.button("+ Add condition"):
            root["children"].append(new_leaf())
            st.rerun()
    with add_cols[1]:
        if st.button("+ Add no Tuan/Triet"):
            root["children"].append(new_no_tuan_triet_leaf())
            st.rerun()
    with add_cols[2]:
        if st.button("+ Add nested group"):
            root["children"].append(new_group())
            st.rerun()

    st.markdown("---")
    st.subheader("Preview & Save")

    cach_cuc = {
        "id": cc_id,
        "name": cc_name,
        "page": int(cc_page),
        "priority": int(cc_priority),
        "meaning": cc_meaning,
        "conditions": node_to_dict(root),
    }

    with st.expander("YAML preview", expanded=True):
        st.code(
            yaml.safe_dump(cach_cuc, allow_unicode=True, sort_keys=False),
            language="yaml",
        )

    file_slug = sanitize_id(cc_id) if cc_id else ""
    out_path = OUTPUT_DIR / f"{file_slug}.yaml" if file_slug else None
    st.caption(f"Output file: `{out_path}`" if out_path else "Output file: _(enter an id)_")

    save_cols = st.columns([1, 1, 4])
    with save_cols[0]:
        save = st.button("Save", type="primary")
    with save_cols[1]:
        if st.button("Reset form"):
            reset_form()
            st.rerun()

    if save:
        if not cc_id.strip():
            st.error("id is required")
        elif not file_slug:
            st.error("id must contain at least one alphanumeric character")
        elif not cc_name.strip():
            st.error("name is required")
        elif not root["children"]:
            st.error("at least one condition is required")
        else:
            assert out_path is not None
            out_path.parent.mkdir(parents=True, exist_ok=True)
            existed = out_path.exists()
            with out_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    {"cach_cuc": [cach_cuc]},
                    f,
                    allow_unicode=True,
                    sort_keys=False,
                )
            action = "Overwrote" if existed else "Saved"
            st.success(f"{action} '{cc_id}' → {out_path}")


if __name__ == "__main__":
    main()
