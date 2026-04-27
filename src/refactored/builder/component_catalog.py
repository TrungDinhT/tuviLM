from __future__ import annotations

from functools import cache
from pathlib import Path

from pydantic import TypeAdapter

from src.refactored.component import Component
from src.refactored.component.cung import CungRole
from src.refactored.component.elementary import DiaChi, DiaChiEntity, ThienCan, ThienCanEntity
from src.refactored.component.sao import Sao, TuanTriet, TuHoa, VongTrangSinh


class ComponentCatalog:
    _cung_adapter = TypeAdapter(list[CungRole])
    _dia_chi_adapter = TypeAdapter(list[DiaChiEntity])
    _sao_adapter = TypeAdapter(list[Sao | VongTrangSinh])
    _thien_can_adapter = TypeAdapter(list[ThienCanEntity])
    _tuhoa_adapter = TypeAdapter(list[TuHoa])
    _tuan_triet_adapter = TypeAdapter(list[TuanTriet])

    def __init__(self, catalog_dir: Path | None = None) -> None:
        self._catalog_dir = (
            catalog_dir or Path(__file__).resolve().parent.parent / "catalog"
        )
        self._components = self._load_components()
        self._dia_chi_entities = {
            entity.value: entity for entity in self._load_dia_chi_entities()
        }
        self._thien_can_entities = {
            entity.value: entity for entity in self._load_thien_can_entities()
        }

    def get(self, component_id: str) -> Component:
        try:
            return self._components[component_id]
        except KeyError as exc:
            raise KeyError(
                f"Component id `{component_id}` is not defined in the catalog."
            ) from exc

    def get_many(self, component_ids: list[str]) -> list[Component]:
        return [self.get(component_id) for component_id in component_ids]

    def get_dia_chi(self, dia_chi: DiaChi) -> DiaChiEntity:
        try:
            return self._dia_chi_entities[dia_chi]
        except KeyError as exc:
            raise KeyError(
                f"Dia chi `{dia_chi}` is not defined in the catalog."
            ) from exc

    def get_thien_can(self, thien_can: ThienCan) -> ThienCanEntity:
        try:
            return self._thien_can_entities[thien_can]
        except KeyError as exc:
            raise KeyError(
                f"Thien can `{thien_can}` is not defined in the catalog."
            ) from exc

    def _load_components(self) -> dict[str, Component]:
        components: dict[str, Component] = {}

        for component in self._load_cungs():
            self._register(components, component)
        for component in self._load_saos():
            self._register(components, component)
        for component in self._load_tuhoas():
            self._register(components, component)
        for component in self._load_tuan_triet():
            self._register(components, component)

        return components

    def _load_cungs(self) -> list[CungRole]:
        raw_json = (self._catalog_dir / "cung_role.json").read_text(encoding="utf-8")
        return self._cung_adapter.validate_json(raw_json)

    def _load_dia_chi_entities(self) -> list[DiaChiEntity]:
        raw_json = (self._catalog_dir / "dia_chi.json").read_text(encoding="utf-8")
        return self._dia_chi_adapter.validate_json(raw_json)

    def _load_saos(self) -> list[Sao | VongTrangSinh]:
        raw_json = (self._catalog_dir / "sao.json").read_text(encoding="utf-8")
        return self._sao_adapter.validate_json(raw_json)

    def _load_tuhoas(self) -> list[TuHoa]:
        raw_json = (self._catalog_dir / "tuhoa.json").read_text(encoding="utf-8")
        return self._tuhoa_adapter.validate_json(raw_json)

    def _load_thien_can_entities(self) -> list[ThienCanEntity]:
        raw_json = (self._catalog_dir / "thien_can.json").read_text(encoding="utf-8")
        return self._thien_can_adapter.validate_json(raw_json)

    def _load_tuan_triet(self) -> list[TuanTriet]:
        raw_json = (self._catalog_dir / "tuan_triet.json").read_text(encoding="utf-8")
        return self._tuan_triet_adapter.validate_json(raw_json)

    def _register(self, components: dict[str, Component], component: Component) -> None:
        if component.id in components:
            raise ValueError(f"Duplicate component id in catalog: {component.id}")
        components[component.id] = component


@cache
def get_default_catalog() -> ComponentCatalog:
    return ComponentCatalog()
