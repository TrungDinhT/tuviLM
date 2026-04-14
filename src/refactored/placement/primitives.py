"""Placement DSL primitives used by declarative rule sets.

This module is organized in four layers:
1. Small marker/value objects that help rules stay readable.
2. Rule classes that register absolute or relative placement specs.
3. Reusable position factories that encode common domain formulas.
4. Tiny internal helpers used to adapt offsets and context-derived steps.
"""

from dataclasses import dataclass
from typing import Callable, Protocol

from src.refactored.component.elementary import (
    CircleDirection,
    DiaChi,
    IndexedEnumMixin,
)
from src.refactored.component.prior import LaSoContext
from src.refactored.placement.registry import (
    AbsolutePositionResolver,
    AbsolutePositionSpec,
    ComponentId,
    PlacementRegistry,
    PositionTransform,
    RelativePositionSpec,
    normalize_position_transform,
)
from src.refactored.placement.transforms import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop,
    get_xung_chieu,
    mirror_across,
)

ContextStepSelector = Callable[[LaSoContext], int]


# ---------------------------------------------------------------------------
# Grouping markers for declarative rule blocks
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SameSlot:
    """Marker for multiple components that intentionally share one ring slot."""

    component_ids: tuple[ComponentId, ...]


# `Vong` accepts either a single component ID or a grouped same-slot marker.
VongMember = ComponentId | SameSlot


def same_slot(*component_ids: ComponentId) -> SameSlot:
    """Build a same-slot marker for grouped ring declarations."""

    if len(component_ids) < 2:
        raise ValueError("same_slot requires at least 2 component ids")
    return SameSlot(component_ids)


# ---------------------------------------------------------------------------
# Base protocol and concrete rule declarations
# ---------------------------------------------------------------------------

class Rule(Protocol):
    """Protocol for rules to register placement specs on a builder."""

    def register_components(self, registry: PlacementRegistry): ...


class RelativePosition(Rule):
    """Rule to register a component relative to another component."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        reference_id: ComponentId,
        transform: PositionTransform,
    ):
        self.component_id = component_id
        self.reference_id = reference_id
        self.transform = transform

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.component_id,
            RelativePositionSpec(self.reference_id, self.transform),
        )


class SamePosition(RelativePosition):
    """Rule to register a component at the same position as another component."""

    def __init__(
        self, *, component_id: ComponentId, reference_id: ComponentId
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=_offset_transform(0),
        )


class XungChieu(RelativePosition):
    """Rule to register a component at the opposite position of another component."""

    def __init__(
        self, *, component_id: ComponentId, reference_id: ComponentId
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_xung_chieu,
        )


class NhiHop(RelativePosition):
    """Rule to register a component at the nhi hop position of another component."""

    def __init__(
        self, *, component_id: ComponentId, reference_id: ComponentId
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_nhi_hop,
        )


class LucHai(RelativePosition):
    """Rule to register a component at the luc hai position of another component."""

    def __init__(
        self, *, component_id: ComponentId, reference_id: ComponentId
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_luc_hai,
        )


class TamHop(RelativePosition):
    """Rule to register a component at the directional tam hop position."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        reference_id: ComponentId,
        direction: CircleDirection,
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=lambda position: get_tam_hop(position, direction),
        )


class MirrorAcross(RelativePosition):
    """Rule to mirror a component across an axis from another component."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        reference_id: ComponentId,
        axis: tuple[DiaChi, DiaChi],
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=lambda position: mirror_across(position, axis),
        )


class FromAnchor(Rule):
    """Rule to register a component relative to a fixed DiaChi anchor."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        anchor: DiaChi,
        transform: PositionTransform,
    ):
        self.component_id = component_id
        self.anchor = anchor
        self.transform = normalize_position_transform(transform)

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.component_id,
            AbsolutePositionSpec(
                lambda context: self.transform(self.anchor, context)
            ),
        )


class Vong(Rule):
    """Register a circular sequence of components from one principal anchor.

    `others` advances one DiaChi step at a time, clockwise from the principal
    position.
    A `same_slot(...)` entry means all listed components share that same step.
    """

    def __init__(
        self,
        principal_id: ComponentId,
        principal_position_fn: AbsolutePositionResolver,
        others: list[VongMember],
    ):
        self.principal_id = principal_id
        self.principal_position_fn = principal_position_fn
        self.others = others

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.principal_id,
            AbsolutePositionSpec(self.principal_position_fn),
        )
        for idx, member in enumerate(self.others):
            if isinstance(member, SameSlot):
                anchor_id, *same_slot_ids = member.component_ids
                registry.register_component_lazy(
                    anchor_id,
                    RelativePositionSpec(
                        self.principal_id, _offset_transform(idx + 1)
                    ),
                )
                for component_id in same_slot_ids:
                    registry.register_component_lazy(
                        component_id,
                        RelativePositionSpec(anchor_id, _offset_transform(0)),
                    )
            else:
                registry.register_component_lazy(
                    member,
                    RelativePositionSpec(
                        self.principal_id, _offset_transform(idx + 1)
                    ),
                )


class AbsolutePosition(Rule):
    """Rule to register a component at an absolute position."""

    def __init__(
        self, *, component_id: ComponentId, position_fn: AbsolutePositionResolver
    ):
        self.component_id = component_id
        self.position_fn = position_fn

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.component_id,
            AbsolutePositionSpec(self.position_fn),
        )


class DefinitivePosition(Rule):
    """Rule to register a component at a definitive position."""

    def __init__(
        self, *, component_id: ComponentId, position: DiaChi
    ):
        self.component_id = component_id
        self.position = position

    def register_components(self, registry: PlacementRegistry):
        registry.register_component(
            self.component_id,
            self.position,
        )


# ---------------------------------------------------------------------------
# Domain position factories
# ---------------------------------------------------------------------------

def thai_tue_position_fn(context: LaSoContext) -> DiaChi:
    """Thái Tuế an tại cung theo Địa Chi năm sinh."""
    return context.prior.get_dia_chi()


def loc_ton_position_fn(context: LaSoContext) -> DiaChi:
    """Lộc Tồn an tại cung theo Thiên Can năm sinh."""
    return {
        "Giáp": DiaChi.DAN,
        "Ất": DiaChi.MEO,
        "Bính": DiaChi.TI,
        "Đinh": DiaChi.NGO,
        "Mậu": DiaChi.TI,
        "Kỷ": DiaChi.NGO,
        "Canh": DiaChi.THAN,
        "Tân": DiaChi.DAU,
        "Nhâm": DiaChi.HOI,
        "Quý": DiaChi.TY,
    }[context.prior.get_thien_can()]


def tuvi_position_fn(context: LaSoContext) -> DiaChi:
    """An Tử Vi khởi tại Dần, tính theo ngày sinh và cục số.

    Ceiling-divides the birth date by the cục number to find how many
    steps to travel. Even quotients advance by the remainder, odd
    quotients retreat by the remainder.
    """
    cuc_number = context.cuc.number
    date = context.prior.date

    mod = date % cuc_number
    if mod == 0:
        div = date // cuc_number
        borrow = 0
    else:
        div = date // cuc_number + 1
        borrow = cuc_number - mod

    offset = (div - 1 + borrow) if div % 2 == 0 else (div - 1 - borrow)
    return DiaChi.DAN + offset


# ---------------------------------------------------------------------------
# Reusable transform builders
# ---------------------------------------------------------------------------

def move_by_birth_dia_chi(
    *, direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_with(
        lambda context: context.prior.get_dia_chi().index,
        direction=direction,
        step_multiplier=step_multiplier,
    )


def move_by_birth_hour(
    *, direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_by_attr(
        "hour",
        direction=direction,
        step_multiplier=step_multiplier,
    )


def move_by_birth_month(
    *, direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_with(
        lambda context: context.prior.month - 1,
        direction=direction,
        step_multiplier=step_multiplier,
    )


def move_with(
    step_selector: ContextStepSelector,
    *,
    direction: CircleDirection,
    step_multiplier: int = 1,
) -> PositionTransform:
    """Move from a reference position using a fixed circular direction."""

    def transform(reference_position: DiaChi, context: LaSoContext) -> DiaChi:
        steps = step_selector(context) * step_multiplier
        return reference_position + direction * steps

    return transform


def move_by_van_direction(
    step_selector: ContextStepSelector, *, step_multiplier: int = 1
) -> PositionTransform:
    """Move from a reference position using van direction and context-derived steps."""

    def transform(reference_position: DiaChi, context: LaSoContext) -> DiaChi:
        steps = step_selector(context) * step_multiplier
        return reference_position + context.van_direction() * steps

    return transform


def move_by_attr(
    attribute_name: str,
    *,
    direction: CircleDirection,
    step_multiplier: int = 1,
) -> PositionTransform:
    """Build a fixed-direction transform from a prior attribute."""
    return move_with(
        lambda context: _get_prior_attr_steps(context, attribute_name),
        direction=direction,
        step_multiplier=step_multiplier,
    )


def offset_by(position: DiaChi, offset: int) -> DiaChi:
    return position + offset


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _offset_transform(offset: int) -> Callable[[DiaChi], DiaChi]:
    """Adapt a fixed offset into the simple one-argument transform shape."""
    return lambda position: offset_by(position, offset)


def _get_prior_attr_steps(context: LaSoContext, attribute_name: str) -> int:
    """Read an integer-like step value from `LaSoContext.prior`."""
    value = getattr(context.prior, attribute_name)
    if isinstance(value, int):
        return value
    if isinstance(value, IndexedEnumMixin):
        return value.index
    raise TypeError(
        f"Prior attribute `{attribute_name}` must be an int or derived from `IndexedEnumMixin`."
    )
