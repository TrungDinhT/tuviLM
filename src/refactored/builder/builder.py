import datetime as dt
from dataclasses import dataclass

from src.refactored.builder.components_registry import (
    AbsolutePositionSpec,
    ComponentRegistry,
    PositionSpec,
    RelativePositionSpec,
)
from src.refactored.component import Component
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import Gender, LaSoPrior


@dataclass
class PositionedComponent:
    component: Component
    position: DiaChi


class Builder(ComponentRegistry):
    def __init__(self, time: dt.datetime, gender: Gender) -> None:
        self._la_so_prior = LaSoPrior.from_solar_day(time, gender)
        self._position_specs: dict[Component, PositionSpec] = {}
        self._components: dict[Component, PositionedComponent] = {}
        self._resolving: list[Component] = []

    def get_or_resolve_position(self, component: Component) -> DiaChi:
        """Find the position of a registered component."""
        if component in self._components:
            return self._components[component].position
        if component not in self._position_specs:
            raise KeyError(f"Component has no registered position spec: {component}")
        return self._compute_position(component)

    def register_component(self, component: Component, position: DiaChi) -> None:
        """Register a component with a known position."""
        self._components[component] = PositionedComponent(component, position)

    def register_component_lazy(
        self, component: Component, spec: PositionSpec
    ) -> None:
        """Register a component position spec for later resolution."""
        self._position_specs[component] = spec

    def resolve_pending(self) -> None:
        """Resolve all pending components using their declared specs."""
        for component in list(self._position_specs):
            if component not in self._components:
                self._compute_position(component)

    def _compute_position(self, component: Component) -> DiaChi:
        """Compute and cache a component position from its declared spec."""
        if component in self._resolving:
            cycle = " -> ".join(str(item) for item in [*self._resolving, component])
            raise ValueError(f"Circular position dependency detected: {cycle}")

        self._resolving.append(component)
        try:
            spec = self._position_specs[component]
            if isinstance(spec, RelativePositionSpec):
                reference_position = self.get_or_resolve_position(
                    spec.reference_component
                )
                position = spec.transform(reference_position)
            elif isinstance(spec, AbsolutePositionSpec):
                position = spec.position_fn(self._la_so_prior)
            else:
                raise ValueError(f"Invalid position spec: {spec}")
        finally:
            self._resolving.pop()

        self.register_component(component, position)
        return position
