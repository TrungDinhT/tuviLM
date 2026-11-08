"""Validated reports and descriptive diversity metrics, with no model calls."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from math import comb, isfinite, prod
from statistics import mean
from typing import Any

import yaml

from src.agent.workflow.strength_weakness.ontology import get_capability_definition
from src.agent.workflow.strength_weakness.output.capability_profile import CapabilityProfile

ProfileKey = tuple[str, str, str, str]


def profile_key(profile: dict) -> ProfileKey:
    """Names alone are not unique; birth details must agree across runs."""
    return tuple(str(profile.get(k, '')) for k in ('name', 'birth_date', 'birth_time', 'gender'))


def profile_label(key: ProfileKey) -> str:
    name, date, hour, gender = key
    gender = {'male': 'Nam', 'female': 'Nữ'}.get(gender, gender)
    return f'{name} · {date} · giờ {hour} · {gender}'


@dataclass
class Report:
    source: str
    model: str
    document: dict
    rows: dict[ProfileKey, dict]
    digest: str

    @property
    def label(self) -> str:
        return f'{self.model} · {self.source}'

    @property
    def successful(self) -> dict[ProfileKey, dict]:
        return {key: row for key, row in self.rows.items() if 'output' in row}


def parse_report_yaml(text: str) -> Any:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f'Invalid YAML report: {exc}') from exc


def read_report(data: bytes, source: str) -> Report:
    try:
        document = parse_report_yaml(data.decode('utf-8-sig'))
    except UnicodeError as exc:
        raise ValueError('Report phải dùng UTF-8.') from exc
    if not isinstance(document, dict) or document.get('workflow') != 'strength_weakness':
        raise ValueError('Viewer chỉ nhận report workflow strength_weakness.')
    results = document.get('results', [])
    if not isinstance(results, list):
        raise ValueError('results phải là danh sách hồ sơ.')
    rows = {}
    for index, original in enumerate(results, 1):
        if not isinstance(original, dict) or not isinstance(original.get('profile'), dict):
            raise ValueError(f'Hồ sơ #{index}: thiếu profile.')
        profile = original['profile']
        if any(profile.get(k) is None for k in ('name', 'birth_date', 'birth_time', 'gender')):
            raise ValueError(f'Hồ sơ #{index}: thiếu tên hoặc thông tin sinh để đối chiếu.')
        key = profile_key(profile)
        if key in rows:
            raise ValueError(f'Hồ sơ trùng định danh: {profile_label(key)}')
        row = dict(original)
        if 'error' in row:
            row.pop('output', None)
        elif 'output' in row:
            try:
                row['output'] = CapabilityProfile.model_validate(row['output']).model_dump(mode='json')
            except ValueError as exc:
                raise ValueError(f'Hồ sơ #{index}: output không hợp lệ: {exc}') from exc
        else:
            row['error'] = 'Chưa có kết quả.'
        rows[key] = row
    return Report(source, str(document.get('model', 'Không rõ model')), document, rows, sha256(data).hexdigest())


def common_profiles(reports: list[Report]) -> list[ProfileKey]:
    if not reports:
        return []
    common = set.intersection(*(set(r.successful) for r in reports))
    return [key for key in reports[0].successful if key in common]


def number(metrics: Any, key: str) -> float | None:
    value = metrics.get(key) if isinstance(metrics, dict) else None
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value >= 0 else None


def complete_total(rows: list[dict], key: str) -> float | None:
    values = [number(row.get('metrics'), key) for row in rows]
    return sum(values) if values and all(v is not None for v in values) else None


def strength_labels(row: dict, level: str) -> list[str]:
    return [str(getattr(get_capability_definition(f['nang_luc_id']), level))
            for f in row['output']['diem_manh']]


def overlap(a: set, b: set) -> float | None:
    return len(a & b) / len(a | b) if a | b else None


def diversity(label_lists: list[list[str]]) -> dict:
    """Exact rarefaction to two findings; undefined values remain None.

    Empty/empty pairs have no evidence of similarity and are excluded from raw
    Jaccard. Equal-two is unavailable if any profile has fewer than two findings.
    """
    counts = [Counter(labels) for labels in label_lists]
    sets = [set(labels) for labels in label_lists]
    union = set().union(*sets)
    pairs = [v for a, b in combinations(sets, 2) if (v := overlap(a, b)) is not None]
    frequencies = Counter(x for labels in label_lists for x in labels)
    total = sum(map(len, label_lists))
    result = {
        'profiles': len(sets), 'findings': total, 'unique': len(union),
        'within': mean(map(len, sets)) if sets else None,
        'jaccard': mean(pairs) if pairs else None, 'pairs': len(pairs),
        'identical_pairs': sum(bool(a) and a == b for a, b in combinations(sets, 2)),
        'equal_two_unique': None, 'equal_two_within': None, 'equal_two_jaccard': None,
        'equal_two_eligible': sum(len(labels) >= 2 for labels in label_lists),
        'top_three_share': sum(sorted(frequencies.values(), reverse=True)[:3]) / total if total else None,
        'frequencies': {label: sum(label in s for s in sets) for label in sorted(union)},
    }
    if not counts or any(sum(c.values()) < 2 for c in counts):
        return result
    result['equal_two_unique'] = sum(
        1 - prod(comb(sum(c.values()) - c[x], 2) / comb(sum(c.values()), 2) for c in counts)
        for x in union)
    result['equal_two_within'] = mean(
        sum(1 - comb(sum(c.values()) - n, 2) / comb(sum(c.values()), 2) for n in c.values())
        for c in counts)
    distributions = []
    for labels in label_lists:
        outcomes = Counter(frozenset(pair) for pair in combinations(labels, 2))
        total_outcomes = sum(outcomes.values())
        distributions.append([(s, n / total_outcomes) for s, n in outcomes.items()])
    expected = [sum(pa * pb * len(a & b) / len(a | b) for a, pa in da for b, pb in db)
                for da, db in combinations(distributions, 2)]
    result['equal_two_jaccard'] = mean(expected) if expected else None
    return result


def reviewed_weaknesses(report: Report, annotations: dict) -> dict[ProfileKey, list[str]] | None:
    """Annotations are valid only for the exact reviewed file and finding order."""
    entry = annotations.get('reports', {}).get(report.digest)
    if not entry or entry.get('model') != report.model:
        return None
    indexed = {profile_key(p['profile']): p for p in entry['profiles']}
    if set(indexed) != set(report.successful):
        return None
    result = {}
    themes = annotations.get('themes', {})
    for key, row in report.successful.items():
        annotated = indexed[key]['weaknesses']
        if [f['title'] for f in annotated] != [f['ten'] for f in row['output']['diem_yeu']]:
            return None
        labels = [f['primary_theme'] for f in annotated]
        if not set(labels) <= themes.keys():
            return None
        result[key] = labels
    return result
