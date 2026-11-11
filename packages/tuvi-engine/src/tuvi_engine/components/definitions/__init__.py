from typing import TypeAlias

from src.refactored.components.definitions.ban_menh import BanMenh
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

Component: TypeAlias = DiaChiEntity | ThienCanEntity | Cuc | CungRole | Sao | BanMenh

__all__ = [
    "BanMenh",
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
