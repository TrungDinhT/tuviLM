from typing import TypeAlias

from src.refactored.components.definitions.cuc import Cuc
from src.refactored.components.definitions.cung_role import CungRole
from src.refactored.components.definitions.elementary import DiaChiEntity, ThienCanEntity
from src.refactored.components.definitions.sao import (
    ChinhPhuTinh,
    Sao,
    TuanTriet,
    TuHoa,
    VongTrangSinh,
)

Component: TypeAlias = DiaChiEntity | ThienCanEntity | Cuc | CungRole | Sao

__all__ = [
    "ChinhPhuTinh",
    "Component",
    "Cuc",
    "CungRole",
    "DiaChiEntity",
    "Sao",
    "ThienCanEntity",
    "TuHoa",
    "TuanTriet",
    "VongTrangSinh",
]
