from __future__ import annotations

from functools import cache
from pathlib import Path

from pydantic import TypeAdapter

from src.refactored.component import Component
from src.refactored.component.cung import Cung
from src.refactored.component.sao import Sao
from src.refactored.component.tuan_triet import TuanTriet


class ComponentCatalog:
    _cung_adapter = TypeAdapter(list[Cung])
    _sao_adapter = TypeAdapter(list[Sao])
    _tuan_triet_adapter = TypeAdapter(list[TuanTriet])

    def __init__(self, catalog_dir: Path | None = None) -> None:
        self._catalog_dir = (
            catalog_dir or Path(__file__).resolve().parent.parent / "catalog"
        )
        self._components = self._load_components()

    def get(self, component_id: str) -> Component:
        try:
            return self._components[component_id]
        except KeyError as exc:
            raise KeyError(
                f"Component id `{component_id}` is not defined in the catalog."
            ) from exc

    def get_many(self, component_ids: list[str]) -> list[Component]:
        return [self.get(component_id) for component_id in component_ids]

    def _load_components(self) -> dict[str, Component]:
        components: dict[str, Component] = {}

        for component in self._load_cungs():
            self._register(components, component)
        for component in self._load_saos():
            self._register(components, component)
        for component in self._load_tuan_triet():
            self._register(components, component)

        return components

    def _load_cungs(self) -> list[Cung]:
        raw_json = (self._catalog_dir / "cung.json").read_text(encoding="utf-8")
        return self._cung_adapter.validate_json(raw_json)

    def _load_saos(self) -> list[Sao]:
        raw_json = (self._catalog_dir / "sao.json").read_text(encoding="utf-8")
        return self._sao_adapter.validate_json(raw_json)

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
