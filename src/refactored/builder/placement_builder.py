from src.refactored.component.elementary import DiaChi
from src.refactored.context.protocol import PlacementContext
from src.refactored.placement.compiler import PlacementRuleCompiler
from src.refactored.placement.engine import PlacementEngine
from src.refactored.placement.registry import ComponentId
from src.refactored.placement.rules import get_default_placement_rule_compiler


class PlacementBuilder:
    def __init__(
        self,
        context: PlacementContext,
        compiler: PlacementRuleCompiler | None = None,
    ) -> None:
        self._context = context
        self._compiler = compiler or get_default_placement_rule_compiler()

    def resolve_all(self) -> dict[ComponentId, DiaChi]:
        specialized_rules = self._compiler.compile(self._context)
        placement_engine = PlacementEngine(specialized_rules)
        return placement_engine.resolve_all()
