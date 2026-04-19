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
    return tuple(int(part) for part in display_id.split("."))


def _part_sort_key(part_id: str | None) -> tuple[object, ...]:
    if part_id is None:
        return ("",)
    pieces = re.split(r"(\d+)", part_id)
    return tuple(int(piece) if piece.isdigit() else piece for piece in pieces)


def _canonical_id(part_id: str | None, display_id: str, uses_part_prefixes: bool) -> str:
    if uses_part_prefixes and part_id:
        return f"{part_id}/{display_id}"
    return display_id


def _section_file_sort_key(item: tuple[Path, str | None]) -> tuple[object, ...]:
    path, part_id = item
    match = SECTION_FILE_RE.match(path.name)
    if not match:
        return (*_part_sort_key(part_id), 0)
    return (
        *_part_sort_key(part_id),
        *_display_sort_key(_raw_id_to_display(match.group("raw_id"))),
    )


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
    local_id: str
    raw_id: str
    slug: str
    title: str
    part_id: str | None
    parent_id: str | None
    level: int
    path: Path
    content: str
    summary: str
    children_ids: list[str]


class SectionMeta(BaseModel):
    id: str = Field(
        description="Section id usable by the book tools, for example '1.1'."
    )
    local_id: str = Field(description="Section id inside its part, for example '1.1'.")
    part_id: str | None = Field(
        default=None,
        description="Book part folder when it is not the default part.",
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
    local_id: str
    part_id: str | None
    title: str
    breadcrumb: str
    content: str


class SectionSearchHit(BaseModel):
    id: str
    local_id: str
    part_id: str | None
    title: str
    breadcrumb: str
    score: float = Field(description="Heuristic score. Higher is better.")
    summary: str


class ListSectionsResult(BaseModel):
    sections: list[SectionMeta]


class SearchSectionsResult(BaseModel):
    hits: list[SectionSearchHit]


class BookIndex:
    def __init__(self, root_dir: str | Path, *, default_part_id: str | None = None) -> None:
        self.root_dir = Path(root_dir)
        self.default_part_id = default_part_id
        self._uses_part_prefixes = False
        self._sections_by_id: dict[str, SectionRecord] = {}
        self._sections_by_local_id: dict[str, list[str]] = {}
        self._part_ids: set[str] = set()
        self._build_index()

    @property
    def part_ids(self) -> list[str]:
        return sorted(self._part_ids, key=_part_sort_key)

    def _default_part_id(self) -> str | None:
        if self.default_part_id in self._part_ids:
            return self.default_part_id
        return None

    def _public_section_id(self, section_id: str | None) -> str | None:
        if section_id is None:
            return None

        default_part_id = self._default_part_id()
        if default_part_id:
            prefix = f"{default_part_id}/"
            if section_id.startswith(prefix):
                return section_id[len(prefix):]
        return section_id

    def _public_part_id(self, part_id: str | None) -> str | None:
        if part_id == self._default_part_id():
            return None
        return part_id

    def _iter_section_files(self) -> list[tuple[Path, str | None]]:
        direct_files = [
            path for path in self.root_dir.glob("*.md")
            if SECTION_FILE_RE.match(path.name)
        ]
        if direct_files:
            return [(path, None) for path in direct_files]

        files: list[tuple[Path, str | None]] = []
        for path in self.root_dir.glob("*/*.md"):
            if SECTION_FILE_RE.match(path.name):
                files.append((path, path.parent.name))
        self._uses_part_prefixes = len({part_id for _, part_id in files if part_id}) > 1
        return files

    def _build_index(self) -> None:
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Book directory does not exist: {self.root_dir}")

        section_files = self._iter_section_files()
        temp_records: list[SectionRecord] = []

        for path, part_id in sorted(section_files, key=_section_file_sort_key):
            match = SECTION_FILE_RE.match(path.name)
            if not match:
                continue

            raw_id = match.group("raw_id")
            slug = match.group("slug")
            local_id = _raw_id_to_display(raw_id)
            fallback_title = _slug_to_title(slug)
            section_id = _canonical_id(part_id, local_id, self._uses_part_prefixes)

            parent_local_id = _parent_display_id(local_id)
            parent_id = (
                _canonical_id(part_id, parent_local_id, self._uses_part_prefixes)
                if parent_local_id
                else None
            )

            markdown_text = path.read_text(encoding="utf-8")
            title, content = _extract_title_and_content(
                markdown_text,
                fallback_title,
                local_id,
            )

            temp_records.append(
                SectionRecord(
                    id=section_id,
                    local_id=local_id,
                    raw_id=raw_id,
                    slug=slug,
                    title=title,
                    part_id=part_id,
                    parent_id=parent_id,
                    level=_section_level(local_id),
                    path=path,
                    content=content,
                    summary=_make_summary(content),
                    children_ids=[],
                )
            )
            if part_id:
                self._part_ids.add(part_id)

        base_id_counts = Counter(record.id for record in temp_records)
        for record in temp_records:
            if base_id_counts[record.id] > 1:
                record.id = f"{record.id}#{record.slug}"

        self._sections_by_id = {record.id: record for record in temp_records}
        self._sections_by_local_id = {}
        for record in temp_records:
            self._sections_by_local_id.setdefault(record.local_id, []).append(record.id)

        for record in temp_records:
            if record.parent_id and record.parent_id not in self._sections_by_id:
                record.parent_id = self._nearest_existing_parent_id(record)
            if record.parent_id and record.parent_id in self._sections_by_id:
                self._sections_by_id[record.parent_id].children_ids.append(record.id)

        for record in self._sections_by_id.values():
            record.children_ids.sort(
                key=lambda section_id: self._record_sort_key(
                    self._sections_by_id[section_id]
                )
            )

    def _record_sort_key(self, record: SectionRecord) -> tuple[object, ...]:
        return (*_part_sort_key(record.part_id), *_display_sort_key(record.local_id))

    def _nearest_existing_parent_id(self, record: SectionRecord) -> str | None:
        parts = record.local_id.split(".")
        for length in range(len(parts) - 1, 0, -1):
            parent_local_id = ".".join(parts[:length])
            parent_id = _canonical_id(
                record.part_id,
                parent_local_id,
                self._uses_part_prefixes,
            )
            if parent_id in self._sections_by_id:
                return parent_id
        return None

    def _lookup_candidates(self, section_id: str) -> list[str]:
        normalized = section_id.strip().replace(":", "/", 1)
        if not normalized:
            return []

        candidates: list[str] = []
        if normalized in self._sections_by_id:
            candidates.append(normalized)

        if "/" in normalized:
            part_id, local_id = normalized.split("/", 1)
            local_id = local_id.replace("_", ".")
            canonical = _canonical_id(part_id, local_id, self._uses_part_prefixes)
            if canonical in self._sections_by_id and canonical not in candidates:
                candidates.append(canonical)
            return candidates

        local_id = normalized.replace("_", ".")
        if self.default_part_id:
            default_canonical = _canonical_id(
                self.default_part_id,
                local_id,
                self._uses_part_prefixes,
            )
            if default_canonical in self._sections_by_id and default_canonical not in candidates:
                candidates.append(default_canonical)

        for candidate in self._sections_by_local_id.get(local_id, []):
            if candidate not in candidates:
                candidates.append(candidate)
        return candidates

    def has_section(self, section_id: str) -> bool:
        try:
            self.get_record(section_id)
        except ValueError:
            return False
        return True

    def get_record(self, section_id: str) -> SectionRecord:
        candidates = self._lookup_candidates(section_id)
        if not candidates:
            raise ValueError(f"Unknown section id: {section_id}")
        if len(candidates) == 1:
            return self._sections_by_id[candidates[0]]
        if self.default_part_id:
            default_candidates = [
                candidate for candidate in candidates
                if candidate.startswith(f"{self.default_part_id}/")
            ]
            if len(default_candidates) == 1:
                return self._sections_by_id[default_candidates[0]]
        public_candidates = [
            self._public_section_id(candidate) or candidate for candidate in candidates
        ]
        raise ValueError(
            f"Ambiguous section id '{section_id}'. Use one of: {', '.join(public_candidates)}"
        )

    def list_sections(
        self,
        parent_id: str | None = None,
        *,
        part_id: str | None = None,
    ) -> list[SectionRecord]:
        if parent_id and parent_id in self._part_ids and part_id is None:
            part_id = parent_id
            parent_id = None

        if parent_id is None:
            if part_id is None:
                part_id = self._default_part_id()
            top_level = [
                section for section in self._sections_by_id.values()
                if section.parent_id is None
                and (part_id is None or section.part_id == part_id)
            ]
            return sorted(top_level, key=self._record_sort_key)

        parent = self.get_record(parent_id)
        return [self.get_record(child_id) for child_id in parent.children_ids]

    def breadcrumb(self, section_id: str) -> str:
        record = self.get_record(section_id)
        parts: list[str] = []
        current_id: str | None = record.id

        while current_id is not None:
            current = self.get_record(current_id)
            parts.append(f"{current.local_id} {current.title}")
            current_id = current.parent_id

        if record.part_id and record.part_id != self._default_part_id():
            parts.append(record.part_id)

        return " > ".join(reversed(parts))

    def get_meta(self, section_id: str) -> SectionMeta:
        record = self.get_record(section_id)
        return SectionMeta(
            id=self._public_section_id(record.id) or record.id,
            local_id=record.local_id,
            part_id=self._public_part_id(record.part_id),
            title=record.title,
            parent_id=self._public_section_id(record.parent_id),
            level=record.level,
            breadcrumb=self.breadcrumb(record.id),
            children=[
                self._public_section_id(child_id) or child_id
                for child_id in record.children_ids
            ],
            summary=record.summary,
        )

    def read_section(
        self,
        section_id: str,
        *,
        include_children: bool = False,
        max_chars: int | None = None,
    ) -> SectionContent:
        record = self.get_record(section_id)

        content = record.content
        if include_children and record.children_ids:
            parts = [content]
            for child_id in record.children_ids:
                child = self.get_record(child_id)
                parts.append(f"\n\n## {child.local_id} {child.title}\n\n{child.content}")
            content = "".join(parts).strip()

        if max_chars is not None and max_chars > 3 and len(content) > max_chars:
            content = content[: max_chars - 3].rstrip() + "..."

        return SectionContent(
            id=self._public_section_id(record.id) or record.id,
            local_id=record.local_id,
            part_id=self._public_part_id(record.part_id),
            title=record.title,
            breadcrumb=self.breadcrumb(record.id),
            content=content,
        )

    def search_sections(self, query: str, top_k: int = 5) -> list[SectionSearchHit]:
        query_norm = _normalize_text(query)
        query_tokens = set(re.findall(r"\w+", query_norm))

        hits: list[SectionSearchHit] = []
        default_part_id = self._default_part_id()

        for record in self._sections_by_id.values():
            if default_part_id and record.part_id != default_part_id:
                continue

            public_id = self._public_section_id(record.id) or record.id
            hay_id = _normalize_text(public_id)
            hay_local_id = _normalize_text(record.local_id)
            hay_title = _normalize_text(record.title)
            hay_summary = _normalize_text(record.summary)
            hay_content = _normalize_text(record.content[:5000])

            score = 0.0

            if query_norm and (query_norm in hay_id or query_norm in hay_local_id):
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
                        id=public_id,
                        local_id=record.local_id,
                        part_id=self._public_part_id(record.part_id),
                        title=record.title,
                        breadcrumb=self.breadcrumb(record.id),
                        score=round(score, 3),
                        summary=record.summary,
                    )
                )

        hits.sort(
            key=lambda hit: (
                -hit.score,
                self._record_sort_key(self.get_record(hit.id)),
            )
        )
        return hits[:top_k]
