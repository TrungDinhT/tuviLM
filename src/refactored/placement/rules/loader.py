from __future__ import annotations

from functools import cache
from pathlib import Path

import yaml
from pydantic import TypeAdapter

from src.refactored.model.elementary import ThienCan
from src.refactored.placement.registry import ComponentId, PlacementRegistry
from src.refactored.placement.rules.registration import (
    DeclarationRule,
    as_rule_adapters,
    build_tu_hoa_target_mapping,
    register_declarations,
)
from src.refactored.placement.rules.declarations.validation import (
    validate_declaration_group,
)
from src.refactored.placement.rules.declarations.models import (
    PlacementRuleDeclaration,
    PlacementRuleGroup,
)

RuleGroupName = str

_RULE_GROUP_ADAPTER = TypeAdapter(PlacementRuleGroup)


def load_rule_group(
    group_name: RuleGroupName,
    *,
    data_dir: Path | None = None,
) -> tuple[DeclarationRule, ...]:
    return as_rule_adapters(load_declaration_group(group_name, data_dir=data_dir))


def register_declaration_group(
    registry: PlacementRegistry,
    group_name: RuleGroupName,
    *,
    data_dir: Path | None = None,
) -> None:
    register_declarations(
        registry,
        load_declaration_group(group_name, data_dir=data_dir),
    )


@cache
def load_declaration_group(
    group_name: RuleGroupName,
    *,
    data_dir: Path | None = None,
) -> tuple[PlacementRuleDeclaration, ...]:
    rule_data_dir = data_dir or Path(__file__).resolve().parent / "data"
    path = rule_data_dir / f"{group_name}.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    group = _RULE_GROUP_ADAPTER.validate_python(raw)
    validate_declaration_group(group.rules, group_name=group_name)
    return group.rules


def load_tu_hoa_target_mapping(
    *,
    data_dir: Path | None = None,
) -> dict[ThienCan, dict[str, ComponentId]]:
    return build_tu_hoa_target_mapping(
        load_declaration_group("tu_hoa", data_dir=data_dir)
    )
