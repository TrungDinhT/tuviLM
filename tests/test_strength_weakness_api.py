from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import FastAPI

from api import main as routes
from src.agent.deps import TuviAgentDeps
from src.agent.workflow.strength_weakness import CapabilityProfile, StrengthFinding


@pytest.mark.parametrize('birth', [
    {'calendar': 'solar', 'year': 1990, 'month': 5, 'day': 15, 'hour': 10, 'gender': 'M'},
    {'calendar': 'solar', 'year': 1995, 'month': 8, 'day': 12, 'hour': 14, 'gender': 'F'},
])
def test_analysis_uses_explicit_birth_chart_and_serializes_profile(monkeypatch, birth):
    app = FastAPI()
    app.add_api_route('/analysis', routes.analyze_strength_weakness, methods=['POST'], response_model=CapabilityProfile)
    workflow_agent = object()
    base_deps = TuviAgentDeps(strength_weakness_agent=workflow_agent)
    app.state.api_state = SimpleNamespace(agent_deps=base_deps)
    output = CapabilityProfile(
        tong_quan='Tổng quan',
        diem_manh=[StrengthFinding(nang_luc_id='quyet_doan', mo_ta='Mô tả', giai_thich='Giải thích')],
    )
    run = AsyncMock(return_value=output)
    monkeypatch.setattr(routes, 'run_strength_weakness_agent', run)

    async def request():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            return await client.post('/analysis', json=birth)

    response = asyncio.run(request())
    assert response.status_code == 200
    assert response.json() == output.model_dump(mode='json')
    assert response.json()['diem_manh'][0]['nang_luc']
    args = run.call_args.kwargs
    expected = routes._la_so_from_build_request(routes.BuildLasoRequest.model_validate(birth))
    assert args['agent'] is workflow_agent
    assert args['deps'] is not base_deps
    assert args['deps'].la_so.prior == expected.prior
    assert base_deps.la_so is None


def test_analysis_rejects_invalid_date_before_running_model(monkeypatch):
    app = FastAPI()
    app.add_api_route('/analysis', routes.analyze_strength_weakness, methods=['POST'])
    run = AsyncMock()
    monkeypatch.setattr(routes, 'run_strength_weakness_agent', run)

    async def request():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            return await client.post('/analysis', json={
                'calendar': 'solar', 'year': 1990, 'month': 2, 'day': 31, 'hour': 10, 'gender': 'M',
            })

    assert asyncio.run(request()).status_code == 422
    run.assert_not_called()
