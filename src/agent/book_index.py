from __future__ import annotations

import dataclasses as dc
from collections import Counter
import difflib
import re
from pathlib import Path

from pydantic import BaseModel, Field

try:
    from unidecode import unidecode
except ImportError:  # pragma: no cover - dependency exists in this project.
    def unidecode(value: str) -> str:
        return value


SECTION_FILE_RE = re.compile(r"^(?P<raw_id>\d+(?:_\d+)*)_(?P<slug>.+)\.md$")
NUMBERED_TITLE_RE = re.compile(r"^(?P<section_id>\d+(?:\.\d+)*)(?:\.)?\s+(?P<title>.+)$")
SECTION_ID_RE = re.compile(r"^\d+(?:\.\d+)*$")


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").strip().title()


def _raw_id_to_display(raw_id: str) -> str:
    return raw_id.replace("_", ".")


def _parent_display_id(display_id: str) -> str | None:
    parts = display_id.split(".")
    if len(parts) <= 1:
        return None
    return ".".join(parts[:-1])


def _section_level(display_id: str) -> int:
    return len(display_id.split("."))


def _display_sort_key(display_id: str) -> tuple[int, ...]:
    numeric_id = display_id.split("#")[0]
    return tuple(int(part) for part in numeric_id.split("."))


def _normalize_section_id(section_id: str) -> str:
    normalized = section_id.strip().replace("_", ".").split("#", 1)[0]
    if not SECTION_ID_RE.fullmatch(normalized):
        raise ValueError(
            "section_id must use numeric format, for example '3', '3.4', "
            "'3.4.5', or '8.11'."
        )
    return normalized


def _normalize_text(value: str) -> str:
    return unidecode(value).casefold().strip()


def _extract_title_and_content(
    markdown_text: str,
    fallback_title: str,
    display_id: str,
) -> tuple[str, str]:
    """
    Extract a section title from the first markdown heading or numbered line.
    The chunk files usually start with lines such as "1.1. Thuận lý - Nghịch lý".
    """
    lines = markdown_text.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        heading = stripped.lstrip("#").strip() if stripped.startswith("#") else stripped
        title_match = NUMBERED_TITLE_RE.match(heading)
        if title_match and title_match.group("section_id") == display_id:
            title = title_match.group("title").strip()
            remaining = "\n".join(lines[i + 1 :]).strip()
            return title or fallback_title, remaining

        if stripped.startswith("#"):
            title = heading
            remaining = "\n".join(lines[i + 1 :]).strip()
            return title or fallback_title, remaining

        break

    return fallback_title, markdown_text.strip()


def _make_summary(text: str, max_chars: int = 240) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


@dc.dataclass(slots=True)
class SectionRecord:
    id: str
    raw_id: str
    slug: str
    title: str
    parent_id: str | None
    level: int
    path: Path
    content: str
    summary: str
    children_ids: list[str]

    def sort_description(self) -> str:
        return f"{self.id} {self.title}"


class SectionMeta(BaseModel):
    id: str = Field(
        description="Section id usable by the book tools, for example '1.1'."
    )
    title: str
    parent_id: str | None
    level: int
    breadcrumb: str
    children: list[str] = Field(
        default_factory=list,
        description="Immediate child section ids.",
    )
    summary: str


class SectionContent(BaseModel):
    id: str
    title: str
    breadcrumb: str
    content: str


class SectionSearchHit(BaseModel):
    id: str
    title: str
    breadcrumb: str
    score: float = Field(description="Heuristic score. Higher is better.")
    summary: str


class ListSectionsResult(BaseModel):
    sections: list[SectionMeta]


class SearchSectionsResult(BaseModel):
    hits: list[SectionSearchHit]


class BookIndexNode(BaseModel):
    id: str = Field(description="Section id usable by read_section.")
    title: str
    level: int
    breadcrumb: str
    summary: str | None = None
    children: list["BookIndexNode"] = Field(default_factory=list)


class BookIndexResult(BaseModel):
    parent_id: str | None = Field(
        default=None,
        description="Section id used as the root of this index view.",
    )
    depth: int = Field(description="How many descendant levels are included.")
    truncated: bool = Field(
        description="True when max_sections stopped the tree before all matching sections were returned."
    )
    sections: list[BookIndexNode]


class BookIndex:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self._sections_by_id: dict[str, SectionRecord] = {}
        self._build_index()

    def _iter_section_files(self) -> list[Path]:
        direct = [p for p in self.root_dir.glob("*.md") if SECTION_FILE_RE.match(p.name)]
        if direct:
            return direct
        return [p for p in self.root_dir.glob("*/*.md") if SECTION_FILE_RE.match(p.name)]

    def _build_index(self) -> None:
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Book directory does not exist: {self.root_dir}")

        section_files = sorted(
            self._iter_section_files(),
            key=lambda p: _display_sort_key(
                _raw_id_to_display(SECTION_FILE_RE.match(p.name).group("raw_id"))  # type: ignore[union-attr]
            ),
        )
        temp_records: list[SectionRecord] = []

        for path in section_files:
            match = SECTION_FILE_RE.match(path.name)
            if not match:
                continue

            raw_id = match.group("raw_id")
            slug = match.group("slug")
            section_id = _raw_id_to_display(raw_id)
            fallback_title = _slug_to_title(slug)

            parent_id = _parent_display_id(section_id)

            markdown_text = path.read_text(encoding="utf-8")
            title, content = _extract_title_and_content(
                markdown_text,
                fallback_title,
                section_id,
            )

            temp_records.append(
                SectionRecord(
                    id=section_id,
                    raw_id=raw_id,
                    slug=slug,
                    title=title,
                    parent_id=parent_id,
                    level=_section_level(section_id),
                    path=path,
                    content=content,
                    summary=_make_summary(content),
                    children_ids=[],
                )
            )

        base_id_counts = Counter(record.id for record in temp_records)
        for record in temp_records:
            if base_id_counts[record.id] > 1:
                record.id = f"{record.id}#{record.slug}"

        self._sections_by_id = {record.id: record for record in temp_records}

        for record in temp_records:
            if record.parent_id and record.parent_id not in self._sections_by_id:
                record.parent_id = self._nearest_existing_parent_id(record)
            if record.parent_id and record.parent_id in self._sections_by_id:
                self._sections_by_id[record.parent_id].children_ids.append(record.id)

        for record in self._sections_by_id.values():
            record.children_ids.sort(
                key=lambda sid: _display_sort_key(self._sections_by_id[sid].id)
            )

    def _nearest_existing_parent_id(self, record: SectionRecord) -> str | None:
        parts = record.id.split(".")
        for length in range(len(parts) - 1, 0, -1):
            parent_id = ".".join(parts[:length])
            if parent_id in self._sections_by_id:
                return parent_id
        return None

    def has_section(self, section_id: str) -> bool:
        try:
            normalized = _normalize_section_id(section_id)
        except ValueError:
            return False
        return normalized in self._sections_by_id

    def get_record(self, section_id: str) -> SectionRecord:
        normalized = _normalize_section_id(section_id)
        record = self._sections_by_id.get(normalized)
        if record is None:
            raise ValueError(f"Unknown section id: {section_id}")
        return record

    def _ancestor_records(self, record: SectionRecord) -> list[SectionRecord]:
        records: list[SectionRecord] = []
        current_id: str | None = record.id

        while current_id is not None:
            current = self.get_record(current_id)
            records.append(current)
            current_id = current.parent_id

        return list(reversed(records))

    def list_sections(self, parent_id: str | None = None) -> list[SectionRecord]:
        if parent_id is None:
            top_level = [r for r in self._sections_by_id.values() if r.parent_id is None]
            return sorted(top_level, key=lambda r: _display_sort_key(r.id))

        parent = self.get_record(parent_id)
        return [self.get_record(child_id) for child_id in parent.children_ids]

    def breadcrumb(self, section_id: str) -> str:
        record = self.get_record(section_id)
        parts: list[str] = []
        current_id: str | None = record.id

        while current_id is not None:
            current = self.get_record(current_id)
            parts.append(f"{current.id} {current.title}")
            current_id = current.parent_id

        return " > ".join(reversed(parts))

    def get_meta(self, section_id: str) -> SectionMeta:
        record = self.get_record(section_id)
        return SectionMeta(
            id=record.id,
            title=record.title,
            parent_id=record.parent_id,
            level=record.level,
            breadcrumb=self.breadcrumb(record.id),
            children=list(record.children_ids),
            summary=record.summary,
        )

    def read_index(
        self,
        parent_id: str | None = None,
        *,
        depth: int = 2,
        include_summary: bool = False,
        max_sections: int = 80,
    ) -> BookIndexResult:
        bounded_depth = max(1, min(depth, 6))
        bounded_max_sections = max(1, min(max_sections, 300))
        remaining = bounded_max_sections
        truncated = False

        def make_node(record: SectionRecord, current_depth: int) -> BookIndexNode:
            nonlocal remaining, truncated
            remaining -= 1

            children: list[BookIndexNode] = []
            if current_depth < bounded_depth:
                for child_id in record.children_ids:
                    if remaining <= 0:
                        truncated = True
                        break
                    child = self.get_record(child_id)
                    children.append(make_node(child, current_depth + 1))
            elif record.children_ids:
                truncated = True

            return BookIndexNode(
                id=record.id,
                title=record.title,
                level=record.level,
                breadcrumb=self.breadcrumb(record.id),
                summary=record.summary if include_summary else None,
                children=children,
            )

        roots = self.list_sections(parent_id=parent_id)
        sections: list[BookIndexNode] = []
        for record in roots:
            if remaining <= 0:
                truncated = True
                break
            sections.append(make_node(record, 1))

        public_parent_id = None
        if parent_id is not None:
            parent_record = self.get_record(parent_id)
            public_parent_id = parent_record.id

        return BookIndexResult(
            parent_id=public_parent_id,
            depth=bounded_depth,
            truncated=truncated,
            sections=sections,
        )

    def read_section(
        self,
        section_id: str,
        *,
        max_chars: int | None = None,
    ) -> SectionContent:
        """
        Read a section and its parent context.

        section_id must be a numeric id such as "3", "3.4", "3.4.5", or
        "8.11". If a slug suffix is provided, for example
        "8.11#bo-sao-khoc-hu-thien-khoc-thien-hu", only "8.11" is used.
        The returned content includes all parent section content before the
        requested section content, for example read_section("3.5") returns
        content from section "3" followed by section "3.5".
        """
        record = self.get_record(section_id)

        parts = [
            f"## {ancestor.id} {ancestor.title}\n\n{ancestor.content}"
            for ancestor in self._ancestor_records(record)
        ]
        content = "\n\n".join(parts).strip()

        if max_chars is not None and max_chars > 3 and len(content) > max_chars:
            content = content[: max_chars - 3].rstrip() + "..."

        return SectionContent(
            id=record.id,
            title=record.title,
            breadcrumb=self.breadcrumb(record.id),
            content=content,
        )

    def get_catalog(self, section_id: str | None = None, depth: int | None = None) -> str:
        def render_node(record: SectionRecord, prefix: str, is_last: bool, remaining_depth: int | None) -> list[str]:
            connector = "└── " if is_last else "├── "
            lines = [f"{prefix}{connector}{record.id} {record.title}"]
            if remaining_depth is not None and remaining_depth <= 0:
                return lines
            child_prefix = prefix + ("    " if is_last else "│   ")
            next_depth = None if remaining_depth is None else remaining_depth - 1
            for i, child_id in enumerate(record.children_ids):
                child = self.get_record(child_id)
                lines.extend(render_node(child, child_prefix, i == len(record.children_ids) - 1, next_depth))
            return lines

        if section_id is None:
            roots = self.list_sections(parent_id=None)
            lines: list[str] = []
            next_depth = None if depth is None else depth - 1
            for i, record in enumerate(roots):
                is_last = i == len(roots) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{connector}{record.id} {record.title}")
                if next_depth is None or next_depth > 0:
                    child_prefix = "    " if is_last else "│   "
                    child_next_depth = None if next_depth is None else next_depth - 1
                    for j, child_id in enumerate(record.children_ids):
                        child = self.get_record(child_id)
                        lines.extend(render_node(child, child_prefix, j == len(record.children_ids) - 1, child_next_depth))
            return "\n".join(lines)

        record = self.get_record(section_id)
        lines = [f"{record.id} {record.title}"]
        if depth is None or depth > 0:
            next_depth = None if depth is None else depth - 1
            for i, child_id in enumerate(record.children_ids):
                child = self.get_record(child_id)
                lines.extend(render_node(child, "", i == len(record.children_ids) - 1, next_depth))
        return "\n".join(lines)

    def search_sections(self, query: str, top_k: int = 5) -> list[SectionSearchHit]:
        query_norm = _normalize_text(query)
        query_tokens = set(re.findall(r"\w+", query_norm))

        hits: list[SectionSearchHit] = []

        for record in self._sections_by_id.values():
            hay_id = _normalize_text(record.id)
            hay_title = _normalize_text(record.title)
            hay_summary = _normalize_text(record.summary)
            hay_content = _normalize_text(record.content[:5000])

            score = 0.0

            if query_norm and query_norm in hay_id:
                score += 10.0

            if query_norm and query_norm in hay_title:
                score += 8.0

            if query_norm and query_norm in hay_summary:
                score += 4.0

            title_tokens = set(re.findall(r"\w+", hay_title))
            summary_tokens = set(re.findall(r"\w+", hay_summary))
            content_tokens = set(re.findall(r"\w+", hay_content))

            score += 2.5 * len(query_tokens & title_tokens)
            score += 1.2 * len(query_tokens & summary_tokens)
            score += 0.4 * len(query_tokens & content_tokens)

            if query_norm:
                fuzzy_title = difflib.SequenceMatcher(None, query_norm, hay_title).ratio()
                score += fuzzy_title * 2.0

            if score > 0:
                hits.append(
                    SectionSearchHit(
                        id=record.id,
                        title=record.title,
                        breadcrumb=self.breadcrumb(record.id),
                        score=round(score, 3),
                        summary=record.summary,
                    )
                )

        hits.sort(
            key=lambda hit: (
                -hit.score,
                _display_sort_key(hit.id),
            )
        )
        return hits[:top_k]
