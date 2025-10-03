import datetime as dt
from dataclasses import dataclass

from src.refactored.builder.components_registry import (
    PositionResolver,
    RelativePositionResolver,
)
from src.refactored.component import Component, ComponentRegistry
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import Gender, LaSoPrior


@dataclass
class PositionedComponent:
    component: Component
    position: DiaChi


class Builder(ComponentRegistry):
    def __init__(self, time: dt.datetime, gender: Gender) -> None:
        self._la_so_prior = LaSoPrior.from_solar_day(time, gender)
        self._component_resolvers: dict[Component, PositionResolver] = {}
        self._component_registry: dict[Component, PositionedComponent] = {}

    def get_or_resolve_position(self, component: Component) -> DiaChi:
        """Find the position of a registered component."""
        if component in self._component_registry:
            return self._component_registry[component].position
        return self._resolve_position(component)

    def register_component(self, component: Component, position: DiaChi) -> None:
        """Register a component with a known position."""
        self._component_registry[component] = PositionedComponent(component, position)

    def register_component_lazy(
        self, component: Component, resolver: PositionResolver
    ) -> None:
        """Register a component with a position resolver for later resolution."""
        self._component_resolvers[component] = resolver

    def resolve_pending(self) -> None:
        """Resolve all pending components using their resolvers."""
        for component in self._component_resolvers:
            if component not in self._component_registry:
                self._resolve_position(component)

    def _resolve_position(self, component: Component) -> DiaChi:
        """Resolve the position of a component."""
        resolver = self._component_resolvers[component]
        if isinstance(resolver, RelativePositionResolver):
            position = resolver(component, self)
        else:
            position = resolver(self._la_so_prior)
        self.register_component(component, position)
        return position
