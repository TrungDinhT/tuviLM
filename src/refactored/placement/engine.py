from __future__ import annotations

from src.refactored.component.elementary import DiaChi
from src.refactored.placement.compiler import (
    SpecializedAbsoluteSpec,
    SpecializedPlacementRules,
    SpecializedRelativeSpec,
)
from src.refactored.placement.registry import ComponentId


class PlacementEngine:
    def __init__(self, rules: SpecializedPlacementRules) -> None:
        self._rules = rules
        self._positions: dict[ComponentId, DiaChi] = {}
        self._resolving: list[ComponentId] = []

    def clear_cache(self) -> None:
        self._positions.clear()
        self._resolving.clear()

    def resolve_all(self) -> dict[ComponentId, DiaChi]:
        for component_id in self._rules.specs:
            self._resolve_dependency_chain(component_id)

        return dict(self._positions)

    def resolve_one(self, component_id: ComponentId) -> DiaChi:
        return self._resolve_dependency_chain(component_id)

    def _resolve_dependency_chain(self, component_id: ComponentId) -> DiaChi:
        if component_id in self._positions:
            return self._positions[component_id]
        if component_id in self._resolving:
            cycle = " -> ".join([*self._resolving, component_id])
            raise ValueError(f"Circular position dependency detected: {cycle}")

        self._resolving.append(component_id)
        try:
            spec = self._rules.specs[component_id]
            if isinstance(spec, SpecializedRelativeSpec):
                reference_id = spec.reference_id
                reference_position = self._resolve_dependency_chain(
                    reference_id
                )
                position = spec.transform(reference_position)
            elif isinstance(spec, SpecializedAbsoluteSpec):
                position = spec.position_fn()
            else:
                raise ValueError(f"Invalid position spec: {spec}")
        finally:
            self._resolving.pop()

        self._positions[component_id] = position
        return position
