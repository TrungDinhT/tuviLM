from functools import cache
from pathlib import Path

from pydantic import TypeAdapter

from src.refactored.component.elementary import ComponentBase, NguHanh


class Cuc(ComponentBase):
    number: int
    ngu_hanh: NguHanh


_CUC_ADAPTER = TypeAdapter(list[Cuc])


@cache
def get_default_cucs() -> tuple[Cuc, ...]:
    catalog_dir = Path(__file__).resolve().parent.parent / "catalog"
    raw_json = (catalog_dir / "cuc.json").read_text(encoding="utf-8")
    return tuple(_CUC_ADAPTER.validate_json(raw_json))


LIST_CUC = get_default_cucs()
