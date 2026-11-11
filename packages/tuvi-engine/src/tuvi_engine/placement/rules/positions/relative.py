from __future__ import annotations

from typing import Callable, Mapping

from src.refactored.context.protocol import PlacementContext
from src.refactored.model.elementary import (
    CircleDirection,
    DiaChi,
    IndexedEnumMixin,
)
from src.refactored.placement.registry import AbsolutePositionResolver, PositionTransform

ContextStepSelector = Callable[[PlacementContext], int]
DiaChiGroup = tuple[DiaChi, ...]


def position_by_dia_chi_groups(
    groups: Mapping[DiaChiGroup, DiaChi],
) -> AbsolutePositionResolver:
    resolved_positions = {
        dia_chi: position
        for list_dia_chi, position in groups.items()
        for dia_chi in list_dia_chi
    }

    expected_size = sum(len(birth_dia_chis) for birth_dia_chis in groups)
    if len(resolved_positions) != expected_size:
        raise ValueError("Birth DiaChi groups must not overlap.")

    return lambda context: resolved_positions[context.dia_chi]


def move_by_dia_chi(
    direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_with(
        lambda context: context.dia_chi.index,
        direction=direction,
        step_multiplier=step_multiplier,
    )


def move_by_birth_hour(
    direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_by_attr(
        "hour",
        direction=direction,
        step_multiplier=step_multiplier,
    )


def move_by_birth_month(
    direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_with(
        lambda context: context.prior.month - 1,
        direction=direction,
        step_multiplier=step_multiplier,
    )


def move_with(
    step_selector: ContextStepSelector,
    *,
    direction: CircleDirection,
    step_multiplier: int = 1,
) -> PositionTransform:
    def transform(reference_position: DiaChi, context: PlacementContext) -> DiaChi:
        steps = step_selector(context) * step_multiplier
        return reference_position + direction * steps

    return transform


def move_by_van_direction(
    step_selector: ContextStepSelector, *, step_multiplier: int = 1
) -> PositionTransform:
    def transform(reference_position: DiaChi, context: PlacementContext) -> DiaChi:
        steps = step_selector(context) * step_multiplier
        return reference_position + context.van_direction * steps

    return transform


def move_by_attr(
    attribute_name: str,
    *,
    direction: CircleDirection,
    step_multiplier: int = 1,
) -> PositionTransform:
    return move_with(
        lambda context: _get_prior_attr_steps(context, attribute_name),
        direction=direction,
        step_multiplier=step_multiplier,
    )


def offset_transform(offset: int) -> Callable[[DiaChi], DiaChi]:
    return lambda position: position + offset


def same_position(position: DiaChi) -> DiaChi:
    return position


def _get_prior_attr_steps(context: PlacementContext, attribute_name: str) -> int:
    value = getattr(context.prior, attribute_name)
    if isinstance(value, int):
        return value
    if isinstance(value, IndexedEnumMixin):
        return value.index
    raise TypeError(
        f"Prior attribute `{attribute_name}` must be an int or derived from `IndexedEnumMixin`."
    )
