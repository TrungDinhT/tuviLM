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

    def _validate_structural_integrity(self) -> None:
        for component_id, spec in self.specs.items():
            if isinstance(spec, SpecializedRelativeSpec):
                reference_id = spec.reference_id
                if reference_id not in self.specs:
                    raise KeyError(
                        "Component reference has no registered position spec: "
                        f"{component_id} -> {reference_id}"
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

    def compile(
        self,
        context: PlacementContext,
        *,
        scope: Set[ComponentId] | None = None,
        seed: Mapping[ComponentId, DiaChi] | None = None,
    ) -> SpecializedPlacementRules:
        """Compile registered placement specs for one context.

        When `scope` is provided, only the requested component ids and their
        unseeded dependency closure are specialized. References outside the
        compiled graph are rewritten from `seed`.
        """
        specialized_specs = self._specialize(
            context=context,
            scope=set(self._specs) if scope is None else set(scope),
            seed=seed or {},
        )
        return SpecializedPlacementRules(specs=specialized_specs)

    def _specialize(
        self,
        *,
        context: PlacementContext,
        scope: Set[ComponentId],
        seed: Mapping[ComponentId, DiaChi],
    ) -> SpecializedPlacementSpecMap:
        specialized: SpecializedPlacementSpecMap = {}
        resolving: list[ComponentId] = []

        def visit(component_id: ComponentId) -> None:
            if component_id in specialized:
                return
            if component_id in resolving:
                cycle = " -> ".join([*resolving, component_id])
                raise ValueError(f"Circular position dependency detected: {cycle}")
            try:
                spec = self._specs[component_id]
            except KeyError as exc:
                raise KeyError(
                    f"Component id `{component_id}` has no registered position spec."
                ) from exc

            resolving.append(component_id)
            try:
                if isinstance(spec, AbsolutePositionSpec):
                    specialized[component_id] = SpecializedAbsoluteSpec(
                        position_fn=lambda fn=spec.position_fn, ctx=context: fn(ctx),
                    )
                    return

                if isinstance(spec, RelativePositionSpec):
                    reference_id = spec.resolve_reference_id(context)
                    if reference_id in seed and reference_id not in scope:
                        anchor_position = seed[reference_id]
                        tr = spec.transform
                        specialized[component_id] = SpecializedAbsoluteSpec(
                            position_fn=lambda p=anchor_position, fn=tr, ctx=context: fn(
                                p, ctx
                            ),
                        )
                    else:
                        visit(reference_id)
                        specialized[component_id] = SpecializedRelativeSpec(
                            reference_id=reference_id,
                            transform=lambda position, tr=spec.transform, ctx=context: tr(
                                position, ctx
                            ),
                        )
                    return

                raise ValueError(f"Invalid position spec: {spec}")
            finally:
                resolving.pop()

        for component_id in scope:
            visit(component_id)

        return specialized
