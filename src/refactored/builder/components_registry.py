import inspect
from dataclasses import dataclass, field
from typing import Callable, Protocol

from src.refactored.component import Component
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import LaSoContext


SimplePositionTransform = Callable[[DiaChi], DiaChi]
RelativePositionTransform = Callable[[DiaChi, LaSoContext], DiaChi]
PositionTransform = SimplePositionTransform | RelativePositionTransform
AbsolutePositionResolver = Callable[[LaSoContext], DiaChi]


def normalize_position_transform(
    transform: PositionTransform,
) -> RelativePositionTransform:
    """Adapt relative transforms to a uniform `(position, context)` signature."""
    param_count = len(inspect.signature(transform).parameters)

    if param_count == 1:
        return lambda position, _context: transform(position)
    if param_count == 2:
        return transform

    raise TypeError(
        "Relative position transforms must accept either "
        "`(position)` or `(position, context)`."
    )


@dataclass(frozen=True)
class AbsolutePositionSpec:
    """Declarative spec for positions resolved directly from chart context."""

    position_fn: AbsolutePositionResolver


@dataclass(frozen=True)
class RelativePositionSpec:
    """Declarative spec for positions derived from another component."""

    reference: Component
    transform: RelativePositionTransform = field(repr=False)

    def __init__(self, reference: Component, transform: PositionTransform) -> None:
        object.__setattr__(self, "reference", reference)
        object.__setattr__(
            self,
            "transform",
            normalize_position_transform(transform),
        )


PositionSpec = AbsolutePositionSpec | RelativePositionSpec


class ComponentRegistry(Protocol):
    """Protocol for registering declarative component position specs."""

    def register_component_lazy(self, component: Component, spec: PositionSpec) -> None:
        """Register a component position spec for later resolution."""
        ...
