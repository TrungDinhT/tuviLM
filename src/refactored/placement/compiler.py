from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Set

from src.refactored.component.elementary import DiaChi
from src.refactored.context.protocol import PlacementContext
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

    def __post_init__(self) -> None:
        self._validate_structural_integrity()

    def restrict_to(
        self,
        ids: Set[ComponentId],
        seed: Mapping[ComponentId, DiaChi],
    ) -> SpecializedPlacementRules:
        """Return only `ids` specs, rewriting external references as constants from `seed`."""
        self._check_seed_covers_external_refs(ids, seed)
        new_specs: SpecializedPlacementSpecMap = {}
        for component_id in ids:
            spec = self.specs[component_id]
            if isinstance(spec, SpecializedAbsoluteSpec):
                new_specs[component_id] = spec
            elif isinstance(spec, SpecializedRelativeSpec):
                ref_id = spec.reference_id
                if ref_id in ids:
                    new_specs[component_id] = spec
                else:
                    anchor_position = seed[ref_id]
                    tr = spec.transform
                    new_specs[component_id] = SpecializedAbsoluteSpec(
                        position_fn=lambda p=anchor_position, fn=tr: fn(p),
                    )
            else:
                raise ValueError(f"Invalid position spec: {spec}")
        return SpecializedPlacementRules(specs=new_specs)

    def _validate_structural_integrity(self) -> None:
        for component_id, spec in self.specs.items():
            if isinstance(spec, SpecializedRelativeSpec):
                reference_id = spec.reference_id
                if reference_id not in self.specs:
                    raise KeyError(
                        "Component reference has no registered position spec: "
                        f"{component_id} -> {reference_id}"
                    )

    def _check_seed_covers_external_refs(
        self, ids: Set[ComponentId], seed: Mapping[ComponentId, DiaChi]
    ) -> None:
        for consumer_id in ids:
            spec = self.specs[consumer_id]
            if not isinstance(spec, SpecializedRelativeSpec):
                continue
            ref_id = spec.reference_id
            if ref_id in ids:
                continue
            if ref_id not in seed:
                raise KeyError(
                    f"Restricted spec {consumer_id!r} requires reference {ref_id!r} "
                    "which is not in `ids` and not in `seed`."
                )


class PlacementRuleCompiler(PlacementRegistry):
    """Incrementally register rules, then compile them for one context."""

    def __init__(self) -> None:
        self._specs: PlacementSpecMap = {}

    def register_component_lazy(
        self, component_id: ComponentId, spec: PositionSpec
    ) -> None:
        if component_id in self._specs:
            raise ValueError(
                f"Duplicate component id in placement specs: {component_id}"
            )
        self._specs[component_id] = spec

    def register_component(self, component_id: ComponentId, position: DiaChi) -> None:
        self.register_component_lazy(
            component_id,
            AbsolutePositionSpec(lambda _ctx, pos=position: pos),
        )

    def register_rules(self, rules: Iterable[Rule]) -> None:
        for rule in rules:
            rule.register_components(self)

    def compile(self, context: PlacementContext) -> SpecializedPlacementRules:
        specialized_specs = self._specialize(context)
        return SpecializedPlacementRules(specs=specialized_specs)

    def _specialize(self, context: PlacementContext) -> SpecializedPlacementSpecMap:
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
