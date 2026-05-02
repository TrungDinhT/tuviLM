from __future__ import annotations

from dataclasses import dataclass

from pydantic_evals.evaluators import (
    EvaluationReason,
    Evaluator,
    EvaluatorContext,
    EvaluatorOutput,
)

from src.evals.schema import AgentResult, TuviEvalExpected, TuviEvalInput


@dataclass
class TuviAgentQuality(Evaluator[TuviEvalInput, AgentResult, dict]):
    """Cheap deterministic checks for a Tu Vi agent answer."""

    def evaluate(
        self,
        ctx: EvaluatorContext[TuviEvalInput, AgentResult, dict],
    ) -> EvaluatorOutput:
        expected = _coerce_expected(ctx.expected_output)
        if not isinstance(ctx.output, AgentResult):
            return {
                "structured_result": EvaluationReason(
                    False,
                    reason=f"Task returned {type(ctx.output).__name__}, expected AgentResult.",
                )
            }

        output = ctx.output.output
        output_lower = output.lower()

        checks: dict[str, EvaluationReason] = {
            "structured_result": EvaluationReason(
                isinstance(ctx.output, AgentResult),
                reason="Task returned AgentResult.",
            ),
            "non_empty_output": EvaluationReason(
                len(output.strip()) >= expected.min_output_chars,
                reason=f"Output length is {len(output.strip())} chars.",
            ),
        }

        for required in expected.required_substrings:
            checks[f"contains:{required}"] = EvaluationReason(
                required.lower() in output_lower,
                reason=f"Required substring: {required}",
            )

        for forbidden in expected.forbidden_substrings:
            checks[f"omits:{forbidden}"] = EvaluationReason(
                forbidden.lower() not in output_lower,
                reason=f"Forbidden substring: {forbidden}",
            )

        tools_used = set(ctx.output.tools_used)
        for tool_name in expected.required_tools:
            checks[f"used_tool:{tool_name}"] = EvaluationReason(
                tool_name in tools_used,
                reason=f"Tools used: {', '.join(ctx.output.tools_used) or '(none captured)'}",
            )

        return checks


def _coerce_expected(value: object) -> TuviEvalExpected:
    if isinstance(value, TuviEvalExpected):
        return value
    if isinstance(value, dict):
        return TuviEvalExpected.model_validate(value)
    return TuviEvalExpected()
