from __future__ import annotations

from dataclasses import dataclass

from src.refactored.component.cung import Role
from src.refactored.component.elementary import DiaChi
from src.refactored.context.protocol import PlacementContext
from src.refactored.placement.bundle import get_default_placement_rule_compiler
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.registry import ComponentId


def _partition_flat_by_role(
    flat: dict[ComponentId, DiaChi],
) -> tuple[dict[Role, DiaChi], dict[ComponentId, DiaChi]]:
    roles: dict[Role, DiaChi] = {}
    saos: dict[ComponentId, DiaChi] = {}
    for cid, pos in flat.items():
        try:
            roles[Role(cid)] = pos
        except ValueError:
            saos[cid] = pos
    return roles, saos


@dataclass(frozen=True, slots=True)
class NatalPlacement:
    """Partitioned natal resolve: palace roles vs star / component ids."""

    role_positions: dict[Role, DiaChi]
    sao_positions: dict[ComponentId, DiaChi]


def resolve_natal_placement(
    context: PlacementContext,
    *,
    compiler: PlacementRuleCompiler | None = None,
) -> NatalPlacement:
    compiler = compiler or get_default_placement_rule_compiler()
    specs = compiler.compile(context)
    flat = PlacementEngine(specs).resolve_all()
    roles, saos = _partition_flat_by_role(flat)
    return NatalPlacement(role_positions=roles, sao_positions=saos)
