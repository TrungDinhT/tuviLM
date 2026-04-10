import datetime as dt

import pytest

from src.refactored.builder.builder import Builder
from src.refactored.builder.components_registry import (
    AbsolutePositionSpec,
    RelativePositionSpec,
)
from src.refactored.component.elementary import ComponentBase, DiaChi
from src.refactored.component.prior import Gender


def test_builder_resolves_chained_specs_in_any_order():
    component_a = ComponentBase(name="A")
    component_b = ComponentBase(name="B")
    component_c = ComponentBase(name="C")

    builder = Builder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)

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
        AbsolutePositionSpec(lambda _prior: DiaChi.DAN),
    )

    builder.resolve_pending()

    assert builder.get_or_resolve_position(component_a) == DiaChi.DAN
    assert builder.get_or_resolve_position(component_b) == DiaChi.MEO
    assert builder.get_or_resolve_position(component_c) == DiaChi.THIN


def test_builder_detects_circular_position_dependencies():
    component_a = ComponentBase(name="A")
    component_b = ComponentBase(name="B")

    builder = Builder(dt.datetime(1996, 12, 19, 6, 30), Gender.MALE)
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
