"""Prompt output schemas available to the personality workflow."""

from importlib import import_module


_seven_foundation_questions = import_module(
    ".7_foundation_questions",
    package=__name__,
)

SEVEN_FOUNDATION_QUESTIONS_PROMPT: str = (
    _seven_foundation_questions.OUTPUT_SCHEMA_PROMPT
)

__all__ = ["SEVEN_FOUNDATION_QUESTIONS_PROMPT"]
