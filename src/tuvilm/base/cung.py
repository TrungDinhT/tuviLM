from typing import Literal
from sao import Sao

MAP_POSITION = {

}

class Cung:

    def __init__(
        self,
        position : int,
        chinh_tinh : list[Sao],
        phu_tinh : list[Sao],
    ):
        self.position = position
        self.chinh_tinh = chinh_tinh
        self.phu_tinh = phu_tinh
        self.name = MAP_POSITION[position]
