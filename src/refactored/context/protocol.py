from typing import Protocol, runtime_checkable


@runtime_checkable
class PlacementContext(Protocol):
    """Structural marker for any context object accepted by placement primitives.

    Concrete contexts expose whichever of the following attributes they need;
    primitives access them ad hoc. There are no required members.
    """
