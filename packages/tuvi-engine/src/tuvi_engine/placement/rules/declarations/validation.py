from __future__ import annotations

from typing import Sequence

from src.refactored.placement.component_groups import TU_HOA_IDS
from src.refactored.placement.registry import ComponentId
from src.refactored.placement.rules.declarations.models import (
    CircleDeclaration,
    OffsetGroupDeclaration,
    PlacementRuleDeclaration,
    SamePositionMemberDeclaration,
    TuHoaDeclaration,
    TuanTrietPairDeclaration,
)


def validate_declaration_group(
    declarations: Sequence[PlacementRuleDeclaration],
    *,
    group_name: str,
) -> None:
    registered_ids: set[ComponentId] = set()
    for declaration in declarations:
        for component_id in _declared_component_ids(declaration):
            if component_id in registered_ids:
                raise ValueError(
                    f"Duplicate component id in `{group_name}` declarations: {component_id}"
                )
            registered_ids.add(component_id)


def _declared_component_ids(
    declaration: PlacementRuleDeclaration,
) -> tuple[ComponentId, ...]:
    if isinstance(declaration, CircleDeclaration):
        ids = [declaration.principal_id]
        for member in declaration.others:
            if isinstance(member, str):
                ids.append(member)
            elif isinstance(member, SamePositionMemberDeclaration):
                ids.extend([member.component_id, member.reference_id])
        return tuple(ids)
    if isinstance(declaration, OffsetGroupDeclaration):
        return (declaration.anchor_id, *declaration.offsets)
    if isinstance(declaration, TuanTrietPairDeclaration):
        return declaration.pair_ids
    if isinstance(declaration, TuHoaDeclaration):
        return tuple(TU_HOA_IDS)
    component_id = getattr(declaration, "component_id", None)
    return (component_id,) if component_id is not None else ()
