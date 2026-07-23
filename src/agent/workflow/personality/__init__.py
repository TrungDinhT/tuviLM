"""Configurable personality workflow."""

from .agent import (
    DEFAULT_PERSONALITY_CONFIG,
    PERSONALITY_AGENT_BASE_INSTRUCTION,
    PERSONALITY_AGENT_INSTRUCTION,
    PERSONALITY_EVIDENCE_REGISTRY,
    PERSONALITY_OUTPUT_REGISTRY,
    PersonalityAgentConfig,
    PersonalityEvidenceSchema,
    PersonalityOutputSchema,
    build_personality_agent,
    build_personality_agent_instruction,
    get_personality_evidence_schema,
    get_personality_output_schema,
    register_personality_evidence_schema,
    register_personality_output_schema,
    resolve_personality_config,
    run_personality_workflow,
    run_tinh_cach_workflow,
)
from .input.tanbien import (
    PersonalityEvidence,
    collect_personality_evidence,
    get_personality_evidence,
)

__all__ = [
    "DEFAULT_PERSONALITY_CONFIG",
    "PERSONALITY_AGENT_BASE_INSTRUCTION",
    "PERSONALITY_AGENT_INSTRUCTION",
    "PERSONALITY_EVIDENCE_REGISTRY",
    "PERSONALITY_OUTPUT_REGISTRY",
    "PersonalityAgentConfig",
    "PersonalityEvidence",
    "PersonalityEvidenceSchema",
    "PersonalityOutputSchema",
    "build_personality_agent",
    "build_personality_agent_instruction",
    "collect_personality_evidence",
    "get_personality_evidence",
    "get_personality_evidence_schema",
    "get_personality_output_schema",
    "register_personality_evidence_schema",
    "register_personality_output_schema",
    "resolve_personality_config",
    "run_personality_workflow",
    "run_tinh_cach_workflow",
]
