import datetime as dt

from src.refactored.placement.registry import (
    AbsolutePositionSpec,
    ComponentId,
    DynamicRelativePositionSpec,
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
        self._position_specs: dict[ComponentId, PositionSpec] = {}
        self._positions: dict[ComponentId, DiaChi] = {}
        self._resolving: list[ComponentId] = []

    def get_or_resolve_position(self, component_id: ComponentId) -> DiaChi:
        """Find the position of a registered component."""
        if component_id in self._positions:
            return self._positions[component_id]
        if component_id not in self._position_specs:
            raise KeyError(f"Component has no registered position spec: {component_id}")
        return self._compute_position(component_id)

    def register_component(
        self, component_id: ComponentId, position: DiaChi
    ) -> None:
        """Register a component with a known position."""
        self._positions[component_id] = position

    def register_component_lazy(
        self, component_id: ComponentId, spec: PositionSpec
    ) -> None:
        """Register a component position spec for later resolution."""
        self._position_specs[component_id] = spec

    def register_rules(self, rules) -> None:
        """Register declarative placement rules into the builder."""
        for rule in rules:
            rule.register_components(self)

    def resolve_pending(self) -> None:
        """Resolve all pending components using their declared specs."""
        for component_id in list(self._position_specs):
            if component_id not in self._positions:
                self._compute_position(component_id)

    def resolve_all(self) -> dict[ComponentId, DiaChi]:
        """Resolve all pending components and return an id-based position mapping."""
        self.resolve_pending()
        return dict(self._positions)

    def _compute_position(self, component_id: ComponentId) -> DiaChi:
        """Compute and cache a component position from its declared spec."""
        if component_id in self._resolving:
            cycle = " -> ".join([*self._resolving, component_id])
            raise ValueError(f"Circular position dependency detected: {cycle}")

        self._resolving.append(component_id)
        try:
            spec = self._position_specs[component_id]
            if isinstance(spec, RelativePositionSpec):
                reference_position = self.get_or_resolve_position(spec.reference_id)
                position = spec.transform(reference_position, self._la_so_context)
            elif isinstance(spec, DynamicRelativePositionSpec):
                reference_id = spec.reference_id_fn(self._la_so_context)
                reference_position = self.get_or_resolve_position(reference_id)
                position = spec.transform(reference_position, self._la_so_context)
            elif isinstance(spec, AbsolutePositionSpec):
                position = spec.position_fn(self._la_so_context)
            else:
                raise ValueError(f"Invalid position spec: {spec}")
        finally:
            self._resolving.pop()

        self.register_component(component_id, position)
        return position
