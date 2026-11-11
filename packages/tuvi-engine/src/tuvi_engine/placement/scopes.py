"""Component scopes materialized by each non-natal placement layer kind."""

from src.refactored.placement.component_groups import (
    PERIOD_ROLE_IDS,
    SAO_LUU_IDS,
    TU_HOA_IDS,
)
from src.refactored.placement.registry import ComponentId


TIEU_HAN_SCOPE: frozenset[ComponentId] = SAO_LUU_IDS | TU_HOA_IDS
DAI_HAN_SCOPE: frozenset[ComponentId] = PERIOD_ROLE_IDS | TU_HOA_IDS
LUU_NIEN_DAI_HAN_SCOPE: frozenset[ComponentId] = PERIOD_ROLE_IDS
TU_HOA_PHAI_SCOPE: frozenset[ComponentId] = TU_HOA_IDS
