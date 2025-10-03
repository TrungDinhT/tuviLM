from functools import partial
from src.refactored.component import Component
from src.refactored.component.elementary import DiaChi
from typing import Protocol
from src.refactored.builder.components_registry import (
    ComponentRegistry,
    RelativePositionResolver,
    PositionTransform,
)
from src.refactored.transform import (
    get_xung_chieu,
    get_nhi_hop,
    get_luc_hai,
    get_tam_hop_thuan,
    get_tam_hop_nghich,
)


def offset_position(position: DiaChi, offset: int) -> DiaChi:
    return position + offset


class Rule(Protocol):
    """Protocol for rules to register component into a component registry."""

    def register_components(self, registry: ComponentRegistry): ...


class RelativePosition(Rule):
    """Rule to register a component relative to another component."""

    def __init__(
        self, *, reference: Component, other: Component, transform: PositionTransform
    ):
        self.reference = reference
        self.other = other
        self.transform = transform

    def register_components(self, registry: ComponentRegistry):
        registry.register_component_lazy(
            self.other,
            RelativePositionResolver(self.reference, self.transform),
        )


class SamePosition(RelativePosition):
    """Rule to register a component at the same position as another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=partial(offset_position, offset=0),
        )


class XungChieu(RelativePosition):
    """Rule to register a component at the opposite position of another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=get_xung_chieu,
        )


class NhiHop(RelativePosition):
    """Rule to register a component at the nhi hop position of another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=get_nhi_hop,
        )


class LucHai(RelativePosition):
    """Rule to register a component at the luc hai position of another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=get_luc_hai,
        )


class TamHopThuan(RelativePosition):
    """Rule to register a component at the tam hop position of another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=get_tam_hop_thuan,
        )


class TamHopNghich(RelativePosition):
    """Rule to register a component at the tam hop nghich position of another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=get_tam_hop_nghich,
        )


class CircularOrderedGroup(Rule):
    """Rule to register a group of components in a circular order."""

    def __init__(self, principal: Component, others: list[Component]):
        self.principal = principal
        self.others = others

    def register_components(self, registry: ComponentRegistry):
        for idx, component in enumerate(self.others):
            registry.register_component_lazy(
                component,
                RelativePositionResolver(
                    self.principal, partial(offset_position, offset=idx + 1)
                ),
            )
