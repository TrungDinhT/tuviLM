"""Run with OPENROUTER_SIMULATION_URL from the Postman simulation listening log."""
import asyncio
import os
from pathlib import Path
import time

from openai import AsyncOpenAI
import pytest
from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings
from pydantic_ai.providers.openrouter import OpenRouterProvider

from src.agent.deps import TuviAgentDeps
from src.agent.workflow.strength_weakness.agent import build_strength_weakness_agent
from src.agent.workflow.strength_weakness.stream import stream_strength_weakness
from src.refactored.la_so import LaSo
from tests.fixtures.laso_priors import FIXTURE_PRIOR_A


@pytest.mark.skipif(not os.getenv("OPENROUTER_SIMULATION_URL"), reason="Local Postman simulation is opt-in")
@pytest.mark.parametrize("mode", ["success", "invalid_first"])
def test_real_sdk_streams_and_retries_against_simulation(mode):
    async def run():
        client = AsyncOpenAI(
            api_key="local-simulation-only",
            base_url=os.environ["OPENROUTER_SIMULATION_URL"].rstrip("/") + "/api/v1",
        )
        try:
            agent = build_strength_weakness_agent(
                OpenRouterModel("deepseek/deepseek-v4.1-flash", provider=OpenRouterProvider(openai_client=client)),
                model_settings=OpenRouterModelSettings(
                    openrouter_provider={"order": ["together"], "allow_fallbacks": True, "sort": "latency"},
                    openrouter_reasoning={"effort": "low"},
                    extra_body={"mock_mode": mode},
                ),
            )
            deps = TuviAgentDeps(
                la_so=LaSo.from_prior(FIXTURE_PRIOR_A),
                book_root=Path(__file__).resolve().parents[1] / "data/tuvitanbien_chunking_compact/part_2",
            )
            timed = []
            async for event in stream_strength_weakness(agent=agent, deps=deps, request="Kiểm tra streaming"):
                timed.append((time.monotonic(), event))
            assert timed[-1][1]["type"] == "done"
            assert next(t for t, event in timed if event["type"] == "finding") < timed[-1][0] - 0.1
            assert sum(event["type"] == "reset" for _, event in timed) == (1 if mode == "invalid_first" else 0)
            assert len(timed[-1][1]["profile"]["diem_manh"]) == 3
        finally:
            await client.close()
    asyncio.run(run())
