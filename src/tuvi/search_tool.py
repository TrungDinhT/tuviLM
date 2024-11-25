from src.tuvi.tinh_ban import TinhBan
from src.tuvi.types import TYPE_DIA_CHI


# TODO : Must improve this
def search_sao(tinhBan : TinhBan, sao_name : str) -> TYPE_DIA_CHI:
    for position, cung in tinhBan.map_cung.items():
        list_sao_name = [sao.name for sao in cung.chinhTinh + cung.phuTinh]
        if sao_name in list_sao_name:
            return position
    raise ValueError(f"Can not find {sao_name}")
