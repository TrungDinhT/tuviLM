"""Default wiring of declarative rule lists into one connected placement graph."""

from __future__ import annotations

from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.rules.loader import register_declaration_group


def get_default_placement_rule_compiler() -> PlacementRuleCompiler:
    """Full chart rule graph: role palaces, chính / phụ tinh, tứ hóa — one registration graph."""
    compiler = PlacementRuleCompiler()
    register_declaration_group(compiler, "cung_roles")
    register_declaration_group(compiler, "chinh_tinh")
    register_declaration_group(compiler, "phu_tinh")
    register_declaration_group(compiler, "tuan_triet")
    register_declaration_group(compiler, "tu_hoa")
    return compiler
