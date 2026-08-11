"""Reusable contracts for tool-backed agent workflows."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

WorkflowTool = Callable[..., Any]
InputBuilderTool = Callable[..., BaseModel]


@dataclass(frozen=True, slots=True)
class WorkflowInputDefinition:
    """One input projection and the single tool that builds it."""

    name: str
    model: type[BaseModel]
    tool: InputBuilderTool
    instructions: tuple[str, ...] = ()
    supporting_tools: tuple[WorkflowTool, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkflowOutputInstruction:
    """Response instructions plus the output type enforced by the agent."""

    name: str
    instruction: str
    output_type: Any = str
