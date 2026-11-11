from __future__ import annotations

from src.agent.tool.cach_cuc.loader import load_cach_cuc_source
from src.agent.tool.cach_cuc.models import SourceKind

# (group id in the cach_cuc groups data, Vietnamese label). Ordered so
# higher-signal groups surface first in tool output.
PHU_TINH_GROUP_LABELS: tuple[tuple[str, str], ...] = (
    ("luc_cat", "Lục Cát"),
    ("luc_sat", "Lục Sát"),
    ("tu_hoa", "Tứ Hóa"),
    ("tu_linh", "Tứ Linh"),
    ("tam_minh", "Tam Minh"),
)


def load_phu_tinh_groups(
    source_kind: SourceKind = SourceKind.TUVITANBIEN,
) -> dict[str, tuple[str, ...]]:
    """Return {group_id: star ids} for the five phụ tinh groups, from data."""
    data = load_cach_cuc_source(source_kind)
    return {
        group_id: tuple(data.groups[group_id].stars)
        for group_id, _ in PHU_TINH_GROUP_LABELS
    }


def build_group_of_star(groups: dict[str, tuple[str, ...]]) -> dict[str, str]:
    """Invert grouped stars into star id -> group id.

    The five groups do not overlap, so each star maps to at most one group.
    """
    return {star: group_id for group_id, stars in groups.items() for star in stars}
