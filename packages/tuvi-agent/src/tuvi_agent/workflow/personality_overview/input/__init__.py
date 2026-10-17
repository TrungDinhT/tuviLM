"""Evidence definition for the standalone personality overview workflow."""

from tuvi_agent.workflow.contracts import WorkflowInputDefinition
from .evidence import (
    PersonalityOverviewEvidence,
    get_personality_overview_evidence,
)
from .trung_chau import TRUNG_CHAU_INSTRUCTIONS

PERSONALITY_OVERVIEW_INPUT = WorkflowInputDefinition(
    name="evidence",
    model=PersonalityOverviewEvidence,
    tool=get_personality_overview_evidence,
    instructions=(TRUNG_CHAU_INSTRUCTIONS,),
)
