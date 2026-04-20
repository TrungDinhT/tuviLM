from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import LaSoContext
from src.refactored.placement.primitives import Rule
from src.refactored.placement.registry import (
    AbsolutePositionSpec,
    ComponentId,
    PlacementRegistry,
    PositionSpec,
    RelativePositionSpec,
)

PlacementSpecMap = dict[ComponentId, PositionSpec]
SpecializedAbsoluteResolver = Callable[[], DiaChi]
SpecializedRelativeTransform = Callable[[DiaChi], DiaChi]


@dataclass(frozen=True)
class SpecializedAbsoluteSpec:
    position_fn: SpecializedAbsoluteResolver


@dataclass(frozen=True)
class SpecializedRelativeSpec:
    reference_id: ComponentId
    transform: SpecializedRelativeTransform


SpecializedPositionSpec = SpecializedAbsoluteSpec | SpecializedRelativeSpec
SpecializedPlacementSpecMap = dict[ComponentId, SpecializedPositionSpec]


@dataclass(frozen=True)
class SpecializedPlacementRules:
    specs: SpecializedPlacementSpecMap


class PlacementRuleCompiler(PlacementRegistry):
    """Incrementally register rules, then compile them for one context."""

    def __init__(self) -> None:
        self._specs: PlacementSpecMap = {}

    def register_component_lazy(self, component_id: ComponentId, spec: PositionSpec) -> None:
        if component_id in self._specs:
            raise ValueError(f"Duplicate component id in placement specs: {component_id}")
        self._specs[component_id] = spec

    def register_component(self, component_id: ComponentId, position: DiaChi) -> None:
        self.register_component_lazy(
            component_id,
            AbsolutePositionSpec(lambda _ctx, pos=position: pos),
        )

    def register_rules(self, rules: Iterable[Rule]) -> None:
        for rule in rules:
            rule.register_components(self)

    def compile(self, context: LaSoContext) -> SpecializedPlacementRules:
        specs = self._specialize(context)
        self._validate_references_exist(specs)
        return SpecializedPlacementRules(specs=specs)

    def _specialize(self, context: LaSoContext) -> SpecializedPlacementSpecMap:
        specialized: SpecializedPlacementSpecMap = {}
        for component_id, spec in self._specs.items():
            if isinstance(spec, RelativePositionSpec):
                reference_id = spec.resolve_reference_id(context)
                specialized[component_id] = SpecializedRelativeSpec(
                    reference_id=reference_id,
                    transform=lambda position, tr=spec.transform, ctx=context: tr(
                        position, ctx
                    ),
                )
            elif isinstance(spec, AbsolutePositionSpec):
                specialized[component_id] = SpecializedAbsoluteSpec(
                    position_fn=lambda fn=spec.position_fn, ctx=context: fn(ctx),
                )
            else:
                raise ValueError(f"Invalid position spec: {spec}")
        return specialized

    @staticmethod
    def _validate_references_exist(specs: SpecializedPlacementSpecMap) -> None:
        for component_id, spec in specs.items():
            if isinstance(spec, SpecializedRelativeSpec):
                reference_id = spec.reference_id
                if reference_id not in specs:
                    raise KeyError(
                        "Component reference has no registered position spec: "
                        f"{component_id} -> {reference_id}"
                    )

