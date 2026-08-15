from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.agent.book_index import SectionContent, SectionSearchHit


class SaoInfoSection(BaseModel):
    """Một mục sách dùng chung cho một hoặc nhiều sao được yêu cầu."""

    model_config = ConfigDict(frozen=True)

    star_names: list[str]
    section: SectionContent


class SaoInfoSearchResult(BaseModel):
    """Thông tin sách cho một nhóm chính tinh và phụ tinh."""

    model_config = ConfigDict(frozen=True)

    requested_star_names: list[str]
    sections: list[SaoInfoSection]
    not_found: list[str] = Field(default_factory=list)
    suggestions: dict[str, list[SectionSearchHit]] = Field(default_factory=dict)
