from __future__ import annotations

from functools import cache
import logging
from pathlib import Path

import yaml

from src.agent.cach_cuc.models import CachCucData, SourceKind


_logger = logging.getLogger(__name__)


DEFAULT_TUVITANBIEN_CACH_CUC_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "cach_cuc_reviewed.yaml"
)


def load_cach_cuc_data(path: Path) -> CachCucData:
    _logger.info("Loading cach_cuc data from %s", path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        data = CachCucData.model_validate(raw)
    except Exception as e:
        _logger.error("Failed to validate cach_cuc data from %s: %s", path, e)
        raise ValueError(f"Failed to validate cach_cuc data from {path}: {e}") from e
    _logger.info(
        "Loaded cach_cuc data from %s: entries=%d groups=%d",
        path,
        len(data.cach_cuc),
        len(data.groups),
    )
    return data


@cache
def load_cach_cuc_source(source_kind: SourceKind) -> CachCucData:
    _logger.debug("Resolving cach_cuc source: source_kind=%s", source_kind)
    if source_kind == SourceKind.TUVITANBIEN:
        return load_cach_cuc_data(DEFAULT_TUVITANBIEN_CACH_CUC_PATH)
    raise ValueError(f"Unsupported cach_cuc source kind: {source_kind}")
