"""Runtime evaluator package for cach_cuc matching."""

from __future__ import annotations

from src.agent.tool.cach_cuc.evaluator.context import CachCucMatchContext, STAR_ALIASES
from src.agent.tool.cach_cuc.evaluator.core import match_condition
from src.agent.tool.cach_cuc.evaluator.match_types import (
    MatchOutcome,
    merge_related_roles,
)


__all__ = [
    "CachCucMatchContext",
    "MatchOutcome",
    "STAR_ALIASES",
    "match_condition",
    "merge_related_roles",
]
