from __future__ import annotations

from typing import Callable, TypeAlias

from src.refactored.context.protocol import PlacementContext
from src.refactored.model.elementary import CircleDirection, DiaChi
from src.refactored.placement.registry import AbsolutePositionResolver, PositionTransform
from src.refactored.placement.rules.positions import absolute, relative
from src.refactored.placement.transforms import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop,
    get_xung_chieu,
    mirror_across,
)

PairPositionResolver = Callable[[PlacementContext], tuple[DiaChi, DiaChi]]
TransformBuilder: TypeAlias = Callable[..., PositionTransform]
StepSelector: TypeAlias = Callable[[PlacementContext], int]

ABSOLUTE_FORMULAS: dict[str, AbsolutePositionResolver] = {
    "menh_position": absolute.menh_position_fn,
    "tuvi_position": absolute.tuvi_position_fn,
    "thai_tue_position": absolute.thai_tue_position_fn,
    "loc_ton_position": absolute.loc_ton_position_fn,
    "dau_quan_position": absolute.dau_quan_position_fn,
    "trang_sinh_position": absolute.trang_sinh_position_fn,
}

PAIR_FORMULAS: dict[str, PairPositionResolver] = {
    "triet_positions": absolute.triet_positions_fn,
    "tuan_positions": absolute.tuan_positions_fn,
}

DIRECTIONS: dict[str, CircleDirection] = {
    "cw": CircleDirection.CW,
    "ccw": CircleDirection.CCW,
}

TRANSFORM_BUILDERS: dict[str, TransformBuilder] = {
    "same": lambda **_: relative.same_position,
    "xung_chieu": lambda **_: get_xung_chieu,
    "nhi_hop": lambda **_: get_nhi_hop,
    "luc_hai": lambda **_: get_luc_hai,
    "tam_hop": lambda **kwargs: _build_tam_hop_transform(kwargs["direction"]),
    "mirror_across": lambda **kwargs: _build_mirror_across_transform(kwargs["axis"]),
    "move_by_dia_chi": lambda **kwargs: relative.move_by_dia_chi(
        direction=DIRECTIONS[kwargs["direction"]],
        step_multiplier=kwargs["step_multiplier"],
    ),
    "move_by_birth_hour": lambda **kwargs: relative.move_by_birth_hour(
        direction=DIRECTIONS[kwargs["direction"]],
        step_multiplier=kwargs["step_multiplier"],
    ),
    "move_by_birth_month": lambda **kwargs: relative.move_by_birth_month(
        direction=DIRECTIONS[kwargs["direction"]],
        step_multiplier=kwargs["step_multiplier"],
    ),
    "move_by_birth_date": lambda **kwargs: relative.move_with(
        lambda context, offset=kwargs["date_offset"]: context.prior.date + offset,
        direction=DIRECTIONS[kwargs["direction"]],
        step_multiplier=kwargs["step_multiplier"],
    ),
    "move_by_van_direction": lambda **kwargs: relative.move_by_van_direction(
        _build_step_selector(kwargs["step"]),
        step_multiplier=kwargs["step_multiplier"],
    ),
}

STEP_SELECTORS: dict[str, StepSelector] = {
    "birth_hour_index": lambda context: context.prior.hour.index,
}


def resolve_absolute_formula(name: str) -> AbsolutePositionResolver:
    try:
        return ABSOLUTE_FORMULAS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown absolute placement formula: {name}") from exc


def resolve_pair_formula(name: str) -> PairPositionResolver:
    try:
        return PAIR_FORMULAS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown pair placement formula: {name}") from exc


def build_transform(
    transform: str,
    *,
    direction: str | None = None,
    axis: tuple[str, str] | None = None,
    step_multiplier: int = 1,
    date_offset: int = 0,
    step: str | int | None = None,
) -> PositionTransform:
    try:
        builder = TRANSFORM_BUILDERS[transform]
    except KeyError as exc:
        raise ValueError(f"Unknown placement transform: {transform}") from exc
    return builder(
        direction=direction,
        axis=axis,
        step_multiplier=step_multiplier,
        date_offset=date_offset,
        step=step,
    )


def build_circle_offset_transform(direction: str, offset: int) -> PositionTransform:
    if direction == "van":
        return relative.move_by_van_direction(
            lambda _context, step=offset: step
        )
    return relative.move_with(
        lambda _context, step=offset: step,
        direction=DIRECTIONS[direction],
    )


def _build_step_selector(step: str | int | None) -> StepSelector:
    if isinstance(step, int):
        return lambda _context: step
    if step is None:
        raise ValueError("Context-aware transform requires `step`.")
    try:
        return STEP_SELECTORS[step]
    except KeyError as exc:
        raise ValueError(f"Unknown step selector: {step}") from exc


def _build_tam_hop_transform(direction: str) -> PositionTransform:
    return lambda position: get_tam_hop(position, DIRECTIONS[direction])


def _build_mirror_across_transform(
    axis: tuple[str, str] | None,
) -> PositionTransform:
    if axis is None:
        raise ValueError("`mirror_across` transform requires `axis`.")
    parsed_axis = (DiaChi(axis[0]), DiaChi(axis[1]))
    return lambda position: mirror_across(position, parsed_axis)
