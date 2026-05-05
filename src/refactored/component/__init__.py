from typing import TypeAlias

from src.refactored.component.cuc import Cuc
from src.refactored.component.cung_role import CungRole
from src.refactored.component.elementary import DiaChiEntity, ThienCanEntity
from src.refactored.component.sao import ChinhPhuTinh, Sao, TuanTriet, TuHoa, VongTrangSinh

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
