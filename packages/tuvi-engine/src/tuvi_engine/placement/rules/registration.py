from __future__ import annotations

from typing import Callable, Sequence, TypeAlias

from src.refactored.context.protocol import PlacementContext
from src.refactored.model.elementary import DiaChi, ThienCan
from src.refactored.placement.component_groups import TU_HOA_IDS
from src.refactored.placement.registry import (
    AbsolutePositionResolver,
    AbsolutePositionSpec,
    ComponentId,
    PlacementRegistry,
    RelativePositionSpec,
)
from src.refactored.placement.rules.declarations import resolvers
from src.refactored.placement.rules.declarations.models import (
    AbsoluteByDiaChiGroupsDeclaration,
    AbsoluteByThienCanDeclaration,
    AbsoluteFormulaDeclaration,
    AnchorDeclaration,
    CircleDeclaration,
    DefinitiveDeclaration,
    DiaChiGroupDeclaration,
    FromAnchorDeclaration,
    OffsetGroupDeclaration,
    PlacementRuleDeclaration,
    RelativeDeclaration,
    SamePositionDeclaration,
    TuanTrietPairDeclaration,
    TuHoaDeclaration,
)
from src.refactored.placement.rules.positions import relative

DeclarationRegistrar: TypeAlias = Callable[
    [PlacementRegistry, PlacementRuleDeclaration], None
]
AnchorResolver: TypeAlias = Callable[
    [AnchorDeclaration], DiaChi | AbsolutePositionResolver
]


class DeclarationRule:
    """Adapter so loaded declarations can satisfy the Rule protocol in tests."""

    def __init__(self, declaration: PlacementRuleDeclaration) -> None:
        self.declaration = declaration

    def __getattr__(self, name: str):
        return getattr(self.declaration, name)

    def register_components(self, registry: PlacementRegistry) -> None:
        register_declaration(registry, self.declaration)


def as_rule_adapters(
    declarations: Sequence[PlacementRuleDeclaration],
) -> tuple[DeclarationRule, ...]:
    return tuple(DeclarationRule(declaration) for declaration in declarations)


def register_declarations(
    registry: PlacementRegistry,
    declarations: Sequence[PlacementRuleDeclaration],
) -> None:
    for declaration in declarations:
        register_declaration(registry, declaration)


def register_declaration(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    try:
        registrar = _DECLARATION_REGISTRARS[type(declaration)]
    except KeyError as exc:
        raise TypeError(f"Unsupported placement declaration: {declaration!r}") from exc
    registrar(registry, declaration)


def build_tu_hoa_target_mapping(
    declarations: Sequence[PlacementRuleDeclaration],
) -> dict[ThienCan, dict[str, ComponentId]]:
    tu_hoa_declarations = [
        declaration
        for declaration in declarations
        if isinstance(declaration, TuHoaDeclaration)
    ]
    if len(tu_hoa_declarations) != 1:
        raise ValueError(
            "Expected exactly one Tứ Hóa declaration, "
            f"found {len(tu_hoa_declarations)}."
        )
    return _parse_tu_hoa_mapping(tu_hoa_declarations[0].mapping)


def _register_absolute_formula(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, AbsoluteFormulaDeclaration):
        raise TypeError(f"Invalid absolute formula declaration: {declaration!r}")
    registry.register_component_lazy(
        declaration.component_id,
        AbsolutePositionSpec(
            resolvers.resolve_absolute_formula(declaration.formula)
        ),
    )


def _register_absolute_by_thien_can(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, AbsoluteByThienCanDeclaration):
        raise TypeError(f"Invalid Thiên Can declaration: {declaration!r}")
    mapping = {
        ThienCan(thien_can): DiaChi(position)
        for thien_can, position in declaration.mapping.items()
    }
    registry.register_component_lazy(
        declaration.component_id,
        AbsolutePositionSpec(lambda context: mapping[context.thien_can]),
    )


def _register_absolute_by_dia_chi_groups(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, AbsoluteByDiaChiGroupsDeclaration):
        raise TypeError(f"Invalid Địa Chi group declaration: {declaration!r}")
    registry.register_component_lazy(
        declaration.component_id,
        AbsolutePositionSpec(_position_by_dia_chi_groups(declaration.groups)),
    )


def _register_definitive(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, DefinitiveDeclaration):
        raise TypeError(f"Invalid definitive declaration: {declaration!r}")
    registry.register_component(declaration.component_id, DiaChi(declaration.position))


def _register_relative(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, RelativeDeclaration):
        raise TypeError(f"Invalid relative declaration: {declaration!r}")
    registry.register_component_lazy(
        declaration.component_id,
        RelativePositionSpec(
            declaration.reference_id,
            resolvers.build_transform(
                declaration.transform,
                direction=declaration.direction,
                axis=declaration.axis,
                step_multiplier=declaration.step_multiplier,
                date_offset=declaration.date_offset,
            ),
        ),
    )


def _register_from_anchor(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, FromAnchorDeclaration):
        raise TypeError(f"Invalid anchor declaration: {declaration!r}")
    anchor = _resolve_anchor(declaration.anchor)
    transform = resolvers.build_transform(
        declaration.transform,
        direction=declaration.direction,
        step_multiplier=declaration.step_multiplier,
        step=declaration.step,
    )

    def position_fn(context: PlacementContext) -> DiaChi:
        anchor_position = anchor(context) if callable(anchor) else anchor
        return transform(anchor_position, context)

    registry.register_component_lazy(
        declaration.component_id,
        AbsolutePositionSpec(position_fn),
    )


def _register_circle(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, CircleDeclaration):
        raise TypeError(f"Invalid circle declaration: {declaration!r}")
    anchor = _resolve_anchor(declaration.anchor)
    if not callable(anchor):
        anchor_fn = lambda _context, position=anchor: position
    else:
        anchor_fn = anchor

    registry.register_component_lazy(
        declaration.principal_id,
        AbsolutePositionSpec(anchor_fn),
    )

    for offset, member in enumerate(declaration.others, start=1):
        transform = resolvers.build_circle_offset_transform(
            declaration.direction, offset
        )
        if isinstance(member, str):
            registry.register_component_lazy(
                member,
                RelativePositionSpec(declaration.principal_id, transform),
            )
            continue

        registry.register_component_lazy(
            member.component_id,
            RelativePositionSpec(member.reference_id, relative.same_position),
        )
        registry.register_component_lazy(
            member.reference_id,
            RelativePositionSpec(declaration.principal_id, transform),
        )


def _register_offset_group(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, OffsetGroupDeclaration):
        raise TypeError(f"Invalid offset group declaration: {declaration!r}")
    anchor = _resolve_anchor(declaration.anchor)
    if not callable(anchor):
        anchor_fn = lambda _context, position=anchor: position
    else:
        anchor_fn = anchor

    registry.register_component_lazy(
        declaration.anchor_id,
        AbsolutePositionSpec(anchor_fn),
    )
    for component_id, offset in declaration.offsets.items():
        registry.register_component_lazy(
            component_id,
            RelativePositionSpec(
                declaration.anchor_id,
                relative.offset_transform(offset),
            ),
        )


def _register_same_position(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, SamePositionDeclaration):
        raise TypeError(f"Invalid same-position declaration: {declaration!r}")
    registry.register_component_lazy(
        declaration.component_id,
        RelativePositionSpec(
            declaration.reference_id,
            relative.same_position,
        ),
    )


def _register_tuan_triet_pair(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, TuanTrietPairDeclaration):
        raise TypeError(f"Invalid Tuần/Triệt declaration: {declaration!r}")
    formula = resolvers.resolve_pair_formula(declaration.formula)
    first_id, second_id = declaration.pair_ids
    registry.register_component_lazy(
        first_id,
        AbsolutePositionSpec(lambda context: formula(context)[0]),
    )
    registry.register_component_lazy(
        second_id,
        AbsolutePositionSpec(lambda context: formula(context)[1]),
    )


def _register_tu_hoa(
    registry: PlacementRegistry,
    declaration: PlacementRuleDeclaration,
) -> None:
    if not isinstance(declaration, TuHoaDeclaration):
        raise TypeError(f"Invalid Tứ Hóa declaration: {declaration!r}")
    mapping = _parse_tu_hoa_mapping(declaration.mapping)
    for entity in TU_HOA_IDS:
        registry.register_component_lazy(
            entity,
            RelativePositionSpec(
                lambda context, e=entity: mapping[context.thien_can][e],
                relative.same_position,
            ),
        )


def _resolve_anchor(anchor: AnchorDeclaration) -> DiaChi | AbsolutePositionResolver:
    try:
        resolver = _ANCHOR_RESOLVERS[anchor.kind]
    except KeyError as exc:
        raise ValueError(f"Unknown anchor kind: {anchor.kind}") from exc
    return resolver(anchor)


def _resolve_fixed_anchor(anchor: AnchorDeclaration) -> DiaChi:
    return DiaChi(anchor.value)


def _resolve_formula_anchor(anchor: AnchorDeclaration) -> AbsolutePositionResolver:
    return resolvers.resolve_absolute_formula(anchor.name)


def _resolve_dia_chi_groups_anchor(
    anchor: AnchorDeclaration,
) -> AbsolutePositionResolver:
    return _position_by_dia_chi_groups(anchor.groups)


def _position_by_dia_chi_groups(
    groups: Sequence[DiaChiGroupDeclaration],
) -> AbsolutePositionResolver:
    return relative.position_by_dia_chi_groups(
        {
            tuple(DiaChi(dia_chi) for dia_chi in group.dia_chi): DiaChi(group.position)
            for group in groups
        }
    )

def _parse_tu_hoa_mapping(
    raw_mapping: dict[str, dict[str, str]],
) -> dict[ThienCan, dict[str, ComponentId]]:
    mapping = {
        ThienCan(thien_can): dict(entities)
        for thien_can, entities in raw_mapping.items()
    }
    for thien_can in ThienCan:
        if thien_can not in mapping:
            raise ValueError(f"Missing Tứ Hóa mapping for {thien_can!r}")
        entities = mapping[thien_can]
        for entity in TU_HOA_IDS:
            if entity not in entities:
                raise ValueError(
                    f"Missing `{entity}` for {thien_can!r} in Tứ Hóa mapping."
                )
            target = entities[entity]
            if target in TU_HOA_IDS:
                raise ValueError(
                    "Tứ Hóa target cannot be another Tứ Hóa entity: "
                    f"{target!r} for {thien_can!r} `{entity}`"
                )
    return mapping


_DECLARATION_REGISTRARS: dict[type[PlacementRuleDeclaration], DeclarationRegistrar] = {
    AbsoluteFormulaDeclaration: _register_absolute_formula,
    AbsoluteByThienCanDeclaration: _register_absolute_by_thien_can,
    AbsoluteByDiaChiGroupsDeclaration: _register_absolute_by_dia_chi_groups,
    DefinitiveDeclaration: _register_definitive,
    RelativeDeclaration: _register_relative,
    FromAnchorDeclaration: _register_from_anchor,
    CircleDeclaration: _register_circle,
    OffsetGroupDeclaration: _register_offset_group,
    SamePositionDeclaration: _register_same_position,
    TuanTrietPairDeclaration: _register_tuan_triet_pair,
    TuHoaDeclaration: _register_tu_hoa,
}

_ANCHOR_RESOLVERS: dict[str, AnchorResolver] = {
    "dia_chi": _resolve_fixed_anchor,
    "formula": _resolve_formula_anchor,
    "dia_chi_groups": _resolve_dia_chi_groups_anchor,
}
