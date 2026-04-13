from functools import partial
from typing import Callable, Protocol

from src.refactored.component.elementary import DiaChi, IndexedEnumMixin
from src.refactored.component.prior import LaSoContext
from src.refactored.placement.registry import (
    AbsolutePositionResolver,
    AbsolutePositionSpec,
    ComponentId,
    PlacementRegistry,
    PositionTransform,
    RelativePositionSpec,
)
from src.refactored.placement.transforms import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop_nghich,
    get_tam_hop_thuan,
    get_xung_chieu,
)

ContextStepSelector = Callable[[LaSoContext], int]


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
            transform=partial(offset_by, offset=0),
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


class TamHopThuan(RelativePosition):
    """Rule to register a component at the tam hop position of another component."""

    def __init__(
        self, *, component_id: ComponentId, reference_id: ComponentId
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_tam_hop_thuan,
        )


class TamHopNghich(RelativePosition):
    """Rule to register a component at the tam hop nghich position of another component."""

    def __init__(
        self, *, component_id: ComponentId, reference_id: ComponentId
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_tam_hop_nghich,
        )


class Vong(Rule):
    """Rule to register a group of components in a circular order."""

    def __init__(
        self,
        principal_id: ComponentId,
        principal_position_fn: AbsolutePositionResolver,
        others: list[ComponentId],
    ):
        self.principal_id = principal_id
        self.principal_position_fn = principal_position_fn
        self.others = others

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.principal_id,
            AbsolutePositionSpec(self.principal_position_fn),
        )
        for idx, component_id in enumerate(self.others):
            registry.register_component_lazy(
                component_id,
                RelativePositionSpec(
                    self.principal_id, partial(offset_by, offset=idx + 1)
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


def thai_tue_position_fn(context: LaSoContext) -> DiaChi:
    """Thái Tuế an tại cung theo Địa Chi năm sinh."""
    return context.prior.get_dia_chi()


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


def move_by_van_direction(
    step_selector: ContextStepSelector, *, multiplier: int = 1
) -> PositionTransform:
    """Move from a reference position using van direction and context-derived steps."""

    def transform(reference_position: DiaChi, context: LaSoContext) -> DiaChi:
        steps = step_selector(context) * multiplier
        return reference_position + context.van_direction() * steps

    return transform


def move_by_la_so_attr(
    attribute_name: str, *, step_multiplier: int = 1
) -> PositionTransform:
    """Build a relative transform from a prior attribute such as `month` or `hour`."""
    return move_by_van_direction(
        partial(_get_prior_attr_steps, attribute_name=attribute_name),
        multiplier=step_multiplier,
    )


def offset_by(position: DiaChi, offset: int) -> DiaChi:
    return position + offset


def _get_prior_attr_steps(context: LaSoContext, attribute_name: str) -> int:
    value = getattr(context.prior, attribute_name)
    if isinstance(value, int):
        return value
    if isinstance(value, IndexedEnumMixin):
        return value.index
    raise TypeError(
        f"Prior attribute `{attribute_name}` must be an int or derived from `IndexedEnumMixin`."
    )
