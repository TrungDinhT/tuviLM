"""Shared result types for cach_cuc matching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.agent.cach_cuc.models import Role


@dataclass(frozen=True)
class MatchOutcome:
    """Boolean condition result plus roles inferred for filtering."""

    matched: bool
    related_roles: tuple[Role, ...] = ()


def merge_related_roles(*role_groups: Iterable[Role]) -> tuple[Role, ...]:
    """Merge role groups while preserving first-seen YAML order."""
    roles: list[Role] = []
    for role_group in role_groups:
        for role in role_group:
            if role not in roles:
                roles.append(role)
    return tuple(roles)
