from types import SimpleNamespace

import pytest
from pydantic_ai import ModelRetry

from src.agent.book_index import SectionContent, SectionSearchHit
from src.agent.tool.tu_vi_tan_bien import search_star_info


class _Book:
    def __init__(self) -> None:
        self.read_ids: list[str] = []

    def read_section(self, section_id: str) -> SectionContent:
        self.read_ids.append(section_id)
        return SectionContent(
            id=section_id,
            title=f"Mục {section_id}",
            breadcrumb=f"Sao > {section_id}",
            content=f"Ý nghĩa trừu tượng của mục {section_id}",
        )

    def search_sections(self, query: str, top_k: int = 5) -> list[SectionSearchHit]:
        assert top_k == 3
        return [
            SectionSearchHit(
                id="3.1",
                title="Gợi ý",
                breadcrumb="Sao > Gợi ý",
                score=1.0,
                summary=f"Gợi ý cho {query}",
            )
        ]


def _ctx(book: _Book):
    return SimpleNamespace(deps=SimpleNamespace(require_book=lambda: book))


def test_search_star_info_batches_chinh_tinh_and_phu_tinh_by_section() -> None:
    book = _Book()

    result = search_star_info(
        _ctx(book),
        ["Tử Vi", "Kình Dương", "Đà La", "Tử Vi"],
    )

    assert result.requested_star_names == ["Tử Vi", "Kình Dương", "Đà La"]
    assert book.read_ids == ["3.1", "3.15"]
    assert [section.star_names for section in result.sections] == [
        ["Tử Vi"],
        ["Kình Dương", "Đà La"],
    ]
    assert result.not_found == []


def test_search_star_info_keeps_unknown_name_unmatched() -> None:
    result = search_star_info(_ctx(_Book()), ["Sao không có"])

    assert result.sections == []
    assert result.not_found == ["Sao không có"]
    assert result.suggestions["Sao không có"][0].title == "Gợi ý"


def test_search_star_info_limits_batch_size() -> None:
    with pytest.raises(ModelRetry, match="tối đa 12 sao"):
        search_star_info(_ctx(_Book()), [f"Sao {index}" for index in range(13)])
