import datetime as dt

from src.refactored.builder.placement_registry import (
    AbsolutePositionSpec,
    ComponentName,
    PlacementRegistry,
    PositionSpec,
    RelativePositionSpec,
)
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import Gender, LaSoContext, LaSoPrior


class PlacementBuilder(PlacementRegistry):
    def __init__(self, time: dt.datetime, gender: Gender) -> None:
        la_so_prior = LaSoPrior.from_solar_day(time, gender)
        self._la_so_context = LaSoContext.from_prior(la_so_prior)
        self._position_specs: dict[ComponentName, PositionSpec] = {}
        self._positions: dict[ComponentName, DiaChi] = {}
        self._resolving: list[ComponentName] = []

    def get_or_resolve_position(self, component_name: ComponentName) -> DiaChi:
        """Find the position of a registered component."""
        if component_name in self._positions:
            return self._positions[component_name]
        if component_name not in self._position_specs:
            raise KeyError(f"Component has no registered position spec: {component_name}")
        return self._compute_position(component_name)

    def register_component(
        self, component_name: ComponentName, position: DiaChi
    ) -> None:
        """Register a component with a known position."""
        self._positions[component_name] = position

    def register_component_lazy(
        self, component_name: ComponentName, spec: PositionSpec
    ) -> None:
        """Register a component position spec for later resolution."""
        self._position_specs[component_name] = spec

    def register_rules(self, rules) -> None:
        """Register declarative placement rules into the builder."""
        for rule in rules:
            rule.register_components(self)

    def resolve_pending(self) -> None:
        """Resolve all pending components using their declared specs."""
        for component_name in list(self._position_specs):
            if component_name not in self._positions:
                self._compute_position(component_name)

    def resolve_all(self) -> dict[ComponentName, DiaChi]:
        """Resolve all pending components and return a name-based position mapping."""
        self.resolve_pending()
        return dict(self._positions)

    def _compute_position(self, component_name: ComponentName) -> DiaChi:
        """Compute and cache a component position from its declared spec."""
        if component_name in self._resolving:
            cycle = " -> ".join([*self._resolving, component_name])
            raise ValueError(f"Circular position dependency detected: {cycle}")

        self._resolving.append(component_name)
        try:
            spec = self._position_specs[component_name]
            if isinstance(spec, RelativePositionSpec):
                reference_position = self.get_or_resolve_position(spec.reference_name)
                position = spec.transform(reference_position, self._la_so_context)
            elif isinstance(spec, AbsolutePositionSpec):
                position = spec.position_fn(self._la_so_context)
            else:
                raise ValueError(f"Invalid position spec: {spec}")
        finally:
            self._resolving.pop()

        self.register_component(component_name, position)
        return position
