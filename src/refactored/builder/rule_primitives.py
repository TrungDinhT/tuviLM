from functools import partial
from typing import Callable, Protocol

from src.refactored.builder.components_registry import (
    AbsolutePositionResolver,
    AbsolutePositionSpec,
    ComponentRegistry,
    PositionTransform,
    RelativePositionSpec,
)
from src.refactored.component import Component
from src.refactored.component.elementary import CyclicIndexMixin, DiaChi
from src.refactored.component.prior import LaSoContext
from src.refactored.transform import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop_nghich,
    get_tam_hop_thuan,
    get_xung_chieu,
)

ContextStepSelector = Callable[[LaSoContext], int]


class Rule(Protocol):
    """Protocol for rules to register component into a component registry."""

    def register_components(self, registry: ComponentRegistry): ...


# ========================= Relative Position Rules =========================


class RelativePosition(Rule):
    """Rule to register a component relative to another component."""

    def __init__(
        self,
        *,
        component: Component,
        reference: Component,
        transform: PositionTransform,
    ):
        self.component = component
        self.reference = reference
        self.transform = transform

    def register_components(self, registry: ComponentRegistry):
        registry.register_component_lazy(
            self.component,
            RelativePositionSpec(self.reference, self.transform),
        )


class SamePosition(RelativePosition):
    """Rule to register a component at the same position as another component."""

    def __init__(self, *, component: Component, reference: Component):
        super().__init__(
            component=component,
            reference=reference,
            transform=partial(_offset_by, offset=0),
        )


class XungChieu(RelativePosition):
    """Rule to register a component at the opposite position of another component."""

    def __init__(self, *, component: Component, reference: Component):
        super().__init__(
            component=component,
            reference=reference,
            transform=get_xung_chieu,
        )


class NhiHop(RelativePosition):
    """Rule to register a component at the nhi hop position of another component."""

    def __init__(self, *, component: Component, reference: Component):
        super().__init__(
            component=component,
            reference=reference,
            transform=get_nhi_hop,
        )


class LucHai(RelativePosition):
    """Rule to register a component at the luc hai position of another component."""

    def __init__(self, *, component: Component, reference: Component):
        super().__init__(
            component=component,
            reference=reference,
            transform=get_luc_hai,
        )


class TamHopThuan(RelativePosition):
    """Rule to register a component at the tam hop position of another component."""

    def __init__(self, *, component: Component, reference: Component):
        super().__init__(
            component=component,
            reference=reference,
            transform=get_tam_hop_thuan,
        )


class TamHopNghich(RelativePosition):
    """Rule to register a component at the tam hop nghich position of another component."""

    def __init__(self, *, component: Component, reference: Component):
        super().__init__(
            component=component,
            reference=reference,
            transform=get_tam_hop_nghich,
        )


class Vong(Rule):
    """Rule to register a group of components in a circular order."""

    def __init__(
        self,
        principal: Component,
        principal_position_fn: AbsolutePositionResolver,
        others: list[Component],
    ):
        self.principal = principal
        self.principal_position_fn = principal_position_fn
        self.others = others

    def register_components(self, registry: ComponentRegistry):
        registry.register_component_lazy(
            self.principal,
            AbsolutePositionSpec(self.principal_position_fn),
        )
        for idx, component in enumerate(self.others):
            registry.register_component_lazy(
                component,
                RelativePositionSpec(
                    self.principal, partial(_offset_by, offset=idx + 1)
                ),
            )


class AbsolutePosition(Rule):
    """Rule to register a component at an absolute position."""

    def __init__(self, *, component: Component, position_fn: AbsolutePositionResolver):
        self.component = component
        self.position_fn = position_fn

    def register_components(self, registry: ComponentRegistry):
        registry.register_component_lazy(
            self.component,
            AbsolutePositionSpec(self.position_fn),
        )


def move_by_van_direction(
    step_selector: ContextStepSelector, *, multiplier: int = 1
) -> PositionTransform:
    """Move from a reference position using van direction and context-derived steps."""

    def transform(reference_position: DiaChi, context: LaSoContext) -> DiaChi:
        steps = step_selector(context) * multiplier
        return reference_position + context.van_direction() * steps

    return transform


def move_by_la_so_attr(
    attribute_name: str, *, multiplier: int = 1
) -> PositionTransform:
    """Build a relative transform from a prior attribute such as `month` or `hour`."""
    return move_by_van_direction(
        partial(_get_prior_attr_steps, attribute_name=attribute_name),
        multiplier=multiplier,
    )


# ========================= Absolute Position Rules =========================


def thai_tue_position_fn(context: LaSoContext) -> DiaChi:
    """Thái Tuế an tại cung theo Địa Chi năm sinh."""
    return context.prior.get_dia_chi()


# ========================= Utility functions =========================
def _offset_by(position: DiaChi, offset: int) -> DiaChi:
    return position + offset


def _get_prior_attr_steps(context: LaSoContext, attribute_name: str) -> int:
    value = getattr(context.prior, attribute_name)
    if isinstance(value, int):
        return value
    if isinstance(value, CyclicIndexMixin):
        return value.index
    raise TypeError(
        f"Prior attribute `{attribute_name}` must be an int or derived from `CyclicIndexMixin`."
    )
