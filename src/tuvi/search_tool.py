from typing import Literal
from src.tuvi.tinh_ban import TinhBan
from src.tuvi.element.types import LIST_DIA_CHI, TYPE_DIA_CHI
from src.tuvi.database.tinhban import StarComposition
from src.tuvi.transform import get_tam_hop, get_xung_chieu

# TODO : Must improve this
def search_sao(tinhBan : TinhBan, sao_name : str) -> TYPE_DIA_CHI:
    for position, cung in tinhBan.map_cung.items():
        list_sao_name = [sao.name for sao in cung.chinhTinh + cung.phuTinh]
        if sao_name in list_sao_name:
            return position
    raise ValueError(f"Can not find {sao_name}")

def search_list_sao(tinhBan : TinhBan, list_sao : list[str]) -> list[TYPE_DIA_CHI]:
    return [search_sao(tinhBan, sao) for sao in list_sao]


def check_composition(
    tinhBan : TinhBan,
    composition : StarComposition
) -> bool:

    list_sao_positions = search_list_sao(tinhBan, composition.list_sao)

    if (role := composition.role):
        for position, cung in tinhBan.map_cung.items():
            if cung.role == role:
                position_role = position
                break

        considered_positions = [position_role]

        if composition.relation == "tam phuong":
            considered_positions += list(get_tam_hop(position_role))
        if composition.relation == "tu chinh":
            considered_positions += list(get_tam_hop(position_role)) + [get_xung_chieu(position_role)]

        return all(p in considered_positions for p in list_sao_positions)
    else:
        if composition.relation == "tam phuong":
            if len(list_sao_positions) != 3:
                return False
