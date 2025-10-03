from typing import Callable, Protocol

from src.refactored.component.elementary import DiaChi
from src.refactored.component import Component, ComponentRegistry
from src.refactored.component.prior import LaSoPrior


PositionTransform = Callable[[DiaChi], DiaChi]


class RelativePositionResolver:
    """Protocol for resolvers that resolve position relative to another component."""

    def __init__(
        self, reference_component: Component, transform: PositionTransform
    ) -> None:
        """Initialize a relative position resolver."""
        self._reference_component = reference_component
        self._transform = transform

    def __call__(self, component: Component, registry: ComponentRegistry) -> DiaChi:
        """Resolve the position of a component relative to another component."""
        reference_position = registry.get_or_resolve_position(self._reference_component)
        return self._transform(reference_position)


AbsolutePositionResolver = Callable[[LaSoPrior], DiaChi]


PositionResolver = RelativePositionResolver | AbsolutePositionResolver


class ComponentRegistry(Protocol):
    """Protocol for a registry of components."""

    def get_or_resolve_position(self, component: Component) -> DiaChi:
        """Get or resolve the position of a component."""
        ...

    def register_component(self, component: Component, position: DiaChi) -> None:
        """Register a component with a known position."""
        ...

    def register_component_lazy(
        self, component: Component, resolver: PositionResolver
    ) -> None:
        """Register a component with a position resolver for later resolution."""
        ...
