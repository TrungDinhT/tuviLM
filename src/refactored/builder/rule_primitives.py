from functools import partial
from typing import Protocol

from src.refactored.builder.components_registry import (
    AbsolutePositionResolver,
    AbsolutePositionSpec,
    ComponentRegistry,
    PositionTransform,
    RelativePositionSpec,
)
from src.refactored.component import Component
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import LaSoPrior
from src.refactored.transform import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop_nghich,
    get_tam_hop_thuan,
    get_xung_chieu,
)


class Rule(Protocol):
    """Protocol for rules to register component into a component registry."""

    def register_components(self, registry: ComponentRegistry): ...


# ========================= Relative Position Rules =========================

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
            RelativePositionSpec(self.reference, self.transform),
        )


class SamePosition(RelativePosition):
    """Rule to register a component at the same position as another component."""

    def __init__(self, *, reference: Component, other: Component):
        super().__init__(
            reference=reference,
            other=other,
            transform=partial(_offset_by, offset=0),
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


class Vong(Rule):
    """Rule to register a group of components in a circular order."""

    def __init__(self, principal: Component, others: list[Component]):
        self.principal = principal
        self.others = others

    def register_components(self, registry: ComponentRegistry):
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


# ========================= Absolute Position Rules =========================

def menh_position_fn(prior: LaSoPrior) -> DiaChi:
    month_anchor = DiaChi.DAN + (prior.month - 1)
    return month_anchor - prior.hour.index


def thai_tue_position_fn(prior: LaSoPrior) -> DiaChi:
    """Thái Tuế an tại cung theo Địa Chi năm sinh."""
    return prior.get_dia_chi()




# ========================= Utility functions =========================
def _offset_by(position: DiaChi, offset: int) -> DiaChi:
    return position + offset
