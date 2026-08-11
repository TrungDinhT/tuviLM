"""Configurable personality workflow."""

from .agent import (
    DEFAULT_PERSONALITY_CONFIG,
    PERSONALITY_AGENT_BASE_INSTRUCTION,
    PERSONALITY_AGENT_INSTRUCTION,
    PERSONALITY_INPUT_REGISTRY,
    PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY,
    PersonalityAgentConfig,
    build_personality_agent,
    build_personality_agent_instruction,
    get_personality_input,
    get_personality_output_instruction,
    register_personality_input,
    register_personality_output_instruction,
    resolve_personality_config,
    run_personality_workflow,
    run_tinh_cach_workflow,
)
from .input.tanbien import (
    PersonalityEvidence,
    get_personality_evidence,
    luan_tinh_cach_skill,
)

__all__ = [
    "DEFAULT_PERSONALITY_CONFIG",
    "PERSONALITY_AGENT_BASE_INSTRUCTION",
    "PERSONALITY_AGENT_INSTRUCTION",
    "PERSONALITY_INPUT_REGISTRY",
    "PERSONALITY_OUTPUT_INSTRUCTION_REGISTRY",
    "PersonalityAgentConfig",
    "PersonalityEvidence",
    "build_personality_agent",
    "build_personality_agent_instruction",
    "get_personality_evidence",
    "get_personality_input",
    "get_personality_output_instruction",
    "luan_tinh_cach_skill",
    "register_personality_input",
    "register_personality_output_instruction",
    "resolve_personality_config",
    "run_personality_workflow",
    "run_tinh_cach_workflow",
]
