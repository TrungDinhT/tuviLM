from __future__ import annotations

from collections.abc import Awaitable, Callable

from src.agent.deps import TuviAgentDeps
from src.agent.main import build_tuvi_agent
from src.evals.schema import AgentResult, TuviEvalInput
from src.tuvi.builder import Builder


TuviEvalTask = Callable[[TuviEvalInput], Awaitable[AgentResult]]


def build_tuvi_eval_task(model: str, book_root: str) -> TuviEvalTask:
    async def run_case(inputs: TuviEvalInput) -> AgentResult:
        agent = build_tuvi_agent(model=model)
        tinh_ban = Builder().build(inputs.tuvi_time)
        deps = TuviAgentDeps(
            agent=agent,
            tinh_ban=tinh_ban,
            book_root=book_root
        )

        result = await agent.run(inputs.query, deps=deps)
        return AgentResult.from_run_result(result)

    run_case.__name__ = "tuvi_agent"
    return run_case
