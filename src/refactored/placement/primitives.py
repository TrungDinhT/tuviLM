"""Placement DSL primitives used by declarative rule sets.

This module is organized in four layers:
1. Small marker/value objects that help rules stay readable.
2. Rule classes that register absolute or relative placement specs.
3. Reusable position factories that encode common domain formulas.
4. Tiny internal helpers used to adapt offsets and context-derived steps.
"""

from enum import Enum
from typing import Callable, Literal, Mapping, Protocol, get_args

from src.refactored.component.elementary import (
    CircleDirection,
    DiaChi,
    IndexedEnumMixin,
    NguHanh,
    ThienCan,
)
from src.refactored.component.prior import LaSoContext
from src.refactored.placement.registry import (
    AbsolutePositionResolver,
    AbsolutePositionSpec,
    ComponentId,
    PlacementRegistry,
    PositionTransform,
    RelativePositionSpec,
    normalize_position_transform,
)
from src.refactored.placement.transforms import (
    get_luc_hai,
    get_nhi_hop,
    get_tam_hop,
    get_xung_chieu,
    mirror_across,
)

ContextStepSelector = Callable[[LaSoContext], int]
ThienCanPositionMap = Mapping[ThienCan, DiaChi]
DiaChiGroup = tuple[DiaChi, ...]
AnchorResolver = DiaChi | AbsolutePositionResolver
PairPositionResolver = Callable[[LaSoContext], tuple[DiaChi, DiaChi]]

TuHoaEntity = Literal["hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky"]
TUHOA_ENTITIES: tuple[TuHoaEntity, ...] = get_args(TuHoaEntity)


# ---------------------------------------------------------------------------
# Base protocol and concrete rule declarations
# ---------------------------------------------------------------------------


class Rule(Protocol):
    """Protocol for rules to register placement specs on a builder."""

    def register_components(self, registry: PlacementRegistry): ...


class RelativePosition(Rule):
    """Rule to register a component relative to another component."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        reference_id: ComponentId,
        transform: PositionTransform,
    ):
        self.component_id = component_id
        self.reference_id = reference_id
        self.transform = transform

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.component_id,
            RelativePositionSpec(self.reference_id, self.transform),
        )


class SamePosition(RelativePosition):
    """Rule to register a component at the same position as another component."""

    def __init__(self, component_id: ComponentId, reference_id: ComponentId):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=_same_position,
        )


class XungChieu(RelativePosition):
    """Rule to register a component at the opposite position of another component."""

    def __init__(self, *, component_id: ComponentId, reference_id: ComponentId):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_xung_chieu,
        )


class NhiHop(RelativePosition):
    """Rule to register a component at the nhi hop position of another component."""

    def __init__(self, *, component_id: ComponentId, reference_id: ComponentId):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_nhi_hop,
        )


class LucHai(RelativePosition):
    """Rule to register a component at the luc hai position of another component."""

    def __init__(self, *, component_id: ComponentId, reference_id: ComponentId):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=get_luc_hai,
        )


class TamHop(RelativePosition):
    """Rule to register a component at the directional tam hop position."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        reference_id: ComponentId,
        direction: CircleDirection,
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=lambda position: get_tam_hop(position, direction),
        )


class MirrorAcross(RelativePosition):
    """Rule to mirror a component across an axis from another component."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        reference_id: ComponentId,
        axis: tuple[DiaChi, DiaChi],
    ):
        super().__init__(
            component_id=component_id,
            reference_id=reference_id,
            transform=lambda position: mirror_across(position, axis),
        )


class FromAnchor(Rule):
    """Rule to register a component relative to a fixed or computed anchor."""

    def __init__(
        self,
        *,
        component_id: ComponentId,
        anchor: AnchorResolver,
        transform: PositionTransform,
    ):
        self.component_id = component_id
        self.anchor = anchor
        self.transform = normalize_position_transform(transform)

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.component_id,
            AbsolutePositionSpec(
                lambda context: self.transform(
                    self.anchor(context) if callable(self.anchor) else self.anchor,
                    context,
                )
            ),
        )


class AbsolutePosition(Rule):
    """Rule to register a component at an absolute position."""

    def __init__(
        self, *, component_id: ComponentId, position_fn: AbsolutePositionResolver
    ):
        self.component_id = component_id
        self.position_fn = position_fn

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.component_id,
            AbsolutePositionSpec(self.position_fn),
        )


class TuanTrietPosition(Rule):
    """Register two component ids that share one pair-position computation."""

    def __init__(
        self,
        *,
        pair_ids: tuple[ComponentId, ComponentId],
        pair_position_fn: PairPositionResolver,
    ):
        self.pair_ids = pair_ids
        self.pair_position_fn = pair_position_fn

    def register_components(self, registry: PlacementRegistry):
        cache: list[tuple[DiaChi, DiaChi] | None] = [None]

        def _pair(context: LaSoContext) -> tuple[DiaChi, DiaChi]:
            if cache[0] is None:
                cache[0] = self.pair_position_fn(context)
            return cache[0]

        first_id, second_id = self.pair_ids
        registry.register_component_lazy(
            first_id,
            AbsolutePositionSpec(lambda ctx: _pair(ctx)[0]),
        )
        registry.register_component_lazy(
            second_id,
            AbsolutePositionSpec(lambda ctx: _pair(ctx)[1]),
        )


class TuHoaPosition(Rule):
    """Register all four Tứ Hóa positions from one Thiên Can → target sao table."""

    def __init__(
        self, *, mapping: dict[ThienCan, dict[TuHoaEntity, ComponentId]]
    ) -> None:
        self._validate(mapping)
        self.mapping = mapping

    def register_components(self, registry: PlacementRegistry):
        for entity in TUHOA_ENTITIES:
            registry.register_component_lazy(
                entity,
                RelativePositionSpec(
                    lambda ctx, e=entity: self.mapping[ctx.prior.get_thien_can()][e],
                    transform=_same_position,
                ),
            )

    @staticmethod
    def _validate(mapping: dict[ThienCan, dict[TuHoaEntity, ComponentId]]) -> None:
        for thien_can in ThienCan:
            if thien_can not in mapping:
                raise ValueError(f"Missing Tứ Hóa mapping for {thien_can!r}")
            entities = mapping[thien_can]
            for entity in TUHOA_ENTITIES:
                if entity not in entities:
                    raise ValueError(
                        f"Missing `{entity}` for {thien_can!r} in Tứ Hóa mapping."
                    )
                target = entities[entity]
                if target in TUHOA_ENTITIES:
                    raise ValueError(
                        "Tứ Hóa target cannot be another Tứ Hóa entity: "
                        f"{target!r} for {thien_can!r} `{entity}`"
                    )


class DefinitivePosition(Rule):
    """Rule to register a component at a definitive position."""

    def __init__(self, *, component_id: ComponentId, position: DiaChi):
        self.component_id = component_id
        self.position = position

    def register_components(self, registry: PlacementRegistry):
        registry.register_component(
            self.component_id,
            self.position,
        )


class OffsetGroup(Rule):
    """Register components at fixed offsets from an anchor."""

    def __init__(
        self,
        anchor_id: ComponentId,
        anchor_position_fn: AbsolutePositionResolver,
        offsets: dict[ComponentId, int],
    ):
        self.anchor_id = anchor_id
        self.anchor_position_fn = anchor_position_fn
        self.offsets = offsets

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.anchor_id,
            AbsolutePositionSpec(self.anchor_position_fn),
        )
        for component_id, offset in self.offsets.items():
            registry.register_component_lazy(
                component_id,
                RelativePositionSpec(self.anchor_id, _offset_transform(offset)),
            )


CircleMember = ComponentId | SamePosition


class Circle(Rule):
    """Register a circular sequence of components from one principal anchor.

    `others` advances one DiaChi step at a time from the principal following
    the specified direction.
    """

    class Direction(Enum):
        CW = "cw"
        CCW = "ccw"
        VAN = "van"

    def __init__(
        self,
        principal_id: ComponentId,
        principal_position_fn: AbsolutePositionResolver,
        others: list[CircleMember],
        direction: "Circle.Direction" = Direction.CW,
    ):
        self.principal_id = principal_id
        self.principal_position_fn = principal_position_fn
        self.others = others
        self.direction = direction

    def _member_offset_transform(self, offset: int) -> PositionTransform:
        if self.direction is Circle.Direction.CW:
            return move_with(_constant_step(offset), direction=CircleDirection.CW)
        if self.direction is Circle.Direction.CCW:
            return move_with(_constant_step(offset), direction=CircleDirection.CCW)
        if self.direction is Circle.Direction.VAN:
            return move_by_van_direction(_constant_step(offset))
        raise ValueError(f"Invalid vong direction: {self.direction}")

    def _register_vong_member(
        self, registry: PlacementRegistry, member: CircleMember, offset: int
    ):
        if isinstance(member, ComponentId):
            registry.register_component_lazy(
                member,
                RelativePositionSpec(self.principal_id, self._member_offset_transform(offset)),
            )
        elif isinstance(member, SamePosition):
            member.register_components(registry)
            registry.register_component_lazy(
                member.reference_id,
                RelativePositionSpec(self.principal_id, self._member_offset_transform(offset)),
            )
        else:
            raise ValueError(f"Invalid vong member type: {type(member)}")

    def register_components(self, registry: PlacementRegistry):
        registry.register_component_lazy(
            self.principal_id,
            AbsolutePositionSpec(self.principal_position_fn),
        )
        for idx, member in enumerate(self.others):
            offset = idx + 1
            self._register_vong_member(registry, member, offset)


# ---------------------------------------------------------------------------
# Domain position factories
# ---------------------------------------------------------------------------


def menh_position_fn(context: LaSoContext) -> DiaChi:
    return context.menh_position


def tuvi_position_fn(context: LaSoContext) -> DiaChi:
    """An Tử Vi khởi tại Dần, tính theo ngày sinh và cục số.

    Ceiling-divides the birth date by the cục number to find how many
    steps to travel. Even quotients advance by the remainder, odd
    quotients retreat by the remainder.
    """
    cuc_number = context.cuc.number
    date = context.prior.date

    mod = date % cuc_number
    if mod == 0:
        div = date // cuc_number
        borrow = 0
    else:
        div = date // cuc_number + 1
        borrow = cuc_number - mod

    offset = (div - 1 + borrow) if div % 2 == 0 else (div - 1 - borrow)
    return DiaChi.DAN + offset


def thai_tue_position_fn(context: LaSoContext) -> DiaChi:
    """Thái Tuế an tại cung theo Địa Chi năm sinh."""
    return context.prior.get_dia_chi()


def loc_ton_position_fn(context: LaSoContext) -> DiaChi:
    """Lộc Tồn an tại cung theo Thiên Can năm sinh."""
    position_fn = position_by_thien_can(
        {
            ThienCan.GIAP: DiaChi.DAN,
            ThienCan.AT: DiaChi.MEO,
            ThienCan.BINH: DiaChi.TI,
            ThienCan.DINH: DiaChi.NGO,
            ThienCan.MAU: DiaChi.TI,
            ThienCan.KY: DiaChi.NGO,
            ThienCan.CANH: DiaChi.THAN,
            ThienCan.TAN: DiaChi.DAU,
            ThienCan.NHAM: DiaChi.HOI,
            ThienCan.QUY: DiaChi.TY,
        }
    )
    return position_fn(context)


def dau_quan_position_fn(context: LaSoContext) -> DiaChi:
    """Đẩu Quân an từ Địa Chi năm sinh, lùi theo tháng rồi tiến theo giờ."""
    month_position = context.prior.get_dia_chi() - (context.prior.month - 1)
    return month_position + context.prior.hour.index


def trang_sinh_position_fn(context: LaSoContext) -> DiaChi:
    """Tràng Sinh anchor by cục ngũ hành."""
    return {
        NguHanh.KIM: DiaChi.TI,
        NguHanh.MOC: DiaChi.HOI,
        NguHanh.HOA: DiaChi.DAN,
        NguHanh.THO: DiaChi.THAN,
        NguHanh.THUY: DiaChi.THAN,
    }[context.cuc.ngu_hanh]


def triet_positions_fn(context: LaSoContext) -> tuple[DiaChi, DiaChi]:
    """Two Triệt positions from year Thiên Can (legacy MAP_TRIET)."""
    _TRIET_POSITIONS: dict[ThienCan, tuple[DiaChi, DiaChi]] = {
        ThienCan.GIAP: (DiaChi.THAN, DiaChi.DAU),
        ThienCan.AT: (DiaChi.NGO, DiaChi.MUI),
        ThienCan.BINH: (DiaChi.THIN, DiaChi.TI),
        ThienCan.DINH: (DiaChi.DAN, DiaChi.MEO),
        ThienCan.MAU: (DiaChi.TY, DiaChi.SUU),
        ThienCan.KY: (DiaChi.THAN, DiaChi.DAU),
        ThienCan.CANH: (DiaChi.NGO, DiaChi.MUI),
        ThienCan.TAN: (DiaChi.THIN, DiaChi.TI),
        ThienCan.NHAM: (DiaChi.DAN, DiaChi.MEO),
        ThienCan.QUY: (DiaChi.TY, DiaChi.SUU),
    }
    return _TRIET_POSITIONS[context.prior.get_thien_can()]


def tuan_positions_fn(context: LaSoContext) -> tuple[DiaChi, DiaChi]:
    """Two Tuần positions from (year Địa Chi index - year Thiên Can index) mod 12."""
    _TUAN_POSITIONS: dict[DiaChi, tuple[DiaChi, DiaChi]] = {
        DiaChi.TY: (DiaChi.TUAT, DiaChi.HOI),
        DiaChi.DAN: (DiaChi.TY, DiaChi.SUU),
        DiaChi.THIN: (DiaChi.DAN, DiaChi.MEO),
        DiaChi.NGO: (DiaChi.THIN, DiaChi.TI),
        DiaChi.THAN: (DiaChi.NGO, DiaChi.MUI),
        DiaChi.TUAT: (DiaChi.THAN, DiaChi.DAU),
    }
    dia_chi = context.prior.get_dia_chi()
    thien_can_index = context.prior.get_thien_can().index
    return _TUAN_POSITIONS[dia_chi - thien_can_index]


# Each Cung carries a Thiên Can derived from the year's Thiên Can per the
# Ngũ Hổ Độn rule (see "Phối hợp với mười can"):
#
#   - The Thiên Can at Dần is fixed by the year's Thiên Can.
#   - From Dần, the Thiên Can advances one step clockwise per Địa Chi,
#   giving every Cung its Thiên Can.
DAN_THIEN_CAN_BY_YEAR: dict[ThienCan, ThienCan] = {
    ThienCan.GIAP: ThienCan.BINH,
    ThienCan.KY: ThienCan.BINH,
    ThienCan.AT: ThienCan.MAU,
    ThienCan.CANH: ThienCan.MAU,
    ThienCan.BINH: ThienCan.CANH,
    ThienCan.TAN: ThienCan.CANH,
    ThienCan.DINH: ThienCan.NHAM,
    ThienCan.NHAM: ThienCan.NHAM,
    ThienCan.MAU: ThienCan.GIAP,
    ThienCan.QUY: ThienCan.GIAP,
}

def cung_thien_can_for(year_thien_can: ThienCan, position: DiaChi) -> ThienCan:
    """Resolve the Thiên Can of the Cung at ``position`` per Ngũ Hổ Độn."""
    dan_thien_can = DAN_THIEN_CAN_BY_YEAR[year_thien_can]
    return dan_thien_can + (position - DiaChi.DAN)


def position_by_thien_can(
    mapping: ThienCanPositionMap,
) -> AbsolutePositionResolver:
    """Build an absolute position resolver from a Thiên Can map."""

    return lambda context: mapping[context.prior.get_thien_can()]


def position_by_dia_chi_groups(
    groups: Mapping[DiaChiGroup, DiaChi],
) -> AbsolutePositionResolver:
    """Build an absolute resolver from grouped birth DiaChi declarations."""

    resolved_positions = {
        dia_chi: position
        for list_dia_chi, position in groups.items()
        for dia_chi in list_dia_chi
    }

    expected_size = sum(len(birth_dia_chis) for birth_dia_chis in groups)
    if len(resolved_positions) != expected_size:
        raise ValueError("Birth DiaChi groups must not overlap.")

    return lambda context: resolved_positions[context.prior.get_dia_chi()]


# ---------------------------------------------------------------------------
# Reusable transform builders
# ---------------------------------------------------------------------------


def move_by_dia_chi(
    direction: CircleDirection, step_multiplier: int = 1
) -> PositionTransform:
    return move_with(
        lambda context: context.prior.get_dia_chi().index,
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
    """Move from a reference position using a fixed circular direction."""

    def transform(reference_position: DiaChi, context: LaSoContext) -> DiaChi:
        steps = step_selector(context) * step_multiplier
        return reference_position + direction * steps

    return transform


def move_by_van_direction(
    step_selector: ContextStepSelector, *, step_multiplier: int = 1
) -> PositionTransform:
    """Move from a reference position using van direction and context-derived steps."""

    def transform(reference_position: DiaChi, context: LaSoContext) -> DiaChi:
        steps = step_selector(context) * step_multiplier
        return reference_position + context.van_direction() * steps

    return transform


def move_by_attr(
    attribute_name: str,
    *,
    direction: CircleDirection,
    step_multiplier: int = 1,
) -> PositionTransform:
    """Build a fixed-direction transform from a prior attribute."""
    return move_with(
        lambda context: _get_prior_attr_steps(context, attribute_name),
        direction=direction,
        step_multiplier=step_multiplier,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _constant_step(offset: int) -> ContextStepSelector:
    return lambda _: offset


def _offset_transform(offset: int) -> Callable[[DiaChi], DiaChi]:
    """Adapt a fixed offset into the simple one-argument transform shape."""
    return lambda position: position + offset


def _same_position(position: DiaChi) -> DiaChi:
    return position


def _get_prior_attr_steps(context: LaSoContext, attribute_name: str) -> int:
    """Read an integer-like step value from `LaSoContext.prior`."""
    value = getattr(context.prior, attribute_name)
    if isinstance(value, int):
        return value
    if isinstance(value, IndexedEnumMixin):
        return value.index
    raise TypeError(
        f"Prior attribute `{attribute_name}` must be an int or derived from `IndexedEnumMixin`."
    )
