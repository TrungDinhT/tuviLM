from typing import TypeAlias

from tuvi_engine.components.definitions.ban_menh import BanMenh
from tuvi_engine.components.definitions.cuc import Cuc
from tuvi_engine.components.definitions.cung_role import CungRole
from tuvi_engine.components.definitions.elementary import DiaChiEntity, ThienCanEntity
from tuvi_engine.components.definitions.sao import (
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
