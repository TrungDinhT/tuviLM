"""Functional Rule-based System for La So Tu Vi Sao Positioning

This module implements a declarative, functional approach to calculating sao positions
on the la so tu vi. Each rule encapsulates the logic for positioning one or more sao,
returning functions that can be applied to specific birth data.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Union
from dataclasses import dataclass
from enum import Enum

# Import types from the existing codebase
from src.tuvi.element.types import TYPE_DIA_CHI, TYPE_THIEN_CAN, LIST_DIA_CHI
from src.tuvi.birth import BirthTime
from src.tuvi.element.sao import Sao, ChinhTinh, PhuTinh


# Type aliases for better readability
PositionCalculator = Callable[[BirthTime], TYPE_DIA_CHI]
SaoPositionResult = Dict[str, TYPE_DIA_CHI]  # sao_name -> position
RuleApplicator = Callable[[BirthTime], SaoPositionResult]


class RuleType(Enum):
    """Types of rules for organizing different calculation strategies"""
    MAP_BASED = "map_based"          # Uses lookup tables (like MAP_LOC_TON_POSITION)
    OFFSET_BASED = "offset_based"    # Calculates positions with offsets from reference points
    CIRCULAR_GROUP = "circular_group" # Handles circular arrangements like VONG_THAI_TUE
    RELATIVE = "relative"            # Positions relative to other sao
    COMPLEX = "complex"              # Complex multi-step calculations


@dataclass
class SaoDefinition:
    """Defines a sao with its properties"""
    name: str
    elemental: str
    is_chinh_tinh: bool = False

    def create_sao(self) -> Sao:
        """Create the appropriate Sao instance"""
        if self.is_chinh_tinh:
            return ChinhTinh(name=self.name, elemental=self.elemental)
        else:
            return PhuTinh(name=self.name, elemental=self.elemental)


class Rule(ABC):
    """Abstract base class for all positioning rules"""

    def __init__(self, rule_type: RuleType, description: str = ""):
        self.rule_type = rule_type
        self.description = description

    @abstractmethod
    def get_applicator(self) -> RuleApplicator:
        """Return a function that calculates sao positions given birth time"""
        pass

    @abstractmethod
    def get_sao_names(self) -> List[str]:
        """Return list of sao names this rule handles"""
        pass


class MapBasedRule(Rule):
    """Rule that uses lookup tables to determine positions"""

    def __init__(self, sao_def: SaoDefinition, position_map: Dict[Union[TYPE_THIEN_CAN, TYPE_DIA_CHI], TYPE_DIA_CHI],
                 key_selector: Callable[[BirthTime], Union[TYPE_THIEN_CAN, TYPE_DIA_CHI]]):
        super().__init__(RuleType.MAP_BASED, f"Map-based positioning for {sao_def.name}")
        self.sao_def = sao_def
        self.position_map = position_map
        self.key_selector = key_selector

    def get_applicator(self) -> RuleApplicator:
        def applicator(birth_time: BirthTime) -> SaoPositionResult:
            key = self.key_selector(birth_time)
            position = self.position_map.get(key)
            if position is None:
                raise ValueError(f"No position found for key {key} in {self.sao_def.name} rule")
            return {self.sao_def.name: position}
        return applicator

    def get_sao_names(self) -> List[str]:
        return [self.sao_def.name]


class OffsetBasedRule(Rule):
    """Rule that calculates positions using offsets from reference points"""

    def __init__(self, sao_def: SaoDefinition,
                 reference_selector: Callable[[BirthTime], Union[TYPE_DIA_CHI, int]],
                 offset_calculator: Callable[[BirthTime], int],
                 direction: int = 1):
        super().__init__(RuleType.OFFSET_BASED, f"Offset-based positioning for {sao_def.name}")
        self.sao_def = sao_def
        self.reference_selector = reference_selector
        self.offset_calculator = offset_calculator
        self.direction = direction  # 1 for forward, -1 for backward

    def get_applicator(self) -> RuleApplicator:
        def applicator(birth_time: BirthTime) -> SaoPositionResult:
            reference = self.reference_selector(birth_time)
            offset = self.offset_calculator(birth_time)

            # Convert reference to index if it's a dia_chi string
            if isinstance(reference, str):
                ref_index = LIST_DIA_CHI.index(reference)
            else:
                ref_index = reference

            # Calculate final position
            final_index = (ref_index + self.direction * offset) % 12
            position = LIST_DIA_CHI[final_index]

            return {self.sao_def.name: position}
        return applicator

    def get_sao_names(self) -> List[str]:
        return [self.sao_def.name]


class CircularGroupRule(Rule):
    """Rule for handling circular arrangements of multiple sao (like VONG_THAI_TUE)"""

    def __init__(self, sao_group: List[List[SaoDefinition]],
                 start_position_selector: Callable[[BirthTime], TYPE_DIA_CHI],
                 description: str = ""):
        super().__init__(RuleType.CIRCULAR_GROUP, description)
        self.sao_group = sao_group
        self.start_position_selector = start_position_selector

    def get_applicator(self) -> RuleApplicator:
        def applicator(birth_time: BirthTime) -> SaoPositionResult:
            start_position = self.start_position_selector(birth_time)
            start_index = LIST_DIA_CHI.index(start_position)

            result = {}

            for i, sao_list in enumerate(self.sao_group):
                current_position_index = (start_index + i) % 12
                current_position = LIST_DIA_CHI[current_position_index]

                for sao_def in sao_list:
                    result[sao_def.name] = current_position

            return result
        return applicator

    def get_sao_names(self) -> List[str]:
        names = []
        for sao_list in self.sao_group:
            for sao_def in sao_list:
                names.append(sao_def.name)
        return names


class RuleRegistry:
    """Registry for managing and applying rules"""

    def __init__(self):
        self.rules: List[Rule] = []
        self._sao_to_rule_map: Dict[str, Rule] = {}

    def register_rule(self, rule: Rule):
        """Register a new rule"""
        self.rules.append(rule)
        for sao_name in rule.get_sao_names():
            if sao_name in self._sao_to_rule_map:
                raise ValueError(f"Sao {sao_name} is already handled by another rule")
            self._sao_to_rule_map[sao_name] = rule

    def get_rule_for_sao(self, sao_name: str) -> Rule:
        """Get the rule that handles a specific sao"""
        return self._sao_to_rule_map.get(sao_name)

    def apply_all_rules(self, birth_time: BirthTime) -> Dict[str, TYPE_DIA_CHI]:
        """Apply all registered rules to get all sao positions"""
        all_positions = {}

        for rule in self.rules:
            applicator = rule.get_applicator()
            positions = applicator(birth_time)
            all_positions.update(positions)

        return all_positions

    def apply_rules_for_sao_list(self, birth_time: BirthTime, sao_names: List[str]) -> Dict[str, TYPE_DIA_CHI]:
        """Apply rules only for specific sao"""
        positions = {}
        processed_rules = set()

        for sao_name in sao_names:
            rule = self.get_rule_for_sao(sao_name)
            if rule and rule not in processed_rules:
                applicator = rule.get_applicator()
                rule_positions = applicator(birth_time)
                # Only include requested sao positions
                for name, pos in rule_positions.items():
                    if name in sao_names:
                        positions[name] = pos
                processed_rules.add(rule)

        return positions


# Example rule definitions using existing constants
def create_sample_rules() -> RuleRegistry:
    """Create sample rules to demonstrate the system"""
    from src.tuvi.constant import MAP_LOC_TON_POSITION, VONG_THAI_TUE

    registry = RuleRegistry()

    # Example 1: Map-based rule for Lộc Tồn
    loc_ton_rule = MapBasedRule(
        sao_def=SaoDefinition("Lộc Tồn", "Thổ"),
        position_map=MAP_LOC_TON_POSITION,
        key_selector=lambda bt: bt.thien_can
    )
    registry.register_rule(loc_ton_rule)

    # Example 2: Offset-based rule for a simple calculation
    sample_offset_rule = OffsetBasedRule(
        sao_def=SaoDefinition("Sample Sao", "Kim"),
        reference_selector=lambda bt: "Dần",  # Start from Dần
        offset_calculator=lambda bt: bt.month - 1,  # Offset by month
        direction=1
    )
    registry.register_rule(sample_offset_rule)

    # Example 3: Circular group rule for Thái Tuế group (simplified)
    # Convert VONG_THAI_TUE to SaoDefinition format
    thai_tue_sao_group = []
    for sao_list in VONG_THAI_TUE:
        converted_sao_list = []
        for sao in sao_list:
            converted_sao_list.append(SaoDefinition(sao.name, sao.elemental))
        thai_tue_sao_group.append(converted_sao_list)

    thai_tue_rule = CircularGroupRule(
        sao_group=thai_tue_sao_group,
        start_position_selector=lambda bt: bt.dia_chi,  # Start from birth year's dia_chi
        description="Thái Tuế circular group positioning"
    )
    registry.register_rule(thai_tue_rule)

    return registry


# Factory functions for common rule patterns
def create_map_rule(sao_name: str, elemental: str, position_map: Dict, key_selector: Callable) -> MapBasedRule:
    """Factory function for creating map-based rules"""
    return MapBasedRule(
        SaoDefinition(sao_name, elemental),
        position_map,
        key_selector
    )

def create_offset_rule(sao_name: str, elemental: str, reference_selector: Callable,
                      offset_calculator: Callable, direction: int = 1) -> OffsetBasedRule:
    """Factory function for creating offset-based rules"""
    return OffsetBasedRule(
        SaoDefinition(sao_name, elemental),
        reference_selector,
        offset_calculator,
        direction
    )


if __name__ == "__main__":
    # Demo usage
    import datetime as dt

    # Create sample registry
    registry = create_sample_rules()

    # Create sample birth time
    sample_time = dt.datetime(1998, 4, 4, 8)
    birth_time = BirthTime.from_solar_day(sample_time, "M")

    # Apply all rules
    all_positions = registry.apply_all_rules(birth_time)
    print("All sao positions:", all_positions)

    # Apply specific rules
    specific_positions = registry.apply_rules_for_sao_list(birth_time, ["Lộc Tồn", "Thái Tuế"])
    print("Specific sao positions:", specific_positions)
