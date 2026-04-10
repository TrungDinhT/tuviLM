from dataclasses import dataclass
from typing import Callable, Protocol

from src.refactored.component import Component
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import LaSoPrior


PositionTransform = Callable[[DiaChi], DiaChi]
AbsolutePositionResolver = Callable[[LaSoPrior], DiaChi]


@dataclass(frozen=True)
class AbsolutePositionSpec:
    """Declarative spec for positions resolved directly from prior data."""

    position_fn: AbsolutePositionResolver


@dataclass(frozen=True)
class RelativePositionSpec:
    """Declarative spec for positions derived from another component."""

    reference_component: Component
    transform: PositionTransform


PositionSpec = AbsolutePositionSpec | RelativePositionSpec


class ComponentRegistry(Protocol):
    """Protocol for registering declarative component position specs."""

    def register_component_lazy(self, component: Component, spec: PositionSpec) -> None:
        """Register a component position spec for later resolution."""
        ...
