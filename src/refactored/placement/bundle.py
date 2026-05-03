"""Default wiring of declarative rule lists into one connected placement graph."""

from __future__ import annotations

from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.rules import (
    CHINH_TINH_RULES,
    PHU_TINH_RULES,
    ROLE_RULES,
    TU_HOA_RULES,
)


def get_default_placement_rule_compiler() -> PlacementRuleCompiler:
    """Full chart rule graph: role palaces, chính / phụ tinh, tứ hóa — one registration graph."""
    compiler = PlacementRuleCompiler()
    compiler.register_rules(ROLE_RULES)
    compiler.register_rules(CHINH_TINH_RULES)
    compiler.register_rules(PHU_TINH_RULES)
    compiler.register_rules(TU_HOA_RULES)
    return compiler
