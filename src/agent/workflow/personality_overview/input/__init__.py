"""Evidence definition for the standalone personality overview workflow."""

from src.agent.workflow.contracts import WorkflowInputDefinition
from .tanbien import (
    PersonalityOverviewEvidence,
    get_personality_overview_evidence,
    get_personality_overview_tat_ach_evidence,
)

PERSONALITY_OVERVIEW_INPUT = WorkflowInputDefinition(
    name="tanbien",
    model=PersonalityOverviewEvidence,
    tool=get_personality_overview_evidence,
    supporting_tools=(
        get_personality_overview_tat_ach_evidence,
    ),
)
