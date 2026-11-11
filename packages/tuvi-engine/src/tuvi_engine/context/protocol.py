from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class PlacementContext(Protocol):
    """Context accepted by placement primitives and rules.

    This protocol is intentionally structural and broad. Concrete contexts
    expose whichever attributes their placement primitives need, such as
    `thien_can`, `dia_chi`, `menh_position`, `cuc`, `van_direction`, or `prior`.
    """
