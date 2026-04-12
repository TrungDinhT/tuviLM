import datetime as dt

import pytest

from src.refactored.builder.placement_builder import PlacementBuilder
from src.refactored.builder.placement_registry import (
    AbsolutePositionSpec,
    RelativePositionSpec,
)
from src.refactored.component.elementary import DiaChi
from src.refactored.component.prior import Gender


def test_builder_resolves_chained_specs_in_any_order():
    component_a = "A"
    component_b = "B"
    component_c = "C"

    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)

    builder.register_component_lazy(
        component_c,
        RelativePositionSpec(component_b, lambda position: position + 1),
    )
    builder.register_component_lazy(
        component_b,
        RelativePositionSpec(component_a, lambda position: position + 1),
    )
    builder.register_component_lazy(
        component_a,
        AbsolutePositionSpec(lambda _context: DiaChi.DAN),
    )

    builder.resolve_pending()

    assert builder.get_or_resolve_position(component_a) == DiaChi.DAN
    assert builder.get_or_resolve_position(component_b) == DiaChi.MEO
    assert builder.get_or_resolve_position(component_c) == DiaChi.THIN


def test_builder_supports_prior_aware_relative_specs():
    component_a = "A"
    component_b = "B"

    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    builder.register_component_lazy(
        component_b,
        RelativePositionSpec(
            component_a,
            lambda position, context: position + context.van_direction(),
        ),
    )
    builder.register_component_lazy(
        component_a,
        AbsolutePositionSpec(lambda _context: DiaChi.DAN),
    )

    builder.resolve_pending()

    assert builder.get_or_resolve_position(component_b) == DiaChi.MEO


def test_builder_detects_circular_position_dependencies():
    component_a = "A"
    component_b = "B"

    builder = PlacementBuilder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
    builder.register_component_lazy(
        component_a,
        RelativePositionSpec(component_b, lambda position: position + 1),
    )
    builder.register_component_lazy(
        component_b,
        RelativePositionSpec(component_a, lambda position: position + 1),
    )

    with pytest.raises(ValueError, match="Circular position dependency detected"):
        builder.resolve_pending()
