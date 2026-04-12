from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, TypeAdapter, field_validator

from src.refactored.component import Component
from src.refactored.component.cung import Cung, Role
from src.refactored.component.elementary import NguHanh
from src.refactored.component.sao import Sao, SaoType


class CungRecord(BaseModel):
    role: Role

    def to_component(self) -> Cung:
        return Cung(role=self.role)


class SaoRecord(BaseModel):
    name: str
    ngu_hanh: NguHanh
    is_chinh_tinh: bool = False
    sao_type: list[SaoType] = Field(default_factory=list)

    @field_validator("ngu_hanh", mode="before")
    @classmethod
    def _parse_ngu_hanh(cls, value: str | NguHanh) -> NguHanh:
        if isinstance(value, NguHanh):
            return value
        return NguHanh(value)

    @field_validator("sao_type", mode="before")
    @classmethod
    def _parse_sao_type(cls, value: list[str] | list[SaoType]) -> list[SaoType]:
        return [item if isinstance(item, SaoType) else SaoType[item] for item in value]

    def to_component(self) -> Sao:
        return Sao(
            name=self.name,
            ngu_hanh=self.ngu_hanh,
            is_chinh_tinh=self.is_chinh_tinh,
            sao_type=self.sao_type,
        )


class ComponentCatalog:
    _cung_records_adapter = TypeAdapter(list[CungRecord])
    _sao_records_adapter = TypeAdapter(list[SaoRecord])

    def __init__(self, catalog_dir: Path | None = None) -> None:
        self._catalog_dir = catalog_dir or Path(__file__).resolve().parent
        self._components = self._load_components()

    def get(self, name: str) -> Component:
        try:
            return self._components[name]
        except KeyError as exc:
            raise KeyError(f"Component `{name}` is not defined in the catalog.") from exc

    def get_many(self, names: list[str]) -> list[Component]:
        return [self.get(name) for name in names]

    def _load_components(self) -> dict[str, Component]:
        components: dict[str, Component] = {}

        for component in self._load_cungs():
            self._register(components, component)
        for component in self._load_saos():
            self._register(components, component)

        return components

    def _load_cungs(self) -> list[Cung]:
        raw_json = (self._catalog_dir / "cung.json").read_text(encoding="utf-8")
        records = self._cung_records_adapter.validate_json(raw_json)
        return [record.to_component() for record in records]

    def _load_saos(self) -> list[Sao]:
        raw_json = (self._catalog_dir / "sao.json").read_text(encoding="utf-8")
        records = self._sao_records_adapter.validate_json(raw_json)
        return [record.to_component() for record in records]

    def _register(self, components: dict[str, Component], component: Component) -> None:
        if component.name in components:
            raise ValueError(f"Duplicate component name in catalog: {component.name}")
        components[component.name] = component


@lru_cache(maxsize=1)
def get_default_catalog() -> ComponentCatalog:
    return ComponentCatalog()
