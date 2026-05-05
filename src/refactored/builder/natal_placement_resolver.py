from __future__ import annotations

from dataclasses import InitVar, dataclass
from functools import cached_property
from types import MappingProxyType
from typing import Mapping

from src.refactored.builder.cung_builder import CungBuilder
from src.refactored.component.cung import Cung, Role
from src.refactored.component.elementary import DiaChi
from src.refactored.context.natal import NatalContext
from src.refactored.placement.bundle import get_default_placement_rule_compiler
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.primitives import cung_thien_can_for
from src.refactored.placement.registry import ComponentId


@dataclass
class NatalPlacement:
    """Canonical flat component positions; role/sao split and ``cungs`` are derived."""

    component_positions: InitVar[Mapping[ComponentId, DiaChi]]
    natal_ctx: InitVar[NatalContext]

    def __post_init__(
        self, component_positions: Mapping[ComponentId, DiaChi], natal_ctx: NatalContext
    ) -> None:
        object.__setattr__(
            self,
            "component_positions",
            MappingProxyType(dict(component_positions)),
        )
        object.__setattr__(self, "_natal_ctx", natal_ctx)

    @cached_property
    def role_positions(self) -> dict[Role, DiaChi]:
        return {
            Role(id): pos for id, pos in self.component_positions.items() if id in Role
        }

    @cached_property
    def sao_positions(self) -> dict[ComponentId, DiaChi]:
        return {
            id: pos for id, pos in self.component_positions.items() if id not in Role
        }

    @cached_property
    def cungs(self) -> dict[DiaChi, Cung]:
        cung_builders: dict[DiaChi, CungBuilder] = {
            dia_chi: CungBuilder(
                dia_chi=dia_chi,
                thien_can=cung_thien_can_for(self._natal_ctx.thien_can, dia_chi),
            )
            for dia_chi in DiaChi
        }

        for id, pos in self.component_positions.items():
            if id in Role:
                if id == Role.CUNG_THAN:
                    cung_builders[pos].set_is_cung_than(True)
                else:
                    cung_builders[pos].set_role(Role(id))
            else:
                cung_builders[pos].add_sao(id)

        return {dia_chi: builder.build() for dia_chi, builder in cung_builders.items()}

    def cung_at(self, dia_chi: DiaChi) -> Cung:
        return self.cungs[dia_chi]


def resolve_natal_placement(
    context: NatalContext,
    *,
    compiler: PlacementRuleCompiler | None = None,
) -> NatalPlacement:
    compiler = compiler or get_default_placement_rule_compiler()
    specs = compiler.compile(context)
    component_positions = PlacementEngine(specs).resolve_all()
    return NatalPlacement(component_positions=component_positions, natal_ctx=context)
