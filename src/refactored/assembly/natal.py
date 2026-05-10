from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.refactored.components.definitions.cung_role import Role
from src.refactored.model.elementary import DiaChi
from src.refactored.context.natal import NatalContext
from src.refactored.model.period_focus import (
    PeriodFocusMaps,
    build_dai_han_focus_map,
    build_tieu_han_focus_map,
)
from src.refactored.model.cung import CungId, derive_cung_thien_can
from src.refactored.placement.bundle import get_default_placement_rule_compiler
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.model.layer import (
    NATAL_LAYER_ID,
    STRUCTURAL_COMPONENT_IDS,
    PlacementLayer,
)
from src.refactored.placement.registry import ComponentId
from src.refactored.model.tinh_ban import TinhBan


_ROLE_BY_ID = {role.value: role for role in Role}


@dataclass(frozen=True)
class NatalPlacement:
    role_positions: dict[Role, DiaChi]
    sao_positions: dict[ComponentId, DiaChi]


def resolve_natal_positions(
    context: NatalContext,
    compiler: PlacementRuleCompiler | None = None,
) -> dict[ComponentId, DiaChi]:
    active_compiler = compiler or get_default_placement_rule_compiler()
    specialized_rules = active_compiler.compile(context)
    return PlacementEngine(specialized_rules).resolve_all()


def resolve_natal_placement(
    context: NatalContext,
    compiler: PlacementRuleCompiler | None = None,
) -> NatalPlacement:
    resolved = resolve_natal_positions(context, compiler)
    role_positions: dict[Role, DiaChi] = {}
    sao_positions: dict[ComponentId, DiaChi] = {}

    for component_id, dia_chi in resolved.items():
        if role := _ROLE_BY_ID.get(component_id):
            role_positions[role] = dia_chi
        else:
            sao_positions[component_id] = dia_chi

    return NatalPlacement(role_positions=role_positions, sao_positions=sao_positions)


def build_cung_ids(
    context: NatalContext,
    resolved_positions: Mapping[ComponentId, DiaChi],
) -> dict[DiaChi, CungId]:
    role_by_position = _role_by_position(resolved_positions)
    cung_than_position = resolved_positions[Role.CUNG_THAN.value]

    return {
        dia_chi: CungId(
            dia_chi=dia_chi,
            thien_can=derive_cung_thien_can(
                year_thien_can=context.thien_can,
                cung_dia_chi=dia_chi,
            ),
            natal_role=role_by_position[dia_chi],
            is_cung_than=dia_chi == cung_than_position,
        )
        for dia_chi in DiaChi
    }


def build_natal_layer(
    resolved_positions: Mapping[ComponentId, DiaChi],
) -> PlacementLayer:
    return PlacementLayer.from_component_positions(
        id=NATAL_LAYER_ID,
        positions={
            component_id: dia_chi
            for component_id, dia_chi in resolved_positions.items()
            if component_id not in STRUCTURAL_COMPONENT_IDS
        },
    )


def build_natal_tinh_ban(
    context: NatalContext,
    compiler: PlacementRuleCompiler | None = None,
) -> TinhBan:
    resolved_positions = resolve_natal_positions(context, compiler)
    cung_ids = build_cung_ids(context, resolved_positions)
    natal_layer = build_natal_layer(resolved_positions)
    period_focus_maps = PeriodFocusMaps(
        tieu_han=build_tieu_han_focus_map(
            natal_year_dia_chi=context.dia_chi,
            van_direction=context.van_direction,
        ),
        dai_han=build_dai_han_focus_map(
            cuc_number=context.cuc.number,
            menh_position=context.menh_position,
            van_direction=context.van_direction,
        ),
    )
    return TinhBan(
        cung_ids=cung_ids,
        natal_layer=natal_layer,
        period_focus_maps=period_focus_maps,
    )


def _role_by_position(
    resolved_positions: Mapping[ComponentId, DiaChi],
) -> dict[DiaChi, Role]:
    role_by_position: dict[DiaChi, Role] = {}
    for role in Role:
        if role is Role.CUNG_THAN:
            continue
        role_by_position[resolved_positions[role.value]] = role
    return role_by_position
