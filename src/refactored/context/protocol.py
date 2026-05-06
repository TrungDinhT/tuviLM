from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from src.refactored.component.elementary import DiaChi

if TYPE_CHECKING:
    from src.refactored.context.prior import LunarYear
    from src.refactored.placement.layer import LayerId


@runtime_checkable
class PlacementContext(Protocol):
    """Context accepted by placement primitives and rules.

    This protocol is intentionally structural and broad. Concrete contexts
    expose whichever attributes their placement primitives need, such as
    `thien_can`, `dia_chi`, `menh_position`, `cuc`, `van_direction`, or `prior`.
    """


@runtime_checkable
class LayerContext(PlacementContext, Protocol):
    """Context that materializes exactly one placement layer."""

    @property
    def layer_id(self) -> LayerId: ...


@runtime_checkable
class PeriodContext(LayerContext, Protocol):
    """Layer context for prediction-period overlays."""

    @property
    def focus_position(self) -> DiaChi: ...
