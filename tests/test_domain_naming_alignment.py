"""Phase 0 / workstream 09 — domain naming alignment (typing + Cung field)."""

from __future__ import annotations

import types
import typing
from typing import TypeAliasType, get_args, get_origin

from src.refactored.components.definitions.elementary import (
    DiaChiEntity,
    ThienCanEntity,
)
from src.refactored.components.repository import get_default_repository
from src.refactored.components.definitions import Component, Sao
from src.refactored.components.definitions import __all__ as component_all
from src.refactored.components.definitions.cuc import Cuc
from src.refactored.components.definitions.cung_role import CungRole
from src.refactored.components.definitions.sao import ChinhPhuTinh, TuanTriet, TuHoa, VongTrangSinh
from src.refactored.model.cung import Cung
from src.refactored.placement import registry as placement_registry


def _flatten_types(tp: object) -> set[type]:
    """Expand unions (including PEP 695 aliases) into concrete types."""
    if tp is typing.Any:
        return set()
    if isinstance(tp, TypeAliasType):
        return _flatten_types(tp.__value__)
    if isinstance(tp, types.UnionType):
        out: set[type] = set()
        for arg in tp.__args__:
            out |= _flatten_types(arg)
        return out
    origin = get_origin(tp)
    args = get_args(tp)
    if origin is typing.Union:
        out = set()
        for arg in args:
            out |= _flatten_types(arg)
        return out
    if args and origin is not None:
        return _flatten_types(origin) if origin else set()
    if isinstance(tp, type):
        return {tp}
    return set()


def test_sao_type_alias_is_union_of_catalog_star_types() -> None:
    members = _flatten_types(Sao)
    assert members == {ChinhPhuTinh, TuHoa, VongTrangSinh, TuanTriet}


def test_component_type_alias_includes_structural_types_and_sao_members() -> None:
    members = _flatten_types(Component)
    assert {DiaChiEntity, ThienCanEntity, Cuc, CungRole}.issubset(members)
    assert _flatten_types(Sao).issubset(members)


def test_component_public_exports_include_aliases_and_chinh_phu_tinh() -> None:
    assert "Component" in component_all
    assert "Sao" in component_all
    assert "ChinhPhuTinh" in component_all


def test_chinh_phu_tinh_is_concrete_star_model_class() -> None:
    assert issubclass(ChinhPhuTinh, object)
    assert ChinhPhuTinh.__name__ == "ChinhPhuTinh"


def test_cung_uses_layered_components_tuple() -> None:
    fields = Cung.__dataclass_fields__  # type: ignore[attr-defined]
    assert "components" in fields


def test_component_id_unchanged_in_placement_registry() -> None:
    assert placement_registry.ComponentId is str


def test_catalog_get_covers_component_union_examples() -> None:
    catalog = get_default_repository()
    assert isinstance(catalog.get("menh"), CungRole)
    assert isinstance(catalog.get("tu_vi"), ChinhPhuTinh)
    assert isinstance(catalog.get("ty"), DiaChiEntity)
    assert isinstance(catalog.get("giap"), ThienCanEntity)
    assert isinstance(catalog.get("hoa_luc_cuc"), Cuc)
